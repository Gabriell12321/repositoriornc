import logging
import sqlite3
import json
import threading
from flask import Blueprint, request, jsonify, render_template, redirect, session

# Local DB path to avoid early circular imports
DB_PATH = 'ippel_system.db'

rnc = Blueprint('rnc', __name__)

# Limite padrão para endpoints do RNC (se limiter ativo)
try:
    import importlib
    _rl = importlib.import_module('services.rate_limit')
    _limiter = getattr(_rl, 'limiter')()
    if _limiter is not None:
        _limiter.limit("180 per minute")(rnc)
except Exception:
    pass
# Proteções avançadas (CSRF/Permissões) com fallback seguro
try:
    import importlib as _importlib_ep
    _ep = _importlib_ep.import_module('services.endpoint_protection')
    csrf_protect = getattr(_ep, 'csrf_protect')
    require_permission = getattr(_ep, 'require_permission')
except Exception:
    def csrf_protect(*_a, **_k):
        def _d(f):
            return f
        return _d
    def require_permission(*_a, **_k):
        def _d(f):
            return f
        return _d
logger = logging.getLogger('ippel.rnc')


@rnc.route('/api/rnc/create', methods=['POST'])
@csrf_protect()
def create_rnc():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401

    try:
        from services.permissions import has_permission
        from services.cache import clear_rnc_cache
        from services.groups import get_users_by_group
        from services.rnc import share_rnc_with_user
        data = request.get_json() or {}

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(rncs)")
        cols = {row[1] for row in cursor.fetchall()}

        import datetime as _dt
        now = _dt.datetime.now()
        rnc_number = f"RNC-{now.year}-{now.month:02d}-{now.day:02d}-{now.hour:02d}{now.minute:02d}{now.second:02d}"

        signature_columns = {
            'signature_inspection_name',
            'signature_engineering_name',
            'signature_inspection2_name'
        }
        if signature_columns & cols:
            assinaturas = [
                data.get('signature_inspection_name', data.get('assinatura1', '')),
                data.get('signature_engineering_name', data.get('assinatura2', '')),
                data.get('signature_inspection2_name', data.get('assinatura3', '')),
            ]
            if not any(a and a != 'NOME' for a in assinaturas):
                return jsonify({'success': False, 'message': 'É obrigatório preencher pelo menos uma assinatura!'}), 400

        cursor.execute('SELECT department FROM users WHERE id = ?', (session['user_id'],))
        user_dept_row = cursor.fetchone()
        user_department = user_dept_row[0] if user_dept_row else 'N/A'

        values_by_col = {
            'rnc_number': rnc_number,
            'title': data.get('title', 'RNC sem título'),
            'description': data.get('description', ''),
            'equipment': data.get('equipment', ''),
            'client': data.get('client', ''),
            'priority': data.get('priority', 'Média'),
            'status': 'Pendente',
            'user_id': session['user_id'],
            'assigned_user_id': data.get('assigned_user_id'),
            'department': user_department,
            'signature_inspection_name': data.get('signature_inspection_name', data.get('assinatura1', '')),
            'signature_engineering_name': data.get('signature_engineering_name', data.get('assinatura2', '')),
            'signature_inspection2_name': data.get('signature_inspection2_name', data.get('assinatura3', '')),
            'price': float(data.get('price') or 0),
            'disposition_usar': int(data.get('disposition_usar', False)),
            'disposition_retrabalhar': int(data.get('disposition_retrabalhar', False)),
            'disposition_rejeitar': int(data.get('disposition_rejeitar', False)),
            'disposition_sucata': int(data.get('disposition_sucata', False)),
            'disposition_devolver_estoque': int(data.get('disposition_devolver_estoque', False)),
            'disposition_devolver_fornecedor': int(data.get('disposition_devolver_fornecedor', False)),
            'inspection_aprovado': int(data.get('inspection_aprovado', False)),
            'inspection_reprovado': int(data.get('inspection_reprovado', False)),
            'inspection_ver_rnc': data.get('inspection_ver_rnc', ''),
        }

        insert_cols = [c for c in values_by_col.keys() if c in cols]
        insert_vals = [values_by_col[c] for c in insert_cols]

        if not insert_cols:
            conn.close()
            return jsonify({'success': False, 'message': 'Schema da tabela rncs inválido'}), 500

        placeholders = ", ".join(["?"] * len(insert_cols))
        sql = f"INSERT INTO rncs ({', '.join(insert_cols)}) VALUES ({placeholders})"
        cursor.execute('BEGIN IMMEDIATE')
        cursor.execute(sql, insert_vals)
        rnc_id = cursor.lastrowid

        shared_group_ids = data.get('shared_group_ids', []) or []

        try:
            def _share_task(rid, owner_id, group_ids):
                for gid in group_ids or []:
                    if not gid:
                        continue
                    users = get_users_by_group(gid)
                    for u in users:
                        uid = u[0]
                        if uid != owner_id:
                            share_rnc_with_user(rid, owner_id, uid, 'view')
            threading.Thread(target=_share_task, args=(rnc_id, session['user_id'], shared_group_ids), daemon=True).start()
        except Exception as e:
            logger.warning(f"Agendamento de compartilhamento falhou: {e}")

        try:
            conn.commit()
        finally:
            conn.close()

        try:
            clear_rnc_cache()
        except Exception:
            pass

        return jsonify({
            'success': True,
            'message': 'RNC criado com sucesso!',
            'rnc_id': rnc_id,
            'rnc_number': rnc_number
        })
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
        logger.error(f"Erro ao criar RNC: {e}")
        return jsonify({'success': False, 'message': 'Erro interno ao criar RNC'}), 500


@rnc.route('/rnc/<int:rnc_id>/chat')
def rnc_chat(rnc_id):
    if 'user_id' not in session:
        return redirect('/')
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.name as user_name, au.name as assigned_user_name
            FROM rncs r
            LEFT JOIN users u ON r.user_id = u.id
            LEFT JOIN users au ON r.assigned_user_id = au.id
            WHERE r.id = ?
        ''', (rnc_id,))
        rnc_row = cursor.fetchone()
        # Capturar os nomes das colunas antes de executar outras queries
        rnc_columns = [d[0] for d in cursor.description] if cursor.description else []
        if not rnc_row:
            conn.close()
            return render_template('error.html', message='RNC não encontrado'), 404
        cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
        current_user = cursor.fetchone()
        cursor.execute('''
            SELECT cm.id, cm.user_id, u.name, cm.message, cm.message_type, cm.created_at
            FROM chat_messages cm
            JOIN users u ON cm.user_id = u.id
            WHERE cm.rnc_id = ?
            ORDER BY cm.created_at ASC
        ''', (rnc_id,))
        messages = cursor.fetchall()
        conn.close()
        # Mapear RNC para dict para acesso via rnc.id / rnc.rnc_number no template
        rnc_dict = {}
        try:
            if rnc_row and rnc_columns:
                rnc_dict = dict(zip(rnc_columns, rnc_row))
            else:
                # Fallback mínimo
                rnc_dict = {'id': rnc_id}
        except Exception:
            rnc_dict = {'id': rnc_id}
        return render_template('rnc_chat.html', rnc=rnc_dict, current_user=current_user, messages=messages)
    except Exception:
        try:
            conn.close()
        except Exception:
            pass
        return render_template('error.html', message='Erro interno do sistema'), 500


@rnc.route('/api/rnc/list')
def list_rncs():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401

    conn = None
    try:
        from services.permissions import has_permission
        from services.db import get_db_connection, return_db_connection
        from services.cache import get_cached_query, cache_query
        try:
            # Local import to avoid cyclic/analysis issues
            from services.pagination import parse_cursor_limit, compute_window  # type: ignore
        except Exception:
            import importlib
            pagination = importlib.import_module('services.pagination')
            parse_cursor_limit = getattr(pagination, 'parse_cursor_limit')
            compute_window = getattr(pagination, 'compute_window')
        tab = request.args.get('tab', 'active')
        user_id = session['user_id']
        force_refresh = request.args.get('_t') is not None

        # Cursor-based pagination params (shared util)
        cursor_id, limit = parse_cursor_limit(request, default_limit=50000, max_limit=50000)

        cache_key = f"rncs_list_{user_id}_{tab}_{cursor_id}_{limit}"
        if not force_refresh:
            cached_result = get_cached_query(cache_key)
            if cached_result:
                logger.info(f"Retornando cache para {cache_key}")
                return jsonify(cached_result)
        else:
            logger.info(f"Force refresh solicitado - ignorando cache para {cache_key}")

        conn = get_db_connection()
        cursor = conn.cursor()
        # Build query with cursor-based pagination
        view_all_active = has_permission(user_id, 'view_all_rncs')
        view_all_finalized = has_permission(user_id, 'view_finalized_rncs')

        select_prefix = "SELECT"
        joins = [
            "FROM rncs r",
            "LEFT JOIN users u ON r.user_id = u.id",
            "LEFT JOIN users au ON r.assigned_user_id = au.id",
        ]
        where = ["(r.is_deleted = 0 OR r.is_deleted IS NULL)"]
        params = []

        if tab == 'finalized':
            where.append("r.status = 'Finalizado'")
            if not view_all_finalized:
                joins.append("LEFT JOIN rnc_shares rs ON rs.rnc_id = r.id")
                where.append("(r.user_id = ? OR r.assigned_user_id = ? OR rs.shared_with_user_id = ?)")
                params.extend([user_id, user_id, user_id])
                select_prefix = "SELECT DISTINCT"
        else:
            # default to active
            where.append("r.status NOT IN ('Finalizado')")
            if not view_all_active:
                joins.append("LEFT JOIN rnc_shares rs ON rs.rnc_id = r.id")
                where.append("(r.user_id = ? OR r.assigned_user_id = ? OR rs.shared_with_user_id = ?)")
                params.extend([user_id, user_id, user_id])
                select_prefix = "SELECT DISTINCT"

        if cursor_id is not None:
            # Desc order, so use r.id < cursor for next page
            where.append("r.id < ?")
            params.append(cursor_id)

        columns = (
            "r.id, r.rnc_number, r.title, r.equipment, r.client, r.priority, r.status, "
            "r.user_id, r.assigned_user_id, r.created_at, r.updated_at, r.finalized_at, "
            "u.name AS user_name, u.department AS user_department, au.name AS assigned_user_name"
        )

        sql = f"""
            {select_prefix}
                {columns}
            {' '.join(joins)}
            WHERE {' AND '.join(where)}
            ORDER BY r.id DESC
            LIMIT ?
        """
        params_with_limit = params + [limit + 1]  # fetch one extra row to detect has_more
        cursor.execute(sql, tuple(params_with_limit))

        rncs_rows = cursor.fetchall()
        rncs_rows, has_more, next_cursor = compute_window(rncs_rows, limit, id_index=0)
        logger.info(f"🔍 Query executada para {tab}: {len(rncs_rows)} RNCs retornados (limit={limit}, has_more={has_more})")

        current_user_id = session['user_id']
        formatted_rncs = [
            {
                'id': rnc[0],
                'rnc_number': rnc[1],
                'title': rnc[2],
                'equipment': rnc[3],
                'client': rnc[4],
                'priority': rnc[5],
                'status': rnc[6],
                'user_id': rnc[7],
                'assigned_user_id': rnc[8],
                'created_at': rnc[9],
                'updated_at': rnc[10],
                'finalized_at': rnc[11],
                'user_name': rnc[12],
                'user_department': rnc[13] or 'N/A',
                'assigned_user_name': rnc[14],
                'department': rnc[13] or 'N/A',
                'setor': rnc[13] or 'N/A',
                'is_creator': (current_user_id == rnc[7]),
                'is_assigned': (current_user_id == rnc[8])
            }
            for rnc in rncs_rows
        ]

        result = {
            'success': True,
            'rncs': formatted_rncs,
            'tab': tab,
            'limit': limit,
            'next_cursor': next_cursor,
            'has_more': has_more,
        }
        # Cache the result (Redis-backed with in-memory fallback)
        cache_query(cache_key, result, ttl=120)

        response = jsonify(result)
        response.headers['Cache-Control'] = 'public, max-age=120' if not force_refresh else 'no-cache'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    except Exception as e:
        logger.error(f"Erro ao listar RNCs: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    finally:
        if conn:
            try:
                from services.db import return_db_connection
                return_db_connection(conn)
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass

@rnc.route('/api/rnc/get/<int:rnc_id>', methods=['GET'])
def api_get_rnc(rnc_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info(rncs)')
        columns = [row[1] for row in cursor.fetchall()]
        cursor.execute('SELECT * FROM rncs WHERE id = ?', (rnc_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return jsonify({'success': False, 'message': 'RNC não encontrada'}), 404
        rnc_dict = dict(zip(columns, row))
        for key in rnc_dict:
            if key.startswith('disposition_') or key.startswith('inspection_'):
                rnc_dict[key] = bool(rnc_dict[key])
        return jsonify({'success': True, 'rnc': rnc_dict})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500


@rnc.route('/rnc/<int:rnc_id>')
def view_rnc(rnc_id):
    if 'user_id' not in session:
        return redirect('/')
    try:
        from services.rnc import can_user_access_rnc
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.name as user_name, au.name as assigned_user_name
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            LEFT JOIN users au ON r.assigned_user_id = au.id
            WHERE r.id = ?
        ''', (rnc_id,))
        rnc_data = cursor.fetchone()
        conn.close()
        if not rnc_data:
            return render_template('error.html', message='RNC não encontrado')
        if not isinstance(rnc_data, (tuple, list)):
            logger.error(f"Erro: rnc_data não é uma tupla/lista: {type(rnc_data)} - {rnc_data}")
            return render_template('error.html', message='Erro interno do sistema')

        if not can_user_access_rnc(session['user_id'], rnc_id):
            logger.warning(f"Acesso negado para usuário {session['user_id']} à RNC {rnc_id}")
            return render_template('error.html', message='Acesso negado')

        try:
            conn_cols = sqlite3.connect(DB_PATH)
            cur_cols = conn_cols.cursor()
            cur_cols.execute('PRAGMA table_info(rncs)')
            base_columns = [row[1] for row in cur_cols.fetchall()]
            conn_cols.close()
        except Exception:
            base_columns = [
                'id','rnc_number','title','description','equipment','client','priority','status','user_id','assigned_user_id',
                'is_deleted','deleted_at','finalized_at','created_at','updated_at','disposition_usar','disposition_retrabalhar',
                'disposition_rejeitar','disposition_sucata','disposition_devolver_estoque','disposition_devolver_fornecedor',
                'inspection_aprovado','inspection_reprovado','inspection_ver_rnc','signature_inspection_date','signature_engineering_date',
                'signature_inspection2_date','signature_inspection_name','signature_engineering_name','signature_inspection2_name','price'
            ]
        columns = base_columns + ['user_name', 'assigned_user_name']

        if len(rnc_data) < len(columns):
            rnc_data = list(rnc_data) + [None] * (len(columns) - len(rnc_data))

        rnc_dict = dict(zip(columns, rnc_data))

        def parse_label_map(text: str):
            if not text:
                return {}
            mapping = {}
            lines = [ln.strip() for ln in str(text).split('\n') if ln.strip()]
            for ln in lines:
                if ':' in ln:
                    parts = ln.split(':', 1)
                    if len(parts) == 2:
                        label = parts[0].strip()
                        val = parts[1].strip()
                        normalized_label = label.lower().replace(' ', '').replace('ã', 'a').replace('ç', 'c')
                        if 'desenho' in normalized_label:
                            mapping['Desenho'] = val
                        elif 'mp' in normalized_label:
                            mapping['MP'] = val
                        elif 'revisao' in normalized_label or 'revisão' in normalized_label:
                            mapping['Revisão'] = val
                        elif 'cv' in normalized_label:
                            mapping['CV'] = val
                        elif 'pos' in normalized_label:
                            mapping['POS'] = val
                        elif 'conjunto' in normalized_label:
                            mapping['Conjunto'] = val
                        elif 'modelo' in normalized_label:
                            mapping['Modelo'] = val
                        elif 'quantidade' in normalized_label:
                            mapping['Quantidade'] = val
                        elif 'area' in normalized_label and 'responsavel' in normalized_label:
                            mapping['Área responsável'] = val
                        elif 'descricao' in normalized_label and 'rnc' in normalized_label:
                            mapping['Descrição da RNC'] = val
                        elif 'instrucao' in normalized_label and 'retrabalho' in normalized_label:
                            mapping['Instrução para retrabalho'] = val
                        elif 'valor' in normalized_label:
                            mapping['Valor'] = val
                        else:
                            mapping[label] = val
            return mapping

        txt_fields = parse_label_map(rnc_dict.get('description') or '')
        is_creator = (session['user_id'] == rnc_data[8])
        return render_template('view_rnc_full.html', rnc=rnc_dict, is_creator=is_creator, txt_fields=txt_fields)
    except Exception as e:
        logger.error(f"Erro ao visualizar RNC {rnc_id}: {e}")
        return render_template('error.html', message='Erro interno do sistema')


@rnc.route('/rnc/<int:rnc_id>/reply', methods=['GET'])
def reply_rnc(rnc_id):
    if 'user_id' not in session:
        return redirect('/')
    try:
        from services.permissions import has_permission
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.name as user_name, au.name as assigned_user_name
              FROM rncs r
              LEFT JOIN users u ON r.user_id = u.id
              LEFT JOIN users au ON r.assigned_user_id = au.id
             WHERE r.id = ?
        ''', (rnc_id,))
        rnc_data = cursor.fetchone()
        conn.close()

        if not rnc_data:
            return render_template('error.html', message='RNC não encontrado')

        owner_id = rnc_data[8]
        is_creator = str(session['user_id']) == str(owner_id)
        is_admin = has_permission(session['user_id'], 'admin_access')
        can_reply = has_permission(session['user_id'], 'reply_rncs')
        # Novo: permitir responder se o RNC foi compartilhado com o usuário (qualquer nível)
        shared_can_reply = False
        try:
            conn_share = sqlite3.connect(DB_PATH)
            cur_share = conn_share.cursor()
            cur_share.execute('SELECT 1 FROM rnc_shares WHERE rnc_id = ? AND shared_with_user_id = ? LIMIT 1', (rnc_id, session['user_id']))
            shared_can_reply = cur_share.fetchone() is not None
            conn_share.close()
        except Exception:
            shared_can_reply = False
        if not (is_creator or is_admin or can_reply or shared_can_reply):
            return render_template('error.html', message='Acesso negado: você não tem permissão para responder este RNC')

        try:
            conn_cols = sqlite3.connect(DB_PATH)
            cur_cols = conn_cols.cursor()
            cur_cols.execute('PRAGMA table_info(rncs)')
            base_columns = [row[1] for row in cur_cols.fetchall()]
            conn_cols.close()
        except Exception:
            base_columns = [
                'id','rnc_number','title','description','equipment','client','priority','status','user_id','assigned_user_id',
                'is_deleted','deleted_at','finalized_at','created_at','updated_at','disposition_usar','disposition_retrabalhar',
                'disposition_rejeitar','disposition_sucata','disposition_devolver_estoque','disposition_devolver_fornecedor',
                'inspection_aprovado','inspection_reprovado','inspection_ver_rnc','signature_inspection_date','signature_engineering_date',
                'signature_inspection2_date','signature_inspection_name','signature_engineering_name','signature_inspection2_name','price'
            ]
        columns = base_columns + ['user_name', 'assigned_user_name']

        if len(rnc_data) < len(columns):
            rnc_data = list(rnc_data) + [None] * (len(columns) - len(rnc_data))

        rnc_dict = dict(zip(columns, rnc_data))
        return render_template('edit_rnc_form.html', rnc=rnc_dict, is_editing=True, is_reply=True)
    except Exception as e:
        logger.error(f"Erro ao abrir modo Responder para RNC {rnc_id}: {e}")
        return render_template('error.html', message='Erro interno do sistema')


@rnc.route('/rnc/<int:rnc_id>/print')
def print_rnc(rnc_id):
    if 'user_id' not in session:
        return redirect('/')
    try:
        # Carregar dados básicos do RNC diretamente
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rncs WHERE id = ?', (rnc_id,))
        rnc_data = cursor.fetchone()
        conn.close()
        if rnc_data is None:
            logger.error(f"Erro ao buscar RNC {rnc_id}")
            return render_template('error.html', message='RNC não encontrado')

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.name as user_name, au.name as assigned_user_name
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            LEFT JOIN users au ON r.assigned_user_id = au.id
            WHERE r.id = ?
        ''', (rnc_id,))
        row = cursor.fetchone()
        columns = [d[0] for d in cursor.description]
        conn.close()

        rnc_dict = dict(zip(columns, row)) if row else {}
        for date_key in ['created_at', 'updated_at', 'finalized_at']:
            if isinstance(rnc_dict.get(date_key), (tuple, list)):
                rnc_dict[date_key] = rnc_dict.get(date_key)[0]

        if 'price' not in rnc_dict:
            rnc_dict['price'] = 0
        if 'user_name' not in rnc_dict:
            rnc_dict['user_name'] = 'Sistema'

        def parse_label_map(text: str):
            if not text:
                return {}
            mapping = {}
            lines = [ln.strip() for ln in str(text).split('\n') if ln.strip()]
            for ln in lines:
                if ':' in ln:
                    parts = ln.split(':', 1)
                    if len(parts) == 2:
                        label = parts[0].strip()
                        val = parts[1].strip()
                        normalized_label = label.lower().replace(' ', '').replace('ã', 'a').replace('ç', 'c')
                        if 'desenho' in normalized_label:
                            mapping['Desenho'] = val
                        elif 'mp' in normalized_label:
                            mapping['MP'] = val
                        elif 'revisao' in normalized_label or 'revisão' in normalized_label:
                            mapping['Revisão'] = val
                        elif 'cv' in normalized_label:
                            mapping['CV'] = val
                        elif 'pos' in normalized_label:
                            mapping['POS'] = val
                        elif 'conjunto' in normalized_label:
                            mapping['Conjunto'] = val
                        elif 'modelo' in normalized_label:
                            mapping['Modelo'] = val
                        elif 'quantidade' in normalized_label:
                            mapping['Quantidade'] = val
                        elif 'area' in normalized_label and 'responsavel' in normalized_label:
                            mapping['Área responsável'] = val
                        elif 'descricao' in normalized_label and 'rnc' in normalized_label:
                            mapping['Descrição da RNC'] = val
                        elif 'instrucao' in normalized_label and 'retrabalho' in normalized_label:
                            mapping['Instrução para retrabalho'] = val
                        elif 'valor' in normalized_label:
                            mapping['Valor'] = val
                        else:
                            mapping[label] = val
            return mapping

        txt_fields = parse_label_map(rnc_dict.get('description') or '')
        return render_template('view_rnc_print.html', rnc=rnc_dict, txt_fields=txt_fields)
    except Exception as e:
        logger.error(f"Erro ao gerar página de impressão para RNC {rnc_id}: {e}")
        return render_template('error.html', message='Erro interno do sistema')


@rnc.route('/rnc/<int:rnc_id>/pdf-generator')
def pdf_generator(rnc_id):
    if 'user_id' not in session:
        return redirect('/')
    try:
        from services.permissions import has_permission
        # Carregar dados básicos do RNC
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rncs WHERE id = ?', (rnc_id,))
        rnc_data = cursor.fetchone()
        conn.close()
        if rnc_data is None:
            logger.error(f"Erro ao buscar RNC {rnc_id}")
            return render_template('error.html', message='RNC não encontrado')

        user_id_index = 8
        try:
            if len(rnc_data) <= user_id_index:
                logger.error(f"RNC {rnc_id} não tem dados suficientes: {len(rnc_data)} colunas")
                return render_template('error.html', message='Dados do RNC incompletos')
            user_id_from_rnc = rnc_data[user_id_index]
            user_has_permission = has_permission(session['user_id'], 'view_all_rncs')
            is_creator = (user_id_from_rnc == session['user_id'])
            if not user_has_permission and not is_creator:
                logger.warning(f"Usuário {session['user_id']} tentou acessar RNC {rnc_id} sem permissão")
                return render_template('error.html', message='Acesso negado')
        except Exception as access_error:
            logger.error(f"Erro ao verificar permissões para RNC {rnc_id}: {access_error}")
            return render_template('error.html', message='Erro ao verificar permissões')

        columns = [
            'id', 'rnc_number', 'title', 'description', 'equipment', 'client', 
            'priority', 'status', 'user_id', 'created_at', 'updated_at', 
            'assigned_user_id', 'disposition_usar', 'disposition_retrabalhar', 
            'disposition_rejeitar', 'disposition_sucata', 'disposition_devolver_estoque', 
            'disposition_devolver_fornecedor', 'inspection_aprovado', 'inspection_reprovado', 
            'inspection_ver_rnc', 'signature_inspection_date', 'signature_engineering_date', 
            'signature_inspection2_date', 'signature_inspection_name', 'signature_engineering_name', 
            'signature_inspection2_name', 'is_deleted', 'deleted_at', 'finalized_at',
            'user_name', 'assigned_user_name'
        ]
        if len(rnc_data) < len(columns):
            rnc_data = list(rnc_data) + [None] * (len(columns) - len(rnc_data))
        rnc_dict = dict(zip(columns, rnc_data))
        try:
            return render_template('view_rnc_pdf_js.html', rnc=rnc_dict)
        except Exception as template_error:
            logger.error(f"Erro ao renderizar template para RNC {rnc_id}: {template_error}")
            return render_template('error.html', message='Erro ao gerar página')
    except Exception as e:
        logger.error(f"Erro ao acessar gerador de PDF para RNC {rnc_id}: {e}")
        return render_template('error.html', message='Erro interno do sistema')


@rnc.route('/rnc/<int:rnc_id>/edit', methods=['GET', 'POST'])
def edit_rnc(rnc_id):
    if 'user_id' not in session:
        return redirect('/')
    try:
        from services.permissions import has_permission
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.name as user_name, au.name as assigned_user_name
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            LEFT JOIN users au ON r.assigned_user_id = au.id
            WHERE r.id = ?
        ''', (rnc_id,))
        rnc_data = cursor.fetchone()
        conn.close()

        if not rnc_data:
            return render_template('error.html', message='RNC não encontrado')
        if not isinstance(rnc_data, (tuple, list)):
            logger.error(f"Erro: rnc_data não é uma tupla/lista: {type(rnc_data)} - {rnc_data}")
            return render_template('error.html', message='Erro interno do sistema')

        user_is_creator = rnc_data[8] == session['user_id']
        can_edit_all = has_permission(session['user_id'], 'edit_all_rncs')
        can_edit_own = has_permission(session['user_id'], 'edit_own_rnc')
        if not (can_edit_all or (can_edit_own and user_is_creator)):
            return render_template('error.html', message='Acesso negado: você não tem permissão para editar este RNC')

        try:
            conn_cols = sqlite3.connect(DB_PATH)
            cur_cols = conn_cols.cursor()
            cur_cols.execute('PRAGMA table_info(rncs)')
            base_columns = [row[1] for row in cur_cols.fetchall()]
            conn_cols.close()
        except Exception:
            base_columns = [
                'id','rnc_number','title','description','equipment','client','priority','status','user_id','assigned_user_id',
                'is_deleted','deleted_at','finalized_at','created_at','updated_at','disposition_usar','disposition_retrabalhar',
                'disposition_rejeitar','disposition_sucata','disposition_devolver_estoque','disposition_devolver_fornecedor',
                'inspection_aprovado','inspection_reprovado','inspection_ver_rnc','signature_inspection_date','signature_engineering_date',
                'signature_inspection2_date','signature_inspection_name','signature_engineering_name','signature_inspection2_name','price'
            ]
        columns = base_columns + ['user_name', 'assigned_user_name']
        if len(rnc_data) < len(columns):
            rnc_data = list(rnc_data) + [None] * (len(columns) - len(rnc_data))
        rnc_dict = dict(zip(columns, rnc_data))
        return render_template('edit_rnc_form.html', rnc=rnc_dict, is_editing=True)
    except Exception as e:
        logger.error(f"Erro ao editar RNC {rnc_id}: {e}")
        return render_template('error.html', message='Erro interno do sistema')


@rnc.route('/api/rnc/<int:rnc_id>/update', methods=['PUT'])
@csrf_protect()
def update_rnc_api(rnc_id):
    logger.info(f"Iniciando atualização da RNC {rnc_id}")
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        from services.permissions import has_permission
        from services.cache import clear_rnc_cache, query_cache, cache_lock
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rncs WHERE id = ?', (rnc_id,))
        rnc_data = cursor.fetchone()
        if not rnc_data:
            return jsonify({'success': False, 'message': 'RNC não encontrado'}), 404
        if not isinstance(rnc_data, (tuple, list)):
            logger.error(f"Erro: rnc_data não é uma tupla/lista: {type(rnc_data)} - {rnc_data}")
            return jsonify({'success': False, 'message': 'Erro interno do sistema'}), 500

        user_is_creator = str(rnc_data[8]) == str(session['user_id'])
        can_edit_all = has_permission(session['user_id'], 'edit_all_rncs')
        can_edit_own = has_permission(session['user_id'], 'edit_own_rnc')
        has_admin = has_permission(session['user_id'], 'admin_access')
        department_match = False

        if has_permission(session['user_id'], 'view_all_departments_rncs'):
            department_match = True
        else:
            cursor.execute('SELECT department FROM rncs WHERE id = ?', (rnc_id,))
            rnc_dept = cursor.fetchone()
            if rnc_dept and rnc_dept[0] == 'Engenharia' and has_permission(session['user_id'], 'view_engineering_rncs'):
                department_match = True

        can_reply = has_permission(session['user_id'], 'reply_rncs')
        # Novo: permitir atualização quando o RNC foi compartilhado com o usuário (qualquer nível)
        is_shared_with_user = False
        try:
            cur_shared = conn.cursor()
            cur_shared.execute('SELECT 1 FROM rnc_shares WHERE rnc_id = ? AND shared_with_user_id = ? LIMIT 1', (rnc_id, session['user_id']))
            is_shared_with_user = cur_shared.fetchone() is not None
        except Exception:
            is_shared_with_user = False
        if not (can_edit_all or (can_edit_own and user_is_creator) or has_admin or department_match or can_reply or is_shared_with_user):
            logger.warning(f"Acesso negado para edição do RNC {rnc_id}")
            return jsonify({'success': False, 'message': 'Acesso negado: você não tem permissão para editar este RNC'}), 403

        data = request.get_json() or {}
        try:
            cur_cols = conn.cursor()
            cur_cols.execute('PRAGMA table_info(rncs)')
            col_names = [row[1] for row in cur_cols.fetchall()]
        except Exception:
            col_names = []
        current = {}
        try:
            if col_names and isinstance(rnc_data, (tuple, list)):
                current = dict(zip(col_names, rnc_data))
        except Exception:
            current = {}

        def get_bool(key):
            v = data.get(key, current.get(key))
            if isinstance(v, bool):
                return 1 if v else 0
            try:
                return 1 if str(v).strip().lower() in ('1','true','on','yes','y') else 0
            except Exception:
                return 0

        cursor.execute('SELECT signature_inspection_name, signature_engineering_name, signature_inspection2_name FROM rncs WHERE id = ?', (rnc_id,))
        current_sign = cursor.fetchone() or (None, None, None)
        new_sign = (
            data.get('signature_inspection_name', current_sign[0] or ''),
            data.get('signature_engineering_name', current_sign[1] or ''),
            data.get('signature_inspection2_name', current_sign[2] or '')
        )
        if not any(s and s != 'NOME' for s in new_sign):
            return jsonify({'success': False, 'message': 'É obrigatório preencher pelo menos uma assinatura!'}), 400

        disposition_usar = get_bool('disposition_usar')
        disposition_retrabalhar = get_bool('disposition_retrabalhar')
        disposition_rejeitar = get_bool('disposition_rejeitar')
        disposition_sucata = get_bool('disposition_sucata')
        disposition_devolver_estoque = get_bool('disposition_devolver_estoque')
        disposition_devolver_fornecedor = get_bool('disposition_devolver_fornecedor')
        inspection_aprovado = get_bool('inspection_aprovado')
        inspection_reprovado = get_bool('inspection_reprovado')
        inspection_ver_rnc = data.get('inspection_ver_rnc', current.get('inspection_ver_rnc', ''))
        instruction_retrabalho = data.get('instruction_retrabalho', current.get('instruction_retrabalho', ''))
        cause_rnc = data.get('cause_rnc', current.get('cause_rnc', ''))
        action_rnc = data.get('action_rnc', current.get('action_rnc', ''))

        cursor.execute('''
            UPDATE rncs 
            SET title = ?, description = ?, equipment = ?, client = ?, 
                priority = ?, status = ?, updated_at = CURRENT_TIMESTAMP,
                signature_inspection_name = ?, signature_engineering_name = ?, signature_inspection2_name = ?,
                signature_inspection_date = COALESCE(NULLIF(?, ''), signature_inspection_date),
                signature_engineering_date = COALESCE(NULLIF(?, ''), signature_engineering_date),
                signature_inspection2_date = COALESCE(NULLIF(?, ''), signature_inspection2_date),
                disposition_usar = ?, disposition_retrabalhar = ?, disposition_rejeitar = ?, disposition_sucata = ?,
                disposition_devolver_estoque = ?, disposition_devolver_fornecedor = ?,
                inspection_aprovado = ?, inspection_reprovado = ?, inspection_ver_rnc = ?,
                instruction_retrabalho = ?, cause_rnc = ?, action_rnc = ?
            WHERE id = ?
        ''', (
            data.get('title', current.get('title','')),
            data.get('description', current.get('description','')),
            data.get('equipment', current.get('equipment','')),
            data.get('client', current.get('client','')),
            data.get('priority', current.get('priority','Média')),
            data.get('status', current.get('status','Pendente')),
            new_sign[0],
            new_sign[1],
            new_sign[2],
            data.get('signature_inspection_date',''),
            data.get('signature_engineering_date',''),
            data.get('signature_inspection2_date',''),
            disposition_usar,
            disposition_retrabalhar,
            disposition_rejeitar,
            disposition_sucata,
            disposition_devolver_estoque,
            disposition_devolver_fornecedor,
            inspection_aprovado,
            inspection_reprovado,
            inspection_ver_rnc,
            instruction_retrabalho,
            cause_rnc,
            action_rnc,
            rnc_id
        ))
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()

        clear_rnc_cache()
        try:
            keys_to_remove = []
            for key in list(query_cache.keys()):
                if key.startswith('rncs_list_') or key.startswith('charts_'):
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del query_cache[key]
        except Exception:
            pass
        return jsonify({'success': True, 'message': 'RNC atualizado com sucesso!', 'affected_rows': affected_rows})
    except Exception as e:
        logger.error(f"Erro ao atualizar RNC {rnc_id}: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500


@rnc.route('/api/rnc/<int:rnc_id>/finalize', methods=['POST'])
@csrf_protect()
def finalize_rnc(rnc_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        from services.permissions import has_permission
        from services.cache import clear_rnc_cache
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rncs WHERE id = ? AND is_deleted = 0', (rnc_id,))
        rnc_row = cursor.fetchone()
        if not rnc_row:
            conn.close()
            return jsonify({'success': False, 'message': 'RNC não encontrado'}), 404
        if not isinstance(rnc_row, (tuple, list)):
            logger.error(f"Erro: rnc não é uma tupla/lista: {type(rnc_row)} - {rnc_row}")
            conn.close()
            return jsonify({'success': False, 'message': 'Erro interno do sistema'}), 500

        user_id = session['user_id']
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        user_role = user[0]
        rnc_creator_id = rnc_row[8]
        is_creator = (user_id == rnc_creator_id)
        if not is_creator and user_role != 'admin':
            conn.close()
            return jsonify({'success': False, 'message': 'Apenas o criador do RNC pode finalizá-lo'}), 403

        cursor.execute('''
            UPDATE rncs 
            SET status = 'Finalizado', finalized_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (rnc_id,))
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Erro ao finalizar RNC'}), 500
        conn.commit()
        conn.close()
        clear_rnc_cache()
        return jsonify({'success': True, 'message': 'RNC finalizado com sucesso!'})
    except Exception as e:
        logger.error(f"Erro ao finalizar RNC: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500


@rnc.route('/api/rnc/<int:rnc_id>/reply', methods=['POST'])
@csrf_protect()
def reply_rnc_api(rnc_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        from services.permissions import has_permission
        from services.cache import clear_rnc_cache
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, user_id, assigned_user_id, status FROM rncs WHERE id = ? AND is_deleted = 0', (rnc_id,))
        rnc = cursor.fetchone()
        if not rnc:
            conn.close()
            return jsonify({'success': False, 'message': 'RNC não encontrada'}), 404
        rnc_creator_id = rnc[1]
        user_id = session['user_id']
        is_creator = str(user_id) == str(rnc_creator_id)
        is_admin = has_permission(user_id, 'admin_access')
        can_reply = has_permission(user_id, 'reply_rncs')
        # Novo: permitir responder se compartilhado com o usuário
        shared_can_reply = False
        try:
            cur_share = conn.cursor()
            cur_share.execute('SELECT 1 FROM rnc_shares WHERE rnc_id = ? AND shared_with_user_id = ? LIMIT 1', (rnc_id, user_id))
            shared_can_reply = cur_share.fetchone() is not None
        except Exception:
            shared_can_reply = False
        if not (is_creator or is_admin or can_reply or shared_can_reply):
            conn.close()
            return jsonify({'success': False, 'message': 'Sem permissão para responder esta RNC'}), 403
        cursor.execute('''
            UPDATE rncs
               SET status = 'Pendente',
                   finalized_at = NULL,
                   updated_at = CURRENT_TIMESTAMP,
                   assigned_user_id = user_id
             WHERE id = ?
        ''', (rnc_id,))
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Nenhuma alteração realizada'}), 400
        conn.commit()
        conn.close()
        clear_rnc_cache()
        return jsonify({'success': True, 'message': 'RNC reenviada com sucesso'})
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500


@rnc.route('/api/rnc/<int:rnc_id>/delete', methods=['DELETE'])
@csrf_protect()
def delete_rnc(rnc_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        from services.cache import cache_lock, query_cache
        from services.permissions import has_permission
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, user_id FROM rncs WHERE id = ?', (rnc_id,))
        rnc = cursor.fetchone()
        if not rnc:
            conn.close()
            return jsonify({'success': False, 'message': 'RNC não encontrado'}), 404
        # Permissão: apenas criador ou admin pode deletar
        creator_id = rnc[1]
        user_id = session['user_id']
        is_creator = str(user_id) == str(creator_id)
        is_admin = has_permission(user_id, 'admin_access')
        if not (is_creator or is_admin):
            conn.close()
            return jsonify({'success': False, 'message': 'Sem permissão para excluir este RNC'}), 403
        cursor.execute('DELETE FROM rncs WHERE id = ?', (rnc_id,))
        cursor.execute('DELETE FROM rnc_shares WHERE rnc_id = ?', (rnc_id,))
        cursor.execute('DELETE FROM chat_messages WHERE rnc_id = ?', (rnc_id,))
        conn.commit()
        conn.close()
        with cache_lock:
            keys_to_remove = [key for key in list(query_cache.keys()) if 'rncs_list_' in key or 'rnc_' in key or 'charts_' in key]
            for key in keys_to_remove:
                del query_cache[key]
        logger.info(f"RNC {rnc_id} excluído definitivamente por usuário {session['user_id']}")
        return jsonify({'success': True, 'message': 'RNC excluído definitivamente.', 'cache_cleared': True})
    except Exception as e:
        logger.error(f"Erro ao deletar RNC: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500


@rnc.route('/api/rnc/<int:rnc_id>/share', methods=['POST'])
@csrf_protect()
def share_rnc(rnc_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        from services.permissions import has_permission
        from services.rnc import share_rnc_with_user
        data = request.get_json()
        shared_with_user_ids = data.get('shared_with_user_ids', [])
        permission_level = data.get('permission_level', 'view')
        cursor = sqlite3.connect(DB_PATH).cursor()
        cursor.execute('SELECT * FROM rncs WHERE id = ?', (rnc_id,))
        rnc_data = cursor.fetchone()
        cursor.connection.close()
        if rnc_data is None:
            return jsonify({'success': False, 'message': 'RNC não encontrado'}), 404
        user_id_index = 8
        if len(rnc_data) <= user_id_index:
            return jsonify({'success': False, 'message': 'Dados do RNC incompletos'}), 400
        is_creator = (rnc_data[user_id_index] == session['user_id'])
        has_admin_permission = has_permission(session['user_id'], 'view_all_rncs')
        if not is_creator and not has_admin_permission:
            return jsonify({'success': False, 'message': 'Sem permissão para compartilhar esta RNC'}), 403
        success_count = 0
        for user_id in shared_with_user_ids:
            if share_rnc_with_user(rnc_id, session['user_id'], user_id, permission_level):
                success_count += 1
        if success_count > 0:
            return jsonify({'success': True, 'message': f'RNC compartilhada com {success_count} usuário(s) com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao compartilhar RNC'}), 500
    except Exception as e:
        logger.error(f"Erro ao compartilhar RNC {rnc_id}: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do sistema'}), 500


@rnc.route('/api/rnc/<int:rnc_id>/shared-users', methods=['GET'])
def get_shared_users(rnc_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        from services.rnc import can_user_access_rnc
        from services.db import get_db_connection, return_db_connection
        try:
            from services.pagination import parse_cursor_limit, compute_window  # type: ignore
        except Exception:
            import importlib
            pagination = importlib.import_module('services.pagination')
            parse_cursor_limit = getattr(pagination, 'parse_cursor_limit')
            compute_window = getattr(pagination, 'compute_window')
        if not can_user_access_rnc(session['user_id'], rnc_id):
            return jsonify({'success': False, 'message': 'Sem permissão para acessar esta RNC'}), 403
        cursor_id, limit = parse_cursor_limit(request, default_limit=20, max_limit=200)

        conn = get_db_connection()
        cur = conn.cursor()
        where_extra = ""
        params = [rnc_id]
        # Use rs.id (share row id) as cursor anchor for deterministic pagination
        if cursor_id is not None:
            where_extra = " AND rs.id < ?"
            params.append(cursor_id)
        params.append(limit + 1)
        cur.execute(
            '''
            SELECT rs.id, rs.shared_with_user_id, rs.permission_level, u.name, u.email
              FROM rnc_shares rs
              JOIN users u ON rs.shared_with_user_id = u.id
             WHERE rs.rnc_id = ?
                   ''' + where_extra + '''
             ORDER BY rs.id DESC
             LIMIT ?
            ''', tuple(params)
        )
        rows = cur.fetchall()
        # id_index=0 now (rs.id)
        rows, has_more, next_cursor = compute_window(rows, limit, id_index=0)
        return_db_connection(conn)

        shared_users_list = [
            {
                'user_id': user_id,
                'permission_level': perm,
                'name': name,
                'email': email,
            }
            for (_row_id, user_id, perm, name, email) in rows
        ]
        return jsonify({'success': True, 'shared_users': shared_users_list, 'limit': limit, 'next_cursor': next_cursor, 'has_more': has_more})
    except Exception as e:
        logger.error(f"Erro ao buscar usuários compartilhados da RNC {rnc_id}: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do sistema'}), 500


# Debug endpoints (mantidos no blueprint RNC)
@rnc.route('/api/debug/rnc-count')
def debug_rnc_count():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        from services.db import get_db_connection, return_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM rncs')
        total = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE status = "Finalizado"')
        finalizados = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE (is_deleted = 0 OR is_deleted IS NULL) AND status = "Finalizado"')
        finalizados_ativos = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE (is_deleted = 0 OR is_deleted IS NULL) AND status != "Finalizado"')
        ativos = cursor.fetchone()[0]
        return_db_connection(conn)
        return jsonify({'success': True, 'counts': {'total': total, 'finalizados': finalizados, 'finalizados_ativos': finalizados_ativos, 'ativos': ativos}})
    except Exception as e:
        logger.error(f"Erro no debug: {e}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500


@rnc.route('/api/debug/user-rncs')
def debug_user_rncs():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        from services.db import get_db_connection, return_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = session['user_id']
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE user_id = ?', (user_id,))
        created_by_user = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE assigned_user_id = ?', (user_id,))
        assigned_to_user = cursor.fetchone()[0]
        cursor.execute('''SELECT COUNT(*) FROM rncs 
                         WHERE (is_deleted = 0 OR is_deleted IS NULL) 
                         AND status != "Finalizado" 
                         AND (user_id = ? OR assigned_user_id = ?)''', (user_id, user_id))
        active_total = cursor.fetchone()[0]
        cursor.execute('''SELECT COUNT(*) FROM rncs 
                         WHERE (is_deleted = 0 OR is_deleted IS NULL) 
                         AND status = "Finalizado" 
                         AND (user_id = ? OR assigned_user_id = ?)''', (user_id, user_id))
        finalized_total = cursor.fetchone()[0]
        cursor.execute('''SELECT id, rnc_number, title, status, user_id, assigned_user_id 
                         FROM rncs 
                         WHERE (user_id = ? OR assigned_user_id = ?) 
                         ORDER BY id DESC LIMIT 5''', (user_id, user_id))
        examples = cursor.fetchall()
        return_db_connection(conn)
        return jsonify({
            'success': True,
            'user_id': user_id,
            'user_name': session.get('user_name', 'N/A'),
            'counts': {
                'created_by_user': created_by_user,
                'assigned_to_user': assigned_to_user,
                'active_total': active_total,
                'finalized_total': finalized_total
            },
            'examples': [
                {
                    'id': ex[0],
                    'rnc_number': ex[1],
                    'title': ex[2],
                    'status': ex[3],
                    'is_creator': ex[4] == user_id,
                    'is_assigned': ex[5] == user_id
                }
                for ex in examples
            ]
        })
    except Exception as e:
        logger.error(f"Erro no debug de usuário: {e}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500


@rnc.route('/api/debug/user-shares')
def debug_user_shares():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        from services.db import get_db_connection, return_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = session['user_id']
        cursor.execute('''
            SELECT rs.rnc_id, r.rnc_number, r.title, r.status, 
                   u.name as shared_by, rs.permission_level, rs.created_at
            FROM rnc_shares rs
            JOIN rncs r ON rs.rnc_id = r.id
            LEFT JOIN users u ON rs.shared_by_user_id = u.id
            WHERE rs.shared_with_user_id = ?
            ORDER BY rs.created_at DESC LIMIT 10
        ''', (user_id,))
        shared_with_user = cursor.fetchall()
        cursor.execute('''
            SELECT rs.rnc_id, r.rnc_number, r.title, r.status, 
                   u.name as shared_with, rs.permission_level, rs.created_at
            FROM rnc_shares rs
            JOIN rncs r ON rs.rnc_id = r.id
            LEFT JOIN users u ON rs.shared_with_user_id = u.id
            WHERE rs.shared_by_user_id = ?
            ORDER BY rs.created_at DESC LIMIT 10
        ''', (user_id,))
        shared_by_user = cursor.fetchall()
        cursor.execute('SELECT COUNT(*) FROM rnc_shares WHERE shared_with_user_id = ?', (user_id,))
        total_shared_with = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM rnc_shares WHERE shared_by_user_id = ?', (user_id,))
        total_shared_by = cursor.fetchone()[0]
        return_db_connection(conn)
        return jsonify({
            'success': True,
            'user_id': user_id,
            'user_name': session.get('user_name', 'N/A'),
            'totals': {
                'shared_with_me': total_shared_with,
                'shared_by_me': total_shared_by
            },
            'shared_with_me': [
                {
                    'rnc_id': share[0],
                    'rnc_number': share[1],
                    'title': share[2],
                    'status': share[3],
                    'shared_by': share[4],
                    'permission': share[5],
                    'shared_at': share[6]
                }
                for share in shared_with_user
            ],
            'shared_by_me': [
                {
                    'rnc_id': share[0],
                    'rnc_number': share[1],
                    'title': share[2],
                    'status': share[3],
                    'shared_with': share[4],
                    'permission': share[5],
                    'shared_at': share[6]
                }
                for share in shared_by_user
            ]
        })
    except Exception as e:
        logger.error(f"Erro no debug de compartilhamentos: {e}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500


@rnc.route('/api/debug/rnc-signatures/<int:rnc_id>')
def debug_rnc_signatures(rnc_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        from services.db import get_db_connection, return_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, rnc_number, title,
                   signature_inspection_name, signature_engineering_name, signature_inspection2_name,
                   signature_inspection_date, signature_engineering_date, signature_inspection2_date
            FROM rncs 
            WHERE id = ?
        ''', (rnc_id,))
        rnc_data = cursor.fetchone()
        return_db_connection(conn)
        if not rnc_data:
            return jsonify({'success': False, 'message': 'RNC não encontrada'}), 404
        return jsonify({
            'success': True,
            'rnc_id': rnc_id,
            'rnc_number': rnc_data[1],
            'title': rnc_data[2],
            'signatures': {
                'inspection_name': rnc_data[3],
                'engineering_name': rnc_data[4],
                'inspection2_name': rnc_data[5],
                'inspection_date': rnc_data[6],
                'engineering_date': rnc_data[7],
                'inspection2_date': rnc_data[8]
            },
            'debug_info': {
                'inspection_empty': not rnc_data[3] or rnc_data[3] == 'NOME',
                'engineering_empty': not rnc_data[4] or rnc_data[4] == 'NOME',
                'inspection2_empty': not rnc_data[5] or rnc_data[5] == 'NOME'
            }
        })
    except Exception as e:
        logger.error(f"Erro no debug de assinaturas: {e}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

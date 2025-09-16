import logging
import sqlite3
import json
import threading
from datetime import datetime  # IMPORT ADICIONADO: necessário para gerar rnc_number
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
def create_rnc():
    """Endpoint robusto para criação de RNC com validações obrigatórias"""
    try:
        # Verificar autenticação
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        # Obter dados
        data = request.get_json() or {}
        
        # VALIDAÇÕES OBRIGATÓRIAS PARA CRIAÇÃO
        required_fields = {
            'title': 'Título é obrigatório',
            'description': 'Descrição da não conformidade é obrigatória',
            'equipment': 'Equipamento é obrigatório',
            'client': 'Cliente é obrigatório'
        }
        
        missing_fields = []
        for field, message in required_fields.items():
            if not data.get(field, '').strip():
                missing_fields.append(message)
        
        if missing_fields:
            return jsonify({
                'success': False, 
                'message': 'Campos obrigatórios não preenchidos: ' + ', '.join(missing_fields)
            }), 400
        
        # Conectar ao banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(rncs)")
        cols = {row[1] for row in cursor.fetchall()}
        
        # Gerar número RNC
        now = datetime.now()
        rnc_number = f"RNC-{now.year}-{now.month:02d}-{now.day:02d}-{now.hour:02d}{now.minute:02d}{now.second:02d}"
        
        # Obter departamento do usuário
        cursor.execute('SELECT department FROM users WHERE id = ?', (session['user_id'],))
        user_dept_row = cursor.fetchone()
        user_department = user_dept_row[0] if user_dept_row else 'N/A'
        
        # Obter nome do usuário criador para auto-preenchimento da primeira assinatura
        cursor.execute('SELECT name, department FROM users WHERE id = ?', (session['user_id'],))
        user_info = cursor.fetchone()
        user_name = user_info[0] if user_info else 'Usuário'
        user_dept = user_info[1] if user_info else 'N/A'
        
        # Dados básicos para inserção
        basic_data = {
            'rnc_number': rnc_number,
            'title': data.get('title', 'RNC sem título'),
            'description': data.get('description', ''),
            'equipment': data.get('equipment', ''),
            'client': data.get('client', ''),
            'priority': data.get('priority', 'Média'),
            'status': 'Pendente',
            'user_id': session['user_id'],
            'department': user_department,
            # Auto-preencher primeira assinatura com criador da RNC
            'signature_inspection_name': f'{user_name} ({user_dept})',
            'signature_inspection_date': now.strftime('%d/%m/%Y')
        }
        
        # Adicionar campos opcionais se existirem
        optional_fields = {
            'signature_inspection_name': data.get('signature_inspection_name', ''),
            'signature_engineering_name': data.get('signature_engineering_name', ''),
            'signature_inspection2_name': data.get('signature_inspection2_name', ''),
            'price': float(data.get('price') or 0),
            'assigned_user_id': data.get('assigned_user_id'),
            'disposition_usar': int(data.get('disposition_usar', False)),
            'disposition_retrabalhar': int(data.get('disposition_retrabalhar', False)),
            'disposition_rejeitar': int(data.get('disposition_rejeitar', False)),
            'disposition_sucata': int(data.get('disposition_sucata', False)),
            'disposition_devolver_estoque': int(data.get('disposition_devolver_estoque', False)),
            'disposition_devolver_fornecedor': int(data.get('disposition_devolver_fornecedor', False)),
            'inspection_aprovado': int(data.get('inspection_aprovado', False)),
            'inspection_reprovado': int(data.get('inspection_reprovado', False)),
            'inspection_ver_rnc': data.get('inspection_ver_rnc', ''),
            'instruction_retrabalho': data.get('instruction_retrabalho', ''),
            'cause_rnc': data.get('cause_rnc', ''),
            'action_rnc': data.get('action_rnc', ''),
        }
        
        # Combinar dados básicos com opcionais
        all_data = {**basic_data, **optional_fields}
        
        # Filtrar apenas colunas que existem
        insert_cols = [c for c in all_data.keys() if c in cols]
        insert_vals = [all_data[c] for c in insert_cols]
        
        if not insert_cols:
            conn.close()
            return jsonify({'success': False, 'message': 'Nenhuma coluna válida encontrada'}), 500
        
        # Executar inserção
        placeholders = ", ".join(["?"] * len(insert_cols))
        sql = f"INSERT INTO rncs ({', '.join(insert_cols)}) VALUES ({placeholders})"
        
        cursor.execute(sql, insert_vals)
        rnc_id = cursor.lastrowid
        
        # Tentar compartilhamento (opcional)
        try:
            raw_ids = data.get('shared_group_ids', []) or []
            # Normalizar: aceitar int, str numérica, lista de str
            normalized_ids = []
            for raw in raw_ids:
                if raw in (None, ''):
                    continue
                try:
                    normalized_ids.append(int(raw))
                except Exception:
                    logger.warning(f"shared_group_ids: ID inválido ignorado: {raw!r}")
            if normalized_ids:
                logger.info(f"Iniciando compartilhamento RNC {rnc_id} com grupos {normalized_ids}")
                try:
                    from services.groups import get_users_by_group
                    from services.rnc import share_rnc_with_user

                    def _share_task(rid: int, owner_id: int, group_ids: list[int]):
                        total_links = 0
                        for gid in group_ids:
                            if not isinstance(gid, int) or gid <= 0:
                                logger.warning(f"_share_task: gid inválido: {gid!r}")
                                continue
                            try:
                                users = get_users_by_group(gid) or []
                                logger.info(f"Grupo {gid}: {len(users)} usuários ativos para compartilhar")
                                for u in users:
                                    try:
                                        uid = u[0]
                                        if uid != owner_id:
                                            if share_rnc_with_user(rid, owner_id, uid, 'view'):
                                                total_links += 1
                                    except Exception as ie:
                                        logger.warning(f"Falha ao compartilhar com usuário do grupo {gid}: {ie}")
                            except Exception as e:
                                logger.warning(f"Erro ao processar grupo {gid}: {e}")
                        logger.info(f"Compartilhamento concluído RNC {rid}: {total_links} vínculos criados")

                    threading.Thread(target=_share_task, args=(rnc_id, session['user_id'], normalized_ids), daemon=True).start()
                except Exception as e:
                    logger.warning(f"Compartilhamento não disponível: {e}")
        except Exception as e:
            logger.warning(f"Erro no compartilhamento: {e}")
        
        # Commit
        conn.commit()
        conn.close()
        
        # Limpar cache (opcional)
        try:
            from services.cache import clear_rnc_cache
            clear_rnc_cache()
        except Exception:
            pass
        
        return jsonify({
            'success': True,
            'message': 'RNC criada com sucesso!',
            'rnc_id': rnc_id,
            'rnc_number': rnc_number
        })
        
    except Exception as e:
        # Log detalhado do erro
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Erro ao criar RNC: {e}")
        logger.error(f"Traceback completo: {error_details}")
        
        # Retornar mensagem mais específica se possível
        error_message = 'Erro interno ao criar RNC'
        if 'UNIQUE constraint failed' in str(e):
            error_message = 'Número de RNC já existe. Tente novamente.'
        elif 'FOREIGN KEY constraint failed' in str(e):
            error_message = 'Usuário inválido. Faça login novamente.'
        elif 'no such table' in str(e):
            error_message = 'Banco de dados não configurado corretamente.'
        
        return jsonify({'success': False, 'message': error_message}), 500

@rnc.route('/rnc/<int:rnc_id>/chat')
def rnc_chat(rnc_id):
    if 'user_id' not in session:
        return redirect('/')
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
         SELECT r.*, u.name as user_name, au.name as assigned_user_name,
             u.department as user_department, au.department as assigned_user_department
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
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*,
                   u.name as user_name,
                   au.name as assigned_user_name,
                   u.department as user_department,
                   au.department as assigned_user_department
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
            return render_template('error.html', message='Erro interno do sistema')

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
                'inspection_reprovado','inspection_ver_rnc','signature_inspection_date','signature_engineering_date',
                'signature_inspection2_date','signature_inspection_name','signature_engineering_name','inspection_aprovado',
                'signature_inspection2_name','price','department','instruction_retrabalho','cause_rnc','action_rnc','responsavel'
            ]

        columns = base_columns + ['user_name', 'assigned_user_name', 'user_department', 'assigned_user_department']

        if len(rnc_data) < len(columns):
            rnc_data = list(rnc_data) + [None] * (len(columns) - len(rnc_data))

        rnc_dict = dict(zip(columns, rnc_data))

        # Função para extrair campos de texto da descrição
        def parse_label_map(text: str):
            if not text:
                return {}
            result = {}
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if key and value:
                            # Sempre preservar chave original
                            result[key] = value
                            
                            # Normalizar chaves para facilitar busca
                            normalized_key = key.lower().replace(' ', '').replace('ã', 'a').replace('ç', 'c')
                            
                            # Mapear campos específicos (além da chave original)
                            if 'desenho' in normalized_key or key.upper() == 'DES':
                                result['Desenho'] = value
                            elif 'mp' in normalized_key or key.upper() == 'MP':
                                result['MP'] = value
                            elif 'revisao' in normalized_key or 'revisão' in normalized_key or key.upper() == 'REV':
                                result['Revisão'] = value
                            elif 'cv' in normalized_key or key.upper() == 'CV':
                                result['CV'] = value
                            elif 'pos' in normalized_key or key.upper() == 'POS':
                                result['POS'] = value
                            elif 'conjunto' in normalized_key or key.upper() == 'CONJUNTO':
                                result['Conjunto'] = value
                            elif 'modelo' in normalized_key or key.upper() == 'MOD':
                                result['Modelo'] = value
                            elif 'quantidade' in normalized_key or 'qtde' in normalized_key or key.upper() == 'QTDE LOTE':
                                result['Quantidade'] = value
                            elif 'material' in normalized_key or key.upper() == 'MATERIAL':
                                result['Material'] = value
                            elif 'area' in normalized_key and 'responsavel' in normalized_key:
                                result['Área responsável'] = value
                            elif 'setor' in normalized_key or key.upper() == 'SETOR':
                                result['Setor'] = value
                            elif 'descricao' in normalized_key and 'desenho' in normalized_key:
                                result['Descrição do desenho'] = value
                            elif 'descricao' in normalized_key and 'rnc' in normalized_key:
                                result['Descrição da RNC'] = value
                            elif 'instrucao' in normalized_key and 'retrabalho' in normalized_key:
                                result['Instrução para retrabalho'] = value
                            elif 'causa' in normalized_key and 'rnc' in normalized_key:
                                result['Causa da RNC'] = value
                            elif 'acao' in normalized_key:
                                result['Ação a ser tomada'] = value
                            elif 'valor' in normalized_key:
                                result['Valor'] = value
                            elif 'oc' in normalized_key or 'ordem' in normalized_key or key.upper() == 'OC':
                                result['OC'] = value
                            elif 'responsavel' in normalized_key:
                                result['Responsável'] = value
            return result

        # Extrair campos de texto da descrição para visualização
        txt_fields = parse_label_map(rnc_dict.get('description') or '')
        
        # Se responsavel está vazio, tentar extrair do description
        if not rnc_dict.get('responsavel'):
            description = rnc_dict.get('description') or ''
            lines = description.split('\n')
            for line in lines:
                if 'responsável' in line.lower() or 'responsavel' in line.lower():
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            responsavel = parts[1].strip()
                            if responsavel:
                                rnc_dict['responsavel'] = responsavel
                                break
            
            # Se ainda está vazio, usar o nome do usuário
            if not rnc_dict.get('responsavel'):
                rnc_dict['responsavel'] = rnc_dict.get('user_name') or 'N/A'
        
        # Determinar criador de forma robusta usando o dict
        is_creator = str(session['user_id']) == str(rnc_dict.get('user_id'))
        
        # Debug: Log os dados para verificar se estão chegando
        logger.info(f"DEBUG - RNC {rnc_id}: rnc_number={rnc_dict.get('rnc_number')}, title={rnc_dict.get('title')}")
        logger.info(f"DEBUG - RNC {rnc_id}: equipment={rnc_dict.get('equipment')}, client={rnc_dict.get('client')}")
        logger.info(f"DEBUG - RNC {rnc_id}: description length={len(str(rnc_dict.get('description') or ''))}")
        logger.info(f"DEBUG - RNC {rnc_id}: txt_fields={txt_fields}")
        logger.info(f"DEBUG - RNC {rnc_id}: signature_inspection_name={rnc_dict.get('signature_inspection_name')}")
        
        # Debug específico para os novos campos
        logger.info(f"DEBUG - RNC {rnc_id}: instruction_retrabalho='{rnc_dict.get('instruction_retrabalho')}'")
        logger.info(f"DEBUG - RNC {rnc_id}: cause_rnc='{rnc_dict.get('cause_rnc')}'")
        logger.info(f"DEBUG - RNC {rnc_id}: action_rnc='{rnc_dict.get('action_rnc')}'")
        logger.info(f"DEBUG - RNC {rnc_id}: responsavel='{rnc_dict.get('responsavel')}'")
        logger.info(f"DEBUG - RNC {rnc_id}: txt_fields.get('Responsável')='{txt_fields.get('Responsável')}'")
        logger.info(f"DEBUG - RNC {rnc_id}: Chaves do rnc_dict: {list(rnc_dict.keys())}")
        
        # Visualização usa o template atualizado com estilo do modelo
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
            SELECT r.*, u.name as user_name, au.name as assigned_user_name,
                   u.department as user_department, au.department as assigned_user_department
              FROM rncs r
              LEFT JOIN users u ON r.user_id = u.id
              LEFT JOIN users au ON r.assigned_user_id = au.id
             WHERE r.id = ? AND r.is_deleted = 0
        ''', (rnc_id,))
        rnc_data = cursor.fetchone()
        conn.close()

        if not rnc_data:
            logger.warning(f"RNC {rnc_id} não encontrado para usuário {session.get('user_id')}")
            return render_template('error.html', 
                message=f'RNC #{rnc_id} não encontrado ou foi removido.',
                suggestions=[
                    'Verifique se o número do RNC está correto',
                    'O RNC pode ter sido removido ou finalizado',
                    'Entre em contato com o administrador se o problema persistir'
                ])

        owner_id = rnc_data[8]
        assigned_user_id = rnc_data[9] if len(rnc_data) > 9 else None
        is_creator = str(session['user_id']) == str(owner_id)
        is_assigned = assigned_user_id is not None and str(session['user_id']) == str(assigned_user_id)
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

        if not (is_creator or is_assigned or is_admin or can_reply or shared_can_reply):
            logger.warning(f"Usuário {session.get('user_id')} tentou responder RNC {rnc_id} sem permissão")
            return render_template('error.html', 
                message='Acesso negado: você não tem permissão para responder este RNC',
                suggestions=[
                    'Verifique se você tem permissão para responder RNCs',
                    'Entre em contato com o criador do RNC ou administrador',
                    'Solicite que o RNC seja compartilhado com você'
                ])

        try:
            conn_cols = sqlite3.connect(DB_PATH)
            cur_cols = conn_cols.cursor()
            cur_cols.execute('PRAGMA table_info(rncs)')
            base_columns = [row[1] for row in cur_cols.fetchall()]
            conn_cols.close()
        except Exception as e:
            logger.error(f"Erro ao obter colunas da tabela rncs: {e}")
            base_columns = [
                'id','rnc_number','title','description','equipment','client','priority','status','user_id','assigned_user_id',
                'is_deleted','deleted_at','finalized_at','created_at','updated_at','disposition_usar','disposition_retrabalhar',
                'disposition_rejeitar','disposition_sucata','disposition_devolver_estoque','disposition_devolver_fornecedor',
                'inspection_aprovado','inspection_reprovado','inspection_ver_rnc','signature_inspection_date','signature_engineering_date',
                'signature_inspection2_date','signature_inspection_name','signature_engineering_name','signature_inspection2_name','price',
                'cause_rnc','action_rnc','instruction_retrabalho'
            ]
        columns = base_columns + ['user_name', 'assigned_user_name', 'user_department', 'assigned_user_department']

        if len(rnc_data) < len(columns):
            rnc_data = list(rnc_data) + [None] * (len(columns) - len(rnc_data))

        rnc_dict = dict(zip(columns, rnc_data))
        logger.info(f"Usuário {session.get('user_id')} acessando modo resposta para RNC {rnc_id}")
        
        # Configurando valores padrão para garantir renderização correta mesmo em caso de problemas
        if 'txt_fields' not in locals() or txt_fields is None:
            txt_fields = {}
        return render_template('edit_rnc_form.html', rnc=rnc_dict, is_editing=True, is_reply=True, txt_fields=txt_fields)
    except Exception as e:
        logger.error(f"Erro ao abrir modo Responder para RNC {rnc_id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        try:
            # Garantir que o formato de resposta seja consistente mesmo em caso de erro
            return render_template('error.html', 
                message='Erro interno do sistema ao carregar o formulário de resposta',
                suggestions=[
                    'Tente novamente em alguns segundos',
                    'Verifique sua conexão com o sistema',
                    'Entre em contato com o suporte técnico se o problema persistir'
                ])
        except Exception as inner_e:
            logger.critical(f"Erro fatal na renderização da página de erro: {inner_e}")
            return "Erro crítico ao carregar a resposta. Por favor, contate o suporte técnico."


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
            """Extrai pares label→valor da descrição, tolerando diferentes separadores e abreviações.
            Suporta linhas como:
              - "DES.: 123   REV - X   POS = 1   MOD  ABC"
              - "QTDE LOTE: 25" → Quantidade
              - "DESCRIÇÃO DES.: ..." → Descrição da RNC/Descrição do desenho
            """
            import re, unicodedata
            if not text:
                return {}
            def _norm(s: str) -> str:
                s = unicodedata.normalize('NFD', s)
                s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
                s = s.lower()
                s = re.sub(r'[^a-z0-9]', '', s)
                return s
            # Suporta: ":", "-", "—", "=", ou 2+ espaços como separador
            sep_re = re.compile(r'^\s*([A-Za-zÀ-ÿ\.\s/_-]{2,}?)\s*(?:[:=\-\u2013\u2014]+|\s{2,})\s*(.+)$')
            token_re = re.compile(r'^\s*([A-Za-zÀ-ÿ\.]{2,})\s+(.+)$')
            mapping: dict[str, str] = {}
            lines = [ln.rstrip() for ln in str(text).split('\n') if ln.strip()]
            for ln in lines:
                m = sep_re.match(ln)
                if not m:
                    m = token_re.match(ln)
                if not m:
                    continue
                label, val = m.group(1).strip(), m.group(2).strip()
                n = _norm(label)
                if n in {'des', 'desenho'}:
                    mapping['Desenho'] = val
                elif n in {'mp'}:
                    mapping['MP'] = val
                elif n in {'rev', 'revisao'}:
                    mapping['Revisão'] = val
                elif n == 'cv' or 'cv' in n:
                    mapping['CV'] = val
                elif n == 'pos' or 'pos' in n:
                    mapping['POS'] = val
                elif 'conjunto' in n or n == 'conj':
                    mapping['Conjunto'] = val
                elif n in {'modelo', 'mod'}:
                    mapping['Modelo'] = val
                elif n == 'quantidade' or n.startswith('qtde') or n.startswith('qtd'):
                    mapping['Quantidade'] = val
                elif 'material' in n or n == 'mat':
                    mapping['Material'] = val
                elif n in {'oc', 'ordemdecompra', 'ordemcompra'}:
                    mapping['OC'] = val
                elif ('area' in n and 'responsavel' in n) or n in {'arearesponsavel'}:
                    mapping['Área responsável'] = val
                elif ('descricao' in n and 'rnc' in n) or n in {'descricaodes', 'descricaododesenho', 'descricaodesenho'}:
                    # Preencher ambos para máxima compatibilidade com templates
                    mapping['Descrição da RNC'] = val
                    mapping['Descrição do desenho'] = val
                elif 'instrucao' in n and 'retrabalho' in n:
                    mapping['Instrução para retrabalho'] = val
                elif n in {'valor', 'vlr'}:
                    mapping['Valor'] = val
                else:
                    mapping[label] = val
            return mapping
        txt_fields = parse_label_map(rnc_dict.get('description') or '')
        return render_template('view_rnc_print.html', rnc=rnc_dict, txt_fields=txt_fields, mode='print')
    except Exception as e:
        logger.error(f"Erro ao gerar página de impressão para RNC {rnc_id}: {e}")
        return render_template('error.html', message='Erro interno do sistema')


@rnc.route('/rnc/<int:rnc_id>/print-modelo')
def print_rnc_modelo(rnc_id):
    """Renderiza o novo modelo de impressão (templates/modelo.html) com todos os dados da RNC."""
    if 'user_id' not in session:
        return redirect('/')
    try:
        # Carregar linha completa com joins para nomes
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
        columns = [d[0] for d in cursor.description] if cursor.description else []
        conn.close()
        if not row:
            return render_template('error.html', message='RNC não encontrado')

        rnc_dict = dict(zip(columns, row))
        # Normalizar booleans
        for key in list(rnc_dict.keys()):
            if key.startswith('disposition_') or key.startswith('inspection_'):
                try:
                    rnc_dict[key] = bool(rnc_dict[key])
                except Exception:
                    pass

        # Extrair campos rotulados do description
        def parse_label_map(text: str):
            """Extrai pares label→valor da descrição, tolerando diferentes separadores e abreviações.
            Suporta linhas como:
              - "DES.: 123   REV - X   POS = 1   MOD  ABC"
              - "QTDE LOTE: 25" → Quantidade
              - "DESCRIÇÃO DES.: ..." → Descrição da RNC/Descrição do desenho
            """
            import re, unicodedata
            if not text:
                return {}
            def _norm(s: str) -> str:
                s = unicodedata.normalize('NFD', s)
                s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
                s = s.lower()
                s = re.sub(r'[^a-z0-9]', '', s)
                return s
            sep_re = re.compile(r'^\s*([A-Za-zÀ-ÿ\.\s/_-]{2,}?)\s*(?:[:=\-\u2013\u2014]+|\s{2,})\s*(.+)$')
            token_re = re.compile(r'^\s*([A-Za-zÀ-ÿ\.]{2,})\s+(.+)$')
            mapping: dict[str, str] = {}
            lines = [ln.rstrip() for ln in str(text).split('\n') if ln.strip()]
            for ln in lines:
                m = sep_re.match(ln)
                if not m:
                    m = token_re.match(ln)
                if not m:
                    continue
                label, val = m.group(1).strip(), m.group(2).strip()
                n = _norm(label)
                if n in {'des', 'desenho'}:
                    mapping['Desenho'] = val
                elif n in {'mp'}:
                    mapping['MP'] = val
                elif n in {'rev', 'revisao'}:
                    mapping['Revisão'] = val
                elif n == 'cv' or 'cv' in n:
                    mapping['CV'] = val
                elif n == 'pos' or 'pos' in n:
                    mapping['POS'] = val
                elif 'conjunto' in n or n == 'conj':
                    mapping['Conjunto'] = val
                elif n in {'modelo', 'mod'}:
                    mapping['Modelo'] = val
                elif n == 'quantidade' or n.startswith('qtde') or n.startswith('qtd'):
                    mapping['Quantidade'] = val
                elif 'material' in n or n == 'mat':
                    mapping['Material'] = val
                elif n in {'oc', 'ordemdecompra', 'ordemcompra'}:
                    mapping['OC'] = val
                elif ('area' in n and 'responsavel' in n) or n in {'arearesponsavel'}:
                    mapping['Área responsável'] = val
                elif ('descricao' in n and 'rnc' in n) or n in {'descricaodes', 'descricaododesenho', 'descricaodesenho'}:
                    mapping['Descrição da RNC'] = val
                    mapping['Descrição do desenho'] = val
                elif 'instrucao' in n and 'retrabalho' in n:
                    mapping['Instrução para retrabalho'] = val
                elif n in {'valor', 'vlr'}:
                    mapping['Valor'] = val
                elif n in {'causa'}:
                    mapping['Causa'] = val
                elif 'acao' in n or 'acaosertomada' in n:
                    mapping['Ação'] = val
                else:
                    mapping[label] = val
            return mapping

        txt_fields = parse_label_map(rnc_dict.get('description') or '')
        # Compatibilidade de nomes de depto
        if 'department' not in rnc_dict or not rnc_dict.get('department'):
            rnc_dict['department'] = rnc_dict.get('user_department')

        return render_template('modelo.html', rnc=rnc_dict, txt_fields=txt_fields)
    except Exception as e:
        logger.error(f"Erro ao renderizar modelo de impressão da RNC {rnc_id}: {e}")
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


@rnc.route('/rnc/<int:rnc_id>/download-pdf')
def download_rnc_pdf(rnc_id):
    """Download do PDF da RNC"""
    if 'user_id' not in session:
        return redirect('/')
    
    try:
        from services.pdf_generator import pdf_generator
        from services.permissions import has_permission
        
        # Verificar permissões
        user_id = session['user_id']
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, assigned_user_id FROM rncs WHERE id = ? AND is_deleted = 0', (rnc_id,))
        rnc = cursor.fetchone()
        conn.close()
        
        if not rnc:
            return render_template('error.html', message='RNC não encontrada')
        
        rnc_creator_id = rnc[0]
        rnc_assigned_id = rnc[1]
        
        # Verificar permissões
        is_creator = str(user_id) == str(rnc_creator_id)
        is_assigned = (rnc_assigned_id is not None and str(user_id) == str(rnc_assigned_id))
        is_admin = has_permission(user_id, 'admin_access')
        can_view = has_permission(user_id, 'view_all_rncs')
        
        # Verificar se foi compartilhada
        shared_can_view = False
        try:
            conn_share = sqlite3.connect(DB_PATH)
            cur_share = conn_share.cursor()
            cur_share.execute('SELECT 1 FROM rnc_shares WHERE rnc_id = ? AND shared_with_user_id = ? LIMIT 1', (rnc_id, user_id))
            shared_can_view = cur_share.fetchone() is not None
            conn_share.close()
        except Exception:
            shared_can_view = False
        
        if not (is_creator or is_assigned or is_admin or can_view or shared_can_view):
            return render_template('error.html', message='Acesso negado: você não tem permissão para visualizar esta RNC')
        
        # Gerar PDF
        pdf_path = pdf_generator.generate_pdf(rnc_id)
        if not pdf_path:
            return render_template('error.html', message='Erro ao gerar PDF da RNC')
        
        # Enviar arquivo para download
        from flask import send_file
        import os
        
        filename = os.path.basename(pdf_path)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF da RNC {rnc_id}: {e}")
        return render_template('error.html', message='Erro interno ao gerar PDF')


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
        
        # Adicionar a função parse_label_map para extrair campos de texto
        def parse_label_map(text: str):
            if not text:
                return {}
            result = {}
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if key and value:
                            result[key] = value
            return result
        
        # Extrair campos de texto da descrição
        txt_fields = parse_label_map(rnc_dict.get('description') or '')
        
        return render_template('edit_rnc_form.html', rnc=rnc_dict, txt_fields=txt_fields, is_editing=True)
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
        rnc_assigned_id = rnc[2]
        user_id = session['user_id']
        is_creator = str(user_id) == str(rnc_creator_id)
        is_admin = has_permission(user_id, 'admin_access')
        is_assigned = (rnc_assigned_id is not None and str(user_id) == str(rnc_assigned_id))
        can_reply = has_permission(user_id, 'reply_rncs')
        # Novo: permitir responder se compartilhado com o usuário
        shared_can_reply = False
        try:
            cur_share = conn.cursor()
            cur_share.execute('SELECT 1 FROM rnc_shares WHERE rnc_id = ? AND shared_with_user_id = ? LIMIT 1', (rnc_id, user_id))
            shared_can_reply = cur_share.fetchone() is not None
        except Exception:
            shared_can_reply = False
        if not (is_creator or is_assigned or is_admin or can_reply or shared_can_reply):
            conn.close()
            return jsonify({'success': False, 'message': 'Sem permissão para responder esta RNC'}), 403
        cursor.execute('''
            UPDATE rncs
               SET status = 'Pendente',
                   finalized_at = NULL,
                   updated_at = CURRENT_TIMESTAMP,
                   assigned_user_id = ?
             WHERE id = ?
        ''', (user_id, rnc_id))
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

@rnc.route('/api/rnc/test-create', methods=['POST'])
def test_create_rnc():
    """Endpoint de teste para criação de RNC"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        data = request.get_json() or {}
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Gerar número simples
        now = datetime.now()
        rnc_number = f"TEST-{now.strftime('%Y%m%d%H%M%S')}"
        
        # Dados mínimos
        cursor.execute("""
            INSERT INTO rncs (rnc_number, title, description, user_id, department, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            rnc_number,
            data.get('title', 'RNC Teste'),
            data.get('description', 'Teste'),
            session['user_id'],
            'Teste',
            'Pendente'
        ))
        
        rnc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'RNC de teste criada!',
            'rnc_id': rnc_id,
            'rnc_number': rnc_number
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500


@rnc.route('/api/rnc/create-simple', methods=['POST'])
def create_rnc_simple():
    """Endpoint simplificado para criação de RNC"""
    try:
        # Verificar autenticação
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        # Obter dados
        data = request.get_json() or {}
        
        # Conectar ao banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Gerar número RNC
        now = datetime.now()
        rnc_number = f"RNC-{now.year}-{now.month:02d}-{now.day:02d}-{now.hour:02d}{now.minute:02d}{now.second:02d}"
        
        # Obter departamento do usuário
        cursor.execute('SELECT department FROM users WHERE id = ?', (session['user_id'],))
        user_dept_row = cursor.fetchone()
        user_department = user_dept_row[0] if user_dept_row else 'N/A'
        
        # Dados básicos para inserção
        cursor.execute("INSERT INTO rncs (rnc_number, title, description, equipment, client, priority, status, user_id, department) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            rnc_number,
            data.get('title', 'RNC sem título'),
            data.get('description', ''),
            data.get('equipment', ''),
            data.get('client', ''),
            data.get('priority', 'Média'),
            'Pendente',
            session['user_id'],
            user_department
        ))
        
        rnc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'RNC criada com sucesso!',
            'rnc_id': rnc_id,
            'rnc_number': rnc_number
        })
        
    except Exception as e:
        # Log do erro
        logger.error(f"Erro no endpoint simplificado: {e}")
        
        # Mensagem específica
        error_message = 'Erro interno ao criar RNC'
        if 'UNIQUE constraint failed' in str(e):
            error_message = 'Número de RNC já existe. Tente novamente.'
        elif 'FOREIGN KEY constraint failed' in str(e):
            error_message = 'Usuário inválido. Faça login novamente.'
        elif 'no such table' in str(e):
            error_message = 'Banco de dados não configurado corretamente.'
        
        return jsonify({'success': False, 'message': error_message}), 500

@rnc.route('/api/rnc/debug-create', methods=['POST'])
def debug_create_rnc():
    """Endpoint de debug para criação de RNC"""
    try:
        # Verificar autenticação
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        # Obter dados
        data = request.get_json() or {}
        
        # Conectar ao banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(rncs)")
        cols = {row[1] for row in cursor.fetchall()}
        
        # Gerar número RNC
        now = datetime.now()
        rnc_number = f"DEBUG-{now.year}-{now.month:02d}-{now.day:02d}-{now.hour:02d}{now.minute:02d}{now.second:02d}"
        
        # Obter departamento do usuário
        cursor.execute('SELECT department FROM users WHERE id = ?', (session['user_id'],))
        user_dept_row = cursor.fetchone()
        user_department = user_dept_row[0] if user_dept_row else 'N/A'
        
        # Dados para inserção (apenas colunas básicas)
        basic_data = {
            'rnc_number': rnc_number,
            'title': data.get('title', 'RNC Debug'),
            'description': data.get('description', 'Teste de debug'),
            'equipment': data.get('equipment', ''),
            'client': data.get('client', ''),
            'priority': data.get('priority', 'Média'),
            'status': 'Pendente',
            'user_id': session['user_id'],
            'department': user_department
        }
        
        # Filtrar apenas colunas que existem
        insert_cols = [c for c in basic_data.keys() if c in cols]
        insert_vals = [basic_data[c] for c in insert_cols]
        
        if not insert_cols:
            conn.close()
            return jsonify({'success': False, 'message': 'Nenhuma coluna válida encontrada'}), 500
        
        # Executar inserção
        placeholders = ", ".join(["?"] * len(insert_cols))
        sql = f"INSERT INTO rncs ({', '.join(insert_cols)}) VALUES ({placeholders})"
        
        cursor.execute(sql, insert_vals)
        rnc_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'RNC de debug criada!',
            'rnc_id': rnc_id,
            'rnc_number': rnc_number,
            'debug_info': {
                'columns_found': len(cols),
                'columns_used': len(insert_cols),
                'user_department': user_department
            }
        })
        
    except Exception as e:
        # Log detalhado
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Erro no debug: {e}")
        logger.error(f"Traceback: {error_details}")
        
        return jsonify({
            'success': False, 
            'message': f'Erro: {str(e)}',
            'debug_info': {
                'error_type': type(e).__name__,
                'error_details': str(e)
            }
        }), 500


@rnc.route('/api/rnc/<int:rnc_id>/respond', methods=['POST'])
def respond_to_rnc(rnc_id):
    """Endpoint para resposta obrigatória à RNC - CAUSA e AÇÃO"""
    try:
        # Verificar autenticação
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        user_id = session['user_id']
        data = request.get_json() or {}
        
        # VALIDAÇÕES OBRIGATÓRIAS PARA RESPOSTA
        required_response_fields = {
            'cause_rnc': 'Causa da RNC é obrigatória para resposta',
            'action_rnc': 'Ação a ser tomada é obrigatória para resposta'
        }
        
        missing_fields = []
        for field, message in required_response_fields.items():
            if not data.get(field, '').strip():
                missing_fields.append(message)
        
        if missing_fields:
            return jsonify({
                'success': False, 
                'message': 'Campos obrigatórios para resposta não preenchidos: ' + ', '.join(missing_fields)
            }), 400
        
        # Conectar ao banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a RNC existe e se o usuário pode responder
        cursor.execute('''
            SELECT user_id, assigned_user_id, status, title 
            FROM rncs 
            WHERE id = ? AND (is_deleted = 0 OR is_deleted IS NULL)
        ''', (rnc_id,))
        
        rnc_row = cursor.fetchone()
        if not rnc_row:
            conn.close()
            return jsonify({'success': False, 'message': 'RNC não encontrada'}), 404
        
        creator_id, assigned_user_id, status, title = rnc_row
        
        # Verificar permissão para responder
        # Pode responder: criador, responsável atribuído, admin, ou usuários compartilhados
        can_respond = False
        
        # Verificar se é admin
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        user_role = cursor.fetchone()
        if user_role and user_role[0] == 'admin':
            can_respond = True
        # Verificar se é criador ou responsável
        elif user_id == creator_id or user_id == assigned_user_id:
            can_respond = True
        else:
            # Verificar se tem acesso via compartilhamento
            cursor.execute('''
                SELECT 1 FROM rnc_shares 
                WHERE rnc_id = ? AND shared_with_user_id = ? 
                LIMIT 1
            ''', (rnc_id, user_id))
            if cursor.fetchone():
                can_respond = True
        
        if not can_respond:
            conn.close()
            return jsonify({'success': False, 'message': 'Sem permissão para responder a esta RNC'}), 403
        
        # Atualizar campos de resposta obrigatória
        update_fields = {
            'cause_rnc': data.get('cause_rnc', '').strip(),
            'action_rnc': data.get('action_rnc', '').strip(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Verificar se campos existem na tabela
        cursor.execute("PRAGMA table_info(rncs)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        
        # Filtrar apenas campos que existem
        valid_fields = {k: v for k, v in update_fields.items() if k in existing_cols}
        
        if valid_fields:
            set_clause = ', '.join([f"{k} = ?" for k in valid_fields.keys()])
            values = list(valid_fields.values()) + [rnc_id]
            
            cursor.execute(f'''
                UPDATE rncs 
                SET {set_clause}
                WHERE id = ?
            ''', values)
        
        conn.commit()
        conn.close()
        
        # Log da ação
        logger.info(f"Usuário {user_id} respondeu à RNC {rnc_id} - Causa: {data.get('cause_rnc', '')[:50]}...")
        
        return jsonify({
            'success': True,
            'message': f'Resposta registrada com sucesso para RNC: {title}',
            'rnc_id': rnc_id,
            'fields_updated': list(valid_fields.keys())
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Erro ao responder RNC {rnc_id}: {e}")
        logger.error(f"Traceback: {error_details}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500


@rnc.route('/api/rnc/<int:rnc_id>/response-status', methods=['GET'])
def get_response_status(rnc_id):
    """Verificar status de resposta obrigatória da RNC"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        user_id = session['user_id']
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar RNC e status de resposta
        cursor.execute('''
            SELECT 
                r.id, r.title, r.status, r.user_id, r.assigned_user_id,
                r.cause_rnc, r.action_rnc,
                u_creator.name as creator_name,
                u_assigned.name as assigned_name
            FROM rncs r
            LEFT JOIN users u_creator ON r.user_id = u_creator.id
            LEFT JOIN users u_assigned ON r.assigned_user_id = u_assigned.id
            WHERE r.id = ? AND (r.is_deleted = 0 OR r.is_deleted IS NULL)
        ''', (rnc_id,))
        
        rnc_data = cursor.fetchone()
        if not rnc_data:
            conn.close()
            return jsonify({'success': False, 'message': 'RNC não encontrada'}), 404
        
        (rid, title, status, creator_id, assigned_id, 
         cause_rnc, action_rnc, creator_name, assigned_name) = rnc_data
        
        # Verificar se usuário pode ver esta RNC
        can_access = False
        is_admin = False
        
        # Verificar se é admin
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        user_role = cursor.fetchone()
        if user_role and user_role[0] == 'admin':
            can_access = True
            is_admin = True
        # Verificar se é criador ou responsável
        elif user_id == creator_id or user_id == assigned_id:
            can_access = True
        else:
            # Verificar compartilhamento
            cursor.execute('''
                SELECT 1 FROM rnc_shares 
                WHERE rnc_id = ? AND shared_with_user_id = ? 
                LIMIT 1
            ''', (rnc_id, user_id))
            if cursor.fetchone():
                can_access = True
        
        if not can_access:
            conn.close()
            return jsonify({'success': False, 'message': 'Sem permissão para ver esta RNC'}), 403
        
        # Status de resposta
        response_complete = bool(cause_rnc and cause_rnc.strip() and action_rnc and action_rnc.strip())
        
        # Determinar quem deve responder
        needs_response_from = []
        if creator_id and not response_complete:
            needs_response_from.append({'user_id': creator_id, 'name': creator_name, 'role': 'creator'})
        if assigned_id and assigned_id != creator_id and not response_complete:
            needs_response_from.append({'user_id': assigned_id, 'name': assigned_name, 'role': 'assigned'})
        
        conn.close()
        
        return jsonify({
            'success': True,
            'rnc_id': rnc_id,
            'title': title,
            'status': status,
            'response_complete': response_complete,
            'cause_filled': bool(cause_rnc and cause_rnc.strip()),
            'action_filled': bool(action_rnc and action_rnc.strip()),
            'needs_response_from': needs_response_from,
            'current_user_can_respond': user_id in [creator_id, assigned_id] or is_admin,
            'current_response': {
                'cause_rnc': cause_rnc or '',
                'action_rnc': action_rnc or ''
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao verificar status de resposta RNC {rnc_id}: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

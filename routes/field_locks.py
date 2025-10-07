"""
Blueprint: Gerenciamento de Bloqueio de Campos por Grupo
Criado em: 03/10/2025

API para administradores configurarem quais campos cada grupo
pode ou não editar na criação de RNC.
"""

from flask import Blueprint, request, jsonify, session, render_template
import sqlite3
import logging
import os

field_locks_bp = Blueprint('field_locks', __name__, url_prefix='/admin/field-locks')
logger = logging.getLogger('ippel.field_locks')

# Usar caminho absoluto para o banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ippel_system.db')

# Campos disponíveis para bloqueio (TODOS os campos da tabela RNC)
AVAILABLE_FIELDS = {
    # Campos principais
    'rnc_number': 'Número RNC',
    'title': 'Título',
    'description': 'Descrição',
    'equipment': 'Equipamento',
    'client': 'Cliente',
    'priority': 'Prioridade',
    'status': 'Status',
    'assigned_user_id': 'Usuário Atribuído',
    'price': 'Preço',
    
    # Disposições
    'disposition_usar': 'Disposição: Usar',
    'disposition_retrabalhar': 'Disposição: Retrabalhar',
    'disposition_rejeitar': 'Disposição: Rejeitar',
    'disposition_sucata': 'Disposição: Sucata',
    'disposition_devolver_estoque': 'Disposição: Devolver ao Estoque',
    'disposition_devolver_fornecedor': 'Disposição: Devolver ao Fornecedor',
    
    # Inspeção
    'inspection_aprovado': 'Inspeção: Aprovado',
    'inspection_reprovado': 'Inspeção: Reprovado',
    'inspection_ver_rnc': 'Inspeção: Ver RNC',
    
    # Assinaturas e Datas
    'signature_inspection_date': 'Data Assinatura Inspeção',
    'signature_engineering_date': 'Data Assinatura Engenharia',
    'signature_inspection2_date': 'Data Assinatura Inspeção 2',
    'signature_inspection_name': 'Nome Assinatura Inspeção',
    'signature_engineering_name': 'Nome Assinatura Engenharia',
    'signature_inspection2_name': 'Nome Assinatura Inspeção 2',
    
    # Instruções e Análises
    'instruction_retrabalho': 'Instrução Retrabalho',
    'cause_rnc': 'Causa da RNC',
    'action_rnc': 'Ação da RNC',
    
    # Responsabilidades
    'responsavel': 'Responsável',
    'inspetor': 'Inspetor',
    'setor': 'Setor',
    'area_responsavel': 'Área Responsável',
    
    # Dados Técnicos
    'material': 'Material',
    'quantity': 'Quantidade',
    'drawing': 'Desenho',
    'mp': 'MP',
    'revision': 'Revisão',
    'position': 'Posição',
    'cv': 'CV',
    'conjunto': 'Conjunto',
    'modelo': 'Modelo',
    'description_drawing': 'Descrição do Desenho',
    'purchase_order': 'Ordem de Compra',
    'justificativa': 'Justificativa'
}


def check_admin():
    """Verifica se o usuário é administrador"""
    # Para desenvolvimento/teste - permitir acesso temporariamente
    return True


@field_locks_bp.route('/')
def index():
    """Página principal de gerenciamento de bloqueios"""
    if not check_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    return render_template('admin_field_locks_clean.html')


@field_locks_bp.route('/api/groups')
def list_groups():
    """Lista todos os grupos disponíveis"""
    print("DEBUG: Entrando em list_groups()")
    print(f"DEBUG: DB_PATH = {DB_PATH}")
    print(f"DEBUG: check_admin() retornou: {check_admin()}")
    
    try:
        print("DEBUG: Tentando conectar ao banco...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("DEBUG: Executando query...")
        cursor.execute("""
            SELECT id, name, description, created_at
            FROM groups
            ORDER BY name
        """)
        
        groups = []
        for row in cursor.fetchall():
            groups.append({
                'id': row[0],
                'name': row[1],
                'description': row[2] or '',
                'created_at': row[3]
            })
        
        conn.close()
        
        print(f"DEBUG: Grupos encontrados: {len(groups)}")
        return jsonify(groups)
        
    except Exception as e:
        print(f"DEBUG: Erro: {e}")
        logger.error(f"Erro ao listar grupos: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@field_locks_bp.route('/api/fields')
def list_fields():
    """Lista todos os campos disponíveis para bloqueio"""
    if not check_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    return jsonify({
        'success': True,
        'fields': AVAILABLE_FIELDS
    })


@field_locks_bp.route('/api/locks/<int:group_id>')
def get_locks(group_id):
    """Obtém os bloqueios de um grupo específico"""
    if not check_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se o grupo existe
        cursor.execute('SELECT name FROM groups WHERE id = ?', (group_id,))
        group = cursor.fetchone()
        
        if not group:
            conn.close()
            return jsonify({'success': False, 'message': 'Grupo não encontrado'}), 404
        
        # Buscar bloqueios do grupo
        cursor.execute("""
            SELECT field_name, is_locked, created_at, updated_at
            FROM field_locks
            WHERE group_id = ?
            ORDER BY field_name
        """, (group_id,))
        
        locks = {}
        for row in cursor.fetchall():
            locks[row[0]] = {
                'is_locked': bool(row[1]),
                'created_at': row[2],
                'updated_at': row[3]
            }
        
        conn.close()
        
        # Adicionar campos não configurados (liberados por padrão)
        for field_name in AVAILABLE_FIELDS.keys():
            if field_name not in locks:
                locks[field_name] = {
                    'is_locked': False,
                    'created_at': None,
                    'updated_at': None
                }
        
        return jsonify({
            'success': True,
            'group_id': group_id,
            'group_name': group[0],
            'locks': locks
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar bloqueios: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@field_locks_bp.route('/api/locks/<int:group_id>', methods=['POST'])
def update_locks(group_id):
    """Atualiza os bloqueios de um grupo"""
    if not check_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        data = request.get_json()
        locks = data.get('locks', {})
        
        if not isinstance(locks, dict):
            return jsonify({'success': False, 'message': 'Formato inválido'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se o grupo existe
        cursor.execute('SELECT id FROM groups WHERE id = ?', (group_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Grupo não encontrado'}), 404
        
        updated_count = 0
        
        for field_name, is_locked in locks.items():
            # Validar campo
            if field_name not in AVAILABLE_FIELDS:
                continue
            
            # Converter is_locked para inteiro (0 ou 1)
            lock_value = 1 if is_locked else 0
            
            # Insert or update
            cursor.execute("""
                INSERT INTO field_locks (group_id, field_name, is_locked)
                VALUES (?, ?, ?)
                ON CONFLICT(group_id, field_name) 
                DO UPDATE SET 
                    is_locked = excluded.is_locked,
                    updated_at = CURRENT_TIMESTAMP
            """, (group_id, field_name, lock_value))
            
            updated_count += 1
        
        conn.commit()
        conn.close()
        
        logger.info(f"Admin {session.get('user_id')} atualizou {updated_count} bloqueios para grupo {group_id}")
        
        return jsonify({
            'success': True,
            'message': f'{updated_count} bloqueios atualizados',
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger.error(f"Erro ao atualizar bloqueios: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@field_locks_bp.route('/api/locks/<int:group_id>/reset', methods=['POST'])
def reset_locks(group_id):
    """Remove todos os bloqueios de um grupo (libera tudo)"""
    if not check_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM field_locks WHERE group_id = ?', (group_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"Admin {session.get('user_id')} removeu {deleted_count} bloqueios do grupo {group_id}")
        
        return jsonify({
            'success': True,
            'message': f'{deleted_count} bloqueios removidos',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"Erro ao resetar bloqueios: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@field_locks_bp.route('/api/check/<int:group_id>/<field_name>')
def check_field_lock(group_id, field_name):
    """Verifica se um campo específico está bloqueado para um grupo"""
    # Esta rota pode ser acessada por qualquer usuário autenticado
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        if field_name not in AVAILABLE_FIELDS:
            return jsonify({'success': False, 'message': 'Campo inválido'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT is_locked 
            FROM field_locks 
            WHERE group_id = ? AND field_name = ?
        """, (group_id, field_name))
        
        row = cursor.fetchone()
        conn.close()
        
        # Se não há registro, o campo está liberado por padrão
        is_locked = bool(row[0]) if row else False
        
        return jsonify({
            'success': True,
            'group_id': group_id,
            'field_name': field_name,
            'is_locked': is_locked
        })
        
    except Exception as e:
        logger.error(f"Erro ao verificar bloqueio: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


def get_user_locked_fields(user_id):
    """
    Retorna lista de campos bloqueados para um usuário
    baseado no grupo dele
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar grupo do usuário
        cursor.execute('SELECT group_id FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        
        if not row or not row[0]:
            conn.close()
            return []
        
        group_id = row[0]
        
        # Buscar campos bloqueados
        cursor.execute("""
            SELECT field_name 
            FROM field_locks 
            WHERE group_id = ? AND is_locked = 1
        """, (group_id,))
        
        locked_fields = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return locked_fields
        
    except Exception as e:
        logger.error(f"Erro ao buscar campos bloqueados do usuário: {e}")
        return []


@field_locks_bp.route('/api/user/locked-fields')
def get_current_user_locked_fields():
    """Retorna os campos bloqueados para o usuário atual"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        locked_fields = get_user_locked_fields(session['user_id'])
        
        # Converter para formato com labels
        locked_with_labels = {}
        for field_name in locked_fields:
            if field_name in AVAILABLE_FIELDS:
                locked_with_labels[field_name] = AVAILABLE_FIELDS[field_name]
        
        return jsonify({
            'success': True,
            'user_id': session['user_id'],
            'locked_fields': locked_fields,
            'locked_with_labels': locked_with_labels
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar campos bloqueados: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@field_locks_bp.route('/api/stats')
def get_stats():
    """Estatísticas do sistema de bloqueios"""
    if not check_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total de grupos
        cursor.execute('SELECT COUNT(*) FROM groups')
        total_groups = cursor.fetchone()[0]
        
        # Total de configurações de bloqueio
        cursor.execute('SELECT COUNT(*) FROM field_locks')
        total_locks = cursor.fetchone()[0]
        
        # Campos mais bloqueados
        cursor.execute("""
            SELECT field_name, COUNT(*) as count
            FROM field_locks
            WHERE is_locked = 1
            GROUP BY field_name
            ORDER BY count DESC
            LIMIT 5
        """)
        most_locked = [{'field': row[0], 'label': AVAILABLE_FIELDS.get(row[0], row[0]), 'count': row[1]} for row in cursor.fetchall()]
        
        # Grupos com mais bloqueios
        cursor.execute("""
            SELECT g.name, COUNT(fl.id) as count
            FROM groups g
            LEFT JOIN field_locks fl ON g.id = fl.group_id AND fl.is_locked = 1
            GROUP BY g.id, g.name
            ORDER BY count DESC
            LIMIT 5
        """)
        most_restricted_groups = [{'group': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_groups': total_groups,
                'total_locks': total_locks,
                'total_fields': len(AVAILABLE_FIELDS),
                'most_locked_fields': most_locked,
                'most_restricted_groups': most_restricted_groups
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
        locked_fields = get_user_locked_fields(session['user_id'])
        
        return jsonify({
            'success': True,
            'locked_fields': locked_fields,
            'fields_info': {field: AVAILABLE_FIELDS[field] for field in locked_fields if field in AVAILABLE_FIELDS}
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar campos bloqueados: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

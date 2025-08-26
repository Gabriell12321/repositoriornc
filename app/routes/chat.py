from flask import Blueprint, request, jsonify, session
import sqlite3

bp = Blueprint('chat', __name__)


@bp.route('/api/private-chat/messages/<int:contact_id>')
def get_private_messages(contact_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        limit = request.args.get('limit', type=int)
        user_id = session['user_id']
        DB_PATH = 'ippel_system.db'
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        query = '''
            SELECT pm.id, pm.sender_id, pm.recipient_id, pm.message, pm.message_type,
                   pm.is_read, pm.created_at, u.name as user_name, u.department
            FROM private_messages pm
            JOIN users u ON pm.sender_id = u.id
            WHERE (pm.sender_id = ? AND pm.recipient_id = ?) 
               OR (pm.sender_id = ? AND pm.recipient_id = ?)
            ORDER BY pm.created_at DESC
        '''
        if limit:
            query += f' LIMIT {limit}'
        cursor.execute(query, (user_id, contact_id, contact_id, user_id))
        messages = cursor.fetchall()
        conn.close()
        messages_list = []
        for msg in messages:
            messages_list.append({
                'id': msg[0],
                'sender_id': msg[1],
                'recipient_id': msg[2],
                'message': msg[3],
                'message_type': msg[4],
                'is_read': msg[5],
                'created_at': msg[6],
                'user_name': msg[7],
                'department': msg[8],
                'user_id': msg[1]
            })
        if not limit or limit > 1:
            messages_list.reverse()
        return jsonify({'success': True, 'messages': messages_list})
    except Exception:
        return jsonify({'success': False, 'message': 'Erro interno: falha ao buscar mensagens'}), 500


@bp.route('/api/private-chat/unread-count/<int:contact_id>')
def get_unread_count(contact_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        user_id = session['user_id']
        DB_PATH = 'ippel_system.db'
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM private_messages
            WHERE sender_id = ? AND recipient_id = ? AND is_read = 0
        ''', (contact_id, user_id))
        count = cursor.fetchone()[0]
        conn.close()
        return jsonify({'success': True, 'count': count})
    except Exception:
        return jsonify({'success': False, 'message': 'Erro interno: falha ao contar mensagens'}), 500

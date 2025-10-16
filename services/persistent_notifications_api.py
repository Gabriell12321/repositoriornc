#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔔 Sistema de Notificações Persistentes - Frontend
Sistema que mostra notificações "chatas" até o usuário responder
"""

import sqlite3
import os
from flask import Blueprint, jsonify, request, session
import logging

logger = logging.getLogger(__name__)

# Blueprint para as APIs de notificações persistentes
persistent_notifications_bp = Blueprint('persistent_notifications', __name__)

DB_PATH = 'ippel_system.db'

@persistent_notifications_bp.route('/api/persistent-notifications/pending', methods=['GET'])
def get_pending_notifications():
    """API para buscar notificações pendentes (não respondidas) do usuário"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar notificações persistentes não respondidas
        cursor.execute("""
            SELECT 
                pn.id,
                pn.rnc_id,
                pn.change_type,
                pn.change_details,
                pn.created_at,
                pn.created_by_user_id,
                u.name as created_by_name,
                u.department as created_by_dept,
                r.title as rnc_title,
                r.rnc_number as rnc_number
            FROM rnc_change_notifications pn
            LEFT JOIN users u ON pn.created_by_user_id = u.id
            LEFT JOIN rncs r ON pn.rnc_id = r.id
            WHERE pn.id IN (
                SELECT notification_id 
                FROM rnc_notification_recipients 
                WHERE user_id = ? AND is_responded = 0
            )
            ORDER BY pn.created_at DESC
            LIMIT 10
        """, (user_id,))
        
        notifications = []
        for row in cursor.fetchall():
            notification_id, rnc_id, change_type, change_details, created_at, created_by_user_id, created_by_name, created_by_dept, rnc_title, rnc_number = row
            
            # Parse change_details se for JSON
            try:
                import json
                details = json.loads(change_details) if change_details else {}
            except:
                details = {}
            
            # Criar mensagem baseada no tipo
            if change_type == 'create':
                message = f"📝 {created_by_name} criou uma nova RNC: {rnc_title}"
                action_text = "Ver RNC"
            elif change_type == 'update':
                message = f"✏️ {created_by_name} atualizou a RNC: {rnc_title}"
                action_text = "Ver Alterações"
            elif change_type == 'chat_response':
                chat_msg = details.get('message', '')[:50] + ('...' if len(details.get('message', '')) > 50 else '')
                message = f"💬 {created_by_name} respondeu: {chat_msg}"
                action_text = "Ver Chat"
            else:
                message = f"🔔 {created_by_name} fez alterações na RNC: {rnc_title}"
                action_text = "Ver RNC"
            
            notifications.append({
                'id': notification_id,
                'rnc_id': rnc_id,
                'rnc_number': rnc_number,
                'rnc_title': rnc_title,
                'change_type': change_type,
                'message': message,
                'action_text': action_text,
                'created_at': created_at,
                'created_by_name': created_by_name,
                'created_by_dept': created_by_dept,
                'details': details
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar notificações pendentes: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@persistent_notifications_bp.route('/api/persistent-notifications/<int:notification_id>/respond', methods=['POST'])
def respond_to_notification(notification_id):
    """API para marcar notificação como respondida"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    data = request.get_json() or {}
    response_text = data.get('response', '')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Marcar como respondida
        cursor.execute("""
            UPDATE rnc_notification_recipients
            SET is_responded = 1, 
                response_text = ?,
                responded_at = CURRENT_TIMESTAMP
            WHERE notification_id = ? AND user_id = ?
        """, (response_text, notification_id, user_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Notificação não encontrada'}), 404
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Usuário {user_id} respondeu à notificação {notification_id}")
        
        return jsonify({
            'success': True,
            'message': 'Resposta registrada com sucesso!'
        })
        
    except Exception as e:
        logger.error(f"Erro ao responder notificação {notification_id}: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@persistent_notifications_bp.route('/api/persistent-notifications/<int:notification_id>/dismiss', methods=['POST'])
def dismiss_notification(notification_id):
    """API para dispensar notificação temporariamente (não remove, mas para de incomodar)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    user_id = session['user_id']
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Marcar como temporariamente dispensada (mas não respondida)
        cursor.execute("""
            UPDATE rnc_notification_recipients
            SET is_dismissed = 1,
                dismissed_at = CURRENT_TIMESTAMP
            WHERE notification_id = ? AND user_id = ?
        """, (notification_id, user_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Notificação não encontrada'}), 404
        
        conn.commit()
        conn.close()
        
        logger.info(f"📵 Usuário {user_id} dispensou temporariamente a notificação {notification_id}")
        
        return jsonify({
            'success': True,
            'message': 'Notificação dispensada'
        })
        
    except Exception as e:
        logger.error(f"Erro ao dispensar notificação {notification_id}: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

def register_persistent_notifications_routes(app):
    """Registrar as rotas de notificações persistentes no app Flask"""
    app.register_blueprint(persistent_notifications_bp)
    logger.info("✅ Rotas de notificações persistentes registradas")
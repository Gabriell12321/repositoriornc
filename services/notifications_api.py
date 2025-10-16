#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIs para Sistema de Notificações Melhorado
Endpoints REST para gerenciamento de notificações em tempo real
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
import logging
from .enhanced_notifications import (
    enhanced_notification_service,
    NotificationType,
    NotificationPriority,
    NotificationChannel
)

# Configurar logging
logger = logging.getLogger(__name__)

# Blueprint para APIs de notificação
notifications_bp = Blueprint('notifications_api', __name__)


@notifications_bp.route('/api/notifications/unread', methods=['GET'])
def get_unread_notifications():
    """API para buscar notificações não lidas do usuário"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        user_id = session['user_id']
        
        # Buscar notificações não lidas
        notifications = enhanced_notification_service.get_user_notifications(
            user_id=user_id,
            unread_only=True,
            limit=50
        )
        
        # Contar total não lidas
        count = enhanced_notification_service.get_unread_count(user_id)
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': count
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar notificações não lidas: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500


@notifications_bp.route('/api/notifications/all', methods=['GET'])
def get_all_notifications():
    """API para buscar todas as notificações do usuário com paginação"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        user_id = session['user_id']
        
        # Parâmetros de paginação
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)  # Máximo 100
        offset = (page - 1) * per_page
        
        # Filtros
        notification_type = request.args.get('type')
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        # Buscar notificações
        notifications = enhanced_notification_service.get_user_notifications(
            user_id=user_id,
            unread_only=unread_only,
            limit=per_page,
            offset=offset,
            notification_type=notification_type
        )
        
        # Contar total para paginação
        count = enhanced_notification_service.get_unread_count(user_id) if unread_only else len(notifications)
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': count,
                'pages': (count + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar notificações: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500


@notifications_bp.route('/api/notifications/mark-read', methods=['POST'])
def mark_notifications_read():
    """API para marcar notificações como lidas"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        if not data or 'notification_ids' not in data:
            return jsonify({
                'success': False,
                'message': 'IDs das notificações são obrigatórios'
            }), 400
        
        notification_ids = data['notification_ids']
        if not isinstance(notification_ids, list):
            notification_ids = [notification_ids]
        
        # Marcar como lidas
        success = enhanced_notification_service.mark_as_read(notification_ids, user_id)
        
        if success:
            # Retornar nova contagem
            new_count = enhanced_notification_service.get_unread_count(user_id)
            return jsonify({
                'success': True,
                'message': 'Notificações marcadas como lidas',
                'unread_count': new_count
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao marcar notificações como lidas'
            }), 500
        
    except Exception as e:
        logger.error(f"Erro ao marcar notificações como lidas: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500


@notifications_bp.route('/api/notifications/dismiss', methods=['POST'])
def dismiss_notifications():
    """API para dispensar notificações"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        if not data or 'notification_ids' not in data:
            return jsonify({
                'success': False,
                'message': 'IDs das notificações são obrigatórios'
            }), 400
        
        notification_ids = data['notification_ids']
        if not isinstance(notification_ids, list):
            notification_ids = [notification_ids]
        
        # Dispensar notificações
        success = enhanced_notification_service.mark_as_dismissed(notification_ids, user_id)
        
        if success:
            # Retornar nova contagem
            new_count = enhanced_notification_service.get_unread_count(user_id)
            return jsonify({
                'success': True,
                'message': 'Notificações dispensadas',
                'unread_count': new_count
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao dispensar notificações'
            }), 500
        
    except Exception as e:
        logger.error(f"Erro ao dispensar notificações: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500


@notifications_bp.route('/api/notifications/rnc/<int:rnc_id>/dismiss', methods=['POST'])
def dismiss_rnc_notifications(rnc_id):
    """API para dispensar todas as notificações de uma RNC específica"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        user_id = session['user_id']
        
        # Buscar todas as notificações não lidas desta RNC
        import sqlite3
        conn = sqlite3.connect(enhanced_notification_service.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM notifications 
            WHERE to_user_id = ? AND rnc_id = ? AND is_read = 0 AND is_dismissed = 0
        """, (user_id, rnc_id))
        
        notification_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if notification_ids:
            # Dispensar notificações
            success = enhanced_notification_service.mark_as_dismissed(notification_ids, user_id)
            
            if success:
                # Também marcar como lidas
                enhanced_notification_service.mark_as_read(notification_ids, user_id)
                
                # Retornar nova contagem
                new_count = enhanced_notification_service.get_unread_count(user_id)
                logger.info(f"✅ {len(notification_ids)} notificações da RNC {rnc_id} dispensadas para usuário {user_id}")
                
                return jsonify({
                    'success': True,
                    'message': f'{len(notification_ids)} notificações dispensadas',
                    'dismissed_count': len(notification_ids),
                    'unread_count': new_count
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Erro ao dispensar notificações'
                }), 500
        else:
            # Nenhuma notificação para dispensar
            return jsonify({
                'success': True,
                'message': 'Nenhuma notificação para dispensar',
                'dismissed_count': 0,
                'unread_count': enhanced_notification_service.get_unread_count(user_id)
            })
        
    except Exception as e:
        logger.error(f"Erro ao dispensar notificações da RNC: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500


@notifications_bp.route('/api/notifications/create', methods=['POST'])
def create_notification():
    """API para criar notificação (para admins/sistema)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        # Verificar se usuário tem permissão para criar notificações
        from services.permissions import has_permission
        if not has_permission(session['user_id'], 'admin_access'):
            return jsonify({
                'success': False,
                'message': 'Sem permissão para criar notificações'
            }), 403
        
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['type', 'to_user_id', 'data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo obrigatório: {field}'
                }), 400
        
        # Criar notificação
        notification_id = enhanced_notification_service.create_notification(
            notification_type=data['type'],
            to_user_id=data['to_user_id'],
            data=data['data'],
            from_user_id=session['user_id'],
            rnc_id=data.get('rnc_id'),
            priority=data.get('priority'),
            channels=[NotificationChannel(c) for c in data.get('channels', ['in_app'])],
            expires_in_hours=data.get('expires_in_hours'),
            group_id=data.get('group_id')
        )
        
        if notification_id:
            return jsonify({
                'success': True,
                'message': 'Notificação criada com sucesso',
                'notification_id': notification_id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao criar notificação'
            }), 500
        
    except Exception as e:
        logger.error(f"Erro ao criar notificação: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500


@notifications_bp.route('/api/notifications/count', methods=['GET'])
def get_notification_count():
    """API para buscar contagem de notificações não lidas"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        user_id = session['user_id']
        count = enhanced_notification_service.get_unread_count(user_id)
        
        return jsonify({
            'success': True,
            'count': count
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar contagem: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500


@notifications_bp.route('/api/notifications/preferences', methods=['GET'])
def get_notification_preferences():
    """API para buscar preferências de notificação do usuário"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        user_id = session['user_id']
        
        # Buscar preferências (implementar quando necessário)
        # Por ora, retornar preferências padrão
        preferences = {
            'rnc_created': {'in_app': True, 'email': True, 'browser': True},
            'rnc_assigned': {'in_app': True, 'email': True, 'browser': True},
            'rnc_updated': {'in_app': True, 'email': False, 'browser': True},
            'rnc_commented': {'in_app': True, 'email': False, 'browser': True},
            'rnc_finalized': {'in_app': True, 'email': True, 'browser': True},
        }
        
        return jsonify({
            'success': True,
            'preferences': preferences
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar preferências: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500


@notifications_bp.route('/api/notifications/preferences', methods=['POST'])
def update_notification_preferences():
    """API para atualizar preferências de notificação"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        if not data or 'preferences' not in data:
            return jsonify({
                'success': False,
                'message': 'Preferências são obrigatórias'
            }), 400
        
        # Salvar preferências (implementar quando necessário)
        # Por ora, apenas retornar sucesso
        
        return jsonify({
            'success': True,
            'message': 'Preferências atualizadas com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao atualizar preferências: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500


@notifications_bp.route('/api/notifications/stats', methods=['GET'])
def get_notification_stats():
    """API para buscar estatísticas de notificação (admin)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        # Verificar permissão de admin
        from services.permissions import has_permission
        if not has_permission(session['user_id'], 'admin_access'):
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        # Buscar estatísticas dos últimos 30 dias
        import sqlite3
        conn = sqlite3.connect(enhanced_notification_service.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT date, notification_type, channel, 
                   sent_count, read_count, click_count
            FROM notification_stats
            WHERE date >= date('now', '-30 days')
            ORDER BY date DESC, notification_type, channel
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        stats = []
        for row in rows:
            stats.append({
                'date': row[0],
                'type': row[1],
                'channel': row[2],
                'sent': row[3],
                'read': row[4],
                'clicked': row[5],
                'read_rate': round((row[4] / row[3]) * 100, 1) if row[3] > 0 else 0,
                'click_rate': round((row[5] / row[3]) * 100, 1) if row[3] > 0 else 0
            })
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500


# Funções de conveniência para criar notificações específicas de RNC
def notify_rnc_created(rnc_id: int, rnc_number: str, creator_id: int, creator_name: str):
    """Notifica sobre criação de RNC"""
    try:
        # Buscar usuários para notificar (admins, grupos, etc.)
        import sqlite3
        conn = sqlite3.connect(enhanced_notification_service.db_path)
        cursor = conn.cursor()
        
        # Buscar admins
        cursor.execute("SELECT id FROM users WHERE role = 'admin'")
        admin_ids = [row[0] for row in cursor.fetchall()]
        
        # Buscar usuários de grupos relevantes
        cursor.execute("""
            SELECT DISTINCT u.id 
            FROM users u 
            JOIN groups g ON u.group_id = g.id 
            WHERE g.name LIKE '%RNC%' OR g.name LIKE '%Qualidade%'
        """)
        group_user_ids = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # Combinar e remover duplicatas
        user_ids = list(set(admin_ids + group_user_ids))
        
        # Remover o criador da lista
        if creator_id in user_ids:
            user_ids.remove(creator_id)
        
        # Criar notificações
        for user_id in user_ids:
            enhanced_notification_service.create_notification(
                notification_type=NotificationType.RNC_CREATED,
                to_user_id=user_id,
                data={
                    'rnc_number': rnc_number,
                    'creator_name': creator_name,
                    'action_url': f'/rnc/{rnc_id}'
                },
                from_user_id=creator_id,
                rnc_id=rnc_id,
                channels=[NotificationChannel.IN_APP, NotificationChannel.BROWSER]
            )
        
        logger.info(f"Notificações de criação enviadas para {len(user_ids)} usuários")
        
    except Exception as e:
        logger.error(f"Erro ao notificar criação de RNC: {e}")


def notify_rnc_assigned(rnc_id: int, rnc_number: str, assigned_user_id: int, assigner_id: int, assigner_name: str):
    """Notifica sobre atribuição de RNC"""
    try:
        enhanced_notification_service.create_notification(
            notification_type=NotificationType.RNC_ASSIGNED,
            to_user_id=assigned_user_id,
            data={
                'rnc_number': rnc_number,
                'assigner_name': assigner_name,
                'action_url': f'/rnc/{rnc_id}'
            },
            from_user_id=assigner_id,
            rnc_id=rnc_id,
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL, NotificationChannel.BROWSER]
        )
        
        logger.info(f"Notificação de atribuição enviada para usuário {assigned_user_id}")
        
    except Exception as e:
        logger.error(f"Erro ao notificar atribuição de RNC: {e}")


def notify_rnc_commented(rnc_id: int, rnc_number: str, commenter_id: int, commenter_name: str, participants: list):
    """Notifica sobre comentário em RNC"""
    try:
        # Notificar todos os participantes exceto o comentarista
        for user_id in participants:
            if user_id != commenter_id:
                enhanced_notification_service.create_notification(
                    notification_type=NotificationType.RNC_COMMENTED,
                    to_user_id=user_id,
                    data={
                        'rnc_number': rnc_number,
                        'commenter_name': commenter_name,
                        'action_url': f'/rnc/{rnc_id}/chat'
                    },
                    from_user_id=commenter_id,
                    rnc_id=rnc_id,
                    channels=[NotificationChannel.IN_APP, NotificationChannel.BROWSER]
                )
        
        logger.info(f"Notificações de comentário enviadas para {len(participants)-1} usuários")
        
    except Exception as e:
        logger.error(f"Erro ao notificar comentário de RNC: {e}")


def notify_rnc_finalized(rnc_id: int, rnc_number: str, finalizer_id: int, finalizer_name: str):
    """Notifica sobre finalização de RNC"""
    try:
        # Buscar stakeholders da RNC (criador, participantes, etc.)
        import sqlite3
        conn = sqlite3.connect(enhanced_notification_service.db_path)
        cursor = conn.cursor()
        
        # Buscar criador e responsável
        cursor.execute("SELECT user_id, assigned_user_id FROM rncs WHERE id = ?", (rnc_id,))
        row = cursor.fetchone()
        
        stakeholders = []
        if row:
            if row[0]:  # criador
                stakeholders.append(row[0])
            if row[1]:  # responsável
                stakeholders.append(row[1])
        
        # Buscar usuários que comentaram
        cursor.execute("""
            SELECT DISTINCT user_id 
            FROM chat_messages 
            WHERE rnc_id = ?
        """, (rnc_id,))
        
        for comment_row in cursor.fetchall():
            stakeholders.append(comment_row[0])
        
        conn.close()
        
        # Remover duplicatas e o finalizador
        stakeholders = list(set(stakeholders))
        if finalizer_id in stakeholders:
            stakeholders.remove(finalizer_id)
        
        # Criar notificações
        for user_id in stakeholders:
            enhanced_notification_service.create_notification(
                notification_type=NotificationType.RNC_FINALIZED,
                to_user_id=user_id,
                data={
                    'rnc_number': rnc_number,
                    'finalizer_name': finalizer_name,
                    'action_url': f'/rnc/{rnc_id}'
                },
                from_user_id=finalizer_id,
                rnc_id=rnc_id,
                priority=NotificationPriority.HIGH,
                channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL, NotificationChannel.BROWSER]
            )
        
        logger.info(f"Notificações de finalização enviadas para {len(stakeholders)} usuários")
        
    except Exception as e:
        logger.error(f"Erro ao notificar finalização de RNC: {e}")


# Exportar blueprint
__all__ = ['notifications_bp', 'notify_rnc_created', 'notify_rnc_assigned', 'notify_rnc_commented', 'notify_rnc_finalized']
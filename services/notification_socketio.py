#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integração do Sistema de Notificações Melhorado com Socket.IO
Comunicação em tempo real para notificações push
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request, session
import json
import logging
from datetime import datetime
from .enhanced_notifications import (
    enhanced_notification_service,
    NotificationType,
    NotificationChannel
)

# Configurar logging
logger = logging.getLogger(__name__)

# Armazenar conexões ativas
active_connections = {}


def init_notification_socketio(socketio: SocketIO):
    """Inicializar eventos Socket.IO para notificações"""
    
    @socketio.on('connect', namespace='/notifications')
    def on_connect():
        """Usuário conectou ao namespace de notificações"""
        if 'user_id' not in session:
            logger.warning("Conexão não autorizada no namespace de notificações")
            return False
        
        user_id = session['user_id']
        connection_id = request.sid
        
        # Armazenar conexão
        if user_id not in active_connections:
            active_connections[user_id] = set()
        active_connections[user_id].add(connection_id)
        
        # Juntar à room do usuário
        join_room(f"user_{user_id}")
        
        logger.info(f"Usuário {user_id} conectado às notificações (SID: {connection_id})")
        
        # Enviar notificações não lidas
        try:
            unread_notifications = enhanced_notification_service.get_user_notifications(
                user_id=user_id,
                unread_only=True,
                limit=10
            )
            
            unread_count = enhanced_notification_service.get_unread_count(user_id)
            
            emit('notifications_sync', {
                'notifications': unread_notifications,
                'count': unread_count
            })
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar notificações para usuário {user_id}: {e}")
    
    
    @socketio.on('disconnect', namespace='/notifications')
    def on_disconnect():
        """Usuário desconectou do namespace de notificações"""
        if 'user_id' not in session:
            return
        
        user_id = session['user_id']
        connection_id = request.sid
        
        # Remover conexão
        if user_id in active_connections:
            active_connections[user_id].discard(connection_id)
            if not active_connections[user_id]:
                del active_connections[user_id]
        
        # Sair da room
        leave_room(f"user_{user_id}")
        
        logger.info(f"Usuário {user_id} desconectado das notificações (SID: {connection_id})")
    
    
    @socketio.on('mark_notification_read', namespace='/notifications')
    def on_mark_read(data):
        """Marcar notificação como lida via Socket.IO"""
        if 'user_id' not in session:
            emit('error', {'message': 'Não autorizado'})
            return
        
        try:
            user_id = session['user_id']
            notification_id = data.get('notification_id')
            
            if not notification_id:
                emit('error', {'message': 'ID da notificação é obrigatório'})
                return
            
            # Marcar como lida
            success = enhanced_notification_service.mark_as_read([notification_id], user_id)
            
            if success:
                # Buscar nova contagem
                new_count = enhanced_notification_service.get_unread_count(user_id)
                
                emit('notification_read', {
                    'notification_id': notification_id,
                    'unread_count': new_count
                })
                
                logger.debug(f"Notificação {notification_id} marcada como lida para usuário {user_id}")
            else:
                emit('error', {'message': 'Erro ao marcar notificação como lida'})
                
        except Exception as e:
            logger.error(f"Erro ao marcar notificação como lida via Socket.IO: {e}")
            emit('error', {'message': 'Erro interno do servidor'})
    
    
    @socketio.on('mark_all_read', namespace='/notifications')
    def on_mark_all_read():
        """Marcar todas as notificações como lidas"""
        if 'user_id' not in session:
            emit('error', {'message': 'Não autorizado'})
            return
        
        try:
            user_id = session['user_id']
            
            # Buscar todas as notificações não lidas
            unread_notifications = enhanced_notification_service.get_user_notifications(
                user_id=user_id,
                unread_only=True,
                limit=1000  # Assumindo que não há mais de 1000 não lidas
            )
            
            notification_ids = [n['id'] for n in unread_notifications]
            
            if notification_ids:
                success = enhanced_notification_service.mark_as_read(notification_ids, user_id)
                
                if success:
                    emit('all_notifications_read', {
                        'count': len(notification_ids)
                    })
                    
                    logger.info(f"{len(notification_ids)} notificações marcadas como lidas para usuário {user_id}")
                else:
                    emit('error', {'message': 'Erro ao marcar notificações como lidas'})
            else:
                emit('all_notifications_read', {'count': 0})
                
        except Exception as e:
            logger.error(f"Erro ao marcar todas as notificações como lidas: {e}")
            emit('error', {'message': 'Erro interno do servidor'})
    
    
    @socketio.on('dismiss_notification', namespace='/notifications')
    def on_dismiss_notification(data):
        """Dispensar notificação"""
        if 'user_id' not in session:
            emit('error', {'message': 'Não autorizado'})
            return
        
        try:
            user_id = session['user_id']
            notification_id = data.get('notification_id')
            
            if not notification_id:
                emit('error', {'message': 'ID da notificação é obrigatório'})
                return
            
            # Dispensar notificação
            success = enhanced_notification_service.mark_as_dismissed([notification_id], user_id)
            
            if success:
                # Buscar nova contagem
                new_count = enhanced_notification_service.get_unread_count(user_id)
                
                emit('notification_dismissed', {
                    'notification_id': notification_id,
                    'unread_count': new_count
                })
                
                logger.debug(f"Notificação {notification_id} dispensada para usuário {user_id}")
            else:
                emit('error', {'message': 'Erro ao dispensar notificação'})
                
        except Exception as e:
            logger.error(f"Erro ao dispensar notificação via Socket.IO: {e}")
            emit('error', {'message': 'Erro interno do servidor'})
    
    
    @socketio.on('get_notifications', namespace='/notifications')
    def on_get_notifications(data):
        """Buscar notificações via Socket.IO"""
        if 'user_id' not in session:
            emit('error', {'message': 'Não autorizado'})
            return
        
        try:
            user_id = session['user_id']
            
            # Parâmetros opcionais
            unread_only = data.get('unread_only', False)
            limit = min(data.get('limit', 20), 100)  # Máximo 100
            offset = data.get('offset', 0)
            
            # Buscar notificações
            notifications = enhanced_notification_service.get_user_notifications(
                user_id=user_id,
                unread_only=unread_only,
                limit=limit,
                offset=offset
            )
            
            count = enhanced_notification_service.get_unread_count(user_id)
            
            emit('notifications_list', {
                'notifications': notifications,
                'unread_count': count
            })
            
        except Exception as e:
            logger.error(f"Erro ao buscar notificações via Socket.IO: {e}")
            emit('error', {'message': 'Erro interno do servidor'})


def send_realtime_notification(user_id: int, notification_data: dict, socketio: SocketIO):
    """
    Enviar notificação em tempo real via Socket.IO
    
    Args:
        user_id: ID do usuário destinatário
        notification_data: Dados da notificação
        socketio: Instância do SocketIO
    """
    try:
        # Verificar se usuário está conectado
        if user_id in active_connections:
            # Enviar para todas as conexões do usuário
            socketio.emit(
                'new_notification',
                notification_data,
                room=f"user_{user_id}",
                namespace='/notifications'
            )
            
            # Enviar também contagem atualizada
            unread_count = enhanced_notification_service.get_unread_count(user_id)
            socketio.emit(
                'unread_count_update',
                {'count': unread_count},
                room=f"user_{user_id}",
                namespace='/notifications'
            )
            
            logger.debug(f"Notificação em tempo real enviada para usuário {user_id}")
            return True
        else:
            logger.debug(f"Usuário {user_id} não está conectado para receber notificação em tempo real")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao enviar notificação em tempo real: {e}")
        return False


def broadcast_system_notification(notification_data: dict, socketio: SocketIO, user_ids: list = None):
    """
    Transmitir notificação do sistema para múltiplos usuários
    
    Args:
        notification_data: Dados da notificação
        socketio: Instância do SocketIO
        user_ids: Lista de IDs de usuários (se None, envia para todos conectados)
    """
    try:
        if user_ids:
            # Enviar para usuários específicos
            for user_id in user_ids:
                if user_id in active_connections:
                    socketio.emit(
                        'system_notification',
                        notification_data,
                        room=f"user_{user_id}",
                        namespace='/notifications'
                    )
        else:
            # Enviar para todos os usuários conectados
            for user_id in active_connections.keys():
                socketio.emit(
                    'system_notification',
                    notification_data,
                    room=f"user_{user_id}",
                    namespace='/notifications'
                )
        
        logger.info(f"Notificação do sistema transmitida para {len(user_ids) if user_ids else len(active_connections)} usuários")
        
    except Exception as e:
        logger.error(f"Erro ao transmitir notificação do sistema: {e}")


def get_connected_users():
    """Obter lista de usuários conectados"""
    return list(active_connections.keys())


def get_user_connection_count(user_id: int):
    """Obter número de conexões de um usuário"""
    return len(active_connections.get(user_id, set()))


def is_user_online(user_id: int):
    """Verificar se usuário está online"""
    return user_id in active_connections


# Integração com enhanced_notifications para envio automático
class RealtimeNotificationService:
    """Serviço para integrar notificações com Socket.IO"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
    
    def send_notification(self, user_id: int, notification_type: NotificationType, data: dict, **kwargs):
        """
        Criar e enviar notificação com suporte a tempo real
        
        Args:
            user_id: ID do usuário destinatário
            notification_type: Tipo da notificação
            data: Dados da notificação
            **kwargs: Argumentos adicionais para enhanced_notification_service.create_notification
        """
        try:
            # Verificar se deve incluir canal in-app
            channels = kwargs.get('channels', [NotificationChannel.IN_APP])
            if NotificationChannel.IN_APP not in channels:
                channels.append(NotificationChannel.IN_APP)
            kwargs['channels'] = channels
            
            # Criar notificação no banco
            notification_id = enhanced_notification_service.create_notification(
                notification_type=notification_type,
                to_user_id=user_id,
                data=data,
                **kwargs
            )
            
            if notification_id:
                # Preparar dados para Socket.IO
                notification_data = {
                    'id': notification_id,
                    'type': notification_type.value,
                    'data': data,
                    'created_at': datetime.now().isoformat(),
                    'read_at': None,
                    'dismissed_at': None
                }
                
                # Enviar em tempo real se usuário estiver conectado
                if is_user_online(user_id):
                    send_realtime_notification(user_id, notification_data, self.socketio)
                
                return notification_id
            else:
                logger.error(f"Falha ao criar notificação para usuário {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao enviar notificação com Socket.IO: {e}")
            return None
    
    def send_bulk_notification(self, user_ids: list, notification_type: NotificationType, data: dict, **kwargs):
        """
        Enviar notificação para múltiplos usuários
        
        Args:
            user_ids: Lista de IDs de usuários
            notification_type: Tipo da notificação
            data: Dados da notificação
            **kwargs: Argumentos adicionais
        """
        notification_ids = []
        
        for user_id in user_ids:
            notification_id = self.send_notification(user_id, notification_type, data, **kwargs)
            if notification_id:
                notification_ids.append(notification_id)
        
        logger.info(f"Notificação em lote enviada para {len(notification_ids)}/{len(user_ids)} usuários")
        return notification_ids


# Exportar funções principais
__all__ = [
    'init_notification_socketio',
    'send_realtime_notification',
    'broadcast_system_notification',
    'get_connected_users',
    'is_user_online',
    'RealtimeNotificationService'
]
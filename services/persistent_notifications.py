#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔔 Serviço de Notificações Persistentes para RNC
Gerencia notificações "chatas" que só param quando o usuário responder
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PersistentNotificationService:
    """Serviço para gerenciar notificações persistentes de RNC"""
    
    def __init__(self, db_path: str = 'ippel_system.db'):
        self.db_path = db_path
    
    def get_connection(self):
        """Obtém conexão com o banco"""
        return sqlite3.connect(self.db_path)
    
    def log_rnc_change(self, rnc_id: int, changed_by_user_id: int, 
                      change_type: str, change_description: str = None,
                      old_value: Any = None, new_value: Any = None,
                      field_changed: str = None) -> int:
        """
        Registra uma alteração na RNC
        
        Args:
            rnc_id: ID da RNC
            changed_by_user_id: ID do usuário que fez a alteração
            change_type: Tipo de alteração ('created', 'updated', 'responded', 'value_added', 'finalized')
            change_description: Descrição da alteração
            old_value: Valor anterior
            new_value: Novo valor
            field_changed: Campo específico alterado
            
        Returns:
            ID do registro de alteração criado
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Converter valores para JSON se necessário
            old_value_json = json.dumps(old_value) if old_value is not None else None
            new_value_json = json.dumps(new_value) if new_value is not None else None
            
            cursor.execute("""
                INSERT INTO rnc_changes 
                (rnc_id, changed_by_user_id, change_type, change_description, 
                 old_value, new_value, field_changed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (rnc_id, changed_by_user_id, change_type, change_description,
                  old_value_json, new_value_json, field_changed))
            
            change_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Alteração RNC {rnc_id} registrada: {change_type} por usuário {changed_by_user_id}")
            
            # Criar notificações persistentes para usuários relacionados
            self.create_persistent_notifications_for_change(change_id, rnc_id, changed_by_user_id, change_type, change_description)
            
            return change_id
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar alteração RNC {rnc_id}: {e}")
            raise
    
    def get_rnc_related_users(self, rnc_id: int, exclude_user_id: int = None) -> List[int]:
        """
        Obtém lista de usuários relacionados a uma RNC
        (criador, atribuídos, compartilhados)
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            users = set()
            
            # 1. Criador da RNC
            cursor.execute("SELECT user_id FROM rncs WHERE id = ?", (rnc_id,))
            creator = cursor.fetchone()
            if creator and creator[0]:
                users.add(creator[0])
            
            # 2. Usuário atribuído
            cursor.execute("SELECT assigned_user_id FROM rncs WHERE id = ?", (rnc_id,))
            assigned = cursor.fetchone()
            if assigned and assigned[0]:
                users.add(assigned[0])
            
            # 3. Usuários compartilhados
            cursor.execute("SELECT shared_with_user_id FROM rnc_shares WHERE rnc_id = ?", (rnc_id,))
            shared_users = cursor.fetchall()
            for user in shared_users:
                users.add(user[0])
            
            # Remover o usuário que fez a alteração (não notificar a si mesmo)
            if exclude_user_id:
                users.discard(exclude_user_id)
            
            conn.close()
            
            logger.info(f"📊 RNC {rnc_id} tem {len(users)} usuários relacionados: {list(users)}")
            return list(users)
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter usuários da RNC {rnc_id}: {e}")
            return []
    
    def create_persistent_notifications_for_change(self, change_id: int, rnc_id: int, 
                                                  changed_by_user_id: int, change_type: str,
                                                  change_description: str = None):
        """Cria notificações persistentes para uma alteração"""
        try:
            # Obter usuários relacionados (excluindo quem fez a alteração)
            target_users = self.get_rnc_related_users(rnc_id, exclude_user_id=changed_by_user_id)
            
            if not target_users:
                logger.info(f"ℹ️ Nenhum usuário para notificar sobre RNC {rnc_id}")
                return
            
            # Obter informações da RNC e do usuário
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Dados da RNC
            cursor.execute("SELECT rnc_number, title FROM rncs WHERE id = ?", (rnc_id,))
            rnc_data = cursor.fetchone()
            if not rnc_data:
                logger.error(f"❌ RNC {rnc_id} não encontrada")
                return
            
            rnc_number, rnc_title = rnc_data
            
            # Dados do usuário que fez a alteração
            cursor.execute("SELECT name FROM users WHERE id = ?", (changed_by_user_id,))
            user_data = cursor.fetchone()
            user_name = user_data[0] if user_data else f"Usuário {changed_by_user_id}"
            
            # Gerar título e mensagem baseado no tipo de alteração
            title, message = self.generate_notification_content(
                change_type, rnc_number, rnc_title, user_name, change_description
            )
            
            # Calcular próxima exibição (imediata)
            next_show_at = datetime.now()
            
            # Criar notificação persistente para cada usuário
            for user_id in target_users:
                cursor.execute("""
                    INSERT INTO persistent_notifications 
                    (rnc_id, rnc_change_id, target_user_id, title, message, change_type,
                     is_persistent, response_required, max_attempts, current_attempts,
                     repeat_interval_minutes, next_show_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (rnc_id, change_id, user_id, title, message, change_type,
                      1,  # is_persistent
                      1,  # response_required  
                      10, # max_attempts
                      0,  # current_attempts
                      5,  # repeat_interval_minutes
                      next_show_at))
                
                logger.info(f"🔔 Notificação persistente criada: RNC {rnc_number} → Usuário {user_id}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar notificações persistentes: {e}")
    
    def generate_notification_content(self, change_type: str, rnc_number: str, 
                                    rnc_title: str, user_name: str, 
                                    change_description: str = None) -> tuple[str, str]:
        """Gera título e mensagem da notificação baseado no tipo de alteração"""
        
        change_messages = {
            'created': {
                'title': f'🆕 Nova RNC: {rnc_number}',
                'message': f'{user_name} criou uma nova RNC "{rnc_title}". Você foi atribuído/compartilhado e precisa revisar.'
            },
            'updated': {
                'title': f'📝 RNC Atualizada: {rnc_number}',
                'message': f'{user_name} fez alterações na RNC "{rnc_title}". Verifique as mudanças e responda se necessário.'
            },
            'responded': {
                'title': f'💬 Nova Resposta: {rnc_number}',
                'message': f'{user_name} adicionou uma resposta na RNC "{rnc_title}". Sua atenção é necessária!'
            },
            'value_added': {
                'title': f'💰 Valor Adicionado: {rnc_number}',
                'message': f'{user_name} adicionou valores/custos na RNC "{rnc_title}". Revise os valores inseridos.'
            },
            'finalized': {
                'title': f'✅ RNC Finalizada: {rnc_number}',
                'message': f'{user_name} finalizou a RNC "{rnc_title}". Verifique o resultado final.'
            }
        }
        
        default_content = {
            'title': f'🔔 Alteração: {rnc_number}',
            'message': f'{user_name} fez alterações na RNC "{rnc_title}". Verifique as mudanças.'
        }
        
        content = change_messages.get(change_type, default_content)
        
        # Adicionar descrição se fornecida
        if change_description:
            content['message'] += f'\n\nDetalhes: {change_description}'
        
        return content['title'], content['message']
    
    def get_pending_notifications(self, user_id: int) -> List[Dict]:
        """Obtém notificações persistentes pendentes para um usuário"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Buscar notificações que devem ser mostradas agora
            cursor.execute("""
                SELECT id, rnc_id, title, message, change_type, current_attempts,
                       max_attempts, repeat_interval_minutes, created_at, last_shown_at
                FROM persistent_notifications 
                WHERE target_user_id = ? 
                  AND is_persistent = 1 
                  AND responded_at IS NULL 
                  AND dismissed_at IS NULL
                  AND (next_show_at IS NULL OR next_show_at <= CURRENT_TIMESTAMP)
                  AND current_attempts < max_attempts
                ORDER BY created_at DESC
            """, (user_id,))
            
            notifications = []
            for row in cursor.fetchall():
                notification = {
                    'id': row[0],
                    'rnc_id': row[1], 
                    'title': row[2],
                    'message': row[3],
                    'change_type': row[4],
                    'current_attempts': row[5],
                    'max_attempts': row[6],
                    'repeat_interval_minutes': row[7],
                    'created_at': row[8],
                    'last_shown_at': row[9]
                }
                notifications.append(notification)
            
            conn.close()
            
            logger.info(f"📥 Usuário {user_id} tem {len(notifications)} notificações persistentes pendentes")
            return notifications
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter notificações pendentes: {e}")
            return []
    
    def mark_notification_shown(self, notification_id: int):
        """Marca uma notificação como exibida e agenda próxima exibição"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Atualizar contadores e próxima exibição
            cursor.execute("""
                UPDATE persistent_notifications 
                SET current_attempts = current_attempts + 1,
                    last_shown_at = CURRENT_TIMESTAMP,
                    next_show_at = datetime(CURRENT_TIMESTAMP, '+' || repeat_interval_minutes || ' minutes')
                WHERE id = ?
            """, (notification_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"🔔 Notificação {notification_id} marcada como exibida")
            
        except Exception as e:
            logger.error(f"❌ Erro ao marcar notificação como exibida: {e}")
    
    def respond_to_notification(self, notification_id: int, user_id: int):
        """Marca uma notificação como respondida (para a notificação chata)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Marcar como respondida
            cursor.execute("""
                UPDATE persistent_notifications 
                SET responded_at = CURRENT_TIMESTAMP,
                    is_persistent = 0
                WHERE id = ? AND target_user_id = ?
            """, (notification_id, user_id))
            
            # Verificar se foi atualizada
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"✅ Notificação {notification_id} marcada como respondida pelo usuário {user_id}")
            else:
                logger.warning(f"⚠️ Notificação {notification_id} não encontrada ou não pertence ao usuário {user_id}")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao responder notificação: {e}")
    
    def dismiss_notification(self, notification_id: int, user_id: int):
        """Dispensa uma notificação persistente (usuário escolhe ignorar)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE persistent_notifications 
                SET dismissed_at = CURRENT_TIMESTAMP,
                    is_persistent = 0
                WHERE id = ? AND target_user_id = ?
            """, (notification_id, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"🚫 Notificação {notification_id} dispensada pelo usuário {user_id}")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao dispensar notificação: {e}")
    
    def get_stats(self, user_id: int = None) -> Dict:
        """Obtém estatísticas das notificações persistentes"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            where_clause = "WHERE target_user_id = ?" if user_id else ""
            params = [user_id] if user_id else []
            
            # Notificações ativas
            cursor.execute(f"""
                SELECT COUNT(*) FROM persistent_notifications 
                {where_clause} AND is_persistent = 1 AND responded_at IS NULL AND dismissed_at IS NULL
            """, params)
            stats['active'] = cursor.fetchone()[0]
            
            # Notificações respondidas
            cursor.execute(f"""
                SELECT COUNT(*) FROM persistent_notifications 
                {where_clause} AND responded_at IS NOT NULL
            """, params)
            stats['responded'] = cursor.fetchone()[0]
            
            # Notificações dispensadas
            cursor.execute(f"""
                SELECT COUNT(*) FROM persistent_notifications 
                {where_clause} AND dismissed_at IS NOT NULL
            """, params)
            stats['dismissed'] = cursor.fetchone()[0]
            
            # Notificações expiradas (máximo de tentativas)
            cursor.execute(f"""
                SELECT COUNT(*) FROM persistent_notifications 
                {where_clause} AND current_attempts >= max_attempts AND responded_at IS NULL
            """, params)
            stats['expired'] = cursor.fetchone()[0]
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}


# Instância global do serviço
persistent_notification_service = PersistentNotificationService()
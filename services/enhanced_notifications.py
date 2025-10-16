#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Notificações Melhorado para RNCs
Versão aprimorada com notificações em tempo real, tipos múltiplos e gerenciamento avançado
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Union
import json
from enum import Enum
import uuid

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = 'ippel_system.db'


class NotificationType(Enum):
    """Tipos de notificação disponíveis"""
    RNC_CREATED = "rnc_created"
    RNC_ASSIGNED = "rnc_assigned"
    RNC_UPDATED = "rnc_updated"
    RNC_COMMENTED = "rnc_commented"
    RNC_FINALIZED = "rnc_finalized"
    RNC_SHARED = "rnc_shared"
    SYSTEM_ALERT = "system_alert"
    USER_MENTION = "user_mention"
    DEADLINE_WARNING = "deadline_warning"
    APPROVAL_REQUEST = "approval_request"


class NotificationPriority(Enum):
    """Prioridades de notificação"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationChannel(Enum):
    """Canais de notificação"""
    IN_APP = "in_app"
    EMAIL = "email"
    BROWSER = "browser"
    SMS = "sms"  # Para futuro


class EnhancedNotificationService:
    """Serviço avançado de notificações com múltiplos canais e tipos"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.ensure_tables()
    
    def ensure_tables(self):
        """Garante que as tabelas de notificação existam"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela principal de notificações
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    priority TEXT DEFAULT 'normal',
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    data TEXT,  -- JSON com dados extras
                    
                    -- Relacionamentos
                    from_user_id INTEGER,
                    to_user_id INTEGER NOT NULL,
                    rnc_id INTEGER,
                    
                    -- Canais e estado
                    channels TEXT DEFAULT 'in_app',  -- JSON array
                    is_read BOOLEAN DEFAULT 0,
                    is_dismissed BOOLEAN DEFAULT 0,
                    
                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    read_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    
                    -- Metadados
                    icon TEXT,
                    action_url TEXT,
                    group_id TEXT,  -- Para agrupar notificações relacionadas
                    
                    FOREIGN KEY (from_user_id) REFERENCES users(id),
                    FOREIGN KEY (to_user_id) REFERENCES users(id),
                    FOREIGN KEY (rnc_id) REFERENCES rncs(id)
                )
            """)
            
            # Tabela de preferências de notificação por usuário
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    notification_type TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    is_enabled BOOLEAN DEFAULT 1,
                    quiet_hours_start TIME,
                    quiet_hours_end TIME,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, notification_type, channel)
                )
            """)
            
            # Tabela de templates de notificação
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL UNIQUE,
                    title_template TEXT NOT NULL,
                    message_template TEXT NOT NULL,
                    default_priority TEXT DEFAULT 'normal',
                    default_channels TEXT DEFAULT '["in_app"]',
                    default_icon TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de estatísticas de notificação
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    notification_type TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    sent_count INTEGER DEFAULT 0,
                    read_count INTEGER DEFAULT 0,
                    click_count INTEGER DEFAULT 0,
                    
                    UNIQUE(date, notification_type, channel)
                )
            """)
            
            # Índices para performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(to_user_id, is_read)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_group ON notifications(group_id)")
            
            conn.commit()
            conn.close()
            
            # Inserir templates padrão
            self.create_default_templates()
            
        except Exception as e:
            logger.error(f"Erro ao criar tabelas de notificação: {e}")
    
    def create_default_templates(self):
        """Cria templates padrão de notificação"""
        templates = [
            {
                'type': NotificationType.RNC_CREATED.value,
                'title_template': '📋 Nova RNC Criada',
                'message_template': 'RNC {rnc_number} foi criada por {creator_name}',
                'priority': NotificationPriority.NORMAL.value,
                'icon': '📋'
            },
            {
                'type': NotificationType.RNC_ASSIGNED.value,
                'title_template': '👤 RNC Atribuída a Você',
                'message_template': 'RNC {rnc_number} foi atribuída a você por {assigner_name}',
                'priority': NotificationPriority.HIGH.value,
                'icon': '👤'
            },
            {
                'type': NotificationType.RNC_UPDATED.value,
                'title_template': '📝 RNC Atualizada',
                'message_template': 'RNC {rnc_number} foi atualizada por {updater_name}',
                'priority': NotificationPriority.NORMAL.value,
                'icon': '📝'
            },
            {
                'type': NotificationType.RNC_COMMENTED.value,
                'title_template': '💬 Novo Comentário',
                'message_template': '{commenter_name} comentou na RNC {rnc_number}',
                'priority': NotificationPriority.NORMAL.value,
                'icon': '💬'
            },
            {
                'type': NotificationType.RNC_FINALIZED.value,
                'title_template': '✅ RNC Finalizada',
                'message_template': 'RNC {rnc_number} foi finalizada por {finalizer_name}',
                'priority': NotificationPriority.HIGH.value,
                'icon': '✅'
            },
            {
                'type': NotificationType.RNC_SHARED.value,
                'title_template': '🔗 RNC Compartilhada',
                'message_template': 'RNC {rnc_number} foi compartilhada com você por {sharer_name}',
                'priority': NotificationPriority.NORMAL.value,
                'icon': '🔗'
            },
            {
                'type': NotificationType.SYSTEM_ALERT.value,
                'title_template': '⚠️ Alerta do Sistema',
                'message_template': '{message}',
                'priority': NotificationPriority.HIGH.value,
                'icon': '⚠️'
            },
            {
                'type': NotificationType.USER_MENTION.value,
                'title_template': '🏷️ Você foi Mencionado',
                'message_template': '{mentioner_name} mencionou você na RNC {rnc_number}',
                'priority': NotificationPriority.HIGH.value,
                'icon': '🏷️'
            },
            {
                'type': NotificationType.DEADLINE_WARNING.value,
                'title_template': '⏰ Prazo se Aproximando',
                'message_template': 'RNC {rnc_number} tem prazo em {days_remaining} dias',
                'priority': NotificationPriority.HIGH.value,
                'icon': '⏰'
            },
            {
                'type': NotificationType.APPROVAL_REQUEST.value,
                'title_template': '✋ Aprovação Necessária',
                'message_template': 'RNC {rnc_number} precisa da sua aprovação',
                'priority': NotificationPriority.URGENT.value,
                'icon': '✋'
            }
        ]
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for template in templates:
                cursor.execute("""
                    INSERT OR IGNORE INTO notification_templates 
                    (type, title_template, message_template, default_priority, default_icon)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    template['type'],
                    template['title_template'],
                    template['message_template'],
                    template['priority'],
                    template['icon']
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao criar templates padrão: {e}")
    
    def create_notification(
        self,
        notification_type: Union[NotificationType, str],
        to_user_id: int,
        data: Dict = None,
        from_user_id: Optional[int] = None,
        rnc_id: Optional[int] = None,
        priority: Optional[NotificationPriority] = None,
        channels: List[NotificationChannel] = None,
        expires_in_hours: Optional[int] = None,
        group_id: Optional[str] = None
    ) -> str:
        """
        Cria uma nova notificação
        
        Args:
            notification_type: Tipo da notificação
            to_user_id: ID do usuário destinatário
            data: Dados para interpolação no template
            from_user_id: ID do usuário remetente (opcional)
            rnc_id: ID da RNC relacionada (opcional)
            priority: Prioridade da notificação
            channels: Canais de entrega
            expires_in_hours: Expira em X horas
            group_id: ID do grupo para agrupar notificações
            
        Returns:
            ID da notificação criada
        """
        try:
            # Converter enum para string se necessário
            if isinstance(notification_type, NotificationType):
                notification_type = notification_type.value
            
            # Não gerar ID - deixar o banco gerar automaticamente (INTEGER)
            # O SQLite vai gerar um ID incremental automaticamente
            
            # Buscar template
            template = self.get_template(notification_type)
            if not template:
                logger.error(f"Template não encontrado para tipo: {notification_type}")
                return None
            
            # Preparar dados padrão
            if data is None:
                data = {}
            
            # Interpolar template
            title = self.interpolate_template(template['title_template'], data)
            message = self.interpolate_template(template['message_template'], data)
            
            # Definir prioridade
            if priority is None:
                priority = NotificationPriority(template['default_priority'])
            if isinstance(priority, NotificationPriority):
                priority = priority.value
            
            # Definir canais
            if channels is None:
                channels = [NotificationChannel.IN_APP]
            channels_json = json.dumps([c.value if isinstance(c, NotificationChannel) else c for c in channels])
            
            # Calcular expiração
            expires_at = None
            if expires_in_hours:
                expires_at = datetime.now() + timedelta(hours=expires_in_hours)
            
            # Inserir notificação (sem especificar ID - deixar autoincrement)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO notifications 
                (type, priority, title, message, data, from_user_id, to_user_id, 
                 rnc_id, channels, icon, action_url, group_id, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                notification_type,
                priority,
                title,
                message,
                json.dumps(data) if data else None,
                from_user_id,
                to_user_id,
                rnc_id,
                channels_json,
                template.get('default_icon'),
                data.get('action_url'),
                group_id,
                expires_at
            ))
            
            # Obter ID gerado automaticamente
            notification_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            # Processar canais de entrega
            self.process_notification_channels(notification_id)
            
            # Atualizar estatísticas
            self.update_stats(notification_type, channels, 'sent')
            
            logger.info(f"Notificação criada: {notification_id} para usuário {to_user_id}")
            return notification_id
            
        except Exception as e:
            logger.error(f"Erro ao criar notificação: {e}")
            return None
    
    def get_template(self, notification_type: str) -> Dict:
        """Busca template de notificação"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT title_template, message_template, default_priority, 
                       default_channels, default_icon
                FROM notification_templates 
                WHERE type = ? AND is_active = 1
            """, (notification_type,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'title_template': row[0],
                    'message_template': row[1],
                    'default_priority': row[2],
                    'default_channels': json.loads(row[3]) if row[3] else ['in_app'],
                    'default_icon': row[4]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar template: {e}")
            return None
    
    def interpolate_template(self, template: str, data: Dict) -> str:
        """Interpola dados no template"""
        try:
            return template.format(**data)
        except KeyError as e:
            logger.warning(f"Chave não encontrada no template: {e}")
            return template
        except Exception as e:
            logger.error(f"Erro na interpolação: {e}")
            return template
    
    def process_notification_channels(self, notification_id: str):
        """Processa os canais de entrega da notificação"""
        try:
            # Buscar notificação
            notification = self.get_notification_by_id(notification_id)
            if not notification:
                return
            
            channels = json.loads(notification['channels'])
            
            for channel in channels:
                if channel == NotificationChannel.IN_APP.value:
                    # Já está salva no banco
                    pass
                elif channel == NotificationChannel.EMAIL.value:
                    self.send_email_notification(notification)
                elif channel == NotificationChannel.BROWSER.value:
                    self.send_browser_notification(notification)
                # elif channel == NotificationChannel.SMS.value:
                #     self.send_sms_notification(notification)
            
        except Exception as e:
            logger.error(f"Erro ao processar canais: {e}")
    
    def get_notification_by_id(self, notification_id) -> Dict:
        """Busca notificação por ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT n.*, u.name as to_user_name, u.email as to_user_email,
                       fu.name as from_user_name
                FROM notifications n
                LEFT JOIN users u ON n.to_user_id = u.id
                LEFT JOIN users fu ON n.from_user_id = fu.id
                WHERE n.id = ?
            """, (notification_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar notificação: {e}")
            return None
    
    def send_email_notification(self, notification: Dict):
        """Envia notificação por email"""
        try:
            # Importar serviço de email existente
            from .email_notifications import email_notification_service
            
            # Aqui você integraria com o serviço de email existente
            # Por ora, apenas log
            logger.info(f"Email notification: {notification['title']} para {notification['to_user_email']}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
    
    def send_browser_notification(self, notification: Dict):
        """Envia notificação do navegador via WebSocket/Server-Sent Events"""
        try:
            # Aqui você integraria com Socket.IO ou SSE
            logger.info(f"Browser notification: {notification['title']} para usuário {notification['to_user_id']}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação do navegador: {e}")
    
    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
        notification_type: Optional[str] = None
    ) -> List[Dict]:
        """Busca notificações do usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Construir query
            conditions = ["to_user_id = ?", "expires_at IS NULL OR expires_at > datetime('now')"]
            params = [user_id]
            
            if unread_only:
                conditions.append("is_read = 0")
            
            if notification_type:
                conditions.append("type = ?")
                params.append(notification_type)
            
            where_clause = " AND ".join(conditions)
            
            cursor.execute(f"""
                SELECT n.*, fu.name as from_user_name
                FROM notifications n
                LEFT JOIN users fu ON n.from_user_id = fu.id
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, params + [limit, offset])
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            notifications = []
            for row in rows:
                notification = dict(zip(columns, row))
                if notification['data']:
                    notification['data'] = json.loads(notification['data'])
                notifications.append(notification)
            
            conn.close()
            return notifications
            
        except Exception as e:
            logger.error(f"Erro ao buscar notificações: {e}")
            return []
    
    def mark_as_read(self, notification_ids: List[str], user_id: int) -> bool:
        """Marca notificações como lidas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            placeholders = ','.join(['?' for _ in notification_ids])
            cursor.execute(f"""
                UPDATE notifications 
                SET is_read = 1, read_at = datetime('now')
                WHERE id IN ({placeholders}) AND to_user_id = ?
            """, notification_ids + [user_id])
            
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            # Atualizar estatísticas
            for _ in range(affected_rows):
                self.update_stats('unknown', ['in_app'], 'read')
            
            return affected_rows > 0
            
        except Exception as e:
            logger.error(f"Erro ao marcar como lida: {e}")
            return False
    
    def mark_as_dismissed(self, notification_ids: List[str], user_id: int) -> bool:
        """Marca notificações como dispensadas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            placeholders = ','.join(['?' for _ in notification_ids])
            cursor.execute(f"""
                UPDATE notifications 
                SET is_dismissed = 1
                WHERE id IN ({placeholders}) AND to_user_id = ?
            """, notification_ids + [user_id])
            
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            return affected_rows > 0
            
        except Exception as e:
            logger.error(f"Erro ao dispensar notificação: {e}")
            return False
    
    def get_unread_count(self, user_id: int) -> int:
        """Conta notificações não lidas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM notifications 
                WHERE to_user_id = ? AND is_read = 0 AND is_dismissed = 0
                  AND (expires_at IS NULL OR expires_at > datetime('now'))
            """, (user_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            logger.error(f"Erro ao contar não lidas: {e}")
            return 0
    
    def update_stats(self, notification_type: str, channels: List[str], action: str):
        """Atualiza estatísticas de notificação"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().date()
            
            for channel in channels:
                cursor.execute(f"""
                    INSERT OR IGNORE INTO notification_stats 
                    (date, notification_type, channel) 
                    VALUES (?, ?, ?)
                """, (today, notification_type, channel))
                
                if action == 'sent':
                    cursor.execute("""
                        UPDATE notification_stats 
                        SET sent_count = sent_count + 1
                        WHERE date = ? AND notification_type = ? AND channel = ?
                    """, (today, notification_type, channel))
                elif action == 'read':
                    cursor.execute("""
                        UPDATE notification_stats 
                        SET read_count = read_count + 1
                        WHERE date = ? AND notification_type = ? AND channel = ?
                    """, (today, notification_type, channel))
                elif action == 'click':
                    cursor.execute("""
                        UPDATE notification_stats 
                        SET click_count = click_count + 1
                        WHERE date = ? AND notification_type = ? AND channel = ?
                    """, (today, notification_type, channel))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar estatísticas: {e}")
    
    def cleanup_old_notifications(self, days_old: int = 30) -> int:
        """Remove notificações antigas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            cursor.execute("""
                DELETE FROM notifications 
                WHERE created_at < ? OR expires_at < datetime('now')
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Limpeza: {deleted_count} notificações antigas removidas")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")
            return 0


# Instância global do serviço
enhanced_notification_service = EnhancedNotificationService()


# Funções de conveniência para compatibilidade
def create_notification(notification_type: str, to_user_id: int, data: Dict = None, **kwargs) -> str:
    """Função de conveniência para criar notificação"""
    return enhanced_notification_service.create_notification(
        notification_type, to_user_id, data, **kwargs
    )


def get_user_notifications(user_id: int, unread_only: bool = False, **kwargs) -> List[Dict]:
    """Função de conveniência para buscar notificações"""
    return enhanced_notification_service.get_user_notifications(
        user_id, unread_only, **kwargs
    )


def mark_notifications_read(notification_ids: List[str], user_id: int) -> bool:
    """Função de conveniência para marcar como lidas"""
    return enhanced_notification_service.mark_as_read(notification_ids, user_id)


def get_unread_notifications_count(user_id: int) -> int:
    """Função de conveniência para contar não lidas"""
    return enhanced_notification_service.get_unread_count(user_id)


if __name__ == "__main__":
    # Teste básico
    service = EnhancedNotificationService()
    print("✅ Serviço de notificações melhorado carregado")
    print(f"📊 Tabelas criadas e templates instalados")
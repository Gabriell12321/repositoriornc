#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Notificações por Email para RNCs
Módulo responsável por enviar notificações automáticas para grupos e usuários
quando uma nova RNC é criada
"""

import smtplib
import sqlite3
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional, Tuple
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações de email - serão carregadas do banco ou config
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': 'seu-email@gmail.com',  # Será carregado do banco
    'password': 'sua-senha-de-app',  # Será carregado do banco
    'from_name': 'Sistema IPPEL RNC'
}

DB_PATH = 'ippel_system.db'


class EmailNotificationService:
    """Serviço para envio de notificações por email"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.load_email_config()
    
    def load_email_config(self):
        """Carrega configurações de email do banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se existe tabela de configurações
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='email_config'
            """)
            
            if cursor.fetchone():
                cursor.execute("""
                    SELECT smtp_server, smtp_port, email, password, from_name 
                    FROM email_config 
                    WHERE active = 1 
                    LIMIT 1
                """)
                config = cursor.fetchone()
                
                if config:
                    EMAIL_CONFIG['smtp_server'] = config[0]
                    EMAIL_CONFIG['smtp_port'] = config[1]
                    EMAIL_CONFIG['email'] = config[2]
                    EMAIL_CONFIG['password'] = config[3]
                    EMAIL_CONFIG['from_name'] = config[4]
                    logger.info("Configurações de email carregadas do banco")
                else:
                    logger.warning("Nenhuma configuração de email ativa encontrada")
            else:
                logger.warning("Tabela email_config não encontrada, usando configurações padrão")
                
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao carregar configurações de email: {e}")
    
    def get_users_to_notify(self, rnc_data: Dict) -> List[Dict]:
        """
        Obtém lista de usuários que devem ser notificados sobre a nova RNC
        Inclui usuários de grupos específicos e usuários individuais
        """
        users_to_notify = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. Buscar usuários de grupos que devem ser notificados
            # Verificar se existem configurações de notificação por grupo
            cursor.execute("""
                SELECT g.id, g.name, g.description
                FROM groups g
                WHERE g.notify_on_rnc = 1
            """)
            notification_groups = cursor.fetchall()
            
            for group_id, group_name, group_desc in notification_groups:
                # Buscar usuários do grupo (usando group_id na tabela users)
                cursor.execute("""
                    SELECT u.id, u.name, u.email, u.department
                    FROM users u
                    WHERE u.group_id = ? AND u.email IS NOT NULL AND u.email != ''
                """, (group_id,))
                
                group_users = cursor.fetchall()
                for user_id, name, email, department in group_users:
                    users_to_notify.append({
                        'user_id': user_id,
                        'name': name,
                        'email': email,
                        'department': department,
                        'notification_type': 'group',
                        'group_name': group_name
                    })
            
            # 2. Buscar usuários com notificação individual habilitada
            cursor.execute("""
                SELECT id, name, email, department
                FROM users
                WHERE notify_on_rnc = 1 AND email IS NOT NULL AND email != ''
            """)
            
            individual_users = cursor.fetchall()
            for user_id, name, email, department in individual_users:
                # Evitar duplicatas (usuário já incluído por grupo)
                if not any(u['user_id'] == user_id for u in users_to_notify):
                    users_to_notify.append({
                        'user_id': user_id,
                        'name': name,
                        'email': email,
                        'department': department,
                        'notification_type': 'individual',
                        'group_name': None
                    })
            
            # 3. Sempre notificar administradores
            cursor.execute("""
                SELECT id, name, email, department
                FROM users
                WHERE role = 'admin' AND email IS NOT NULL AND email != ''
            """)
            
            admin_users = cursor.fetchall()
            for user_id, name, email, department in admin_users:
                if not any(u['user_id'] == user_id for u in users_to_notify):
                    users_to_notify.append({
                        'user_id': user_id,
                        'name': name,
                        'email': email,
                        'department': department,
                        'notification_type': 'admin',
                        'group_name': None
                    })
            
            conn.close()
            
            logger.info(f"Encontrados {len(users_to_notify)} usuários para notificar")
            return users_to_notify
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuários para notificação: {e}")
            return []
    
    def create_email_content(self, rnc_data: Dict, user_data: Dict) -> Tuple[str, str, str]:
        """
        Cria o conteúdo do email (assunto, texto, HTML)
        """
        rnc_number = rnc_data.get('rnc_number', 'RNC-XXXX')
        rnc_title = rnc_data.get('title', 'Sem título')
        creator_name = rnc_data.get('creator_name', 'Sistema')
        department = rnc_data.get('department', 'N/A')
        
        # Assunto do email
        subject = f"Nova RNC Criada: {rnc_number} - {rnc_title}"
        
        # Conteúdo texto simples
        text_content = f"""
Nova RNC Criada no Sistema IPPEL

RNC: {rnc_number}
Título: {rnc_title}
Criado por: {creator_name}
Departamento: {department}
Data de Criação: {datetime.now().strftime('%d/%m/%Y às %H:%M')}

Descrição: {rnc_data.get('description', 'Não informado')}

Para visualizar a RNC completa, acesse o sistema IPPEL.

---
Este é um email automático do Sistema IPPEL RNC.
Não responda a este email.
        """.strip()
        
        # Conteúdo HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            max-width: 600px; 
            margin: 0 auto; 
            color: #333;
        }}
        .header {{ 
            background: linear-gradient(135deg, #dc2626, #b91c1c); 
            color: white; 
            padding: 20px; 
            border-radius: 10px 10px 0 0; 
            text-align: center; 
        }}
        .content {{ 
            background: #f9fafb; 
            padding: 20px; 
            border-radius: 0 0 10px 10px; 
        }}
        .info-box {{ 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 20px; 
            border-left: 4px solid #dc2626;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }}
        .label {{
            font-weight: bold;
            color: #374151;
        }}
        .value {{
            color: #6b7280;
        }}
        .footer {{ 
            text-align: center; 
            margin-top: 20px; 
            color: #6b7280; 
            font-size: 12px; 
        }}
        .notification-badge {{
            background: #dc2626;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 style="margin: 0;">🔔 Nova RNC Criada</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">Sistema IPPEL - Relatórios de Não Conformidade</p>
    </div>
    
    <div class="content">
        <div class="info-box">
            <h2 style="color: #dc2626; margin-top: 0; margin-bottom: 15px;">
                {rnc_number} - {rnc_title}
            </h2>
            
            <div class="detail-row">
                <span class="label">Criado por:</span>
                <span class="value">{creator_name}</span>
            </div>
            
            <div class="detail-row">
                <span class="label">Departamento:</span>
                <span class="value">{department}</span>
            </div>
            
            <div class="detail-row">
                <span class="label">Data de Criação:</span>
                <span class="value">{datetime.now().strftime('%d/%m/%Y às %H:%M')}</span>
            </div>
            
            <div class="detail-row">
                <span class="label">Equipamento:</span>
                <span class="value">{rnc_data.get('equipment', 'Não informado')}</span>
            </div>
            
            <div class="detail-row">
                <span class="label">Cliente:</span>
                <span class="value">{rnc_data.get('client', 'Não informado')}</span>
            </div>
        </div>
        
        <div class="info-box">
            <h3 style="color: #374151; margin-top: 0;">Descrição:</h3>
            <p style="color: #6b7280; line-height: 1.5; margin-bottom: 0;">
                {rnc_data.get('description', 'Não informado')}
            </p>
        </div>
        
        <div style="text-align: center; margin: 20px 0;">
            <span class="notification-badge">
                Notificação enviada para: {user_data['name']} ({user_data['notification_type']})
            </span>
        </div>
        
        <div class="footer">
            <p>Este é um email automático do Sistema IPPEL RNC.</p>
            <p>Para visualizar a RNC completa, acesse o sistema IPPEL.</p>
            <p style="color: #dc2626;">⚠️ Não responda a este email.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return subject, text_content, html_content
    
    def send_email(self, recipient_email: str, subject: str, text_content: str, html_content: str) -> bool:
        """
        Envia um email para o destinatário especificado
        """
        try:
            # Verificar se as configurações de email estão válidas
            if EMAIL_CONFIG['email'] == 'seu-email@gmail.com':
                logger.warning("Configurações de email não foram definidas")
                return False
            
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['email']}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg['Reply-To'] = EMAIL_CONFIG['email']
            
            # Anexar conteúdo
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Conectar e enviar (suporte SSL/TLS)
            smtp_port = EMAIL_CONFIG['smtp_port']
            smtp_server = EMAIL_CONFIG['smtp_server']
            
            if smtp_port == 465:
                # Porta 465 usa SSL direto
                with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                    server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
                    server.send_message(msg)
            else:
                # Porta 587 usa STARTTLS
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
                    server.send_message(msg)
            
            logger.info(f"Email enviado com sucesso para {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email para {recipient_email}: {e}")
            return False
    
    def log_notification(self, rnc_id: int, user_id: int, email: str, status: str, error_msg: str = None):
        """
        Registra o log da tentativa de notificação
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Criar tabela de logs se não existir
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rnc_id INTEGER,
                    user_id INTEGER,
                    email TEXT,
                    status TEXT,
                    error_message TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (rnc_id) REFERENCES rncs(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            cursor.execute("""
                INSERT INTO notification_logs (rnc_id, user_id, email, status, error_message)
                VALUES (?, ?, ?, ?, ?)
            """, (rnc_id, user_id, email, status, error_msg))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao registrar log de notificação: {e}")
    
    def notify_rnc_creation(self, rnc_id: int) -> Dict:
        """
        Função principal para notificar sobre criação de RNC
        Retorna estatísticas do envio
        """
        try:
            # Buscar dados da RNC
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    r.id, r.rnc_number, r.title, r.description, 
                    r.equipment, r.client, r.department,
                    u.name as creator_name, u.email as creator_email
                FROM rncs r
                LEFT JOIN users u ON r.inspector_id = u.id
                WHERE r.id = ?
            """, (rnc_id,))
            
            rnc_row = cursor.fetchone()
            conn.close()
            
            if not rnc_row:
                logger.error(f"RNC {rnc_id} não encontrada")
                return {'success': False, 'message': 'RNC não encontrada'}
            
            # Converter para dicionário
            rnc_data = {
                'id': rnc_row[0],
                'rnc_number': rnc_row[1],
                'title': rnc_row[2],
                'description': rnc_row[3],
                'equipment': rnc_row[4],
                'client': rnc_row[5],
                'department': rnc_row[6],
                'creator_name': rnc_row[7],
                'creator_email': rnc_row[8]
            }
            
            # Obter usuários para notificar
            users_to_notify = self.get_users_to_notify(rnc_data)
            
            if not users_to_notify:
                logger.warning("Nenhum usuário configurado para receber notificações")
                return {'success': True, 'message': 'Nenhum usuário para notificar', 'sent': 0, 'failed': 0}
            
            # Enviar notificações
            sent_count = 0
            failed_count = 0
            
            for user in users_to_notify:
                try:
                    # Criar conteúdo do email
                    subject, text_content, html_content = self.create_email_content(rnc_data, user)
                    
                    # Enviar email
                    success = self.send_email(user['email'], subject, text_content, html_content)
                    
                    if success:
                        sent_count += 1
                        self.log_notification(rnc_id, user['user_id'], user['email'], 'sent')
                    else:
                        failed_count += 1
                        self.log_notification(rnc_id, user['user_id'], user['email'], 'failed', 'Erro no envio')
                        
                except Exception as e:
                    failed_count += 1
                    error_msg = str(e)
                    logger.error(f"Erro ao notificar usuário {user['email']}: {error_msg}")
                    self.log_notification(rnc_id, user['user_id'], user['email'], 'failed', error_msg)
            
            logger.info(f"Notificações enviadas para RNC {rnc_id}: {sent_count} sucessos, {failed_count} falhas")
            
            return {
                'success': True,
                'message': f'Notificações processadas: {sent_count} enviadas, {failed_count} falharam',
                'sent': sent_count,
                'failed': failed_count,
                'total_users': len(users_to_notify)
            }
            
        except Exception as e:
            logger.error(f"Erro geral ao notificar criação de RNC {rnc_id}: {e}")
            return {'success': False, 'message': f'Erro: {str(e)}'}


# Instância global do serviço
email_notification_service = EmailNotificationService()


def notify_new_rnc(rnc_id: int) -> Dict:
    """
    Função de conveniência para notificar sobre nova RNC
    Pode ser chamada de qualquer lugar do sistema
    """
    return email_notification_service.notify_rnc_creation(rnc_id)


if __name__ == "__main__":
    # Teste básico
    service = EmailNotificationService()
    print("Serviço de notificações por email carregado")
    print(f"Configuração atual: {EMAIL_CONFIG['email']}")   
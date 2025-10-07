#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE EMAIL BIDIRECIONAL - IPPEL
Sistema de relatórios de não conformidades com comunicação por email
"""

import sqlite3
import smtplib
import imaplib
import email
import json
import base64
import os
import logging
import threading
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import decode_header
import uuid
import re
from typing import Dict, List, Optional, Tuple

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmailSystem:
    """Sistema de email bidirecional para IPPEL"""
    
    def __init__(self, db_path: str = 'ippel_system.db'):
        self.db_path = db_path
        self.smtp_config = {}
        self.imap_config = {}
        self.load_config()
        
    def load_config(self):
        """Carrega configurações do banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Carregar configurações SMTP
            cursor.execute("SELECT config_key, config_value FROM system_config WHERE config_key LIKE 'smtp_%'")
            for key, value in cursor.fetchall():
                self.smtp_config[key] = value
                
            # Carregar configurações IMAP
            cursor.execute("SELECT config_key, config_value FROM system_config WHERE config_key LIKE 'imap_%'")
            for key, value in cursor.fetchall():
                self.imap_config[key] = value
                
            conn.close()
            logger.info("Configurações carregadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            
    def log_system_event(self, level: str, category: str, message: str, details: Dict = None):
        """Registra evento no sistema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            details_json = json.dumps(details) if details else None
            
            cursor.execute("""
                INSERT INTO system_logs (level, category, message, details)
                VALUES (?, ?, ?, ?)
            """, (level, category, message, details_json))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao registrar log: {e}")
            
    def create_email_thread(self, rnc_id: int, subject: str) -> str:
        """Cria um novo thread de email para um RNC"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            thread_id = f"ippel-rnc-{rnc_id}-{uuid.uuid4().hex[:8]}"
            
            cursor.execute("""
                INSERT INTO email_threads (rnc_id, thread_id, subject)
                VALUES (?, ?, ?)
            """, (rnc_id, thread_id, subject))
            
            conn.commit()
            conn.close()
            
            self.log_system_event('info', 'email', f'Thread criado: {thread_id}', {'rnc_id': rnc_id})
            return thread_id
            
        except Exception as e:
            logger.error(f"Erro ao criar thread: {e}")
            return None
            
    def send_rnc_notification(self, rnc_id: int, recipient_email: str, 
                            subject: str = None, body: str = None) -> bool:
        """Envia notificação de RNC por email com link único"""
        try:
            # Buscar dados do RNC
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT rnc_number, title, description, equipment, client, 
                       u.name as inspector_name
                FROM rnc_reports r
                JOIN users u ON r.inspector_id = u.id
                WHERE r.id = ?
            """, (rnc_id,))
            
            rnc_data = cursor.fetchone()
            if not rnc_data:
                logger.error(f"RNC {rnc_id} não encontrado")
                return False
                
            rnc_number, title, description, equipment, client, inspector_name = rnc_data
            
            # Criar link único para o RNC
            from link_system import RNCLinkSystem
            link_system = RNCLinkSystem(self.db_path)
            
            link_data = link_system.create_rnc_link(
                rnc_id=rnc_id,
                created_by=1,  # ID do usuário atual
                recipient_email=recipient_email,
                expires_in_days=30,
                max_accesses=5
            )
            
            # Criar thread se não existir
            cursor.execute("SELECT thread_id FROM email_threads WHERE rnc_id = ?", (rnc_id,))
            thread_result = cursor.fetchone()
            
            if thread_result:
                thread_id = thread_result[0]
            else:
                thread_id = self.create_email_thread(rnc_id, f"RNC {rnc_number} - {title}")
                
            # Preparar email
            if not subject:
                subject = f"RNC {rnc_number} - {title}"
                
            if not body:
                body = self.generate_rnc_email_body_with_link(rnc_data, link_data)
                
            # Enviar email
            success = self.send_email(
                to_email=recipient_email,
                subject=subject,
                body=body,
                thread_id=thread_id,
                rnc_id=rnc_id
            )
            
            conn.close()
            return success
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação RNC: {e}")
            self.log_system_event('error', 'email', f'Erro ao enviar RNC {rnc_id}', {'error': str(e)})
            return False
            
    def generate_rnc_email_body(self, rnc_data: Tuple) -> str:
        """Gera corpo do email com dados do RNC"""
        rnc_number, title, description, equipment, client, inspector_name = rnc_data
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #dc3545 0%, #b21f35 100%); 
                            color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                    <h1 style="margin: 0; font-size: 24px;">Relatório de Não Conformidade</h1>
                    <p style="margin: 5px 0; font-size: 18px;">RNC Nº: {rnc_number}</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="color: #dc3545; margin-top: 0;">Detalhes do RNC</h2>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; font-weight: bold; width: 30%;">Título:</td>
                            <td style="padding: 8px;">{title}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Equipamento:</td>
                            <td style="padding: 8px;">{equipment or 'N/A'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Cliente:</td>
                            <td style="padding: 8px;">{client or 'N/A'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Inspetor:</td>
                            <td style="padding: 8px;">{inspector_name}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background: #fff; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px;">
                    <h3 style="color: #495057; margin-top: 0;">Descrição da Não Conformidade</h3>
                    <p style="text-align: justify;">{description}</p>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 8px;">
                    <p style="margin: 0; font-size: 14px; color: #6c757d;">
                        <strong>Importante:</strong> Para responder a este email, mantenha o assunto original.
                        Sua resposta será automaticamente associada a este RNC.
                    </p>
                </div>
                
                <div style="margin-top: 20px; text-align: center; color: #6c757d; font-size: 12px;">
                    <p>Sistema IPPEL - Relatórios de Não Conformidades</p>
                    <p>Este é um email automático. Não responda diretamente a este endereço.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return body
        
    def generate_rnc_email_body_with_link(self, rnc_data: Tuple, link_data: Dict) -> str:
        """Gera corpo do email com link único para o RNC"""
        rnc_number, title, description, equipment, client, inspector_name = rnc_data
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #dc3545 0%, #b21f35 100%); 
                            color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                    <h1 style="margin: 0; font-size: 24px;">Relatório de Não Conformidade</h1>
                    <p style="margin: 5px 0; font-size: 18px;">RNC Nº: {rnc_number}</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="color: #dc3545; margin-top: 0;">Detalhes do RNC</h2>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; font-weight: bold; width: 30%;">Título:</td>
                            <td style="padding: 8px;">{title}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Equipamento:</td>
                            <td style="padding: 8px;">{equipment or 'N/A'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Cliente:</td>
                            <td style="padding: 8px;">{client or 'N/A'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Inspetor:</td>
                            <td style="padding: 8px;">{inspector_name}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background: #fff; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #495057; margin-top: 0;">Descrição da Não Conformidade</h3>
                    <p style="text-align: justify;">{description}</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                            border: 2px solid #2196f3; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
                    <h3 style="color: #1565c0; margin-top: 0; text-align: center;">🔗 Acesse o RNC Completo</h3>
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="{link_data['link_url']}" 
                           style="background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%); 
                                  color: white; padding: 15px 30px; text-decoration: none; 
                                  border-radius: 25px; font-weight: bold; font-size: 16px;
                                  display: inline-block; box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);">
                            📋 Ver RNC Completo
                        </a>
                    </div>
                    <div style="text-align: center; color: #1565c0; font-size: 14px;">
                        <strong>Código de Acesso:</strong> {link_data['access_code']}
                    </div>
                    <div style="text-align: center; color: #1565c0; font-size: 12px; margin-top: 10px;">
                        ⏰ Link válido até: {link_data['expires_at'][:10]}
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 8px;">
                    <p style="margin: 0; font-size: 14px; color: #6c757d;">
                        <strong>🔒 Segurança:</strong> Este link é único e seguro. Não compartilhe com terceiros.
                    </p>
                </div>
                
                <div style="margin-top: 20px; text-align: center; color: #6c757d; font-size: 12px;">
                    <p>Sistema IPPEL - Relatórios de Não Conformidades</p>
                    <p>Este é um email automático. Não responda diretamente a este endereço.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return body
        
    def send_email(self, to_email: str, subject: str, body: str, 
                  thread_id: str = None, rnc_id: int = None, 
                  attachments: List[str] = None) -> bool:
        """Envia email usando SMTP"""
        try:
            # Configurar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.smtp_config.get('email_from_name', 'Sistema IPPEL')} <{self.smtp_config.get('smtp_username')}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Adicionar headers para threading
            if thread_id:
                msg['X-Thread-ID'] = thread_id
                msg['References'] = thread_id
                msg['In-Reply-To'] = thread_id
                
            # Corpo do email
            text_part = MIMEText(body.replace('<br>', '\n').replace('<p>', '').replace('</p>', '\n'), 'plain', 'utf-8')
            html_part = MIMEText(body, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Adicionar anexos
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
            
            # Enviar via SMTP
            with smtplib.SMTP(self.smtp_config.get('smtp_host'), int(self.smtp_config.get('smtp_port', 587))) as server:
                server.starttls()
                server.login(self.smtp_config.get('smtp_username'), self.smtp_config.get('smtp_password'))
                server.send_message(msg)
            
            # Registrar no banco
            self.save_email_message(
                thread_id=thread_id,
                from_email=self.smtp_config.get('smtp_username'),
                to_email=to_email,
                subject=subject,
                body=body,
                direction='outbound',
                rnc_id=rnc_id
            )
            
            self.log_system_event('info', 'email', f'Email enviado para {to_email}', {
                'subject': subject, 'thread_id': thread_id, 'rnc_id': rnc_id
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            self.log_system_event('error', 'email', f'Erro ao enviar email para {to_email}', {'error': str(e)})
            return False
            
    def save_email_message(self, thread_id: str, from_email: str, to_email: str,
                          subject: str, body: str, direction: str, 
                          rnc_id: int = None, attachments: str = None):
        """Salva mensagem no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            message_id = f"msg-{uuid.uuid4().hex}"
            
            cursor.execute("""
                INSERT INTO email_messages 
                (thread_id, message_id, from_email, to_email, subject, body, 
                 html_body, attachments, direction, status, sent_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'sent', CURRENT_TIMESTAMP)
            """, (thread_id, message_id, from_email, to_email, subject, body, 
                  body, attachments, direction))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {e}")
            
    def check_incoming_emails(self):
        """Verifica emails recebidos via IMAP"""
        try:
            # Conectar ao servidor IMAP
            mail = imaplib.IMAP4_SSL(self.imap_config.get('imap_host', 'imap.gmail.com'))
            mail.login(self.imap_config.get('imap_username'), self.imap_config.get('imap_password'))
            mail.select('INBOX')
            
            # Buscar emails não lidos
            status, messages = mail.search(None, 'UNSEEN')
            
            if status == 'OK':
                for num in messages[0].split():
                    status, msg_data = mail.fetch(num, '(RFC822)')
                    
                    if status == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        # Processar email
                        self.process_incoming_email(email_message)
                        
            mail.close()
            mail.logout()
            
        except Exception as e:
            logger.error(f"Erro ao verificar emails: {e}")
            self.log_system_event('error', 'email', 'Erro ao verificar emails recebidos', {'error': str(e)})
            
    def process_incoming_email(self, email_message):
        """Processa email recebido"""
        try:
            # Extrair informações do email
            from_email = email_message['from']
            subject = email_message['subject']
            thread_id = email_message.get('X-Thread-ID') or email_message.get('References')
            
            # Extrair corpo do email
            body = self.extract_email_body(email_message)
            
            # Buscar RNC relacionado
            rnc_id = self.find_rnc_from_thread(thread_id)
            
            if rnc_id:
                # Salvar mensagem recebida
                self.save_email_message(
                    thread_id=thread_id,
                    from_email=from_email,
                    to_email=self.smtp_config.get('smtp_username'),
                    subject=subject,
                    body=body,
                    direction='inbound',
                    rnc_id=rnc_id
                )
                
                # Criar notificação
                self.create_notification(
                    user_id=self.get_user_by_email(from_email),
                    rnc_id=rnc_id,
                    type='email_received',
                    title=f'Resposta recebida - RNC {rnc_id}',
                    message=f'Email recebido de {from_email}: {subject}'
                )
                
                # Auto-reply se configurado
                if self.smtp_config.get('auto_reply_enabled', 'false').lower() == 'true':
                    self.send_auto_reply(from_email, subject, thread_id, rnc_id)
                    
            self.log_system_event('info', 'email', f'Email processado de {from_email}', {
                'subject': subject, 'thread_id': thread_id, 'rnc_id': rnc_id
            })
            
        except Exception as e:
            logger.error(f"Erro ao processar email: {e}")
            
    def extract_email_body(self, email_message) -> str:
        """Extrai corpo do email"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
                elif part.get_content_type() == "text/html":
                    body = part.get_payload(decode=True).decode()
        else:
            body = email_message.get_payload(decode=True).decode()
            
        return body
        
    def find_rnc_from_thread(self, thread_id: str) -> Optional[int]:
        """Encontra RNC relacionado ao thread"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT rnc_id FROM email_threads WHERE thread_id = ?
            """, (thread_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Erro ao buscar RNC do thread: {e}")
            return None
            
    def get_user_by_email(self, email: str) -> Optional[int]:
        """Busca usuário por email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário: {e}")
            return None
            
    def create_notification(self, user_id: int, rnc_id: int, type: str, title: str, message: str):
        """Cria notificação no sistema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO notifications (user_id, rnc_id, type, title, message)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, rnc_id, type, title, message))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao criar notificação: {e}")
            
    def send_auto_reply(self, to_email: str, original_subject: str, thread_id: str, rnc_id: int):
        """Envia resposta automática"""
        try:
            subject = f"Re: {original_subject}"
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <p>Olá,</p>
                <p>Recebemos sua resposta para o RNC #{rnc_id}.</p>
                <p>Nossa equipe irá analisar sua mensagem e entrar em contato em breve.</p>
                <p>Atenciosamente,<br>Sistema IPPEL</p>
            </body>
            </html>
            """
            
            self.send_email(to_email, subject, body, thread_id, rnc_id)
            
        except Exception as e:
            logger.error(f"Erro ao enviar auto-reply: {e}")
            
    def start_email_monitor(self):
        """Inicia monitoramento de emails em background"""
        def monitor_loop():
            while True:
                try:
                    self.check_incoming_emails()
                    time.sleep(300)  # Verificar a cada 5 minutos
                except Exception as e:
                    logger.error(f"Erro no monitor de email: {e}")
                    time.sleep(60)  # Esperar 1 minuto em caso de erro
                    
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("Monitor de email iniciado")

# Exemplo de uso
if __name__ == "__main__":
    email_system = EmailSystem()
    
    # Exemplo: Enviar notificação de RNC
    # email_system.send_rnc_notification(
    #     rnc_id=1,
    #     recipient_email="gerente@empresa.com",
    #     subject="Novo RNC identificado",
    #     body="Detalhes do RNC..."
    # )
    
    # Iniciar monitor de email
    email_system.start_email_monitor()
    
    # Manter programa rodando
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Sistema encerrado pelo usuário") 
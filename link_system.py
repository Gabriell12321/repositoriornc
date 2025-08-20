#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE LINKS ÚNICOS PARA RNCs - IPPEL
Sistema seguro para compartilhamento de relatórios de não conformidades
"""

import sqlite3
import hashlib
import secrets
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class RNCLinkSystem:
    """Sistema de links únicos para RNCs"""
    
    def __init__(self, db_path: str = 'ippel_system.db'):
        self.db_path = db_path
        self.init_link_tables()
        
    def init_link_tables(self):
        """Inicializa tabelas para sistema de links"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de links únicos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rnc_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rnc_id INTEGER NOT NULL,
                    link_token TEXT UNIQUE NOT NULL,
                    access_code TEXT NOT NULL,
                    created_by INTEGER NOT NULL,
                    recipient_email TEXT,
                    expires_at TIMESTAMP,
                    max_accesses INTEGER DEFAULT 1,
                    current_accesses INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (rnc_id) REFERENCES rnc_reports(id),
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """)
            
            # Tabela de acessos aos links
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS link_accesses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link_id INTEGER NOT NULL,
                    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    access_successful BOOLEAN DEFAULT 1,
                    FOREIGN KEY (link_id) REFERENCES rnc_links(id)
                )
            """)
            
            # Índices para performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rnc_links_token ON rnc_links(link_token)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rnc_links_rnc_id ON rnc_links(rnc_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rnc_links_expires ON rnc_links(expires_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_link_accesses_link_id ON link_accesses(link_id)")
            
            conn.commit()
            conn.close()
            logger.info("Tabelas de links inicializadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar tabelas de links: {e}")
            
    def generate_link_token(self) -> str:
        """Gera token único para link"""
        return secrets.token_urlsafe(32)
        
    def generate_access_code(self) -> str:
        """Gera código de acesso (6 dígitos)"""
        return secrets.token_hex(3).upper()
        
    def create_rnc_link(self, rnc_id: int, created_by: int, 
                       recipient_email: str = None, 
                       expires_in_days: int = 30,
                       max_accesses: int = 1) -> Dict:
        """Cria um novo link único para RNC"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se RNC existe
            cursor.execute("SELECT rnc_number, title FROM rnc_reports WHERE id = ?", (rnc_id,))
            rnc_data = cursor.fetchone()
            
            if not rnc_data:
                raise ValueError(f"RNC {rnc_id} não encontrado")
                
            rnc_number, rnc_title = rnc_data
            
            # Gerar token e código únicos
            link_token = self.generate_link_token()
            access_code = self.generate_access_code()
            
            # Calcular data de expiração
            expires_at = datetime.now() + timedelta(days=expires_in_days)
            
            # Inserir link no banco
            cursor.execute("""
                INSERT INTO rnc_links 
                (rnc_id, link_token, access_code, created_by, recipient_email, 
                 expires_at, max_accesses)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (rnc_id, link_token, access_code, created_by, recipient_email,
                  expires_at, max_accesses))
            
            link_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Gerar URL do link
            link_url = self.generate_link_url(link_token)
            
            link_data = {
                'id': link_id,
                'rnc_id': rnc_id,
                'rnc_number': rnc_number,
                'rnc_title': rnc_title,
                'link_token': link_token,
                'access_code': access_code,
                'link_url': link_url,
                'expires_at': expires_at.isoformat(),
                'max_accesses': max_accesses,
                'recipient_email': recipient_email
            }
            
            self.log_system_event('info', 'link', f'Link criado para RNC {rnc_number}', {
                'link_id': link_id,
                'rnc_id': rnc_id,
                'recipient_email': recipient_email
            })
            
            return link_data
            
        except Exception as e:
            logger.error(f"Erro ao criar link RNC: {e}")
            raise
            
    def generate_link_url(self, link_token: str) -> str:
        """Gera URL completa do link"""
        # Usar IP local para acesso direto
        import socket
        try:
            # Obter IP local
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            base_url = f"http://{local_ip}:5000"
        except:
            # Fallback para localhost
            base_url = "http://localhost:5000"
        
        return f"{base_url}/rnc/view/{link_token}"
        
    def validate_link(self, link_token: str, access_code: str = None) -> Optional[Dict]:
        """Valida um link e retorna dados do RNC se válido"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar link
            cursor.execute("""
                SELECT l.*, r.rnc_number, r.title, r.description, r.equipment,
                       r.client, r.created_at as rnc_created_at,
                       u.name as created_by_name
                FROM rnc_links l
                JOIN rnc_reports r ON l.rnc_id = r.id
                JOIN users u ON l.created_by = u.id
                WHERE l.link_token = ? AND l.is_active = 1
            """, (link_token,))
            
            link_data = cursor.fetchone()
            
            if not link_data:
                return None
                
            # Verificar se link expirou
            expires_at = datetime.fromisoformat(link_data[8])
            if datetime.now() > expires_at:
                self.log_system_event('warning', 'link', f'Link expirado: {link_token}')
                return None
                
            # Verificar limite de acessos
            if link_data[9] > 0 and link_data[10] >= link_data[9]:
                self.log_system_event('warning', 'link', f'Limite de acessos atingido: {link_token}')
                return None
                
            # Verificar código de acesso se necessário
            if access_code and link_data[3] != access_code:
                self.log_system_event('warning', 'link', f'Código de acesso inválido: {link_token}')
                return None
                
            # Incrementar contador de acessos
            cursor.execute("""
                UPDATE rnc_links 
                SET current_accesses = current_accesses + 1
                WHERE id = ?
            """, (link_data[0],))
            
            # Registrar acesso
            cursor.execute("""
                INSERT INTO link_accesses (link_id, ip_address, user_agent)
                VALUES (?, ?, ?)
            """, (link_data[0], '127.0.0.1', 'Web Browser'))
            
            conn.commit()
            conn.close()
            
            # Retornar dados do RNC
            rnc_data = {
                'link_id': link_data[0],
                'rnc_id': link_data[1],
                'rnc_number': link_data[12],
                'title': link_data[13],
                'description': link_data[14],
                'equipment': link_data[15],
                'client': link_data[16],
                'created_at': link_data[17],
                'created_by': link_data[18],
                'expires_at': link_data[8],
                'accesses_remaining': max(0, link_data[9] - link_data[10] - 1)
            }
            
            self.log_system_event('info', 'link', f'Link acessado: {link_token}', {
                'link_id': link_data[0],
                'rnc_id': link_data[1]
            })
            
            return rnc_data
            
        except Exception as e:
            logger.error(f"Erro ao validar link: {e}")
            return None
            
    def get_link_statistics(self, link_id: int) -> Dict:
        """Obtém estatísticas de um link"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Dados do link
            cursor.execute("""
                SELECT l.*, r.rnc_number, r.title
                FROM rnc_links l
                JOIN rnc_reports r ON l.rnc_id = r.id
                WHERE l.id = ?
            """, (link_id,))
            
            link_data = cursor.fetchone()
            
            if not link_data:
                return {}
                
            # Histórico de acessos
            cursor.execute("""
                SELECT accessed_at, ip_address, user_agent, access_successful
                FROM link_accesses
                WHERE link_id = ?
                ORDER BY accessed_at DESC
            """, (link_id,))
            
            accesses = cursor.fetchall()
            
            conn.close()
            
            return {
                'link_info': {
                    'id': link_data[0],
                    'rnc_id': link_data[1],
                    'rnc_number': link_data[12],
                    'title': link_data[13],
                    'created_at': link_data[10],
                    'expires_at': link_data[8],
                    'max_accesses': link_data[9],
                    'current_accesses': link_data[10],
                    'is_active': link_data[11]
                },
                'accesses': [
                    {
                        'accessed_at': access[0],
                        'ip_address': access[1],
                        'user_agent': access[2],
                        'successful': access[3]
                    }
                    for access in accesses
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do link: {e}")
            return {}
            
    def deactivate_link(self, link_id: int) -> bool:
        """Desativa um link"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE rnc_links SET is_active = 0 WHERE id = ?
            """, (link_id,))
            
            conn.commit()
            conn.close()
            
            self.log_system_event('info', 'link', f'Link desativado: {link_id}')
            return True
            
        except Exception as e:
            logger.error(f"Erro ao desativar link: {e}")
            return False
            
    def get_active_links_for_rnc(self, rnc_id: int) -> List[Dict]:
        """Obtém todos os links ativos para um RNC"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT l.*, u.name as created_by_name
                FROM rnc_links l
                JOIN users u ON l.created_by = u.id
                WHERE l.rnc_id = ? AND l.is_active = 1
                ORDER BY l.created_at DESC
            """, (rnc_id,))
            
            links = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': link[0],
                    'link_token': link[2],
                    'access_code': link[3],
                    'recipient_email': link[5],
                    'expires_at': link[8],
                    'max_accesses': link[9],
                    'current_accesses': link[10],
                    'created_at': link[11],
                    'created_by': link[12],
                    'link_url': self.generate_link_url(link[2])
                }
                for link in links
            ]
            
        except Exception as e:
            logger.error(f"Erro ao buscar links do RNC: {e}")
            return []
            
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

# Exemplo de uso
if __name__ == "__main__":
    link_system = RNCLinkSystem()
    
    # Exemplo: Criar link para RNC
    # link_data = link_system.create_rnc_link(
    #     rnc_id=1,
    #     created_by=1,
    #     recipient_email="gerente@empresa.com",
    #     expires_in_days=30,
    #     max_accesses=5
    # )
    # print(f"Link criado: {link_data['link_url']}")
    # print(f"Código de acesso: {link_data['access_code']}")
    
    # Exemplo: Validar link
    # rnc_data = link_system.validate_link("token_aqui", "COD123")
    # if rnc_data:
    #     print(f"RNC válido: {rnc_data['rnc_number']}")
    # else:
    #     print("Link inválido ou expirado") 
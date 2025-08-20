#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INICIALIZADOR DO SISTEMA IPPEL
Script para configurar completamente o sistema
"""

import sqlite3
import os
import sys
from datetime import datetime

def init_database():
    """Inicializa o banco de dados com todas as tabelas"""
    print("🔧 Inicializando banco de dados...")
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Criar tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                department TEXT,
                role TEXT DEFAULT 'inspector',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Criar tabela de RNCs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rnc_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rnc_number TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                equipment TEXT,
                client TEXT,
                priority TEXT DEFAULT 'Média',
                status TEXT DEFAULT 'Pendente',
                inspector_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inspector_id) REFERENCES users(id)
            )
        """)
        
        # Criar tabela de detalhes do RNC
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rnc_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rnc_id INTEGER NOT NULL,
                item_description TEXT NOT NULL,
                instruction TEXT,
                cause TEXT,
                action TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rnc_id) REFERENCES rnc_reports(id)
            )
        """)
        
        # Criar tabela de assinaturas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rnc_signatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rnc_id INTEGER NOT NULL,
                signature_type TEXT NOT NULL,
                signature_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                signer_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rnc_id) REFERENCES rnc_reports(id)
            )
        """)
        
        # Criar tabela de threads de email
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT UNIQUE NOT NULL,
                rnc_id INTEGER,
                subject TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rnc_id) REFERENCES rnc_reports(id)
            )
        """)
        
        # Criar tabela de mensagens de email
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                message_id TEXT UNIQUE NOT NULL,
                from_email TEXT NOT NULL,
                to_email TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT,
                html_body TEXT,
                attachments TEXT,
                direction TEXT NOT NULL,
                status TEXT DEFAULT 'sent',
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (thread_id) REFERENCES email_threads(thread_id)
            )
        """)
        
        # Criar tabela de notificações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                rnc_id INTEGER,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (rnc_id) REFERENCES rnc_reports(id)
            )
        """)
        
        # Criar tabela de configurações do sistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Criar tabela de logs do sistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                category TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Inserir usuário administrador padrão
        from werkzeug.security import generate_password_hash
        
        admin_password = generate_password_hash('admin123')
        
        cursor.execute("""
            INSERT OR IGNORE INTO users (name, email, password_hash, department, role)
            VALUES (?, ?, ?, ?, ?)
        """, ('Administrador', 'admin@ippel.com.br', admin_password, 'TI', 'admin'))
        
        # Inserir configurações padrão
        configs = [
            ('smtp_host', 'smtp.gmail.com', 'Servidor SMTP'),
            ('smtp_port', '587', 'Porta SMTP'),
            ('smtp_username', 'ippel@gmail.com', 'Email SMTP'),
            ('smtp_password', '', 'Senha SMTP'),
            ('email_from_name', 'Sistema IPPEL', 'Nome do remetente'),
            ('imap_host', 'imap.gmail.com', 'Servidor IMAP'),
            ('imap_port', '993', 'Porta IMAP'),
            ('imap_username', 'ippel@gmail.com', 'Email IMAP'),
            ('imap_password', '', 'Senha IMAP'),
            ('system_name', 'Sistema IPPEL', 'Nome do sistema'),
            ('company_name', 'IPPEL', 'Nome da empresa')
        ]
        
        for key, value, description in configs:
            cursor.execute("""
                INSERT OR IGNORE INTO system_config (config_key, config_value, description)
                VALUES (?, ?, ?)
            """, (key, value, description))
        
        # Commit das alterações
        conn.commit()
        conn.close()
        
        print("✅ Banco de dados inicializado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False

def check_templates():
    """Verifica se todos os templates existem"""
    print("📋 Verificando templates...")
    
    required_templates = [
        'templates/base.html',
        'templates/login.html',
        'templates/dashboard.html',
        'templates/new_rnc.html',
        'templates/list_rncs.html',
        'templates/view_rnc.html',
        'templates/notifications.html',
        'templates/view_rnc_public.html',
        'templates/error.html'
    ]
    
    missing_templates = []
    
    for template in required_templates:
        if not os.path.exists(template):
            missing_templates.append(template)
        else:
            print(f"✅ {template}")
    
    if missing_templates:
        print(f"❌ Templates faltando: {missing_templates}")
        return False
    else:
        print("✅ Todos os templates estão presentes!")
        return True

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print("📦 Verificando dependências...")
    
    required_packages = [
        'flask',
        'flask_login',
        'werkzeug',
        'jinja2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - FALTANDO")
    
    if missing_packages:
        print(f"❌ Pacotes faltando: {missing_packages}")
        print("💡 Execute: pip install -r requirements.txt")
        return False
    else:
        print("✅ Todas as dependências estão instaladas!")
        return True

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 INICIALIZADOR DO SISTEMA IPPEL")
    print("=" * 60)
    print()
    
    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Instale as dependências primeiro!")
        return False
    
    print()
    
    # Verificar templates
    if not check_templates():
        print("\n❌ Templates estão faltando!")
        return False
    
    print()
    
    # Inicializar banco de dados
    if not init_database():
        print("\n❌ Falha ao inicializar banco de dados!")
        return False
    
    print()
    print("=" * 60)
    print("✅ SISTEMA INICIALIZADO COM SUCESSO!")
    print("=" * 60)
    print()
    print("🌐 Para iniciar o servidor:")
    print("   python main_system.py")
    print()
    print("🔐 Credenciais padrão:")
    print("   Email: admin@ippel.com.br")
    print("   Senha: admin123")
    print()
    print("📱 Acesse em:")
    print("   http://192.168.0.100:5000")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    main() 
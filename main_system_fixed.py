#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA PRINCIPAL - RELATÓRIOS DE NÃO CONFORMIDADES IPPEL
Sistema completo com banco de dados, email bidirecional e interface web
VERSÃO CORRIGIDA - Trata erros de backup e inicialização
"""

import sqlite3
import os
import logging
import threading
import time
import datetime
import uuid
import secrets
import random
import hashlib
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'ippel_secret_key_2024'

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configurações do banco
DB_PATH = 'ippel_system.db'

# Backup: diretório de destino no Windows (fornecido pelo cliente)
BACKUP_DIR = r'G:\Meu Drive\BACKUP BANCO DE DADOS IPPEL'

def ensure_backup_dir_exists() -> bool:
    """Tenta criar diretório de backup, retorna True se sucesso"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        return True
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível criar diretório de backup '{BACKUP_DIR}': {e}")
        print("💡 O sistema continuará funcionando, mas sem backup automático")
        return False

def backup_database_now() -> bool:
    """Snapshot consistente utilizando API de backup do SQLite."""
    if not ensure_backup_dir_exists():
        return False
        
    try:
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = os.path.join(BACKUP_DIR, f"ippel_system_{ts}.db")
        
        src = sqlite3.connect(DB_PATH, timeout=30.0)
        dst = sqlite3.connect(dest, timeout=30.0)
        
        with dst:
            src.backup(dst)
        
        src.close()
        dst.close()
        print(f"✅ Backup criado: {dest}")
        return True
        
    except Exception as e:
        print(f"⚠️ Erro ao criar backup: {e}")
        return False

def start_backup_scheduler(interval_seconds: int = 480) -> bool:
    """Inicia agendador de backup, retorna True se sucesso"""
    try:
        def _run():
            try:
                # Backup imediato ao iniciar
                if backup_database_now():
                    print("✅ Backup inicial realizado com sucesso")
                else:
                    print("⚠️ Backup inicial falhou, continuando...")
                
                while True:
                    time.sleep(interval_seconds)
                    backup_database_now()
            except Exception as e:
                print(f"❌ Erro no agendador de backup: {e}")
                print("💡 O sistema continuará funcionando sem backup automático")
        
        thread = threading.Thread(target=_run, name='BackupScheduler', daemon=True)
        thread.start()
        return True
        
    except Exception as e:
        print(f"❌ Falha ao iniciar agendador de backup: {e}")
        return False

class User(UserMixin):
    def __init__(self, id, name, email, department, role):
        self.id = id
        self.name = name
        self.email = email
        self.department = department
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, email, department, role 
            FROM users WHERE id = ?
        """, (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
        return None
    except Exception as e:
        logger.error(f"Erro ao carregar usuário: {e}")
        return None

def init_database():
    """Inicializar banco de dados se não existir"""
    try:
        if not os.path.exists(DB_PATH):
            print("🗄️ Criando banco de dados...")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Criar tabelas
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    department TEXT,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE rnc_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rnc_number TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    equipment TEXT,
                    client TEXT,
                    priority TEXT DEFAULT 'Média',
                    status TEXT DEFAULT 'Pendente',
                    price REAL DEFAULT 0,
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE rnc_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rnc_id INTEGER NOT NULL,
                    item_number INTEGER,
                    description TEXT,
                    instruction TEXT,
                    cause TEXT,
                    action TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (rnc_id) REFERENCES rnc_reports (id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE rnc_signatures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rnc_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    signature_type TEXT NOT NULL,
                    signature_data TEXT,
                    signed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (rnc_id) REFERENCES rnc_reports (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Tabela de grupos (para compartilhamento/seleção no formulário)
            cursor.execute('''
                CREATE TABLE groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT DEFAULT ''
                )
            ''')

            # Popular grupos padrão
            default_groups = [
                ('Produção', 'Grupo de Produção'),
                ('Engenharia', 'Grupo de Engenharia'),
                ('Compras', 'Grupo de Compras'),
                ('Comercial', 'Grupo Comercial'),
                ('PCP', 'Planejamento e Controle da Produção'),
                ('Qualidade', 'Grupo de Qualidade'),
                ('Manutenção', 'Grupo de Manutenção'),
                ('Logística', 'Grupo de Logística')
            ]
            cursor.executemany('INSERT OR IGNORE INTO groups (name, description) VALUES (?, ?)', default_groups)
            
            # Inserir usuário admin padrão
            admin_password = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO users (name, email, password_hash, department, role)
                VALUES (?, ?, ?, ?, ?)
            ''', ('Administrador', 'admin@ippel.com.br', admin_password, 'Administração', 'admin'))
            
            # Inserir alguns usuários de exemplo
            users_data = [
                ('João Silva', 'joao@ippel.com.br', generate_password_hash('joao123'), 'Produção', 'user'),
                ('Maria Santos', 'maria@ippel.com.br', generate_password_hash('maria123'), 'Qualidade', 'user'),
                ('Pedro Costa', 'pedro@ippel.com.br', generate_password_hash('pedro123'), 'Manutenção', 'user'),
            ]
            cursor.executemany('''
                INSERT INTO users (name, email, password_hash, department, role)
                VALUES (?, ?, ?, ?, ?)
            ''', users_data)
            
            conn.commit()
            conn.close()
            print("✅ Banco de dados criado com sucesso!")
        else:
            print("✅ Banco de dados já existe")
            
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        print("💡 Tentando continuar sem inicialização...")

# Rotas básicas para teste
@app.route('/')
def index():
    return '''
    <h1>🚀 Sistema IPPEL Admin</h1>
    <p>Servidor funcionando corretamente!</p>
    <ul>
        <li><a href="/dashboard">Dashboard</a></li>
        <li><a href="/status">Status</a></li>
    </ul>
    '''

@app.route('/status')
def status():
    return jsonify({
        'status': 'online',
        'timestamp': datetime.datetime.now().isoformat(),
        'message': 'Sistema IPPEL funcionando corretamente'
    })

@app.route('/dashboard')
def dashboard():
    return '''
    <h1>📊 Dashboard IPPEL</h1>
    <p>Sistema de Relatórios de Não Conformidades</p>
    <p><strong>Status:</strong> ✅ Funcionando</p>
    '''

if __name__ == '__main__':
    print("🚀 Iniciando Sistema IPPEL Admin...")
    print("=" * 50)
    
    try:
        # Inicializar banco de dados
        init_database()
        
        # Iniciar backup automático do banco (imediato e a cada 8 minutos)
        if start_backup_scheduler(interval_seconds=480):
            print("✅ Agendador de backup iniciado")
        else:
            print("⚠️ Agendador de backup não iniciado, mas sistema continuará funcionando")
        
        # Obter IP local
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "127.0.0.1"
        
        print("🚀 Sistema IPPEL Admin iniciado!")
        print("=" * 50)
        print(f"📊 Painel Admin: http://{local_ip}:5000")
        print(f"📋 Formulário: http://{local_ip}:5001")
        print("=" * 50)
        print("💡 Use o start_admin.bat para iniciar este servidor")
        print("💡 Use o start_form.bat para iniciar o formulário")
        print("=" * 50)
        
        # Iniciar servidor Flask
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Erro fatal ao iniciar sistema: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Verifique os logs acima para identificar o problema")

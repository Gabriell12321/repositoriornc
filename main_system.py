#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA PRINCIPAL - RELATÓRIOS DE NÃO CONFORMIDADES IPPEL
Sistema completo com banco de dados, email bidirecional e interface web
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

import threading
import time
import datetime

def ensure_backup_dir_exists() -> None:
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
    except Exception as e:
        print(f"Erro ao criar diretório de backup '{BACKUP_DIR}': {e}")

def backup_database_now() -> None:
    """Snapshot consistente utilizando API de backup do SQLite."""
    ensure_backup_dir_exists()
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = os.path.join(BACKUP_DIR, f"ippel_system_{ts}.db")
    try:
        src = sqlite3.connect(DB_PATH, timeout=30.0)
        dst = sqlite3.connect(dest, timeout=30.0)
        with dst:
            src.backup(dst)
        src.close(); dst.close()
        print(f"✅ Backup criado: {dest}")
    except Exception as e:
        print(f"⚠️ Erro ao criar backup: {e}")

def start_backup_scheduler(interval_seconds: int = 480) -> None:
    def _run():
        # Backup imediato ao iniciar
        backup_database_now()
        while True:
            time.sleep(interval_seconds)
            backup_database_now()
    threading.Thread(target=_run, name='BackupScheduler', daemon=True).start()

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
    if not os.path.exists(DB_PATH):
        try:
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
                ('João Silva', 'joao@ippel.com.br', 'joao123', 'Produção', 'user'),
                ('Maria Santos', 'maria@ippel.com.br', 'maria123', 'Qualidade', 'user'),
                ('Pedro Costa', 'pedro@ippel.com.br', 'pedro123', 'Manutenção', 'user'),
                ('Ana Oliveira', 'ana@ippel.com.br', 'ana123', 'Engenharia', 'user')
            ]
            
            for name, email, password, dept, role in users_data:
                password_hash = generate_password_hash(password)
                cursor.execute('''
                    INSERT INTO users (name, email, password_hash, department, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, email, password_hash, dept, role))
            
            conn.commit()
            conn.close()
            logger.info("Banco de dados inicializado com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar banco: {e}")

def ensure_schema_migrations():
    """Garantir que a tabela rnc_reports possua a coluna price."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(rnc_reports)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'price' not in columns:
            cursor.execute("ALTER TABLE rnc_reports ADD COLUMN price REAL DEFAULT 0")
            conn.commit()
            logger.info("Migração aplicada: coluna 'price' adicionada em rnc_reports")

        # Garantir tabela de grupos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='groups'")
        if cursor.fetchone() is None:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT DEFAULT ''
                )
            ''')
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
            conn.commit()
            logger.info("Migração aplicada: tabela 'groups' criada e populada")
        conn.close()
    except Exception as e:
        logger.error(f"Erro ao aplicar migração de schema: {e}")

# --- Suporte a clientes (para selects/autocomplete) ---
def ensure_clients_table():
    """Garantir que a tabela 'clients' exista para uso em formulários."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS clients (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT UNIQUE NOT NULL,
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
               )'''
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Erro ao garantir tabela clients: {e}")

class RNCSystem:
    def __init__(self, db_path: str):
        self.db_path = db_path
        # Garantir migrações de schema necessárias
        ensure_schema_migrations()
    
    def _get_conn(self):
        """Obter conexão configurada com timeout e WAL."""
        conn = sqlite3.connect(self.db_path, timeout=10, isolation_level=None)  # autocommit
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA busy_timeout=8000;")
        except Exception:
            pass
        return conn
        
    def create_rnc(self, data: dict) -> int:
        """Criar novo RNC"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Gerar número do RNC
            rnc_number = self.generate_rnc_number()
            
            cursor.execute("""
                INSERT INTO rncs 
                (rnc_number, title, description, equipment, client, priority, status, price, user_id, department)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rnc_number,
                data.get('title', 'RNC sem título'),
                data.get('description', ''),
                data.get('equipment', ''),
                data.get('client', ''),
                data.get('priority', 'Média'),
                data.get('status', 'Pendente'),
                float(data.get('price') or 0),
                data.get('user_id', 1),
                data.get('department', '')  # Incluir o departamento/grupo
            ))
            
            rnc_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"RNC criado com sucesso: {rnc_number}")
            return rnc_id
            
        except Exception as e:
            logger.error(f"Erro ao criar RNC: {e}")
            return None
            
    def generate_rnc_number(self) -> str:
        """Gerar número único do RNC"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar último número
            cursor.execute("SELECT MAX(CAST(SUBSTR(rnc_number, 5) AS INTEGER)) FROM rncs")
            result = cursor.fetchone()
            
            if result[0] is None:
                next_number = 1
            else:
                next_number = result[0] + 1
                
            conn.close()
            
            # Formato: RNC-2024-0001
            year = datetime.datetime.now().year
            return f"RNC-{year}-{next_number:04d}"
            
        except Exception as e:
            logger.error(f"Erro ao gerar número RNC: {e}")
            return f"RNC-{datetime.datetime.now().year}-{int(time.time())}"
            
    def get_rnc_list(self, user_id: int = None, filters: dict = None) -> list:
        """Busca lista de RNCs considerando compartilhamentos (rnc_shares).
        Regras:
        - Admin: vê todas
        - Usuário comum: vê próprias, departamento e compartilhadas explicitamente
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Primeiro, obter informações do usuário para filtrar por departamento
            user_department = None
            user_role = None
            if user_id:
                cursor.execute("SELECT department, role FROM users WHERE id = ?", (user_id,))
                user_info = cursor.fetchone()
                if user_info:
                    user_department = user_info[0]
                    user_role = user_info[1]
            
            # Query base - inclui compartilhamentos
            query = """
                SELECT DISTINCT r.id, r.rnc_number, r.title, r.status, r.priority,
                                r.created_at, u.name as user_name, r.department
                FROM rncs r
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN rnc_shares rs ON rs.rnc_id = r.id
                WHERE r.is_deleted = 0
            """
            params = []

            if user_id and user_role != 'admin':
                # Mostrar RNCs criadas pelo usuário, do departamento ou compartilhadas
                if user_department:
                    query += " AND (r.user_id = ? OR r.department = ? OR rs.shared_with_user_id = ?)"
                    params.extend([user_id, user_department, user_id])
                else:
                    query += " AND (r.user_id = ? OR rs.shared_with_user_id = ?)"
                    params.extend([user_id, user_id])
            # Admin mantém visão total sem filtros extras
            
            if filters:
                if filters.get('status'):
                    query += " AND r.status = ?"
                    params.append(filters['status'])
                    
                if filters.get('priority'):
                    query += " AND r.priority = ?"
                    params.append(filters['priority'])
                    
                if filters.get('department'):
                    query += " AND r.department = ?"
                    params.append(filters['department'])
            
            query += " ORDER BY r.created_at DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'rnc_number': row[1],
                    'title': row[2],
                    'status': row[3],
                    'priority': row[4],
                    'created_at': row[5],
                    'user_name': row[6],
                    'department': row[7] if len(row) > 7 else None
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Erro ao buscar RNCs: {e}")
            return []
            
    def get_rnc_details(self, rnc_id: int) -> dict:
        """Busca detalhes completos de um RNC"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Dados principais
            cursor.execute("""
                SELECT r.*, u.name as user_name
                FROM rncs r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.id = ?
            """, (rnc_id,))
            
            rnc_data = cursor.fetchone()
            if not rnc_data:
                return None
                
            # Detalhes técnicos
            cursor.execute("""
                SELECT * FROM rnc_details WHERE rnc_id = ?
                ORDER BY item_number
            """, (rnc_id,))
            
            details = cursor.fetchall()
            
            # Assinaturas
            cursor.execute("""
                SELECT rs.*, u.name as user_name
                FROM rnc_signatures rs
                JOIN users u ON rs.user_id = u.id
                WHERE rs.rnc_id = ?
                ORDER BY rs.signed_at
            """, (rnc_id,))
            
            signatures = cursor.fetchall()
            
            conn.close()
            
            return {
                'main': rnc_data,
                'details': details,
                'signatures': signatures
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes do RNC {rnc_id}: {e}")
            return None
            
    def update_rnc(self, rnc_id: int, data: dict) -> bool:
        """Atualizar RNC existente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE rnc_reports 
                SET title = ?, description = ?, equipment = ?, client = ?, 
                    priority = ?, status = ?, price = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                data.get('title', ''),
                data.get('description', ''),
                data.get('equipment', ''),
                data.get('client', ''),
                data.get('priority', 'Média'),
                data.get('status', 'Pendente'),
                float(data.get('price') or 0),
                rnc_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"RNC {rnc_id} atualizado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar RNC {rnc_id}: {e}")
            return False

# Instanciar sistema
rnc_system = RNCSystem(DB_PATH)

# Rotas Flask
@app.route('/')
@login_required
def dashboard():
    """Dashboard principal"""
    try:
        # Buscar RNCs do usuário atual
        user_rncs = rnc_system.get_rnc_list(user_id=current_user.id)
        
        # Estatísticas
        total_rncs = len(user_rncs)
        pending_rncs = len([r for r in user_rncs if r['status'] == 'Pendente'])
        completed_rncs = len([r for r in user_rncs if r['status'] == 'Concluído'])
        
        return render_template('dashboard.html', 
                            rncs=user_rncs[:10],  # Últimos 10
                            stats={
                                'total': total_rncs,
                                'pending': pending_rncs,
                                'completed': completed_rncs
                            })
                            
    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        flash('Erro ao carregar dashboard', 'error')
        return render_template('dashboard.html', rncs=[], stats={'total': 0, 'pending': 0, 'completed': 0})

@app.route('/charts-demo')
@login_required
def charts_demo():
    """Página de demonstração dos gráficos avançados"""
    return render_template('charts_demo.html')

@app.route('/dashboard-enhanced')
@login_required
def dashboard_enhanced():
    """Dashboard com gráficos avançados"""
    return render_template('dashboard_enhanced.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, email, password_hash, department, role
                FROM users WHERE email = ?
            """, (email,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data and check_password_hash(user_data[3], password):
                user = User(user_data[0], user_data[1], user_data[2], user_data[4], user_data[5])
                login_user(user)
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Email ou senha incorretos', 'error')
                
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            flash('Erro interno do sistema', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/rnc/new', methods=['GET', 'POST'])
@login_required
def new_rnc():
    """Criar novo RNC"""
    if request.method == 'POST':
        try:
            data = {
                'title': request.form.get('title'),
                'description': request.form.get('description'),
                'equipment': request.form.get('equipment'),
                'client': request.form.get('client'),
                'priority': request.form.get('priority', 'Média'),
                'price': request.form.get('price'),
                'user_id': current_user.id
            }
            
            rnc_id = rnc_system.create_rnc(data)
            
            if rnc_id:
                flash('RNC criado com sucesso!', 'success')
                return redirect(url_for('view_rnc', rnc_id=rnc_id))
            else:
                flash('Erro ao criar RNC', 'error')
                
        except Exception as e:
            logger.error(f"Erro ao criar RNC: {e}")
            flash('Erro interno do sistema', 'error')
    
    # GET: renderizar formulário já com lista de clientes
    try:
        ensure_clients_table()
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT name FROM clients ORDER BY name')
        clients = [row[0] for row in cur.fetchall()]
        conn.close()
    except Exception as e:
        logger.error(f"Erro ao carregar clientes para novo RNC: {e}")
        clients = []
    return render_template('new_rnc.html', clients=clients)

@app.route('/rnc/<int:rnc_id>')
@login_required
def view_rnc(rnc_id):
    """Visualizar RNC específico"""
    try:
        rnc_details = rnc_system.get_rnc_details(rnc_id)
        
        if not rnc_details:
            flash('RNC não encontrado', 'error')
            return redirect(url_for('dashboard'))
            
        # Verificar se o usuário tem acesso a este RNC
        if rnc_details['main'][9] != current_user.id and current_user.role != 'admin':
            flash('Acesso negado', 'error')
            return redirect(url_for('dashboard'))
            
        return render_template('view_rnc.html', rnc=rnc_details)
        
    except Exception as e:
        logger.error(f"Erro ao visualizar RNC {rnc_id}: {e}")
        flash('Erro interno do sistema', 'error')
        return redirect(url_for('dashboard'))

@app.route('/rnc/list')
@login_required
def list_rncs():
    """Listar todos os RNCs do usuário"""
    try:
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('priority'):
            filters['priority'] = request.args.get('priority')
            
        rncs = rnc_system.get_rnc_list(user_id=current_user.id, filters=filters)
        return render_template('list_rncs.html', rncs=rncs)
        
    except Exception as e:
        logger.error(f"Erro ao listar RNCs: {e}")
        flash('Erro interno do sistema', 'error')
        return render_template('list_rncs.html', rncs=[])

# APIs para integração com formulário
@app.route('/api/rnc/create', methods=['POST'])
def create_rnc_from_form():
    """API para criar RNC a partir do formulário index.html"""
    try:
        data = request.get_json()
        
        # Verificar se usuário está logado
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            }), 401
        
        # Processar grupos selecionados para obter o departamento
        shared_group_ids = data.get('shared_group_ids', [])
        department = ''
        
        if shared_group_ids:
            # Conectar ao banco para buscar o nome do grupo selecionado
            try:
                conn = sqlite3.connect('ippel_system.db')
                cursor = conn.cursor()
                
                # Buscar nome do primeiro grupo selecionado pela tabela groups
                for group_id in shared_group_ids:
                    if group_id and str(group_id).isdigit():
                        cursor.execute("SELECT name FROM groups WHERE id = ?", (group_id,))
                        result = cursor.fetchone()
                        if result and result[0]:
                            department = result[0]
                            break
                conn.close()
                
            except Exception as e:
                logger.error(f"Erro ao processar grupos: {e}")
                department = ''
        
        # Fallback: se ainda vazio, usar primeiro grupo como texto (caso frontend envie nomes futuramente)
        if not department and shared_group_ids:
            department = str(shared_group_ids[0])
        
        # Extrair dados do formulário
        rnc_data = {
            'title': data.get('title', 'RNC sem título'),
            'description': data.get('description', ''),
            'equipment': data.get('equipment', ''),
            'client': data.get('client', ''),
            'priority': data.get('priority', 'Média'),
            'status': 'Pendente',
            'price': data.get('price', 0),
            'user_id': current_user.id,
            'department': department  # Incluir o departamento dos grupos selecionados
        }
        
        # Log para debug
        logger.info(f"Criando RNC - Usuário: {current_user.username}, Grupos selecionados: {shared_group_ids}, Departamento atribuído: {department}")
        
        # Criar RNC no sistema
        rnc_id = rnc_system.create_rnc(rnc_data)
        
        if rnc_id:
            # Buscar dados do RNC criado
            rnc_details = rnc_system.get_rnc_details(rnc_id)
            
            # Registrar compartilhamentos explícitos para usuários dos grupos selecionados
            try:
                if shared_group_ids:
                    import time
                    conn = rnc_system._get_conn()
                    cursor = conn.cursor()
                    total_shared = 0
                    for group_id in shared_group_ids:
                        if not group_id:
                            continue
                        if str(group_id).isdigit():
                            cursor.execute("SELECT name FROM groups WHERE id = ?", (group_id,))
                            g = cursor.fetchone()
                            group_name = g[0] if g else None
                        else:
                            group_name = str(group_id)
                        if str(group_id).isdigit():
                            cursor.execute("SELECT id FROM users WHERE (group_id = ? OR department = ?) AND is_active = 1", (group_id, group_name))
                        else:
                            cursor.execute("SELECT id FROM users WHERE department = ? AND is_active = 1", (group_name,))
                        user_rows = cursor.fetchall()
                        for (uid,) in user_rows:
                            if uid == current_user.id:
                                continue
                            # Retry simples em caso de database locked
                            for attempt in range(5):
                                try:
                                    cursor.execute("""
                                        INSERT OR IGNORE INTO rnc_shares (rnc_id, shared_by_user_id, shared_with_user_id, permission_level)
                                        VALUES (?, ?, ?, 'view')
                                    """, (rnc_id, current_user.id, uid))
                                    total_shared += 1
                                    break
                                except sqlite3.OperationalError as ex:
                                    if 'locked' in str(ex).lower() and attempt < 4:
                                        time.sleep(0.3 * (attempt + 1))
                                        continue
                                    else:
                                        raise
                    conn.commit(); conn.close()
                    logger.info(f"RNC {rnc_id} compartilhada com {total_shared} usuários (agrupamento misto) grupos={shared_group_ids} dept={department}")
            except Exception as e:
                logger.error(f"Falha ao registrar compartilhamentos da RNC {rnc_id}: {e}")
            
            return jsonify({
                'success': True,
                'message': 'RNC criado com sucesso!',
                'rnc_id': rnc_id,
                'rnc_number': rnc_details['main'][1] if rnc_details else None,
                'redirect_url': f'/rnc/{rnc_id}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao criar RNC'
            }), 400
            
    except Exception as e:
        logger.error(f"Erro ao criar RNC via API: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/rnc/<int:rnc_id>/details')
@login_required
def get_rnc_details_api(rnc_id):
    """API para obter detalhes de um RNC"""
    try:
        rnc_details = rnc_system.get_rnc_details(rnc_id)
        
        if rnc_details:
            # Verificar acesso
            if rnc_details['main'][9] != current_user.id and current_user.role != 'admin':
                return jsonify({
                    'success': False,
                    'message': 'Acesso negado'
                }), 403
                
            return jsonify({
                'success': True,
                'rnc': rnc_details
            })
        else:
            return jsonify({
                'success': False,
                'message': 'RNC não encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"Erro ao buscar RNC {rnc_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/rnc/list')
def get_rnc_list_api():
    """API para listar RNCs do usuário"""
    try:
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            }), 401
        
        # Verificar o parâmetro tab para filtrar por status
        tab = request.args.get('tab', 'active')
        
        # Configurar filtros baseados na aba
        filters = {}
        if tab == 'finalized':
            filters['status'] = 'finalizado'
        elif tab == 'active':
            # Para aba "active", filtrar por status não finalizado
            # Buscar todas e filtrar no código (ou ajustar query depois)
            pass
            
        rncs = rnc_system.get_rnc_list(user_id=current_user.id, filters=filters)
        
        # Se tab = 'active', filtrar apenas os não finalizados
        if tab == 'active':
            rncs = [rnc for rnc in rncs if rnc['status'] != 'finalizado']
        
        return jsonify({
            'success': True,
            'rncs': rncs
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar RNCs: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@app.route('/api/admin/groups', methods=['GET'])
def api_get_groups():
    """Retornar lista de grupos para seleção no formulário.
    Acesso: qualquer usuário autenticado. Mantém o formato esperado pelo index.html
    """
    try:
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM groups ORDER BY name")
        rows = cursor.fetchall()
        conn.close()

        groups_list = [
            {
                'id': row[0],
                'name': row[1],
                'description': row[2] or '',
                'user_count': 0
            }
            for row in rows
        ]

        return jsonify({'success': True, 'groups': groups_list})
    except Exception as e:
        logger.error(f"Erro ao listar grupos: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do sistema'}), 500


@app.route('/api/logout')
def api_logout():
    """Logout via API, usado pelo formulário público."""
    try:
        if current_user.is_authenticated:
            logout_user()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erro no logout: {e}")
        return jsonify({'success': False, 'message': 'Erro ao fazer logout'}), 500

@app.route('/api/user/info')
def get_user_info():
    """API para obter informações do usuário logado"""
    try:
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            }), 401
            
        return jsonify({
            'success': True,
            'user': {
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email,
                'department': current_user.department,
                'role': current_user.role
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter informações do usuário: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/admin/groups', methods=['GET'])
def api_admin_groups():
    """Retorna lista de grupos para seleção no formulário.
    Qualquer usuário autenticado pode listar grupos (não exige permissão admin)."""
    try:
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM groups ORDER BY name")
        rows = cursor.fetchall()

        groups_list = []
        for row in rows:
            group_id, group_name, description = row
            # Estimar número de usuários pelo campo department
            cursor.execute("SELECT COUNT(*) FROM users WHERE department = ?", (group_name,))
            count = cursor.fetchone()[0]
            groups_list.append({
                'id': group_id,
                'name': group_name,
                'description': description or '',
                'user_count': count
            })

        conn.close()
        return jsonify({'success': True, 'groups': groups_list})
    except Exception as e:
        logger.error(f"Erro ao listar grupos: {e}")
        return jsonify({'success': False, 'message': 'Erro interno ao listar grupos'}), 500

@app.route('/api/charts/enhanced-data')
def api_charts_enhanced_data():
    """Endpoint para dados dos gráficos aprimorados com dados reais da planilha de indicadores"""
    try:
        period = request.args.get('period', '30')
        department = request.args.get('department', 'all')
        # Tentar carregar dados reais da planilha de indicadores
        import json
        import os
        from pathlib import Path
        # Prefer JSON files under data/ quando presente para manter a raiz limpa
        _ROOT = Path(__file__).resolve().parent
        _DATA_DIR = _ROOT / 'data'
        api_data_file = str((_DATA_DIR / 'api_chart_data.json') if (_DATA_DIR / 'api_chart_data.json').exists() else (_ROOT / 'api_chart_data.json'))
        if os.path.exists(api_data_file):
            try:
                with open(api_data_file, 'r', encoding='utf-8') as f:
                    real_data = json.load(f)
                
                # Se os dados foram carregados com sucesso, usar dados reais
                if real_data.get('success'):
                    logger.info("Usando dados reais da planilha de indicadores")
                    
                    # Enriquecer com dados adicionais para os gráficos
                    chart_data = real_data['data'].copy()
                    
                    # Adicionar dados de tendência simulados baseados nos dados reais
                    chart_data['trend'] = [
                        {'date': '2025-08-01', 'count': 12},
                        {'date': '2025-08-02', 'count': 8},
                        {'date': '2025-08-03', 'count': 15},
                        {'date': '2025-08-04', 'count': 6},
                        {'date': '2025-08-05', 'count': 18},
                        {'date': '2025-08-06', 'count': 11},
                        {'date': '2025-08-07', 'count': 9}
                    ]
                    
                    # Adicionar dados de status baseados nos departamentos
                    total_rncs = sum(dept['count'] for dept in chart_data.get('departments', []))
                    chart_data['status'] = [
                        {'label': 'Aberta', 'count': int(total_rncs * 0.3), 'color': '#ff6b6b'},
                        {'label': 'Em Análise', 'count': int(total_rncs * 0.25), 'color': '#4ecdc4'},
                        {'label': 'Aguardando', 'count': int(total_rncs * 0.15), 'color': '#45b7d1'},
                        {'label': 'Finalizada', 'count': int(total_rncs * 0.3), 'color': '#96ceb4'}
                    ]
                    
                    # Adicionar dados de prioridade
                    chart_data['priority'] = [
                        {'label': 'Baixa', 'count': int(total_rncs * 0.4), 'color': '#4ade80'},
                        {'label': 'Média', 'count': int(total_rncs * 0.35), 'color': '#fbbf24'},
                        {'label': 'Alta', 'count': int(total_rncs * 0.2), 'color': '#f97316'},
                        {'label': 'Crítica', 'count': int(total_rncs * 0.05), 'color': '#ef4444'}
                    ]
                    
                    # Adicionar dados para outros gráficos
                    chart_data.update({
                        'area': {
                            'dates': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                            'datasets': [
                                {'label': 'Abertas', 'data': [20, 25, 18, 30, 22, 28]},
                                {'label': 'Em Análise', 'data': [15, 20, 12, 25, 18, 22]},
                                {'label': 'Finalizadas', 'data': [35, 40, 30, 45, 38, 42]}
                            ]
                        },
                        'scatter': {
                            'data': [
                                {'x': 1, 'y': 5}, {'x': 2, 'y': 8}, {'x': 3, 'y': 12}, {'x': 4, 'y': 15},
                                {'x': 1, 'y': 3}, {'x': 2, 'y': 6}, {'x': 3, 'y': 9}, {'x': 4, 'y': 18}
                            ]
                        },
                        'stacked': {
                            'labels': ['Engenharia', 'Produção', 'Suprimentos', 'PCP'],
                            'datasets': [
                                {'label': 'Abertas', 'data': [12, 8, 15, 6]},
                                {'label': 'Em Análise', 'data': [8, 12, 10, 4]},
                                {'label': 'Finalizadas', 'data': [25, 18, 22, 12]}
                            ]
                        },
                        'heatmap': []
                    })
                    
                    # Gerar dados do heatmap
                    for day in range(7):
                        for hour in range(24):
                            chart_data['heatmap'].append({
                                'x': hour,
                                'y': day, 
                                'v': random.randint(1, 15)
                            })
                    
                    return jsonify({'success': True, 'data': chart_data})
                    
            except Exception as e:
                logger.warning(f"Erro ao carregar dados da planilha: {e}")
        
        # Fallback para dados simulados se não conseguir carregar dados reais
        logger.info("Usando dados simulados - planilha não disponível")
        
        # Dados simulados realistas baseados no banco
        data = {
            'trend': [
                {'date': '202000'
                ''
                '5-08-01', 'count': 12},
                {'date': '2025-08-02', 'count': 8},
                {'date': '2025-08-03', 'count': 15},
                {'date': '2025-08-04', 'count': 6},
                {'date': '2025-08-05', 'count': 18},
                {'date': '2025-08-06', 'count': 11},
                {'date': '2025-08-07', 'count': 9}
            ],
            'status': [
                {'label': 'Aberta', 'count': 125, 'color': '#ff6b6b'},
                {'label': 'Em Análise', 'count': 89, 'color': '#4ecdc4'},
                {'label': 'Aguardando', 'count': 34, 'color': '#45b7d1'},
                {'label': 'Finalizada', 'count': 342, 'color': '#96ceb4'}
            ],
            'priority': [
                {'label': 'Baixa', 'count': 180, 'color': '#4ade80'},
                {'label': 'Média', 'count': 250, 'color': '#fbbf24'},
                {'label': 'Alta', 'count': 120, 'color': '#f97316'},
                {'label': 'Crítica', 'count': 40, 'color': '#ef4444'}
            ],
            'users': [
                {'label': 'João Silva', 'count': 25},
                {'label': 'Maria Santos', 'count': 18},
                {'label': 'Carlos Lima', 'count': 22},
                {'label': 'Ana Costa', 'count': 15},
                {'label': 'Pedro Rocha', 'count': 12}
            ],
            'equipment': [
                {'label': 'Torno CNC', 'count': 8},
                {'label': 'Prensa Hidráulica', 'count': 12},
                {'label': 'Soldadora MIG', 'count': 6},
                {'label': 'Compressor', 'count': 9},
                {'label': 'Fresa', 'count': 7}
            ],
            'kpis': {'total': 590, 'resolved': 512},
            'departments': [
                {'label': 'Produção', 'count': 45, 'efficiency': 85},
                {'label': 'Qualidade', 'count': 32, 'efficiency': 92},
                {'label': 'Manutenção', 'count': 28, 'efficiency': 78},
                {'label': 'Comercial', 'count': 15, 'efficiency': 95}
            ],
            'heatmap': [],
            'area': {
                'dates': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                'datasets': [
                    {'label': 'Abertas', 'data': [20, 25, 18, 30, 22, 28]},
                    {'label': 'Em Análise', 'data': [15, 20, 12, 25, 18, 22]},
                    {'label': 'Finalizadas', 'data': [35, 40, 30, 45, 38, 42]}
                ]
            },
            'scatter': {
                'data': [
                    {'x': 1, 'y': 5}, {'x': 2, 'y': 8}, {'x': 3, 'y': 12}, {'x': 4, 'y': 15},
                    {'x': 1, 'y': 3}, {'x': 2, 'y': 6}, {'x': 3, 'y': 9}, {'x': 4, 'y': 18}
                ]
            },
            'stacked': {
                'labels': ['Produção', 'Qualidade', 'Manutenção', 'Comercial'],
                'datasets': [
                    {'label': 'Abertas', 'data': [12, 8, 15, 6]},
                    {'label': 'Em Análise', 'data': [8, 12, 10, 4]},
                    {'label': 'Finalizadas', 'data': [25, 18, 22, 12]}
                ]
            }
        }
        
        # Gerar dados do heatmap
        for day in range(7):
            for hour in range(24):
                data['heatmap'].append({
                    'x': hour,
                    'y': day, 
                    'v': random.randint(1, 20)
                })
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"Erro ao gerar dados dos gráficos: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/dashboard/api/kpis')
def api_kpis():
    """Endpoint para KPIs do dashboard"""
    try:
        return jsonify({
            'total': 2856,
            'avgTime': '7.2',
            'resolution': 87,
            'efficiency': 92,
            'totalChange': 12,
            'avgTimeChange': -8,
            'resolutionChange': 5,
            'efficiencyChange': 3
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/test_charts')
def test_charts():
    """Página de teste dos gráficos"""
    return send_from_directory('.', 'test_charts.html')

@app.route('/rnc/<int:rnc_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_rnc(rnc_id):
    """Editar RNC existente"""
    try:
        rnc_details = rnc_system.get_rnc_details(rnc_id)
        
        if not rnc_details:
            flash('RNC não encontrado', 'error')
            return redirect(url_for('dashboard'))
            
        # Verificar se o usuário tem acesso a este RNC
        if rnc_details['main'][9] != current_user.id and current_user.role != 'admin':
            flash('Acesso negado', 'error')
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            # Processar formulário de edição
            data = {
                'title': request.form.get('title', ''),
                'description': request.form.get('description', ''),
                'equipment': request.form.get('equipment', ''),
                'client': request.form.get('client', ''),
                'priority': request.form.get('priority', 'Média'),
                'status': request.form.get('status', 'Pendente'),
                'price': request.form.get('price')
            }
            
            if rnc_system.update_rnc(rnc_id, data):
                flash('RNC atualizado com sucesso!', 'success')
                return redirect(url_for('view_rnc', rnc_id=rnc_id))
            else:
                flash('Erro ao atualizar RNC', 'error')
                
        return render_template('edit_rnc.html', rnc=rnc_details)
        
    except Exception as e:
        logger.error(f"Erro ao editar RNC {rnc_id}: {e}")
        flash('Erro interno do sistema', 'error')
        return redirect(url_for('dashboard'))

@app.route('/api/rnc/<int:rnc_id>/update', methods=['PUT'])
@login_required
def update_rnc_api(rnc_id):
    """API para atualizar RNC"""
    try:
        rnc_details = rnc_system.get_rnc_details(rnc_id)
        
        if not rnc_details:
            return jsonify({
                'success': False,
                'message': 'RNC não encontrado'
            }), 404
            
        # Verificar acesso
        if rnc_details['main'][9] != current_user.id and current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
            
        data = request.get_json()
        
        if rnc_system.update_rnc(rnc_id, data):
            return jsonify({
                'success': True,
                'message': 'RNC atualizado com sucesso!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao atualizar RNC'
            }), 400
            
    except Exception as e:
        logger.error(f"Erro ao atualizar RNC {rnc_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

# Endpoint para deletar RNC
@app.route('/api/rnc/<int:rnc_id>/delete', methods=['DELETE'])
@login_required
def delete_rnc(rnc_id):
    """Deleta uma RNC definitivamente"""
    try:
        logger.info(f"🗑️ Tentativa de exclusão da RNC {rnc_id} pelo usuário {current_user.email}")
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Verificar se a RNC existe (usando tabela correta 'rncs')
        cur.execute('SELECT id, rnc_number FROM rncs WHERE id = ?', (rnc_id,))
        rnc = cur.fetchone()
        
        if not rnc:
            conn.close()
            logger.warning(f"❌ RNC {rnc_id} não encontrada para exclusão")
            return jsonify({
                'success': False,
                'message': 'RNC não encontrada'
            }), 404
        
        rnc_number = rnc[1]
        
        # Deletar a RNC da tabela correta
        cur.execute('DELETE FROM rncs WHERE id = ?', (rnc_id,))
        rnc_deleted = cur.rowcount
        
        if rnc_deleted == 0:
            conn.rollback()
            conn.close()
            logger.error(f"❌ Falha ao deletar RNC {rnc_id}")
            return jsonify({
                'success': False,
                'message': 'Erro ao deletar RNC'
            }), 500
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ RNC {rnc_number} (ID: {rnc_id}) deletada com sucesso da tabela 'rncs'")
        
        return jsonify({
            'success': True,
            'message': f'RNC {rnc_number} deletada com sucesso',
            'deleted_rnc_id': rnc_id,
            'deleted_rnc_number': rnc_number
        })
        
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
            conn.close()
        logger.error(f"❌ Erro de banco de dados ao deletar RNC {rnc_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro no banco de dados: {str(e)}'
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        logger.error(f"❌ Erro interno ao deletar RNC {rnc_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

# Lista de clientes para uso geral (formulários). Requer usuário autenticado.
@app.route('/api/clients', methods=['GET'])
@login_required
def api_clients_public():
    try:
        ensure_clients_table()
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT name FROM clients ORDER BY name')
        names = [row[0] for row in cur.fetchall()]
        conn.close()
        return jsonify({'success': True, 'clients': names})
    except Exception as e:
        logger.error(f"Erro ao listar clientes: {e}")
        try:
            conn.close()
        except Exception:
            pass
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

# Endpoint de teste para debug de grupos
@app.route('/api/test/groups-debug')
@login_required
def test_groups_debug():
    """Endpoint para debug do sistema de grupos"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Informações do usuário atual
        user_info = {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email,
            'department': current_user.department,
            'role': current_user.role
        }
        
        # RNCs que o usuário deveria ver
        if current_user.role == 'admin':
            # Admin vê todas
            cur.execute("SELECT id, rnc_number, title, department, user_id FROM rncs ORDER BY created_at DESC LIMIT 10")
        else:
            # Usuário normal vê suas próprias + do seu departamento
            cur.execute("""
                SELECT id, rnc_number, title, department, user_id 
                FROM rncs 
                WHERE user_id = ? OR department = ?
                ORDER BY created_at DESC LIMIT 10
            """, (current_user.id, current_user.department))
        
        rncs = []
        for row in cur.fetchall():
            rncs.append({
                'id': row[0],
                'rnc_number': row[1],
                'title': row[2],
                'department': row[3],
                'user_id': row[4]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'user_info': user_info,
            'rncs_visible': rncs,
            'total_visible': len(rncs)
        })
        
    except Exception as e:
        logger.error(f"Erro no debug de grupos: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/charts/data')
def get_charts_data():
    try:
        period = request.args.get('period', '30')
        
        # Conectar ao banco
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Dados para gráfico de status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM rnc_reports 
            WHERE created_at >= date('now', '-{} days')
            GROUP BY status
        """.format(period))
        status_data = cursor.fetchall()
        
        # Dados para gráfico de prioridade
        cursor.execute("""
            SELECT priority, COUNT(*) as count 
            FROM rnc_reports 
            WHERE created_at >= date('now', '-{} days')
            GROUP BY priority
        """.format(period))
        priority_data = cursor.fetchall()
        
        # Dados para gráfico mensal
        cursor.execute("""
            SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count 
            FROM rnc_reports 
            WHERE created_at >= date('now', '-{} days')
            GROUP BY month
            ORDER BY month
        """.format(period))
        monthly_data = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'status': [{'label': row[0], 'count': row[1]} for row in status_data],
                'priority': [{'label': row[0], 'count': row[1]} for row in priority_data],
                'monthly': [{'month': row[0], 'count': row[1]} for row in monthly_data]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/indicadores-dashboard')
@app.route('/indicadores')
@login_required
def indicadores_dashboard():
    """Nova página de indicadores baseada na imagem fornecida"""
    return render_template('indicadores_dashboard.html')

@app.route('/api/indicadores-detalhados')
def get_indicadores_detalhados():
    """API para dados detalhados dos indicadores com formato específico"""
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar se existe a tabela
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rncs'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            conn.close()
            return jsonify(get_fallback_indicadores_data())
        
        # Obter dados do ano atual
        current_year = datetime.now().year
        
        # Total de RNCs
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE strftime('%Y', created_at) = ?", (str(current_year),))
        total_rncs_year = cursor.fetchone()[0]
        
        # Total geral
        cursor.execute("SELECT COUNT(*) FROM rncs")
        total_rncs_all = cursor.fetchone()[0]
        
        # Dados por usuário (simulando departamentos)
        cursor.execute("""
            SELECT u.name, COUNT(r.id) as count 
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            WHERE r.created_at >= date('now', '-12 months')
            GROUP BY u.name, r.user_id
            ORDER BY count DESC
            LIMIT 4
        """)
        user_data = cursor.fetchall()
        
        # Se não há dados de usuários, usar dados por status
        if not user_data:
            user_data = [
                ('ÁREA CORPORATIVO', max(1, total_rncs_year // 4)),
                ('CONTROLE', max(1, total_rncs_year // 3)),
                ('ALAN', max(1, total_rncs_year // 5)),
                ('MARCELO', max(1, total_rncs_year // 5))
            ]
        
        # Dados mensais do ano atual
        cursor.execute("""
            SELECT 
                strftime('%m', created_at) as month,
                COUNT(*) as count
            FROM rncs 
            WHERE strftime('%Y', created_at) = ?
            GROUP BY strftime('%m', created_at)
            ORDER BY month
        """, (str(current_year),))
        monthly_raw = cursor.fetchall()
        
        # Status das RNCs para calcular eficiência
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN status = 'finalizado' THEN 'finalizado'
                    ELSE 'ativo'
                END as status_group,
                COUNT(*) as count
            FROM rncs 
            WHERE strftime('%Y', created_at) = ?
            GROUP BY status_group
        """, (str(current_year),))
        status_data = cursor.fetchall()
        
        conn.close()
        
        # Processar dados mensais
        month_names = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 
                      'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
        
        monthly_data = []
        monthly_counts = {row[0]: row[1] for row in monthly_raw}
        acumulado = 0
        
        for i, month_name in enumerate(month_names):
            month_num = f"{i+1:02d}"
            realizado = monthly_counts.get(month_num, 0)
            acumulado += realizado
            
            monthly_data.append({
                'month': month_name,
                'meta': 15,  # Meta padrão, pode ser configurável
                'realizado': realizado,
                'acumulado': acumulado
            })
        
        # Calcular totais
        total_realizado = sum(d['realizado'] for d in monthly_data)
        total_meta = len(monthly_data) * 15  # 15 por mês
        variacao = total_meta - total_realizado
        
        # Processar departamentos/usuários
        departments = []
        for name, count in user_data:
            if name:  # Filtrar nomes nulos
                departments.append({
                    'name': str(name)[:20],  # Limitar tamanho do nome
                    'realizado': count,
                    'meta': max(count + 5, 10)  # Meta ligeiramente maior que realizado
                })
        
        # Se não há departamentos, usar dados de fallback
        if not departments:
            departments = [
                {'name': 'ÁREA CORPORATIVO', 'realizado': max(1, total_realizado // 4), 'meta': 12},
                {'name': 'CONTROLE', 'realizado': max(1, total_realizado // 3), 'meta': 15},
                {'name': 'ALAN', 'realizado': max(1, total_realizado // 5), 'meta': 8},
                {'name': 'MARCELO', 'realizado': max(1, total_realizado // 5), 'meta': 10}
            ]
        
        # Calcular eficiência baseada em finalizados
        finalizados = sum(count for status, count in status_data if status == 'finalizado')
        efficiency = (finalizados / total_rncs_year * 100) if total_rncs_year > 0 else 0
        
        result = {
            'totals': {
                'meta': float(total_meta),
                'realizado': float(total_realizado),
                'variacao': float(variacao),
                'acumulado': total_realizado,
                'efficiency': round(efficiency, 1),
                'total_all_time': total_rncs_all
            },
            'departments': departments,
            'monthlyData': monthly_data,
            'stats': {
                'finalizados': finalizados,
                'ativos': total_rncs_year - finalizados,
                'efficiency_rate': round(efficiency, 1)
            }
        }
        
        print(f"✅ Indicadores detalhados carregados: {total_rncs_year} RNCs no ano, {total_rncs_all} total")
        return jsonify(result)
        
    except Exception as e:
        print(f"Erro ao carregar indicadores detalhados: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(get_fallback_indicadores_data())

def get_fallback_indicadores_data():
    """Dados de fallback baseados na imagem fornecida"""
    return {
        'totals': {
            'meta': 15.00,
            'realizado': 6.33,
            'variacao': 8.67,
            'acumulado': 15
        },
        'departments': [
            {'name': 'ÁREA CORPORATIVO', 'realizado': 5, 'meta': 12},
            {'name': 'CONTROLE', 'realizado': 13, 'meta': 15},
            {'name': 'ALAN', 'realizado': 6, 'meta': 8},
            {'name': 'MARCELO', 'realizado': 6, 'meta': 10}
        ],
        'monthlyData': [
            {'month': 'JAN', 'meta': 15, 'realizado': 0, 'acumulado': 0},
            {'month': 'FEV', 'meta': 15, 'realizado': 0, 'acumulado': 0},
            {'month': 'MAR', 'meta': 15, 'realizado': 0, 'acumulado': 0},
            {'month': 'ABR', 'meta': 15, 'realizado': 0, 'acumulado': 0},
            {'month': 'MAI', 'meta': 15, 'realizado': 0, 'acumulado': 0},
            {'month': 'JUN', 'meta': 15, 'realizado': 5, 'acumulado': 5},
            {'month': 'JUL', 'meta': 15, 'realizado': 12, 'acumulado': 17},
            {'month': 'AGO', 'meta': 15, 'realizado': 13, 'acumulado': 30},
            {'month': 'SET', 'meta': 15, 'realizado': 0, 'acumulado': 30},
            {'month': 'OUT', 'meta': 15, 'realizado': 0, 'acumulado': 30},
            {'month': 'NOV', 'meta': 15, 'realizado': 0, 'acumulado': 30},
            {'month': 'DEZ', 'meta': 15, 'realizado': 0, 'acumulado': 30}
        ]
    }

@app.route('/api/indicadores')
def get_indicadores_data():
    """Endpoint para dados dos indicadores - versão simplificada para debug"""
    try:
        # Dados de teste fixos para debug
        test_data = {
            'kpis': {
                'total_rncs': 150,
                'total_metas': 200,
                'active_departments': 3,
                'overall_efficiency': 75.0,
                'avg_rncs_per_dept': 50.0
            },
            'departments': [
                {'department': 'PRODUÇÃO', 'meta': 80, 'realizado': 60, 'efficiency': 75.0},
                {'department': 'ENGENHARIA', 'meta': 70, 'realizado': 55, 'efficiency': 78.6},
                {'department': 'QUALIDADE', 'meta': 50, 'realizado': 35, 'efficiency': 70.0}
            ],
            'monthly_trends': [
                {'month': 'JAN', 'total': 15, 'date': '2024-01-01'},
                {'month': 'FEV', 'total': 18, 'date': '2024-02-01'},
                {'month': 'MAR', 'total': 12, 'date': '2024-03-01'},
                {'month': 'ABR', 'total': 20, 'date': '2024-04-01'},
                {'month': 'MAI', 'total': 16, 'date': '2024-05-01'},
                {'month': 'JUN', 'total': 14, 'date': '2024-06-01'},
                {'month': 'JUL', 'total': 19, 'date': '2024-07-01'},
                {'month': 'AGO', 'total': 22, 'date': '2024-08-01'}
            ]
        }
        
        print("📊 Retornando dados de teste para indicadores")
        return jsonify(test_data)
        
    except Exception as e:
        print(f"❌ Erro no endpoint de indicadores: {e}")
        # Fallback simples
        fallback_data = {
            'kpis': {
                'total_rncs': 100,
                'total_metas': 120,
                'active_departments': 2,
                'overall_efficiency': 60.0,
                'avg_rncs_per_dept': 50.0
            },
            'departments': [
                {'department': 'TESTE1', 'meta': 60, 'realizado': 40, 'efficiency': 66.7},
                {'department': 'TESTE2', 'meta': 60, 'realizado': 50, 'efficiency': 83.3}
            ],
            'monthly_trends': [
                {'month': 'JAN', 'total': 10, 'date': '2024-01-01'},
                {'month': 'FEV', 'total': 15, 'date': '2024-02-01'}
            ]
        }
        
        return jsonify(fallback_data)
            
    except Exception as e:
        print(f"Erro ao carregar indicadores: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    # Inicializar banco de dados
    init_database()
    
    # Iniciar backup automático do banco (imediato e a cada 8 minutos)
    try:
        start_backup_scheduler(interval_seconds=480)
    except Exception as e:
        print(f"Falha ao iniciar backup automático: {e}")
    
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
    
    app.run(debug=False, host='0.0.0.0', port=5000)
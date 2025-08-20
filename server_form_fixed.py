#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import sqlite3
import hashlib
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template
from werkzeug.security import check_password_hash, generate_password_hash
import logging
import os
from datetime import datetime
import secrets
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import threading
import time
import gc
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
import queue
import psutil

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configurações de performance para produção
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache estático por 1 ano
app.config['TEMPLATES_AUTO_RELOAD'] = False  # Desabilitar auto-reload em produção
app.config['JSON_SORT_KEYS'] = False  # Manter ordem das chaves JSON

# Configurar SocketIO com otimizações para 200 usuários
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='eventlet',  # Eventlet é melhor para muitos usuários simultâneos
    ping_timeout=120,  # Aumentado para 200 usuários
    ping_interval=30,  # Aumentado para 200 usuários
    max_http_buffer_size=2e8,  # 200MB buffer para 200 usuários
    logger=False,  # Desabilitar logs do SocketIO
    engineio_logger=False,
    max_connections=500,  # Suporte a até 500 conexões simultâneas
    transports=['websocket', 'polling']  # Suporte a múltiplos transportes
)

# Usar caminho absoluto para o banco de dados
DB_PATH = os.path.abspath('ippel_system.db')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Armazenamento temporário de usuários online
online_users = {}

# Pool de conexões para banco de dados - Reduzido para evitar conflitos
db_pool = queue.Queue(maxsize=20)  # Pool reduzido para 20 conexões
executor = ThreadPoolExecutor(max_workers=10)  # Pool reduzido para 10 threads

# Cache de consultas frequentes
query_cache = {}
cache_lock = threading.Lock()

# Métricas de performance
performance_metrics = {
    'requests_per_second': 0,
    'active_connections': 0,
    'db_connections': 0,
    'memory_usage': 0
}

def get_local_ip():
    """Obter IP local da máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def get_available_port(start_port=5001):
    """Encontrar porta disponível"""
    import socket
    port = start_port
    while port < start_port + 100:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            port += 1
    return start_port

def get_db_connection():
    """Obter conexão do pool de banco de dados"""
    try:
        conn = db_pool.get_nowait()
        performance_metrics['db_connections'] += 1
        return conn
    except queue.Empty:
        # Criar nova conexão se pool estiver vazio
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30.0)
            # Aplicar configurações básicas apenas
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            performance_metrics['db_connections'] += 1
            return conn
        except Exception as e:
            logger.error(f"Erro ao criar conexão com banco: {e}")
            # Retornar None em caso de erro
            return None

def return_db_connection(conn):
    """Retornar conexão ao pool"""
    try:
        if conn:
            conn.rollback()  # Rollback para limpar transações
            db_pool.put_nowait(conn)
            performance_metrics['db_connections'] -= 1
    except queue.Full:
        if conn:
            conn.close()
    except Exception as e:
        logger.error(f"Erro ao retornar conexão: {e}")
        if conn:
            conn.close()

def cache_query(key, data, ttl=300):
    """Cache de consultas com TTL de 5 minutos"""
    with cache_lock:
        if len(query_cache) > 1000:
            oldest_key = min(query_cache.keys(), key=lambda k: query_cache[k]['timestamp'])
            del query_cache[oldest_key]
        
        query_cache[key] = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl
        }

def get_cached_query(key):
    """Obter dados do cache"""
    with cache_lock:
        if key in query_cache:
            cache_entry = query_cache[key]
            if time.time() - cache_entry['timestamp'] < cache_entry['ttl']:
                return cache_entry['data']
            else:
                del query_cache[key]
    return None

def clear_expired_cache():
    """Limpar cache expirado"""
    with cache_lock:
        current_time = time.time()
        expired_keys = [
            key for key, entry in query_cache.items()
            if current_time - entry['timestamp'] > entry['ttl']
        ]
        for key in expired_keys:
            del query_cache[key]

def performance_monitor():
    """Monitor de performance em background"""
    while True:
        try:
            performance_metrics['memory_usage'] = psutil.Process().memory_info().rss / 1024 / 1024
            performance_metrics['active_connections'] = len(online_users)
            
            clear_expired_cache()
            
            if performance_metrics['memory_usage'] > 1000:
                gc.collect()
                logger.info(f"Garbage collection executado. Memória: {performance_metrics['memory_usage']:.1f}MB")
            
            if int(time.time()) % 300 == 0:
                logger.info(f"Performance - Usuários: {len(online_users)}, Memória: {performance_metrics['memory_usage']:.1f}MB, Conexões DB: {performance_metrics['db_connections']}")
            
            time.sleep(15)
        except Exception as e:
            logger.error(f"Erro no monitor de performance: {e}")
            time.sleep(30)

def init_database():
    """Inicializar banco de dados com tratamento de erro melhorado"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        # Aplicar configurações básicas
        try:
            cursor.execute('PRAGMA synchronous=NORMAL')
            cursor.execute('PRAGMA cache_size=10000')
            cursor.execute('PRAGMA temp_store=MEMORY')
        except sqlite3.OperationalError as e:
            print(f"⚠️ Aviso: Algumas otimizações do SQLite não puderam ser aplicadas: {e}")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        return
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            permissions TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Tabela de RNCs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rncs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rnc_number TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            equipment TEXT,
            client TEXT,
            priority TEXT DEFAULT 'Média',
            status TEXT DEFAULT 'Pendente',
            user_id INTEGER,
            assigned_user_id INTEGER,
            is_deleted BOOLEAN DEFAULT 0,
            deleted_at TIMESTAMP,
            finalized_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (assigned_user_id) REFERENCES users (id)
        )
    ''')
    
    # Verificar se existe usuário admin
    cursor.execute('SELECT * FROM users WHERE role = "admin" LIMIT 1')
    admin_exists = cursor.fetchone()
    
    if not admin_exists:
        # Criar usuário admin padrão
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, department, role, permissions)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Administrador', 'admin@ippel.com.br', admin_password, 'TI', 'admin', '["all"]'))
        
        print("✅ Usuário admin criado:")
        print("   Email: admin@ippel.com.br")
        print("   Senha: admin123")
        print("   Permissões: Todas")
        
        # Criar usuários de teste
        test_users = [
            ('Elvio Silva', 'elvio@ippel.com.br', 'elvio123', 'Produção', 'user', '["create_rnc"]'),
            ('Maria Santos', 'maria@ippel.com.br', 'maria123', 'Qualidade', 'user', '["create_rnc"]'),
            ('João Costa', 'joao@ippel.com.br', 'joao123', 'Manutenção', 'user', '["create_rnc"]'),
            ('Ana Oliveira', 'ana@ippel.com.br', 'ana123', 'Logística', 'user', '["create_rnc"]')
        ]
        
        for user_data in test_users:
            try:
                user_password = generate_password_hash(user_data[2])
                cursor.execute('''
                    INSERT INTO users (name, email, password_hash, department, role, permissions)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_data[0], user_data[1], user_password, user_data[3], user_data[4], user_data[5]))
                print(f"✅ Usuário criado: {user_data[0]} ({user_data[1]})")
            except sqlite3.IntegrityError:
                pass
    
    conn.commit()
    conn.close()

def get_user_by_email(email):
    """Buscar usuário por email"""
    cache_key = f"user_email_{email}"
    cached_result = get_cached_query(cache_key)
    if cached_result:
        return cached_result
    
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = 1', (email,))
        user = cursor.fetchone()
        cache_query(cache_key, user, ttl=600)
        return user
    finally:
        if conn:
            return_db_connection(conn)

def get_user_by_id(user_id):
    """Buscar usuário por ID"""
    cache_key = f"user_id_{user_id}"
    cached_result = get_cached_query(cache_key)
    if cached_result:
        return cached_result
    
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ? AND is_active = 1', (user_id,))
        user = cursor.fetchone()
        cache_query(cache_key, user, ttl=600)
        return user
    finally:
        if conn:
            return_db_connection(conn)

def has_permission(user_id, permission):
    """Verificar se usuário tem permissão específica"""
    user = get_user_by_id(user_id)
    if not user:
        return False
    
    if user[5] == 'admin':
        return True
    
    import json
    try:
        permissions = json.loads(user[6] or '[]')
        return permission in permissions or 'all' in permissions
    except:
        return False

@app.route('/')
def index():
    """Página principal com login"""
    if 'user_id' in session:
        return redirect('/dashboard')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard interativo para usuários logados"""
    if 'user_id' not in session:
        return redirect('/')
    return render_template('dashboard_improved.html')

@app.route('/form')
def form():
    """Formulário RNC (apenas para usuários logados)"""
    if 'user_id' not in session:
        return redirect('/')
    
    return send_from_directory('.', 'index.html')

@app.route('/api/login', methods=['POST'])
def login():
    """API de login"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user_data = get_user_by_email(email)
        
        if user_data and check_password_hash(user_data[3], password):
            session['user_id'] = user_data[0]
            session['user_name'] = user_data[1]
            session['user_email'] = user_data[2]
            session['user_department'] = user_data[4]
            session['user_role'] = user_data[5]
            
            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso!',
                'redirect': '/dashboard',
                'user': {
                    'name': user_data[1],
                    'email': user_data[2],
                    'department': user_data[4]
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Email ou senha incorretos'
            }), 401
            
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do sistema'
        }), 500

@app.route('/api/logout')
def logout():
    """API de logout"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logout realizado com sucesso!'
    })

@app.route('/api/user/info')
def get_user_info():
    """API para obter informações do usuário logado"""
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': 'Usuário não autenticado'
        }), 401
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Erro de conexão com banco de dados'
            }), 500
        
        cursor = conn.cursor()
        cursor.execute('SELECT permissions FROM users WHERE id = ?', (session['user_id'],))
        user_data = cursor.fetchone()
        
        permissions = []
        if user_data and user_data[0]:
            permissions = user_data[0].split(',')
        
        user_info = {
            'id': session['user_id'],
            'name': session['user_name'],
            'email': session['user_email'],
            'department': session['user_department'],
            'role': session['user_role'],
            'permissions': permissions
        }
        
        return jsonify({
            'success': True,
            'user': user_info
        })
    except Exception as e:
        logger.error(f"Erro ao buscar informações do usuário: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar informações do usuário'
        }), 500
    finally:
        if 'conn' in locals():
            return_db_connection(conn)

@app.route('/api/rnc/create', methods=['POST'])
def create_rnc():
    """API para criar RNC"""
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': 'Usuário não autenticado'
        }), 401
    
    try:
        data = request.get_json()
        
        # Verificar se há pelo menos uma assinatura
        assinaturas = [
            data.get('assinatura1', ''),
            data.get('assinatura2', ''),
            data.get('assinatura3', '')
        ]
        
        if not any(assinatura and assinatura != 'NOME' for assinatura in assinaturas):
            return jsonify({
                'success': False,
                'message': 'É obrigatório preencher pelo menos uma assinatura!'
            }), 400
        
        # Gerar número único do RNC
        import datetime
        now = datetime.datetime.now()
        rnc_number = f"RNC-{now.year}-{now.month:02d}-{now.day:02d}-{now.hour:02d}{now.minute:02d}{now.second:02d}"
        
        # Salvar RNC no banco local
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Erro de conexão com banco de dados'
            }), 500
        
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rncs (rnc_number, title, description, equipment, client, priority, status, user_id, assigned_user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rnc_number,
            data.get('title', 'RNC sem título'),
            data.get('description', ''),
            data.get('equipment', ''),
            data.get('client', ''),
            data.get('priority', 'Média'),
            'Pendente',
            session['user_id'],
            data.get('assigned_user_id')
        ))
        
        rnc_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'RNC criado com sucesso!',
            'rnc_id': rnc_id,
            'rnc_number': rnc_number
        })
        
    except Exception as e:
        logger.error(f"Erro ao criar RNC: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500
    finally:
        if 'conn' in locals():
            return_db_connection(conn)

@app.route('/api/rnc/list')
def list_rncs():
    """API para listar RNCs"""
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': 'Usuário não autenticado'
        }), 401
    
    conn = None
    try:
        tab = request.args.get('tab', 'active')
        user_id = session['user_id']
        
        cache_key = f"rncs_list_{user_id}_{tab}"
        cached_result = get_cached_query(cache_key)
        if cached_result:
            return jsonify(cached_result)
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Erro de conexão com banco de dados'
            }), 500
        
        cursor = conn.cursor()
        
        base_query = '''
                SELECT r.*, u.name as user_name, au.name as assigned_user_name
                FROM rncs r 
                LEFT JOIN users u ON r.user_id = u.id 
                LEFT JOIN users au ON r.assigned_user_id = au.id
        '''
        
        if tab == 'active':
            if has_permission(session['user_id'], 'view_all_rncs'):
                cursor.execute(base_query + '''
                    WHERE r.is_deleted = 0 AND r.status != 'Finalizado'
                    ORDER BY r.created_at DESC
                ''')
            else:
                cursor.execute(base_query + '''
                    WHERE r.is_deleted = 0 AND r.status != 'Finalizado' AND r.assigned_user_id = ?
                    ORDER BY r.created_at DESC
                ''', (session['user_id'],))
                
        elif tab == 'finalized':
            if has_permission(session['user_id'], 'view_all_rncs'):
                cursor.execute(base_query + '''
                    WHERE r.is_deleted = 0 AND r.status = 'Finalizado'
                    ORDER BY r.finalized_at DESC
                ''')
            else:
                cursor.execute(base_query + '''
                    WHERE r.is_deleted = 0 AND r.status = 'Finalizado' AND r.assigned_user_id = ?
                    ORDER BY r.finalized_at DESC
                ''', (session['user_id'],))
                
        elif tab == 'deleted':
            if has_permission(session['user_id'], 'delete_rncs'):
                cursor.execute(base_query + '''
                    WHERE r.is_deleted = 1
                    ORDER BY r.deleted_at DESC
                ''')
            else:
                cursor.execute(base_query + '''
                    WHERE r.is_deleted = 1 AND r.user_id = ?
                    ORDER BY r.deleted_at DESC
                ''', (session['user_id'],))
        
        rncs = cursor.fetchall()
        
        formatted_rncs = []
        current_user_id = session['user_id']
        
        for rnc in rncs:
            days_remaining = None
            if tab == 'deleted' and rnc[12]:
                from datetime import datetime
                deleted_date = datetime.strptime(rnc[12], '%Y-%m-%d %H:%M:%S')
                days_elapsed = (datetime.now() - deleted_date).days
                days_remaining = max(0, 30 - days_elapsed)
            
            formatted_rncs.append({
                'id': rnc[0],
                'rnc_number': rnc[1],
                'title': rnc[2],
                'description': rnc[3],
                'equipment': rnc[4],
                'client': rnc[5],
                'priority': rnc[6],
                'status': rnc[7],
                'user_id': rnc[8],
                'assigned_user_id': rnc[9],
                'is_deleted': rnc[10],
                'deleted_at': rnc[11],
                'finalized_at': rnc[12],
                'created_at': rnc[13],
                'updated_at': rnc[14],
                'user_name': rnc[15],
                'assigned_user_name': rnc[16],
                'is_creator': (current_user_id == rnc[8]),
                'days_remaining': days_remaining
            })
        
        result = {
            'success': True,
            'rncs': formatted_rncs,
            'tab': tab
        }
        
        cache_query(cache_key, result, ttl=120)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro ao listar RNCs: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500
    finally:
        if conn:
            return_db_connection(conn)

@app.route('/<path:filename>')
def serve_static(filename):
    """Servir arquivos estáticos"""
    return send_from_directory('.', filename)

if __name__ == '__main__':
    # Inicializar banco de dados
    init_database()
    
    # Inicializar pool de conexões reduzido
    print("🔧 Inicializando pool de conexões...")
    for i in range(5):  # Apenas 5 conexões iniciais
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30.0)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            db_pool.put(conn)
            print(f"   ✅ Conexão {i+1} criada")
        except Exception as e:
            print(f"   ⚠️ Erro ao criar conexão {i+1}: {e}")
    
    # Iniciar monitor de performance em background
    performance_thread = threading.Thread(target=performance_monitor, daemon=True)
    performance_thread.start()
    
    # Obter IP e porta
    local_ip = get_local_ip()
    port = get_available_port(5001)
    
    if port is None:
        print("❌ Erro: Não foi possível encontrar uma porta disponível")
        exit(1)
    
    print("🚀 Iniciando Servidor do Formulário RNC (Versão Corrigida)")
    print("=" * 60)
    print(f"📋 Login/Formulário: http://{local_ip}:{port}")
    print(f"🔧 Painel Admin: http://{local_ip}:5000")
    print("=" * 60)
    print("✅ Usuário Admin criado automaticamente:")
    print("   Email: admin@ippel.com.br")
    print("   Senha: admin123")
    print("=" * 60)
    print("⚡ Otimizações de Performance:")
    print("   - Pool de conexões: 5 conexões iniciais")
    print("   - Cache de consultas: Ativo")
    print("   - Monitor de performance: Ativo")
    print("   - SQLite WAL mode: Ativo")
    print("=" * 60)
    
    try:
        socketio.run(app, host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Servidor do formulário encerrado")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}") 
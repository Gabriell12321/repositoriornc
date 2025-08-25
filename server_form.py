 #!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import hashlib
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template, abort, make_response
import socket

# Importações opcionais com fallback
try:
    from flask_compress import Compress
    HAS_COMPRESS = True
except ImportError:
    Compress = None
    HAS_COMPRESS = False
    print("⚠️ Flask-Compress não instalado - compressão desabilitada")

from werkzeug.middleware.proxy_fix import ProxyFix

# Flask-Limiter desabilitado para evitar problemas de configuração
HAS_LIMITER = False
def get_remote_address():
    return request.remote_addr if request else '127.0.0.1'

try:
    from flask_talisman import Talisman
    HAS_TALISMAN = True
except ImportError:
    Talisman = None
    HAS_TALISMAN = False
    print("⚠️ Flask-Talisman não instalado - headers de segurança desabilitados")

import re
import secrets
import queue
import time
import gc
import json
import threading
import tracemalloc
import datetime
import logging
import os
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from routes.api import api as api_bp

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room  # type: ignore
    HAS_SOCKETIO = True
except ImportError:  # Fallback dummy para executar sem dependência
    HAS_SOCKETIO = False
    class _DummySocketIO:
        def __init__(self, app, *args, **kwargs):
            self.app = app
        def on(self, *args, **kwargs):
            def _decorator(f):
                return f
            return _decorator
        def emit(self, *args, **kwargs):
            pass
        def run(self, app, host='0.0.0.0', port=5000, **kwargs):
            print("⚠️ flask_socketio não instalado - usando Flask padrão (sem WebSocket)")
            app.run(host=host, port=port, debug=kwargs.get('debug', False))
    def emit(*args, **kwargs):
        pass
    def join_room(*args, **kwargs):
        pass
    def leave_room(*args, **kwargs):
        pass
    SocketIO = _DummySocketIO  # type: ignore

from functools import wraps
from concurrent.futures import ThreadPoolExecutor

# psutil é opcional; se der conflito de versão, seguimos sem ele
try:
    import psutil  # type: ignore
    HAS_PSUTIL = True
except Exception:
    psutil = None  # type: ignore
    HAS_PSUTIL = False

try:
    tracemalloc.start()
except Exception:
    pass

app = Flask(__name__)
if HAS_COMPRESS and Compress is not None:
    Compress(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Secret key estável: lê de variável de ambiente ou de arquivo local persistente
_secret_from_env = os.environ.get('IPPEL_SECRET_KEY')
if _secret_from_env:
    app.secret_key = _secret_from_env
else:
    _secret_file = os.path.join(os.path.dirname(__file__), 'ippel_secret.key')
    try:
        if os.path.exists(_secret_file):
            with open(_secret_file, 'r', encoding='utf-8') as f:
                app.secret_key = f.read().strip()
        else:
            _new_secret = secrets.token_hex(32)
            with open(_secret_file, 'w', encoding='utf-8') as f:
                f.write(_new_secret)
            app.secret_key = _new_secret
    except Exception:
        # Fallback (não persiste): ainda assim não quebra
        app.secret_key = secrets.token_hex(32)

# Configurações de performance para produção
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache estático por 1 ano
app.config['TEMPLATES_AUTO_RELOAD'] = False  # Desabilitar auto-reload em produção
app.config['JSON_SORT_KEYS'] = False  # Manter ordem das chaves JSON
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # Respostas JSON compactas
app.config['COMPRESS_ALGORITHM'] = 'gzip'
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/plain',
    'application/javascript', 'application/json',
    'application/octet-stream'
]
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # HTTP em rede local
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_NAME'] = 'ippel_session'
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 8  # 8 horas
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB por requisição

# Registrar blueprints
app.register_blueprint(api_bp)

# Configurar rate limiter (desabilitado para evitar problemas)
class _LimiterDummy:
    def limit(self, *args, **kwargs):
        def _noop_decorator(*args, **kwargs):
            def _wrapper(f):
                return f
            return _wrapper
        return _noop_decorator

limiter = _LimiterDummy()

@app.route('/static/<path:filename>')
def static_files(filename):
    try:
        return send_from_directory('static', filename)
    except Exception:
        return abort(404)

@app.route('/logo.png')
def root_logo():
    try:
        return send_from_directory('static', 'logo.png')
    except Exception:
        return abort(404)

# Políticas de cache por tipo de conteúdo e rota
@app.after_request
def add_cache_headers(response):
    try:
        path_lower = request.path.lower()
        mime = (response.mimetype or '').lower()

        # Assets estáticos: 1 ano
        if path_lower.startswith('/static/') or path_lower.endswith(('.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg')):
            response.cache_control.public = True
            response.cache_control.max_age = 31536000
            response.headers['Expires'] = 'Thu, 31 Dec 2099 23:59:59 GMT'

        # HTML dinâmico: não cachear
        elif 'text/html' in mime:
            response.cache_control.no_cache = True
            response.cache_control.no_store = True
            response.cache_control.must_revalidate = True

        # APIs JSON: para endpoints pesados, permitir cache curto no cliente
        elif 'application/json' in mime or path_lower.startswith('/api/'):
            # Lista de endpoints que podem ser cacheados brevemente
            cacheable = (
                path_lower.startswith('/api/rnc/list') or
                path_lower.startswith('/api/charts/data') or
                path_lower.startswith('/api/notifications/unread')
            )
            if cacheable:
                response.cache_control.public = True
                response.cache_control.max_age = 15  # 15s para sensação de rapidez
            else:
                response.cache_control.no_cache = True
                response.cache_control.no_store = True
                response.cache_control.must_revalidate = True

    except Exception:
        pass
    return response

# Forçar modo 'threading' para estabilidade no Windows/Python 3.13
# (evita erros do eventlet como WinError 10053 ao encerrar websockets)
_async_mode = 'threading'

# Se HTTPS estiver habilitado via ambiente e não houver CERT/KEY definidos,
# forçar 'threading' para permitir ssl_context='adhoc' (eventlet não suporta adhoc).
# OBS: Permitir FORÇAR HTTP via variável IPPEL_FORCE_HTTP (padrão ativo) para evitar habilitar HTTPS por engano.
try:
    _force_http_env = os.environ.get('IPPEL_FORCE_HTTP', '1').strip() in ('1', 'true', 'TRUE', 'yes', 'on')
    _enable_https_env = os.environ.get('IPPEL_ENABLE_HTTPS', '').strip() in ('1', 'true', 'TRUE', 'yes', 'on')
    if _force_http_env:
        _enable_https_env = False
    _has_cert = bool(os.environ.get('SSL_CERTFILE') and os.environ.get('SSL_KEYFILE'))
    if _enable_https_env and not _has_cert:
        _async_mode = 'threading'
except Exception:
    pass

# Configurar SocketIO com fallback seguro (sem exigir eventlet)
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode=_async_mode,
    ping_timeout=120,
    ping_interval=30,
    max_http_buffer_size=200000000,
    logger=False,
    engineio_logger=False,
    transports=['websocket', 'polling']
)

DB_PATH = 'ippel_system.db'
# Diretório de backup no mesmo local do projeto
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backup')

def ensure_backup_dir_exists() -> None:
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
    except Exception as e:
        try:
            logger.error(f"Erro ao criar diretório de backup '{BACKUP_DIR}': {e}")
        except Exception:
            print(f"Erro ao criar diretório de backup '{BACKUP_DIR}': {e}")

def backup_database_now() -> None:
    """Cria um backup consistente do SQLite usando a API nativa de backup."""
    ensure_backup_dir_exists()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest_path = os.path.join(BACKUP_DIR, f"ippel_system_{timestamp}.db")
    try:
        # Usar API de backup do SQLite para snapshot consistente
        src = sqlite3.connect(DB_PATH, timeout=30.0)
        dst = sqlite3.connect(dest_path, timeout=30.0)
        with dst:
            src.backup(dst)
        src.close()
        dst.close()
        try:
            logger.info(f"✅ Backup criado: {dest_path}")
        except Exception:
            print(f"✅ Backup criado: {dest_path}")
    except Exception as e:
        try:
            logger.error(f"⚠️ Erro ao criar backup: {e}")
        except Exception:
            print(f"⚠️ Erro ao criar backup: {e}")

def start_backup_scheduler(interval_seconds: int = 43200) -> None:
    """Inicia uma thread em background para fazer backup periódico.
    Faz um backup IMEDIATO ao iniciar e depois repete a cada 'interval_seconds'
    (padrão: 12 horas).
    """
    def _worker():
        # Backup imediato ao iniciar o agendador
        try:
            backup_database_now()
        except Exception as e:
            try:
                logger.error(f"Erro no backup inicial: {e}")
            except Exception:
                print(f"Erro no backup inicial: {e}")
        # Periódico
        while True:
            try:
                time.sleep(interval_seconds)
                backup_database_now()
            except Exception as e:
                try:
                    logger.error(f"Erro no agendador de backup: {e}")
                except Exception:
                    print(f"Erro no agendador de backup: {e}")
    t = threading.Thread(target=_worker, name='BackupScheduler', daemon=True)
    t.start()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Armazenamento temporário de usuários online
online_users = {}

# Pool de conexões para banco de dados - Otimizado para i5-7500 + 16GB RAM
db_pool = queue.Queue(maxsize=150)  # Pool de 150 conexões para 200+ usuários
executor = ThreadPoolExecutor(max_workers=75)  # Pool de 75 threads para alta concorrência

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
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.execute('PRAGMA journal_mode=WAL')  # Modo WAL para melhor performance
        conn.execute('PRAGMA synchronous=NORMAL')  # Sincronização mais rápida
        conn.execute('PRAGMA cache_size=10000')  # Cache maior
        conn.execute('PRAGMA temp_store=MEMORY')  # Temp tables em memória
        conn.execute('PRAGMA mmap_size=268435456')  # 256MB mmap
        performance_metrics['db_connections'] += 1
        return conn

def return_db_connection(conn):
    """Retornar conexão ao pool"""
    try:
        if conn:
            conn.rollback()  # Rollback para limpar transações
            db_pool.put_nowait(conn)
            performance_metrics['db_connections'] -= 1
    except queue.Full:
        conn.close()

def cache_query(key, data, ttl=300):
    """Cache de consultas com TTL de 5 minutos - Otimizado para 200 usuários"""
    with cache_lock:
        # Limitar cache a 1000 entradas para evitar uso excessivo de memória
        if len(query_cache) > 1000:
            # Remover entradas mais antigas
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

def clear_rnc_cache(user_id=None):
    """Limpar cache de RNCs para um usuário específico ou todos"""
    with cache_lock:
        if user_id:
            # Limpar cache específico do usuário
            keys_to_remove = [
                key for key in query_cache.keys()
                if key.startswith(f"rncs_list_{user_id}_")
            ]
        else:
            # Limpar todo o cache de RNCs
            keys_to_remove = [
                key for key in query_cache.keys()
                if key.startswith("rncs_list_")
            ]
        
        for key in keys_to_remove:
            del query_cache[key]

def get_rnc_data_safe(rnc_id):
    """Buscar dados do RNC de forma segura"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)
        cursor = conn.cursor()
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA busy_timeout=10000')
        
        # Primeiro, verificar se o RNC existe
        cursor.execute('SELECT id FROM rncs WHERE id = ?', (rnc_id,))
        rnc_exists = cursor.fetchone()
        
        if not rnc_exists:
            conn.close()
            return None, "RNC não encontrado"
        
        # Buscar RNC com informações do usuário
        cursor.execute('''
            SELECT r.*, u.name as user_name, au.name as assigned_user_name
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            LEFT JOIN users au ON r.assigned_user_id = au.id
            WHERE r.id = ?
        ''', (rnc_id,))
        
        rnc_data = cursor.fetchone()
        conn.close()
        
        if not rnc_data:
            return None, "RNC não encontrado na consulta completa"
        
        # Verificar se rnc_data é uma tupla/lista
        if not isinstance(rnc_data, (tuple, list)):
            return None, f"Dados inválidos: {type(rnc_data)} - {rnc_data}"
        
        return rnc_data, None
        
    except Exception as e:
        return None, f"Erro ao buscar RNC: {str(e)}"

def performance_monitor():
    """Monitor de performance em background otimizado para 200 usuários"""
    while True:
        try:
            # Atualizar métricas
            if HAS_PSUTIL and psutil is not None:
                performance_metrics['memory_usage'] = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            else:
                try:
                    current, _ = tracemalloc.get_traced_memory()
                    performance_metrics['memory_usage'] = current / 1024 / 1024
                except Exception:
                    performance_metrics['memory_usage'] = 0
            performance_metrics['active_connections'] = len(online_users)
            
            # Limpar cache expirado
            clear_expired_cache()
            
            # Garbage collection mais agressivo para 200 usuários
            if performance_metrics['memory_usage'] > 1000:  # Se usar mais de 1GB
                gc.collect()
                logger.info(f"Garbage collection executado. Memória: {performance_metrics['memory_usage']:.1f}MB")
            
            # Log de performance a cada 5 minutos
            if int(time.time()) % 300 == 0:  # A cada 5 minutos
                logger.info(f"Performance - Usuários: {len(online_users)}, Memória: {performance_metrics['memory_usage']:.1f}MB, Conexões DB: {performance_metrics['db_connections']}")
            
            time.sleep(15)  # Verificar a cada 15 segundos para 200 usuários
        except Exception as e:
            logger.error(f"Erro no monitor de performance: {e}")
            time.sleep(30)
def init_database():
    """Inicializar banco de dados com tabelas de usuários e permissões"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Otimizações do SQLite para melhor performance
    cursor.execute('PRAGMA journal_mode=WAL')
    cursor.execute('PRAGMA synchronous=NORMAL')
    cursor.execute('PRAGMA cache_size=10000')
    cursor.execute('PRAGMA temp_store=MEMORY')
    cursor.execute('PRAGMA mmap_size=268435456')
    cursor.execute('PRAGMA optimize')
    
    # Tabela de grupos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de permissões de grupos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            permission_name TEXT NOT NULL,
            permission_value BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups (id),
            UNIQUE(group_id, permission_name)
        )
    ''')
    
    # Inserir grupos padrão se não existirem
    cursor.execute('SELECT COUNT(*) FROM groups')
    if cursor.fetchone()[0] == 0:
        default_groups = [
            ('Produção', 'Departamento de Produção'),
            ('Engenharia', 'Departamento de Engenharia'),
            ('Terceiros', 'Departamento de Terceiros'),
            ('Compras', 'Departamento de Compras'),
            ('Comercial', 'Departamento Comercial'),
            ('PCP', 'Planejamento e Controle de Produção'),
            ('Expedição', 'Departamento de Expedição'),
            ('Qualidade', 'Departamento de Qualidade')
        ]
        cursor.executemany('INSERT INTO groups (name, description) VALUES (?, ?)', default_groups)
        
        # Obter IDs dos grupos criados
        cursor.execute('SELECT id, name FROM groups')
        groups = cursor.fetchall()
        
        # Definir permissões para cada grupo
        group_permissions = {
            'Produção': [
                'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'delete_own_rnc',
                'view_all_rncs', 'finalize_rnc', 'assign_rnc', 'chat_access'
            ],
            'Engenharia': [
                'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'delete_own_rnc',
                'view_all_rncs', 'edit_all_rncs', 'finalize_rnc', 'assign_rnc',
                'chat_access', 'technical_analysis'
            ],
            'Terceiros': [
                'view_own_rnc', 'chat_access', 'limited_access'
            ],
            'Compras': [
                'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'view_all_rncs',
                'chat_access', 'purchase_analysis'
            ],
            'Comercial': [
                'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'view_all_rncs',
                'chat_access', 'commercial_analysis'
            ],
            'PCP': [
                'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'view_all_rncs',
                'edit_all_rncs', 'finalize_rnc', 'assign_rnc', 'chat_access',
                'planning_control'
            ],
            'Expedição': [
                'view_own_rnc', 'view_all_rncs', 'chat_access', 'shipping_access'
            ],
            'Qualidade': [
                'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'delete_own_rnc',
                'view_all_rncs', 'edit_all_rncs', 'finalize_rnc', 'assign_rnc',
                'chat_access', 'quality_control', 'admin_access', 'view_levantamento_14_15'
            ]
        }
        
        # Inserir permissões para cada grupo
        for group_id, group_name in groups:
            if group_name in group_permissions:
                permissions = group_permissions[group_name]
                for permission in permissions:
                    cursor.execute('''
                        INSERT INTO group_permissions (group_id, permission_name, permission_value)
                        VALUES (?, ?, ?)
                    ''', (group_id, permission, 1))
    
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
            group_id INTEGER,
            avatar_key TEXT,
            avatar_prefs TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (group_id) REFERENCES groups (id)
        )
    ''')
    
    # Adicionar coluna group_id se não existir
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN group_id INTEGER')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass

    # Adicionar coluna avatar_key se não existir
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN avatar_key TEXT')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass

    # Adicionar coluna avatar_prefs se não existir
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN avatar_prefs TEXT')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
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
    
    # Adicionar coluna assigned_user_id se não existir
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN assigned_user_id INTEGER')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    # Adicionar colunas para sistema de lixeira se não existirem
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN is_deleted BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN deleted_at TIMESTAMP')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN finalized_at TIMESTAMP')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    # Adicionar coluna de preço se não existir
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN price REAL DEFAULT 0')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    # Adicionar colunas para disposição e inspeção
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN disposition_usar BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN disposition_retrabalhar BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN disposition_rejeitar BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN disposition_sucata BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass

    # Tabela de compartilhamento de RNCs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rnc_shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rnc_id INTEGER NOT NULL,
            shared_by_user_id INTEGER NOT NULL,
            shared_with_user_id INTEGER NOT NULL,
            permission_level TEXT DEFAULT 'view', -- 'view', 'edit', 'comment'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rnc_id) REFERENCES rncs (id) ON DELETE CASCADE,
            FOREIGN KEY (shared_by_user_id) REFERENCES users (id),
            FOREIGN KEY (shared_with_user_id) REFERENCES users (id),
            UNIQUE(rnc_id, shared_with_user_id)
        )
    ''')
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN disposition_devolver_estoque BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN disposition_devolver_fornecedor BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN inspection_aprovado BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN inspection_reprovado BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN inspection_ver_rnc TEXT')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN signature_inspection_date TEXT')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN signature_engineering_date TEXT')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN signature_inspection2_date TEXT')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN signature_inspection_name TEXT')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN signature_engineering_name TEXT')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    try:
        cursor.execute('ALTER TABLE rncs ADD COLUMN signature_inspection2_name TEXT')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
    
    # Tabela de mensagens do chat
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rnc_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            message_type TEXT DEFAULT 'text',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rnc_id) REFERENCES rncs (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Tabela de notificações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            rnc_id INTEGER,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (rnc_id) REFERENCES rncs (id)
        )
    ''')
    
    # Tabela de mensagens privadas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS private_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            recipient_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            message_type TEXT DEFAULT 'text',
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (recipient_id) REFERENCES users (id)
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
                # Usuário já existe
                pass
    
    conn.commit()
    conn.close()

    # Garantir colunas extras nos RNCs para modo responder/visualização completa
    ensure_rnc_extra_columns()

def ensure_rnc_extra_columns():
    """Garante que a tabela rncs possua colunas extras usadas no modo Responder/Visualização.

    Campos:
      - instruction_retrabalho TEXT
      - cause_rnc TEXT
      - action_rnc TEXT
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info(rncs)')
        cols = [row[1] for row in cursor.fetchall()]
        additions = []
        if 'instruction_retrabalho' not in cols:
            additions.append("ALTER TABLE rncs ADD COLUMN instruction_retrabalho TEXT")
        if 'cause_rnc' not in cols:
            additions.append("ALTER TABLE rncs ADD COLUMN cause_rnc TEXT")
        if 'action_rnc' not in cols:
            additions.append("ALTER TABLE rncs ADD COLUMN action_rnc TEXT")
        for sql in additions:
            try:
                cursor.execute(sql)
            except Exception:
                pass
        conn.commit()
        conn.close()
    except Exception as e:
        try:
            logger.error(f"Erro ao garantir colunas extras dos RNCs: {e}")
        except Exception:
            pass

def get_user_by_email(email):
    """Buscar usuário por email"""
    cache_key = f"user_email_{email}"
    cached_result = get_cached_query(cache_key)
    if cached_result:
        return cached_result
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = 1', (email,))
        user = cursor.fetchone()
        cache_query(cache_key, user, ttl=600)  # Cache por 10 minutos
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
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ? AND is_active = 1', (user_id,))
        user = cursor.fetchone()
        cache_query(cache_key, user, ttl=600)  # Cache por 10 minutos
        return user
    finally:
        if conn:
            return_db_connection(conn)

def has_permission(user_id, permission):
    """Verificar se usuário tem determinada permissão baseada no grupo"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Primeiro, verificar se o usuário é admin (tem todas as permissões)
        cursor.execute('''
            SELECT role FROM users WHERE id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        
        if result and result[0] == 'admin':
            conn.close()
            return True
        
        # Verificar permissão baseada no grupo
        cursor.execute('''
            SELECT gp.permission_value
            FROM group_permissions gp
            JOIN users u ON u.group_id = gp.group_id
            WHERE u.id = ? AND gp.permission_name = ?
        ''', (user_id, permission))
        
        result = cursor.fetchone()
        conn.close()
        
        # Se a permissão foi encontrada e está ativa
        if result and result[0] == 1:
            return True
        
        # Fallback para sistema de departamento (compatibilidade)
        return has_department_permission(user_id, permission)
        
    except Exception as e:
        logger.error(f"Erro ao verificar permissão: {e}")
        return False

def get_user_department(user_id):
    """Obter o departamento do usuário"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT department FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Erro ao obter departamento do usuário: {e}")
        return None

def has_department_permission(user_id, action):
    """
    Verificar permissões baseadas no departamento do usuário
    
    Regras:
    - Engenharia: acesso somente às RNCs criadas
    - Administração: acesso a tudo
    - Produção: acesso somente às RNCs criadas
    - Qualidade: acesso aos gráficos, relatórios, RNCs finalizadas e criadas
    - TI: acesso a tudo
    """
    try:
        department = get_user_department(user_id)
        if not department:
            return False
        
        department = department.lower()
        
        # Administração e TI têm acesso total
        if department in ['administração', 'administracao', 'ti']:
            return True
        
        # Verificar permissões específicas por ação
        if action == 'view_own_rncs':
            # Todos os departamentos podem ver RNCs próprias
            return True
        
        elif action == 'view_all_rncs':
            # Apenas Administração, TI e Qualidade
            return department in ['administração', 'administracao', 'ti', 'qualidade']
        
        elif action == 'view_finalized_rncs':
            # Administração, TI e Qualidade
            return department in ['administração', 'administracao', 'ti', 'qualidade']
        
        elif action == 'view_charts':
            # Administração, TI e Qualidade
            return department in ['administração', 'administracao', 'ti', 'qualidade']
        
        elif action == 'view_reports':
            # Administração, TI e Qualidade
            return department in ['administração', 'administracao', 'ti', 'qualidade']
        
        elif action == 'view_levantamento_14_15':
            # Apenas Administração, TI e Qualidade podem ver Levantamento 14-15
            return department in ['administração', 'administracao', 'ti', 'qualidade']
        
        elif action == 'admin_access':
            # Apenas Administração e TI
            return department in ['administração', 'administracao', 'ti']
        
        elif action == 'manage_users':
            # Apenas Administração e TI
            return department in ['administração', 'administracao', 'ti']
        
        elif action == 'edit_rncs':
            # Todos podem editar suas próprias RNCs (será verificado depois)
            return True
        
        elif action == 'view_groups_for_assignment':
            # Todos podem ver grupos para atribuição de RNCs
            return True
        
        elif action == 'view_users_for_assignment':
            # Todos podem ver usuários para atribuição de RNCs
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Erro ao verificar permissão de departamento: {e}")
        return False

def get_all_users():
    """Buscar todos os usuários ativos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.name, u.email, u.department, u.role, u.permissions, u.created_at, g.name as group_name
        FROM users u
        LEFT JOIN groups g ON u.group_id = g.id
        WHERE u.is_active = 1
        ORDER BY u.name
    ''')
    users = cursor.fetchall()
    conn.close()
    return users

def create_user(name, email, password, department, role, permissions):
    """Criar novo usuário"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    password_hash = generate_password_hash(password)
    import json
    permissions_json = json.dumps(permissions)
    
    try:
        # Verificar se o grupo existe, se não, criar automaticamente
        group_id = None
        if department:
            cursor.execute('SELECT id FROM groups WHERE name = ?', (department,))
            existing_group = cursor.fetchone()
            
            if existing_group:
                group_id = existing_group[0]
            else:
                # Criar o grupo automaticamente
                cursor.execute('INSERT INTO groups (name, description) VALUES (?, ?)', 
                             (department, f'Grupo criado automaticamente para {department}'))
                group_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, department, role, permissions, group_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, password_hash, department, role, permissions_json, group_id))
        
        conn.commit()

        # Índices para performance em consultas do dashboard
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rncs_created_at ON rncs(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rncs_status ON rncs(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rncs_user ON rncs(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rncs_assigned_user ON rncs(assigned_user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rncs_client ON rncs(client)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rncs_equipment ON rncs(equipment)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rncs_priority ON rncs(priority)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rncs_is_deleted ON rncs(is_deleted)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rncs_finalized_at ON rncs(finalized_at)')
            conn.commit()
        except Exception as e:
            logger.error(f"Erro ao criar índices: {e}")
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def update_user(user_id, name, email, department, role, permissions, is_active):
    """Atualizar usuário"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    import json
    permissions_json = json.dumps(permissions)
    
    # Verificar se o grupo existe, se não, criar automaticamente
    group_id = None
    if department:
        cursor.execute('SELECT id FROM groups WHERE name = ?', (department,))
        existing_group = cursor.fetchone()
        
        if existing_group:
            group_id = existing_group[0]
        else:
            # Criar o grupo automaticamente
            cursor.execute('INSERT INTO groups (name, description) VALUES (?, ?)', 
                         (department, f'Grupo criado automaticamente para {department}'))
            group_id = cursor.lastrowid
    
    cursor.execute('''
        UPDATE users 
        SET name = ?, email = ?, department = ?, role = ?, permissions = ?, is_active = ?, group_id = ?
        WHERE id = ?
    ''', (name, email, department, role, permissions_json, is_active, group_id, user_id))
    
    conn.commit()
    conn.close()
    return True

def delete_user(user_id):
    """Desativar usuário (soft delete)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

def restore_user(user_id: int) -> bool:
    """Reativar usuário previamente desativado."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_active = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

def update_user_password(user_id: int, new_password: str) -> bool:
    """Atualizar a senha de um usuário."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    new_hash = generate_password_hash(new_password)
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user_id))
    conn.commit()
    conn.close()
    return True

def get_all_groups():
    """Obter todos os grupos"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT g.id, g.name, g.description, COUNT(u.id) as user_count
            FROM groups g
            LEFT JOIN users u ON g.id = u.group_id AND u.is_active = 1
            GROUP BY g.id
            ORDER BY g.name
        ''')
        groups = cursor.fetchall()
        conn.close()
        return groups
    except Exception as e:
        logger.error(f"Erro ao buscar grupos: {e}")
        return []

def get_group_by_id(group_id):
    """Obter grupo por ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
        group = cursor.fetchone()
        conn.close()
        return group
    except Exception as e:
        logger.error(f"Erro ao buscar grupo: {e}")
        return None

def create_group(name, description):
    """Criar novo grupo"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO groups (name, description) VALUES (?, ?)', (name, description))
        group_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return group_id
    except Exception as e:
        logger.error(f"Erro ao criar grupo: {e}")
        return None

def update_group(group_id, name, description):
    """Atualizar grupo"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE groups SET name = ?, description = ? WHERE id = ?', (name, description, group_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar grupo: {e}")
        return False

def delete_group(group_id):
    """Deletar grupo"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Primeiro, remover referências de usuários
        cursor.execute('UPDATE users SET group_id = NULL WHERE group_id = ?', (group_id,))
        # Depois deletar o grupo
        cursor.execute('DELETE FROM groups WHERE id = ?', (group_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao deletar grupo: {e}")
        return False

def get_users_by_group(group_id):
    """Obter usuários de um grupo"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, email, department, role, is_active
            FROM users 
            WHERE group_id = ? AND is_active = 1
            ORDER BY name
        ''', (group_id,))
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        logger.error(f"Erro ao buscar usuários do grupo: {e}")
        return []
def share_rnc_with_user(rnc_id, shared_by_user_id, shared_with_user_id, permission_level='view'):
    """Compartilhar RNC com usuário com tolerância a lock do SQLite (retry/backoff)."""
    attempt = 0
    max_attempts = 5
    backoff_base = 0.2
    while attempt < max_attempts:
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)
            cursor = conn.cursor()
            cursor.execute('PRAGMA busy_timeout=5000')
            cursor.execute('BEGIN IMMEDIATE')
            cursor.execute(
                '''INSERT OR REPLACE INTO rnc_shares (rnc_id, shared_by_user_id, shared_with_user_id, permission_level)
                   VALUES (?, ?, ?, ?)''',
                (rnc_id, shared_by_user_id, shared_with_user_id, permission_level)
            )
            conn.commit()
            return True
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if 'locked' in msg or 'busy' in msg:
                attempt += 1
                wait = backoff_base * attempt
                try:
                    logger.warning(f"Lock ao compartilhar RNC {rnc_id} (tentativa {attempt}/{max_attempts}) aguardando {wait:.2f}s: {e}")
                except Exception:
                    pass
                time.sleep(wait)
                continue
            else:
                try:
                    logger.error(f"Erro operacional ao compartilhar RNC {rnc_id}: {e}")
                except Exception:
                    pass
                return False
        except Exception as e:
            try:
                logger.error(f"Erro inesperado ao compartilhar RNC {rnc_id}: {e}")
            except Exception:
                pass
            return False
        finally:
            try:
                if conn:
                    conn.close()
            except Exception:
                pass
    try:
        logger.warning("share_rnc_with_user: desistindo após múltiplas tentativas (database locked)")
    except Exception:
        pass
    return False

def get_rnc_shared_users(rnc_id):
    """Obter usuários com quem a RNC foi compartilhada"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT rs.shared_with_user_id, rs.permission_level, u.name, u.email
            FROM rnc_shares rs
            JOIN users u ON rs.shared_with_user_id = u.id
            WHERE rs.rnc_id = ?
        ''', (rnc_id,))
        shared_users = cursor.fetchall()
        conn.close()
        return shared_users
    except Exception as e:
        logger.error(f"Erro ao buscar usuários compartilhados da RNC {rnc_id}: {e}")
        return []

def can_user_access_rnc(user_id, rnc_id):
    """Verificar se usuário pode acessar RNC (criador, compartilhado ou admin)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se é o criador
        cursor.execute('SELECT user_id, department FROM rncs WHERE id = ?', (rnc_id,))
        rnc_data = cursor.fetchone()
        if not rnc_data:
            conn.close()
            logger.warning(f"RNC {rnc_id} não encontrada na verificação de acesso")
            return False
        
        logger.info(f"Verificando acesso do usuário {user_id} à RNC {rnc_id}, criada por {rnc_data[0]}, departamento: {rnc_data[1]}")
        
        # Se é o criador
        if str(rnc_data[0]) == str(user_id):
            logger.info(f"Acesso permitido: usuário {user_id} é o criador da RNC {rnc_id}")
            conn.close()
            return True
        
        # Verificar permissões
        if has_permission(user_id, 'view_all_rncs') or has_permission(user_id, 'admin_access'):
            logger.info(f"Acesso permitido: usuário {user_id} tem permissão admin ou view_all_rncs")
            conn.close() 
            return True
            
        # Verificar acesso por departamento
        rnc_department = rnc_data[1]
        if rnc_department == 'Engenharia' and has_permission(user_id, 'view_engineering_rncs'):
            logger.info(f"Acesso permitido: usuário {user_id} tem permissão view_engineering_rncs e RNC é da Engenharia")
            conn.close()
            return True
            
        if has_permission(user_id, 'view_all_departments_rncs'):
            logger.info(f"Acesso permitido: usuário {user_id} tem permissão view_all_departments_rncs")
            conn.close()
            return True
        
        # Verificar se foi compartilhado com o usuário
        cursor.execute('''
            SELECT permission_level FROM rnc_shares 
            WHERE rnc_id = ? AND shared_with_user_id = ?
        ''', (rnc_id, user_id))
        share_data = cursor.fetchone()
        
        conn.close()
        has_access = share_data is not None
        if has_access:
            logger.info(f"Acesso permitido: RNC {rnc_id} foi compartilhada com o usuário {user_id}")
        else:
            logger.warning(f"Acesso negado: usuário {user_id} não tem permissões necessárias para RNC {rnc_id}")
        return has_access
        
    except Exception as e:
        logger.error(f"Erro ao verificar acesso à RNC: {e}")
        return False

# ==================== FUNÇÕES DE PERMISSÕES ====================

def get_group_permissions(group_id):
    """Obter todas as permissões de um grupo"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT permission_name, permission_value
            FROM group_permissions
            WHERE group_id = ?
            ORDER BY permission_name
        ''', (group_id,))
        permissions = cursor.fetchall()
        conn.close()
        return permissions
    except Exception as e:
        logger.error(f"Erro ao buscar permissões do grupo: {e}")
        return []

def update_group_permissions(group_id, permissions):
    """Atualizar permissões de um grupo"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Remover permissões existentes
        cursor.execute('DELETE FROM group_permissions WHERE group_id = ?', (group_id,))
        
        # Inserir novas permissões
        for permission_name, permission_value in permissions.items():
            cursor.execute('''
                INSERT INTO group_permissions (group_id, permission_name, permission_value)
                VALUES (?, ?, ?)
            ''', (group_id, permission_name, 1 if permission_value else 0))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar permissões do grupo: {e}")
        return False

def get_user_group_permissions(user_id):
    """Obter permissões do usuário baseadas no seu grupo"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se é admin
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result and result[0] == 'admin':
            conn.close()
            return ['all']  # Admin tem todas as permissões
        
        # Buscar permissões do grupo
        cursor.execute('''
            SELECT gp.permission_name
            FROM group_permissions gp
            JOIN users u ON u.group_id = gp.group_id
            WHERE u.id = ? AND gp.permission_value = 1
        ''', (user_id,))
        
        permissions = [row[0] for row in cursor.fetchall()]
        conn.close()
        return permissions
    except Exception as e:
        logger.error(f"Erro ao buscar permissões do usuário: {e}")
        return []

def clear_permissions_cache():
    """Limpar cache de permissões"""
    with cache_lock:
        keys_to_remove = [
            key for key in query_cache.keys()
            if 'permissions' in key
        ]
        for key in keys_to_remove:
            del query_cache[key]
    logger.info("Cache de permissões limpo")

def get_all_permissions():
    """Obter lista de todas as permissões disponíveis com descrições"""
    # Limpar qualquer cache de permissões para forçar dados atualizados
    clear_permissions_cache()
    
    permissions = [
        {
            'name': 'create_rnc',
            'display_name': 'Criar RNC',
            'description': 'Permite criar novas RNCs no sistema'
        },
        {
            'name': 'edit_own_rnc',
            'display_name': 'Editar Próprias RNCs',
            'description': 'Permite editar RNCs criadas pelo próprio usuário'
        },
        {
            'name': 'view_own_rnc',
            'display_name': 'Visualizar Próprias RNCs',
            'description': 'Permite visualizar RNCs criadas pelo próprio usuário'
        },
        {
            'name': 'view_all_rncs',
            'display_name': 'Visualizar Todas as RNCs',
            'description': 'Permite visualizar todas as RNCs do sistema'
        },
        {
            'name': 'edit_all_rncs',
            'display_name': 'Editar Todas as RNCs',
            'description': 'Permite editar qualquer RNC do sistema'
        },
        {
            'name': 'delete_rnc',
            'display_name': 'Excluir RNCs',
            'description': 'Permite excluir RNCs do sistema'
        },
        {
            'name': 'view_finalized_rncs',
            'display_name': 'Visualizar RNCs Finalizadas',
            'description': 'Permite visualizar RNCs com status finalizado'
        },
        {
            'name': 'view_charts',
            'display_name': 'Visualizar Gráficos',
            'description': 'Permite acessar gráficos e estatísticas'
        },
        {
            'name': 'view_reports',
            'display_name': 'Visualizar Relatórios',
            'description': 'Permite acessar relatórios e indicadores'
        },
        {
            'name': 'admin_access',
            'display_name': 'Acesso Administrativo',
            'description': 'Acesso total ao sistema administrativo'
        },
        {
            'name': 'manage_users',
            'display_name': 'Gerenciar Usuários',
            'description': 'Permite criar, editar e excluir usuários'
        },
        {
            'name': 'view_engineering_rncs',
            'display_name': 'Visualizar RNCs da Engenharia',
            'description': 'Permite visualizar RNCs do departamento de engenharia'
        },
        {
            'name': 'view_all_departments_rncs',
            'display_name': 'Visualizar RNCs de Todos os Departamentos',
            'description': 'Permite visualizar RNCs de qualquer departamento'
        },
        {
            'name': 'view_levantamento_14_15',
            'display_name': 'Visualizar Levantamento 14/15',
            'description': 'Permite acessar dados do levantamento 14/15'
        },
        {
            'name': 'view_groups_for_assignment',
            'display_name': 'Visualizar Grupos para Atribuição',
            'description': 'Permite visualizar grupos para atribuição de RNCs'
        },
        {
            'name': 'view_users_for_assignment',
            'display_name': 'Visualizar Usuários para Atribuição',
            'description': 'Permite visualizar usuários para atribuição de RNCs'
        }
    ]
    
    return permissions

@app.route('/')
def index():
    """Página principal com login sempre como entrada."""
    try:
        if 'user_id' in session:
            return redirect('/dashboard')
        # Tentar template personalizado de login; fallback para index.html
        try:
            return render_template('login.html')
        except Exception:
            return send_from_directory('.', 'index.html')
    except Exception:
        return send_from_directory('.', 'index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard interativo protegido por sessão."""
    if 'user_id' not in session:
        return redirect('/')
    
    # Obter informações de permissões do usuário para o frontend
    user_permissions = {
        'canViewAllRncs': has_permission(session['user_id'], 'view_all_rncs'),
        'canViewFinalizedRncs': has_permission(session['user_id'], 'view_finalized_rncs'),
        'canViewCharts': has_permission(session['user_id'], 'view_charts'),
        'canViewReports': has_permission(session['user_id'], 'view_reports'),
    'hasAdminAccess': has_permission(session['user_id'], 'admin_access'),
    # Permissão correta: qualquer usuário com 'create_rnc' pode criar RNCs
    'canCreateRnc': has_permission(session['user_id'], 'create_rnc'),
        'canViewLevantamento1415': has_permission(session['user_id'], 'view_levantamento_14_15'),
        'canViewGroupsForAssignment': has_permission(session['user_id'], 'view_groups_for_assignment'),
        'canViewUsersForAssignment': has_permission(session['user_id'], 'view_users_for_assignment'),
        'canViewEngineeringRncs': has_permission(session['user_id'], 'view_engineering_rncs'),
        'department': get_user_department(session['user_id'])
    }
    
    return render_template('dashboard_improved.html', user_permissions=user_permissions)

@app.route('/indicadores-dashboard')
def indicadores_dashboard():
    """Dashboard de indicadores protegido por sessão."""
    if 'user_id' not in session:
        return redirect('/')
    
    # Verificar se o usuário tem permissão para ver relatórios/indicadores
    if not has_permission(session['user_id'], 'view_reports'):
        # Redirecionar para dashboard principal se não tiver permissão
        return redirect('/dashboard?error=access_denied&message=Acesso negado: usuário não tem permissão para visualizar indicadores')
    
    return render_template('indicadores_dashboard.html')

@app.route('/api/indicadores-detalhados')
def api_indicadores_detalhados():
    """API para dados detalhados dos indicadores"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Dados básicos
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0")
        total_rncs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE status = 'Pendente' AND is_deleted = 0")
        pendentes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE finalized_at IS NOT NULL AND is_deleted = 0")
        finalizadas = cursor.fetchone()[0]
        
        # Tendência mensal (últimos 12 meses)
        tendencia_mensal = {}
        for i in range(12):
            date = datetime.now() - timedelta(days=30*i)
            month_key = date.strftime('%Y-%m')
            cursor.execute("""
                SELECT COUNT(*) FROM rncs 
                WHERE strftime('%Y-%m', created_at) = ? AND is_deleted = 0
            """, (month_key,))
            count = cursor.fetchone()[0]
            tendencia_mensal[date.strftime('%b/%Y')] = count
        
        # RNCs por departamento (baseado nos usuários)
        cursor.execute("""
            SELECT u.department, COUNT(r.id) as total
            FROM rncs r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.is_deleted = 0
            GROUP BY u.department
            ORDER BY total DESC
        """)
        por_departamento = dict(cursor.fetchall())
        
        # Status das RNCs
        cursor.execute("""
            SELECT status, COUNT(*) as total
            FROM rncs 
            WHERE is_deleted = 0
            GROUP BY status
            ORDER BY total DESC
        """)
        por_status = dict(cursor.fetchall())
        
        # Taxa de eficiência
        eficiencia = {
            'finalizadas': finalizadas,
            'pendentes': pendentes,
            'taxa': round((finalizadas / max(total_rncs, 1)) * 100, 1)
        }
        
        # RNCs recentes
        cursor.execute("""
            SELECT r.rnc_number, r.title, r.status, r.priority, r.created_at, u.name as user_name
            FROM rncs r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.is_deleted = 0
            ORDER BY r.created_at DESC
            LIMIT 10
        """)
        rncs_recentes = []
        for row in cursor.fetchall():
            rncs_recentes.append({
                'numero': row[0],
                'titulo': row[1],
                'status': row[2],
                'prioridade': row[3],
                'data': row[4],
                'usuario': row[5] or 'Usuário'
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'total_rncs': total_rncs,
                'pendentes': pendentes,
                'finalizadas': finalizadas,
                'tendencia_mensal': tendencia_mensal,
                'por_departamento': por_departamento if por_departamento else {'Geral': total_rncs},
                'por_status': por_status if por_status else {'Pendente': pendentes, 'Finalizada': finalizadas},
                'eficiencia': eficiencia,
                'rncs_recentes': rncs_recentes
            }
        })
        
    except Exception as e:
        print(f"Erro na API de indicadores: {e}")
        # Dados de fallback
        return jsonify({
            'success': True,
            'data': {
                'total_rncs': 0,
                'pendentes': 0,
                'finalizadas': 0,
                'tendencia_mensal': {},
                'por_departamento': {'Geral': 0},
                'por_status': {'Pendente': 0},
                'eficiencia': {'finalizadas': 0, 'pendentes': 0, 'taxa': 0},
                'rncs_recentes': []
            }
        })

@app.route('/api/indicadores')
def api_indicadores():
    """API para dados dos indicadores (formato compatível com dashboard_improved.html)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Buscar dados das tabelas principais
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0")
        total_rncs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE status = 'Pendente' AND is_deleted = 0")
        pendentes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE finalized_at IS NOT NULL AND is_deleted = 0")
        finalizadas = cursor.fetchone()[0]
        
        # Dados por setor/departamento
        cursor.execute("""
            SELECT u.department as setor, COUNT(r.id) as total
            FROM rncs r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.is_deleted = 0 AND u.department IS NOT NULL
            GROUP BY u.department
            ORDER BY total DESC
        """)
        setores_raw = cursor.fetchall()
        
        # Dados por prioridade
        cursor.execute("""
            SELECT priority, COUNT(*) as total
            FROM rncs 
            WHERE is_deleted = 0 AND priority IS NOT NULL
            GROUP BY priority
            ORDER BY total DESC
        """)
        prioridades_raw = cursor.fetchall()
        
        # Dados mensais para tendência (últimos 6 meses)
        monthly_data = []
        for i in range(6):
            date = datetime.now() - timedelta(days=30*i)
            month_key = date.strftime('%Y-%m')
            cursor.execute("""
                SELECT COUNT(*) FROM rncs 
                WHERE strftime('%Y-%m', created_at) = ? AND is_deleted = 0
            """, (month_key,))
            count = cursor.fetchone()[0]
            monthly_data.append({
                'mes': date.strftime('%b'),
                'total': count
            })
        
        monthly_data.reverse()  # Ordem cronológica
        
        # Eficiência por departamento
        efficiency_data = []
        for setor, total in setores_raw:
            cursor.execute("""
                SELECT COUNT(*) FROM rncs r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.is_deleted = 0 AND u.department = ? AND r.finalized_at IS NOT NULL
            """, (setor,))
            finalizadas_setor = cursor.fetchone()[0]
            
            efficiency = round((finalizadas_setor / max(total, 1)) * 100, 1)
            efficiency_data.append({
                'setor': setor,
                'eficiencia': efficiency,
                'meta': 85.0,  # Meta padrão
                'realizado': efficiency
            })
        
        conn.close()
        
        # Formatar dados compatíveis com o dashboard
        # Converter dados de eficiência em formato de departamentos esperado pelo dashboard
        departments_data = []
        for item in efficiency_data:
            departments_data.append({
                'department': item['setor'],
                'meta': item['meta'],
                'realizado': item['realizado'],
                'efficiency': item['eficiencia']
            })
        
        # Se não há dados de departamentos, usar dados fictícios
        if not departments_data:
            departments_data = [
                {'department': 'PRODUÇÃO', 'meta': 80, 'realizado': 60, 'efficiency': 75.0},
                {'department': 'ENGENHARIA', 'meta': 70, 'realizado': 55, 'efficiency': 78.6},
                {'department': 'QUALIDADE', 'meta': 50, 'realizado': 35, 'efficiency': 70.0}
            ]
        
        result = {
            'success': True,
            'kpis': {
                'total_rncs': total_rncs,
                'total_metas': total_rncs,  # Assumindo que todas as RNCs são metas
                'active_departments': len(setores_raw) if setores_raw else 3,
                'overall_efficiency': round((finalizadas / max(total_rncs, 1)) * 100, 1),
                'avg_rncs_per_dept': round(total_rncs / max(len(setores_raw), 1), 1) if setores_raw else 0
            },
            'totals': {
                'total': total_rncs,
                'pendentes': pendentes,
                'finalizadas': finalizadas,
                'resolvidas': finalizadas
            },
            'departments': departments_data,  # Nome correto esperado pelo dashboard
            'monthly_trends': monthly_data,   # Nome correto esperado pelo dashboard
            'setores': [{'setor': row[0], 'total': row[1]} for row in setores_raw] if setores_raw else [{'setor': 'Geral', 'total': total_rncs}],
            'prioridades': [{'prioridade': row[0], 'total': row[1]} for row in prioridades_raw] if prioridades_raw else [{'prioridade': 'Média', 'total': total_rncs}],
            'tendencia': monthly_data,
            'eficiencia_departamentos': efficiency_data,
            'eficiencia': round((finalizadas / max(total_rncs, 1)) * 100, 1)
        }
        
        print(f"📊 API Indicadores retornando: {result}")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Erro na API de indicadores: {e}")
        import traceback
        traceback.print_exc()
        
        # Dados de fallback em caso de erro
        return jsonify({
            'success': True,
            'kpis': {
                'total_rncs': 0,
                'total_metas': 0,
                'active_departments': 3,
                'overall_efficiency': 0,
                'avg_rncs_per_dept': 0
            },
            'totals': {'total': 0, 'pendentes': 0, 'finalizadas': 0, 'resolvidas': 0},
            'departments': [
                {'department': 'PRODUÇÃO', 'meta': 80, 'realizado': 0, 'efficiency': 0},
                {'department': 'ENGENHARIA', 'meta': 70, 'realizado': 0, 'efficiency': 0},
                {'department': 'QUALIDADE', 'meta': 50, 'realizado': 0, 'efficiency': 0}
            ],
            'monthly_trends': [
                {'mes': 'Jan', 'total': 0},
                {'mes': 'Fev', 'total': 0},
                {'mes': 'Mar', 'total': 0},
                {'mes': 'Abr', 'total': 0},
                {'mes': 'Mai', 'total': 0},
                {'mes': 'Jun', 'total': 0}
            ],
            'setores': [{'setor': 'Geral', 'total': 0}],
            'prioridades': [{'prioridade': 'Média', 'total': 0}],
            'tendencia': [],
            'eficiencia_departamentos': [],
            'eficiencia': 0
        })

@app.route('/dashboard/api/kpis')
def dashboard_api_kpis():
    """API de KPIs para o dashboard melhorado"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # KPIs básicos
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0")
        total_rncs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE status = 'Pendente' AND is_deleted = 0")
        pendentes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE finalized_at IS NOT NULL AND is_deleted = 0")
        finalizadas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT u.department) FROM rncs r LEFT JOIN users u ON r.user_id = u.id WHERE r.is_deleted = 0 AND u.department IS NOT NULL")
        departamentos_ativos = cursor.fetchone()[0]
        
        # Eficiência geral
        eficiencia_geral = round((finalizadas / max(total_rncs, 1)) * 100, 1)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'kpis': {
                'total_rncs': total_rncs,
                'pendentes': pendentes,
                'finalizadas': finalizadas,
                'departamentos_ativos': departamentos_ativos,
                'eficiencia_geral': eficiencia_geral
            }
        })
        
    except Exception as e:
        print(f"❌ Erro na API de KPIs: {e}")
        return jsonify({
            'success': True,
            'kpis': {
                'total_rncs': 0,
                'pendentes': 0,
                'finalizadas': 0,
                'departamentos_ativos': 0,
                'eficiencia_geral': 0
            }
        })

@app.route('/form')
def form():
    """Formulário RNC (apenas para administradores)"""
    if 'user_id' not in session:
        return redirect('/')
    
    # Verificar permissão correta para criar RNCs
    if not has_permission(session['user_id'], 'create_rnc'):
        return render_template('error.html', 
                             error_title='Acesso Negado', 
                             error_message='Você não tem permissão para criar RNCs.'), 403
    
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
            session.permanent = True

            # Cookie auxiliar para reidratar sessão em caso de perda (navegadores ou extensões)
            resp = jsonify({
                'success': True,
                'message': 'Login realizado com sucesso!',
                'redirect': '/dashboard',
                'user': {
                    'name': user_data[1],
                    'email': user_data[2],
                    'department': user_data[4]
                }
            })
            try:
                resp.set_cookie('IPPEL_UID', str(user_data[0]),
                                max_age=60*60*8, path='/', httponly=False, samesite='Lax')
            except Exception:
                pass
            return resp
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
    try:
        session_keys = ['user_id','user_name','user_email','user_department','user_role']
        for k in session_keys:
            try:
                session.pop(k, None)
            except Exception:
                pass
        session.clear()
        resp = jsonify({'success': True, 'message': 'Logout realizado com sucesso!'})
        try:
            resp.delete_cookie('IPPEL_UID', path='/')
        except Exception:
            pass
        return resp
    except Exception:
        return jsonify({'success': True})

@app.route('/api/employee-performance')
def get_employee_performance():
    """API para obter desempenho por funcionário - CORRIGIDA"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    conn = None
    try:
        year = request.args.get('year', '')
        month = request.args.get('month', '')
        print(f"🧑‍💼 API chamada - Ano: {year or 'Todos'}, Mês: {month or 'Todos'}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # NÃO buscar usuários da tabela users - usar apenas as assinaturas das RNCs
        print(f"🔍 Usando apenas assinaturas das RNCs (não usuários da tabela)")

        # Query corrigida para buscar RNCs de TODOS os usuários
        # Primeiro, vamos verificar a estrutura da tabela
        cursor.execute("PRAGMA table_info(rncs)")
        cols = {row[1] for row in cursor.fetchall()}
        print(f"🔍 Colunas da tabela RNCs: {cols}")
        
        # Query corrigida - usar assinatura de engenharia (segunda assinatura)
        base_query = """
            SELECT 
                CASE 
                    WHEN r.signature_engineering_name IS NOT NULL AND r.signature_engineering_name != '' 
                    THEN r.signature_engineering_name
                    ELSE r.user_id
                END as owner_id,
                COUNT(r.id) as rnc_count
            FROM rncs r
            WHERE r.status IN ('Finalizado','finalized')
              AND r.is_deleted = 0
        """

        params = []
        if year and year.lower() != 'todos':
            base_query += " AND strftime('%Y', r.created_at) = ?"
            params.append(year)
            print(f"🗓️ Filtro ano aplicado: {year}")
        if month and month.lower() != 'todos':
            base_query += " AND strftime('%m', r.created_at) = ?"
            params.append(month.zfill(2))
            print(f"📅 Filtro mês aplicado: {month}")

        base_query += " GROUP BY owner_id"
        print(f"🔍 Executando query: {base_query}")
        print(f"📋 Parâmetros: {params}")

        cursor.execute(base_query, params)
        rnc_rows = cursor.fetchall()
        rnc_data = {row[0]: row[1] for row in rnc_rows}
        print(f"📊 RNCs por usuário: {rnc_data}")
        
        # Debug: verificar algumas RNCs para entender a distribuição
        cursor.execute("""
            SELECT r.user_id, u.name, COUNT(*) as count
            FROM rncs r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.status IN ('Finalizado','finalized')
              AND r.is_deleted = 0
            GROUP BY r.user_id, u.name
            ORDER BY count DESC
            LIMIT 10
        """)
        debug_rncs = cursor.fetchall()
        print(f"🔍 Debug - Top 10 usuários por RNCs: {debug_rncs}")
        
        # Verificar se há RNCs com user_id NULL ou inválido
        cursor.execute("""
            SELECT COUNT(*) as total_rncs,
                   COUNT(CASE WHEN user_id IS NULL THEN 1 END) as null_user_id,
                   COUNT(CASE WHEN user_id = 1 THEN 1 END) as admin_rncs
            FROM rncs 
            WHERE status IN ('Finalizado','finalized')
              AND is_deleted = 0
        """)
        debug_stats = cursor.fetchone()
        print(f"📈 Debug - Estatísticas: Total={debug_stats[0]}, NULL user_id={debug_stats[1]}, Admin RNCs={debug_stats[2]}")

        meta_mensal = 5
        result = []
        
        # Criar lista de assinaturas únicas (SEM remover espaços para manter compatibilidade com rnc_data)
        unique_signatures = set()
        for owner_id, count in rnc_rows:
            if isinstance(owner_id, str) and owner_id:
                unique_signatures.add(owner_id)  # SEM .strip() para manter compatibilidade
            elif isinstance(owner_id, int):
                # Se for ID, buscar nome do usuário
                cursor.execute("SELECT name FROM users WHERE id = ?", (owner_id,))
                user_result = cursor.fetchone()
                if user_result:
                    unique_signatures.add(user_result[0])
        
        print(f"🔍 Assinaturas únicas encontradas: {len(unique_signatures)}")
        print(f"🔍 Exemplos: {list(unique_signatures)[:5]}")
        
        # Processar cada assinatura
        for signature in sorted(unique_signatures):
            rncs = rnc_data.get(signature, 0)
            percentage = (rncs / meta_mensal * 100) if meta_mensal > 0 else 0
            status = 'Acima da Meta' if rncs >= meta_mensal else 'Abaixo da Meta'
            
            # Adicionar logs para debug
            print(f"   👤 Processando assinatura: '{signature}' - RNCs: {rncs}")
            
            result.append({
                'id': signature,
                'name': signature,
                'rncs': rncs,
                'meta': meta_mensal,
                'percentage': round(percentage, 1),
                'status': status,
                'department': 'Engenharia'
            })

        result.sort(key=lambda x: x['percentage'], reverse=True)
        print(f"✅ Resultado final: {len(result)} funcionários processados")
        for emp in result[:3]:
            print(f"   👤 {emp['name']}: {emp['rncs']} RNCs ({emp['percentage']}%)")

        return jsonify({
            'success': True,
            'data': result,
            'filters': {
                'year': year or 'todos',
                'month': month or 'todos'
            }
        })
    except Exception as e:
        print(f"❌ Erro ao buscar desempenho de funcionários: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar dados de funcionários: {str(e)}'
        }), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

@app.route('/api/dashboard/performance')
def get_dashboard_performance():
    """API específica para dashboard de desempenho - SEM VERIFICAÇÃO DE PERMISSÃO"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    conn = None
    try:
        year = request.args.get('year', '')
        month = request.args.get('month', '')
        print(f"📊 Dashboard API chamada - Ano: {year or 'Todos'}, Mês: {month or 'Todos'}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # NÃO buscar usuários da tabela users - usar apenas as assinaturas das RNCs
        print(f"🔍 Dashboard - Usando apenas assinaturas das RNCs (não usuários da tabela)")

        # Query para buscar RNCs finalizadas
        # Usar assinatura de engenharia (segunda assinatura)
        base_query = """
            SELECT 
                CASE 
                    WHEN r.signature_engineering_name IS NOT NULL AND r.signature_engineering_name != '' 
                    THEN r.signature_engineering_name
                    ELSE r.user_id
                END as owner_id,
                COUNT(r.id) as rnc_count
            FROM rncs r
            WHERE r.status IN ('Finalizado','finalized')
              AND r.is_deleted = 0
        """

        params = []
        if year and year.lower() != 'todos':
            base_query += " AND strftime('%Y', r.created_at) = ?"
            params.append(year)
        if month and month.lower() != 'todos':
            base_query += " AND strftime('%m', r.created_at) = ?"
            params.append(month.zfill(2))

        base_query += " GROUP BY owner_id"
        cursor.execute(base_query, params)
        rnc_rows = cursor.fetchall()
        rnc_data = {row[0]: row[1] for row in rnc_rows}
        
        # Debug: verificar algumas RNCs para entender a distribuição
        cursor.execute("""
            SELECT r.user_id, u.name, COUNT(*) as count
            FROM rncs r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.status IN ('Finalizado','finalized')
              AND r.is_deleted = 0
            GROUP BY r.user_id, u.name
            ORDER BY count DESC
            LIMIT 10
        """)
        debug_rncs = cursor.fetchall()
        print(f"🔍 Dashboard Debug - Top 10 usuários por RNCs: {debug_rncs}")
        
        # Verificar se há RNCs com user_id NULL ou inválido
        cursor.execute("""
            SELECT COUNT(*) as total_rncs,
                   COUNT(CASE WHEN user_id IS NULL THEN 1 END) as null_user_id,
                   COUNT(CASE WHEN user_id = 1 THEN 1 END) as admin_rncs
            FROM rncs 
            WHERE status IN ('Finalizado','finalized')
              AND is_deleted = 0
        """)
        debug_stats = cursor.fetchone()
        print(f"📈 Dashboard Debug - Estatísticas: Total={debug_stats[0]}, NULL user_id={debug_stats[1]}, Admin RNCs={debug_stats[2]}")

        meta_mensal = 5
        result = []
        
        # Criar lista de assinaturas únicas (SEM remover espaços para manter compatibilidade com rnc_data)
        unique_signatures = set()
        for owner_id, count in rnc_rows:
            if isinstance(owner_id, str) and owner_id:
                unique_signatures.add(owner_id)  # SEM .strip() para manter compatibilidade
            elif isinstance(owner_id, int):
                # Se for ID, buscar nome do usuário
                cursor.execute("SELECT name FROM users WHERE id = ?", (owner_id,))
                user_result = cursor.fetchone()
                if user_result:
                    unique_signatures.add(user_result[0])
        
        print(f"🔍 Dashboard - Assinaturas únicas encontradas: {len(unique_signatures)}")
        print(f"🔍 Dashboard - Exemplos: {list(unique_signatures)[:5]}")
        
        # Processar cada assinatura
        for signature in sorted(unique_signatures):
            rncs = rnc_data.get(signature, 0)
            percentage = (rncs / meta_mensal * 100) if meta_mensal > 0 else 0
            status = 'Acima da Meta' if rncs >= meta_mensal else 'Abaixo da Meta'
            
            # Adicionar logs para debug
            print(f"   📊 Dashboard - Processando assinatura: '{signature}' - RNCs: {rncs}")
            
            result.append({
                'id': signature,
                'name': signature,
                'rncs': rncs,
                'meta': meta_mensal,
                'percentage': round(percentage, 1),
                'status': status,
                'department': 'Engenharia'
            })

        result.sort(key=lambda x: x['percentage'], reverse=True)
        print(f"✅ Dashboard: {len(result)} funcionários processados")

        return jsonify({
            'success': True,
            'data': result,
            'filters': {
                'year': year or 'todos',
                'month': month or 'todos'
            }
        })
    except Exception as e:
        print(f"❌ Erro no dashboard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar dados do dashboard: {str(e)}'
        }), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

@app.route('/api/user/info')
def get_user_info():
    """API para obter informações do usuário logado"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        # Buscar dados básicos do usuário
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.permissions, g.name as group_name, u.avatar_key, u.avatar_prefs
            FROM users u
            LEFT JOIN groups g ON u.group_id = g.id
            WHERE u.id = ?
        ''', (session['user_id'],))
        user_data = cursor.fetchone()
        
        # Buscar permissões específicas do grupo
        cursor.execute('''
            SELECT gp.permission_name, gp.permission_value
            FROM group_permissions gp
            JOIN users u ON u.group_id = gp.group_id
            WHERE u.id = ? AND gp.permission_value = 1
        ''', (session['user_id'],))
        group_permissions = cursor.fetchall()
        conn.close()
        
        # Permissions do usuário (compatibilidade)
        permissions = []
        if user_data and user_data[0]:
            try:
                # Tentar parsear como JSON
                permissions = json.loads(user_data[0])
            except json.JSONDecodeError:
                # Se falhar, assumir que é string separada por vírgulas
                permissions = [p.strip() for p in user_data[0].split(',')]
        
        # Adicionar permissões do grupo
        group_perms_list = [perm[0] for perm in group_permissions]
        
        # Adicionar permissões baseadas em departamento
        department_permissions = {
            'canViewAllRncs': has_permission(session['user_id'], 'view_all_rncs'),
            'canViewOwnRncs': has_permission(session['user_id'], 'view_own_rncs'),
            'canViewFinalizedRncs': has_permission(session['user_id'], 'view_finalized_rncs'),
            'canViewCharts': has_permission(session['user_id'], 'view_charts'),
            'canViewReports': has_permission(session['user_id'], 'view_reports'),
            'hasAdminAccess': has_permission(session['user_id'], 'admin_access'),
            'canManageUsers': has_permission(session['user_id'], 'manage_users'),
            'canEditRncs': has_permission(session['user_id'], 'edit_all_rncs'),
            'canEditOwnRncs': has_permission(session['user_id'], 'edit_own_rnc'),
            'canCreateRnc': has_permission(session['user_id'], 'create_rnc'),
            'canDeleteRncs': has_permission(session['user_id'], 'delete_rncs'),
            'canReplyRncs': has_permission(session['user_id'], 'reply_rncs'),
            'canFinalizeRnc': has_permission(session['user_id'], 'finalize_rnc'),
            'canViewGroupsForAssignment': True,  # Todos podem ver grupos para atribuição
            'canViewUsersForAssignment': True    # Todos podem ver usuários para atribuição
        }
        
        # Preparar preferências de avatar
        avatar_prefs = None
        try:
            if user_data and len(user_data) > 3 and user_data[3]:
                avatar_prefs = json.loads(user_data[3])
        except Exception:
            avatar_prefs = None

        user_info = {
            'id': session['user_id'],
            'name': session['user_name'],
            'email': session['user_email'],
            'department': session.get('user_department') or get_user_department(session['user_id']),
            'group': user_data[1] if user_data else None,
            'role': session['user_role'],
            'permissions': permissions,
            'groupPermissions': group_perms_list,
            'departmentPermissions': department_permissions,
            'avatar': (user_data[2] if user_data and len(user_data) > 2 else None),
            'avatarPrefs': avatar_prefs
        }
        
        logger.info(f"Informações do usuário: {user_info}")
        
        resp = jsonify({'success': True, 'user': user_info})
        resp.headers['Cache-Control'] = 'no-store'
        return resp
    except Exception as e:
        logger.error(f"Erro ao buscar informações do usuário: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar informações do usuário'
        }), 500

    # rota /api/user/avatar movida para routes/api.py (Blueprint)

@app.route('/api/rnc/create', methods=['POST'])
def create_rnc():
    """API para criar RNC (robusta a diferenças de schema)."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401

    # Verificar permissão apropriada para criação de RNC
    if not has_permission(session['user_id'], 'create_rnc'):
        return jsonify({'success': False, 'message': 'Usuário sem permissão para criar RNCs'}), 403

    try:
        data = request.get_json() or {}

        # Abrir conexão e detectar colunas disponíveis
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(rncs)")
        cols = {row[1] for row in cursor.fetchall()}  # set com nomes das colunas

        # Gerar número único do RNC
        import datetime
        now = datetime.datetime.now()
        rnc_number = f"RNC-{now.year}-{now.month:02d}-{now.day:02d}-{now.hour:02d}{now.minute:02d}{now.second:02d}"

        # Se o schema possuir colunas de assinatura, exigir ao menos uma; caso contrário, não bloquear
        signature_columns = {
            'signature_inspection_name',
            'signature_engineering_name',
            'signature_inspection2_name'
        }
        if signature_columns & cols:
            assinaturas = [
                data.get('signature_inspection_name', data.get('assinatura1', '')), 
                data.get('signature_engineering_name', data.get('assinatura2', '')), 
                data.get('signature_inspection2_name', data.get('assinatura3', ''))
            ]
            if not any(a and a != 'NOME' for a in assinaturas):
                return jsonify({'success': False, 'message': 'É obrigatório preencher pelo menos uma assinatura!'}), 400

        # Obter departamento do usuário atual
        cursor.execute('SELECT department FROM users WHERE id = ?', (session['user_id'],))
        user_dept_row = cursor.fetchone()
        user_department = user_dept_row[0] if user_dept_row else 'N/A'

        # Montar insert dinamicamente com base nas colunas do banco
        values_by_col = {
            'rnc_number': rnc_number,
            'title': data.get('title', 'RNC sem título'),
            'description': data.get('description', ''),
            'equipment': data.get('equipment', ''),
            'client': data.get('client', ''),
            'priority': data.get('priority', 'Média'),
            'status': 'Pendente',
            'user_id': session['user_id'],
            'assigned_user_id': data.get('assigned_user_id'),
            'department': user_department,  # Adicionar departamento do usuário
            # opcionais
            'signature_inspection_name': data.get('signature_inspection_name', data.get('assinatura1', '')),
            'signature_engineering_name': data.get('signature_engineering_name', data.get('assinatura2', '')),
            'signature_inspection2_name': data.get('signature_inspection2_name', data.get('assinatura3', '')),
            'price': float(data.get('price') or 0),
            # Campos de disposição (checkboxes)
            'disposition_usar': int(data.get('disposition_usar', False)),
            'disposition_retrabalhar': int(data.get('disposition_retrabalhar', False)),
            'disposition_rejeitar': int(data.get('disposition_rejeitar', False)),
            'disposition_sucata': int(data.get('disposition_sucata', False)),
            'disposition_devolver_estoque': int(data.get('disposition_devolver_estoque', False)),
            'disposition_devolver_fornecedor': int(data.get('disposition_devolver_fornecedor', False)),
            # Campos de inspeção (checkboxes)
            'inspection_aprovado': int(data.get('inspection_aprovado', False)),
            'inspection_reprovado': int(data.get('inspection_reprovado', False)),
            'inspection_ver_rnc': data.get('inspection_ver_rnc', ''),
        }

        insert_cols = [c for c in values_by_col.keys() if c in cols]
        insert_vals = [values_by_col[c] for c in insert_cols]

        if not insert_cols:
            conn.close()
            return jsonify({'success': False, 'message': 'Schema da tabela rncs inválido'}), 500

        placeholders = ", ".join(["?"] * len(insert_cols))
        sql = f"INSERT INTO rncs ({', '.join(insert_cols)}) VALUES ({placeholders})"
        cursor.execute('BEGIN IMMEDIATE')
        cursor.execute(sql, insert_vals)
        rnc_id = cursor.lastrowid

        # Compartilhamento com grupos (opcional)
        shared_group_ids = data.get('shared_group_ids', []) or []
        shared_user_count = 0
        # Compartilhamento é melhor como tarefa em background para não atrasar o retorno
        try:
            import threading
            def _share_task(rid, owner_id, group_ids):
                for gid in group_ids or []:
                    if not gid:
                        continue
                    users = get_users_by_group(gid)
                    for u in users:
                        uid = u[0]
                        if uid != owner_id:
                            share_rnc_with_user(rid, owner_id, uid, 'view')
            threading.Thread(target=_share_task, args=(rnc_id, session['user_id'], shared_group_ids), daemon=True).start()
        except Exception as e:
            logger.warning(f"Agendamento de compartilhamento falhou: {e}")

        try:
            conn.commit()
        finally:
            conn.close()

        # Limpar cache de RNCs
        try:
            clear_rnc_cache()
        except Exception:
            pass

        return jsonify({
            'success': True,
            'message': f'RNC criado com sucesso! Compartilhado com {shared_user_count} usuário(s).',
            'rnc_id': rnc_id,
            'rnc_number': rnc_number
        })
    except Exception as e:
        logger.error(f"Erro ao criar RNC: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
        return jsonify({'success': False, 'message': 'Erro interno ao criar RNC'}), 500

@app.route('/api/rnc/<int:rnc_id>/update', methods=['PUT'])
def update_rnc(rnc_id: int):
    """Atualiza uma RNC existente de forma dinâmica conforme as colunas disponíveis.
    Permite edição por administradores, criador da RNC ou usuário atribuído."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Verificar existência e permissões básicas
        cursor.execute('SELECT user_id, assigned_user_id, COALESCE(is_deleted, 0) FROM rncs WHERE id = ?', (rnc_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'success': False, 'message': 'RNC não encontrada'}), 404

        owner_id, assigned_id, is_deleted = row
        if is_deleted:
            conn.close()
            return jsonify({'success': False, 'message': 'RNC removida'}), 400

        is_admin = has_permission(session['user_id'], 'admin_access')
        if not (is_admin or session['user_id'] in (owner_id, assigned_id)):
            conn.close()
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403

        data = request.get_json() or {}

        # Descobrir colunas da tabela
        cursor.execute('PRAGMA table_info(rncs)')
        cols = {row[1] for row in cursor.fetchall()}

        # Se o schema possuir colunas de assinatura, exigir ao menos uma quando enviados nomes
        signature_columns = {
            'signature_inspection_name',
            'signature_engineering_name',
            'signature_inspection2_name'
        }
        if signature_columns & cols:
            assinaturas = [
                data.get('signature_inspection_name', ''),
                data.get('signature_engineering_name', ''),
                data.get('signature_inspection2_name', '')
            ]
            # Só validar se pelo menos um dos campos de assinatura veio no payload, senão mantém atual
            if any(x is not None for x in assinaturas):
                if not any(a and a != 'NOME' for a in assinaturas):
                    return jsonify({'success': False, 'message': 'É obrigatório preencher pelo menos uma assinatura!'}), 400

        # Mapeia possíveis campos recebidos -> colunas reais
        candidate_values = {
            'title': data.get('title'),
            'description': data.get('description'),
            'equipment': data.get('equipment'),
            'client': data.get('client'),
            'rnc_number': data.get('rnc_number'),
            'priority': data.get('priority'),
            'status': data.get('status'),
            'signature_inspection_name': data.get('signature_inspection_name'),
            'signature_engineering_name': data.get('signature_engineering_name'),
            'signature_inspection2_name': data.get('signature_inspection2_name'),
            'signature_inspection_date': data.get('signature_inspection_date'),
            'signature_engineering_date': data.get('signature_engineering_date'),
            'signature_inspection2_date': data.get('signature_inspection2_date'),
            'instruction_retrabalho': data.get('instruction_retrabalho'),
            'cause_rnc': data.get('cause_rnc'),
            'action_rnc': data.get('action_rnc'),
            'inspection_aprovado': int(data.get('inspection_aprovado')) if 'inspection_aprovado' in data else None,
            'inspection_reprovado': int(data.get('inspection_reprovado')) if 'inspection_reprovado' in data else None,
            'inspection_ver_rnc': data.get('inspection_ver_rnc'),
            'disposition_usar': int(data.get('disposition_usar')) if 'disposition_usar' in data else None,
            'disposition_retrabalhar': int(data.get('disposition_retrabalhar')) if 'disposition_retrabalhar' in data else None,
            'disposition_rejeitar': int(data.get('disposition_rejeitar')) if 'disposition_rejeitar' in data else None,
            'disposition_sucata': int(data.get('disposition_sucata')) if 'disposition_sucata' in data else None,
            'disposition_devolver_estoque': int(data.get('disposition_devolver_estoque')) if 'disposition_devolver_estoque' in data else None,
            'disposition_devolver_fornecedor': int(data.get('disposition_devolver_fornecedor')) if 'disposition_devolver_fornecedor' in data else None,
        }

        update_cols = []
        update_vals = []
        for col, val in candidate_values.items():
            if col in cols and val is not None:
                update_cols.append(f"{col} = ?")
                update_vals.append(val)

        if not update_cols:
            conn.close()
            return jsonify({'success': False, 'message': 'Nada para atualizar'}), 400

        update_sql = f"UPDATE rncs SET {', '.join(update_cols)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        update_vals.append(rnc_id)

        cursor.execute('BEGIN IMMEDIATE')
        cursor.execute(update_sql, update_vals)
        conn.commit()
        conn.close()

        try:
            clear_rnc_cache()
        except Exception:
            pass

        return jsonify({'success': True})

    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        logger.error(f"Erro ao atualizar RNC {rnc_id}: {e}")
        return jsonify({'success': False, 'message': 'Erro interno ao atualizar RNC'}), 500

    except Exception as e:
        logger.error(f"Erro ao criar RNC: {e}")
        try:
            return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
        except Exception:
            # fallback caso jsonify falhe
            return ('{"success": false, "message": "Erro interno"}', 500, {'Content-Type': 'application/json'})
@app.route('/api/rnc/list')
def list_rncs():
    """API para listar RNCs por abas ('active' e 'finalized').

    Observação: o sistema de lixeira foi removido; não há mais aba 'deleted'.
    """
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': 'Usuário não autenticado'
        }), 401
    
    conn = None
    try:
        # Obter parâmetros de filtro
        tab = request.args.get('tab', 'active')  # active, finalized
        user_id = session['user_id']
        
        # Verificar se deve ignorar cache (parâmetro _t indica force refresh)
        force_refresh = request.args.get('_t') is not None
        
        # Cache key baseada no usuário e aba
        cache_key = f"rncs_list_{user_id}_{tab}"
        if not force_refresh:
            cached_result = get_cached_query(cache_key)
            if cached_result:
                logger.info(f"Retornando cache para {cache_key}")
                return jsonify(cached_result)
        else:
            logger.info(f"Force refresh solicitado - ignorando cache para {cache_key}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construir query otimizada - incluindo campos de atribuição
        base_query = '''
                SELECT 
                    r.id,
                    r.rnc_number,
                    r.title,
                    r.equipment,
                    r.client,
                    r.priority,
                    r.status,
                    r.user_id,
                    r.assigned_user_id,
                    r.created_at,
                    r.updated_at,
                    r.finalized_at,
                    u.name AS user_name,
                    u.department AS user_department,
                    au.name AS assigned_user_name
                FROM rncs r 
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN users au ON r.assigned_user_id = au.id
        '''
        
        # Aplicar filtros baseados na aba - SEM LIMITES para mostrar todos os RNCs
        if tab == 'active':
            # RNCs ativos - mostrar todos
            if has_permission(session['user_id'], 'view_all_rncs'):
                cursor.execute(base_query + '''
                    WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL) 
                    AND r.status NOT IN ('Finalizado') 
                    ORDER BY r.id DESC
                ''')
            else:
                # Query para usuário específico - RNCs criados, atribuídos OU compartilhados via rnc_shares
                cursor.execute('''
                    SELECT DISTINCT
                        r.id,
                        r.rnc_number,
                        r.title,
                        r.equipment,
                        r.client,
                        r.priority,
                        r.status,
                        r.user_id,
                        r.assigned_user_id,
                        r.created_at,
                        r.updated_at,
                        r.finalized_at,
                        u.name AS user_name,
                        u.department AS user_department,
                        au.name AS assigned_user_name
                    FROM rncs r 
                    LEFT JOIN users u ON r.user_id = u.id
                    LEFT JOIN users au ON r.assigned_user_id = au.id
                    LEFT JOIN rnc_shares rs ON rs.rnc_id = r.id
                    WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL) 
                    AND r.status NOT IN ('Finalizado') 
                    AND (r.user_id = ? OR r.assigned_user_id = ? OR rs.shared_with_user_id = ?)
                    ORDER BY r.id DESC
                ''', (session['user_id'], session['user_id'], session['user_id']))

        elif tab == 'finalized':
            # RNCs finalizados - mostrar todos
            if has_permission(session['user_id'], 'view_finalized_rncs'):
                cursor.execute(base_query + '''
                    WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL) 
                    AND r.status = 'Finalizado'
                    ORDER BY r.id DESC
                ''')
            else:
                # RNCs finalizados - criados, atribuídos OU compartilhados via rnc_shares
                cursor.execute('''
                    SELECT DISTINCT
                        r.id,
                        r.rnc_number,
                        r.title,
                        r.equipment,
                        r.client,
                        r.priority,
                        r.status,
                        r.user_id,
                        r.assigned_user_id,
                        r.created_at,
                        r.updated_at,
                        r.finalized_at,
                        u.name AS user_name,
                        u.department AS user_department,
                        au.name AS assigned_user_name
                    FROM rncs r 
                    LEFT JOIN users u ON r.user_id = u.id
                    LEFT JOIN users au ON r.assigned_user_id = au.id
                    LEFT JOIN rnc_shares rs ON rs.rnc_id = r.id
                    WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL) 
                    AND r.status = 'Finalizado' 
                    AND (r.user_id = ? OR r.assigned_user_id = ? OR rs.shared_with_user_id = ?)
                    ORDER BY r.id DESC
                ''', (session['user_id'], session['user_id'], session['user_id']))

        else:
            # Fallback para aba ativa - todos os RNCs
            cursor.execute(base_query + '''
                WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL) 
                AND r.status NOT IN ('Finalizado')
                ORDER BY r.id DESC
            ''')
        
        rncs = cursor.fetchall()
        logger.info(f"🔍 Query executada para {tab}: {len(rncs)} RNCs encontrados no banco")
        
        # Formatar dados
        formatted_rncs = []
        current_user_id = session['user_id']
        
        # Usar list comprehension para melhor performance
        formatted_rncs = [
            {
                'id': rnc[0],
                'rnc_number': rnc[1],
                'title': rnc[2],
                'equipment': rnc[3],
                'client': rnc[4],
                'priority': rnc[5],
                'status': rnc[6],
                'user_id': rnc[7],
                'assigned_user_id': rnc[8],
                'created_at': rnc[9],
                'updated_at': rnc[10],
                'finalized_at': rnc[11],
                'user_name': rnc[12],
                'user_department': rnc[13] or 'N/A',
                'assigned_user_name': rnc[14],
                'department': rnc[13] or 'N/A',
                'setor': rnc[13] or 'N/A',
                'is_creator': (current_user_id == rnc[7]),
                'is_assigned': (current_user_id == rnc[8])  # Novo campo para identificar se está atribuído
            }
            for rnc in rncs
        ]
        
        result = {
            'success': True,
            'rncs': formatted_rncs,
            'tab': tab
        }
        
        logger.info(f"📊 Resultado final para {tab}: {len(formatted_rncs)} RNCs serão retornados")
        
        # Cache moderado - 2 minutos para balancear performance e atualização
        cache_query(cache_key, result, ttl=120)
        
        # Retornar com headers otimizados
        response = jsonify(result)
        response.headers['Cache-Control'] = 'public, max-age=120' if not force_refresh else 'no-cache'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
        
    except Exception as e:
        logger.error(f"Erro ao listar RNCs: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500
    finally:
        if conn:
            return_db_connection(conn)

@app.route('/api/rnc/get/<int:rnc_id>', methods=['GET'])
def api_get_rnc(rnc_id):
    """Retorna os dados completos de uma RNC para visualização/edição."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info(rncs)')
        columns = [row[1] for row in cursor.fetchall()]
        cursor.execute('SELECT * FROM rncs WHERE id = ?', (rnc_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return jsonify({'success': False, 'message': 'RNC não encontrada'}), 404
        rnc_dict = dict(zip(columns, row))
        # Normalizar checkboxes para booleano
        for key in rnc_dict:
            if key.startswith('disposition_') or key.startswith('inspection_'):
                rnc_dict[key] = bool(rnc_dict[key])
        return jsonify({'success': True, 'rnc': rnc_dict})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/rnc/<int:rnc_id>')
def view_rnc(rnc_id):
    """Visualizar RNC específico"""
    if 'user_id' not in session:
        return redirect('/')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar RNC com informações do usuário, dados de disposição/inspeção e assinaturas
        cursor.execute('''
            SELECT r.*, u.name as user_name, au.name as assigned_user_name
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            LEFT JOIN users au ON r.assigned_user_id = au.id
            WHERE r.id = ?
        ''', (rnc_id,))
        
        rnc_data = cursor.fetchone()
        conn.close()
        
        if not rnc_data:
            return render_template('error.html', message='RNC não encontrado')
        
        # Verificar se rnc_data é uma tupla/lista antes de acessar índices
        if not isinstance(rnc_data, (tuple, list)):
            logger.error(f"Erro: rnc_data não é uma tupla/lista: {type(rnc_data)} - {rnc_data}")
            return render_template('error.html', message='Erro interno do sistema')
        
        # Verificar permissão de acesso
        is_creator = (str(rnc_data[8]) == str(session['user_id']))  # user_id está na posição 8
        is_finalized = (rnc_data[7] == 'Finalizado')  # status está na posição 7
        
        logger.info(f"Verificando acesso do usuário {session['user_id']} à RNC {rnc_id}")
        logger.info(f"É criador: {is_creator}, Está finalizado: {is_finalized}")
        
        if not can_user_access_rnc(session['user_id'], rnc_id):
            logger.warning(f"Acesso negado para usuário {session['user_id']} à RNC {rnc_id}")
            return render_template('error.html', message='Acesso negado')
        
        # Converter para dicionário segundo a ordem real das colunas da tabela 'rncs'
        # Consultamos PRAGMA para garantir alinhamento (inclui 'price' e assinaturas na posição correta)
        try:
            conn_cols = sqlite3.connect(DB_PATH)
            cur_cols = conn_cols.cursor()
            cur_cols.execute('PRAGMA table_info(rncs)')
            base_columns = [row[1] for row in cur_cols.fetchall()]
            conn_cols.close()
        except Exception:
            base_columns = [
                'id','rnc_number','title','description','equipment','client','priority','status','user_id','assigned_user_id',
                'is_deleted','deleted_at','finalized_at','created_at','updated_at','disposition_usar','disposition_retrabalhar',
                'disposition_rejeitar','disposition_sucata','disposition_devolver_estoque','disposition_devolver_fornecedor',
                'inspection_aprovado','inspection_reprovado','inspection_ver_rnc','signature_inspection_date','signature_engineering_date',
                'signature_inspection2_date','signature_inspection_name','signature_engineering_name','signature_inspection2_name','price'
            ]
        columns = base_columns + ['user_name', 'assigned_user_name']
        
        # Ajustar o número de colunas baseado na estrutura atual
        if len(rnc_data) < len(columns):
            # Adicionar valores padrão para colunas que podem não existir
            rnc_data = list(rnc_data) + [None] * (len(columns) - len(rnc_data))
        
        rnc_dict = dict(zip(columns, rnc_data))

        # Extrair campos rotulados do description (provenientes do TXT)
        def parse_label_map(text: str):
            if not text:
                return {}
            mapping = {}
            lines = [ln.strip() for ln in str(text).split('\n') if ln.strip()]
            for ln in lines:
                if ':' in ln:
                    parts = ln.split(':', 1)
                    if len(parts) == 2:
                        label = parts[0].strip()
                        val = parts[1].strip()
                        normalized_label = label.lower().replace(' ', '').replace('ã', 'a').replace('ç', 'c')
                        if 'desenho' in normalized_label:
                            mapping['Desenho'] = val
                        elif 'mp' in normalized_label:
                            mapping['MP'] = val
                        elif 'revisao' in normalized_label or 'revisão' in normalized_label:
                            mapping['Revisão'] = val
                        elif 'cv' in normalized_label:
                            mapping['CV'] = val
                        elif 'pos' in normalized_label:
                            mapping['POS'] = val
                        elif 'conjunto' in normalized_label:
                            mapping['Conjunto'] = val
                        elif 'modelo' in normalized_label:
                            mapping['Modelo'] = val
                        elif 'quantidade' in normalized_label:
                            mapping['Quantidade'] = val
                        elif 'area' in normalized_label and 'responsavel' in normalized_label:
                            mapping['Área responsável'] = val
                        elif 'descricao' in normalized_label and 'rnc' in normalized_label:
                            mapping['Descrição da RNC'] = val
                        elif 'instrucao' in normalized_label and 'retrabalho' in normalized_label:
                            mapping['Instrução para retrabalho'] = val
                        elif 'valor' in normalized_label:
                            mapping['Valor'] = val
                        else:
                            mapping[label] = val
            return mapping

        txt_fields = parse_label_map(rnc_dict.get('description') or '')
        
        # Verificar se o usuário é o criador do RNC
        is_creator = (session['user_id'] == rnc_data[8])  # user_id do RNC
        
        # Nova visualização completa, preservando estilo das abas do formulário
        return render_template('view_rnc_full.html', rnc=rnc_dict, is_creator=is_creator, txt_fields=txt_fields)
        
    except Exception as e:
        logger.error(f"Erro ao visualizar RNC {rnc_id}: {e}")
        return render_template('error.html', message='Erro interno do sistema')

@app.route('/rnc/<int:rnc_id>/reply', methods=['GET'])
def reply_rnc(rnc_id):
    """Abrir modo Responder (edição simplificada) para a RNC.

    - Permite criador, admin ou quem tenha 'reply_rncs'
    - Reaproveita o formulário de edição, sinalizando is_reply=True (UI pode ajustar rótulos)
    """
    if 'user_id' not in session:
        return redirect('/')

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.name as user_name, au.name as assigned_user_name
              FROM rncs r
              LEFT JOIN users u ON r.user_id = u.id
              LEFT JOIN users au ON r.assigned_user_id = au.id
             WHERE r.id = ?
        ''', (rnc_id,))
        rnc_data = cursor.fetchone()
        conn.close()

        if not rnc_data:
            return render_template('error.html', message='RNC não encontrado')

        # Verificar permissão para responder
        owner_id = rnc_data[8]  # user_id
        is_creator = str(session['user_id']) == str(owner_id)
        is_admin = has_permission(session['user_id'], 'admin_access')
        can_reply = has_permission(session['user_id'], 'reply_rncs')
        if not (is_creator or is_admin or can_reply):
            return render_template('error.html', message='Acesso negado: você não tem permissão para responder este RNC')

        # Mapear colunas dinamicamente conforme a estrutura real
        try:
            conn_cols = sqlite3.connect(DB_PATH)
            cur_cols = conn_cols.cursor()
            cur_cols.execute('PRAGMA table_info(rncs)')
            base_columns = [row[1] for row in cur_cols.fetchall()]
            conn_cols.close()
        except Exception:
            base_columns = [
                'id','rnc_number','title','description','equipment','client','priority','status','user_id','assigned_user_id',
                'is_deleted','deleted_at','finalized_at','created_at','updated_at','disposition_usar','disposition_retrabalhar',
                'disposition_rejeitar','disposition_sucata','disposition_devolver_estoque','disposition_devolver_fornecedor',
                'inspection_aprovado','inspection_reprovado','inspection_ver_rnc','signature_inspection_date','signature_engineering_date',
                'signature_inspection2_date','signature_inspection_name','signature_engineering_name','signature_inspection2_name','price'
            ]
        columns = base_columns + ['user_name', 'assigned_user_name']

        if len(rnc_data) < len(columns):
            rnc_data = list(rnc_data) + [None] * (len(columns) - len(rnc_data))

        rnc_dict = dict(zip(columns, rnc_data))

        # Sinalizar modo de resposta para o template (pode ajustar labels e lógica)
        return render_template('edit_rnc_form.html', rnc=rnc_dict, is_editing=True, is_reply=True)
    except Exception as e:
        logger.error(f"Erro ao abrir modo Responder para RNC {rnc_id}: {e}")
        return render_template('error.html', message='Erro interno do sistema')

@app.route('/rnc/<int:rnc_id>/print')
def print_rnc(rnc_id):
    """Página de impressão do RNC com template idêntico à visualização"""
    if 'user_id' not in session:
        return redirect('/')
    
    try:
        # Usar função segura para buscar dados do RNC
        rnc_data, error_message = get_rnc_data_safe(rnc_id)
        
        if rnc_data is None:
            logger.error(f"Erro ao buscar RNC {rnc_id}: {error_message}")
            return render_template('error.html', message=error_message)
        
        # Reexecutar a consulta para capturar os nomes das colunas e mapear corretamente,
        # evitando erros de índice quando novas colunas são adicionadas (ex.: price)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.name as user_name, au.name as assigned_user_name
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            LEFT JOIN users au ON r.assigned_user_id = au.id
            WHERE r.id = ?
        ''', (rnc_id,))
        row = cursor.fetchone()
        columns = [d[0] for d in cursor.description]
        conn.close()

        rnc_dict = dict(zip(columns, row)) if row else {}
        # Normalizar datas para string simples (evita .strftime no template)
        for date_key in ['created_at', 'updated_at', 'finalized_at']:
            if isinstance(rnc_dict.get(date_key), (tuple, list)):
                rnc_dict[date_key] = rnc_dict.get(date_key)[0]

        # Garantias de campos esperados pelo template
        if 'price' not in rnc_dict:
            rnc_dict['price'] = 0
        if 'user_name' not in rnc_dict:
            rnc_dict['user_name'] = 'Sistema'
        
        # Extrair campos rotulados do description (provenientes do TXT)
        def parse_label_map(text: str):
            if not text:
                return {}
            mapping = {}
            lines = [ln.strip() for ln in str(text).split('\n') if ln.strip()]
            for ln in lines:
                if ':' in ln:
                    parts = ln.split(':', 1)
                    if len(parts) == 2:
                        label = parts[0].strip()
                        val = parts[1].strip()
                        normalized_label = label.lower().replace(' ', '').replace('ã', 'a').replace('ç', 'c')
                        if 'desenho' in normalized_label:
                            mapping['Desenho'] = val
                        elif 'mp' in normalized_label:
                            mapping['MP'] = val
                        elif 'revisao' in normalized_label or 'revisão' in normalized_label:
                            mapping['Revisão'] = val
                        elif 'cv' in normalized_label:
                            mapping['CV'] = val
                        elif 'pos' in normalized_label:
                            mapping['POS'] = val
                        elif 'conjunto' in normalized_label:
                            mapping['Conjunto'] = val
                        elif 'modelo' in normalized_label:
                            mapping['Modelo'] = val
                        elif 'quantidade' in normalized_label:
                            mapping['Quantidade'] = val
                        elif 'area' in normalized_label and 'responsavel' in normalized_label:
                            mapping['Área responsável'] = val
                        elif 'descricao' in normalized_label and 'rnc' in normalized_label:
                            mapping['Descrição da RNC'] = val
                        elif 'instrucao' in normalized_label and 'retrabalho' in normalized_label:
                            mapping['Instrução para retrabalho'] = val
                        elif 'valor' in normalized_label:
                            mapping['Valor'] = val
                        else:
                            mapping[label] = val
            return mapping
        
        # Parse dos campos de texto importados
        txt_fields = parse_label_map(rnc_dict.get('description') or '')
        
        return render_template('view_rnc_print.html', rnc=rnc_dict, txt_fields=txt_fields)
        
    except Exception as e:
        logger.error(f"Erro ao gerar página de impressão para RNC {rnc_id}: {e}")
        return render_template('error.html', message='Erro interno do sistema')

@app.route('/rnc/<int:rnc_id>/pdf-generator')
def pdf_generator(rnc_id):
    """Gerador de PDF com múltiplas opções"""
    if 'user_id' not in session:
        return redirect('/')
    
    try:
        logger.info(f"Tentando acessar gerador de PDF para RNC {rnc_id} para usuário {session['user_id']}")
        
        # Usar função segura para buscar dados do RNC
        rnc_data, error_message = get_rnc_data_safe(rnc_id)
        
        if rnc_data is None:
            logger.error(f"Erro ao buscar RNC {rnc_id}: {error_message}")
            return render_template('error.html', message=error_message)
        
        logger.info(f"RNC {rnc_id} encontrado com {len(rnc_data)} colunas")
        
        # Verificar permissão de acesso - usar índice correto para user_id
        user_id_index = 8  # user_id está na posição 8
        
        # Verificação adicional de segurança
        try:
            if len(rnc_data) <= user_id_index:
                logger.error(f"RNC {rnc_id} não tem dados suficientes: {len(rnc_data)} colunas")
                return render_template('error.html', message='Dados do RNC incompletos')
            
            user_id_from_rnc = rnc_data[user_id_index]
            logger.info(f"User ID do RNC: {user_id_from_rnc}")
            logger.info(f"User ID da sessão: {session['user_id']}")
            
            # Verificar se o usuário tem permissão para ver todos os RNCs ou se é o criador
            user_has_permission = has_permission(session['user_id'], 'view_all_rncs')
            is_creator = (user_id_from_rnc == session['user_id'])
            
            logger.info(f"Usuário tem permissão para ver todos: {user_has_permission}")
            logger.info(f"Usuário é criador: {is_creator}")
            
            if not user_has_permission and not is_creator:
                logger.warning(f"Usuário {session['user_id']} tentou acessar RNC {rnc_id} sem permissão")
                return render_template('error.html', message='Acesso negado')
                
        except Exception as access_error:
            logger.error(f"Erro ao verificar permissões para RNC {rnc_id}: {access_error}")
            return render_template('error.html', message='Erro ao verificar permissões')
        
        # Converter para dicionário incluindo os novos campos e assinaturas
        columns = [
            'id', 'rnc_number', 'title', 'description', 'equipment', 'client', 
            'priority', 'status', 'user_id', 'created_at', 'updated_at', 
            'assigned_user_id', 'disposition_usar', 'disposition_retrabalhar', 
            'disposition_rejeitar', 'disposition_sucata', 'disposition_devolver_estoque', 
            'disposition_devolver_fornecedor', 'inspection_aprovado', 'inspection_reprovado', 
            'inspection_ver_rnc', 'signature_inspection_date', 'signature_engineering_date', 
            'signature_inspection2_date', 'signature_inspection_name', 'signature_engineering_name', 
            'signature_inspection2_name', 'is_deleted', 'deleted_at', 'finalized_at',
            'user_name', 'assigned_user_name'
        ]
        
        # Ajustar o número de colunas baseado na estrutura atual
        if len(rnc_data) < len(columns):
            logger.info(f"Ajustando RNC {rnc_id}: {len(rnc_data)} colunas para {len(columns)}")
            # Adicionar valores padrão para colunas que podem não existir
            rnc_data = list(rnc_data) + [None] * (len(columns) - len(rnc_data))
        
        rnc_dict = dict(zip(columns, rnc_data))
        
        logger.info(f"RNC {rnc_id} preparado para gerador de PDF com sucesso")
        
        try:
            return render_template('view_rnc_pdf_js.html', rnc=rnc_dict)
        except Exception as template_error:
            logger.error(f"Erro ao renderizar template para RNC {rnc_id}: {template_error}")
            import traceback
            logger.error(f"Traceback do template: {traceback.format_exc()}")
            return render_template('error.html', message='Erro ao gerar página')
        
    except Exception as e:
        logger.error(f"Erro ao acessar gerador de PDF para RNC {rnc_id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return render_template('error.html', message='Erro interno do sistema')

@app.route('/rnc/<int:rnc_id>/edit', methods=['GET', 'POST'])
def edit_rnc(rnc_id):
    """Editar RNC existente - Usa o mesmo template de criação"""
    if 'user_id' not in session:
        return redirect('/')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar RNC com assinaturas
        cursor.execute('''
            SELECT r.*, u.name as user_name, au.name as assigned_user_name
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            LEFT JOIN users au ON r.assigned_user_id = au.id
            WHERE r.id = ?
        ''', (rnc_id,))
        
        rnc_data = cursor.fetchone()
        conn.close()
                
        if not rnc_data:
            return render_template('error.html', message='RNC não encontrado')
        
        # Verificar se rnc_data é uma tupla/lista antes de acessar índices
        if not isinstance(rnc_data, (tuple, list)):
            logger.error(f"Erro: rnc_data não é uma tupla/lista: {type(rnc_data)} - {rnc_data}")
            return render_template('error.html', message='Erro interno do sistema')
        
        # Verificar permissão de edição
        user_is_creator = rnc_data[8] == session['user_id']
        can_edit_all = has_permission(session['user_id'], 'edit_all_rncs')
        can_edit_own = has_permission(session['user_id'], 'edit_own_rnc')
        
        if not (can_edit_all or (can_edit_own and user_is_creator)):
            return render_template('error.html', message='Acesso negado: você não tem permissão para editar este RNC')
        
        # Mapear colunas dinamicamente conforme a estrutura real da tabela (inclui price e demais campos)
        try:
            conn_cols = sqlite3.connect(DB_PATH)
            cur_cols = conn_cols.cursor()
            cur_cols.execute('PRAGMA table_info(rncs)')
            base_columns = [row[1] for row in cur_cols.fetchall()]
            conn_cols.close()
        except Exception:
            # Fallback com conjunto amplo conhecido
            base_columns = [
                'id','rnc_number','title','description','equipment','client','priority','status','user_id','assigned_user_id',
                'is_deleted','deleted_at','finalized_at','created_at','updated_at','disposition_usar','disposition_retrabalhar',
                'disposition_rejeitar','disposition_sucata','disposition_devolver_estoque','disposition_devolver_fornecedor',
                'inspection_aprovado','inspection_reprovado','inspection_ver_rnc','signature_inspection_date','signature_engineering_date',
                'signature_inspection2_date','signature_inspection_name','signature_engineering_name','signature_inspection2_name','price'
            ]
        columns = base_columns + ['user_name', 'assigned_user_name']

        # Ajustar o tamanho para evitar perdas quando a estrutura tiver mais/menos colunas
        if len(rnc_data) < len(columns):
            rnc_data = list(rnc_data) + [None] * (len(columns) - len(rnc_data))
        
        rnc_dict = dict(zip(columns, rnc_data))
        
        # Retornar o mesmo template de criação, mas com dados preenchidos
        return render_template('edit_rnc_form.html', rnc=rnc_dict, is_editing=True)
        
    except Exception as e:
        logger.error(f"Erro ao editar RNC {rnc_id}: {e}")
        return render_template('error.html', message='Erro interno do sistema')
@app.route('/api/rnc/<int:rnc_id>/update', methods=['PUT'])
def update_rnc_api(rnc_id):
    """API para atualizar RNC"""
    logger.info(f"Iniciando atualização da RNC {rnc_id}")
    
    if 'user_id' not in session:
        logger.warning("Tentativa de atualização sem autenticação")
        return jsonify({
            'success': False,
            'message': 'Usuário não autenticado'
        }), 401
    
    try:
        # Verificar se RNC existe e capturar estado atual com nomes de colunas
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rncs WHERE id = ?', (rnc_id,))
        rnc_data = cursor.fetchone()
        
        if not rnc_data:
            return jsonify({
                'success': False,
                'message': 'RNC não encontrado'
            }), 404
        
        # Verificar se rnc_data é uma tupla/lista antes de acessar índices
        if not isinstance(rnc_data, (tuple, list)):
            logger.error(f"Erro: rnc_data não é uma tupla/lista: {type(rnc_data)} - {rnc_data}")
            return jsonify({
                'success': False,
                'message': 'Erro interno do sistema'
            }), 500
        
        # Verificar permissão de edição
        user_is_creator = str(rnc_data[8]) == str(session['user_id'])  # rnc_data[8] é user_id
        can_edit_all = has_permission(session['user_id'], 'edit_all_rncs')
        can_edit_own = has_permission(session['user_id'], 'edit_own_rnc')
        has_admin = has_permission(session['user_id'], 'admin_access')
        department_match = False
        
        # Verificar se tem permissão para ver todos os departamentos
        if has_permission(session['user_id'], 'view_all_departments_rncs'):
            department_match = True
        # Verificar se é RNC do departamento da engenharia
        else:
            cursor.execute('SELECT department FROM rncs WHERE id = ?', (rnc_id,))
            rnc_dept = cursor.fetchone()
            if rnc_dept and rnc_dept[0] == 'Engenharia' and has_permission(session['user_id'], 'view_engineering_rncs'):
                department_match = True
        
        logger.info(f"Verificação de permissão para edição RNC {rnc_id}:")
        logger.info(f"  Usuário: {session['user_id']} ({session.get('user_name', 'N/A')})")
        logger.info(f"  Criador do RNC: {rnc_data[8]}")
        logger.info(f"  É criador: {user_is_creator}")
        logger.info(f"  Pode editar todos: {can_edit_all}")
        logger.info(f"  Pode editar próprios: {can_edit_own}")
        logger.info(f"  É admin: {has_admin}")
        logger.info(f"  Match departamento: {department_match}")
        
        # Permitir também usuários com permissão de resposta (reply_rncs)
        can_reply = has_permission(session['user_id'], 'reply_rncs')
        if not (can_edit_all or (can_edit_own and user_is_creator) or has_admin or department_match or can_reply):
            logger.warning(f"Acesso negado para edição do RNC {rnc_id}")
            return jsonify({
                'success': False,
                'message': 'Acesso negado: você não tem permissão para editar este RNC'
            }), 403
        
        data = request.get_json() or {}
        # Mapear colunas para dict atual
        try:
            cur_cols = conn.cursor()
            cur_cols.execute('PRAGMA table_info(rncs)')
            col_names = [row[1] for row in cur_cols.fetchall()]
        except Exception:
            col_names = []
        current = {}
        try:
            if col_names and isinstance(rnc_data, (tuple, list)):
                current = dict(zip(col_names, rnc_data))
        except Exception:
            current = {}

        def get_bool(key):
            v = data.get(key, current.get(key))
            if isinstance(v, bool):
                return 1 if v else 0
            try:
                return 1 if str(v).strip().lower() in ('1','true','on','yes','y') else 0
            except Exception:
                return 0
        logger.info(f"Dados recebidos para atualização do RNC {rnc_id}: {data}")
        
        # Processar assinaturas - permitir atualização se não estiver travada
        cursor.execute('SELECT signature_inspection_name, signature_engineering_name, signature_inspection2_name FROM rncs WHERE id = ?', (rnc_id,))
        current_sign = cursor.fetchone() or (None, None, None)
        
        # Log para debug
        logger.info(f"🔍 Assinaturas atuais: {current_sign}")
        logger.info(f"🔍 Assinaturas recebidas: {data.get('signature_inspection_name')}, {data.get('signature_engineering_name')}, {data.get('signature_inspection2_name')}")
        
        # Usar novas assinaturas se fornecidas, senão manter as atuais
        new_sign = (
            data.get('signature_inspection_name', current_sign[0] or ''),
            data.get('signature_engineering_name', current_sign[1] or ''),
            data.get('signature_inspection2_name', current_sign[2] or '')
        )
        
        logger.info(f"🔍 Assinaturas finais para salvar: {new_sign}")
        if not any(s and s != 'NOME' for s in new_sign):
            return jsonify({'success': False, 'message': 'É obrigatório preencher pelo menos uma assinatura!'}), 400
        
        logger.info(f"Executando UPDATE para RNC {rnc_id}")
        # Preparar campos adicionais (disposição/inspeção + seções textuais) com fallback ao valor atual
        disposition_usar = get_bool('disposition_usar')
        disposition_retrabalhar = get_bool('disposition_retrabalhar')
        disposition_rejeitar = get_bool('disposition_rejeitar')
        disposition_sucata = get_bool('disposition_sucata')
        disposition_devolver_estoque = get_bool('disposition_devolver_estoque')
        disposition_devolver_fornecedor = get_bool('disposition_devolver_fornecedor')
        inspection_aprovado = get_bool('inspection_aprovado')
        inspection_reprovado = get_bool('inspection_reprovado')
        inspection_ver_rnc = data.get('inspection_ver_rnc', current.get('inspection_ver_rnc', ''))
        instruction_retrabalho = data.get('instruction_retrabalho', current.get('instruction_retrabalho', ''))
        cause_rnc = data.get('cause_rnc', current.get('cause_rnc', ''))
        action_rnc = data.get('action_rnc', current.get('action_rnc', ''))

        cursor.execute('''
            UPDATE rncs 
            SET title = ?, description = ?, equipment = ?, client = ?, 
                priority = ?, status = ?, updated_at = CURRENT_TIMESTAMP,
                signature_inspection_name = ?, signature_engineering_name = ?, signature_inspection2_name = ?,
                signature_inspection_date = COALESCE(NULLIF(?, ''), signature_inspection_date),
                signature_engineering_date = COALESCE(NULLIF(?, ''), signature_engineering_date),
                signature_inspection2_date = COALESCE(NULLIF(?, ''), signature_inspection2_date),
                disposition_usar = ?, disposition_retrabalhar = ?, disposition_rejeitar = ?, disposition_sucata = ?,
                disposition_devolver_estoque = ?, disposition_devolver_fornecedor = ?,
                inspection_aprovado = ?, inspection_reprovado = ?, inspection_ver_rnc = ?,
                instruction_retrabalho = ?, cause_rnc = ?, action_rnc = ?
            WHERE id = ?
        ''', (
            data.get('title', current.get('title','')),
            data.get('description', current.get('description','')),
            data.get('equipment', current.get('equipment','')),
            data.get('client', current.get('client','')),
            data.get('priority', current.get('priority','Média')),
            data.get('status', current.get('status','Pendente')),
            new_sign[0],
            new_sign[1],
            new_sign[2],
            data.get('signature_inspection_date',''),
            data.get('signature_engineering_date',''),
            data.get('signature_inspection2_date',''),
            disposition_usar,
            disposition_retrabalhar,
            disposition_rejeitar,
            disposition_sucata,
            disposition_devolver_estoque,
            disposition_devolver_fornecedor,
            inspection_aprovado,
            inspection_reprovado,
            inspection_ver_rnc,
            instruction_retrabalho,
            cause_rnc,
            action_rnc,
            rnc_id
        ))
        
        affected_rows = cursor.rowcount
        logger.info(f"UPDATE executado. Linhas afetadas: {affected_rows}")
        
        conn.commit()
        conn.close()
        
        # Limpar cache para todos os usuários e invalidar caches do dashboard
        clear_rnc_cache()
        try:
            keys_to_remove = []
            with cache_lock:
                for key in list(query_cache.keys()):
                    if key.startswith('rncs_list_') or key.startswith('charts_'):
                        keys_to_remove.append(key)
                for key in keys_to_remove:
                    del query_cache[key]
        except Exception:
            pass
        logger.info(f"Cache limpo após atualização do RNC {rnc_id}")
        
        return jsonify({
            'success': True,
            'message': 'RNC atualizado com sucesso!',
            'affected_rows': affected_rows
        })
        
    except Exception as e:
        logger.error(f"Erro ao atualizar RNC {rnc_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500



@app.route('/api/rnc/<int:rnc_id>/finalize', methods=['POST'])
def finalize_rnc(rnc_id):
    """API para finalizar RNC"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se o RNC existe e não está deletado
        cursor.execute('SELECT * FROM rncs WHERE id = ? AND is_deleted = 0', (rnc_id,))
        rnc = cursor.fetchone()
        
        if not rnc:
            conn.close()
            return jsonify({'success': False, 'message': 'RNC não encontrado'}), 404
        
        # Verificar se rnc é uma tupla/lista antes de acessar índices
        if not isinstance(rnc, (tuple, list)):
            logger.error(f"Erro: rnc não é uma tupla/lista: {type(rnc)} - {rnc}")
            conn.close()
            return jsonify({'success': False, 'message': 'Erro interno do sistema'}), 500
        
        # Verificar permissões
        user_id = session['user_id']
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        user_role = user[0]
        rnc_creator_id = rnc[8]  # user_id do RNC (ajustado para nova estrutura)
        is_creator = (user_id == rnc_creator_id)
        
        # Apenas o criador ou admin pode finalizar o RNC
        if not is_creator and user_role != 'admin':
            conn.close()
            return jsonify({'success': False, 'message': 'Apenas o criador do RNC pode finalizá-lo'}), 403
        
        # Atualizar status para Finalizado com timestamp
        cursor.execute('''
            UPDATE rncs 
            SET status = 'Finalizado', finalized_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (rnc_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Erro ao finalizar RNC'}), 500
        
        conn.commit()
        conn.close()
        
        # Limpar cache de RNCs para todos os usuários
        clear_rnc_cache()
        
        return jsonify({
            'success': True,
            'message': 'RNC finalizado com sucesso!'
        })
        
    except Exception as e:
        logger.error(f"Erro ao finalizar RNC: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/rnc/<int:rnc_id>/reply', methods=['POST'])
def reply_rnc_api(rnc_id):
    """Reabrir/reenviar uma RNC para tratamento (status volta para 'Pendente').

    Regras:
    - Requer sessão ativa
    - Permitido ao criador, admin ou quem tenha permissão 'reply_rncs'
    - Define status='Pendente', finalized_at=NULL, updated_at=CURRENT_TIMESTAMP
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Buscar RNC
        cursor.execute('SELECT id, user_id, assigned_user_id, status FROM rncs WHERE id = ? AND is_deleted = 0', (rnc_id,))
        rnc = cursor.fetchone()
        if not rnc:
            conn.close()
            return jsonify({'success': False, 'message': 'RNC não encontrada'}), 404

        rnc_creator_id = rnc[1]
        user_id = session['user_id']
        is_creator = str(user_id) == str(rnc_creator_id)
        is_admin = has_permission(user_id, 'admin_access')
        can_reply = has_permission(user_id, 'reply_rncs')

        if not (is_creator or is_admin or can_reply):
            conn.close()
            return jsonify({'success': False, 'message': 'Sem permissão para responder esta RNC'}), 403

        # Reabrir RNC
        cursor.execute('''
            UPDATE rncs
               SET status = 'Pendente',
                   finalized_at = NULL,
                   updated_at = CURRENT_TIMESTAMP,
                   assigned_user_id = user_id -- atribui novamente ao criador
             WHERE id = ?
        ''', (rnc_id,))

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Nenhuma alteração realizada'}), 400

        conn.commit()
        conn.close()

        # Limpar cache
        clear_rnc_cache()

        return jsonify({'success': True, 'message': 'RNC reenviada com sucesso'})
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/debug/session')
def api_debug_session():
    data = {k: session.get(k) for k in ['user_id','user_name','user_email','user_department','user_role']}
    data['has_session'] = 'user_id' in session
    return jsonify({'success': True, 'session': data})

@app.route('/api/private-chat/messages/<int:contact_id>')
def get_private_messages(contact_id):
    """API para obter mensagens privadas com um contato específico"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        limit = request.args.get('limit', type=int)
        user_id = session['user_id']
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        query = '''
            SELECT pm.id, pm.sender_id, pm.recipient_id, pm.message, pm.message_type,
                   pm.is_read, pm.created_at, u.name as user_name, u.department
            FROM private_messages pm
            JOIN users u ON pm.sender_id = u.id
            WHERE (pm.sender_id = ? AND pm.recipient_id = ?) 
               OR (pm.sender_id = ? AND pm.recipient_id = ?)
            ORDER BY pm.created_at DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
            
        cursor.execute(query, (user_id, contact_id, contact_id, user_id))
        messages = cursor.fetchall()
        conn.close()
        
        # Converter para formato JSON
        messages_list = []
        for msg in messages:
            messages_list.append({
                'id': msg[0],
                'sender_id': msg[1],
                'recipient_id': msg[2],
                'message': msg[3],
                'message_type': msg[4],
                'is_read': msg[5],
                'created_at': msg[6],
                'user_name': msg[7],
                'department': msg[8],
                'user_id': msg[1]  # Para compatibilidade
            })
        
        # Inverter ordem se não for limit=1 (para mostrar mais antigas primeiro no chat)
        if not limit or limit > 1:
            messages_list.reverse()
        
        return jsonify({'success': True, 'messages': messages_list})
        
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens privadas: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/private-chat/unread-count/<int:contact_id>')
def get_unread_count(contact_id):
    """API para obter contagem de mensagens não lidas de um contato"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        user_id = session['user_id']
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM private_messages
            WHERE sender_id = ? AND recipient_id = ? AND is_read = 0
        ''', (contact_id, user_id))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({'success': True, 'count': count})
        
    except Exception as e:
        logger.error(f"Erro ao contar mensagens não lidas: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache_api():
    """API para limpar cache do servidor"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        # LIMPEZA COMPLETA E FORÇADA DO CACHE
        user_id = session['user_id']
        is_admin = has_permission(user_id, 'admin_access')
        
        # Limpar TODOS os caches independentemente de permissão
        with cache_lock:
            cache_count = len(query_cache)
            query_cache.clear()  # Limpar TUDO
            logger.info(f"🗑️ LIMPEZA FORÇADA: {cache_count} entradas de cache removidas")
        
        # Também limpar usando a função específica
        clear_rnc_cache()
        
        if is_admin:
            logger.info(f"Admin {user_id} executou limpeza completa do cache")
            message = f"Cache completo limpo com sucesso ({cache_count} entradas removidas)"
        else:
            logger.info(f"Usuário {user_id} executou limpeza de cache")
            message = f"Cache limpo com sucesso ({cache_count} entradas removidas)"
        
        return jsonify({
            'success': True,
            'message': message,
            'cache_cleared_count': cache_count
        })
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/debug/rnc-count')
def debug_rnc_count():
    """Rota de debug para verificar contagem real de RNCs"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Contar todos os RNCs
        cursor.execute('SELECT COUNT(*) FROM rncs')
        total = cursor.fetchone()[0]
        
        # Contar finalizados
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE status = "Finalizado"')
        finalizados = cursor.fetchone()[0]
        
        # Contar finalizados sem deletados
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE (is_deleted = 0 OR is_deleted IS NULL) AND status = "Finalizado"')
        finalizados_ativos = cursor.fetchone()[0]
        
        # Contar ativos
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE (is_deleted = 0 OR is_deleted IS NULL) AND status != "Finalizado"')
        ativos = cursor.fetchone()[0]
        
        return_db_connection(conn)
        
        return jsonify({
            'success': True,
            'counts': {
                'total': total,
                'finalizados': finalizados,
                'finalizados_ativos': finalizados_ativos,
                'ativos': ativos
            }
        })
        
    except Exception as e:
        logger.error(f"Erro no debug: {e}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@app.route('/api/debug/user-rncs')
def debug_user_rncs():
    """Debug para verificar RNCs do usuário atual"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = session['user_id']
        
        # RNCs criados pelo usuário
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE user_id = ?', (user_id,))
        created_by_user = cursor.fetchone()[0]
        
        # RNCs atribuídos ao usuário
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE assigned_user_id = ?', (user_id,))
        assigned_to_user = cursor.fetchone()[0]
        
        # RNCs ativos (criados OU atribuídos)
        cursor.execute('''SELECT COUNT(*) FROM rncs 
                         WHERE (is_deleted = 0 OR is_deleted IS NULL) 
                         AND status != "Finalizado" 
                         AND (user_id = ? OR assigned_user_id = ?)''', (user_id, user_id))
        active_total = cursor.fetchone()[0]
        
        # RNCs finalizados (criados OU atribuídos)
        cursor.execute('''SELECT COUNT(*) FROM rncs 
                         WHERE (is_deleted = 0 OR is_deleted IS NULL) 
                         AND status = "Finalizado" 
                         AND (user_id = ? OR assigned_user_id = ?)''', (user_id, user_id))
        finalized_total = cursor.fetchone()[0]
        
        # Obter alguns exemplos
        cursor.execute('''SELECT id, rnc_number, title, status, user_id, assigned_user_id 
                         FROM rncs 
                         WHERE (user_id = ? OR assigned_user_id = ?) 
                         ORDER BY id DESC LIMIT 5''', (user_id, user_id))
        examples = cursor.fetchall()
        
        return_db_connection(conn)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'user_name': session.get('user_name', 'N/A'),
            'counts': {
                'created_by_user': created_by_user,
                'assigned_to_user': assigned_to_user,
                'active_total': active_total,
                'finalized_total': finalized_total
            },
            'examples': [
                {
                    'id': ex[0],
                    'rnc_number': ex[1],
                    'title': ex[2],
                    'status': ex[3],
                    'is_creator': ex[4] == user_id,
                    'is_assigned': ex[5] == user_id
                }
                for ex in examples
            ]
        })
        
    except Exception as e:
        logger.error(f"Erro no debug de usuário: {e}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@app.route('/api/debug/user-shares')
def debug_user_shares():
    """Debug para verificar compartilhamentos do usuário atual"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = session['user_id']
        
        # RNCs compartilhadas COM o usuário
        cursor.execute('''
            SELECT rs.rnc_id, r.rnc_number, r.title, r.status, 
                   u.name as shared_by, rs.permission_level, rs.created_at
            FROM rnc_shares rs
            JOIN rncs r ON rs.rnc_id = r.id
            LEFT JOIN users u ON rs.shared_by_user_id = u.id
            WHERE rs.shared_with_user_id = ?
            ORDER BY rs.created_at DESC LIMIT 10
        ''', (user_id,))
        shared_with_user = cursor.fetchall()
        
        # RNCs compartilhadas PELO usuário
        cursor.execute('''
            SELECT rs.rnc_id, r.rnc_number, r.title, r.status, 
                   u.name as shared_with, rs.permission_level, rs.created_at
            FROM rnc_shares rs
            JOIN rncs r ON rs.rnc_id = r.id
            LEFT JOIN users u ON rs.shared_with_user_id = u.id
            WHERE rs.shared_by_user_id = ?
            ORDER BY rs.created_at DESC LIMIT 10
        ''', (user_id,))
        shared_by_user = cursor.fetchall()
        
        # Contar total de compartilhamentos
        cursor.execute('SELECT COUNT(*) FROM rnc_shares WHERE shared_with_user_id = ?', (user_id,))
        total_shared_with = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM rnc_shares WHERE shared_by_user_id = ?', (user_id,))
        total_shared_by = cursor.fetchone()[0]
        
        return_db_connection(conn)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'user_name': session.get('user_name', 'N/A'),
            'totals': {
                'shared_with_me': total_shared_with,
                'shared_by_me': total_shared_by
            },
            'shared_with_me': [
                {
                    'rnc_id': share[0],
                    'rnc_number': share[1],
                    'title': share[2],
                    'status': share[3],
                    'shared_by': share[4],
                    'permission': share[5],
                    'shared_at': share[6]
                }
                for share in shared_with_user
            ],
            'shared_by_me': [
                {
                    'rnc_id': share[0],
                    'rnc_number': share[1],
                    'title': share[2],
                    'status': share[3],
                    'shared_with': share[4],
                    'permission': share[5],
                    'shared_at': share[6]
                }
                for share in shared_by_user
            ]
        })
        
    except Exception as e:
        logger.error(f"Erro no debug de compartilhamentos: {e}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@app.route('/api/debug/rnc-signatures/<int:rnc_id>')
def debug_rnc_signatures(rnc_id):
    """Debug específico para verificar assinaturas de uma RNC"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar todas as colunas de assinatura
        cursor.execute('''
            SELECT id, rnc_number, title,
                   signature_inspection_name, signature_engineering_name, signature_inspection2_name,
                   signature_inspection_date, signature_engineering_date, signature_inspection2_date
            FROM rncs 
            WHERE id = ?
        ''', (rnc_id,))
        
        rnc_data = cursor.fetchone()
        return_db_connection(conn)
        
        if not rnc_data:
            return jsonify({'success': False, 'message': 'RNC não encontrada'}), 404
        
        return jsonify({
            'success': True,
            'rnc_id': rnc_id,
            'rnc_number': rnc_data[1],
            'title': rnc_data[2],
            'signatures': {
                'inspection_name': rnc_data[3],
                'engineering_name': rnc_data[4],
                'inspection2_name': rnc_data[5],
                'inspection_date': rnc_data[6],
                'engineering_date': rnc_data[7],
                'inspection2_date': rnc_data[8]
            },
            'debug_info': {
                'inspection_empty': not rnc_data[3] or rnc_data[3] == 'NOME',
                'engineering_empty': not rnc_data[4] or rnc_data[4] == 'NOME',
                'inspection2_empty': not rnc_data[5] or rnc_data[5] == 'NOME'
            }
        })
        
    except Exception as e:
        logger.error(f"Erro no debug de assinaturas: {e}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@app.route('/api/rnc/<int:rnc_id>/delete', methods=['DELETE'])
def delete_rnc(rnc_id):
    """API para deletar RNC definitivamente (lixeira removida)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se RNC existe
        cursor.execute('SELECT * FROM rncs WHERE id = ?', (rnc_id,))
        rnc = cursor.fetchone()
        
        if not rnc:
            conn.close()
            return jsonify({'success': False, 'message': 'RNC não encontrado'}), 404
        
        # Exclusão definitiva
        cursor.execute('DELETE FROM rncs WHERE id = ?', (rnc_id,))
        
        # Também excluir dados relacionados
        cursor.execute('DELETE FROM rnc_shares WHERE rnc_id = ?', (rnc_id,))
        cursor.execute('DELETE FROM chat_messages WHERE rnc_id = ?', (rnc_id,))
        
        conn.commit()
        conn.close()
        
        # LIMPAR CACHE IMEDIATAMENTE e forçar reload
        with cache_lock:
            # Limpar TODOS os caches relacionados a RNCs
            keys_to_remove = [
                key for key in query_cache.keys()
                if 'rncs_list_' in key or 'rnc_' in key or 'charts_' in key
            ]
            for key in keys_to_remove:
                del query_cache[key]
        
        logger.info(f"RNC {rnc_id} excluído definitivamente por usuário {session['user_id']}")
        
        return jsonify({
            'success': True,
            'message': 'RNC excluído definitivamente.',
            'cache_cleared': True  # Indicar que cache foi limpo
        })
        
    except Exception as e:
        logger.error(f"Erro ao deletar RNC: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/rnc/<int:rnc_id>/share', methods=['POST'])
def share_rnc(rnc_id):
    """Compartilhar RNC com usuários"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        shared_with_user_ids = data.get('shared_with_user_ids', [])
        permission_level = data.get('permission_level', 'view')
        
        # Verificar se usuário pode compartilhar esta RNC
        rnc_data, error_message = get_rnc_data_safe(rnc_id)
        if rnc_data is None:
            return jsonify({'success': False, 'message': error_message}), 404
        
        # Verificar se é o criador ou tem permissão de admin
        user_id_index = 8  # user_id
        if len(rnc_data) <= user_id_index:
            return jsonify({'success': False, 'message': 'Dados do RNC incompletos'}), 400
        
        is_creator = (rnc_data[user_id_index] == session['user_id'])
        has_admin_permission = has_permission(session['user_id'], 'view_all_rncs')
        
        if not is_creator and not has_admin_permission:
            return jsonify({'success': False, 'message': 'Sem permissão para compartilhar esta RNC'}), 403
        
        # Compartilhar com cada usuário
        success_count = 0
        for user_id in shared_with_user_ids:
            if share_rnc_with_user(rnc_id, session['user_id'], user_id, permission_level):
                success_count += 1
        
        if success_count > 0:
            return jsonify({
                'success': True,
                'message': f'RNC compartilhada com {success_count} usuário(s) com sucesso!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao compartilhar RNC'
            }), 500
        
    except Exception as e:
        logger.error(f"Erro ao compartilhar RNC {rnc_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do sistema'
        }), 500

@app.route('/api/rnc/<int:rnc_id>/shared-users', methods=['GET'])
def get_shared_users(rnc_id):
    """Obter usuários com quem a RNC foi compartilhada"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        # Verificar se usuário pode ver esta RNC
        if not can_user_access_rnc(session['user_id'], rnc_id):
            return jsonify({'success': False, 'message': 'Sem permissão para acessar esta RNC'}), 403
        
        shared_users = get_rnc_shared_users(rnc_id)
        
        shared_users_list = []
        for user_data in shared_users:
            shared_users_list.append({
                'user_id': user_data[0],
                'permission_level': user_data[1],
                'name': user_data[2],
                'email': user_data[3]
            })
        
        return jsonify({
            'success': True,
            'shared_users': shared_users_list
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar usuários compartilhados da RNC {rnc_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do sistema'
        }), 500

@app.route('/api/admin/grant-permission', methods=['POST'])
def grant_permission():
    """API para admins concederem permissões a usuários"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    # Verificar se usuário é admin
    if not has_permission(session['user_id'], 'manage_users'):
        return jsonify({'success': False, 'message': 'Sem permissão para gerenciar usuários'}), 403
    
    try:
        data = request.get_json()
        target_user_id = data.get('user_id')
        permission = data.get('permission')
        
        if not target_user_id or not permission:
            return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar permissões atuais do usuário
        cursor.execute('SELECT permissions FROM users WHERE id = ?', (target_user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            conn.close()
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        # Processar permissões atuais
        current_permissions_str = user_data[0] or '[]'
        try:
            # Tentar parsear como JSON
            current_permissions = json.loads(current_permissions_str)
        except json.JSONDecodeError:
            # Se falhar, assumir que é string separada por vírgulas
            if current_permissions_str.strip():
                current_permissions = [p.strip() for p in current_permissions_str.split(',')]
            else:
                current_permissions = []
        
        # Adicionar nova permissão se não existir
        if permission not in current_permissions:
            current_permissions.append(permission)
            permissions_json = json.dumps(current_permissions)
            
            cursor.execute('UPDATE users SET permissions = ? WHERE id = ?', (permissions_json, target_user_id))
            conn.commit()
            conn.close()
            
            logger.info(f"Permissão '{permission}' concedida para usuário {target_user_id}")
            
            return jsonify({
                'success': True,
                'message': f'Permissão "{permission}" concedida com sucesso!'
            })
        else:
            conn.close()
            return jsonify({
                'success': False,
                'message': f'Usuário já possui a permissão "{permission}"'
            }), 400
        
    except Exception as e:
        logger.error(f"Erro ao conceder permissão: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno do sistema: {str(e)}'
        }), 500

@app.route('/api/admin/revoke-permission', methods=['POST'])
def revoke_permission():
    """API para admins removerem permissões de usuários"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    # Verificar se usuário é admin
    if not has_permission(session['user_id'], 'manage_users'):
        return jsonify({'success': False, 'message': 'Sem permissão para gerenciar usuários'}), 403
    
    try:
        data = request.get_json()
        target_user_id = data.get('user_id')
        permission = data.get('permission')
        
        if not target_user_id or not permission:
            return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar permissões atuais do usuário
        cursor.execute('SELECT permissions FROM users WHERE id = ?', (target_user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            conn.close()
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        # Processar permissões atuais
        current_permissions_str = user_data[0] or '[]'
        try:
            # Tentar parsear como JSON
            current_permissions = json.loads(current_permissions_str)
        except json.JSONDecodeError:
            # Se falhar, assumir que é string separada por vírgulas
            if current_permissions_str.strip():
                current_permissions = [p.strip() for p in current_permissions_str.split(',')]
            else:
                current_permissions = []
        
        # Remover permissão se existir
        if permission in current_permissions:
            current_permissions.remove(permission)
            permissions_json = json.dumps(current_permissions)
            
            cursor.execute('UPDATE users SET permissions = ? WHERE id = ?', (permissions_json, target_user_id))
            conn.commit()
            conn.close()
            
            logger.info(f"Permissão '{permission}' removida do usuário {target_user_id}")
            
            return jsonify({
                'success': True,
                'message': f'Permissão "{permission}" removida com sucesso!'
            })
        else:
            conn.close()
            return jsonify({
                'success': False,
                'message': f'Usuário não possui a permissão "{permission}"'
            }), 400
        
    except Exception as e:
        logger.error(f"Erro ao remover permissão: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno do sistema: {str(e)}'
        }), 500

# Rotas de gerenciamento de grupos (apenas para admins)
@app.route('/api/admin/groups', methods=['GET'])
@app.route('/api/groups', methods=['GET'])
def api_get_groups():
    """API para obter todos os grupos.
    Disponível para qualquer usuário autenticado - permite visualizar grupos
    para atribuição/compartilhamento de RNCs independente do departamento."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        groups = get_all_groups()
        groups_list = []
        for group in groups:
            groups_list.append({
                'id': group[0],
                'name': group[1],
                'description': group[2],
                'user_count': group[3]
            })
        
        return jsonify({'success': True, 'groups': groups_list})
    except Exception as e:
        logger.error(f"Erro ao buscar grupos: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do sistema'}), 500

@app.route('/api/admin/groups', methods=['POST'])
def api_create_group():
    """API para criar novo grupo"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    if not has_permission(session['user_id'], 'manage_users'):
        return jsonify({'success': False, 'message': 'Sem permissão para gerenciar grupos'}), 403
    
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return jsonify({'success': False, 'message': 'Nome do grupo é obrigatório'}), 400
        
        group_id = create_group(name, description)
        if group_id:
            return jsonify({
                'success': True,
                'message': f'Grupo "{name}" criado com sucesso!',
                'group_id': group_id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao criar grupo'
            }), 500
    except Exception as e:
        logger.error(f"Erro ao criar grupo: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do sistema'
        }), 500

@app.route('/api/admin/groups/<int:group_id>', methods=['PUT'])
def api_update_group(group_id):
    """API para atualizar grupo"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    if not has_permission(session['user_id'], 'manage_users'):
        return jsonify({'success': False, 'message': 'Sem permissão para gerenciar grupos'}), 403
    
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return jsonify({'success': False, 'message': 'Nome do grupo é obrigatório'}), 400
        
        if update_group(group_id, name, description):
            return jsonify({
                'success': True,
                'message': f'Grupo atualizado com sucesso!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao atualizar grupo'
            }), 500
    except Exception as e:
        logger.error(f"Erro ao atualizar grupo: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do sistema'
        }), 500

@app.route('/api/admin/groups/<int:group_id>', methods=['DELETE'])
def api_delete_group(group_id):
    """API para deletar grupo"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    if not has_permission(session['user_id'], 'manage_users'):
        return jsonify({'success': False, 'message': 'Sem permissão para gerenciar grupos'}), 403
    
    try:
        if delete_group(group_id):
            return jsonify({
                'success': True,
                'message': 'Grupo deletado com sucesso!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao deletar grupo'
            }), 500
    except Exception as e:
        logger.error(f"Erro ao deletar grupo: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do sistema'
        }), 500

@app.route('/api/admin/groups/<int:group_id>/users', methods=['GET'])
def api_get_group_users(group_id):
    """API para obter usuários de um grupo"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        users = get_users_by_group(group_id)
        users_list = []
        for user in users:
            users_list.append({
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'department': user[3],
                'role': user[4]
            })
        
        return jsonify({
            'success': True,
            'users': users_list
        })
    except Exception as e:
        logger.error(f"Erro ao buscar usuários do grupo: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do sistema'
        }), 500

@app.route('/api/admin/groups/suggestions', methods=['GET'])
def api_get_group_suggestions():
    """API para obter sugestões de grupos existentes"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT name FROM groups ORDER BY name')
        groups = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'groups': groups
        })
    except Exception as e:
        logger.error(f"Erro ao buscar sugestões de grupos: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do sistema'
        }), 500

@app.route('/api/admin/users/<int:user_id>/groups', methods=['GET'])
def api_get_user_groups(user_id):
    """API para obter grupos de um usuário específico"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obter grupo principal do usuário
        cursor.execute('''
            SELECT g.id, g.name, g.description 
            FROM groups g 
            JOIN users u ON g.id = u.group_id 
            WHERE u.id = ?
        ''', (user_id,))
        main_group = cursor.fetchone()
        
        # Obter todos os grupos disponíveis
        cursor.execute('SELECT id, name, description FROM groups ORDER BY name')
        all_groups = cursor.fetchall()
        
        conn.close()
        
        groups_list = []
        for group in all_groups:
            groups_list.append({
                'id': group[0],
                'name': group[1],
                'description': group[2],
                'is_main': main_group and main_group[0] == group[0]
            })
        
        return jsonify({
            'success': True,
            'groups': groups_list,
            'main_group': main_group[1] if main_group else None
        })
    except Exception as e:
        logger.error(f"Erro ao buscar grupos do usuário: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do sistema'
        }), 500

@app.route('/api/admin/users/<int:user_id>/add-to-group', methods=['POST'])
def api_add_user_to_group(user_id):
    """API para adicionar usuário a um grupo"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    if not has_permission(session['user_id'], 'manage_users'):
        return jsonify({'success': False, 'message': 'Sem permissão para gerenciar usuários'}), 403
    
    try:
        data = request.get_json()
        group_id = data.get('group_id')
        
        if not group_id:
            return jsonify({'success': False, 'message': 'ID do grupo é obrigatório'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se o grupo existe
        cursor.execute('SELECT name FROM groups WHERE id = ?', (group_id,))
        group = cursor.fetchone()
        
        if not group:
            conn.close()
            return jsonify({'success': False, 'message': 'Grupo não encontrado'}), 404
        
        # Atualizar o grupo do usuário
        cursor.execute('UPDATE users SET group_id = ? WHERE id = ?', (group_id, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Usuário adicionado ao grupo "{group[0]}" com sucesso!'
        })
    except Exception as e:
        logger.error(f"Erro ao adicionar usuário ao grupo: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do sistema'
        }), 500

# ==================== APIs DE PERMISSÕES ====================

@app.route('/api/admin/groups/<int:group_id>/permissions', methods=['GET'])
def api_get_group_permissions(group_id):
    """API para obter permissões de um grupo"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    if not has_permission(session['user_id'], 'admin_access'):
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        permissions = get_group_permissions(group_id)  # lista de tuplas (name, value)
        # Filtrar apenas permissões concedidas (valor truthy)
        granted_permissions = [name for name, value in permissions if value]
        return jsonify({
            'success': True,
            'group_id': group_id,
            'permissions': granted_permissions
        })
    except Exception as e:
        logger.error(f"Erro ao buscar permissões do grupo: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

@app.route('/api/admin/groups/<int:group_id>/permissions', methods=['PUT'])
def api_update_group_permissions(group_id):
    """API para atualizar permissões de um grupo"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    if not has_permission(session['user_id'], 'admin_access'):
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        data = request.get_json() or {}
        raw_permissions = data.get('permissions', [])

        # Aceitar tanto lista (['perm_a', 'perm_b']) quanto dict ({'perm_a': True})
        if isinstance(raw_permissions, list):
            # Validar nomes contra lista global de permissões
            valid_names = {p['name'] for p in get_all_permissions()}
            invalid = [p for p in raw_permissions if p not in valid_names]
            # Ignorar inválidas ao invés de falhar completamente
            if invalid:
                logger.warning(f"Ignorando permissões desconhecidas para grupo {group_id}: {invalid}")
            # Converter somente válidas para dict com valor True
            permissions_dict = {p: True for p in raw_permissions if p in valid_names}
        elif isinstance(raw_permissions, dict):
            # Filtrar por nomes válidos e normalizar valores para boolean
            valid_names = {p['name'] for p in get_all_permissions()}
            permissions_dict = {name: bool(val) for name, val in raw_permissions.items() if name in valid_names}
        else:
            return jsonify({'success': False, 'error': 'Formato de permissões não suportado'}), 400

        if update_group_permissions(group_id, permissions_dict):
            logger.info(f"Permissões atualizadas para grupo {group_id}: {sorted(list(permissions_dict.keys()))}")
            return jsonify({'success': True, 'message': 'Permissões atualizadas com sucesso', 'applied': list(permissions_dict.keys())})
        else:
            return jsonify({'success': False, 'error': 'Erro ao atualizar permissões'}), 500
    except Exception as e:
        logger.error(f"Erro ao atualizar permissões do grupo: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

@app.route('/api/admin/permissions/list', methods=['GET'])
def api_get_all_permissions():
    """API para obter lista de todas as permissões disponíveis"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    if not has_permission(session['user_id'], 'admin_access'):
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        # Limpar qualquer cache de permissões para garantir dados atualizados
        clear_permissions_cache()
        permissions = get_all_permissions()
        logger.info(f"API: Retornando {len(permissions)} permissões atualizadas")
        return jsonify({'success': True, 'permissions': permissions})
    except Exception as e:
        logger.error(f"Erro ao buscar permissões: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

@app.route('/api/user/permissions', methods=['GET'])
def api_get_user_permissions():
    """API para obter permissões do usuário logado"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        permissions = get_user_group_permissions(session['user_id'])
        return jsonify({'permissions': permissions})
    except Exception as e:
        logger.error(f"Erro ao buscar permissões do usuário: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Rotas de gerenciamento de usuários (apenas para admins)
@app.route('/admin/users')
def admin_users():
    """Página de gerenciamento de usuários"""
    if 'user_id' not in session:
        return redirect('/')
    
    if not has_permission(session['user_id'], 'manage_users'):
        return redirect('/dashboard')
    
    return render_template('admin_users.html')

@app.route('/admin/groups')
def admin_groups():
    """Página de gerenciamento de grupos"""
    if 'user_id' not in session:
        return redirect('/')
    
    if not has_permission(session['user_id'], 'manage_users'):
        return redirect('/dashboard')
    
    return render_template('admin_groups.html')

@app.route('/admin/permissions')
def admin_permissions():
    """Página de gerenciamento de permissões dos grupos"""
    if 'user_id' not in session:
        return redirect('/')
    
    if not has_permission(session['user_id'], 'admin_access'):
        return redirect('/dashboard')
    
    return render_template('admin_permissions.html')

@app.route('/admin/clients')
def admin_clients():
    """Cadastro de Clientes (somente admins)."""
    if 'user_id' not in session:
        return redirect('/')
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'view_clients_admin')):
        return redirect('/dashboard')
    return render_template('admin_client.html')

@app.route('/admin/areas')
def admin_areas():
    """Cadastro de Áreas (UI)."""
    if 'user_id' not in session:
        return redirect('/')
    # Permissão: admin ou manage_areas ou view_areas_admin
    if not (has_permission(session['user_id'], 'admin_access') or
            has_permission(session['user_id'], 'manage_areas') or
            has_permission(session['user_id'], 'view_areas_admin')):
        return redirect('/dashboard')
    # Garantir tabela e dados padrão
    ensure_areas_table()
    return render_template('admin_areas.html')

# ---------------------- SECTORS (SETOR) ----------------------
def ensure_sectors_table():
    """Garante a tabela de setores (semelhante a áreas)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS sectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            color TEXT DEFAULT '#5b21b6',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit(); conn.close()
    except Exception as e:
        logger.error(f"Erro ao garantir tabela sectors: {e}")

@app.route('/admin/sectors')
def admin_sectors():
    """Cadastro de Setores (UI)."""
    if 'user_id' not in session:
        return redirect('/')
    if not (has_permission(session['user_id'], 'admin_access') or
            has_permission(session['user_id'], 'manage_sectors') or
            has_permission(session['user_id'], 'view_sectors_admin')):
        return redirect('/dashboard')
    ensure_sectors_table()
    return render_template('admin_sectors.html')

def ensure_clients_table():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit(); conn.close()
    except Exception as e:
        logger.error(f"Erro ao garantir tabela clients: {e}")

def ensure_operators_table():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS operators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        # Garantir coluna number caso a tabela já exista
        try:
            cur.execute('ALTER TABLE operators ADD COLUMN number TEXT')
        except sqlite3.OperationalError:
            pass
        # Índice único para número (apenas quando não nulo)
        try:
            cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_operators_number ON operators(number) WHERE number IS NOT NULL')
        except sqlite3.OperationalError:
            pass
        conn.commit(); conn.close()
    except Exception as e:
        logger.error(f"Erro ao garantir tabela operators: {e}")

@app.route('/admin/operators')
def admin_operators():
    if 'user_id' not in session:
        return redirect('/')
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'view_operators_admin')):
        return redirect('/dashboard')
    return render_template('admin_operator.html')

@app.route('/api/admin/operators', methods=['GET'])
def api_list_operators():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'view_operators_admin')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_operators_table()
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute('SELECT id, name, number FROM operators ORDER BY name')
    rows = [{'id': r[0], 'name': r[1], 'number': r[2]} for r in cur.fetchall()]
    conn.close()
    return jsonify({'success': True, 'operators': rows})

@app.route('/api/admin/operators', methods=['POST'])
def api_create_operator():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'view_operators_admin')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_operators_table()
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    number = (str(data.get('number')).strip() if data.get('number') is not None else None)
    if not name:
        return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    try:
        cur.execute('INSERT INTO operators (name, number) VALUES (?, ?)', (name, number))
        conn.commit()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Operador já existe'}), 400
    finally:
        conn.close()

@app.route('/api/admin/operators/<int:operator_id>', methods=['PUT'])
def api_update_operator(operator_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'view_operators_admin')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_operators_table()
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    number = (str(data.get('number')).strip() if data.get('number') is not None else None)
    if not name:
        return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute('UPDATE operators SET name = ?, number = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (name, number, operator_id))
    conn.commit(); conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/operators/<int:operator_id>', methods=['DELETE'])
def api_delete_operator(operator_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'view_operators_admin')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_operators_table()
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute('DELETE FROM operators WHERE id = ?', (operator_id,))
    conn.commit(); conn.close()
    return jsonify({'success': True})

def ensure_areas_table():
    """Garante a tabela de áreas para cadastro administrativo."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            color TEXT DEFAULT '#6f42c1',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        # Inserir áreas padrão (idempotente)
        default_areas = [
            ('Fundibem',            '', '#6f42c1'),
            ('Engenharia',          '', '#007bff'),
            ('Terceiros',           '', '#17a2b8'),
            ('Transporte',          '', '#fd7e14'),
            ('Não Definidos',       '', '#6c757d'),
            ('Qualidade',           '', '#dc3545'),
            ('Compras',             '', '#20c997'),
            ('Comercial',           '', '#28a745'),
            ('PCP',                 '', '#6610f2'),
            ('Almoxarifado',        '', '#ffc107'),
            ('Produção',            '', '#343a40'),
            ('Filial',              '', '#4b2ca1'),
        ]
        cur.executemany('INSERT OR IGNORE INTO areas (name, description, color) VALUES (?, ?, ?)', default_areas)
        conn.commit(); conn.close()
    except Exception as e:
        logger.error(f"Erro ao garantir tabela areas: {e}")

@app.route('/api/admin/clients', methods=['GET'])
def api_list_clients():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'view_clients_admin')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_clients_table()
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute('SELECT id, name FROM clients ORDER BY name')
    rows = [{'id': r[0], 'name': r[1]} for r in cur.fetchall()]
    conn.close()
    return jsonify({'success': True, 'clients': rows})

@app.route('/api/admin/areas', methods=['GET'])
def api_list_areas():
    """Lista áreas cadastradas (somente admins/áreas)."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or
            has_permission(session['user_id'], 'manage_areas') or
            has_permission(session['user_id'], 'view_areas_admin')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_areas_table()
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute('SELECT id, name, description, color, is_active, created_at FROM areas ORDER BY name')
    rows = [
        {
            'id': r[0], 'name': r[1], 'description': r[2] or '', 'color': r[3] or '#6f42c1',
            'is_active': bool(r[4]), 'created_at': r[5]
        } for r in cur.fetchall()
    ]
    conn.close()
    return jsonify({'success': True, 'areas': rows})

@app.route('/api/admin/sectors', methods=['GET'])
def api_list_sectors():
    """Lista setores cadastrados (somente admins/setores)."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or
            has_permission(session['user_id'], 'manage_sectors') or
            has_permission(session['user_id'], 'view_sectors_admin')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_sectors_table()
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute('SELECT id, name, description, color, is_active, created_at FROM sectors ORDER BY name')
    rows = [
        {
            'id': r[0], 'name': r[1], 'description': r[2] or '', 'color': r[3] or '#5b21b6',
            'is_active': bool(r[4]), 'created_at': r[5]
        } for r in cur.fetchall()
    ]
    conn.close()
    return jsonify({'success': True, 'sectors': rows})
@app.route('/api/admin/areas', methods=['POST'])
def api_create_area():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'manage_areas')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_areas_table()
    data = request.get_json(force=True) if request.is_json else request.form
    name = (data.get('name') or '').strip()
    description = (data.get('description') or '').strip()
    color = (data.get('color') or '#6f42c1').strip()
    if not name:
        return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400
    try:
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute('INSERT INTO areas (name, description, color) VALUES (?, ?, ?)', (name, description, color))
        conn.commit(); area_id = cur.lastrowid; conn.close()
        return jsonify({'success': True, 'area': {'id': area_id, 'name': name, 'description': description, 'color': color}})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Já existe uma área com este nome'}), 409
    except Exception as e:
        logger.error(f"Erro ao criar área: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@app.route('/api/admin/sectors', methods=['POST'])
def api_create_sector():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'manage_sectors')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_sectors_table()
    data = request.get_json(force=True) if request.is_json else request.form
    name = (data.get('name') or '').strip()
    description = (data.get('description') or '').strip()
    color = (data.get('color') or '#5b21b6').strip()
    if not name:
        return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400
    try:
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute('INSERT INTO sectors (name, description, color) VALUES (?, ?, ?)', (name, description, color))
        conn.commit(); sector_id = cur.lastrowid; conn.close()
        return jsonify({'success': True, 'sector': {'id': sector_id, 'name': name, 'description': description, 'color': color}})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Já existe um setor com este nome'}), 409
    except Exception as e:
        logger.error(f"Erro ao criar setor: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@app.route('/api/admin/areas/<int:area_id>', methods=['PUT'])
def api_update_area(area_id: int):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'manage_areas')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_areas_table()
    data = request.get_json(force=True) if request.is_json else request.form
    name = data.get('name')
    description = data.get('description')
    color = data.get('color')
    is_active = data.get('is_active')
    try:
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        fields = []; params = []
        if name is not None:
            fields.append('name = ?'); params.append(name)
        if description is not None:
            fields.append('description = ?'); params.append(description)
        if color is not None:
            fields.append('color = ?'); params.append(color)
        if is_active is not None:
            fields.append('is_active = ?'); params.append(1 if str(is_active).lower() in ('1','true','yes') else 0)
        if not fields:
            return jsonify({'success': False, 'message': 'Nada para atualizar'}), 400
        params.append(area_id)
        cur.execute(f"UPDATE areas SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", params)
        conn.commit(); conn.close()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Nome já em uso'}), 409
    except Exception as e:
        logger.error(f"Erro ao atualizar área {area_id}: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@app.route('/api/admin/sectors/<int:sector_id>', methods=['PUT'])
def api_update_sector(sector_id: int):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'manage_sectors')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_sectors_table()
    data = request.get_json(force=True) if request.is_json else request.form
    name = data.get('name')
    description = data.get('description')
    color = data.get('color')
    is_active = data.get('is_active')
    try:
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        fields = []; params = []
        if name is not None:
            fields.append('name = ?'); params.append(name)
        if description is not None:
            fields.append('description = ?'); params.append(description)
        if color is not None:
            fields.append('color = ?'); params.append(color)
        if is_active is not None:
            fields.append('is_active = ?'); params.append(1 if str(is_active).lower() in ('1','true','yes') else 0)
        if not fields:
            return jsonify({'success': False, 'message': 'Nada para atualizar'}), 400
        params.append(sector_id)
        cur.execute(f"UPDATE sectors SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", params)
        conn.commit(); conn.close()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Nome já em uso'}), 409
    except Exception as e:
        logger.error(f"Erro ao atualizar setor {sector_id}: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@app.route('/api/admin/areas/<int:area_id>', methods=['DELETE'])
def api_delete_area(area_id: int):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'manage_areas')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_areas_table()
    try:
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute('UPDATE areas SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (area_id,))
        conn.commit(); conn.close()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erro ao desativar área {area_id}: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@app.route('/api/admin/sectors/<int:sector_id>', methods=['DELETE'])
def api_delete_sector(sector_id: int):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'manage_sectors')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_sectors_table()
    try:
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute('UPDATE sectors SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (sector_id,))
        conn.commit(); conn.close()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erro ao desativar setor {sector_id}: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

# Lista de clientes para uso geral (formulários), sem exigir permissão de admin
@app.route('/api/clients', methods=['GET'])
def api_list_clients_public():
    """Retorna somente os nomes dos clientes para autocomplete/seleção no formulário de RNC.
    Requer usuário autenticado, mas não exige permissão administrativa.
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    try:
        ensure_clients_table()
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT name FROM clients ORDER BY name')
        names = [r[0] for r in cur.fetchall()]
        conn.close()
        return jsonify({'success': True, 'clients': names})
    except Exception as e:
        logger.error(f"Erro ao listar clientes públicos: {e}")
        try:
            conn.close()
        except Exception:
            pass
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@app.route('/api/admin/clients', methods=['POST'])
def api_create_client():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'view_clients_admin')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_clients_table()
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    try:
        cur.execute('INSERT INTO clients (name) VALUES (?)', (name,))
        conn.commit()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Cliente já existe'}), 400
    finally:
        conn.close()

@app.route('/api/admin/clients/<int:client_id>', methods=['PUT'])
def api_update_client(client_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not (has_permission(session['user_id'], 'admin_access') or has_permission(session['user_id'], 'view_clients_admin')):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_clients_table()
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute('UPDATE clients SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (name, client_id))
    conn.commit(); conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/clients/<int:client_id>', methods=['DELETE'])
def api_delete_client(client_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if not has_permission(session['user_id'], 'admin_access') and not has_permission(session['user_id'], 'manage_users'):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    ensure_clients_table()
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    conn.commit(); conn.close()
    return jsonify({'success': True})

@app.route('/api/users/list')
def api_list_users():
    """API para listar usuários ativos - disponível para todos os usuários
    autenticados para permitir atribuição/compartilhamento de RNCs"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email, department FROM users WHERE is_active = 1 ORDER BY name')
        users = cursor.fetchall()
        conn.close()
        
        formatted_users = []
        for user in users:
            formatted_users.append({
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'department': user[3]
            })
        
        return jsonify({'success': True, 'users': formatted_users})
        
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/admin/users', methods=['GET'])
def api_get_users():
    """Listar usuários com filtros (q, role, department, include_inactive)."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    if not has_permission(session['user_id'], 'manage_users'):
        return jsonify({'success': False, 'message': 'Sem permissão'}), 403
    
    # Coletar filtros
    q = request.args.get('q', '').strip()
    role = request.args.get('role')
    department = request.args.get('department')
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

    # Montar query dinâmica
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = '''
        SELECT u.id, u.name, u.email, u.department, u.role, u.permissions,
               u.created_at, u.is_active, g.name as group_name
        FROM users u
        LEFT JOIN groups g ON u.group_id = g.id
        WHERE 1=1
    '''
    params = []
    if not include_inactive:
        query += ' AND u.is_active = 1'
    if q:
        like = f"%{q}%"
        query += ' AND (u.name LIKE ? OR u.email LIKE ? OR u.department LIKE ?)'
        params.extend([like, like, like])
    if role:
        query += ' AND u.role = ?'
        params.append(role)
    if department:
        query += ' AND u.department = ?'
        params.append(department)
    query += ' ORDER BY u.name'

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    formatted_users = []
    import json
    for user in rows:
        permissions = []
        try:
            permissions = json.loads(user[5] or '[]')
        except Exception:
            permissions = []
        formatted_users.append({
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'department': user[3],
            'role': user[4],
            'permissions': permissions,
            'created_at': user[6],
            'is_active': bool(user[7]),
            'group_name': user[8]
        })
    
    return jsonify({'success': True, 'users': formatted_users})

@app.route('/api/admin/users', methods=['POST'])
def api_create_user():
    """API para criar usuário (apenas admin)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    if not has_permission(session['user_id'], 'manage_users'):
        return jsonify({'success': False, 'message': 'Sem permissão'}), 403
    
    try:
        data = request.get_json()
        
        success = create_user(
            name=data.get('name'),
            email=data.get('email'),
            password=data.get('password'),
            department=data.get('department'),
            role=data.get('role', 'user'),
            permissions=data.get('permissions', [])
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Usuário criado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Email já existe!'}), 400
            
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
def api_update_user(user_id):
    """API para atualizar usuário (apenas admin)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    if not has_permission(session['user_id'], 'manage_users'):
        return jsonify({'success': False, 'message': 'Sem permissão'}), 403
    
    try:
        data = request.get_json()
        
        success = update_user(
            user_id=user_id,
            name=data.get('name'),
            email=data.get('email'),
            department=data.get('department'),
            role=data.get('role'),
            permissions=data.get('permissions', []),
            is_active=data.get('is_active', True)
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Usuário atualizado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao atualizar usuário!'}), 400
            
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    """API para deletar usuário (apenas admin)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    if not has_permission(session['user_id'], 'manage_users'):
        return jsonify({'success': False, 'message': 'Sem permissão'}), 403
    
    try:
        success = delete_user(user_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Usuário desativado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao deletar usuário!'}), 400
            
    except Exception as e:
        logger.error(f"Erro ao deletar usuário: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/admin/users/<int:user_id>/restore', methods=['POST'])
def api_restore_user(user_id):
    """Reativar usuário desativado."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401

    if not has_permission(session['user_id'], 'manage_users'):
        return jsonify({'success': False, 'message': 'Sem permissão'}), 403

    try:
        if restore_user(user_id):
            return jsonify({'success': True, 'message': 'Usuário restaurado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao restaurar usuário!'}), 400
    except Exception as e:
        logger.error(f"Erro ao restaurar usuário: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
def api_reset_user_password(user_id):
    """Definir uma nova senha para o usuário."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401

    if not has_permission(session['user_id'], 'manage_users'):
        return jsonify({'success': False, 'message': 'Sem permissão'}), 403

    data = request.get_json() or {}
    new_password = data.get('new_password')
    if not new_password or len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Senha inválida (mínimo 6 caracteres)'}), 400

    try:
        if update_user_password(user_id, new_password):
            return jsonify({'success': True, 'message': 'Senha redefinida com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao redefinir senha!'}), 400
    except Exception as e:
        logger.error(f"Erro ao redefinir senha: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/chat')
def general_chat():
    """Página do chat geral"""
    if 'user_id' not in session:
        return redirect('/')
    
    return render_template('general_chat.html')

@app.route('/rnc/<int:rnc_id>/chat')
def rnc_chat(rnc_id):
    if 'user_id' not in session:
        return redirect('/')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar informações do RNC
        cursor.execute('''
            SELECT r.*, u.name as user_name, au.name as assigned_user_name
            FROM rncs r
            LEFT JOIN users u ON r.user_id = u.id
            LEFT JOIN users au ON r.assigned_user_id = au.id
            WHERE r.id = ?
        ''', (rnc_id,))
        rnc = cursor.fetchone()
        
        if not rnc:
            conn.close()
            return render_template('error.html', message='RNC não encontrado'), 404
        
        # Buscar usuário atual
        cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
        current_user = cursor.fetchone()
        
        # Buscar mensagens do chat
        cursor.execute('''
            SELECT cm.*, u.name as user_name, u.department
            FROM chat_messages cm
            LEFT JOIN users u ON cm.user_id = u.id
            WHERE cm.rnc_id = ?
            ORDER BY cm.created_at ASC
        ''', (rnc_id,))
        messages = cursor.fetchall()
        
        conn.close()
        
        rnc_data = {
            'id': rnc[0], 'rnc_number': rnc[1], 'title': rnc[2], 'description': rnc[3],
            'equipment': rnc[4], 'client': rnc[5], 'priority': rnc[6], 'status': rnc[7],
            'user_id': rnc[8], 'assigned_user_id': rnc[9], 'created_at': rnc[10],
            'updated_at': rnc[11], 'user_name': rnc[12], 'assigned_user_name': rnc[13]
        }
        
        return render_template('rnc_chat.html', rnc=rnc_data, messages=messages, current_user=current_user)
        
    except Exception as e:
        logger.error(f"Erro ao carregar chat do RNC: {e}")
        return render_template('error.html', message='Erro ao carregar chat'), 500

@app.route('/api/chat/<int:rnc_id>/messages')
def get_chat_messages(rnc_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cm.*, u.name as user_name, u.department
            FROM chat_messages cm
            LEFT JOIN users u ON cm.user_id = u.id
            WHERE cm.rnc_id = ?
            ORDER BY cm.created_at ASC
        ''', (rnc_id,))
        messages = cursor.fetchall()
        
        conn.close()
        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'id': msg[0],
                'rnc_id': msg[1],
                'user_id': msg[2],
                'message': msg[3],
                'message_type': msg[4],
                'created_at': msg[5],
                'user_name': msg[6],
                'department': msg[7]
            })
        
        return jsonify({'success': True, 'messages': formatted_messages})
        
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/chat/<int:rnc_id>/messages/<int:message_id>', methods=['DELETE'])
def delete_chat_message(rnc_id, message_id):
    """Excluir mensagem do chat de um RNC.
    Regras:
    - Usuário deve estar autenticado
    - Pode excluir se for autor da mensagem ou se for admin
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401

    user_id = session['user_id']
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Buscar mensagem
        cursor.execute('SELECT id, rnc_id, user_id FROM chat_messages WHERE id = ? AND rnc_id = ?', (message_id, rnc_id))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'success': False, 'message': 'Mensagem não encontrada'}), 404

        _, msg_rnc_id, author_id = row

        # Buscar role do usuário atual
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        current_role = user_row[0] if user_row else 'user'

        # Verificar permissão (autor ou admin)
        if user_id != author_id and current_role != 'admin':
            conn.close()
            return jsonify({'success': False, 'message': 'Sem permissão para excluir esta mensagem'}), 403

        # Excluir mensagem
        cursor.execute('DELETE FROM chat_messages WHERE id = ?', (message_id,))
        conn.commit()
        conn.close()

        # Notificar clientes na sala para remover a mensagem
        try:
            socketio.emit('message_deleted', {'id': message_id, 'rnc_id': msg_rnc_id}, room=f'rnc_{msg_rnc_id}')
        except Exception as e:
            logger.error(f'Erro ao emitir evento de exclusão de mensagem: {e}')

        return jsonify({'success': True, 'message': 'Mensagem excluída com sucesso'})

    except Exception as e:
        logger.error(f"Erro ao excluir mensagem: {e}")
        if 'conn' in locals():
            conn.close()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/notifications/unread')
def get_unread_notifications():
    """API para buscar notificações não lidas"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar notificações não lidas do usuário
        cursor.execute('''
            SELECT n.*, r.rnc_number, r.title as rnc_title
            FROM notifications n
            LEFT JOIN rncs r ON n.rnc_id = r.id
            WHERE n.user_id = ? AND n.is_read = 0
            ORDER BY n.created_at DESC
            LIMIT 10
        ''', (session['user_id'],))
        
        notifications = cursor.fetchall()
        conn.close()
        
        formatted_notifications = []
        for notif in notifications:
            formatted_notifications.append({
                'id': notif[0],
                'user_id': notif[1],
                'rnc_id': notif[2],
                'type': notif[3],
                'title': notif[4],
                'message': notif[5],
                'is_read': notif[6],
                'created_at': notif[7],
                'rnc_number': notif[8],
                'rnc_title': notif[9]
            })
        
        return jsonify({
            'success': True,
            'notifications': formatted_notifications,
            'count': len(formatted_notifications)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar notificações: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/notifications/mark-read', methods=['POST'])
def mark_notifications_read():
    """API para marcar notificações como lidas"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        notification_ids = data.get('notification_ids', [])
        
        if not notification_ids:
            return jsonify({'success': False, 'message': 'IDs de notificação não fornecidos'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Marcar notificações como lidas
        placeholders = ','.join(['?' for _ in notification_ids])
        cursor.execute(f'''
            UPDATE notifications 
            SET is_read = 1 
            WHERE id IN ({placeholders}) AND user_id = ?
        ''', notification_ids + [session['user_id']])
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'{cursor.rowcount} notificação(ões) marcada(s) como lida(s)'
        })
        
    except Exception as e:
        logger.error(f"Erro ao marcar notificações como lidas: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

# Eventos WebSocket
@socketio.on('connect')
def handle_connect():
    try:
        if 'user_id' not in session:
            # Tentar reidratar sessão a partir do cookie auxiliar
            uid = request.cookies.get('IPPEL_UID')
            if uid and uid.isdigit():
                try:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute('SELECT id, name, email, department, role FROM users WHERE id = ?', (int(uid),))
                    row = cursor.fetchone()
                    conn.close()
                    if row:
                        session['user_id'] = row[0]
                        session['user_name'] = row[1]
                        session['user_email'] = row[2]
                        session['user_department'] = row[3]
                        session['user_role'] = row[4]
                        session.permanent = True
                        logger.info(f"Sessão reidratada via cookie para user {row[0]}")
                except Exception as e:
                    logger.error(f"Falha ao reidratar sessão socket: {e}")
        if 'user_id' in session:
            user_id = session['user_id']
            online_users[request.sid] = user_id
            logger.info(f"Usuário {user_id} conectado (socket)")
        else:
            logger.warning("Conexão socket sem sessão válida")
    except Exception as e:
        logger.error(f"Erro em handle_connect: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in online_users:
        user_id = online_users.pop(request.sid)
        logger.info(f"Usuário {user_id} desconectado")

@socketio.on('join_room')
def handle_join_room(data):
    room = data['room']
    join_room(room)
    logger.info(f"Usuário entrou na sala: {room}")

@socketio.on('leave_room')
def handle_leave_room(data):
    room = data['room']
    leave_room(room)
    logger.info(f"Usuário saiu da sala: {room}")

@socketio.on('send_message')
def handle_send_message(data):
    # Verificar se o usuário está logado
    if 'user_id' not in session:
        logger.error("Usuário não autenticado ao tentar enviar mensagem")
        emit('error', {'message': 'Usuário não autenticado'})
        return
    
    logger.info(f"Tentativa de envio de mensagem: {data}")
    
    try:
        # Verificar tipo de chat
        if 'chat_type' in data:
            if data['chat_type'] == 'private':
                handle_private_message(data)
            elif data['chat_type'] == 'general':
                handle_general_chat_message(data)
            else:
                handle_rnc_chat_message(data)
        else:
            handle_rnc_chat_message(data)
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        emit('error', {'message': 'Erro ao enviar mensagem'})
    return
def handle_private_message(data):
    """Processar mensagem privada"""
    try:
        message = data['message']
        recipient_id = data['recipient_id']
        sender_id = session['user_id']
        
        # Salvar mensagem no banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO private_messages (sender_id, recipient_id, message, message_type)
            VALUES (?, ?, ?, ?)
        ''', (sender_id, recipient_id, message, 'text'))
        
        message_id = cursor.lastrowid
        
        # Buscar informações do usuário
        cursor.execute('SELECT name, department FROM users WHERE id = ?', (sender_id,))
        user_info = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        # Preparar dados da mensagem
        message_data = {
            'id': message_id,
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'message': message,
            'message_type': 'text',
            'is_read': False,
            'created_at': datetime.now().isoformat(),
            'user_name': user_info[0] if user_info else 'Usuário',
            'department': user_info[1] if user_info else ''
        }
        
        # Criar sala única para a conversa
        room = f"private_{min(sender_id, recipient_id)}_{max(sender_id, recipient_id)}"
        
        # Enviar mensagem para a sala privada
        emit('private_message', message_data, room=room)
        
        # Criar notificação para o destinatário
        notification_data = {
            'type': 'new_private_message',
            'title': f'💬 Nova mensagem de {user_info[0] if user_info else "Usuário"}',
            'message': f'{message[:50]}{"..." if len(message) > 50 else ""}',
            'sender_id': sender_id,
            'sender_name': user_info[0] if user_info else 'Usuário',
            'timestamp': datetime.now().isoformat()
        }
        
        # Salvar notificação no banco
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notifications (user_id, type, title, message, is_read)
                VALUES (?, ?, ?, ?, ?)
            ''', (recipient_id, 'new_private_message', notification_data['title'], notification_data['message'], 0))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Erro ao salvar notificação: {e}")
        
        # Enviar notificação em tempo real
        emit('notification', notification_data, room=f'user_{recipient_id}')
        
        logger.info(f"Nova mensagem privada de {sender_id} para {recipient_id}: {message}")
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem privada: {e}")
        emit('error', {'message': 'Erro ao enviar mensagem'})

def handle_general_chat_message(data):
    """Processar mensagem do chat geral (mantido para compatibilidade)"""
    try:
        message = data['message']
        user_id = session['user_id']
        
        # Buscar informações do usuário
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT name, department FROM users WHERE id = ?', (user_id,))
        user_info = cursor.fetchone()
        conn.close()
        
        # Preparar dados da mensagem
        message_data = {
            'id': 0,
            'user_id': user_id,
            'message': message,
            'message_type': 'text',
            'created_at': datetime.now().isoformat(),
            'user_name': user_info[0] if user_info else 'Usuário',
            'department': user_info[1] if user_info else ''
        }
        
        # Enviar mensagem para todos os usuários online
        emit('general_chat_message', message_data, broadcast=True)
        
        logger.info(f"Nova mensagem no chat geral: {message}")
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem do chat geral: {e}")
        emit('error', {'message': 'Erro ao enviar mensagem'})

def handle_rnc_chat_message(data):
    """Processar mensagem do chat de RNC"""
    try:
        rnc_id = data['rnc_id']
        message = data['message']
        user_id = session['user_id']
        
        # Salvar mensagem no banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_messages (rnc_id, user_id, message, message_type)
            VALUES (?, ?, ?, ?)
        ''', (rnc_id, user_id, message, 'text'))
        
        message_id = cursor.lastrowid
        
        # Buscar informações do usuário
        cursor.execute('SELECT name, department FROM users WHERE id = ?', (user_id,))
        user_info = cursor.fetchone()
        
        # Buscar informações do RNC para notificação
        cursor.execute('SELECT rnc_number, title FROM rncs WHERE id = ?', (rnc_id,))
        rnc_info = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        # Preparar dados da mensagem
        message_data = {
            'id': message_id,
            'rnc_id': rnc_id,
            'user_id': user_id,
            'message': message,
            'message_type': 'text',
            'created_at': datetime.now().isoformat(),
            'user_name': user_info[0] if user_info else 'Usuário',
            'department': user_info[1] if user_info else ''
        }
        
        # Preparar dados da notificação
        notification_data = {
            'type': 'new_message',
            'title': f'💬 Nova mensagem no RNC {rnc_info[0] if rnc_info else rnc_id}',
            'message': f'{user_info[0] if user_info else "Usuário"}: {message[:50]}{"..." if len(message) > 50 else ""}',
            'rnc_id': rnc_id,
            'rnc_number': rnc_info[0] if rnc_info else f'RNC-{rnc_id}',
            'rnc_title': rnc_info[1] if rnc_info else 'RNC',
            'user_name': user_info[0] if user_info else 'Usuário',
            'department': user_info[1] if user_info else '',
            'timestamp': datetime.now().isoformat()
        }
        
        # Enviar mensagem para todos na sala
        emit('new_message', message_data, room=f'rnc_{rnc_id}')
        
        # Salvar notificação no banco de dados para todos os usuários ativos (exceto o remetente)
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Buscar todos os usuários ativos
            cursor.execute('SELECT id FROM users WHERE is_active = 1 AND id != ?', (user_id,))
            active_users = cursor.fetchall()
            
            logger.info(f"Criando notificações para {len(active_users)} usuários")
            
            # Criar notificações para cada usuário
            for user in active_users:
                cursor.execute('''
                    INSERT INTO notifications (user_id, rnc_id, type, title, message, is_read)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user[0], rnc_id, 'new_message', notification_data['title'], notification_data['message'], 0))
            
            conn.commit()
            conn.close()
            logger.info(f"Notificações criadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar notificações: {e}")
            if 'conn' in locals():
                conn.close()
        
        # Enviar notificação para todos na sala (exceto o remetente)
        emit('notification', notification_data, room=f'rnc_{rnc_id}', include_self=False)
        
        # Enviar notificação global para usuários online (exceto o remetente)
        emit('global_notification', notification_data, include_self=False)
        
        logger.info(f"Nova mensagem no RNC {rnc_id}: {message}")
        
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        emit('error', {'message': 'Erro ao enviar mensagem'})

@socketio.on('typing')
def handle_typing(data):
    if 'user_id' not in session:
        return
    
    try:
        chat_type = data.get('chat_type', 'rnc')  # 'rnc' ou 'private'
        is_typing = data['is_typing']
        user_id = session['user_id']
        
        # Buscar informações do usuário
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM users WHERE id = ?', (user_id,))
        user_info = cursor.fetchone()
        conn.close()
        
        typing_data = {
            'user_id': user_id,
            'user_name': user_info[0] if user_info else 'Usuário',
            'is_typing': is_typing
        }
        
        if chat_type == 'rnc':
            rnc_id = data.get('rnc_id')
            if rnc_id:
                # Enviar indicador de digitação para chat de RNC
                emit('user_typing', typing_data, room=f'rnc_{rnc_id}', include_self=False)
        elif chat_type == 'private':
            contact_id = data.get('contact_id')
            if contact_id:
                # Enviar indicador de digitação para chat privado
                room_name = f'private_{min(user_id, contact_id)}_{max(user_id, contact_id)}'
                emit('user_typing', typing_data, room=room_name, include_self=False)
        
    except Exception as e:
        logger.error(f"Erro ao processar indicador de digitação: {e}")

@app.route('/<path:filename>')
def serve_static(filename):
    """Servir arquivos estáticos"""
    # Evitar path traversal
    if '..' in filename or filename.startswith(('/', '\\')):
        return abort(400)
    return send_from_directory('.', filename)

def cleanup_old_deleted_rncs():
    """(Desativado) Lixeira removida."""
    return

def schedule_cleanup():
    """(Desativado) Lixeira removida."""
    logger.info("Rotina de limpeza desativada (lixeira removida)")

@app.route('/api/charts/data')
def get_chart_data():
    """API para fornecer dados dos gráficos - CORRIGIDA"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Remover verificação de permissão para permitir acesso aos gráficos
    # if not has_permission(session['user_id'], 'view_charts'):
    #     return jsonify({'error': 'Acesso negado: usuário não tem permissão para visualizar gráficos'}), 403
    
    try:
        period = request.args.get('period', '30', type=int)
        cache_key = f"charts_{session['user_id']}_{period}"
        cached = get_cached_query(cache_key)
        if cached:
            return jsonify(cached)
        logger.info(f"Gerando dados de gráficos para período de {period} dias")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Data limite baseada no período
        from datetime import datetime, timedelta
        limit_date = datetime.now() - timedelta(days=period)
        # Evitar DeprecationWarning do sqlite3 (Py 3.12+) convertendo datetime para string explícita
        limit_date_str = limit_date.strftime('%Y-%m-%d %H:%M:%S')
        
        # 1. Gráfico de Status
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM rncs 
            WHERE created_at >= ? AND is_deleted = 0
            GROUP BY status
            ORDER BY count DESC
        ''', (limit_date_str,))
        status_data = cursor.fetchall()
        
        # 2. Gráfico de Tendência Temporal (RNCs por dia)
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM rncs 
            WHERE created_at >= ? AND is_deleted = 0
            GROUP BY DATE(created_at)
            ORDER BY date
        ''', (limit_date_str,))
        trend_data = cursor.fetchall()
        
        # 3. Gráfico de Clientes
        cursor.execute('''
            SELECT client, COUNT(*) as count
            FROM rncs 
            WHERE created_at >= ? AND is_deleted = 0 AND client IS NOT NULL AND client != ''
            GROUP BY client
            ORDER BY count DESC
            LIMIT 10
        ''', (limit_date_str,))
        client_data = cursor.fetchall()
        
        # 4. Gráfico de Equipamentos
        cursor.execute('''
            SELECT equipment, COUNT(*) as count
            FROM rncs 
            WHERE created_at >= ? AND is_deleted = 0 AND equipment IS NOT NULL AND equipment != ''
            GROUP BY equipment
            ORDER BY count DESC
            LIMIT 10
        ''', (limit_date_str,))
        equipment_data = cursor.fetchall()
        
        # 5. Gráfico de Departamentos
        cursor.execute('''
            SELECT u.department, COUNT(*) as count
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE r.created_at >= ? AND r.is_deleted = 0 AND u.department IS NOT NULL
            GROUP BY u.department
            ORDER BY count DESC
        ''', (limit_date_str,))
        department_data = cursor.fetchall()
        
        # 6. Gráfico de Prioridades
        cursor.execute('''
            SELECT priority, COUNT(*) as count
            FROM rncs 
            WHERE created_at >= ? AND is_deleted = 0 AND priority IS NOT NULL
            GROUP BY priority
            ORDER BY count DESC
        ''', (limit_date_str,))
        priority_data = cursor.fetchall()
        
        # 7. Gráfico de Disposição
        disposition_data = []
        dispositions = [
            ('disposition_usar', 'Usar'),
            ('disposition_retrabalhar', 'Retrabalhar'),
            ('disposition_rejeitar', 'Rejeitar'),
            ('disposition_sucata', 'Sucata'),
            ('disposition_devolver_estoque', 'Devolver ao Estoque'),
            ('disposition_devolver_fornecedor', 'Devolver ao Fornecedor')
        ]
        
        for field, label in dispositions:
            cursor.execute(f'''
                SELECT COUNT(*) as count
                FROM rncs 
                WHERE created_at >= ? AND is_deleted = 0 AND {field} = 1
            ''', (limit_date_str,))
            count = cursor.fetchone()[0]
            if count > 0:
                disposition_data.append((label, count))
        
        # 8. Gráfico de Usuários
        cursor.execute('''
            SELECT u.name, COUNT(*) as count
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE r.created_at >= ? AND r.is_deleted = 0
            GROUP BY r.user_id, u.name
            ORDER BY count DESC
            LIMIT 10
        ''', (limit_date_str,))
        user_data = cursor.fetchall()
        
        return_db_connection(conn)
        
        result = {
            'status': [{'label': row[0], 'count': row[1]} for row in status_data],
            'trend': [{'date': row[0], 'count': row[1]} for row in trend_data],
            'clients': [{'label': row[0], 'count': row[1]} for row in client_data],
            'equipment': [{'label': row[0], 'count': row[1]} for row in equipment_data],
            'departments': [{'label': row[0], 'count': row[1]} for row in department_data],
            'priorities': [{'label': row[0], 'count': row[1]} for row in priority_data],
            'dispositions': [{'label': row[0], 'count': row[1]} for row in disposition_data],
            'users': [{'label': row[0], 'count': row[1]} for row in user_data]
        }
        cache_query(cache_key, result, ttl=60)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro ao gerar dados dos gráficos: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/charts/simple-data')
def get_simple_charts_data():
    """API simplificada para dados dos gráficos - CORRIGIDA"""
    try:
        logger.info("Iniciando API simple-data")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Buscar dados básicos
        cur.execute('SELECT COUNT(*) FROM rncs WHERE is_deleted = 0')
        total_rncs = cur.fetchone()[0]
        
        cur.execute('SELECT status, COUNT(*) FROM rncs WHERE is_deleted = 0 GROUP BY status')
        status_data = cur.fetchall()
        
        # Buscar usuários que criaram RNCs
        cur.execute('''
            SELECT u.name, COUNT(*) as count
            FROM rncs r
            JOIN users u ON r.user_id = u.id
            WHERE r.is_deleted = 0
            GROUP BY r.user_id, u.name
            ORDER BY count DESC
            LIMIT 10
        ''')
        users_data = cur.fetchall()
        
        return_db_connection(conn)
        
        result = {
            'success': True,
            'data': {
                'total_rncs': total_rncs,
                'status': [{'label': row[0], 'count': row[1]} for row in status_data],
                'users': [{'label': row[0], 'count': row[1]} for row in users_data]
            }
        }
        
        logger.info(f"API simple-data retornando: {len(users_data)} usuários")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro na API simple-data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500



# Route para importação de dados (mantido para compatibilidade)
@app.route('/api/importar-dados', methods=['GET'])
def importar_dados():
    """Route simples para compatibilidade"""
    return jsonify({'success': True, 'message': 'Dados importados com sucesso'})

@app.route('/api/test/performance')
def test_performance_api():
    """API de teste para verificar se todos os usuários estão sendo retornados"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. VERIFICAR TODOS OS USUÁRIOS NO BANCO
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users_db = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1 OR is_active IS NULL")
        active_users_db = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE name IS NOT NULL AND name != ''")
        named_users_db = cursor.fetchone()[0]
        
        print(f"🔍 DIAGNÓSTICO COMPLETO:")
        print(f"   📊 Total de usuários no banco: {total_users_db}")
        print(f"   ✅ Usuários ativos: {active_users_db}")
        print(f"   📝 Usuários com nome: {named_users_db}")
        
        # 2. BUSCAR TODOS OS USUÁRIOS ATIVOS COM NOME
        cursor.execute("""
            SELECT id, name, department, is_active FROM users 
            WHERE name IS NOT NULL 
              AND name != '' 
              AND (is_active = 1 OR is_active IS NULL)
            ORDER BY id
        """)
        all_users = cursor.fetchall()
        
        print(f"👥 Usuários encontrados na consulta: {len(all_users)}")
        for user_id, name, dept, active in all_users[:10]:
            print(f"   ID {user_id}: {name} - {dept or 'Sem dept'} - Ativo: {active}")
        
        # 3. BUSCAR RNCs BASEADAS NAS ASSINATURAS DE ENGENHARIA
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN r.signature_engineering_name IS NOT NULL AND r.signature_engineering_name != '' 
                    THEN r.signature_engineering_name
                    ELSE r.user_id
                END as owner_id,
                COUNT(r.id) as rnc_count
            FROM rncs r
            WHERE r.status IN ('Finalizado','finalized')
              AND r.is_deleted = 0
            GROUP BY owner_id
            ORDER BY rnc_count DESC
        """)
        rnc_rows = cursor.fetchall()
        rnc_data = {row[0]: row[1] for row in rnc_rows}
        
        print(f"📊 RNCs encontradas por assinatura: {rnc_data}")
        
        # 4. PROCESSAR RESULTADO BASEADO NAS ASSINATURAS
        meta_mensal = 5
        result = []
        
        # Criar lista de assinaturas únicas
        unique_signatures = set()
        for owner_id, count in rnc_rows:
            if isinstance(owner_id, str) and owner_id.strip():
                unique_signatures.add(owner_id.strip())
            elif isinstance(owner_id, int):
                # Se for ID, buscar nome do usuário
                cursor.execute("SELECT name FROM users WHERE id = ?", (owner_id,))
                user_result = cursor.fetchone()
                if user_result:
                    unique_signatures.add(user_result[0])
        
        print(f"🔍 Assinaturas únicas encontradas: {unique_signatures}")
        
        # Processar cada assinatura
        for signature in sorted(unique_signatures):
            rncs = rnc_data.get(signature, 0)
            percentage = (rncs / meta_mensal * 100) if meta_mensal > 0 else 0
            status = 'Acima da Meta' if rncs >= meta_mensal else 'Abaixo da Meta'
            
            print(f"🧪 PROCESSANDO - Assinatura: {signature} - RNCs: {rncs} - Status: {status}")
            
            result.append({
                'id': signature,
                'name': signature,
                'rncs': rncs,
                'meta': meta_mensal,
                'percentage': round(percentage, 1),
                'status': status,
                'department': 'Engenharia',
                'is_active': True
            })
        
        # 5. VERIFICAR USUÁRIOS QUE NÃO APARECERAM
        users_with_rncs = set(rnc_data.keys())
        all_user_ids = {user[0] for user in all_users}
        users_without_rncs = all_user_ids - users_with_rncs
        
        print(f"⚠️ Usuários sem RNCs: {users_without_rncs}")
        
        conn.close()
        
        return jsonify({
            'success': True,
            'diagnostic': {
                'total_users_db': total_users_db,
                'active_users_db': active_users_db,
                'named_users_db': named_users_db,
                'users_found_in_query': len(all_users),
                'users_with_rncs': len(users_with_rncs),
                'users_without_rncs': len(users_without_rncs)
            },
            'total_users': len(all_users),
            'total_rncs_found': len(rnc_data),
            'data': result,
            'debug': {
                'users_processed': len(result),
                'rnc_data': rnc_data,
                'users_without_rncs': list(users_without_rncs)
            }
        })
        
    except Exception as e:
        print(f"❌ Erro no teste de performance: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/available-years')
def get_available_years():
    """API para retornar os anos disponíveis no banco de dados"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        # Gerar todos os anos de 2013 até 2025
        all_years = [str(year) for year in range(2013, 2026)]
        
        # Adicionar anos futuros até 2030
        current_year = datetime.now().year
        for year in range(2026, 2031):
            all_years.append(str(year))
        
        # Ordenar anos (mais recentes primeiro)
        all_years.sort(reverse=True)
        
        print(f"📅 Anos gerados: {all_years}")
        
        return jsonify({
            'success': True,
            'years': all_years,
            'current_year': str(current_year),
            'total_years': len(all_years)
        })
        
    except Exception as e:
        print(f"Erro ao buscar anos disponíveis: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@app.route('/api/available-months')
def get_available_months():
    """API para retornar todos os meses disponíveis"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        # Todos os meses do ano
        months = [
            {'value': '01', 'name': 'Janeiro'},
            {'value': '02', 'name': 'Fevereiro'},
            {'value': '03', 'name': 'Março'},
            {'value': '04', 'name': 'Abril'},
            {'value': '05', 'name': 'Maio'},
            {'value': '06', 'name': 'Junho'},
            {'value': '07', 'name': 'Julho'},
            {'value': '08', 'name': 'Agosto'},
            {'value': '09', 'name': 'Setembro'},
            {'value': '10', 'name': 'Outubro'},
            {'value': '11', 'name': 'Novembro'},
            {'value': '12', 'name': 'Dezembro'}
        ]
        
        return jsonify({
            'success': True,
            'months': months,
            'total_months': len(months)
        })
        
    except Exception as e:
        print(f"Erro ao buscar meses disponíveis: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    # Inicializar banco de dados
    init_database()
    
    # Inicializar pool de conexões otimizado para i5-7500 + 16GB RAM
    for _ in range(150):  # 150 conexões para 200+ usuários
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=NORMAL')
        conn.execute('PRAGMA cache_size=100000')  # Cache aumentado para i5-7500 + 16GB RAM
        conn.execute('PRAGMA temp_store=MEMORY')
        conn.execute('PRAGMA mmap_size=1073741824')  # 1GB mmap para i5-7500 + 16GB RAM
        conn.execute('PRAGMA page_size=4096')
        conn.execute('PRAGMA auto_vacuum=INCREMENTAL')
        db_pool.put(conn)
    
    # Iniciar backup automático (a cada 12 horas, sem backup imediato)
    try:
        start_backup_scheduler(interval_seconds=43200)
    except Exception as e:
        try:
            logger.error(f"Falha ao iniciar backup automático: {e}")
        except Exception:
            print(f"Falha ao iniciar backup automático: {e}")
    
    # Iniciar monitor de performance em background
    performance_thread = threading.Thread(target=performance_monitor, daemon=True)
    performance_thread.start()
    
    # Obter IP e usar porta fixa para acesso em rede
    local_ip = get_local_ip()
    port = 5001
    
    print("🚀 Iniciando Servidor do Formulário RNC")
    print("=" * 50)
    # Detectar HTTPS via variáveis de ambiente
    import os as _os
    _enable_https = _os.environ.get('IPPEL_ENABLE_HTTPS', '').strip() in ('1', 'true', 'TRUE', 'yes', 'on')
    _force_http = _os.environ.get('IPPEL_FORCE_HTTP', '1').strip() in ('1', 'true', 'TRUE', 'yes', 'on')
    if _force_http:
        _enable_https = False
    _certfile = _os.environ.get('SSL_CERTFILE')
    _keyfile = _os.environ.get('SSL_KEYFILE')

    # Forçar somente HTTP
    _enable_https = False
    print(f"📋 Login/Formulário: http://{local_ip}:{port}")
    print(f"🔧 Painel Admin: http://{local_ip}:5000")
    print("=" * 50)
    print("✅ Usuário Admin criado automaticamente:")
    print("   Email: admin@ippel.com.br")
    print("   Senha: admin123")
    print("=" * 50)
    print("🗑️ Lixeira desativada:")
    print("   - Exclusão agora é definitiva (sem retenção)")
    print("=" * 50)
    print("⚡ Otimizações de Performance:")
    print("   - Pool de conexões: 20 conexões")
    print("   - Cache de consultas: Ativo")
    print("   - Monitor de performance: Ativo")
    print("   - SocketIO threading: Ativo")
    print("   - SQLite WAL mode: Ativo")
    print("=" * 50)
    
    try:
        # Suporte a HTTPS:
        # - IPPEL_ENABLE_HTTPS=1 habilita HTTPS.
        # - Se SSL_CERTFILE e SSL_KEYFILE forem fornecidos, serão usados.
        # - Caso contrário, usa certificado 'adhoc' (autoassinado) quando não estiver em modo eventlet.
        # Somente HTTP
        # Definir cookie de sessão para o domínio/IP acessado
        app.config['SESSION_COOKIE_DOMAIN'] = None  # IP
        app.config['SESSION_COOKIE_PATH'] = '/'
        
        # Executar servidor - usando Flask padrão (SocketIO desabilitado)
        print("⚠️ Executando sem SocketIO - funcionalidades de chat limitadas")
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Servidor do formulário encerrado")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
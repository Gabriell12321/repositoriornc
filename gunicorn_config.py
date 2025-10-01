# Configuração do Gunicorn para produção
import multiprocessing

# Configurações básicas - Otimizado para i5-7500 + 16GB RAM
bind = "0.0.0.0:5001"
workers = max(8, multiprocessing.cpu_count() * 4)  # 16 workers para i5-7500
worker_class = "eventlet"
worker_connections = 3000  # Aumentado para i5-7500 + 16GB RAM
max_requests = 3000  # Aumentado para i5-7500 + 16GB RAM
max_requests_jitter = 150  # Aumentado para i5-7500 + 16GB RAM

# Timeouts
timeout = 30
keepalive = 2
graceful_timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "ippel_server"

# Preload app
preload_app = True

# Worker lifecycle
max_requests_jitter = 50
worker_tmp_dir = "/dev/shm"

# Socket.IO specific
worker_class = "eventlet"
worker_connections = 1000

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

def when_ready(server):
    """Executar quando o servidor estiver pronto"""
    server.log.info("🚀 Servidor IPPEL iniciado em modo produção!")

def worker_int(worker):
    """Executar quando um worker for interrompido"""
    worker.log.info("Worker interrompido")

def pre_fork(server, worker):
    """Executar antes de criar workers"""
    server.log.info("Criando worker...")

def post_fork(server, worker):
    """Executar após criar workers"""
    server.log.info(f"Worker {worker.pid} criado")

def post_worker_init(worker):
    """Executar após inicializar worker"""
    worker.log.info(f"Worker {worker.pid} inicializado")

def worker_abort(worker):
    """Executar quando um worker abortar"""
    worker.log.info(f"Worker {worker.pid} abortado") 
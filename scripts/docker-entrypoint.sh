#!/bin/bash
# Docker entrypoint script para IPPEL RNC System

set -e

echo "=== IPPEL RNC System - Inicialização ==="
echo "Timestamp: $(date)"
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"

# Função para log com timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Função para verificar saúde do banco
check_database() {
    log "Verificando conexão com banco de dados..."
    python -c "
import sqlite3
import sys
try:
    conn = sqlite3.connect('ippel_system.db', timeout=10)
    cursor = conn.cursor()
    cursor.execute('SELECT sqlite_version();')
    version = cursor.fetchone()
    print(f'SQLite version: {version[0]}')
    conn.close()
    print('✓ Banco de dados acessível')
except Exception as e:
    print(f'✗ Erro no banco: {e}')
    sys.exit(1)
"
}

# Função para inicializar banco se necessário
init_database() {
    if [ ! -f "ippel_system.db" ]; then
        log "Banco de dados não encontrado. Inicializando..."
        python -c "
import init_system
import sys
try:
    init_system.initialize_database()
    print('✓ Banco de dados inicializado')
except Exception as e:
    print(f'✗ Erro na inicialização: {e}')
    sys.exit(1)
"
    else
        log "Banco de dados existente encontrado"
    fi
}

# Função para executar migrações
run_migrations() {
    log "Verificando necessidade de migrações..."
    python -c "
import sqlite3
import sys
try:
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Verificar se tabela de controle de versão existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Inserir versão inicial se não existir
    cursor.execute('SELECT COUNT(*) FROM schema_version')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO schema_version (version) VALUES (1)')
    
    conn.commit()
    conn.close()
    print('✓ Migrações verificadas')
except Exception as e:
    print(f'✗ Erro nas migrações: {e}')
    sys.exit(1)
"
}

# Função para verificar dependências críticas
check_dependencies() {
    log "Verificando dependências críticas..."
    python -c "
import sys
required_modules = [
    'flask', 'werkzeug', 'sqlite3', 'hashlib', 
    'datetime', 'secrets', 'smtplib', 'ssl'
]

missing = []
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)

if missing:
    print(f'✗ Módulos ausentes: {missing}')
    sys.exit(1)
else:
    print('✓ Todas as dependências disponíveis')
"
}

# Função para configurar logging
setup_logging() {
    log "Configurando sistema de logs..."
    mkdir -p logs
    touch logs/app.log logs/error.log logs/access.log
    
    # Configurar rotação de logs se logrotate estiver disponível
    if command -v logrotate >/dev/null 2>&1; then
        cat > /tmp/ippel-logrotate.conf << EOF
/app/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 ippel ippel
}
EOF
        log "✓ Configuração de rotação de logs criada"
    fi
}

# Função para backup de segurança
create_safety_backup() {
    if [ -f "ippel_system.db" ]; then
        backup_file="backups/startup_backup_$(date +%Y%m%d_%H%M%S).db"
        mkdir -p backups
        cp "ippel_system.db" "$backup_file"
        log "✓ Backup de segurança criado: $backup_file"
    fi
}

# Função para limpeza de arquivos temporários
cleanup_temp_files() {
    log "Limpando arquivos temporários..."
    find /tmp -name "ippel_*" -type f -mtime +1 -delete 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    log "✓ Limpeza concluída"
}

# Função para verificar configurações
check_config() {
    log "Verificando configurações..."
    python -c "
import os
import sys

# Verificar variáveis de ambiente críticas
env_vars = ['FLASK_APP', 'FLASK_ENV']
missing_vars = []

for var in env_vars:
    if not os.environ.get(var):
        missing_vars.append(var)

if missing_vars:
    print(f'⚠ Variáveis de ambiente não definidas: {missing_vars}')
else:
    print('✓ Variáveis de ambiente configuradas')

# Verificar arquivos de configuração
if os.path.exists('config_local.py'):
    print('✓ Configuração local encontrada')
else:
    print('⚠ Usando configurações padrão')
"
}

# Função para otimizar banco na inicialização
optimize_database() {
    log "Otimizando banco de dados..."
    python -c "
import sqlite3
try:
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Executar VACUUM para compactar
    cursor.execute('VACUUM')
    
    # Analisar estatísticas
    cursor.execute('ANALYZE')
    
    # Configurar performance
    cursor.execute('PRAGMA optimize')
    cursor.execute('PRAGMA journal_mode=WAL')
    cursor.execute('PRAGMA synchronous=NORMAL')
    cursor.execute('PRAGMA cache_size=10000')
    cursor.execute('PRAGMA temp_store=MEMORY')
    
    conn.commit()
    conn.close()
    print('✓ Banco de dados otimizado')
except Exception as e:
    print(f'⚠ Erro na otimização: {e}')
"
}

# Execução das verificações pré-inicialização
main() {
    log "Iniciando verificações pré-inicialização..."
    
    # Verificações essenciais
    check_dependencies
    check_config
    
    # Configurar ambiente
    setup_logging
    
    # Preparar banco de dados
    check_database
    init_database
    run_migrations
    create_safety_backup
    
    # Otimizações
    optimize_database
    cleanup_temp_files
    
    log "✓ Todas as verificações concluídas com sucesso"
    log "Iniciando aplicação IPPEL RNC System..."
    
    # Executar comando principal
    exec "$@"
}

# Tratamento de sinais para shutdown graceful
cleanup_on_exit() {
    log "Recebido sinal de encerramento. Finalizando graciosamente..."
    
    # Fechar conexões de banco abertas
    python -c "
import sqlite3
import os
if os.path.exists('ippel_system.db-wal'):
    try:
        conn = sqlite3.connect('ippel_system.db')
        conn.execute('PRAGMA wal_checkpoint(FULL)')
        conn.close()
        print('✓ WAL checkpoint executado')
    except:
        pass
"
    
    log "Aplicação finalizada"
    exit 0
}

# Configurar tratamento de sinais
trap cleanup_on_exit SIGTERM SIGINT

# Executar função principal
main "$@"

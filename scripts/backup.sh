#!/bin/bash
# Script de backup automatizado - IPPEL RNC System
# Backup inteligente com compressão, versionamento e limpeza automática

set -e

# Configurações
BACKUP_DIR="${BACKUP_PATH:-/backups}"
DB_PATH="${DATABASE_PATH:-/app/data/ippel_system.db}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ippel_backup_$TIMESTAMP"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# Verificar se é executado como root/usuário apropriado
check_permissions() {
    if [ ! -w "$BACKUP_DIR" ]; then
        error "Sem permissão de escrita em $BACKUP_DIR"
        exit 1
    fi
    
    if [ ! -r "$DB_PATH" ]; then
        error "Sem permissão de leitura em $DB_PATH"
        exit 1
    fi
}

# Criar diretório de backup se não existir
prepare_backup_dir() {
    mkdir -p "$BACKUP_DIR"
    success "Diretório de backup preparado: $BACKUP_DIR"
}

# Verificar espaço em disco
check_disk_space() {
    local required_space_mb=100
    local available_space=$(df "$BACKUP_DIR" | awk 'NR==2 {print int($4/1024)}')
    
    if [ "$available_space" -lt "$required_space_mb" ]; then
        error "Espaço insuficiente. Disponível: ${available_space}MB, Necessário: ${required_space_mb}MB"
        exit 1
    fi
    
    success "Espaço em disco verificado: ${available_space}MB disponível"
}

# Backup do banco de dados SQLite
backup_database() {
    log "Iniciando backup do banco de dados..."
    
    if [ ! -f "$DB_PATH" ]; then
        error "Banco de dados não encontrado: $DB_PATH"
        exit 1
    fi
    
    # Backup usando SQLite .backup command (mais seguro que cp)
    local db_backup="$BACKUP_FILE.db"
    sqlite3 "$DB_PATH" ".backup '$db_backup'"
    
    # Verificar integridade do backup
    local integrity_check=$(sqlite3 "$db_backup" "PRAGMA integrity_check;" | head -1)
    if [ "$integrity_check" != "ok" ]; then
        error "Backup do banco falhou na verificação de integridade"
        rm -f "$db_backup"
        exit 1
    fi
    
    success "Backup do banco de dados criado: $db_backup"
}

# Backup de arquivos de configuração
backup_configs() {
    log "Fazendo backup de configurações..."
    
    local config_backup="$BACKUP_FILE.configs.tar.gz"
    local config_files=""
    
    # Lista de arquivos de configuração importantes
    local config_paths=(
        "config_local.py"
        ".env"
        "nginx/nginx.conf"
        "docker-compose.yml"
        "requirements.txt"
    )
    
    # Verificar quais arquivos existem
    for config_path in "${config_paths[@]}"; do
        if [ -f "/app/$config_path" ]; then
            config_files="$config_files /app/$config_path"
        fi
    done
    
    if [ -n "$config_files" ]; then
        tar -czf "$config_backup" $config_files 2>/dev/null || true
        success "Backup de configurações criado: $config_backup"
    else
        warning "Nenhum arquivo de configuração encontrado para backup"
    fi
}

# Backup de logs importantes
backup_logs() {
    log "Fazendo backup de logs recentes..."
    
    local logs_backup="$BACKUP_FILE.logs.tar.gz"
    local logs_dir="/app/logs"
    
    if [ -d "$logs_dir" ]; then
        # Backup apenas dos logs dos últimos 7 dias
        find "$logs_dir" -name "*.log" -mtime -7 -print0 | \
        tar -czf "$logs_backup" --null -T - 2>/dev/null || true
        
        if [ -f "$logs_backup" ]; then
            success "Backup de logs criado: $logs_backup"
        else
            warning "Nenhum log recente encontrado"
        fi
    else
        warning "Diretório de logs não encontrado: $logs_dir"
    fi
}

# Backup de uploads/arquivos do usuário
backup_uploads() {
    log "Fazendo backup de uploads..."
    
    local uploads_backup="$BACKUP_FILE.uploads.tar.gz"
    local uploads_dir="/app/uploads"
    
    if [ -d "$uploads_dir" ] && [ "$(ls -A $uploads_dir)" ]; then
        tar -czf "$uploads_backup" -C "/app" uploads/ 2>/dev/null
        success "Backup de uploads criado: $uploads_backup"
    else
        warning "Diretório de uploads vazio ou não encontrado"
    fi
}

# Criar manifesto do backup
create_manifest() {
    log "Criando manifesto do backup..."
    
    local manifest_file="$BACKUP_FILE.manifest.json"
    
    cat > "$manifest_file" << EOF
{
    "backup_timestamp": "$(date -Iseconds)",
    "backup_type": "automated",
    "database_path": "$DB_PATH",
    "backup_files": [
EOF

    local first=true
    for file in "$BACKUP_DIR"/ippel_backup_$TIMESTAMP.*; do
        if [ -f "$file" ]; then
            if [ "$first" = true ]; then
                first=false
            else
                echo "," >> "$manifest_file"
            fi
            local filename=$(basename "$file")
            local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "unknown")
            echo "        {\"name\": \"$filename\", \"size\": $size}" >> "$manifest_file"
        fi
    done

    cat >> "$manifest_file" << EOF
    ],
    "system_info": {
        "hostname": "$(hostname)",
        "backup_script_version": "1.0",
        "retention_days": $RETENTION_DAYS
    }
}
EOF

    success "Manifesto criado: $manifest_file"
}

# Verificar backups criados
verify_backups() {
    log "Verificando backups criados..."
    
    local backup_count=$(ls -1 "$BACKUP_DIR"/ippel_backup_$TIMESTAMP.* 2>/dev/null | wc -l)
    local total_size=$(du -sh "$BACKUP_DIR"/ippel_backup_$TIMESTAMP.* 2>/dev/null | tail -1 | cut -f1 || echo "0")
    
    if [ "$backup_count" -gt 0 ]; then
        success "Backup concluído: $backup_count arquivo(s), tamanho total: $total_size"
    else
        error "Nenhum arquivo de backup foi criado"
        exit 1
    fi
}

# Limpeza de backups antigos
cleanup_old_backups() {
    log "Limpando backups antigos (retenção: $RETENTION_DAYS dias)..."
    
    local deleted_count=0
    
    # Encontrar e deletar backups mais antigos que RETENTION_DAYS
    find "$BACKUP_DIR" -name "ippel_backup_*" -type f -mtime +$RETENTION_DAYS -print0 | \
    while IFS= read -r -d '' file; do
        rm -f "$file"
        deleted_count=$((deleted_count + 1))
        log "Removido backup antigo: $(basename "$file")"
    done
    
    # Contar backups restantes
    local remaining_count=$(find "$BACKUP_DIR" -name "ippel_backup_*" -type f | wc -l)
    success "Limpeza concluída. Backups restantes: $remaining_count"
}

# Notificação de status (webhook ou email se configurado)
send_notification() {
    local status=$1
    local message=$2
    
    # Se webhook estiver configurado
    if [ -n "${BACKUP_WEBHOOK_URL}" ]; then
        curl -s -X POST "${BACKUP_WEBHOOK_URL}" \
             -H "Content-Type: application/json" \
             -d "{\"status\":\"$status\",\"message\":\"$message\",\"timestamp\":\"$(date -Iseconds)\",\"hostname\":\"$(hostname)\"}" \
             > /dev/null 2>&1 || true
    fi
    
    # Log local sempre
    if [ "$status" = "success" ]; then
        success "$message"
    else
        error "$message"
    fi
}

# Função principal
main() {
    log "=== Iniciando backup automático IPPEL RNC System ==="
    log "Timestamp: $TIMESTAMP"
    
    # Verificações iniciais
    check_permissions
    prepare_backup_dir
    check_disk_space
    
    # Executar backups
    backup_database
    backup_configs
    backup_logs
    backup_uploads
    
    # Finalização
    create_manifest
    verify_backups
    cleanup_old_backups
    
    # Notificação de sucesso
    send_notification "success" "Backup IPPEL RNC concluído com sucesso em $(date)"
    
    log "=== Backup concluído com sucesso ==="
}

# Tratamento de erro
handle_error() {
    local exit_code=$?
    error "Erro durante o backup (código: $exit_code)"
    
    # Limpar backups parciais em caso de erro
    rm -f "$BACKUP_FILE".*
    
    # Notificação de erro
    send_notification "error" "Backup IPPEL RNC falhou em $(date)"
    
    exit $exit_code
}

# Configurar tratamento de erros
trap handle_error ERR

# Executar backup se script for chamado diretamente
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

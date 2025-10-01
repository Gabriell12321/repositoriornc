#!/bin/bash
# Script de deployment automatizado - IPPEL RNC System
# Suporta desenvolvimento, teste e produção

set -e

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
ENV_FILE="$PROJECT_ROOT/.env"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
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

# Função para verificar pré-requisitos
check_prerequisites() {
    log "Verificando pré-requisitos..."
    
    # Docker
    if ! command -v docker &> /dev/null; then
        error "Docker não encontrado. Instale o Docker primeiro."
        exit 1
    fi
    
    # Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose não encontrado. Instale o Docker Compose primeiro."
        exit 1
    fi
    
    # Arquivo .env
    if [ ! -f "$ENV_FILE" ]; then
        warning "Arquivo .env não encontrado. Copiando .env.example..."
        cp "$PROJECT_ROOT/.env.example" "$ENV_FILE"
        warning "Configure o arquivo .env antes de continuar!"
        exit 1
    fi
    
    success "Pré-requisitos verificados"
}

# Função para backup de segurança
create_backup() {
    log "Criando backup de segurança..."
    
    local backup_dir="$PROJECT_ROOT/backups"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$backup_dir/deployment_backup_$timestamp.tar.gz"
    
    mkdir -p "$backup_dir"
    
    # Backup dos dados da aplicação
    if [ -d "$PROJECT_ROOT/data" ]; then
        tar -czf "$backup_file" -C "$PROJECT_ROOT" data/
        success "Backup criado: $backup_file"
    else
        warning "Diretório de dados não encontrado. Primeiro deployment?"
    fi
}

# Função para construir imagens
build_images() {
    local environment=${1:-production}
    
    log "Construindo imagens Docker para ambiente: $environment"
    
    cd "$PROJECT_ROOT"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose build --no-cache ippel-app
    else
        docker compose build --no-cache ippel-app
    fi
    
    success "Imagens construídas com sucesso"
}

# Função para executar testes
run_tests() {
    log "Executando testes automatizados..."
    
    cd "$PROJECT_ROOT"
    
    # Criar container temporário para testes
    docker run --rm \
        -v "$(pwd):/app" \
        -w /app \
        python:3.11-slim \
        sh -c "
            pip install -r requirements.txt
            python -m pytest tests/ -v --tb=short
        " || {
        error "Testes falharam!"
        return 1
    }
    
    success "Todos os testes passaram"
}

# Função para deploy
deploy() {
    local environment=${1:-production}
    local skip_tests=${2:-false}
    
    log "Iniciando deployment para ambiente: $environment"
    
    cd "$PROJECT_ROOT"
    
    # Executar testes se não foi solicitado pular
    if [ "$skip_tests" != "true" ] && [ "$environment" = "production" ]; then
        run_tests || {
            error "Deploy cancelado devido a falhas nos testes"
            exit 1
        }
    fi
    
    # Parar serviços existentes
    log "Parando serviços existentes..."
    if command -v docker-compose &> /dev/null; then
        docker-compose down --remove-orphans
    else
        docker compose down --remove-orphans
    fi
    
    # Construir imagens
    build_images "$environment"
    
    # Inicializar diretórios necessários
    mkdir -p data logs backups uploads
    
    # Configurar perfil baseado no ambiente
    local profile_args=""
    case $environment in
        "development")
            profile_args="--profile development"
            ;;
        "production")
            profile_args="--profile monitoring --profile backup"
            ;;
        "testing")
            profile_args=""
            ;;
    esac
    
    # Iniciar serviços
    log "Iniciando serviços..."
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d $profile_args
    else
        docker compose up -d $profile_args
    fi
    
    # Aguardar aplicação estar pronta
    log "Aguardando aplicação inicializar..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost:5000/health > /dev/null 2>&1; then
            success "Aplicação está executando e saudável"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            error "Aplicação falhou ao inicializar após $max_attempts tentativas"
            show_logs
            exit 1
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    # Mostrar status dos serviços
    show_status
    
    success "Deploy concluído com sucesso!"
    log "Aplicação disponível em: http://localhost:5000"
    
    if [ "$environment" = "production" ]; then
        log "Monitoramento disponível em: http://localhost:3000 (Grafana)"
        log "Métricas disponíveis em: http://localhost:9090 (Prometheus)"
    fi
}

# Função para mostrar status dos serviços
show_status() {
    log "Status dos serviços:"
    
    cd "$PROJECT_ROOT"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
}

# Função para mostrar logs
show_logs() {
    local service=${1:-ippel-app}
    
    cd "$PROJECT_ROOT"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose logs --tail=50 "$service"
    else
        docker compose logs --tail=50 "$service"
    fi
}

# Função para rollback
rollback() {
    warning "Executando rollback..."
    
    cd "$PROJECT_ROOT"
    
    # Parar serviços atuais
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    
    # Restaurar backup mais recente
    local backup_dir="$PROJECT_ROOT/backups"
    local latest_backup=$(ls -t "$backup_dir"/deployment_backup_*.tar.gz 2>/dev/null | head -1)
    
    if [ -n "$latest_backup" ]; then
        log "Restaurando backup: $latest_backup"
        tar -xzf "$latest_backup" -C "$PROJECT_ROOT"
        success "Backup restaurado"
    else
        warning "Nenhum backup encontrado para rollback"
    fi
    
    # Reiniciar com configuração anterior
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    success "Rollback concluído"
}

# Função para limpeza
cleanup() {
    warning "Executando limpeza do sistema..."
    
    cd "$PROJECT_ROOT"
    
    # Parar e remover containers
    if command -v docker-compose &> /dev/null; then
        docker-compose down --volumes --remove-orphans
    else
        docker compose down --volumes --remove-orphans
    fi
    
    # Remover imagens órfãs
    docker image prune -f
    
    # Remover volumes não utilizados
    docker volume prune -f
    
    success "Limpeza concluída"
}

# Função de ajuda
show_help() {
    cat << EOF
IPPEL RNC System - Script de Deployment

Uso: $0 [COMANDO] [OPÇÕES]

Comandos:
    deploy [ENV]        Deploy da aplicação (ENV: development|production|testing)
    status              Mostrar status dos serviços
    logs [SERVICE]      Mostrar logs (padrão: ippel-app)
    test               Executar testes
    backup             Criar backup manual
    rollback           Fazer rollback para versão anterior
    cleanup            Limpar containers e imagens não utilizadas
    help               Mostrar esta ajuda

Opções:
    --skip-tests       Pular testes durante o deploy
    --no-backup        Não criar backup antes do deploy

Exemplos:
    $0 deploy production                    # Deploy completo para produção
    $0 deploy development --skip-tests      # Deploy para desenvolvimento sem testes
    $0 logs nginx-proxy                     # Ver logs do Nginx
    $0 status                               # Ver status de todos os serviços

EOF
}

# Função principal
main() {
    local command=${1:-help}
    shift || true
    
    case $command in
        "deploy")
            local environment=${1:-production}
            local skip_tests=false
            local no_backup=false
            
            # Processar opções
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --skip-tests)
                        skip_tests=true
                        shift
                        ;;
                    --no-backup)
                        no_backup=true
                        shift
                        ;;
                    *)
                        shift
                        ;;
                esac
            done
            
            check_prerequisites
            
            if [ "$no_backup" != "true" ] && [ "$environment" = "production" ]; then
                create_backup
            fi
            
            deploy "$environment" "$skip_tests"
            ;;
            
        "status")
            show_status
            ;;
            
        "logs")
            show_logs "$1"
            ;;
            
        "test")
            check_prerequisites
            run_tests
            ;;
            
        "backup")
            create_backup
            ;;
            
        "rollback")
            rollback
            ;;
            
        "cleanup")
            cleanup
            ;;
            
        "help"|*)
            show_help
            ;;
    esac
}

# Executar função principal com todos os argumentos
main "$@"

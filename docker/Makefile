# Makefile para IPPEL RNC System
# Comandos simplificados para desenvolvimento e deployment

.PHONY: help install dev test build deploy clean lint format security backup

# Configurações
PYTHON_VERSION := 3.11
VENV_DIR := venv
APP_NAME := ippel-rnc
DOCKER_IMAGE := $(APP_NAME):latest

# Cores para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Função para print colorido
define print_info
	@echo -e "$(BLUE)ℹ $(1)$(NC)"
endef

define print_success
	@echo -e "$(GREEN)✓ $(1)$(NC)"
endef

define print_warning
	@echo -e "$(YELLOW)⚠ $(1)$(NC)"
endef

define print_error
	@echo -e "$(RED)✗ $(1)$(NC)"
endef

# Help - comando padrão
help: ## Mostrar esta ajuda
	@echo "IPPEL RNC System - Comandos disponíveis:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Instalação e configuração
install: ## Instalar dependências
	$(call print_info,"Instalando dependências do sistema...")
	@python -m venv $(VENV_DIR)
	@$(VENV_DIR)/bin/pip install --upgrade pip
	@$(VENV_DIR)/bin/pip install -r requirements.txt
	@$(VENV_DIR)/bin/pip install -r requirements_production.txt
	$(call print_success,"Dependências instaladas")

install-dev: install ## Instalar dependências de desenvolvimento
	$(call print_info,"Instalando dependências de desenvolvimento...")
	@$(VENV_DIR)/bin/pip install pytest pytest-cov flake8 black isort bandit safety
	$(call print_success,"Dependências de desenvolvimento instaladas")

# Desenvolvimento
dev: ## Executar aplicação em modo desenvolvimento
	$(call print_info,"Iniciando aplicação em modo desenvolvimento...")
	@export FLASK_ENV=development && $(VENV_DIR)/bin/python main_system.py

dev-docker: ## Executar com Docker em modo desenvolvimento
	$(call print_info,"Iniciando com Docker (desenvolvimento)...")
	@docker-compose up --build

# Testes
test: ## Executar testes
	$(call print_info,"Executando testes...")
	@$(VENV_DIR)/bin/python -m pytest tests/ -v
	$(call print_success,"Testes concluídos")

test-coverage: ## Executar testes com cobertura
	$(call print_info,"Executando testes com análise de cobertura...")
	@$(VENV_DIR)/bin/python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term
	$(call print_success,"Relatório de cobertura gerado em htmlcov/")

test-docker: ## Executar testes no Docker
	$(call print_info,"Executando testes no Docker...")
	@docker run --rm -v $(PWD):/app -w /app python:$(PYTHON_VERSION)-slim sh -c "pip install -r requirements.txt && python -m pytest tests/ -v"

# Qualidade de código
lint: ## Analisar qualidade do código
	$(call print_info,"Analisando qualidade do código...")
	@$(VENV_DIR)/bin/flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	@$(VENV_DIR)/bin/flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	$(call print_success,"Análise de código concluída")

format: ## Formatar código
	$(call print_info,"Formatando código...")
	@$(VENV_DIR)/bin/black .
	@$(VENV_DIR)/bin/isort .
	$(call print_success,"Código formatado")

security: ## Análise de segurança
	$(call print_info,"Executando análise de segurança...")
	@$(VENV_DIR)/bin/safety check -r requirements.txt
	@$(VENV_DIR)/bin/bandit -r . -x tests/
	$(call print_success,"Análise de segurança concluída")

# Build e Deploy
build: ## Construir imagem Docker
	$(call print_info,"Construindo imagem Docker...")
	@docker build -t $(DOCKER_IMAGE) .
	$(call print_success,"Imagem construída: $(DOCKER_IMAGE)")

deploy-dev: build ## Deploy para desenvolvimento
	$(call print_info,"Deploy para ambiente de desenvolvimento...")
	@./scripts/deploy.sh deploy development
	$(call print_success,"Deploy de desenvolvimento concluído")

deploy-prod: ## Deploy para produção
	$(call print_info,"Deploy para ambiente de produção...")
	@./scripts/deploy.sh deploy production
	$(call print_success,"Deploy de produção concluído")

# Banco de dados
db-init: ## Inicializar banco de dados
	$(call print_info,"Inicializando banco de dados...")
	@$(VENV_DIR)/bin/python init_system.py
	$(call print_success,"Banco de dados inicializado")

db-backup: ## Fazer backup do banco
	$(call print_info,"Criando backup do banco de dados...")
	@./scripts/deploy.sh backup
	$(call print_success,"Backup criado")

db-migrate: ## Executar migrações
	$(call print_info,"Executando migrações de banco...")
	@$(VENV_DIR)/bin/python -c "from scripts.generate_architecture_report import migrate_database; migrate_database()"
	$(call print_success,"Migrações executadas")

# Monitoramento e logs
logs: ## Visualizar logs da aplicação
	@docker-compose logs -f ippel-app

logs-nginx: ## Visualizar logs do Nginx
	@docker-compose logs -f nginx-proxy

status: ## Status dos serviços
	$(call print_info,"Status dos serviços:")
	@docker-compose ps

health: ## Verificar saúde da aplicação
	$(call print_info,"Verificando saúde da aplicação...")
	@curl -f http://localhost:5000/health || ($(call print_error,"Aplicação não está saudável") && exit 1)
	$(call print_success,"Aplicação está saudável")

# Utilitários
clean: ## Limpar arquivos temporários e cache
	$(call print_info,"Limpando arquivos temporários...")
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf htmlcov/
	@rm -rf .coverage
	@rm -rf .pytest_cache/
	$(call print_success,"Limpeza concluída")

clean-docker: ## Limpar recursos Docker
	$(call print_info,"Limpando recursos Docker...")
	@docker-compose down --volumes --remove-orphans
	@docker system prune -f
	@docker volume prune -f
	$(call print_success,"Recursos Docker limpos")

backup: ## Criar backup completo
	$(call print_info,"Criando backup completo...")
	@mkdir -p backups
	@tar -czf backups/full_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz \
		--exclude='venv' \
		--exclude='node_modules' \
		--exclude='*.pyc' \
		--exclude='__pycache__' \
		--exclude='.git' \
		.
	$(call print_success,"Backup completo criado")

# Relatórios
report: ## Gerar relatório de arquitetura
	$(call print_info,"Gerando relatório de arquitetura...")
	@$(VENV_DIR)/bin/python scripts/generate_architecture_report.py
	$(call print_success,"Relatório gerado")

metrics: ## Coletar métricas da aplicação
	$(call print_info,"Coletando métricas...")
	@curl -s http://localhost:5000/metrics | head -20
	$(call print_success,"Métricas coletadas")

# Setup completo
setup: install-dev db-init ## Setup completo para desenvolvimento
	$(call print_info,"Configuração completa para desenvolvimento...")
	@cp .env.example .env
	$(call print_warning,"Configure o arquivo .env antes de executar a aplicação")
	$(call print_success,"Setup completo finalizado")

# Verificação completa
check: lint test security ## Verificação completa (lint, test, security)
	$(call print_success,"Todas as verificações passaram")

# Pipeline CI/CD local
ci: clean install-dev check build ## Pipeline CI/CD local completa
	$(call print_success,"Pipeline CI/CD local concluída com sucesso")

# Reset completo
reset: clean clean-docker setup ## Reset completo do ambiente
	$(call print_success,"Ambiente resetado completamente")

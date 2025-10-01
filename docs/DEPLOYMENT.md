# IPPEL RNC System - Documentação de Deployment
# Guia completo para desenvolvimento, teste e produção

## 🚀 Guia de Deploy

### Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Git
- Make (opcional, mas recomendado)

### Instalação Rápida

```bash
# 1. Clonar repositório
git clone <repository-url>
cd ippel-rnc-system

# 2. Configurar ambiente
cp .env.example .env
# Editar .env com suas configurações

# 3. Executar setup
make setup

# 4. Iniciar aplicação
make dev
```

## 🏗️ Ambientes Disponíveis

### Desenvolvimento

```bash
# Opção 1: Com Makefile
make dev

# Opção 2: Docker Compose direto
docker-compose up --build

# Opção 3: Modo Python local
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python main_system.py
```

**Características do ambiente de desenvolvimento:**
- Hot reload automático
- Debug habilitado
- MailHog para testes de email
- Logs detalhados
- Banco com dados de teste

**URLs de acesso:**
- Aplicação: http://localhost:5000
- MailHog: http://localhost:8025
- Logs: `docker-compose logs -f ippel-app`

### Teste

```bash
# Executar todos os testes
make test

# Testes com cobertura
make test-coverage

# Testes no Docker
make test-docker

# CI/CD completo local
make ci
```

### Produção

```bash
# Deploy completo para produção
./scripts/deploy.sh deploy production

# Ou com Makefile
make deploy-prod

# Verificar status
make status

# Ver logs
make logs
```

**Características do ambiente de produção:**
- SSL/HTTPS habilitado
- Rate limiting
- Monitoramento com Prometheus/Grafana
- Backup automático
- Nginx como proxy reverso
- Logs estruturados

## 📊 Monitoramento

### URLs de Monitoramento (Produção)

- **Grafana**: http://localhost:3000
  - Usuário: admin
  - Senha: definida em `GRAFANA_ADMIN_PASSWORD`

- **Prometheus**: http://localhost:9090

- **Health Check**: http://localhost:5000/health

### Métricas Disponíveis

- Performance da aplicação
- Uso de recursos (CPU, memória, disco)
- Estatísticas de RNCs
- Número de usuários ativos
- Tempo de resposta das APIs

## 🔒 Segurança

### Configurações de Produção

1. **Alterar chaves secretas**:
   ```bash
   # Gerar nova SECRET_KEY
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Configurar HTTPS**:
   - Colocar certificados em `./ssl/`
   - Configurar domínio em `.env`

3. **Firewall**:
   ```bash
   # Permitir apenas portas necessárias
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw allow 22/tcp
   ```

4. **Backup**:
   - Configurado automaticamente via cron
   - Backups em `./backups/`
   - Retenção configurável

## 🛠️ Comandos Úteis

### Makefile (Recomendado)

```bash
make help              # Ver todos os comandos
make install           # Instalar dependências
make dev              # Modo desenvolvimento
make test             # Executar testes
make build            # Build Docker
make deploy-prod      # Deploy produção
make backup           # Backup manual
make clean            # Limpar arquivos
make logs             # Ver logs
make status           # Status dos serviços
```

### Docker Compose

```bash
# Iniciar serviços
docker-compose up -d

# Ver logs
docker-compose logs -f [service]

# Status
docker-compose ps

# Parar serviços
docker-compose down

# Rebuild
docker-compose up --build

# Executar comando em container
docker-compose exec ippel-app python manage.py [command]
```

### Scripts Personalizados

```bash
# Deploy com opções
./scripts/deploy.sh deploy production --skip-tests
./scripts/deploy.sh backup
./scripts/deploy.sh rollback
./scripts/deploy.sh cleanup

# Análise de banco
python analyze_database_structure.py

# Relatório de arquitetura
python scripts/generate_architecture_report.py
```

## 📁 Estrutura do Projeto

```
ippel-rnc-system/
├── 📄 Dockerfile                 # Container principal
├── 📄 docker-compose.yml         # Orquestração
├── 📄 docker-compose.override.yml # Override para dev
├── 📄 Makefile                   # Comandos automatizados
├── 📄 .env.example              # Exemplo de configuração
├── 📄 requirements.txt          # Dependências Python
├── 📁 scripts/                  # Scripts de automação
├── 📁 nginx/                    # Configuração Nginx
├── 📁 monitoring/               # Prometheus/Grafana
├── 📁 .github/workflows/        # CI/CD GitHub Actions
├── 📁 static/                   # Arquivos estáticos
├── 📁 templates/                # Templates HTML
├── 📁 routes/                   # Rotas da aplicação
├── 📁 services/                 # Serviços (monitoramento, etc.)
├── 📁 tests/                    # Testes automatizados
└── 📁 data/                     # Dados persistentes
```

## 🔧 Solução de Problemas

### Problemas Comuns

#### Container não inicia
```bash
# Verificar logs
docker-compose logs ippel-app

# Verificar saúde
curl http://localhost:5000/health

# Restart
docker-compose restart ippel-app
```

#### Banco de dados corrompido
```bash
# Restaurar último backup
./scripts/deploy.sh rollback

# Ou backup específico
sqlite3 ippel_system.db ".backup backup_file.db"
```

#### Performance lenta
```bash
# Verificar recursos
docker stats

# Ver métricas
curl http://localhost:5000/metrics

# Logs de performance
docker-compose logs ippel-app | grep "slow"
```

#### Problemas de permissão
```bash
# Corrigir permissões
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh
```

### Logs Importantes

```bash
# Logs da aplicação
docker-compose logs -f ippel-app

# Logs do Nginx
docker-compose logs -f nginx-proxy

# Logs do sistema
tail -f logs/app.log
tail -f logs/error.log
```

## 📈 Escalabilidade

### Scaling Horizontal

```bash
# Múltiplas instâncias da aplicação
docker-compose up --scale ippel-app=3

# Load balancer automático via Nginx
```

### Otimizações

1. **Redis Cache**: Habilitado por padrão
2. **CDN**: Configurar para arquivos estáticos
3. **Database**: Índices otimizados automaticamente
4. **Compression**: Gzip habilitado no Nginx

## 🔄 CI/CD

### GitHub Actions

- **Push em `develop`**: Deploy automático para desenvolvimento
- **Push em `main`**: Deploy automático para produção
- **Pull Request**: Executa testes automaticamente
- **Release**: Cria tag e deploy com versionamento

### Pipeline Local

```bash
# Executar pipeline completa
make ci

# Apenas testes
make check
```

## 📞 Suporte

### Contatos
- **Desenvolvedor**: [seu-email@domain.com]
- **DevOps**: [devops@domain.com]
- **Suporte**: [suporte@ippel.com.br]

### Recursos
- **Documentação**: `/docs`
- **API Docs**: http://localhost:5000/api/docs
- **Status Page**: http://localhost:5000/health/deep

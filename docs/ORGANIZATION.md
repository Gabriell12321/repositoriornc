# 📁 Estrutura de Diretórios do Projeto IPPEL RNC

## 📂 Organização de Pastas

### `/app` - Aplicação Principal
- Módulos principais da aplicação
- Rotas organizadas por funcionalidade

### `/routes` - Rotas Flask
- Blueprints organizados por domínio
- APIs REST

### `/services` - Serviços e Lógica de Negócio
- Camada de serviços
- Integrações externas

### `/templates` - Templates HTML/Jinja2
- Views da aplicação
- Componentes reutilizáveis

### `/static` - Arquivos Estáticos
- CSS, JavaScript, imagens
- Assets do frontend

### `/scripts` - Scripts Utilitários
- `/scripts/check` - Scripts de verificação
- `/scripts/fix` - Scripts de correção
- `/scripts/import` - Scripts de importação de dados
- `/scripts/setup` - Scripts de configuração inicial

### `/tests` - Testes Automatizados
- Testes unitários
- Testes de integração
- Scripts de debug

### `/docs` - Documentação
- `/docs/corrections` - Documentos de correções aplicadas
- `/docs/studies` - Estudos e análises do projeto
- Documentação técnica e de API

### `/migrations` - Migrações de Banco de Dados
- Scripts de migração
- Histórico de mudanças no schema

### `/config` - Configurações
- Arquivos de configuração
- Variáveis de ambiente

### `/data` - Dados e Banco de Dados
- Arquivos de banco de dados SQLite
- Backups

### `/logs` - Logs da Aplicação
- Logs de erro
- Logs de acesso

### `/temp` - Arquivos Temporários
- Arquivos de teste
- Arquivos temporários de processamento

### `/docker` - Configuração Docker
- Dockerfiles
- Docker Compose

### `/monitoring` - Monitoramento
- Scripts de monitoramento
- Dashboards

## 🗂️ Arquivos Principais na Raiz

- `server_form.py` - Servidor principal Flask
- `main_system.py` - Sistema principal
- `server.py` - Servidor alternativo
- `index.html` - Página inicial
- `requirements.txt` - Dependências Python
- `README.md` - Documentação principal
- `.gitignore` - Arquivos ignorados pelo Git
- `database.db` - Banco de dados SQLite
- `ippel_system.db` - Banco do sistema

## 📝 Convenções de Nomenclatura

### Scripts
- `check_*.py` - Scripts de verificação
- `fix_*.py` - Scripts de correção
- `test_*.py` - Scripts de teste
- `import_*.py` - Scripts de importação
- `setup_*.py` - Scripts de configuração

### Documentos
- `CORRECAO_*.md` - Documentos de correções
- `ESTUDO_*.md` - Documentos de estudos
- `RELATORIO_*.md` - Relatórios técnicos

## 🔄 Última Organização
- Data: 06/10/2025
- Todos os arquivos foram organizados nas respectivas pastas
- Scripts de teste movidos para `/tests`
- Documentação consolidada em `/docs`

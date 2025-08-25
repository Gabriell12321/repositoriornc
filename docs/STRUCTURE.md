# Estrutura organizada

Esta estrutura agrupa arquivos por função para manter a raiz limpa e intuitiva.

- docs/ — documentações (.md) exceto README.md da raiz
- logs/ — logs do sistema (ippel_system.log, email_system.log, ippel_security.log)
- backups/ — backups do banco (ippel_system_backup_*.db)
- tests/ — testes Python (test_*.py, debug_*.py)
  - tests/html/ — arquivos HTML de teste (test_*.html, debug_*.html)
- scripts/ — scripts .bat/.sh para iniciar/parar/instalar
- db/ — schema do banco (database_schema.sql). O arquivo de banco de dados em produção fica na raiz (ippel_system.db)
- data/ — opcional: JSONs auxiliares (se usar o modo --move-json)

Para aplicar esta organização:

1. Execute o dry-run:
   - Terminal > Run Task > "Organizar - Dry Run"
2. Se estiver tudo certo, aplique:
   - "Organizar - Aplicar (sem JSON)"
   - ou "Organizar - Aplicar (inclusive JSON)" se quiser mover JSONs soltos para data/

Observações:
- Mantivemos na raiz os diretórios e arquivos de runtime: static/, templates/, routes/, services/, server_form.py, ippel_system.db.
- Após mover JSONs, ajuste caminhos no código se necessário (por exemplo, trocar 'api_chart_data.json' para 'data/api_chart_data.json').

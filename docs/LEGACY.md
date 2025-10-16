# Componentes Legados e Experimentos

Este documento identifica arquivos e caminhos que não devem ser usados em produção e explica por quê.

## Por que isolar?

- Evitar confusão entre tabelas `rncs` (atual) e `rnc_reports` (legado).
- Reduzir risco de endpoints divergentes e schemas inconsistentes.
- Tornar mais clara a inicialização do sistema (um único servidor Flask).

## Arquivos marcados como legados/experimentais

- `main_system.py`
  - Implementa um servidor Flask com `rnc_reports`, fluxos e páginas antigas.
  - Tem endpoints e gráficos próprios, não integrados ao blueprint atual.
  - Diverge do modelo de permissões/compartilhamento e pode quebrar o banco atual.

- `server.py`
  - Mini servidor SMTP/HTML para envio de email (demo/antigo), com `/send-email` e `/test-email`.
  - Usa `index.html` de interface simplificada.
  - Não faz parte do fluxo atual de autenticação/permissões.

- Templates possivelmente legados
  - `templates/view_rnc_public.html`: não há rota ativa principal apontando para este template no backend moderno. Se o objetivo for um link público, deve-se implementar rota dedicada com token de acesso temporal e máscara de dados. Caso contrário, considerar remoção/arquivamento.

## Recomendações

- Produção/Desenvolvimento: use apenas `server_form.py`.
- Migração de quaisquer dados de `rnc_reports` para `rncs` deve ser feita via script dedicado (fora do escopo atual).
- Se algum comportamento dos legados for necessário, reimplementar integrando aos serviços/blueprints atuais.

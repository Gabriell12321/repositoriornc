# Arquitetura do Sistema IPPEL – Relatórios de Não Conformidade (RNC)

Este documento descreve a arquitetura completa: componentes, fluxos, banco de dados, segurança, performance e integrações.

## Visão Geral

- Backend principal: Flask em `server_form.py` (porta padrão 5001).
- Blueprints:
  - `routes/auth.py`: login/logout, lockout progressivo, emissão/rotação de JWT (opcional).
  - `routes/api.py`: utilitários autenticados (CSRF, avatar, upload de imagem com sanitização).
  - `routes/rnc.py`: criação/listagem/edição/finalização/compartilhamento/visualização de RNCs.
- Serviços opcionais: `services/*_client.py` (Julia/Go/Kotlin/Swift/Scala/Nim/V/Zig/Crystal/Deno).
- Frontend: templates Jinja em `templates/` e assets em `static/` com `asset_url()` (minificados + cache-busting).
- Banco: SQLite (`ippel_system.db`) com WAL, PRAGMAs de performance, migrações idempotentes.

Observação: há componentes legados em `main_system.py` e `server.py` (ver `docs/LEGACY.md`). Use somente `server_form.py`.

## Pontos de Entrada

- Produção/Dev: `server_form.py`.
- Scripts: `scripts/*.bat` para iniciar/parar, instalar dependências, etc.
- Serviços externos: sob `services/` (backend tolera ausência com respostas 404 descritivas).

## Estrutura de Pastas (essencial)

- `routes/` — Blueprints (auth, api, rnc)
- `services/` — Serviços de infraestrutura (db, cache, permissions, groups, rnc, clients, segurança)
- `templates/` — Páginas Jinja (dashboards, RNC, admin)
- `static/` — JS/CSS/imagens; pode conter `ts/` (TypeScript) e compilados
- `scripts/` — inicialização e utilitários
- `logs/` — logs (ex.: `security.log`)
- `data/`, `db/`, `backups/` — dados e backups
- `docs/` — documentação

## Banco de Dados e Pool de Conexões

- SQLite: arquivo `ippel_system.db` com modo WAL.
- PRAGMAs default (aplicados por conexão): `journal_mode=WAL`, `synchronous=NORMAL`, `cache_size=10000`, `temp_store=MEMORY`, `mmap_size=268435456`.
- Pool: `services/db.py` mantém fila de até 150 conexões (`queue.Queue`).
  - `warm_pool()` pré-aquece conexões.
  - `get_db_connection()` pega do pool (ou cria novo) e `return_db_connection()` devolve com rollback defensivo.
- Tabelas principais:
  - `users` (id, name, email, password_hash, department, role, permissions JSON, group_id, avatar_key/prefs, is_active, created_at)
  - `groups` e `group_permissions (group_id, permission_name, permission_value)`
  - `rncs` (id, rnc_number, title, description, equipment, client, priority, status, user_id, assigned_user_id, is_deleted, deleted_at, finalized_at, created_at, updated_at, price, disposições, inspeções, assinaturas; colunas extras garantidas por `ensure_rnc_extra_columns()`)
  - `rnc_shares (rnc_id, shared_by_user_id, shared_with_user_id, permission_level, created_at)` com UNIQUE (rnc_id, shared_with_user_id)
  - Auxiliares: `chat_messages`, `notifications`, `private_messages`
- Índices criados (em criação/uso): `rncs(created_at)`, `rncs(status)`, `rncs(user_id)`, `rncs(assigned_user_id)`, `rncs(client)`, `rncs(equipment)`, `rncs(priority)`, `rncs(is_deleted)`, `rncs(finalized_at)`.
- Backups: thread agenda snapshots periódicos para `IPPEL_BACKUP_DIR` (ou fallback na pasta do projeto). Nome `ippel_system_backup_<timestamp>.db`.

## Autenticação, Sessão e JWT

- Sessões Flask: cookies HttpOnly, SameSite=Lax (`SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE='Lax'`). Secret persistido em `ippel_secret.key` ou `IPPEL_SECRET_KEY`.
- Login (POST `/api/login`):
  - Rate limit aplicado se disponível.
  - Lockout progressivo (services/lockout) antes da verificação de senha.
  - Em caso de sucesso: popula `session` (user_id, name, email, department, role) e emite `tokens.access` e `tokens.refresh` (se `services/jwt_auth.py` estiver configurado).
- Logout (GET `/api/logout`): limpa sessão, tenta revogar refresh via cabeçalho `X-Refresh-JTI`.
- JWT middleware: lê `Authorization: Bearer`, decodifica, coloca `g.user_id` e espelha em `session` se necessário (compatibilidade com decoradores).

## Permissões e Autorização

- `services/permissions.py` implementa:
  - `has_permission(user_id, name)`: Admin tem todas; senão, consulta `group_permissions`; fallback por departamento via `has_department_permission`.
  - `has_department_permission`: regras por `department` (Administração/TI têm amplo acesso; Qualidade vê gráficos/relatórios/finalizados; ações básicas abertas para todos: ver/editar próprias RNCs, ver grupos/usuários para atribuição).
- Permissões usadas (principais): `create_rnc`, `edit_own_rnc`, `edit_all_rncs`, `view_own_rnc`, `view_all_rncs`, `view_finalized_rncs`, `reply_rncs`, `delete_rnc`, `view_charts`, `view_reports`, `admin_access`, `manage_users`, `view_engineering_rncs`, `view_all_departments_rncs`, `view_levantamento_14_15`, `update_avatar`, `view_groups_for_assignment`, `view_users_for_assignment`.
- Compartilhamento: `rnc_shares` concede acesso (pelo menos leitura) a usuários específicos. Algumas ações aceitam acesso se compartilhado (reply/update limitado), conforme `routes/rnc.py`.

## Proteção de Endpoints (CSRF, Allowlist)

- `services/endpoint_protection.py`:
  - `ensure_csrf_token()`: gera/retorna token na sessão.
  - `csrf_protect(enforce=None)`: valida headers `X-CSRF-Token`/`X-XSRF-TOKEN` em métodos de escrita. Enforce controlado via `CSRF_ENFORCE` (default off); sempre loga violações.
  - `require_permission('perm')`: verifica sessão/JWT e permissão antes de executar rota.
  - `require_ip_allowlist(env='ADMIN_IP_ALLOWLIST')`: bloqueia acesso a IPs fora da allowlist (CSV em env).

## Rate Limiting

- `services/rate_limit.py` fornece inicialização do Limiter e decorator `rate_limit()`.
- Storage configurável via `REDIS_URL` (ou `memory://` por padrão). Estratégia: fixed-window.
- Fallback seguro: se a lib não estiver instalada, os decoradores viram no-op.

## Logging de Segurança (JSON por linha)

- `services/security_log.py` configura logger `security` (arquivo rotativo `logs/security.log`, ~5MB x5) e console.
- Função `sec_log(cat, act, ip=..., user_id=..., email=..., status=..., details=...)` escreve eventos com timestamp ISO UTC e nível INFO.
- Categorias comuns: `auth` (login success/fail, lockout), `api` (unauthorized), `csrf` (violation), `csp` (violation_report), `rate_limit`.

## Modelo de Dados de RNC

- Colunas principais (resumo):
  - Identificação: `id`, `rnc_number` (gerado com timestamp/ano/mês/dia/hora/min/seg).
  - Conteúdo: `title`, `description` (mapeável por labels no template), `equipment`, `client`, `price`.
  - Status: `priority` (Baixa/Média/Alta/Crítica), `status` (Pendente/Finalizado), `finalized_at`.
  - Autor/atribuição: `user_id` (criador), `assigned_user_id` (responsável atual).
  - Disposições/Inspeção: flags booleanas `disposition_*`, `inspection_*` e campo livre `inspection_ver_rnc`.
  - Assinaturas: `signature_*_name` e `signature_*_date` (ao menos uma assinatura obrigatória em create/update).
  - Datas: `created_at`, `updated_at`, `deleted_at` (soft delete não é usado; exclusão é hard em endpoint atual).

## Fluxos de RNC (Autorização + Negócio)

- Criar (POST `/api/rnc/create`):
  - Requer sessão; verifica colunas presentes em `rncs` dinamicamente e insere apenas as válidas.
  - Gera `rnc_number` baseado em data/hora atual.
  - Aceita `shared_group_ids`: agenda compartilhamento assíncrono via thread (obtém usuários por grupo e cria registros em `rnc_shares`).

- Listar (GET `/api/rnc/list`):
  - Parâmetro `tab=active|finalized` filtra por status; aplica regra de visibilidade (criador/atribuído/compartilhado ou permissões view_all_*).
  - Paginação por cursor: `next_cursor` com ancora em `r.id` (ordem DESC; próximo lote usa `r.id < cursor`).
  - Cache: chave `rncs_list_<user>_<tab>_<cursor>_<limit>` com TTL ~120s (Redis/In-memory). `Cache-Control` público 120s.

- Detalhar (GET `/api/rnc/get/<id>`):
  - Normaliza campos booleanos `disposition_*` e `inspection_*` para True/False.

- Atualizar (PUT `/api/rnc/<id>/update`):
  - Autorização: criador OU `edit_all_rncs` OU `edit_own_rnc` (se criador) OU `admin_access` OU regras por departamento (ex.: Engenharia) OU `reply_rncs` OU se compartilhado com usuário.
  - Valida presença de pelo menos uma assinatura (`signature_*_name` diferente de vazio/NOME).
  - Atualiza campos textuais/flags, datas de assinatura com `COALESCE(NULLIF(...,''), atual)`.
  - Limpa/invalida caches relevantes (listas/charts).

- Finalizar (POST `/api/rnc/<id>/finalize`):
  - Apenas criador (ou admin) pode finalizar. Seta `status='Finalizado'` e `finalized_at=NOW`.

- Responder/Reabrir (POST `/api/rnc/<id>/reply`):
  - Permitido para criador, atribuído, admin, quem tem `reply_rncs` ou quem recebeu share.
  - Seta `status='Pendente'`, limpa `finalized_at` e atribui `assigned_user_id = user atual`.

- Excluir (DELETE `/api/rnc/<id>/delete`):
  - Apenas criador ou admin. Remove de `rncs`, `rnc_shares`, `chat_messages`; invalida caches.

## Cache e Paginação

- Cache de consultas: `services/cache.py` provê in-memory (e Redis se configurado). TTL curto (tipicamente 120s). Invalidação:
  - Em mutações (create/update/delete/finalize/reply), limpa chaves que iniciam com `rncs_list_`/`charts_`.
- Paginação cursor-based:
  - `parse_cursor_limit(request, default_limit, max_limit)` lê `cursor` e `limit` (limita a 50k em listagem principal).
  - `compute_window(rows, limit, id_index=0)` recorta ao limite e calcula `has_more` e `next_cursor`.

## CSP e Headers de Segurança

- Talisman (se instalado) define CSP base com `'unsafe-inline'` temporário para JS/estilos por compatibilidade (ver `docs/csp_migration.md`).
- Report-Only paralelo informa violações em `/csp-report` (registradas no `security.log`).
- Fallback manual aplica CSP mínima e também um Report-Only.

## Upload/Sanitização de Imagens

- Endpoint `/api/user/avatar/upload` aceita `multipart/form-data` com `file`.
- Limite de 4MB por arquivo (e `MAX_CONTENT_LENGTH` 5MB por requisição).
- MIME allowlist via `services.image_utils.is_allowed_mime()`; sanitiza/resize para `WEBP` (256x256) com Pillow e salva em `static/avatars/`.

## Integrações Opcionais

- Julia Analytics: `/api/analytics/summary` (proxy) — requer serviço em `services/julia_analytics`.
- Go Reports PDF: `/api/reports/rnc/<id>.pdf` — conteúdo `application/pdf` retornado pelo serviço Go.
- Kotlin Utils (QR): `/api/utils/qr.png?text=...&size=256`.
- Demais utilidades: `/api/utils/{hash,b64,uuid,token,slug,levenshtein,xxh3,sha256,url/{encode,decode}}` — retornam 404 amigável se cliente não configurado.

## Variáveis de Ambiente Importantes

- `IPPEL_SECRET_KEY` — secret key do Flask (se ausente, usa arquivo `ippel_secret.key`).
- `USE_MIN_ASSETS` — habilita uso de `.min.*` em `asset_url()` (default: on).
- `RATE_LIMIT_DEFAULTS` — limites padrão do Flask-Limiter, ex.: `"200 per minute; 5000 per hour"`.
- `REDIS_URL` — storage do rate limiter/cache (se aplicável).
- `IPPEL_BACKUP_DIR` — diretório para snapshots de backup do SQLite.
- `CSRF_ENFORCE` — ativa enforcement de CSRF (sem, apenas loga violações).
- `ADMIN_IP_ALLOWLIST` — CSV de IPs que podem acessar rotas protegidas por allowlist.
- URLs de serviços opcionais (quando aplicável): `JULIA_ANALYTICS_URL`, `GO_REPORTS_URL`, `KOTLIN_UTILS_URL`, etc.

## Templates & Frontend

- Principais: `dashboard_improved.html`, `indicadores_dashboard.html`.
- RNC: `new_rnc.html`, `edit_rnc_form.html`, `view_rnc_print.html`, `view_rnc_pdf_js.html`, `view_rnc_full.html`.
- `view_rnc_public.html`: não há rota ativa no backend moderno. Se a intenção é link público, implementar endpoint com token de acesso temporário e dados mascarados; caso contrário, tratar como legado (ver `docs/LEGACY.md`).
- Helper `asset_url()` escolhe `.min.*` quando existir e adiciona `?v=<mtime>` para cache-busting.

## Tratamento de Erros e Códigos de Status

- Autorização: 401 (não autenticado), 403 (sem permissão), 429 (lockout/limite).
- Validação: 400 (campos ausentes/assinaturas obrigatórias).
- Não encontrado: 404 (RNC inexistente ou clientes externos não configurados).
- Interno: 500 (com logs em `security.log` quando aplicável).

## Testes de Fumaça (sugestão)

- Login: POST `/api/login` → 200 e `success=True`.
- Sessão: GET `/api/debug/session` → `has_session=True`.
- Criar RNC: POST `/api/rnc/create` → `success=True` e retorna `rnc_id`.
- Listar RNCs: GET `/api/rnc/list` → `rncs` não vazio (após criação).
- Finalizar/Responder: POST `/api/rnc/<id>/finalize` / `/reply` → `success=True`.
- Avatar: POST `/api/user/avatar` com JSON válido → `success=True`.

## Pontos de Atenção

- Componentes legados (`main_system.py`, `server.py`) usam `rnc_reports` (schema diverso). Não usar em produção.
- CSP ainda permite `'unsafe-inline'`; migrar conforme guia (`docs/csp_migration.md`).
- Caminhos de backup em Windows: preferir `IPPEL_BACKUP_DIR` via env para ambientes diferentes.

## Próximos Passos

1. Consolidar `server_form.py` como único entry point no README e arquivar legados.
2. Executar migração CSP (remover inline, adotar nonces, apertar diretivas, SRI em CDNs ou self-host).
3. Garantir ativação de Rate Limiter/Talisman em produção (com `REDIS_URL` e políticas mais restritas).
4. Adicionar suíte mínima de testes (smoke) para auth, RNC e permissões.

---

Para um relatório completo e extenso (inclui inventário e listagens integrais de código), consulte `arquitetura_completa.md` (gerado por `scripts/generate_architecture_report.py`).

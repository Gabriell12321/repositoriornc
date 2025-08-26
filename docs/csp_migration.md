# Migração CSP: de 'unsafe-inline' para nonces e políticas estritas

Este guia ajuda a fortalecer a Content Security Policy (CSP) sem quebrar a UI durante a transição.

## Estado Atual

- Talisman ativo quando disponível; fallback manual caso contrário.
- Diretivas permitem `'unsafe-inline'` (scripts e estilos) por compatibilidade com handlers inline e `<script>` embutidos.
- Report-Only configurado para mapear violações em `/csp-report`.

## Objetivo

- Remover `'unsafe-inline'` de `script-src` e `style-src`.
- Usar nonces para scripts injetados pelo servidor e extrair handlers inline para arquivos JS estáticos.

## Passos

1. Inventário de Inline Scripts/Handlers
   - Buscar `onclick=`, `onchange=`, etc. nos templates.
   - Identificar `<script>` inline nos templates.

2. Extrair para JS estático
   - Mover inline JS para `static/js/...` e importar via `<script src="{{ asset_url('js/arquivo.min.js') }}" defer></script>`.
   - Substituir handlers inline por `addEventListener` no JS.

3. Ativar Nonces
   - No `server_form.py`, ao criar Talisman, habilitar `content_security_policy_nonce_in=['script-src']`.
   - Incluir `{{ csp_nonce() }}` nos `<script>` injetados pelo servidor quando necessário.

4. Ajustar Diretivas CSP
   - Remover `'unsafe-inline'` de `script-src`. Manter CDNs confiáveis (jsdelivr/cdnjs) se indispensáveis; preferir self-hosting.
   - Em `style-src`, preferir classes CSS; se necessário, usar `'unsafe-hashes'` com hashes de estilos inline específicos.

5. Monitorar com Report-Only
   - Primeiro, aplicar as mudanças em modo Report-Only para identificar faltas.
   - Depois, promover a política estrita para ativa.

## Exemplo (trecho de política alvo)

```
script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com 'nonce-...';
style-src 'self';
img-src 'self' data: blob: https://api.dicebear.com;
object-src 'none'; frame-ancestors 'self'; base-uri 'self';
```

## Dicas

- Evite `eval()` e afins (bloqueados por CSP estrita).
- Remova dependências de inline event handlers dos templates.
- Para bibliotecas externas, fixe integridade (SRI) quando via CDN.

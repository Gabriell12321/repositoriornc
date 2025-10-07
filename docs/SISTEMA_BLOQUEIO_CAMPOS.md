# Sistema de Bloqueio de Campos RNC

## 📋 Visão Geral

Este sistema permite que o administrador configure quais campos do formulário RNC cada grupo de usuários pode ou não editar durante a criação e edição de RNCs.

## 🎯 Objetivo

Controlar de forma granular o acesso de edição aos 12 campos principais do formulário RNC:

- **title** - Título
- **description** - Descrição
- **equipment** - Equipamento
- **client** - Cliente
- **priority** - Prioridade
- **status** - Status
- **responsavel** - Responsável
- **inspetor** - Inspetor
- **setor** - Setor
- **area_responsavel** - Área Responsável
- **price** - Preço
- **assigned_user_id** - Usuário Atribuído

## 🔧 Componentes do Sistema

### 1. Banco de Dados

**Tabela: `field_locks`**

```sql
CREATE TABLE field_locks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    is_locked INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    UNIQUE(group_id, field_name)
);
```

**Estrutura:**
- `group_id`: ID do grupo ao qual o bloqueio se aplica
- `field_name`: Nome técnico do campo (ex: 'title', 'description')
- `is_locked`: 1 = bloqueado (não editável), 0 = liberado (editável)
- Índices em `group_id` e `field_name` para performance
- Trigger para atualizar `updated_at` automaticamente

### 2. Backend - API REST

**Arquivo: `routes/field_locks.py`**

**Endpoints disponíveis:**

#### Página de Administração
```
GET /admin/field-locks
```
Renderiza a interface administrativa para gerenciar bloqueios.

#### Listar Grupos
```
GET /admin/field-locks/api/groups
```
Retorna todos os grupos cadastrados no sistema.

**Resposta:**
```json
{
  "success": true,
  "groups": [
    {"id": 1, "name": "Engenharia", "description": "Equipe de Engenharia"},
    {"id": 2, "name": "Inspeção", "description": "Equipe de Inspeção"}
  ]
}
```

#### Listar Campos Bloqueáveis
```
GET /admin/field-locks/api/fields
```
Retorna lista de campos que podem ser bloqueados.

**Resposta:**
```json
{
  "success": true,
  "fields": [
    {"name": "title", "label": "Título"},
    {"name": "description", "label": "Descrição"},
    ...
  ]
}
```

#### Obter Bloqueios de um Grupo
```
GET /admin/field-locks/api/locks/<group_id>
```
Retorna configuração de bloqueios de um grupo específico.

**Resposta:**
```json
{
  "success": true,
  "group_id": 1,
  "locks": {
    "title": {"is_locked": false},
    "description": {"is_locked": true},
    "equipment": {"is_locked": false},
    ...
  }
}
```

#### Atualizar Bloqueios (Admin Only)
```
POST /admin/field-locks/api/locks/<group_id>
Content-Type: application/json

{
  "locks": {
    "title": true,
    "description": false,
    "equipment": true,
    ...
  }
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Bloqueios atualizados com sucesso",
  "updated_count": 12
}
```

#### Resetar Bloqueios (Admin Only)
```
POST /admin/field-locks/api/locks/<group_id>/reset
```
Remove todos os bloqueios de um grupo específico.

#### Verificar Campo Específico
```
GET /admin/field-locks/api/check/<group_id>/<field_name>
```

**Resposta:**
```json
{
  "success": true,
  "group_id": 1,
  "field_name": "title",
  "is_locked": true
}
```

#### Campos Bloqueados do Usuário Atual
```
GET /admin/field-locks/api/user/locked-fields
```
Retorna lista de campos bloqueados para o usuário logado (baseado no grupo dele).

**Resposta:**
```json
{
  "success": true,
  "user_id": 5,
  "group_id": 2,
  "locked_fields": ["description", "price", "status"]
}
```

### 3. Frontend - Interface Admin

**Arquivo: `templates/admin_field_locks.html`**

**Características:**
- Interface moderna com gradiente roxo/azul
- Sidebar com lista de grupos
- Painel principal com grid de campos
- Toggles visuais para cada campo (vermelho = bloqueado, verde = liberado)
- Estatísticas em tempo real (campos bloqueados/liberados/total)
- Botões de ação:
  - 🔒 Bloquear Todos
  - 🔓 Liberar Todos
  - 💾 Salvar Alterações
- Notificações toast para feedback
- Responsivo e com animações

**Como acessar:**
```
http://seu-servidor/admin/field-locks
```

### 4. Frontend - JavaScript de Bloqueio

**Arquivo: `static/js/field_locks.js`**

**Funcionalidades:**
- Auto-inicializa ao carregar a página
- Busca campos bloqueados via API
- Desabilita inputs dinamicamente
- Adiciona indicadores visuais (🔒 ícone, cor de fundo, texto de ajuda)
- Intercepta submissões de formulário para validação client-side
- Mostra notificação temporária listando campos bloqueados
- Previne bypass via DevTools

**Integração em formulários RNC:**

```html
<!-- No final do body, antes de fechar </body> -->
<script src="/static/js/field_locks.js"></script>
```

O script se inicializa automaticamente. Para uso manual:

```javascript
// Inicializar manualmente
await window.FieldLocks.init();

// Buscar campos bloqueados
const lockedFields = await window.FieldLocks.fetch();

// Aplicar bloqueios manualmente
window.FieldLocks.apply(['title', 'price']);

// Validar dados antes de enviar
const isValid = window.FieldLocks.validate(formData);

// Bloquear campo específico
window.FieldLocks.lock('description');
```

### 5. Validação Backend

**Arquivo: `routes/rnc.py`**

Validação adicionada em dois endpoints:

#### `POST /api/rnc` (Criar RNC)
```python
from routes.field_locks import get_user_locked_fields

# No início da função
locked_fields = get_user_locked_fields(session['user_id'])
if locked_fields:
    attempted_fields = []
    for field in locked_fields:
        if field in data and data[field] is not None and data[field] != '':
            attempted_fields.append(field)
    
    if attempted_fields:
        return jsonify({
            'success': False,
            'message': f'Os seguintes campos estão bloqueados: {", ".join(attempted_fields)}'
        }), 403
```

#### `PUT /api/rnc/<rnc_id>/update` (Editar RNC)
Mesma lógica de validação aplicada.

**Comportamento:**
- Se usuário tentar enviar valores para campos bloqueados → HTTP 403
- Mensagem clara indica quais campos violaram a regra
- Validação ocorre ANTES de qualquer processamento

### 6. Migration Script

**Arquivo: `migrate_field_locks.py`**

Script interativo para aplicar/reverter migração.

**Uso:**
```bash
python migrate_field_locks.py
```

**Menu:**
```
=== Sistema de Migração field_locks ===

1. Aplicar migração (criar tabela)
2. Reverter migração (remover tabela)
3. Sair

Escolha: 1

✅ Migração aplicada com sucesso!

Deseja configurar bloqueios iniciais? (s/n): s

Grupos disponíveis:
- ID: 1, Nome: Engenharia
- ID: 2, Nome: Inspeção
- ID: 3, Nome: Qualidade

Digite: group_id:campo1,campo2,campo3
Exemplo: 2:title,price,status
(Enter vazio para pular)

Bloqueios: 2:price,status,description

✅ 3 bloqueios configurados para grupo 2
```

**Arquivo SQL: `migrations/create_field_locks.sql`**
- Criação da tabela
- Índices de performance
- Trigger de atualização
- Dados de exemplo (comentados)

## 📖 Guia de Uso

### Para Administradores

#### 1. Aplicar Migração (Primeira Vez)

```bash
cd /caminho/do/projeto
python migrate_field_locks.py
# Escolher opção 1 (aplicar)
# Configurar bloqueios iniciais se desejar
```

#### 2. Registrar Blueprint (já feito no server_form.py)

Verificar se estas linhas existem:

```python
# Imports
from routes.field_locks import field_locks_bp

# Registros
app.register_blueprint(field_locks_bp)
```

#### 3. Adicionar JavaScript aos Formulários RNC

Editar templates que contêm formulários de criação/edição de RNC:
- `templates/create_rnc.html`
- `templates/edit_rnc_form.html`
- Qualquer outro template com formulário RNC

Adicionar antes de `</body>`:
```html
<script src="/static/js/field_locks.js"></script>
```

#### 4. Acessar Painel Admin

1. Fazer login como admin
2. Acessar: `http://localhost:5000/admin/field-locks`
3. Interface carregará automaticamente

#### 5. Configurar Bloqueios

**Passo a passo:**

1. **Selecionar Grupo**
   - Clicar em um grupo na barra lateral esquerda
   - Grupo ficará destacado em roxo

2. **Configurar Campos**
   - Toggle verde = campo liberado (editável)
   - Toggle vermelho = campo bloqueado (não editável)
   - Clicar no toggle para alternar estado

3. **Uso dos Botões**
   - **🔒 Bloquear Todos**: Bloqueia todos os 12 campos
   - **🔓 Liberar Todos**: Libera todos os 12 campos
   - **💾 Salvar Alterações**: Persiste configuração no banco

4. **Visualizar Estatísticas**
   - Cards superiores mostram:
     - Quantidade de campos bloqueados
     - Quantidade de campos liberados
     - Total de campos

5. **Confirmar Salvamento**
   - Notificação verde aparece no canto superior direito
   - Mostra quantos bloqueios foram atualizados

### Para Desenvolvedores

#### Adicionar Novo Campo Bloqueável

1. **Atualizar `routes/field_locks.py`:**
```python
AVAILABLE_FIELDS = [
    # ... campos existentes ...
    {'name': 'novo_campo', 'label': 'Novo Campo'}
]
```

2. **Atualizar `static/js/field_locks.js`:**
```javascript
const FIELD_TO_INPUT_MAP = {
    // ... mapeamentos existentes ...
    'novo_campo': ['novo_campo', 'input[name="novo_campo"]']
};

const FIELD_LABELS = {
    // ... labels existentes ...
    'novo_campo': 'Novo Campo'
};
```

3. **Nenhuma mudança no banco necessária** - sistema é dinâmico

#### Verificar Bloqueio Programaticamente

```python
from routes.field_locks import get_user_locked_fields

# Em qualquer endpoint
user_id = session.get('user_id')
locked_fields = get_user_locked_fields(user_id)

if 'title' in locked_fields:
    # Campo está bloqueado
    return jsonify({'error': 'Campo bloqueado'}), 403
```

#### Helper Function

```python
def get_user_locked_fields(user_id):
    """
    Retorna lista de campos bloqueados para um usuário.
    
    Args:
        user_id (int): ID do usuário
        
    Returns:
        list: Lista de nomes de campos bloqueados ['title', 'price', ...]
    """
    # Implementação interna busca grupo do usuário
    # e retorna campos com is_locked=1
```

## 🧪 Testando o Sistema

### Teste 1: Configuração Admin

```bash
# 1. Aplicar migração
python migrate_field_locks.py

# 2. Iniciar servidor
python server_form.py

# 3. Acessar como admin
# http://localhost:5000/admin/field-locks

# 4. Selecionar grupo "Inspeção"
# 5. Bloquear campos: price, status, description
# 6. Clicar em "Salvar Alterações"
# 7. Verificar notificação de sucesso
```

### Teste 2: Validação Frontend

```bash
# 1. Fazer login como usuário do grupo "Inspeção"
# 2. Acessar formulário de criar RNC
# 3. Verificar:
#    - Campos price, status, description devem estar:
#      * Desabilitados (cinza, cursor not-allowed)
#      * Com ícone 🔒
#      * Com texto "Este campo está bloqueado para seu grupo"
#    - Notificação aparece listando campos bloqueados
# 4. Outros campos devem estar normais (editáveis)
```

### Teste 3: Validação Backend

```bash
# Terminal 1: Iniciar servidor
python server_form.py

# Terminal 2: Testar API
curl -X POST http://localhost:5000/api/rnc \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{
    "title": "Teste",
    "description": "Tentando burlar...",
    "price": 1000
  }'

# Resposta esperada (se description e price bloqueados):
{
  "success": false,
  "message": "Os seguintes campos estão bloqueados: description, price"
}
```

### Teste 4: Bypass via DevTools

```javascript
// 1. Abrir DevTools (F12)
// 2. Console, tentar habilitar campo bloqueado:
document.getElementById('price').disabled = false;

// 3. Preencher campo e enviar formulário
// 4. Backend deve rejeitar com HTTP 403
// 5. Alert deve aparecer listando campos violados
```

## 🔐 Segurança

### Camadas de Proteção

1. **Frontend (JavaScript)**
   - Desabilita inputs visualmente
   - Adiciona `disabled` e `readOnly`
   - Intercepta submissões
   - **Nível:** Facilita UX, não é segurança real

2. **Backend (Python)**
   - Valida TODOS os requests em create/update
   - Verifica campos bloqueados antes de processar
   - Retorna HTTP 403 se violação detectada
   - **Nível:** Segurança real, não pode ser burlada

3. **Banco de Dados**
   - Constraints UNIQUE evitam duplicatas
   - Foreign keys garantem integridade
   - Índices melhoram performance
   - **Nível:** Integridade dos dados

### Permissões

#### Endpoints Admin (requerem `admin_access`)
- GET `/admin/field-locks`
- POST `/admin/field-locks/api/locks/<group_id>`
- POST `/admin/field-locks/api/locks/<group_id>/reset`

#### Endpoints Públicos (qualquer usuário autenticado)
- GET `/admin/field-locks/api/groups`
- GET `/admin/field-locks/api/fields`
- GET `/admin/field-locks/api/locks/<group_id>`
- GET `/admin/field-locks/api/check/<group_id>/<field>`
- GET `/admin/field-locks/api/user/locked-fields`

### Validação de Admin

```python
def check_admin():
    """Verifica se usuário tem permissão de admin"""
    if 'user_id' not in session:
        return False
    
    from services.permissions import has_permission
    return has_permission(session['user_id'], 'admin_access')
```

## 📊 Performance

### Índices Criados

```sql
-- Busca por grupo (mais comum)
CREATE INDEX idx_field_locks_group ON field_locks(group_id);

-- Busca por campo
CREATE INDEX idx_field_locks_field ON field_locks(field_name);

-- Busca composta (mais rápida)
CREATE UNIQUE INDEX idx_field_locks_unique 
    ON field_locks(group_id, field_name);
```

### Cache Recomendado

Para otimizar, adicionar cache no `get_user_locked_fields()`:

```python
from functools import lru_cache
from services.cache import query_cache

@lru_cache(maxsize=128)
def get_user_locked_fields_cached(user_id):
    return get_user_locked_fields(user_id)
```

Invalidar cache ao atualizar bloqueios:

```python
# No endpoint POST /api/locks/<group_id>
get_user_locked_fields_cached.cache_clear()
```

## 🐛 Troubleshooting

### Problema: Campos não estão sendo bloqueados no frontend

**Possíveis causas:**
1. JavaScript não incluído no template
2. Seletores CSS incorretos no mapeamento
3. Formulário carrega antes do script

**Soluções:**
```html
<!-- Verificar se está incluído -->
<script src="/static/js/field_locks.js"></script>

<!-- Ou carregar manualmente -->
<script>
document.addEventListener('DOMContentLoaded', async () => {
    await window.FieldLocks.init();
});
</script>
```

### Problema: Backend não está validando

**Verificar:**
```python
# Em routes/rnc.py, deve ter:
from routes.field_locks import get_user_locked_fields

# No create_rnc() e update_rnc_api()
locked_fields = get_user_locked_fields(session['user_id'])
if locked_fields:
    # validação...
```

### Problema: Erro "Import could not be resolved"

**Causa:** Ambiente Python não configurado no editor

**Solução:** Erro é apenas do linter, código funciona normalmente

### Problema: Painel admin não carrega

**Verificar:**
1. Blueprint registrado?
```python
app.register_blueprint(field_locks_bp)
```

2. Template existe?
```bash
ls templates/admin_field_locks.html
```

3. Usuário tem permissão admin?
```sql
SELECT * FROM group_permissions WHERE permission_name = 'admin_access';
```

### Problema: Migração falha

**Erro comum:** "table field_locks already exists"

**Solução:**
```bash
# Reverter primeiro
python migrate_field_locks.py
# Escolher opção 2 (reverter)

# Depois aplicar novamente
python migrate_field_locks.py
# Escolher opção 1 (aplicar)
```

## 📚 Referências Técnicas

### Arquivos do Sistema

```
projeto/
├── migrations/
│   └── create_field_locks.sql          # Schema SQL
├── routes/
│   ├── field_locks.py                  # Blueprint API
│   └── rnc.py                          # Validação integrada
├── static/
│   └── js/
│       └── field_locks.js              # Frontend logic
├── templates/
│   └── admin_field_locks.html          # Interface admin
├── migrate_field_locks.py              # Script de migração
└── server_form.py                      # Registro do blueprint
```

### Dependências

**Python:**
- Flask 3.1.2
- sqlite3 (built-in)

**Frontend:**
- Vanilla JavaScript (ES6+)
- Fetch API
- CSS3 com flexbox/grid

**Nenhuma lib adicional necessária!**

## 🎉 Conclusão

Sistema completo de bloqueio de campos implementado com sucesso!

**Features principais:**
✅ 12 campos bloqueáveis
✅ Interface admin moderna e intuitiva
✅ Validação frontend + backend
✅ API RESTful completa
✅ Sistema de migração interativo
✅ Segurança em múltiplas camadas
✅ Performance otimizada com índices
✅ Documentação completa

**Pronto para produção!** 🚀

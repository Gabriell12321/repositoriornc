# Estratégia de Testes - Sistema IPPEL RNC

## 📋 Visão Geral

Este documento define a estratégia de testes para o Sistema de Gestão de RNC da IPPEL, estabelecendo metas de cobertura, frameworks, metodologias e exemplos práticos.

**Data:** Outubro 2025  
**Versão:** 1.0  
**Status:** Proposta Inicial

---

## 🎯 Objetivos de Qualidade

### Metas de Cobertura
- **Cobertura de Código:** ≥ 60% (crítico: ≥ 80%)
- **Cobertura de Branches:** ≥ 50%
- **Testes de Regressão:** 100% dos fluxos principais
- **Tempo de Execução:** < 5 minutos (suite completa)

### Níveis de Prioridade
1. **P0 - Crítico:** Autenticação, Autorização, CRUD RNC, Assinaturas
2. **P1 - Alto:** Admin, Relatórios, Analytics, Field Locks
3. **P2 - Médio:** Gráficos, Notificações, Exportações
4. **P3 - Baixo:** UI/UX, Documentação, Logs

---

## 🛠️ Stack de Testes

### Framework Principal
```python
# pytest 7.4+ (principal)
pytest==7.4.3
pytest-cov==4.1.0
pytest-flask==1.3.0
pytest-mock==3.12.0
pytest-xdist==3.5.0  # testes paralelos
```

### Ferramentas Complementares
- **Coverage.py:** Análise de cobertura
- **Faker:** Geração de dados de teste
- **Factory Boy:** Fixtures complexas
- **Selenium/Playwright:** Testes E2E (futuro)
- **Locust/k6:** Testes de carga

---

## 📐 Pirâmide de Testes

```
        /\
       /E2E\         10% - Testes End-to-End
      /------\
     /  API   \      30% - Testes de Integração
    /----------\
   /   UNIDADE  \    60% - Testes Unitários
  /--------------\
```

### Distribuição Proposta
- **60% Unitários:** Funções isoladas, validações, helpers
- **30% Integração:** APIs, database, microservices
- **10% E2E:** Fluxos completos críticos

---

## 🧪 Estratégia por Módulo

### 1. Autenticação (P0 - Crítico)

**Cobertura Alvo:** 85%

#### Testes Unitários
```python
# tests/unit/test_auth.py
import pytest
from server_form import app, db, User
from werkzeug.security import check_password_hash

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_user_registration_success(client):
    """Teste de registro bem-sucedido"""
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'SecurePass123!',
        'email': 'test@ippel.com'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'test@ippel.com'

def test_user_registration_duplicate(client):
    """Teste de registro duplicado"""
    # Criar usuário
    client.post('/register', data={
        'username': 'testuser',
        'password': 'Pass123!',
        'email': 'test@ippel.com'
    })
    
    # Tentar duplicar
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'Pass456!',
        'email': 'other@ippel.com'
    })
    
    assert b'usuário já existe' in response.data.lower()

def test_login_success(client):
    """Teste de login bem-sucedido"""
    # Registrar usuário
    client.post('/register', data={
        'username': 'testuser',
        'password': 'Pass123!',
        'email': 'test@ippel.com'
    })
    
    # Login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'Pass123!'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'dashboard' in response.data.lower()

def test_login_invalid_credentials(client):
    """Teste de login com credenciais inválidas"""
    response = client.post('/login', data={
        'username': 'nonexistent',
        'password': 'WrongPass123!'
    })
    
    assert b'credenciais inválidas' in response.data.lower()

def test_password_hashing(client):
    """Teste de hash de senha"""
    client.post('/register', data={
        'username': 'testuser',
        'password': 'PlainPassword123!',
        'email': 'test@ippel.com'
    })
    
    user = User.query.filter_by(username='testuser').first()
    assert user.password != 'PlainPassword123!'
    assert check_password_hash(user.password, 'PlainPassword123!')
```

#### Testes de Integração
```python
# tests/integration/test_auth_flow.py
import pytest
from server_form import app, db

def test_full_auth_flow(client):
    """Teste de fluxo completo: registro → login → acesso protegido → logout"""
    # 1. Registro
    response = client.post('/register', data={
        'username': 'flowuser',
        'password': 'Flow123!',
        'email': 'flow@ippel.com'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # 2. Login
    response = client.post('/login', data={
        'username': 'flowuser',
        'password': 'Flow123!'
    }, follow_redirects=True)
    assert b'dashboard' in response.data.lower()
    
    # 3. Acesso a rota protegida
    response = client.get('/dashboard')
    assert response.status_code == 200
    
    # 4. Logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    
    # 5. Tentar acessar rota protegida após logout
    response = client.get('/dashboard', follow_redirects=True)
    assert b'login' in response.data.lower()

def test_2fa_setup_and_validation(client):
    """Teste de configuração e validação 2FA"""
    # Criar e logar usuário
    client.post('/register', data={
        'username': '2fauser',
        'password': 'Secure2FA123!',
        'email': '2fa@ippel.com'
    })
    client.post('/login', data={
        'username': '2fauser',
        'password': 'Secure2FA123!'
    })
    
    # Setup 2FA
    response = client.get('/auth/2fa/setup')
    assert response.status_code == 200
    assert b'qrcode' in response.data.lower() or b'secret' in response.data.lower()
```

---

### 2. CRUD RNC (P0 - Crítico)

**Cobertura Alvo:** 80%

#### Testes Unitários
```python
# tests/unit/test_rnc_crud.py
import pytest
from server_form import RNC, db
from datetime import datetime

def test_create_rnc(client, auth_user):
    """Teste de criação de RNC"""
    response = client.post('/api/rnc/create', json={
        'numero': 'RNC-2025-001',
        'titulo': 'Teste de RNC',
        'descricao': 'Descrição detalhada',
        'prioridade': 'ALTA',
        'setor_origem': 'Engenharia',
        'responsavel': 'João Silva'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['numero'] == 'RNC-2025-001'
    assert data['titulo'] == 'Teste de RNC'

def test_list_rncs_pagination(client, auth_user):
    """Teste de listagem com paginação"""
    # Criar 15 RNCs
    for i in range(15):
        RNC(
            numero=f'RNC-2025-{i:03d}',
            titulo=f'RNC Teste {i}',
            descricao='Descrição',
            prioridade='MÉDIA',
            status='ABERTA'
        ).save()
    
    # Página 1
    response = client.get('/api/rnc/list?page=1&per_page=10')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 10
    assert data['total'] == 15
    
    # Página 2
    response = client.get('/api/rnc/list?page=2&per_page=10')
    data = response.get_json()
    assert len(data['items']) == 5

def test_update_rnc(client, auth_user):
    """Teste de atualização de RNC"""
    # Criar RNC
    rnc = RNC(
        numero='RNC-2025-UPD',
        titulo='Original',
        descricao='Descrição original',
        status='ABERTA'
    )
    db.session.add(rnc)
    db.session.commit()
    
    # Atualizar
    response = client.put(f'/api/rnc/{rnc.id}', json={
        'titulo': 'Atualizado',
        'status': 'EM_ANÁLISE'
    })
    
    assert response.status_code == 200
    rnc_updated = RNC.query.get(rnc.id)
    assert rnc_updated.titulo == 'Atualizado'
    assert rnc_updated.status == 'EM_ANÁLISE'

def test_delete_rnc_soft(client, auth_admin):
    """Teste de exclusão lógica (soft delete)"""
    rnc = RNC(numero='RNC-DEL', titulo='Para deletar', status='ABERTA')
    db.session.add(rnc)
    db.session.commit()
    
    response = client.delete(f'/api/rnc/{rnc.id}')
    assert response.status_code == 200
    
    # Verificar soft delete
    rnc_deleted = RNC.query.get(rnc.id)
    assert rnc_deleted.deleted_at is not None
```

#### Testes de Validação
```python
# tests/unit/test_rnc_validation.py
def test_rnc_required_fields(client, auth_user):
    """Teste de campos obrigatórios"""
    response = client.post('/api/rnc/create', json={
        'titulo': 'Sem número'
        # Faltando 'numero'
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'numero' in data['errors']

def test_rnc_invalid_priority(client, auth_user):
    """Teste de prioridade inválida"""
    response = client.post('/api/rnc/create', json={
        'numero': 'RNC-001',
        'titulo': 'Teste',
        'prioridade': 'URGENTISSIMA'  # Inválido
    })
    
    assert response.status_code == 400

def test_rnc_duplicate_number(client, auth_user):
    """Teste de número duplicado"""
    # Criar primeira RNC
    client.post('/api/rnc/create', json={
        'numero': 'RNC-DUP-001',
        'titulo': 'Primeira'
    })
    
    # Tentar duplicar
    response = client.post('/api/rnc/create', json={
        'numero': 'RNC-DUP-001',
        'titulo': 'Segunda'
    })
    
    assert response.status_code == 409
    assert b'duplicado' in response.data.lower()
```

---

### 3. Permissões e Field Locks (P1 - Alto)

**Cobertura Alvo:** 75%

```python
# tests/unit/test_field_locks.py
def test_field_lock_by_role(client, auth_user):
    """Teste de bloqueio de campo por papel"""
    # Usuário normal não pode editar 'assinatura_responsavel'
    response = client.put('/api/rnc/1', json={
        'assinatura_responsavel': 'Tentativa não autorizada'
    })
    
    assert response.status_code == 403
    assert b'bloqueado' in response.data.lower()

def test_field_lock_by_status(client, auth_user):
    """Teste de bloqueio por status"""
    # RNC finalizada não pode ser editada
    rnc = RNC(numero='RNC-FIN', titulo='Finalizada', status='FINALIZADA')
    db.session.add(rnc)
    db.session.commit()
    
    response = client.put(f'/api/rnc/{rnc.id}', json={
        'titulo': 'Tentativa de edição'
    })
    
    assert response.status_code == 403

def test_admin_bypass_locks(client, auth_admin):
    """Teste de admin bypassando bloqueios"""
    rnc = RNC(numero='RNC-ADM', titulo='Admin test', status='FINALIZADA')
    db.session.add(rnc)
    db.session.commit()
    
    # Admin pode editar RNC finalizada
    response = client.put(f'/api/rnc/{rnc.id}', json={
        'titulo': 'Admin alterou'
    })
    
    assert response.status_code == 200
```

---

### 4. APIs e Analytics (P1 - Alto)

**Cobertura Alvo:** 70%

```python
# tests/integration/test_analytics_api.py
def test_charts_data_endpoint(client, auth_user):
    """Teste de endpoint de dados para gráficos"""
    response = client.get('/api/charts/data')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'status_distribution' in data
    assert 'priority_breakdown' in data
    assert 'trend_data' in data

def test_indicadores_detalhados(client, auth_user):
    """Teste de indicadores detalhados"""
    response = client.get('/api/indicadores-detalhados')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'total_rncs' in data
    assert 'taxa_resolucao' in data
    assert 'tempo_medio_resolucao' in data

def test_microservice_fallback(client, monkeypatch):
    """Teste de fallback quando microserviço está offline"""
    # Simular microserviço offline
    def mock_analytics_call(*args, **kwargs):
        return None
    
    monkeypatch.setattr('services.analytics_client.get_advanced_stats', mock_analytics_call)
    
    response = client.get('/api/analytics/advanced')
    
    # Deve retornar dados básicos como fallback
    assert response.status_code == 200
    data = response.get_json()
    assert 'fallback' in data or 'basic_stats' in data
```

---

### 5. Segurança (P0 - Crítico)

**Cobertura Alvo:** 85%

```python
# tests/security/test_security.py
def test_csrf_protection(client):
    """Teste de proteção CSRF"""
    response = client.post('/api/rnc/create', json={
        'numero': 'RNC-CSRF',
        'titulo': 'Sem CSRF token'
    }, headers={'X-CSRFToken': ''})
    
    assert response.status_code == 403

def test_rate_limiting(client, auth_user):
    """Teste de rate limiting"""
    # Fazer 200 requisições rapidamente
    for i in range(200):
        response = client.get('/api/rnc/list')
        if i < 180:
            assert response.status_code == 200
        else:
            # Após 180 requests/min, deve bloquear
            assert response.status_code == 429

def test_sql_injection_prevention(client, auth_user):
    """Teste de prevenção SQL injection"""
    malicious_input = "'; DROP TABLE rncs; --"
    
    response = client.post('/api/rnc/create', json={
        'numero': malicious_input,
        'titulo': 'Test'
    })
    
    # Deve rejeitar ou sanitizar
    assert response.status_code in [400, 422]
    
    # Tabela ainda deve existir
    from server_form import RNC
    assert RNC.query.count() >= 0

def test_xss_prevention(client, auth_user):
    """Teste de prevenção XSS"""
    xss_payload = '<script>alert("XSS")</script>'
    
    response = client.post('/api/rnc/create', json={
        'numero': 'RNC-XSS',
        'titulo': xss_payload
    })
    
    rnc = RNC.query.filter_by(numero='RNC-XSS').first()
    # HTML deve estar escapado
    assert '&lt;script&gt;' in rnc.titulo or xss_payload not in rnc.titulo
```

---

## 🔧 Configuração do Ambiente de Testes

### Estrutura de Diretórios
```
tests/
├── __init__.py
├── conftest.py              # Fixtures globais
├── unit/                    # Testes unitários
│   ├── test_auth.py
│   ├── test_rnc_crud.py
│   ├── test_validators.py
│   └── test_utils.py
├── integration/             # Testes de integração
│   ├── test_api_flow.py
│   ├── test_database.py
│   └── test_microservices.py
├── security/                # Testes de segurança
│   ├── test_auth_security.py
│   └── test_input_validation.py
└── e2e/                     # Testes end-to-end (futuro)
    └── test_user_journeys.py
```

### Fixtures Globais
```python
# tests/conftest.py
import pytest
from server_form import app, db, User

@pytest.fixture(scope='session')
def test_app():
    """Configuração da aplicação para testes"""
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(test_app):
    """Cliente de teste"""
    return test_app.test_client()

@pytest.fixture
def auth_user(client):
    """Usuário autenticado"""
    user = User(username='testuser', email='test@ippel.com')
    user.set_password('TestPass123!')
    db.session.add(user)
    db.session.commit()
    
    client.post('/login', data={
        'username': 'testuser',
        'password': 'TestPass123!'
    })
    
    return user

@pytest.fixture
def auth_admin(client):
    """Admin autenticado"""
    admin = User(username='admin', email='admin@ippel.com', is_admin=True)
    admin.set_password('AdminPass123!')
    db.session.add(admin)
    db.session.commit()
    
    client.post('/login', data={
        'username': 'admin',
        'password': 'AdminPass123!'
    })
    
    return admin
```

### Configuração pytest.ini
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    unit: Testes unitários rápidos
    integration: Testes de integração
    security: Testes de segurança
    slow: Testes lentos (>1s)
    smoke: Testes smoke para CI/CD

# Cobertura
addopts =
    --cov=server_form
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=60
    -v
    -ra
    --strict-markers

# Parallel execution
# addopts = -n auto  # Descomentar para testes paralelos
```

---

## 🚀 Executando os Testes

### Comandos Básicos
```bash
# Todos os testes
pytest

# Apenas testes unitários
pytest -m unit

# Apenas testes de integração
pytest -m integration

# Testes com cobertura detalhada
pytest --cov=server_form --cov-report=html

# Testes paralelos (4 workers)
pytest -n 4

# Testes smoke (CI/CD)
pytest -m smoke --maxfail=1
```

### Pipeline CI/CD
```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run smoke tests
      run: pytest -m smoke --maxfail=1
    
    - name: Run full test suite
      run: pytest --cov=server_form --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## 📊 Métricas e Monitoramento

### KPIs de Qualidade
| Métrica | Meta | Crítico |
|---------|------|---------|
| Cobertura de Código | ≥60% | ≥80% |
| Testes Passando | 100% | 100% |
| Tempo de Execução | <5min | <10min |
| Flaky Tests | <2% | 0% |
| Bugs em Produção | <5/mês | 0 críticos |

### Dashboard de Cobertura
- **HTML Report:** `htmlcov/index.html`
- **Coverage Badge:** Integrar com Codecov/Coveralls
- **Trending:** Monitorar evolução semanal

---

## 🎯 Smoke Tests (CI/CD)

```python
# tests/smoke/test_smoke.py
import pytest

@pytest.mark.smoke
def test_app_starts(client):
    """Aplicação inicia corretamente"""
    response = client.get('/')
    assert response.status_code in [200, 302]

@pytest.mark.smoke
def test_database_connection(test_app):
    """Conexão com banco funciona"""
    with test_app.app_context():
        from server_form import db
        result = db.session.execute('SELECT 1')
        assert result.scalar() == 1

@pytest.mark.smoke
def test_login_page_loads(client):
    """Página de login carrega"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'login' in response.data.lower()

@pytest.mark.smoke
def test_api_health(client):
    """Health check da API"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
```

---

## 📈 Roadmap de Testes

### Fase 1 - Fundação (1-2 meses)
- ✅ Setup pytest e fixtures
- ✅ Testes unitários críticos (auth, CRUD)
- ✅ CI/CD básico
- ✅ Cobertura ≥40%

### Fase 2 - Expansão (2-3 meses)
- [ ] Testes de integração completos
- [ ] Testes de segurança
- [ ] Cobertura ≥60%
- [ ] Testes de regressão automatizados

### Fase 3 - Maturidade (3-6 meses)
- [ ] Testes E2E com Playwright
- [ ] Testes de carga (Locust)
- [ ] Mutation testing
- [ ] Cobertura ≥75%

---

## ✅ Checklist de Implementação

### Setup Inicial
- [ ] Instalar pytest e dependências
- [ ] Criar estrutura de diretórios `tests/`
- [ ] Configurar `pytest.ini` e `conftest.py`
- [ ] Configurar `.coveragerc`

### Testes Críticos (P0)
- [ ] Autenticação (login, registro, 2FA)
- [ ] CRUD RNC (create, read, update, delete)
- [ ] Autorização (roles, permissions)
- [ ] Assinaturas digitais

### Testes Importantes (P1)
- [ ] Field locks
- [ ] APIs analytics
- [ ] Relatórios
- [ ] Admin functions

### CI/CD
- [ ] GitHub Actions workflow
- [ ] Smoke tests
- [ ] Coverage reporting
- [ ] Badge no README

### Documentação
- [ ] Guia de contribuição com testes
- [ ] Exemplos de testes por módulo
- [ ] Troubleshooting comum

---

## 🔗 Recursos e Referências

- **Pytest Docs:** https://docs.pytest.org/
- **Flask Testing:** https://flask.palletsprojects.com/en/latest/testing/
- **Coverage.py:** https://coverage.readthedocs.io/
- **Testing Best Practices:** https://testdriven.io/

---

**Próximos Passos:**
1. Instalar dependências de teste
2. Criar estrutura de diretórios
3. Implementar smoke tests
4. Configurar CI/CD
5. Atingir 40% de cobertura (milestone 1)

**Mantenedores:** Equipe de Desenvolvimento IPPEL  
**Última Atualização:** Outubro 2025

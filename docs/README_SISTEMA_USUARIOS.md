# 🚀 Sistema IPPEL - Sistema de Usuários

Sistema completo de Relatórios de Não Conformidade (RNC) com **usuários individuais** e **controle de acesso**.

## 👥 Sistema de Usuários

### Usuários Padrão Criados:
- **Admin**: `admin@ippel.com.br` / `admin123`
- **João Silva**: `joao@ippel.com.br` / `joao123` (Produção)
- **Maria Santos**: `maria@ippel.com.br` / `maria123` (Qualidade)
- **Pedro Costa**: `pedro@ippel.com.br` / `pedro123` (Manutenção)
- **Ana Oliveira**: `ana@ippel.com.br` / `ana123` (Engenharia)

## 🏗️ Arquitetura

### 1. **Servidor Admin** (Porta 5000)
- **URL**: `http://IP:5000`
- **Função**: Painel administrativo completo
- **Acesso**: Apenas administradores
- **Funcionalidades**:
  - Dashboard com estatísticas
  - Visualização de todos os RNCs
  - Gerenciamento de usuários
  - Relatórios gerenciais

### 2. **Servidor Formulário** (Porta 5001)
- **URL**: `http://IP:5001`
- **Função**: Formulário com login individual
- **Acesso**: Usuários autorizados
- **Funcionalidades**:
  - Login individual
  - Área do usuário com estatísticas
  - Criação de RNCs
  - Visualização dos próprios RNCs

## 🔐 Controle de Acesso

### Usuários Normais
- ✅ Acessam apenas seus próprios RNCs
- ✅ Criam novos RNCs
- ✅ Veem estatísticas pessoais
- ❌ Não veem RNCs de outros usuários

### Administradores
- ✅ Acessam todos os RNCs
- ✅ Gerenciam usuários
- ✅ Veem estatísticas gerais
- ✅ Relatórios completos

## 🚀 Como Iniciar

### 1. Iniciar Servidor Admin:
```bash
start_admin.bat
```

### 2. Iniciar Servidor Formulário:
```bash
start_form.bat
```

## 📱 Fluxo de Uso

### Para Usuários:
1. **Acessar**: `http://IP:5001`
2. **Fazer Login**: Com email e senha
3. **Ver Área Pessoal**: Nome, departamento e estatísticas
4. **Criar RNC**: Preencher formulário e salvar
5. **Acompanhar**: Ver RNCs criados e status

### Para Administradores:
1. **Acessar**: `http://IP:5000`
2. **Fazer Login**: `admin@ippel.com.br` / `admin123`
3. **Ver Dashboard**: Estatísticas gerais
4. **Gerenciar**: Todos os RNCs e usuários

## 🔄 Integração

### Banco de Dados Compartilhado
- Ambos os servidores usam o mesmo banco SQLite
- Dados sincronizados automaticamente
- Controle de acesso por usuário

### APIs de Comunicação
- Formulário → Admin: Criação de RNCs
- Admin → Formulário: Dados de usuário
- Sessões independentes por servidor

## 📊 Área do Usuário

### No Formulário (Porta 5001):
- **Nome do usuário**
- **Departamento**
- **Estatísticas pessoais**:
  - RNCs concluídos
  - RNCs pendentes
  - Total de RNCs
- **Botão de logout**

### Atualização Automática:
- Após criar novo RNC
- Ao carregar a página
- Em tempo real

## 🛠️ Funcionalidades

### Formulário RNC:
- ✅ Login individual
- ✅ Área do usuário
- ✅ Criação de RNCs
- ✅ Geração de PDF
- ✅ Validação de dados
- ✅ Auto-salvamento

### Painel Admin:
- ✅ Dashboard completo
- ✅ Lista de todos os RNCs
- ✅ Filtros e busca
- ✅ Estatísticas gerais
- ✅ Gerenciamento de usuários

## 🔧 Configuração

### Dependências:
```bash
pip install -r requirements.txt
```

### Banco de Dados:
- Criado automaticamente na primeira execução
- Usuários padrão já incluídos
- Estrutura otimizada para performance

## 📱 Acesso na Rede

### Descobrir IP:
```bash
ipconfig
```

### URLs de Acesso:
- **Formulário**: `http://192.168.1.100:5001`
- **Admin**: `http://192.168.1.100:5000`

## 🔐 Segurança

- **Sessões independentes** por servidor
- **Controle de acesso** por usuário
- **Senhas criptografadas**
- **Validação de autenticação**
- **Logout automático**

## 📞 Suporte

### Problemas Comuns:
1. **"Usuário não autenticado"**: Faça login novamente
2. **"Servidor não disponível"**: Verifique se ambos estão rodando
3. **"Erro de conexão"**: Verifique a rede

### Logs:
- Servidor Admin: Console do `main_system.py`
- Servidor Formulário: Console do `server_form.py`

## 🎯 Benefícios

- **Controle individual** de RNCs
- **Segurança** por usuário
- **Estatísticas pessoais**
- **Interface intuitiva**
- **Sincronização automática**
- **Acesso via rede local** 
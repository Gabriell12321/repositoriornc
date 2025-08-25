# 🚀 Sistema Completo IPPEL - Usuários e Permissões

Sistema completo de gerenciamento de RNCs com controle de usuários e permissões.

## 🎯 **Funcionalidades Principais**

### 👥 **Sistema de Usuários**
- **Usuário Admin padrão** criado automaticamente
- **Gerenciamento completo** de usuários
- **Controle de permissões** granular
- **Soft delete** de usuários

### 🔐 **Sistema de Permissões**
- **Criar RNCs**: Permite criar novos relatórios
- **Ver todos os RNCs**: Acesso a todos os RNCs do sistema
- **Gerenciar usuários**: Criar, editar e deletar usuários
- **Editar RNCs**: Modificar RNCs existentes
- **Deletar RNCs**: Remover RNCs do sistema

### 📊 **Dashboard Inteligente**
- **Visualização personalizada** por usuário
- **Estatísticas em tempo real**
- **Filtros por status**
- **Interface responsiva**

## 🚀 **Como Iniciar**

### **1. Primeira Execução**
```bash
python server_form.py
```

### **2. Login Inicial**
- **Email**: `admin@ippel.com.br`
- **Senha**: `admin123`
- **Permissões**: Todas

### **3. Acessar Sistema**
```
http://SEU_IP:5001
```

## 👤 **Tipos de Usuário**

### **🔴 Administrador**
- **Acesso total** ao sistema
- **Gerenciar usuários** e permissões
- **Ver todos os RNCs**
- **Criar, editar, deletar** qualquer RNC

### **🟡 Usuário Normal**
- **Criar RNCs** próprios
- **Ver apenas** seus RNCs
- **Permissões limitadas**

## 🛠️ **Gerenciamento de Usuários**

### **Criar Novo Usuário**
1. **Login como admin**
2. **Acessar** "Gerenciar Usuários"
3. **Clicar** em "Novo Usuário"
4. **Preencher** dados e permissões
5. **Salvar**

### **Permissões Disponíveis**
- ✅ **create_rnc**: Criar RNCs
- ✅ **view_all_rncs**: Ver todos os RNCs
- ✅ **manage_users**: Gerenciar usuários
- ✅ **edit_rncs**: Editar RNCs
- ✅ **delete_rncs**: Deletar RNCs

### **Funções Disponíveis**
- 👤 **user**: Usuário normal
- 🔴 **admin**: Administrador completo

## 📊 **Estrutura do Banco de Dados**

### **Tabela: users**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    department TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    permissions TEXT DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

### **Tabela: rncs**
```sql
CREATE TABLE rncs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rnc_number TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    equipment TEXT,
    client TEXT,
    priority TEXT DEFAULT 'Média',
    status TEXT DEFAULT 'Pendente',
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## 🔧 **APIs Disponíveis**

### **Autenticação**
- `POST /api/login` - Login de usuário
- `GET /api/logout` - Logout
- `GET /api/user/info` - Informações do usuário

### **RNCs**
- `POST /api/rnc/create` - Criar RNC
- `GET /api/rnc/list` - Listar RNCs

### **Gerenciamento de Usuários (Admin)**
- `GET /api/admin/users` - Listar usuários
- `POST /api/admin/users` - Criar usuário
- `PUT /api/admin/users/<id>` - Atualizar usuário
- `DELETE /api/admin/users/<id>` - Deletar usuário

## 🎨 **Interface do Sistema**

### **Dashboard Principal**
- **Layout responsivo** baseado no Sigatel
- **Cards de RNC** com informações detalhadas
- **Filtros por status** (Todos, Pendentes, Concluídos)
- **Estatísticas em tempo real**
- **Botões de ação** contextuais

### **Gerenciamento de Usuários**
- **Interface moderna** e intuitiva
- **Formulários validados**
- **Permissões visuais** com checkboxes
- **Ações rápidas** (editar, deletar)

## 🔒 **Segurança**

### **Autenticação**
- **Senhas criptografadas** com bcrypt
- **Sessões seguras** com Flask
- **Controle de acesso** por rota

### **Autorização**
- **Verificação de permissões** em cada ação
- **Isolamento de dados** por usuário
- **Logs de auditoria** para ações críticas

## 📱 **Responsividade**

### **Desktop**
- **Layout em grid** para cards
- **Hover effects** completos
- **Animações suaves**

### **Mobile**
- **Layout adaptativo**
- **Touch-friendly**
- **Performance otimizada**

## 🚀 **Deploy**

### **Requisitos**
- Python 3.7+
- Flask
- SQLite3

### **Instalação**
```bash
pip install -r requirements.txt
python server_form.py
```

### **Configuração**
- **Porta padrão**: 5001
- **Banco de dados**: `ippel_system.db`
- **Logs**: Console e arquivo

## 📞 **Suporte**

### **Problemas Comuns**
1. **Erro de login**: Verificar credenciais
2. **Sem permissão**: Contatar administrador
3. **RNCs não aparecem**: Verificar permissões

### **Debug**
- Console do navegador (F12)
- Logs do servidor Python
- Verificar banco de dados

## 🎉 **Benefícios**

### **Para Administradores**
- **Controle total** do sistema
- **Gerenciamento de usuários** intuitivo
- **Relatórios completos**
- **Segurança avançada**

### **Para Usuários**
- **Interface simples** e intuitiva
- **Acesso rápido** aos RNCs
- **Feedback visual** imediato
- **Experiência gamificada**

## 🔄 **Fluxo de Trabalho**

### **1. Login**
- Acessar sistema
- Fazer login com credenciais
- Redirecionamento automático

### **2. Dashboard**
- Visualizar RNCs pessoais
- Ver estatísticas
- Acessar ações rápidas

### **3. Criar RNC**
- Preencher formulário
- Salvar no sistema
- Retorno ao dashboard

### **4. Gerenciamento (Admin)**
- Acessar área de usuários
- Criar/editar/deletar usuários
- Definir permissões

## 🎯 **Resultado Final**

Um sistema completo, seguro e profissional para gerenciamento de RNCs com controle granular de usuários e permissões! 🚀

### **Características Especiais**
- ✅ **Sistema único** (sem dependência do main_system.py)
- ✅ **Usuário admin** criado automaticamente
- ✅ **Gerenciamento completo** de usuários
- ✅ **Permissões granulares** e flexíveis
- ✅ **Interface moderna** baseada no Sigatel
- ✅ **Segurança avançada** com criptografia
- ✅ **Responsividade total** para todos os dispositivos
- ✅ **Performance otimizada** para uso corporativo 
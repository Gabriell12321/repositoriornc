# 🚀 Sistema IPPEL - Dois Servidores

Este sistema agora roda em **dois servidores separados** para melhor organização e controle de acesso.

## 📋 Estrutura dos Servidores

### 1. **Servidor do Formulário** (Porta 5001)
- **Arquivo**: `server_form.py`
- **Acesso**: `http://IP:5001`
- **Função**: Formulário público para criar RNCs
- **Usuários**: Qualquer pessoa da rede

### 2. **Servidor Admin** (Porta 5000)
- **Arquivo**: `main_system.py`
- **Acesso**: `http://IP:5000`
- **Função**: Painel administrativo completo
- **Usuários**: Administradores autorizados

## 🚀 Como Iniciar

### Opção 1: Scripts Automáticos (Recomendado)

#### Para o Painel Admin:
```bash
start_admin.bat
```

#### Para o Formulário:
```bash
start_form.bat
```

### Opção 2: Comandos Manuais

#### 1. Iniciar Servidor Admin (Primeiro):
```bash
python main_system.py
```

#### 2. Iniciar Servidor do Formulário:
```bash
python server_form.py
```

## 🌐 URLs de Acesso

Após iniciar ambos os servidores, você terá acesso a:

### 📊 Painel Admin
- **URL**: `http://SEU_IP:5000`
- **Login**: `admin@ippel.com.br` / `admin123`
- **Funcionalidades**:
  - Dashboard com estatísticas
  - Lista de todos os RNCs
  - Visualização detalhada
  - Gerenciamento de links únicos
  - Sistema de notificações

### 📋 Formulário RNC
- **URL**: `http://SEU_IP:5001`
- **Acesso**: Público (sem login)
- **Funcionalidades**:
  - Formulário para criar RNCs
  - Integração automática com o banco
  - Geração de PDF
  - Envio por email

## 🔄 Integração

Os dois servidores trabalham juntos:

1. **Formulário** → Cria RNCs via API
2. **Admin** → Gerencia e visualiza todos os RNCs
3. **Banco de Dados** → Compartilhado entre ambos

## 📱 Acesso na Rede Local

### Para outros dispositivos na rede:

1. **Descubra o IP do servidor**:
   ```bash
   ipconfig
   ```
   Procure por "IPv4 Address" (ex: 192.168.1.100)

2. **Acesse de qualquer dispositivo**:
   - Painel Admin: `http://192.168.1.100:5000`
   - Formulário: `http://192.168.1.100:5001`

## 🔧 Configuração

### Dependências
Certifique-se de ter instalado:
```bash
pip install -r requirements.txt
```

### Banco de Dados
O banco será criado automaticamente na primeira execução.

## 🛠️ Solução de Problemas

### Erro: "Servidor admin não está rodando"
- **Causa**: O servidor admin não foi iniciado
- **Solução**: Execute `start_admin.bat` primeiro

### Erro: "Porta já em uso"
- **Causa**: Outro processo está usando a porta
- **Solução**: Feche outros programas ou reinicie o computador

### Erro: "Python não encontrado"
- **Causa**: Python não está instalado ou não está no PATH
- **Solução**: Instale o Python e adicione ao PATH

## 📊 Fluxo de Trabalho

1. **Administrador** inicia ambos os servidores
2. **Usuários** acessam o formulário via `IP:5001`
3. **Usuários** criam RNCs no formulário
4. **Administrador** gerencia RNCs via `IP:5000`
5. **Sistema** envia notificações por email automaticamente

## 🔐 Segurança

- **Formulário**: Acesso público para criação
- **Admin**: Protegido por login
- **Banco**: Local (SQLite)
- **Rede**: Apenas rede local

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique se ambos os servidores estão rodando
2. Confirme se as portas 5000 e 5001 estão livres
3. Teste o acesso local antes de usar na rede 
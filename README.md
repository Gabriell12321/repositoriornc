## Otimização de Assets e Compressão HTTP

- Ativamos compressão HTTP (gzip/Brotli) automaticamente quando as dependências estão instaladas.
- Adicionamos um helper `asset_url()` no Jinja que prefere arquivos `.min.js` e `.min.css` quando disponíveis e inclui um parâmetro `?v=mtime` para cache busting.
- Para gerar versões minificadas dos assets, execute o script:
    - Windows PowerShell: `python scripts/minify_assets.py`
    - Os arquivos serão escritos ao lado dos originais com sufixo `.min.*`.

# 📧 Sistema RNC IPPEL - Servidor de E-mail

Sistema completo para geração e envio de relatórios de Não Conformidade (RNC) da IPPEL.

## 🚀 Instalação e Configuração

### Escolha sua opção:

#### **🐍 Python (Recomendado - Mais Simples)**
- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)
- Conta de e-mail Gmail (ou outro provedor)

#### **🟨 Node.js (Alternativa)**
- Node.js (versão 14 ou superior)
- NPM (Node Package Manager)
- Conta de e-mail Gmail (ou outro provedor)

### 2. Instalar Dependências

#### **🐍 Python:**
```bash
pip install -r requirements.txt
```

#### **🟨 Node.js:**
```bash
npm install
```

### 3. Configurar E-mail

#### Para Gmail:
1. **Ative a verificação em 2 etapas** na sua conta Google
2. **Gere uma senha de app**:
   - Vá em "Gerenciar sua Conta Google"
   - Segurança → Verificação em 2 etapas → Senhas de app
   - Gere uma senha para "Email"
3. **Configure as credenciais**:

   **🐍 Python** - Edite o arquivo `server.py`:
   ```python
   EMAIL_CONFIG = {
       'email': 'seu-email@gmail.com',    # Seu e-mail Gmail
       'password': 'sua-senha-de-app'     # Senha de app gerada
   }
   ```

   **🟨 Node.js** - Edite o arquivo `server.js`:
   ```javascript
   auth: {
       user: 'seu-email@gmail.com', // Seu e-mail Gmail
       pass: 'sua-senha-de-app'     // Senha de app gerada
   }
   ```

#### Para Outlook/Hotmail:
```javascript
const transporter = nodemailer.createTransporter({
    service: 'outlook',
    auth: {
        user: 'seu-email@outlook.com',
        pass: 'sua-senha'
    }
});
```

### 4. Iniciar o Servidor

#### **🐍 Python (Recomendado):**
```bash
python server.py
```
Ou duplo clique em: `start_python.bat`

#### **🟨 Node.js:**
```bash
npm start
```
Ou duplo clique em: `start.bat`

**Servidor Python**: http://localhost:5000
**Servidor Node.js**: http://localhost:3000

## 📋 Como Usar

### 1. Acessar o Sistema
- Abra o navegador
- Acesse: http://localhost:3000

- Marque os checkboxes conforme necessário

  - **Primeira Aba**: Descrição, Instrução, Causa
  - **Ação**: Ação a Ser Tomada

### 4. Gerar PDF
- Clique no botão vermelho "📄 Gerar Relatório PDF"
- O arquivo será baixado automaticamente

## 🔧 Configurações Avançadas

### Mudar Porta do Servidor
Edite o arquivo `server.js`:
```javascript
const PORT = 3000; // Mude para a porta desejada
```

### Usar Outro Provedor de E-mail
```javascript
// Para Yahoo
service: 'yahoo'

// Para Outlook

// Para servidor SMTP personalizado
host: 'smtp.seu-servidor.com',
port: 587,
secure: false
```

### Logs do Sistema
O servidor registra todos os e-mails enviados no console:
```
E-mail enviado: {
  messageId: 'abc123...',
  to: 'destinatario@email.com',
  subject: 'Relatório RNC...',
  type: 'first',
  timestamp: '2024-01-XX...'
}
```

## 🛠️ Desenvolvimento

### Modo de Desenvolvimento
```bash
npm run dev
```
O servidor reiniciará automaticamente quando você fizer alterações.

### Estrutura do Projeto
```
├── index.html          # Interface do usuário
├── server.js           # Servidor Node.js
├── package.json        # Dependências
└── README.md          # Este arquivo
```

## 🔒 Segurança

### Variáveis de Ambiente (Recomendado)
Crie um arquivo `.env`:
```env
EMAIL_USER=seu-email@gmail.com
EMAIL_PASS=sua-senha-de-app
PORT=3000
```

E instale o dotenv:
```bash
npm install dotenv
```

### Firewall
Certifique-se de que a porta 3000 está liberada no firewall.

## 📞 Suporte

### Problemas Comuns

#### 1. "Erro de conexão com o servidor"
- Verifique se o servidor está rodando: `npm start`
- Confirme se a porta 3000 está livre

#### 2. "Erro ao enviar e-mail"
- Verifique as credenciais no `server.js`
- Confirme se a verificação em 2 etapas está ativa (Gmail)
- Teste a senha de app

#### 3. "E-mail não chega"
- Verifique a pasta de spam
- Confirme se o e-mail está correto
- Verifique os logs do servidor

### Logs de Debug
Para ver logs detalhados, adicione no `server.js`:
```javascript
transporter.verify(function(error, success) {
    if (error) {
        console.log('Erro na configuração:', error);
    } else {
        console.log('Servidor pronto para enviar e-mails');
    }
});
```

## 📄 Licença

MIT License - IPPEL 2024 
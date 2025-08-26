# IPPEL - Sistema de Relatórios de Não Conformidade

## 🚀 Como Iniciar os Servidores

### Opção 1: Inicialização Automática (Recomendado)
```batch
# Duplo clique no arquivo ou execute no CMD:
iniciar_todos_cmd.bat
```

### Opção 2: Inicialização Manual

#### 1. Servidor Principal (OBRIGATÓRIO)
```batch
cd /d "G:\My Drive\Trabalhos pendentes\rncs\RELATORIO DE NÃO CONFORMIDADE IPPEL"
set RUST_IMAGES_URL=http://127.0.0.1:8081
set KOTLIN_UTILS_URL=http://127.0.0.1:8084
set JULIA_ANALYTICS_URL=http://127.0.0.1:8082
python server_form.py
```
**Acesso:** http://localhost:5001

#### 2. Rust Images Service (OPCIONAL)
```batch
cd /d "G:\My Drive\Trabalhos pendentes\rncs\RELATORIO DE NÃO CONFORMIDADE IPPEL\services\rust_images"
set RUST_IMAGES_ADDR=127.0.0.1:8081
cargo run --release
```
**Porta:** 8081 | **Teste:** curl http://127.0.0.1:8081/health

#### 3. Kotlin Utils Service (OPCIONAL)
```batch
cd /d "G:\My Drive\Trabalhos pendentes\rncs\RELATORIO DE NÃO CONFORMIDADE IPPEL\services\kotlin_utils"
set KOTLIN_UTILS_HOST=0.0.0.0
set KOTLIN_UTILS_PORT=8084
gradlew.bat run
```
**Porta:** 8084 | **Teste:** curl http://127.0.0.1:8084/health

#### 4. Julia Analytics Service (OPCIONAL)
```batch
cd /d "G:\My Drive\Trabalhos pendentes\rncs\RELATORIO DE NÃO CONFORMIDADE IPPEL\services\julia_analytics"
set JULIA_ANALYTICS_ADDR=127.0.0.1:8082
julia --project=. src\server.jl
```
**Porta:** 8082 | **Teste:** curl http://127.0.0.1:8082/health

## 🔧 Configuração Inicial

### Instalar Dependências
```batch
# Execute uma vez antes do primeiro uso:
instalar_dependencias.bat
```

### Login Padrão
- **URL:** http://localhost:5001
- **Email:** admin@ippel.com.br
- **Senha:** admin123

## 📋 Portas Utilizadas

| Serviço | Porta | Status | Função |
|---------|-------|--------|---------|
| **Backend Principal** | 5001 | Obrigatório | Sistema principal |
| Rust Images | 8081 | Opcional | Processamento de imagens |
| Kotlin Utils | 8084 | Opcional | Geração de QR codes |
| Julia Analytics | 8082 | Opcional | Analytics avançados |

## ⚠️ Notas Importantes

- **Execute sempre sem "Administrador"** (o drive G: pode não aparecer)
- **Apenas o Backend Principal é obrigatório** - outros são opcionais
- **Para rede externa:** use o IP da máquina em vez de localhost
- **Firewall:** libere a porta 5001 para acesso na rede

## 🌐 Acesso na Rede

Para acessar de outros dispositivos:
```batch
# Descobrir IP da máquina:
ipconfig | findstr "IPv4"

# Liberar firewall (executar como Admin):
netsh advfirewall firewall add rule name="IPPEL 5001" dir=in action=allow protocol=TCP localport=5001
```

**Acesso externo:** http://SEU_IP:5001

## 🛠️ Solução de Problemas

### Python não encontrado
```batch
# Instale Python de: https://python.org/downloads/
# Marque "Add Python to PATH" na instalação
```

### Drive G: não encontrado
```batch
# Feche terminais "Administrador" e use CMD normal
# Ou mude os caminhos para sua unidade local
```

### Serviços opcionais falhando
```batch
# O sistema funciona apenas com Python + Backend Principal
# Rust/Kotlin/Julia são opcionais para funcionalidades extras
```

---

## 🔧 Informações Técnicas Detalhadas

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

## Desenvolvimento

- TypeScript
    - Código-fonte em `static/ts`, saída em `static/compiled`.
    - Scripts:
        - `npm run build:ts` — compila uma vez
        - `npm run watch:ts` — compila em modo watch
    - Inclua os arquivos gerados no HTML com `asset_url('compiled/arquivo.js')`.

- Julia Analytics (opcional)
    - Serviço em `services/julia_analytics`
    - Rodar local:
        - Instale Julia, então:
            - `julia --project=. -e "using Pkg; Pkg.instantiate();"`
            - `julia --project=. src/server.jl`
    - Endpoints: `GET /health`, `GET /summary`
    - Variáveis de ambiente no Flask:
        - `JULIA_ANALYTICS_URL=http://127.0.0.1:8082`
    - API proxy no Flask: `GET /api/analytics/summary`

    - Go Reports (opcional)
        - Serviço em `services/go_reports`
        - Requisitos: Go 1.21+
        - Rodar local:
            - `go mod tidy`
            - `go run .`
            - Endereço configurável: `GO_REPORTS_ADDR=:8083`
        - Endpoints: `GET /health`, `GET /reports/rnc/:id.pdf`
        - Variáveis de ambiente no Flask:
            - `GO_REPORTS_URL=http://127.0.0.1:8083`
        - API proxy no Flask: `GET /api/reports/rnc/<id>.pdf`

    - Kotlin Utils (opcional)
        - Serviço em `services/kotlin_utils` (Ktor + ZXing)
        - Requisitos: JDK 17+, Gradle (wrapper incluído)
        - Rodar local (na pasta do serviço):
            - Windows PowerShell: `./gradlew.bat run`
            - Config: `KOTLIN_UTILS_HOST=0.0.0.0`, `KOTLIN_UTILS_PORT=8084`
        - Endpoints: `GET /health`, `GET /qr.png?text=...&size=256`
        - Variáveis de ambiente no Flask:
            - `KOTLIN_UTILS_URL=http://127.0.0.1:8084`
        - API proxy no Flask: `GET /api/utils/qr.png?text=...&size=256`

    - Swift Tools (opcional)
        - Serviço em `services/swift_tools` (SwiftNIO + CryptoSwift)
        - Requisitos: Swift 5.9+ (macOS ou WSL/Ubuntu com Swift instalado)
        - Rodar local (na pasta do serviço):
            - `swift build`; `swift run`
            - Config: `SWIFT_TOOLS_HOST=0.0.0.0`, `SWIFT_TOOLS_PORT=8085`
        - Endpoint esperado pelo client: `POST /hash` (body: texto puro) -> `{ ok: true, sha256: "..." }`
        - Variáveis de ambiente no Flask:
            - `SWIFT_TOOLS_URL=http://127.0.0.1:8085`
        - API proxy no Flask: `POST /api/utils/hash/sha256` (JSON `{text}` ou body texto)

    - Scala Tools (opcional)
        - Serviço em `services/scala_tools` (Akka HTTP)
        - Requisitos: Java 11+, sbt 1.10+
        - Rodar local (na pasta do serviço):
            - `sbt run`
            - Config: `SCALA_TOOLS_HOST=0.0.0.0`, `SCALA_TOOLS_PORT=8086`
        - Endpoints: `GET /health`, `POST /b64/encode` (body texto) -> `{ok,data}`, `POST /b64/decode` (body base64) -> `{ok,data}`
        - Variáveis de ambiente no Flask:
            - `SCALA_TOOLS_URL=http://127.0.0.1:8086`
        - API proxy no Flask:
            - `POST /api/utils/b64/encode`
            - `POST /api/utils/b64/decode`

    - Nim Tools (opcional)
        - Serviço em `services/nim_tools` (Jester)
        - Requisitos: Nim 1.6+, Nimble
        - Rodar local (na pasta do serviço):
            - `nimble run`
            - Config: `NIM_TOOLS_HOST=0.0.0.0`, `NIM_TOOLS_PORT=8087`
        - Endpoints: `GET /health`, `GET /uuid`, `GET /token?size=32`
        - Variáveis de ambiente no Flask:
            - `NIM_TOOLS_URL=http://127.0.0.1:8087`
        - API proxy no Flask:
            - `GET /api/utils/uuid`
            - `GET /api/utils/token?size=32`

    - V Tools (opcional)
        - Serviço em `services/v_tools` (vweb)
        - Requisitos: V 0.4+
        - Rodar local (na pasta do serviço):
            - `v run .`
            - Config: `V_TOOLS_HOST=0.0.0.0`, `V_TOOLS_PORT=8088`
        - Endpoints: `GET /health`, `GET /slug?text=...`
        - Variáveis de ambiente no Flask:
            - `V_TOOLS_URL=http://127.0.0.1:8088`
        - API proxy no Flask:
            - `GET /api/utils/slug?text=...`

    - Haskell Tools (opcional)
        - Serviço em `services/haskell_tools` (Scotty)
        - Requisitos: GHC + cabal-install ou Stack
        - Rodar local (na pasta do serviço):
            - Cabal: `cabal run`
            - Stack: `stack run`
            - Config: `HASKELL_TOOLS_HOST=0.0.0.0`, `HASKELL_TOOLS_PORT=8089`
        - Endpoints: `GET /health`, `POST /levenshtein` (body "a;b")
        - Variáveis de ambiente no Flask:
            - `HASKELL_TOOLS_URL=http://127.0.0.1:8089`
        - API proxy no Flask:
            - `POST /api/utils/levenshtein` (JSON `{a,b}` ou body "a;b")

    - Zig Tools (opcional)
        - Serviço em `services/zig_tools` (std.net TCP HTTP minimal)
        - Requisitos: Zig 0.11+
        - Rodar local (na pasta do serviço):
            - `zig build run`
            - Config: `ZIG_TOOLS_HOST=0.0.0.0`, `ZIG_TOOLS_PORT=8090`
        - Endpoints: `GET /health`, `POST /xxh3` (body texto)
        - Variáveis de ambiente no Flask:
            - `ZIG_TOOLS_URL=http://127.0.0.1:8090`
        - API proxy no Flask:
            - `POST /api/utils/xxh3`

    - Crystal Tools (opcional)
        - Serviço em `services/crystal_tools` (Kemal)
        - Requisitos: Crystal 1.8+, Shards
        - Rodar local (na pasta do serviço):
            - `shards install`; `crystal run src/server.cr`
            - Config: `CRYSTAL_TOOLS_HOST=0.0.0.0`, `CRYSTAL_TOOLS_PORT=8091`
        - Endpoints: `GET /health`, `POST /sha256`
        - Variáveis de ambiente no Flask:
            - `CRYSTAL_TOOLS_URL=http://127.0.0.1:8091`
        - API proxy no Flask:
            - `POST /api/utils/sha256`

    - Deno Tools (opcional)
        - Serviço em `services/deno_tools`
        - Requisitos: Deno 1.45+
        - Rodar local (na pasta do serviço):
            - `deno run --allow-env --allow-net server.ts`
            - Config: `DENO_TOOLS_HOST=0.0.0.0`, `DENO_TOOLS_PORT=8092`
        - Endpoints: `GET /health`, `POST /url/encode`, `POST /url/decode`
        - Variáveis de ambiente no Flask:
            - `DENO_TOOLS_URL=http://127.0.0.1:8092`
        - API proxy no Flask:
            - `POST /api/utils/url/encode`
            - `POST /api/utils/url/decode`
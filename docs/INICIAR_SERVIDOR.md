# 🚀 Guia de Inicialização do Servidor RNC

## ✅ Soluções Implementadas

### Problema Original:
- Ambiente virtual Python quebrado (apontando para Python 3.11 inexistente)
- Política de execução PowerShell restritiva
- Conflitos de caminho do Python

### Soluções Aplicadas:

## 🎯 Método Recomendado: Scripts de Inicialização

### Opção 1: Script Batch (Mais Simples)
```cmd
.\start_server.bat
```

### Opção 2: Script PowerShell
```powershell
.\start_server.ps1
```

### Opção 3: Comando Direto
```cmd
python server_form.py
```

## 🔧 Para Corrigir o Ambiente Virtual (Opcional):

1. **Remover ambiente virtual quebrado:**
   ```powershell
   Remove-Item -Recurse -Force .venv
   ```

2. **Criar novo ambiente virtual:**
   ```cmd
   python -m venv .venv
   ```

3. **Ativar ambiente virtual:**
   ```cmd
   .venv\Scripts\activate.bat
   ```

4. **Instalar dependências (se necessário):**
   ```cmd
   pip install flask werkzeug
   ```

## 📋 URLs do Servidor:

- **Login/Formulário**: http://192.168.0.157:5001
- **Admin Panel**: http://192.168.0.157:5000
- **Local**: http://127.0.0.1:5001

## 👤 Credenciais Admin:

- **Email**: admin@ippel.com.br
- **Senha**: admin123

## ⚡ Status Atual:

✅ Servidor funcionando com Python 3.13.7 global
✅ Startup otimizado (~2-3 segundos)
✅ Pool de conexões reduzido (5 conexões iniciais)
✅ Backup e compressão em background
✅ Scripts de inicialização criados

## 🚨 Solução de Problemas:

### Se der erro "execution policies":
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Se Python não for encontrado:
```cmd
where python
```

### Para verificar versão:
```cmd
python --version
```

## 📝 Recomendação:

**Use o arquivo `start_server.bat` para iniciar o servidor.**
É a forma mais simples e evita todos os problemas de ambiente virtual e políticas do PowerShell.
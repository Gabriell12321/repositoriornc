@echo off
chcp 65001 >nul
setlocal ENABLEDELAYEDEXPANSION

title IPPEL - Formulário RNC (HTTPS)
cd /d "%~dp0"

echo.
echo ========================================
echo    🔒 SERVIDOR FORMULÁRIO RNC - HTTPS
echo ========================================
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
  echo ❌ Python não encontrado! Instale o Python.
  pause
  exit /b 1
)

:: Verificar pyOpenSSL
python -c "import OpenSSL" >nul 2>&1
if %errorlevel% neq 0 (
  echo ⚠️  pyOpenSSL não encontrado. Instalando...
  pip install pyOpenSSL
)

:: Matar processos anteriores na porta 5001
echo 🔧 Liberando porta 5001...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001 ^| findstr LISTENING') do (
  taskkill /F /PID %%a >nul 2>&1
)

:: Aguardar liberação da porta
timeout /t 2 /nobreak >nul

:: Definir HTTPS
set IPPEL_ENABLE_HTTPS=1

:: Informar endereços
echo.
echo ✅ Servidor iniciando com HTTPS...
echo.
echo 📋 Acesse o formulário em:
echo    https://localhost:5001
echo    https://192.168.3.11:5001
echo.
echo ⚠️  IMPORTANTE: Aceite o aviso de certificado no navegador!
echo.
echo 🔧 Painel Admin em: http://192.168.3.11:5000
echo.
echo ========================================
echo.

:: Iniciar servidor
python server_form.py

pause

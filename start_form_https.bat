@echo off
chcp 65001 >nul
setlocal ENABLEDELAYEDEXPANSION

title IPPEL - Formulário (HTTPS)
cd /d "%~dp0"

echo.
echo ========================================
echo    🚀 IPPEL - Servidor do Formulário (HTTPS)
echo ========================================
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
  echo ❌ Python não encontrado! Instale o Python e tente novamente.
  pause
  exit /b 1
)

:: Definir variavel para HTTPS
set IPPEL_ENABLE_HTTPS=1

:: Opcional: SSL_CERTFILE e SSL_KEYFILE (se tiver cert valido)
if not "%1"=="" set SSL_CERTFILE=%1
if not "%2"=="" set SSL_KEYFILE=%2

if "%SSL_CERTFILE%"=="" (
  echo 🔒 Sem certificado fornecido: usando certificado adhoc (autoassinado).
) else (
  echo 🔒 Certificado: %SSL_CERTFILE%
  echo 🔑 Chave: %SSL_KEYFILE%
)

echo 🌐 Iniciando servidor seguro...
python server_form.py

endlocal
pause

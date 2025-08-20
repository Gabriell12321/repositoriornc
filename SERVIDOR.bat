@echo off
cd /d "%~dp0"
echo ========================================
echo    SERVIDOR DO FORMULARIO RNC
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Erro: Python não encontrado!
    echo Instale o Python e tente novamente.
    pause
    exit /b 1
)

REM Verificar dependencias basicas
echo 📦 Verificando dependencias...
python -c "import flask, flask_socketio, pythoncom" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Instalando dependencias essenciais...
    pip install flask flask-socketio
)

setlocal ENABLEDELAYEDEXPANSION

REM Habilitar HTTPS adhoc por padrao para evitar erro de handshake
set IPPEL_ENABLE_HTTPS=1
set PORT=5001

REM Informar URL
for /f "tokens=2 delims=: " %%a in ('ipconfig ^| findstr /R /C:"IPv4"') do (
  if not defined HOST_IP set HOST_IP=%%a
)
if "%HOST_IP%"=="" set HOST_IP=localhost

echo 🔒 HTTPS ativado (adhoc). Se tiver certificado, defina SSL_CERTFILE e SSL_KEYFILE antes de executar.
echo 🌐 Acesse: https://%HOST_IP%:%PORT%

echo.
echo 🚀 Iniciando servidor do formulario (PRODUCAO - WSGI Eventlet)...
set IPPEL_FORCE_HTTP=1
python -c "from server_form import app, socketio; socketio.run(app, host='0.0.0.0', port=5001, debug=False)"

endlocal

pause 
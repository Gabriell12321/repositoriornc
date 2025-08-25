@echo off
chcp 65001 >nul
title IPPEL - Producao (WSGI Eventlet)
cd /d "%~dp0"

echo ========================================
echo    🚀 IPPEL - Producao (WSGI Eventlet)
echo ========================================
echo.

REM Instalar/atualizar dependencias essenciais
echo 📦 Instalando dependencias de producao...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
python -m pip install eventlet flask-compress flask-limiter flask-talisman

REM Forcar HTTP (rede interna) e escutar em todas interfaces
set IPPEL_FORCE_HTTP=1

REM Iniciar servidor em modo producao (WSGI Eventlet)
echo 🌐 Iniciando em http://0.0.0.0:5001 (rede interna)
for /f "tokens=2 delims=: " %%a in ('ipconfig ^| findstr /R /C:"IPv4"') do (
  if not defined HOST_IP set HOST_IP=%%a
)
if "%HOST_IP%"=="" set HOST_IP=localhost
echo 📱 Acesse: http://%HOST_IP%:5001
echo.

python -c "from server_form import app, socketio; socketio.run(app, host='0.0.0.0', port=5001, debug=False)"

pause



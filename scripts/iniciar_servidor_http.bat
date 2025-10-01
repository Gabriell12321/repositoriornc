@echo off
chcp 65001 >nul
setlocal ENABLEDELAYEDEXPANSION

title IPPEL - Formulário RNC (HTTP)
cd /d "%~dp0"

echo.
echo ========================================
echo    🌐 SERVIDOR FORMULÁRIO RNC - HTTP
echo ========================================
echo.

:: Garantir que HTTPS esteja DESATIVADO
set IPPEL_ENABLE_HTTPS=
set SSL_CERTFILE=
set SSL_KEYFILE=
set IPPEL_FORCE_HTTP=1

:: Liberar porta 5001, se ocupada
echo 🔧 Liberando porta 5001...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001 ^| findstr LISTENING') do (
  taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

:: Detectar IP local (melhor esforço)
for /f "tokens=14" %%i in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v 127.0.0.1') do set LOCAL_IP=%%i
if "%LOCAL_IP%"=="" set LOCAL_IP=localhost

echo ✅ Iniciando somente em HTTP...
echo.
echo 📋 Login/Formulario: http://%LOCAL_IP%:5001
echo 🔧 Painel Admin:    http://%LOCAL_IP%:5000
echo.
echo ⚠️  Pressione Ctrl+C para parar o servidor
echo.

python -X utf8 -u server_form.py

endlocal
pause



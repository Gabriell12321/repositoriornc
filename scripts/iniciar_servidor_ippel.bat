@echo off
chcp 65001 >nul
title IPPEL - Sistema de Relatórios de Não Conformidade

REM Ir para a raiz do projeto (pasta acima de scripts)
pushd "%~dp0.." >nul 2>&1

echo.
echo ========================================
echo    🚀 IPPEL - Sistema de RNC
echo ========================================
echo.

:: Verificar se Python está instalado
echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo.
    echo 📥 Baixe e instale o Python em: https://www.python.org/downloads/
    echo ⚠️  Certifique-se de marcar "Add Python to PATH" durante a instalação
    echo.
    pause
    exit /b 1
)

:: Verificar se pip está disponível
echo 🔍 Verificando pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip não encontrado!
    echo.
    echo 📥 Reinstale o Python marcando "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: Verificar se as dependências estão instaladas
echo 🔍 Verificando dependências...
python -c "import flask, flask_socketio, gunicorn, eventlet, psutil, flask_compress, flask_limiter, flask_talisman" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Instalando dependências necessárias...
    echo.
    pip install flask flask-socketio gunicorn eventlet psutil python-dateutil flask-compress flask-limiter flask-talisman
    if %errorlevel% neq 0 (
        echo ❌ Erro ao instalar dependências!
        echo.
        echo 💡 Tente executar como administrador
        echo.
        pause
        exit /b 1
    )
    echo ✅ Dependências instaladas com sucesso!
    echo.
)

:: Verificar se o arquivo server_form.py existe
if not exist "server_form.py" (
    echo ❌ Arquivo server_form.py não encontrado!
    echo.
    echo 📁 Certifique-se de executar este iniciador a partir da pasta raiz do projeto.
    echo.
    pause
    exit /b 1
)

:: Verificar recursos do sistema
echo 🔍 Verificando recursos do sistema...
python -c "import psutil; cpu_count = psutil.cpu_count(); memory = psutil.virtual_memory(); print(f'💻 CPUs: {cpu_count}'); print(f'💾 RAM Total: {memory.total / 1024 / 1024 / 1024:.1f} GB'); print(f'💾 RAM Disponível: {memory.available / 1024 / 1024 / 1024:.1f} GB'); print('✅ Sistema adequado para 200+ usuários!' if cpu_count >= 4 and memory.total >= 8 * 1024 * 1024 * 1024 else '⚠️  Sistema pode suportar 200 usuários com performance limitada' if cpu_count >= 2 and memory.total >= 4 * 1024 * 1024 * 1024 else '❌ Sistema pode ter dificuldades com 200 usuários')"

echo.
echo ========================================
echo    🚀 Iniciando Servidor IPPEL
echo ========================================
echo.

:: Configurar variáveis de ambiente
set FLASK_ENV=production
set FLASK_DEBUG=0

:: Iniciar diretamente o servidor principal (server_form.py)
echo 🔄 Iniciando servidor principal (server_form.py)...
echo RUST_IMAGES_URL=%RUST_IMAGES_URL%
echo KOTLIN_UTILS_URL=%KOTLIN_UTILS_URL%
echo JULIA_ANALYTICS_URL=%JULIA_ANALYTICS_URL%
python -u server_form.py

echo.
echo ========================================
echo    👋 Servidor Encerrado
echo ========================================
echo.
pause
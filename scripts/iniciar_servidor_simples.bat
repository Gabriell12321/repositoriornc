@echo off
chcp 65001 >nul
title IPPEL - Sistema de Relatórios de Não Conformidade
cd /d "%~dp0"

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

:: Verificar se o arquivo server_form.py existe
if not exist "server_form.py" (
    echo ❌ Arquivo server_form.py não encontrado!
    echo.
    echo 📁 Certifique-se de que este arquivo .bat está na mesma pasta do projeto
    echo.
    pause
    exit /b 1
)

:: Verificar se as dependências estão instaladas
echo 🔍 Verificando dependências...
python -c "import flask, flask_socketio" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Dependências não encontradas!
    echo.
    echo 📦 Instale as dependências com: pip install flask flask-socketio gunicorn eventlet psutil
    echo.
    echo 💡 Ou execute o arquivo: iniciar_servidor_ippel.bat
    echo.
    pause
    exit /b 1
)

echo ✅ Todas as dependências encontradas!
echo.

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

:: Tentar iniciar com Gunicorn (produção)
echo 🔄 Tentando iniciar em modo PRODUÇÃO...
python start_production.py
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Erro ao iniciar com Gunicorn, tentando modo desenvolvimento...
    echo.
    
    :: Tentar iniciar em modo desenvolvimento
    echo 🔄 Iniciando em modo DESENVOLVIMENTO...
    python -c "import sys; sys.path.append('.'); from server_form import app, socketio; print('🌐 Servidor iniciado em: http://localhost:5001'); print('📱 Acesse no navegador ou compartilhe o IP da máquina'); print('⏹️  Pressione Ctrl+C para parar o servidor'); socketio.run(app, host='0.0.0.0', port=5001, debug=False)"
)

echo.
echo ========================================
echo    👋 Servidor Encerrado
echo ========================================
echo.
pause 
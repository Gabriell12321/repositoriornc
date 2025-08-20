@echo off
chcp 65001 >nul
title IPPEL - Instalador de Dependências
cd /d "%~dp0"

echo.
echo ========================================
echo    📦 IPPEL - Instalador de Dependências
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

echo ✅ Python e pip encontrados!
echo.

:: Atualizar pip, setuptools e wheel
echo 🔄 Atualizando pip, setuptools e wheel...
python -m pip install --upgrade pip setuptools wheel
if %errorlevel% neq 0 (
    echo ⚠️  Erro ao atualizar pip, continuando...
    echo.
)

:: Corrigir conflito do psutil (limpeza e reinstalação)
echo 🧹 Corrigindo possíveis conflitos do psutil...
pip uninstall -y psutil >nul 2>&1
pip uninstall -y psutil >nul 2>&1
python -c "import site,glob,os,shutil;paths=set(site.getsitepackages()+[site.getusersitepackages()]);
import itertools; 
files=list(itertools.chain.from_iterable([glob.glob(p+'\\\
psutil*') for p in paths]));
[
    (shutil.rmtree(f, True) if os.path.isdir(f) else (os.remove(f) if os.path.exists(f) else None))
    for f in files
]" >nul 2>&1
pip install --no-cache-dir --force-reinstall psutil
if %errorlevel% neq 0 (
    echo ❌ Falha ao reinstalar psutil
    echo Tente executar este instalador como Administrador.
    pause
    exit /b 1
)

:: Instalar dependências principais e utilitários de rede/compressão
echo 📦 Instalando dependências principais...
pip install --upgrade flask Flask-SocketIO python-socketio python-engineio flask-compress requests
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar Flask!
    echo.
    pause
    exit /b 1
)

:: Instalar dependências de produção (opcionais em Windows)
echo 📦 Instalando dependências de produção...
pip install --upgrade gunicorn eventlet python-dateutil
if %errorlevel% neq 0 (
    echo ⚠️  Erro ao instalar algumas dependências de produção!
    echo.
    echo 💡 O servidor funcionará em modo desenvolvimento
    echo.
)

:: Verificar instalação
echo 🔍 Verificando instalação...
python -c "import flask; print('✅ Flask instalado')" 2>nul || echo ❌ Flask não instalado
python -c "import flask_socketio; print('✅ Flask-SocketIO instalado')" 2>nul || echo ❌ Flask-SocketIO não instalado
python -c "import socketio; print('✅ python-socketio instalado')" 2>nul || echo ❌ python-socketio não instalado
python -c "import engineio; print('✅ python-engineio instalado')" 2>nul || echo ❌ python-engineio não instalado
python -c "import flask_compress; print('✅ Flask-Compress instalado')" 2>nul || echo ❌ Flask-Compress não instalado
python -c "import psutil,sys; print('✅ psutil instalado, versão:', psutil.__version__)" 2>nul || echo ❌ psutil não instalado
python -c "import eventlet; print('✅ Eventlet instalado')" 2>nul || echo ⚠️ Eventlet não instalado (opcional em Windows)
python -c "import gunicorn; print('✅ Gunicorn instalado')" 2>nul || echo ⚠️ Gunicorn não instalado (opcional em Windows)
echo.
echo 🎉 Verificação concluída!

echo.
echo ========================================
echo    ✅ Instalação Concluída!
echo ========================================
echo.
echo 🚀 Agora você pode executar:
echo    - iniciar_servidor_ippel.bat (recomendado)
echo    - iniciar_servidor_simples.bat
echo.
echo 📱 O servidor estará disponível em: http://localhost:5001
echo 🌐 Para acesso em rede, use o IP da máquina: http://SEU_IP:5001
echo.
pause 
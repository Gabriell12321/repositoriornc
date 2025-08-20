@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
title IPPEL - Instalador DEFINITIVO de Dependências
cd /d "%~dp0"

echo.
echo ================================================
echo    IPPEL - Instalador DEFINITIVO de Dependencias
echo ================================================
echo.

REM 1) Verificar Python
echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nao encontrado!
    echo.
    echo 📥 Baixe e instale o Python: https://www.python.org/downloads/
    echo ⚠️  Marque a opcao "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)

REM 2) Criar/Ativar ambiente virtual .venv
set "VENV_DIR=.venv"
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo 🔧 Criando ambiente virtual em %VENV_DIR% ...
    python -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo ❌ Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
)

call "%VENV_DIR%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo ❌ Falha ao ativar o ambiente virtual.
    pause
    exit /b 1
)

REM 3) Atualizar pip/setuptools/wheel
echo 🔄 Atualizando pip, setuptools e wheel...
python -m pip install --upgrade pip setuptools wheel --prefer-binary
if %errorlevel% neq 0 (
    echo ⚠️  Erro ao atualizar pip. Continuando...
)

REM 4) Instalar dependencias Python BASICAS (versoes estaveis usadas no projeto)
echo 📦 Instalando dependencias basicas do Python...
python -m pip install --no-cache-dir --prefer-binary ^
    Flask==2.3.3 ^
    Flask-Login==0.6.3 ^
    Werkzeug==2.3.7 ^
    Jinja2==3.1.2 ^
    MarkupSafe==2.1.3 ^
    itsdangerous==2.1.2 ^
    click==8.1.7 ^
    blinker==1.6.3 ^
    Flask-SocketIO==5.5.1 ^
    python-socketio==5.13.0 ^
    python-engineio==4.12.2 ^
    simple-websocket==1.1.0 ^
    Flask-Cors==4.0.0 ^
    requests==2.32.3
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependencias basicas do Python.
    pause
    exit /b 1
)

REM 5) Instalar dependencias de PRODUCAO (opcionais no Windows)
echo 🚀 Instalando dependencias de producao (opcional no Windows)...
python -m pip install --no-cache-dir --prefer-binary ^
    eventlet==0.33.3 ^
    gunicorn==21.2.0 ^
    psutil==5.9.6 ^
    python-dateutil==2.8.2
if %errorlevel% neq 0 (
    echo ⚠️  Algumas dependencias de producao nao foram instaladas. No Windows, isto e opcional.
)

REM 6) (Opcional) Instalar a partir de requirements.txt se existir (para cobrir variacoes)
if exist requirements.txt (
    echo 📄 requirements.txt encontrado. Instalando pacotes adicionais...
    python -m pip install --no-cache-dir --prefer-binary -r requirements.txt
)

REM 7) (Opcional) Instalar a partir de requirements_production.txt se existir
if exist requirements_production.txt (
    echo 📄 requirements_production.txt encontrado. Instalando pacotes adicionais de producao...
    python -m pip install --no-cache-dir --prefer-binary -r requirements_production.txt
)

REM 8) Verificacao de instalacao Python
echo 🔍 Verificando instalacao dos pacotes Python...
python - <<PYCHK
import importlib, sys
mods = [
    'flask','flask_login','werkzeug','jinja2','markupsafe','itsdangerous','click','blinker',
    'flask_socketio','socketio','engineio','simple_websocket','flask_cors','requests',
    'eventlet','psutil','dateutil'
]
ok = True
for m in mods:
    try:
        importlib.import_module(m)
        print(f"✅ {m} OK")
    except Exception as e:
        print(f"❌ {m} FALHOU: {e}")
        ok = False
sys.exit(0 if ok else 1)
PYCHK
if %errorlevel% neq 0 (
    echo ❌ Falha na verificacao de dependencias Python.
    pause
    exit /b 1
)

REM 9) (Opcional) Instalar dependencias Node se houver package.json e Node estiver instalado
if exist package.json (
    echo 📦 Detectado package.json. Verificando Node/NPM...
    node --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ⚠️  Node.js nao encontrado. Pule este passo se nao usar server.js.
    ) else (
        echo 🔄 Instalando dependencias Node...
        call npm install --no-fund --no-audit
        if %errorlevel% neq 0 (
            echo ⚠️  Falha ao instalar dependencias Node. Continue se nao for usar server.js.
        ) else (
            echo ✅ Dependencias Node instaladas.
        )
    )
)

echo.
echo ================================================
echo    ✅ Instalacao concluida com sucesso!
echo ================================================
echo.
echo Ambiente virtual: %CD%\%VENV_DIR%
echo.
echo Dicas de uso:
echo   1) Ativar venv:  call %VENV_DIR%\Scripts\activate.bat
echo   2) Iniciar Formulario (HTTP):  python server_form.py
echo   3) Iniciar Admin (HTTP):       python server.py
echo   4) Producao (Linux/WSL):       python start_production.py
echo.
echo Para HTTPS local, use: start_form_https.bat (se aplicavel)
echo.
pause




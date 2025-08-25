@echo off
chcp 65001 >nul
title IPPEL - Instalar TODAS as Dependencias (Windows)
cd /d "%~dp0"

echo.
echo ========================================
echo    📦 IPPEL - Instalacao de Dependencias
echo ========================================
echo.

REM 1) Verificar Python
echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
  echo ❌ Python nao encontrado. Instale em: https://www.python.org/downloads/ (marque "Add Python to PATH").
  pause
  exit /b 1
)

REM 2) Verificar pip
echo 🔍 Verificando pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
  echo ❌ pip nao encontrado. Reinstale o Python marcando "Add Python to PATH".
  pause
  exit /b 1
)

REM 3) Atualizar instalador
echo 🔄 Atualizando pip/setuptools/wheel...
python -m pip install --upgrade pip setuptools wheel
if %errorlevel% neq 0 echo ⚠️  Nao foi possivel atualizar pip; continuando...

REM 4) Instalar dependencias principais
echo 📦 Instalando dependencias do requirements.txt...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
  echo ❌ Falha ao instalar requirements.txt
  pause
  exit /b 1
)

REM 5) Instalar dependencias de producao (em Windows, gunicorn e opcional)
if exist requirements_production.txt (
  echo 📦 Instalando dependencias de producao (pode ignorar erros do gunicorn no Windows)...
  python -m pip install -r requirements_production.txt || echo ⚠️  Alguns pacotes de producao podem ser opcionais no Windows.
)

REM 6) Instalar extras usados pelo server_form.py
echo 📦 Instalando extras (compress, limiter, talisman, eventlet)...
python -m pip install flask-compress flask-limiter flask-talisman eventlet

REM 7) Verificacao rapida
echo.
echo 🔍 Verificando instalacao...
python - <<PYEND
import sys
mods = [
  'flask','flask_login','flask_socketio','eventlet',
  'python_socketio','python_engineio','flask_compress',
  'flask_limiter','flask_talisman','psutil'
]
ok = True
for m in mods:
    try:
        __import__(m)
        print(f'✅ {m} OK')
    except Exception as e:
        ok = False
        print(f'⚠️  Falhou: {m} -> {e}')
print('\nResultado:', 'SUCESSO' if ok else 'COM AVISOS')
PYEND

echo.
echo ========================================
echo    ✅ Instalacao concluida
echo ========================================
echo.
echo ➜ Para iniciar em producao (WSGI Eventlet):
echo    start_producao_eventlet.bat
echo ou SERVIDOR.bat
echo.
pause



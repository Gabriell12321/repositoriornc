@echo off
echo ========================================
echo    SERVIDOR ADMIN IPPEL
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

REM Verificar dependências
echo 📦 Verificando dependências...
pip show flask-login >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Dependências não encontradas. Instalando...
    pip install -r requirements.txt
)

REM Inicializar sistema se necessário
if not exist "ippel_system.db" (
    echo 🔧 Inicializando banco de dados...
    python init_system.py
)

echo.
echo 🚀 Iniciando servidor admin...
echo.
python main_system.py

pause 
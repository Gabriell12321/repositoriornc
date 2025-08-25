@echo off
cd /d "%~dp0"
echo ========================================
echo    Sistema RNC IPPEL - Python Server
echo ========================================
echo.

echo Verificando se o Python esta instalado...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao esta instalado!
    echo Por favor, instale o Python em: https://python.org/
    pause
    exit /b 1
)

echo Python encontrado!
echo.

echo Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Iniciando servidor Python...
echo ========================================
echo.
echo Servidor estara disponivel em: http://localhost:5000
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

python server.py

pause 
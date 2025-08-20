@echo off
echo ========================================
echo    Sistema RNC IPPEL - Servidor
echo ========================================
echo.

echo Verificando se o Node.js esta instalado...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Node.js nao esta instalado!
    echo Por favor, instale o Node.js em: https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js encontrado!
echo.

echo Instalando dependencias...
npm install
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Iniciando servidor...
echo ========================================
echo.
echo Servidor estara disponivel em: http://localhost:3000
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

npm start

pause 
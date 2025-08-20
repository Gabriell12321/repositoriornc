@echo off
chcp 65001 >nul
title Sistema IPPEL - Acesso Local

echo.
echo ========================================
echo    SISTEMA IPPEL - ACESSO LOCAL
echo ========================================
echo.

echo 🔧 Verificando dependências...
python -c "import flask, sqlite3" 2>nul
if errorlevel 1 (
    echo ❌ Dependências não encontradas. Instalando...
    pip install flask
    echo ✅ Dependências instaladas!
) else (
    echo ✅ Dependências OK!
)

echo.
echo 🌐 Obtendo informações de rede...
python -c "from config_local import LocalConfig; LocalConfig.print_network_info()"

echo.
echo 🚀 Iniciando servidor...
echo.
echo ⏳ Aguarde o servidor inicializar...
echo 📱 Você poderá acessar o sistema em outros dispositivos
echo    usando o IP mostrado acima
echo.
echo ⚠️  Pressione Ctrl+C para parar o servidor
echo.

python main_system.py

pause 
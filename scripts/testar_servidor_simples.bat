@echo off
echo ========================================
echo    TESTE DO SERVIDOR IPPEL
echo ========================================
echo.

echo Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo.
echo Verificando dependencias...
python -c "import flask, flask_socketio, psutil; print('✅ Dependencias OK')"
if %errorlevel% neq 0 (
    echo ERRO: Dependencias nao encontradas!
    echo Execute: pip install -r requirements_production.txt
    pause
    exit /b 1
)

echo.
echo Testando importacao do servidor...
python -c "from server_form import app, socketio; print('✅ Servidor importado com sucesso!')"
if %errorlevel% neq 0 (
    echo ERRO: Problema na importacao do servidor!
    pause
    exit /b 1
)

echo.
echo ========================================
echo    SERVIDOR PRONTO PARA USO!
echo ========================================
echo.
echo Para iniciar o servidor, execute:
echo   iniciar_servidor_ippel.bat
echo.
echo Ou para modo simples:
echo   iniciar_servidor_simples.bat
echo.
pause 
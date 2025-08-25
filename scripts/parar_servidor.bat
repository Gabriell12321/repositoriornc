@echo off
chcp 65001 >nul
title IPPEL - Parar Servidor

echo.
echo ========================================
echo    ⏹️  IPPEL - Parar Servidor
echo ========================================
echo.

echo 🔍 Procurando processos do servidor IPPEL...

:: Procurar processos Python relacionados ao IPPEL
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr /I "server_form" >nul
if %errorlevel% equ 0 (
    echo ⚠️  Encontrados processos Python do IPPEL
    echo 🔄 Parando processos...
    
    :: Parar processos Python que contêm "server_form"
    for /f "tokens=2 delims=," %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr /I "server_form"') do (
        echo 🛑 Parando processo: %%i
        taskkill /PID %%i /F >nul 2>&1
    )
)

:: Procurar processos Gunicorn
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr /I "gunicorn" >nul
if %errorlevel% equ 0 (
    echo ⚠️  Encontrados processos Gunicorn
    echo 🔄 Parando processos...
    
    :: Parar processos Gunicorn
    for /f "tokens=2 delims=," %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr /I "gunicorn"') do (
        echo 🛑 Parando processo: %%i
        taskkill /PID %%i /F >nul 2>&1
    )
)

:: Verificar se ainda há processos na porta 5001
echo 🔍 Verificando porta 5001...
netstat -ano | findstr :5001 >nul
if %errorlevel% equ 0 (
    echo ⚠️  Ainda há processos na porta 5001
    echo 🔄 Forçando parada...
    
    :: Parar todos os processos na porta 5001
    for /f "tokens=5" %%i in ('netstat -ano ^| findstr :5001') do (
        echo 🛑 Parando processo na porta 5001: %%i
        taskkill /PID %%i /F >nul 2>&1
    )
)

:: Verificar se os processos foram parados
timeout /t 2 /nobreak >nul

echo 🔍 Verificação final...
netstat -ano | findstr :5001 >nul
if %errorlevel% neq 0 (
    echo ✅ Servidor parado com sucesso!
    echo.
    echo 📊 Status:
    echo    - Porta 5001: Livre
    echo    - Processos IPPEL: Parados
    echo    - Recursos: Liberados
) else (
    echo ⚠️  Ainda há processos ativos
    echo 💡 Tente reiniciar o computador se necessário
)

echo.
echo ========================================
echo    ✅ Operação Concluída
echo ========================================
echo.
echo 🚀 Para iniciar novamente, execute:
echo    - iniciar_servidor_ippel.bat
echo    - iniciar_servidor_simples.bat
echo.
pause 
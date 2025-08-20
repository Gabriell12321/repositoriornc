@echo off
chcp 65001 >nul
title IPPEL - Verificar Status

echo.
echo ========================================
echo    📊 IPPEL - Status do Servidor
echo ========================================
echo.

echo 🔍 Verificando status do servidor IPPEL...
echo.

:: Verificar se há processos Python do IPPEL
echo 📋 Processos IPPEL:
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr /I "server_form" >nul
if %errorlevel% equ 0 (
    echo ✅ Servidor IPPEL está RODANDO
    for /f "tokens=1,2,3,4,5 delims=," %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr /I "server_form"') do (
        echo    - Processo: %%b (PID: %%c)
        echo    - Memória: %%d
        echo    - Status: %%e
    )
) else (
    echo ❌ Servidor IPPEL NÃO está rodando
)

echo.

:: Verificar se há processos Gunicorn
echo 📋 Processos Gunicorn:
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr /I "gunicorn" >nul
if %errorlevel% equ 0 (
    echo ✅ Gunicorn está RODANDO
    for /f "tokens=1,2,3,4,5 delims=," %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr /I "gunicorn"') do (
        echo    - Processo: %%b (PID: %%c)
        echo    - Memória: %%d
        echo    - Status: %%e
    )
) else (
    echo ❌ Gunicorn NÃO está rodando
)

echo.

:: Verificar porta 5001
echo 📋 Porta 5001:
netstat -ano | findstr :5001 >nul
if %errorlevel% equ 0 (
    echo ✅ Porta 5001 está EM USO
    for /f "tokens=1,2,3,4,5" %%a in ('netstat -ano ^| findstr :5001') do (
        echo    - Endereço: %%a
        echo    - Estado: %%b
        echo    - PID: %%e
    )
) else (
    echo ❌ Porta 5001 está LIVRE
)

echo.

:: Verificar arquivo de banco de dados
echo 📋 Banco de Dados:
if exist "ippel_system.db" (
    echo ✅ Arquivo ippel_system.db encontrado
    for %%A in ("ippel_system.db") do (
        echo    - Tamanho: %%~zA bytes
        echo    - Data: %%~tA
    )
) else (
    echo ❌ Arquivo ippel_system.db NÃO encontrado
)

echo.

:: Verificar recursos do sistema
echo 📋 Recursos do Sistema:
python -c "import psutil; cpu_count = psutil.cpu_count(); memory = psutil.virtual_memory(); cpu_percent = psutil.cpu_percent(); print(f'💻 CPUs: {cpu_count}'); print(f'💾 RAM Total: {memory.total / 1024 / 1024 / 1024:.1f} GB'); print(f'💾 RAM Disponível: {memory.available / 1024 / 1024 / 1024:.1f} GB'); print(f'💾 RAM Usada: {memory.percent}%'); print(f'🖥️  CPU Usada: {cpu_percent}%')"

echo.

:: Verificar conectividade
echo 📋 Teste de Conectividade:
ping -n 1 localhost >nul
if %errorlevel% equ 0 (
    echo ✅ Localhost responde
) else (
    echo ❌ Localhost não responde
)

echo.

:: Resumo do status
echo ========================================
echo    📊 RESUMO DO STATUS
echo ========================================

:: Verificar se o servidor está rodando
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr /I "server_form" >nul
if %errorlevel% equ 0 (
    echo ✅ SERVIDOR ATIVO
    echo 🌐 Acesse: http://localhost:5001
    echo 📱 Para parar: parar_servidor.bat
) else (
    echo ❌ SERVIDOR INATIVO
    echo 🚀 Para iniciar: iniciar_servidor_ippel.bat
)

echo.
echo ========================================
echo    ✅ Verificação Concluída
echo ========================================
echo.
pause 
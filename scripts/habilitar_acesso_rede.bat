@echo off
chcp 65001 >nul
title IPPEL - Habilitar Acesso em Rede (Porta 5001)
cd /d "%~dp0"

echo.
echo ========================================
echo    🌐 IPPEL - Acesso em Rede (5001/TCP)
echo ========================================
echo.

:: Verificar permissao de administrador
whoami /groups | find "S-1-5-32-544" >nul
if %errorlevel% neq 0 (
    echo ❌ Este script precisa ser executado como Administrador.
    echo.
    echo ➜ Clique com o botao direito no arquivo e escolha "Executar como administrador".
    echo.
    pause
    exit /b 1
)

echo 🔧 Recriando regras de firewall para a porta 5001 (TCP)...
netsh advfirewall firewall delete rule name="IPPEL Porta 5001 TCP" >nul 2>&1
netsh advfirewall firewall delete rule name="IPPEL Porta 5001 TCP Out" >nul 2>&1
netsh advfirewall firewall add rule name="IPPEL Porta 5001 TCP" dir=in action=allow protocol=TCP localport=5001 profile=any enable=yes >nul 2>&1
netsh advfirewall firewall set rule name="IPPEL Porta 5001 TCP" new edge=yes >nul 2>&1
rem (Opcional) Saida pela 5001
netsh advfirewall firewall add rule name="IPPEL Porta 5001 TCP Out" dir=out action=allow protocol=TCP remoteport=5001 profile=any enable=yes >nul 2>&1

echo 🔧 Liberando python.exe (todas as instalacoes encontradas)...
for %%P in ("%LocalAppData%\Programs\Python\Python313\python.exe" "C:\\Python313\\python.exe" "C:\\Program Files\\Python313\\python.exe" "C:\\Program Files\\Python312\\python.exe" "C:\\Program Files\\Python311\\python.exe" "C:\\Program Files (x86)\\Python313\\python.exe") do (
    if exist %%P (
        netsh advfirewall firewall add rule name="IPPEL Python 5001 - %%~nxP" dir=in action=allow program=%%P protocol=TCP localport=5001 profile=any enable=yes >nul 2>&1
    )
)
for /f "delims=" %%p in ('where python 2^>nul') do (
    netsh advfirewall firewall add rule name="IPPEL Python 5001 - Current" dir=in action=allow program="%%p" protocol=TCP localport=5001 profile=any enable=yes >nul 2>&1
)

echo 🔍 Descobrindo IP local...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "127.0.0.1" ^| findstr /v "Autoconfiguration"') do (
    set IP_TMP=%%a
    goto :after_ip
)
:after_ip
set IP=%IP_TMP: =%

echo.
echo ✅ Regras aplicadas.
echo.
if not "%IP%"=="" (
    echo ➜ Acesse a partir de outros computadores: http://%IP%:5001
) else (
    echo ⚠️ Nao foi possivel detectar o IP automaticamente. Descubra com: ipconfig
)
echo.
echo 💡 Caso ainda nao acesse, verifique:
echo    - Se todos os dispositivos estao na mesma rede
echo    - Se o antivirus nao bloqueia a porta 5001
echo    - Se o servidor esta rodando (SERVIDOR.bat)
echo    - (Opcional) Defina a rede como Privada para liberar compartilhamento
echo      powershell -Command "Get-NetConnectionProfile | Format-Table Name,NetworkCategory" 
echo      powershell -Command "Set-NetConnectionProfile -InterfaceAlias 'Ethernet' -NetworkCategory Private"
echo.
echo 🚀 Iniciando o servidor agora em uma nova janela...
start "IPPEL Servidor" "%~dp0SERVIDOR.bat"
echo.
pause



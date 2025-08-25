@echo off
chcp 65001 >nul
title IPPEL - FORÇAR LIBERAÇÃO DE IP/PORTA 5001
cd /d "%~dp0"

echo.
echo ========================================
echo    🔓 FORÇAR LIBERAÇÃO DE IP (5001)
echo ========================================
echo.

:: Verificar Administrador
whoami /groups | find "S-1-5-32-544" >nul
if %errorlevel% neq 0 (
    echo ❌ Execute este arquivo como ADMINISTRADOR.
    pause
    exit /b 1
)

echo 🔄 Ajustando perfil de rede para Privada (todas as conexoes ativas)...
powershell -NoProfile -Command "Get-NetConnectionProfile | Where-Object {$_.NetworkCategory -ne 'Private'} | Set-NetConnectionProfile -NetworkCategory Private" >nul 2>&1

echo 🧹 Limpando regras antigas IPPEL...
for %%R in ("IPPEL Porta 5001 TCP" "IPPEL Porta 5001 TCP Out" "IPPEL Python 5001" "IPPEL Python 5001 - Current" "IPPEL Any 5001 TCP In" "IPPEL Any 5001 TCP Out" "IPPEL Python Any In" "IPPEL Python Any Out") do (
    netsh advfirewall firewall delete rule name=%%R >nul 2>&1
)

echo 🔧 Criando regras gerais para a porta 5001 (TCP/IPv4 e IPv6)...
netsh advfirewall firewall add rule name="IPPEL Any 5001 TCP In" dir=in action=allow protocol=TCP localport=5001 profile=any enable=yes >nul 2>&1
netsh advfirewall firewall set rule name="IPPEL Any 5001 TCP In" new edge=yes >nul 2>&1
netsh advfirewall firewall add rule name="IPPEL Any 5001 TCP Out" dir=out action=allow protocol=TCP remoteport=5001 profile=any enable=yes >nul 2>&1

echo 🔧 Liberando python.exe (todas as instalacoes encontradas) para qualquer porta (IN/OUT)...
for /f "delims=" %%p in ('where python 2^>nul') do (
    netsh advfirewall firewall add rule name="IPPEL Python Any In" dir=in action=allow program="%%p" protocol=ANY profile=any enable=yes >nul 2>&1
    netsh advfirewall firewall add rule name="IPPEL Python Any Out" dir=out action=allow program="%%p" protocol=ANY profile=any enable=yes >nul 2>&1
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
if not "%IP%"=="" (
    echo ➜ Acesse: http://%IP%:5001
) else (
    echo ⚠️ Detecte o IP com: ipconfig
)
echo.
echo 🚀 Iniciando o servidor agora em uma nova janela...
start "IPPEL Servidor" "%~dp0SERVIDOR.bat"
echo.
pause



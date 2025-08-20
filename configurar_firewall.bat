@echo off
chcp 65001 >nul
title IPPEL - Configurar Firewall (Porta 5001)
cd /d "%~dp0"

set PORT=5001

echo ========================================
echo    🔥 CONFIGURAR FIREWALL - IPPEL (TCP/%PORT%)
echo ========================================
echo.

rem Verificar privilegios de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
  echo ⚠️  Este script precisa de privilegios de ADMINISTRADOR.
  echo    Solicitando elevacao...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)

echo 🔧 Configurando regras persistentes para todas as redes...
echo.

rem Descobrir caminho do Python (para regra por programa)
set "PYTHON_EXE="
for /f "delims=" %%P in ('where python 2^>nul') do (
  if not defined PYTHON_EXE set "PYTHON_EXE=%%P"
)

rem Remover regras antigas para evitar duplicacao
for %%R in (
  "IPPEL HTTPS - Entrada"
  "IPPEL HTTPS - Saida"
  "IPPEL Porta 5001 TCP"
  "IPPEL Porta 5001 TCP Out"
  "IPPEL Any 5001 TCP In"
  "IPPEL Any 5001 TCP Out"
  "IPPEL Python 5001"
  "IPPEL Python 5001 - Current"
  "IPPEL 5001 TCP In"
  "IPPEL 5001 TCP Out"
) do (
  netsh advfirewall firewall delete rule name=%%R >nul 2>&1
)

rem Criar regras de porta (entrada/saida) para todos os perfis
netsh advfirewall firewall add rule name="IPPEL 5001 TCP In"  dir=in  action=allow protocol=TCP localport=%PORT%  profile=any enable=yes >nul
netsh advfirewall firewall set rule  name="IPPEL 5001 TCP In"  new edge=yes >nul
netsh advfirewall firewall add rule name="IPPEL 5001 TCP Out" dir=out action=allow protocol=TCP remoteport=%PORT% profile=any enable=yes >nul

rem Regras por programa (Python) - opcional mas util quando a porta muda
if defined PYTHON_EXE (
  netsh advfirewall firewall add rule name="IPPEL Python - In"  dir=in  action=allow program="%PYTHON_EXE%" profile=any enable=yes >nul
  netsh advfirewall firewall add rule name="IPPEL Python - Out" dir=out action=allow program="%PYTHON_EXE%" profile=any enable=yes >nul
)

echo ✅ Regras aplicadas com sucesso (todas as redes).
echo.

rem Mostrar IP para acesso
for /f "tokens=2 delims=: " %%a in ('ipconfig ^| findstr /R /C:"IPv4"') do (
  if not defined HOST_IP set HOST_IP=%%a
)
if "%HOST_IP%"=="" set HOST_IP=localhost
echo 📱 Acesse pelo navegador: http://%HOST_IP%:%PORT%
echo.

echo 🔎 Verifique as regras com:
echo     netsh advfirewall firewall show rule name^="IPPEL 5001 TCP In"
echo     netsh advfirewall firewall show rule name^="IPPEL 5001 TCP Out"
echo.
pause

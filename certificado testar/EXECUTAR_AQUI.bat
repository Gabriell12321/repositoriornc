@echo off
title Instalador de Certificado SSL - RNC IPPEL

:: Manter janela sempre aberta
if "%1" neq "KEEP_OPEN" (
    start "Instalador SSL" cmd /k "%~f0" KEEP_OPEN
    exit
)

echo.
echo ========================================
echo   INSTALADOR DE CERTIFICADO SSL
echo ========================================
echo.
echo Verificando permissoes...

:: Verificar se já está rodando como admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Executando como administrador
    echo.
    echo Iniciando instalacao...
    echo.
    call "%~dp0gerar_e_instalar_certificado.bat"
    goto :end
)

:: Não é admin, solicitar elevação
echo.
echo [!] Precisa de permissao de administrador
echo.
echo Abrindo janela com permissoes elevadas...
echo Clique em SIM quando perguntado.
echo.
powershell -Command "Start-Process cmd.exe -ArgumentList '/k', '%~dp0gerar_e_instalar_certificado.bat' -Verb RunAs"

:end
echo.
echo Pressione qualquer tecla para fechar esta janela...
pause >nul

@echo off
title GERAR CERTIFICADO OFICIAL PARA GPO
cls

:: Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo.
    echo [X] ERRO: Execute como ADMINISTRADOR!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   GERAR CERTIFICADO OFICIAL IPPEL RNC
echo ========================================
echo.
echo Este script ira gerar um certificado
echo oficial para instalar via GPO em todos
echo os computadores da rede.
echo.
echo Servidor: https://172.25.100.105:5001
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

:: Criar diretório
set "CERT_DIR=%~dp0certificado_oficial"
if not exist "%CERT_DIR%" mkdir "%CERT_DIR%"

:: Executar PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0GERAR_CERTIFICADO_OFICIAL.ps1" -OutputDir "%CERT_DIR%"

if %errorlevel% equ 0 (
    color 0A
    echo.
    echo ========================================
    echo   SUCESSO!
    echo ========================================
    echo.
    echo Certificados gerados em:
    echo %CERT_DIR%
    echo.
    echo Arquivos:
    echo   - IPPEL_RNC_Official.pfx (GPO)
    echo   - IPPEL_RNC_Official.cer (publico)
    echo   - IPPEL_RNC_Official.pem (servidor)
    echo.
    echo SENHA: IPPEL@2025#RNC
    echo.
) else (
    color 0C
    echo.
    echo [X] ERRO ao gerar certificado!
    echo.
)

echo Pressione qualquer tecla para fechar...
pause >nul

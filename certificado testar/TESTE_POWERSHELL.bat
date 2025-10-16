@echo off
title TESTE - Geracao de Certificado
cls
echo.
echo ========================================
echo   TESTE DE GERACAO DE CERTIFICADO
echo ========================================
echo.
echo Este e um teste para verificar se o
echo script PowerShell funciona corretamente.
echo.
echo Pressione qualquer tecla para iniciar...
pause >nul

echo.
echo Testando PowerShell...
echo.

set "TEST_DIR=%~dp0test_certs"
if not exist "%TEST_DIR%" mkdir "%TEST_DIR%"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0generate_cert.ps1" -CertDir "%TEST_DIR%" -CertFile "%TEST_DIR%\test_cert.pem" -CertCrt "%TEST_DIR%\test_cert.crt"

if %errorlevel% equ 0 (
    color 0A
    echo.
    echo ========================================
    echo   SUCESSO!
    echo ========================================
    echo.
    echo O script PowerShell funcionou!
    echo Arquivos criados em: %TEST_DIR%
    echo.
) else (
    color 0C
    echo.
    echo ========================================
    echo   ERRO!
    echo ========================================
    echo.
    echo O script PowerShell falhou.
    echo Veja as mensagens de erro acima.
    echo.
)

echo Pressione qualquer tecla para fechar...
pause >nul

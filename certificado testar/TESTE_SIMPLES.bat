@echo off
title TESTE - Janela nao fecha
cls
echo.
echo ========================================
echo   TESTE DE SCRIPT
echo ========================================
echo.
echo Se voce esta vendo esta mensagem,
echo significa que o script esta funcionando!
echo.
echo Esta janela NAO vai fechar sozinha.
echo.
echo ========================================
echo.
echo Pressione qualquer tecla para continuar
echo com a instalacao do certificado...
pause >nul

:: Chamar o script principal
call "%~dp0gerar_e_instalar_certificado.bat"

echo.
echo ========================================
echo   FIM DO TESTE
echo ========================================
echo.
pause

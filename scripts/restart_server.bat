@echo off
echo ===================================
echo    REINICIANDO SERVIDOR IPPEL
echo ===================================
echo.

:: Verificar se há processos Python rodando
echo Verificando processos Python em execução...
tasklist /fi "imagename eq python.exe" /fo table /nh

echo.
echo Encerrando processos Python (se existirem)...
taskkill /im python.exe /f 2>nul
if %errorlevel% equ 0 (
    echo Processos Python encerrados com sucesso.
) else (
    echo Nenhum processo Python encontrado em execução.
)

echo.
echo Aguardando 2 segundos...
timeout /t 2 /nobreak > nul

echo.
echo Iniciando servidor novamente...
start "Servidor IPPEL" cmd /c "python server_form.py & pause"

echo.
echo Servidor reiniciado! Acesse http://localhost:5000 para verificar.
echo.
echo IMPORTANTE: O botão de impressão deve estar visível no dashboard agora.
echo ===================================

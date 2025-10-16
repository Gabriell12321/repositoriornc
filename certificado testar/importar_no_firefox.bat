@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║        GUIA RÁPIDO - IMPORTAR CERTIFICADO NO FIREFOX      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Este script irá abrir as páginas necessárias para você
echo importar o certificado no Firefox.
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    PASSO A PASSO                           ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 1️⃣  O Firefox será aberto na página de configurações
echo.
echo 2️⃣  Na página que abrir:
echo    • Role até "Certificados"
echo    • Clique em "Ver certificados..."
echo.
echo 3️⃣  Na janela de certificados:
echo    • Vá para aba "Autoridades"
echo    • Clique em "Importar..."
echo.
echo 4️⃣  Selecione o arquivo:
echo    • Navegue até: %~dp0certs\ippel_cert.pem
echo    • Marque: ☑ "Confiar nesta CA para identificar sites"
echo    • Clique em "OK"
echo.
echo 5️⃣  Reinicie o Firefox
echo.
echo 6️⃣  Acesse: https://rnc.ippel.com.br:5001
echo.
echo.
echo Pressione qualquer tecla para abrir o Firefox...
pause >nul

:: Abrir Firefox na página de configurações
start firefox "about:preferences#privacy"

echo.
echo ✅ Firefox aberto!
echo.
echo Role até "Certificados" e siga os passos acima.
echo.
echo O arquivo do certificado está em:
echo %~dp0certs\ippel_cert.pem
echo.
echo.
pause

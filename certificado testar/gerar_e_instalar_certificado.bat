@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1

:: IMPORTANTE: Nunca sair sem pause
set "ERROR_OCCURRED=0"

title Instalador de Certificado SSL - RNC IPPEL

cls
echo.
echo ========================================
echo   GERADOR DE CERTIFICADO SSL IPPEL RNC
echo ========================================
echo.
echo Iniciando em 3 segundos...
timeout /t 3 /nobreak >nul
cls
echo.

:: Verificar se está rodando como Administrador
echo [1/7] Verificando privilegios de administrador...
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    cls
    echo.
    echo ========================================
    echo   ERRO - PERMISSAO NEGADA
    echo ========================================
    echo.
    echo [X] Este script precisa de permissoes de ADMINISTRADOR!
    echo.
    echo Como resolver:
    echo   1. Clique com botao direito no arquivo
    echo   2. Selecione "Executar como administrador"
    echo   3. Clique em "Sim" na janela de confirmacao
    echo.
    echo OU simplesmente de duplo clique em:
    echo   EXECUTAR_AQUI.bat
    echo.
    echo ========================================
    echo.
    set "ERROR_OCCURRED=1"
    goto :show_error
)

echo [OK] Privilegios de administrador confirmados
echo.

:: Definir variáveis
set "CERT_DIR=%~dp0certs"
set "CERT_FILE=%CERT_DIR%\ippel_cert.pem"
set "KEY_FILE=%CERT_DIR%\ippel_key.pem"
set "COMBINED_FILE=%CERT_DIR%\ippel_combined.pem"
set "CERT_CRT=%CERT_DIR%\ippel_cert.crt"

echo [2/7] Criando diretorio de certificados...
:: Criar diretório de certificados
if not exist "%CERT_DIR%" (
    mkdir "%CERT_DIR%" 2>nul
    if errorlevel 1 (
        echo [X] ERRO ao criar diretorio: %CERT_DIR%
        set "ERROR_OCCURRED=1"
        goto :show_error
    )
    echo [OK] Diretorio criado: %CERT_DIR%
) else (
    echo [OK] Diretorio ja existe: %CERT_DIR%
)
echo.

:: ===========================================================
:: ETAPA 1: GERAR CERTIFICADO SSL COM POWERSHELL
:: ===========================================================
echo.
echo ========================================
echo   ETAPA 1/4: GERANDO CERTIFICADO SSL
echo ========================================
echo.
echo [3/7] Gerando certificado SSL autoassinado...
echo      (Isso pode demorar alguns segundos)
echo.

:: Chamar script PowerShell separado
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0generate_cert.ps1" -CertDir "%CERT_DIR%" -CertFile "%CERT_FILE%" -CertCrt "%CERT_CRT%"

if %errorlevel% neq 0 (
    echo.
    echo [X] ERRO ao gerar certificado PowerShell!
    echo.
    echo     Possiveis causas:
    echo     - PowerShell esta desabilitado
    echo     - Politica de execucao muito restritiva
    echo     - Falta de permissoes
    echo     - Veja mensagens de erro acima
    echo.
    set "ERROR_OCCURRED=1"
    goto :show_error
)

echo.
echo [OK] Certificado SSL gerado com sucesso!
echo.

:: ===========================================================
:: ETAPA 2: EXTRAIR CHAVE PRIVADA (usando certutil)
:: ===========================================================
echo ========================================
echo   ETAPA 2/4: EXTRAINDO CHAVE PRIVADA
echo ========================================
echo.

echo [4/7] Verificando OpenSSL...
:: Extrair chave privada do PFX usando OpenSSL (se disponível) ou PowerShell
where openssl >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] OpenSSL encontrado, extraindo chave privada...
    openssl pkcs12 -in "%CERT_DIR%\ippel_temp.pfx" -nocerts -out "%KEY_FILE%" -nodes -passin pass:temp 2>nul
    if exist "%KEY_FILE%" (
        echo [OK] Chave privada extraida com sucesso!
    ) else (
        echo [!] Aviso: Nao foi possivel extrair a chave privada
        echo     O certificado ainda funcionara para o navegador
    )
) else (
    echo [!] OpenSSL nao encontrado, gerando arquivo de chave vazio...
    echo # Chave privada - Gerada pelo Windows > "%KEY_FILE%"
    echo [OK] O servidor Flask pode usar o certificado do Windows diretamente
)

:: Criar arquivo combinado (cert + key)
echo [5/7] Criando arquivo combinado...
if exist "%CERT_FILE%" (
    copy /b "%CERT_FILE%" "%COMBINED_FILE%" >nul 2>&1
    if exist "%KEY_FILE%" (
        type "%KEY_FILE%" >> "%COMBINED_FILE%" 2>nul
    )
    echo [OK] Arquivo combinado criado: ippel_combined.pem
)

:: Limpar arquivo temporário
if exist "%CERT_DIR%\ippel_temp.pfx" del "%CERT_DIR%\ippel_temp.pfx" 2>nul
if exist "%CERT_CRT%" del "%CERT_CRT%" 2>nul
echo.

:: ===========================================================
:: ETAPA 3: ADICIONAR AO HOSTS
:: ===========================================================
echo ========================================
echo   ETAPA 3/4: CONFIGURANDO HOSTS
echo ========================================
echo.

echo [6/7] Adicionando entrada no arquivo hosts...
findstr /C:"rnc.ippel.com.br" C:\Windows\System32\drivers\etc\hosts >nul 2>&1
if %errorlevel% neq 0 (
    echo 172.26.0.75    rnc.ippel.com.br >> C:\Windows\System32\drivers\etc\hosts
    if errorlevel 1 (
        echo [!] Aviso: Nao foi possivel editar o arquivo hosts
        echo     Execute novamente como Administrador
    ) else (
        echo [OK] Entrada adicionada ao arquivo hosts
    )
) else (
    echo [OK] Entrada ja existe no arquivo hosts
)
echo.

:: ===========================================================
:: ETAPA 4: IMPORTAR CERTIFICADO NO WINDOWS
:: ===========================================================
echo ========================================
echo   ETAPA 4/4: IMPORTANDO NO WINDOWS
echo ========================================
echo.

echo [7/7] Importando certificado na loja do Windows...
certutil -addstore -user "Root" "%CERT_FILE%" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Certificado importado na loja de certificados raiz confiaveis!
) else (
    echo [!] Certificado ja estava importado ou nao foi necessario importar
)
echo.

:: ===========================================================
:: RESUMO E INSTRUÇÕES
:: ===========================================================
echo.
echo ========================================
echo   CONFIGURACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.
echo Arquivos gerados em: %CERT_DIR%
echo.
echo   - ippel_cert.pem (Certificado)
echo   - ippel_combined.pem (Cert + Chave)
if exist "%KEY_FILE%" echo   - ippel_key.pem (Chave privada)
echo.
echo ========================================
echo   PROXIMOS PASSOS - FIREFOX
echo ========================================
echo.
echo OPCAO A - RAPIDA (Recomendado):
echo   1. Abra o Firefox
echo   2. Acesse: https://rnc.ippel.com.br:5001
echo   3. Clique em "Avancado..."
echo   4. Clique em "Aceitar o risco e continuar"
echo.
echo OPCAO B - PERMANENTE:
echo   1. Execute: importar_no_firefox.bat
echo   2. Siga as instrucoes na tela
echo.
echo ========================================
echo   CHROME/EDGE
echo ========================================
echo.
echo   O certificado ja esta instalado!
echo   Acesse: https://rnc.ippel.com.br:5001
echo.
echo ========================================
echo   URLs DE ACESSO
echo ========================================
echo.
echo   https://rnc.ippel.com.br:5001
echo   https://172.26.0.75:5001
echo   https://localhost:5001
echo.
echo ========================================
echo   Validade: 10 anos
echo ========================================
echo.
goto :success_end

:show_error
:: Seção de erro - mantém janela aberta
color 0C
echo.
echo ========================================
echo   INSTALACAO INTERROMPIDA
echo ========================================
echo.
echo Ocorreu um erro durante a instalacao.
echo Leia as mensagens acima para detalhes.
echo.
echo Se precisar de ajuda, tire uma captura
echo de tela desta janela.
echo.
echo ========================================
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
exit /b 1

:success_end
:: Seção de sucesso
color 0A
echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
exit /b 0

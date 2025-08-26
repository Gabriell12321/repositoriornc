@echo off
chcp 65001 >nul
title IPPEL - Iniciar Todos os Serviços
setlocal EnableExtensions

echo ========================================
echo  🚀 IPPEL - Iniciando Todos os Serviços
echo ========================================
echo.

REM Detectar a raiz do projeto (pasta onde está este .bat)
set "ROOT=%~dp0"
if "%ROOT:~-1%" == "\" set "ROOT=%ROOT:~0,-1%"

echo 📂 Projeto: %ROOT%

REM Verificar se o diretório existe (teste do drive G:)
if not exist "%ROOT%\NUL" (
    echo ❌ ERRO: Pasta do projeto não acessível!
    echo    Você está executando em modo Administrador?
    echo    O drive G: (Google Drive) não é visível em sessões elevadas.
    echo.
    echo 💡 SOLUÇÃO:
    echo    1. Feche TODAS as janelas
    echo    2. Clique com botão DIREITO no .bat
    echo    3. Escolha "Abrir" (NÃO "Executar como administrador")
    echo.
    pause
    exit /b 1
)

REM Verificar se está em modo administrador
net session >nul 2>&1
if %errorlevel%==0 (
    echo ❌ ERRO: Executando em modo Administrador!
    echo    O drive G: não está acessível em sessões elevadas.
    echo.
    echo 💡 SOLUÇÃO:
    echo    1. Feche esta janela
    echo    2. Execute o .bat SEM "Administrador"
    echo    3. Duplo clique normal no arquivo
    echo.
    pause
    exit /b 1
)

REM Verificar Python
echo [1/5] 🐍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo 📥 Execute primeiro: instalar_dependencias.bat
    pause
    exit /b 1
)
echo ✅ Python disponível

echo.
echo [2/5] 🦀 Iniciando Rust Images (8081)...
if exist "%ROOT%\services\rust_images\Cargo.toml" (
    cargo --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Abrindo Rust Images em nova janela...
        start "🦀 Rust Images (8081)" cmd /k "pushd \"%ROOT%\services\rust_images\" && set RUST_IMAGES_ADDR=127.0.0.1:8081 && echo 🦀 Iniciando Rust Images... && echo Pasta: %%cd%% && cargo run --release"
    ) else (
        echo ⚠️  Cargo não encontrado, pulando Rust Images
    )
) else (
    echo ⚠️  Serviço Rust não encontrado, pulando
)

echo.
echo [3/5] ☕ Iniciando Kotlin Utils (8084)...
if exist "%ROOT%\services\kotlin_utils\build.gradle.kts" (
    java --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Abrindo Kotlin Utils em nova janela...
        start "☕ Kotlin Utils (8084)" cmd /k "pushd \"%ROOT%\services\kotlin_utils\" && set KOTLIN_UTILS_HOST=0.0.0.0 && set KOTLIN_UTILS_PORT=8084 && echo ☕ Iniciando Kotlin Utils... && echo Pasta: %%cd%% && gradlew.bat run"
    ) else (
        echo ⚠️  Java não encontrado, pulando Kotlin Utils
    )
) else (
    echo ⚠️  Serviço Kotlin não encontrado, pulando
)

echo.
echo [4/5] 🔬 Iniciando Julia Analytics (8082)...
if exist "%ROOT%\services\julia_analytics\src\server.jl" (
    julia --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Abrindo Julia Analytics em nova janela...
        start "🔬 Julia Analytics (8082)" cmd /k "pushd \"%ROOT%\services\julia_analytics\" && set JULIA_ANALYTICS_ADDR=127.0.0.1:8082 && echo 🔬 Iniciando Julia Analytics... && echo Pasta: %%cd%% && julia --project=. src\server.jl"
    ) else (
        echo ⚠️  Julia não encontrada, pulando Julia Analytics
    )
) else (
    echo ⚠️  Serviço Julia não encontrado, pulando
)

echo.
echo [5/5] 🌐 Aguardando 3 segundos para serviços iniciarem...
timeout /t 3 /nobreak >nul

echo.
echo 🚀 Iniciando Backend Principal (5001)...
echo ✅ Abrindo IPPEL Backend em nova janela...

REM Configurar variáveis de ambiente para integração
set "RUST_IMAGES_URL=http://127.0.0.1:8081"
set "KOTLIN_UTILS_URL=http://127.0.0.1:8084"
set "JULIA_ANALYTICS_URL=http://127.0.0.1:8082"

start "🌐 IPPEL Backend (5001)" cmd /k "pushd \"%ROOT%\" && set RUST_IMAGES_URL=http://127.0.0.1:8081 && set KOTLIN_UTILS_URL=http://127.0.0.1:8084 && set JULIA_ANALYTICS_URL=http://127.0.0.1:8082 && echo 🌐 Iniciando Backend Principal... && echo Pasta: %%cd%% && echo. && echo 📋 URLs dos serviços: && echo    RUST_IMAGES_URL=%%RUST_IMAGES_URL%% && echo    KOTLIN_UTILS_URL=%%KOTLIN_UTILS_URL%% && echo    JULIA_ANALYTICS_URL=%%JULIA_ANALYTICS_URL%% && echo. && python server_form.py"

echo.
echo ========================================
echo  ✅ TODOS OS SERVIÇOS INICIADOS!
echo ========================================
echo.
echo 🌐 ACESSO AO SISTEMA:
echo    Local: http://localhost:5001
echo    Rede:  http://SEU_IP:5001
echo.
echo 👤 LOGIN PADRÃO:
echo    Email: admin@ippel.com.br
echo    Senha: admin123
echo.
echo 📊 SERVIÇOS AUXILIARES:
echo    🦀 Rust Images: http://127.0.0.1:8081/health
echo    ☕ Kotlin Utils: http://127.0.0.1:8084/health  
echo    🔬 Julia Analytics: http://127.0.0.1:8082/health
echo.
echo 🔧 CONTROLE:
echo    - Cada serviço abre em sua própria janela
echo    - Use Ctrl+C em cada janela para parar
echo    - Feche todas as janelas para parar tudo
echo.
echo ⚠️  IMPORTANTE:
echo    - Se algum serviço falhar, o sistema ainda funcionará
echo    - Apenas o Backend Principal (5001) é obrigatório
echo    - Execute sempre sem "Administrador"
echo.

echo Aguardando 5 segundos antes de abrir o navegador...
timeout /t 5 /nobreak >nul

echo 🌐 Abrindo navegador...
start http://localhost:5001

echo.
echo Pressione qualquer tecla para fechar esta janela de controle...
pause >nul

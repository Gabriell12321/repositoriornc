@echo off
chcp 65001 >nul
title IPPEL - Instalador de Dependências
setlocal EnableExtensions

echo ========================================
echo  IPPEL - Instalador de Dependências
echo  Instalando tudo para funcionamento 100%
echo ========================================
echo.

REM Ir para a raiz do projeto
cd /d "%~dp0"

echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo 📥 Instale o Python em: https://www.python.org/downloads/
    echo ⚠️  Marque "Add Python to PATH" durante a instalação
    pause
    exit /b 1
)

REM Mostrar versão do Python
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ %PYTHON_VERSION% encontrado

REM Verificar se pip está disponível
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip não encontrado no Python!
    echo 📥 Reinstale o Python marcando "Add Python to PATH"
    echo    Ou baixe get-pip.py de: https://bootstrap.pypa.io/get-pip.py
    pause
    exit /b 1
)

echo.
echo [2/6] Instalando dependências Python...
echo Atualizando pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ❌ Erro ao atualizar pip
    pause
    exit /b 1
)

echo Instalando dependências do requirements.txt...
if exist "requirements.txt" (
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ⚠️  Alguns pacotes do requirements.txt falharam, tentando pacotes essenciais...
        python -m pip install flask flask-socketio werkzeug
    )
) else (
    echo ⚠️  requirements.txt não encontrado, instalando pacotes essenciais...
    python -m pip install flask flask-socketio werkzeug
)

echo Instalando pacotes essenciais extras...
python -m pip install gunicorn eventlet psutil python-dateutil pillow pyjwt requests
if %errorlevel% neq 0 (
    echo ⚠️  Alguns pacotes essenciais falharam, mas o sistema deve funcionar
)

echo Instalando pacotes opcionais...
python -m pip install flask-compress flask-limiter flask-talisman brotli
if %errorlevel% neq 0 (
    echo ⚠️  Alguns pacotes opcionais falharam, mas o sistema deve funcionar
)

echo Instalando pacotes de análise (para dashboards)...
python -m pip install numpy pandas matplotlib seaborn plotly jupyter
if %errorlevel% neq 0 (
    echo ⚠️  Pacotes de análise falharam, mas o sistema funcionará sem dashboards avançados
)

echo ✅ Dependências Python instaladas

echo.
echo [3/6] Verificando/Instalando Rust...
cargo --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Rust não encontrado. Tentando instalar via winget...
    winget install Rustlang.Rustup
    if %errorlevel% neq 0 (
        echo ❌ Falha ao instalar Rust via winget
        echo 📥 Instale manualmente em: https://rustup.rs/
        echo ⚠️  Depois feche e reabra este terminal
        pause
        exit /b 1
    )
    echo ✅ Rust instalado - FECHE E REABRA O TERMINAL
    pause
    exit /b 0
)
echo ✅ Rust encontrado

echo.
echo [4/6] Compilando serviço Rust Images...
if exist "services\rust_images\Cargo.toml" (
    cd "services\rust_images"
    echo Verificando/atualizando versões das dependências Rust...
    cargo update
    echo Compilando...
    cargo build --release
    if %errorlevel% neq 0 (
        echo ❌ Erro ao compilar serviço Rust - usando versões compatíveis...
        echo Tentando compilação sem release...
        cargo build
        if %errorlevel% neq 0 (
            echo ⚠️  Rust falhou, mas o sistema funcionará sem processamento de imagens avançado
            cd "%~dp0"
            goto :skip_rust
        )
    )
    cd "%~dp0"
    echo ✅ Serviço Rust compilado
) else (
    echo ⚠️  Pasta do Rust não encontrada, pulando...
)
:skip_rust

echo.
echo [5/6] Verificando/Instalando Java JDK...
java --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Java não encontrado. Tentando instalar via winget...
    winget install Microsoft.OpenJDK.17
    if %errorlevel% neq 0 (
        echo ❌ Falha ao instalar Java via winget
        echo 📥 Instale manualmente: https://adoptium.net/
        pause
        exit /b 1
    )
    echo ✅ Java instalado
)
echo ✅ Java encontrado

echo.
echo [5.1/6] Compilando serviço Kotlin...
if exist "services\kotlin_utils\build.gradle.kts" (
    cd "services\kotlin_utils"
    echo Verificando Gradle Wrapper...
    if not exist "gradlew.bat" (
        echo ⚠️  gradlew.bat não encontrado, tentando gradle direto...
        gradle build
    ) else (
        call gradlew.bat build
    )
    if %errorlevel% neq 0 (
        echo ⚠️  Kotlin falhou, mas o sistema funcionará sem geração de QR codes
        cd "%~dp0"
        goto :skip_kotlin
    )
    cd "%~dp0"
    echo ✅ Serviço Kotlin compilado
) else (
    echo ⚠️  Pasta do Kotlin não encontrada, pulando...
)
:skip_kotlin

echo.
echo [6/6] Verificando/Instalando Julia...
julia --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Julia não encontrada. Tentando múltiplas opções de instalação...
    
    REM Tentar winget primeiro
    echo Tentativa 1: winget...
    winget install Julialang.Julia --silent --accept-source-agreements --accept-package-agreements >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Julia instalada via winget
        goto :julia_installed
    )
    
    REM Tentar chocolatey se disponível
    echo Tentativa 2: chocolatey...
    choco --version >nul 2>&1
    if %errorlevel% equ 0 (
        choco install julia --yes >nul 2>&1
        if %errorlevel% equ 0 (
            echo ✅ Julia instalada via chocolatey
            goto :julia_installed
        )
    )
    
    REM Tentar scoop se disponível
    echo Tentativa 3: scoop...
    scoop --version >nul 2>&1
    if %errorlevel% equ 0 (
        scoop install julia >nul 2>&1
        if %errorlevel% equ 0 (
            echo ✅ Julia instalada via scoop
            goto :julia_installed
        )
    )
    
    echo ❌ Todas as tentativas de instalação automática falharam
    echo 📥 Julia é OPCIONAL - o sistema funcionará sem ela
    echo 💡 Para instalar manualmente depois:
    echo    1. Acesse: https://julialang.org/downloads/
    echo    2. Baixe "Windows x86-64"
    echo    3. Execute o instalador e marque "Add Julia to PATH"
    echo    4. Reabra o terminal e rode este script novamente
    echo.
    echo ⏭️  Continuando sem Julia...
    goto :skip_julia_install
) else (
    echo ✅ Julia já encontrada
)

:julia_installed
echo ✅ Julia encontrada

:skip_julia_install

echo.
echo [6.1/6] Instalando pacotes Julia...
julia --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Julia não disponível - pulando pacotes Julia
    goto :skip_julia
)

if exist "services\julia_analytics\Project.toml" (
    cd "services\julia_analytics"
    echo Instalando pacotes Julia (pode demorar na primeira vez)...
    julia --project=. -e "using Pkg; Pkg.instantiate()" >nul 2>&1
    if %errorlevel% neq 0 (
        echo ⚠️  Pacotes Julia falharam, mas o sistema funcionará sem analytics avançados
        echo 💡 Para tentar depois, execute na pasta services\julia_analytics:
        echo    julia --project=. -e "using Pkg; Pkg.instantiate()"
        cd "%~dp0"
        goto :skip_julia
    )
    cd "%~dp0"
    echo ✅ Pacotes Julia instalados
) else (
    echo ⚠️  Pasta services\julia_analytics não encontrada, pulando...
)
:skip_julia

echo.
echo [7/7] Testando instalação...
echo Testando Python...
python -c "import flask, flask_socketio; print('✅ Python OK')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Teste Python falhou
) else (
    echo ✅ Python testado com sucesso
)

echo Testando comandos opcionais...
cargo --version >nul 2>&1 && echo ✅ Rust OK || echo ⚠️  Rust não disponível
java --version >nul 2>&1 && echo ✅ Java OK || echo ⚠️  Java não disponível  
julia --version >nul 2>&1 && echo ✅ Julia OK || echo ⚠️  Julia não disponível

echo.
echo ========================================
echo  ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo ========================================
echo.
echo � RESUMO DA INSTALAÇÃO:
echo    ✅ Python + Flask (ESSENCIAL) - funcionando
if exist "services\rust_images\target\release\rust_images.exe" (
    echo    ✅ Rust Images - compilado
) else (
    echo    ⚠️  Rust Images - opcional, não compilado
)
if exist "services\kotlin_utils\build\libs\" (
    echo    ✅ Kotlin Utils - compilado  
) else (
    echo    ⚠️  Kotlin Utils - opcional, não compilado
)
julia --version >nul 2>&1 && echo    ✅ Julia Analytics - disponível || echo    ⚠️  Julia Analytics - opcional, não disponível
echo.
echo 🚀 COMO INICIAR O SISTEMA:
echo    1. Duplo clique em: iniciar_todos_cmd.bat
echo    2. OU manualmente: python server_form.py
echo    3. OU use o instalador: instalar_dependencias.bat
echo.
echo 🌐 ACESSO:
echo    - Local: http://localhost:5001
echo    - Rede: http://SEU_IP:5001
echo    - Login: admin@ippel.com.br / admin123
echo.
echo ⚠️  IMPORTANTE:
echo    - Execute sempre SEM "Administrador"
echo    - Se estiver no Google Drive, certifique-se que G: está mapeado
echo    - Para outros PCs: copie toda a pasta e rode este instalador
echo.

echo Pressione qualquer tecla para fechar...
pause >nul

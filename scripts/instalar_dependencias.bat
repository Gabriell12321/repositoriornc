title IPPEL - Instalador de Dependências
@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion
title IPPEL - Instalador de Dependências

rem Detectar raiz (pasta pai de \scripts)
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
pushd "%ROOT%" >nul 2>&1 || ( echo [ERRO] Nao consegui acessar a raiz: "%ROOT%" & pause & exit /b 1 )

echo.
echo ========================================
echo    IPPEL - Instalador de Dependencias
echo ========================================
echo Raiz: %ROOT%
echo.

rem === Python / venv ===
echo [1/5] Verificando/CRIANDO ambiente Python (.venv)...
if not exist "%ROOT%\.venv\Scripts\python.exe" (
    where py >nul 2>&1 && (
        echo  - Criando venv com py -3...
        py -3 -m venv "%ROOT%\.venv"
    ) || (
        echo [ERRO] py.exe nao encontrado. Instale Python 3 e tente novamente: https://www.python.org/downloads/
        pause & exit /b 1
    )
)
set "PY=%ROOT%\.venv\Scripts\python.exe"
set "PIP=%ROOT%\.venv\Scripts\pip.exe"

echo  - Atualizando pip/setuptools/wheel...
"%PY%" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 echo  - [AVISO] Falha ao atualizar pip; continuando...

echo  - Instalando dependencias de requirements.txt...
"%PIP%" install -r "%ROOT%\requirements.txt"
if errorlevel 1 (
    echo [ERRO] Falha ao instalar requirements.txt
    pause & exit /b 1
)

if exist "%ROOT%\requirements_production.txt" (
    echo  - Instalando extras de producao (opcional)...
    "%PIP%" install -r "%ROOT%\requirements_production.txt" || echo  - [AVISO] Alguns pacotes de producao falharam (ok no Windows)
)

echo  - Verificando pacotes principais...
"%PY%" -c "import flask,requests,PIL,flask_socketio,flask_compress; print('OK')" >nul 2>&1 || (
    echo [ERRO] Falta pacote Python essencial. Veja erros acima.
    pause & exit /b 1
)

rem === Kotlin / Gradle ===
echo.
echo [2/5] Preparando servico Kotlin (se Java instalado)...
java -version >nul 2>&1
if errorlevel 1 (
    echo  - Java nao encontrado. Pulando build Kotlin.
) else (
    if exist "%ROOT%\services\kotlin_utils\gradlew.bat" (
        pushd "%ROOT%\services\kotlin_utils" >nul
        echo  - Baixando dependencias Gradle (primeira vez pode demorar)...
        cmd /d /c gradlew.bat -v >nul 2>&1
        cmd /d /c gradlew.bat build -x test
        if errorlevel 1 (
            echo  - [AVISO] build Kotlin falhou (o servico pode ainda iniciar com gradlew run); verifique logs ao iniciar.
        ) else (
            echo  - Kotlin pronto.
        )
        popd >nul
    ) else (
        echo  - Servico Kotlin nao encontrado. Pulando.
    )
)

rem === Rust ===
echo.
echo [3/5] Preparando servico Rust...
cargo --version >nul 2>&1
if errorlevel 1 (
    echo  - Cargo nao encontrado. Pulando build Rust (sera compilado ao rodar).
) else (
    if exist "%ROOT%\services\rust_images\Cargo.toml" (
        pushd "%ROOT%\services\rust_images" >nul
        echo  - Compilando release (pode demorar apenas na primeira vez)...
        cmd /d /c cargo build --release
        if errorlevel 1 (
            echo  - [AVISO] build Rust falhou; sera tentado compilar na hora do start.
        ) else (
            echo  - Rust pronto.
        )
        popd >nul
    ) else (
        echo  - Servico Rust nao encontrado. Pulando.
    )
)

rem === Checagem rapida ===
echo.
echo [4/5] Checando imports Python...
"%PY%" - <<PY
import sys
mods = [
    'flask','flask_socketio','python_socketio','python_engineio','flask_compress',
    'requests','PIL','cssmin','rjsmin','jwt','psutil']
missing=[]
for m in mods:
    try:
        __import__(m)
    except Exception as e:
        missing.append((m,str(e)))
print('OK' if not missing else 'MISSING:'+str(missing))
PY

rem === Final ===
echo.
echo [5/5] Concluido.
echo  - Venv: %PY%
echo  - Para iniciar tudo: iniciar_todos_definitivo.bat
echo  - Para iniciar apenas backend: scripts\run_backend_only.bat
echo.
pause
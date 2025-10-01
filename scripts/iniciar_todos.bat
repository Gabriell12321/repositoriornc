@echo off
chcp 65001 >nul
setlocal EnableExtensions

REM Detecta a raiz do repo (.. a partir de scripts)
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI"

title IPPEL - Iniciar Todos
echo [DEBUG] cwd inicial: %cd%
echo [DEBUG] script: %~f0
echo [DEBUG] script_dir: %SCRIPT_DIR%

REM Valida raiz existente
if not exist "%ROOT%\NUL" (
  echo [ERRO] Caminho raiz nao encontrado:
  echo        %ROOT%
  echo Verifique se o drive (G:) esta montado e tente novamente.
  echo Dica: Se esta janela estiver em modo Administrador, o drive do Google (G:) pode nao estar disponivel.
  echo       Feche e execute o script sem "Executar como administrador".
  pause
  exit /b 1
)

REM Detecta se esta em modo administrador (net session retorna 0 apenas quando admin)
net session >nul 2>&1
if %errorlevel%==0 call :_ADMIN_WARN

echo ========================================
echo  Iniciando todos os serviços (Rust/Kotlin/Julia + IPPEL)
echo  Raiz: %ROOT%
echo ========================================
echo.

REM ---- RUST IMAGES (8081) ----
set "RUST_DIR=%ROOT%\services\rust_images"
echo [INFO] RUST_DIR=%RUST_DIR%
if exist "%RUST_DIR%\Cargo.toml" (
  where cargo >nul 2>&1
  if errorlevel 1 (
    echo [AVISO] cargo nao encontrado. Pulei Rust Images.
  ) else (
    echo [+] Abrindo Rust Images em 127.0.0.1:8081 ...
    start "Rust Images (8081)" cmd /k pushd "%RUST_DIR%" ^& set RUST_IMAGES_ADDR=127.0.0.1:8081 ^& cargo run --release
  )
)
if not exist "%RUST_DIR%\Cargo.toml" echo [AVISO] Pasta/arquivo do Rust nao encontrado. Pulei Rust Images.

REM ---- KOTLIN UTILS (8084) ----
set "KOTLIN_DIR=%ROOT%\services\kotlin_utils"
echo [INFO] KOTLIN_DIR=%KOTLIN_DIR%
if exist "%KOTLIN_DIR%\build.gradle.kts" (
  echo [+] Abrindo Kotlin Utils em 0.0.0.0:8084 ...
  start "Kotlin Utils (8084)" cmd /k pushd "%KOTLIN_DIR%" ^& set KOTLIN_UTILS_HOST=0.0.0.0 ^& set KOTLIN_UTILS_PORT=8084 ^& call gradlew.bat run
)
if not exist "%KOTLIN_DIR%\build.gradle.kts" echo [AVISO] Pasta/arquivo do Kotlin nao encontrado. Pulei Kotlin Utils.

REM ---- JULIA ANALYTICS (8082) ----
set "JULIA_DIR=%ROOT%\services\julia_analytics"
echo [INFO] JULIA_DIR=%JULIA_DIR%
if exist "%JULIA_DIR%\src\server.jl" (
  where julia >nul 2>&1
  if errorlevel 1 (
    echo [AVISO] julia nao encontrada. Pulei Julia Analytics.
  ) else (
    echo [+] Abrindo Julia Analytics em 127.0.0.1:8082 ...
  start "Julia Analytics (8082)" cmd /k pushd "%JULIA_DIR%" ^& set JULIA_ANALYTICS_ADDR=127.0.0.1:8082 ^& julia --project=. src/server.jl
  )
)
if not exist "%JULIA_DIR%\src\server.jl" echo [AVISO] Pasta/arquivo da Julia nao encontrado. Pulei Julia Analytics.

REM ---- BACKEND IPPEL (5001) ----
echo [+] Abrindo Backend IPPEL (5001) com integracoes (server_form.py)...
start "IPPEL Backend (5001)" cmd /k pushd "%ROOT%" ^& set RUST_IMAGES_URL=http://127.0.0.1:8081 ^& set KOTLIN_UTILS_URL=http://127.0.0.1:8084 ^& set JULIA_ANALYTICS_URL=http://127.0.0.1:8082 ^& python -u server_form.py

echo.
echo Tudo iniciado (cada servico em sua janela). Use Ctrl+C em cada janela para parar.
echo.
echo Pressione qualquer tecla para fechar esta janela de controle...
pause >nul
exit /b 0

:_ADMIN_WARN
echo [AVISO] Esta janela esta em modo Administrador.
echo O drive de rede G: pode nao estar acessivel em janelas elevadas.
echo Se aparecer "The system cannot find the path specified",
echo feche esta janela e execute o atalho sem Administrador.
echo.
exit /b 0

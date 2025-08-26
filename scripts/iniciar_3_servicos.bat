@echo off
chcp 65001 >nul
title Iniciar 3 Serviços (Rust, Kotlin, Julia)

REM Detecta a raiz do projeto a partir desta pasta (.. de scripts)
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI"

echo =============================================
echo  Iniciando microserviços: Rust, Kotlin, Julia
echo  Raiz: %ROOT%
echo =============================================
echo.

REM Verificações básicas de ferramentas
where cargo >nul 2>&1
if errorlevel 1 echo [AVISO] cargo nao encontrado. Instale o Rust (https://rustup.rs/).

if exist "%ROOT%\services\kotlin_utils\gradlew.bat" (
  set "GRADLEW=%ROOT%\services\kotlin_utils\gradlew.bat"
) else (
  echo [AVISO] gradlew.bat nao encontrado em services\kotlin_utils. Abra esse diretorio e rode 'gradle wrapper' se necessario.
)

where julia >nul 2>&1
if errorlevel 1 echo [AVISO] julia nao encontrada no PATH. Instale Julia (https://julialang.org/).

echo Abrindo janelas separadas...

REM Rust Images (8081)
start "RUST Images (8081)" cmd /k "cd /d \"%ROOT%\services\rust_images\" ^&^& set RUST_IMAGES_ADDR=127.0.0.1:8081 ^&^& cargo run --release"

REM Kotlin Utils (8084)
start "Kotlin Utils (8084)" cmd /k "cd /d \"%ROOT%\services\kotlin_utils\" ^&^& set KOTLIN_UTILS_HOST=0.0.0.0 ^&^& set KOTLIN_UTILS_PORT=8084 ^&^& .\gradlew.bat run"

REM Julia Analytics (8082)
start "Julia Analytics (8082)" cmd /k "cd /d \"%ROOT%\services\julia_analytics\" ^&^& set JULIA_ANALYTICS_ADDR=127.0.0.1:8082 ^&^& julia --project=. src/server.jl"

echo.
echo URLs de teste:
echo  - Rust:   http://127.0.0.1:8081/health
echo  - Kotlin: http://127.0.0.1:8084/health
echo  - Julia:  http://127.0.0.1:8082/health
echo.
echo Dica: defina no terminal do backend (antes de inicia-lo):
echo  set RUST_IMAGES_URL=http://127.0.0.1:8081
echo  set KOTLIN_UTILS_URL=http://127.0.0.1:8084
echo  set JULIA_ANALYTICS_URL=http://127.0.0.1:8082
echo.
echo Pronto! As janelas foram abertas. Para encerrar um servico, feche a janela correspondente.
echo.
pause

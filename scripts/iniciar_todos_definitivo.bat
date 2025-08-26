@echo off
chcp 65001 >nul
title IPPEL - Iniciar 4 Serviços (Definitivo)
setlocal EnableExtensions EnableDelayedExpansion

:: =====================
:: Contexto do projeto (pasta raiz = pai de \scripts)
:: =====================
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

echo ========================================
echo  Iniciando 4 serviços - IPPEL
echo ========================================
echo Pasta do projeto: "%ROOT%"

:: =====================
:: Impedir execução como Administrador (Drive G:)
:: =====================
net session >nul 2>&1
if %errorlevel%==0 (
  echo [AVISO] Executando como Administrador. Se o drive em Nuvem nao montar, execute sem elevacao.
)

:: =====================
:: Verificações básicas (acesso à raiz via pushd)
:: =====================
pushd "%ROOT%" >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Pasta do projeto nao acessivel: "%ROOT%"
  pause
  exit /b 1
)
popd

:: Detectar Python: venv -> py -3 -> python (nao abortar se ausente)
set "PYTHON="
if exist "%ROOT%\.venv\Scripts\python.exe" set "PYTHON=%ROOT%\.venv\Scripts\python.exe"

if not defined PYTHON (
  py -3 --version >nul 2>&1 && set "PYTHON=py -3"
)
if not defined PYTHON (
  python --version >nul 2>&1 && set "PYTHON=python"
)
if not defined PYTHON (
  echo [AVISO] Python nao encontrado no PATH e sem .venv. O Backend pode nao iniciar.
  echo        Execute scripts\instalar_dependencias.bat para configurar o ambiente.
)

:: =====================
:: Serviços auxiliares (abrem em janelas separadas)
:: =====================

:: 1) Rust Images (8081)
echo.
echo([1/4] Rust Images (8081)
if exist "%ROOT%\services\rust_images\Cargo.toml" (
  cargo --version >nul 2>&1
  if errorlevel 1 (
    echo  - [AVISO] Cargo nao encontrado. Pulando Rust.
  ) else (
    echo  - Abrindo janela: Rust Images
    echo  - Pasta: "%ROOT%\services\rust_images"
  echo  - Encerrando instancia anterior - se existir...
  for /f "tokens=*" %%A in ('tasklist ^| findstr /I "rust_images.exe"') do set "_FOUND_RUST=1"
  if defined _FOUND_RUST (
      taskkill /IM rust_images.exe /F >nul 2>&1
      timeout /t 1 /nobreak >nul
    )
  set "_FOUND_RUST="
    if exist "%ROOT%\services\rust_images\target\release\rust_images.exe" (
      del /f /q "%ROOT%\services\rust_images\target\release\rust_images.exe" >nul 2>&1
    )
  start "Rust Images - 8081" /D "%ROOT%\services\rust_images" cmd /k "set RUST_IMAGES_ADDR=127.0.0.1:8081 && echo Iniciando Rust Images... && cargo run --release || (echo [ERRO] Rust Images saiu com %%ERRORLEVEL%% & echo. & pause)"
  )
) else (
  echo  - [INFO] Servico Rust nao encontrado. Pulando.
)
rem Aguarde um pouco entre janelas
timeout /t 1 /nobreak >nul

:: 2) Kotlin Utils (8084)
echo.
echo([2/4] Kotlin Utils (8084)
if exist "%ROOT%\services\kotlin_utils\build.gradle.kts" (
  java -version >nul 2>&1
  if errorlevel 1 (
    echo  - [AVISO] Java (JDK) nao encontrado. Pulando Kotlin.
  ) else (
    set "KOTLIN_DIR=%ROOT%\services\kotlin_utils"
    if exist "%KOTLIN_DIR%\gradlew.bat" (
      echo  - Abrindo janela: Kotlin Utils
      echo  - Pasta: "%KOTLIN_DIR%"
  start "Kotlin Utils - 8084" /D "%KOTLIN_DIR%" cmd /k "set KOTLIN_UTILS_HOST=0.0.0.0 && set KOTLIN_UTILS_PORT=8084 && echo Iniciando Kotlin Utils... && gradlew.bat run || (echo [ERRO] Kotlin Utils saiu com %%ERRORLEVEL%% & echo. & pause)"
    ) else (
      echo  - [AVISO] gradlew.bat nao encontrado em "%KOTLIN_DIR%". Pulando Kotlin.
    )
  )
) else (
  echo  - [INFO] Servico Kotlin nao encontrado. Pulando.
)
rem Aguarde um pouco entre janelas
timeout /t 1 /nobreak >nul

:: 3) Julia Analytics (8082)
echo.
echo([3/4] Julia Analytics (8082)
if exist "%ROOT%\services\julia_analytics\src\server.jl" (
  julia --version >nul 2>&1
  if errorlevel 1 (
    echo  - [AVISO] Julia nao encontrada. Pulando Julia.
  ) else (
    echo  - Abrindo janela: Julia Analytics
    echo  - Pasta: "%ROOT%\services\julia_analytics"
  start "Julia Analytics - 8082" /D "%ROOT%\services\julia_analytics" cmd /k "set JULIA_ANALYTICS_ADDR=127.0.0.1:8082 && echo Iniciando Julia Analytics... && julia --project=. src\server.jl || (echo [ERRO] Julia Analytics saiu com %%ERRORLEVEL%% & echo. & pause)"
  )
) else (
  echo  - [INFO] Servico Julia nao encontrado. Pulando.
)
rem Aguarde um pouco entre janelas
timeout /t 1 /nobreak >nul

:: =====================
:: Backend principal (5001)
:: =====================
echo.
echo([4/4] Backend Principal (5001)
set "ENTRY=server_form.py"
if not exist "%ROOT%\server_form.py" if exist "%ROOT%\server.py" set "ENTRY=server.py"

set "RUST_IMAGES_URL=http://127.0.0.1:8081"
set "KOTLIN_UTILS_URL=http://127.0.0.1:8084"
set "JULIA_ANALYTICS_URL=http://127.0.0.1:8082"
set "IPPEL_BACKUP_DIR=G:\My Drive\BACKUP BANCO DE DADOS IPPEL"

echo  - Abrindo janela: Backend IPPEL
echo  - Pasta: "%ROOT%"
echo  - Backup dir: "%IPPEL_BACKUP_DIR%"
start "IPPEL Backend (5001)" /D "%ROOT%" cmd /k "set RUST_IMAGES_URL=%RUST_IMAGES_URL% && set KOTLIN_UTILS_URL=%KOTLIN_UTILS_URL% && set JULIA_ANALYTICS_URL=%JULIA_ANALYTICS_URL% && set IPPEL_BACKUP_DIR=%IPPEL_BACKUP_DIR% && chcp 65001>nul && echo Iniciando Backend Principal... && echo Usando Python: %PYTHON% && echo Entry: %ENTRY% && echo IPPEL_BACKUP_DIR=%%IPPEL_BACKUP_DIR%% && ( \"%PYTHON%\" %ENTRY% || ( echo [FALLBACK] Tentando com 'py -3' & py -3 %ENTRY% ) )"
start "IPPEL Backend - 5001" /D "%ROOT%" cmd /k "set RUST_IMAGES_URL=%RUST_IMAGES_URL% && set KOTLIN_UTILS_URL=%KOTLIN_UTILS_URL% && set JULIA_ANALYTICS_URL=%JULIA_ANALYTICS_URL% && set IPPEL_BACKUP_DIR=%IPPEL_BACKUP_DIR% && chcp 65001>nul && echo Iniciando Backend Principal... && echo Usando Python: %PYTHON% && echo Entry: %ENTRY% && echo IPPEL_BACKUP_DIR=%%IPPEL_BACKUP_DIR%% && if exist "%ROOT%\.venv\Scripts\python.exe" ( call "%ROOT%\.venv\Scripts\python.exe" %ENTRY% ) else ( call py -3 %ENTRY% ) || (echo [ERRO] Backend saiu com %%ERRORLEVEL%% & echo. & pause)"

:: =====================
:: Pós-start
:: =====================
echo.
echo Aguardando backend (porta 5001) ficar disponivel para abrir o navegador...
set _wait=0
for /L %%I in (1,1,20) do (
  >nul 2>&1 (curl -s -o NUL -m 1 http://127.0.0.1:5001/) && set _wait=1 && goto :OPEN_BROWSER
  timeout /t 1 /nobreak >nul
)
:OPEN_BROWSER
if "%_wait%"=="1" (
  start http://localhost:5001/
) else (
  echo [AVISO] Nao consegui confirmar o backend em 20s; abra manualmente: http://localhost:5001/
)

echo.
echo ========================================
echo  TODOS OS SERVICOS FORAM INICIADOS
echo ========================================
echo URLs auxiliares (se ativos):
echo   Rust Images:   %RUST_IMAGES_URL%/health
echo   Kotlin Utils:  %KOTLIN_UTILS_URL%/health
echo   Julia:         %JULIA_ANALYTICS_URL%/health

echo.
echo Cada servico abriu em sua propria janela.
echo Use Ctrl+C em cada janela para encerrar.

echo.
pause
exit /b 0

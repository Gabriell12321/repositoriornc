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
echo [1/4] Rust Images (8081)
echo  - Abrindo janela: Rust Images
start "Rust Images - 8081" /D "%ROOT%" cmd /k "chcp 65001>nul && scripts\start_rust_images.bat"
timeout /t 1 /nobreak >nul

:: 2) Kotlin Utils (8084)
echo.
echo [2/4] Kotlin Utils (8084)
echo  - Abrindo janela: Kotlin Utils
start "Kotlin Utils - 8084" /D "%ROOT%" cmd /k "chcp 65001>nul && scripts\start_kotlin_utils.bat"
rem Aguarde um pouco entre janelas
timeout /t 1 /nobreak >nul

:: 3) Julia Analytics (8082)
echo.
echo [3/4] Julia Analytics (8082)
echo  - Abrindo janela: Julia Analytics
start "Julia Analytics - 8082" /D "%ROOT%" cmd /k "chcp 65001>nul && scripts\start_julia_analytics.bat"
rem Aguarde um pouco entre janelas
timeout /t 1 /nobreak >nul
:: (subrotinas removidas; agora cada servico possui seu .bat dedicado)

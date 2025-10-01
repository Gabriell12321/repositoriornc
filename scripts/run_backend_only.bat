@echo off
chcp 65001>nul
title IPPEL Backend - Somente Backend (5001)
setlocal EnableExtensions EnableDelayedExpansion

for %%I in ("%~dp0..") do set "ROOT=%%~fI"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
pushd "%ROOT%" >nul 2>&1 || ( echo [ERRO] Nao consegui acessar a raiz: "%ROOT%" & pause & exit /b 1 )

set "RUST_IMAGES_URL=http://127.0.0.1:8081"
set "KOTLIN_UTILS_URL=http://127.0.0.1:8084"
set "JULIA_ANALYTICS_URL=http://127.0.0.1:8082"
set "IPPEL_BACKUP_DIR=G:\My Drive\BACKUP BANCO DE DADOS IPPEL"

echo ========================================
echo Iniciando Backend (server_form.py)
echo Raiz: %ROOT%
echo RUST_IMAGES_URL=%RUST_IMAGES_URL%
echo KOTLIN_UTILS_URL=%KOTLIN_UTILS_URL%
echo JULIA_ANALYTICS_URL=%JULIA_ANALYTICS_URL%
echo IPPEL_BACKUP_DIR=%IPPEL_BACKUP_DIR%
echo ========================================

set "PYTHON=%ROOT%\.venv\Scripts\python.exe"
if not exist "%PYTHON%" set "PYTHON=py -3"

echo Usando Python: %PYTHON%
echo.

if exist "%ROOT%\.venv\Scripts\python.exe" (
  call "%ROOT%\.venv\Scripts\python.exe" server_form.py
) else (
  call py -3 server_form.py
)

echo.
echo (Janela permanecerá aberta para visualizar erros)
pause
exit /b 0

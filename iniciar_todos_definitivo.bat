@echo off
chcp 65001 >nul
echo Abrindo scripts\iniciar_todos_definitivo.bat a partir da raiz...
set "HERE=%~dp0"
pushd "%HERE%" >nul 2>&1
if not exist "%HERE%scripts\iniciar_todos_definitivo.bat" (
  echo [ERRO] Nao encontrei scripts\iniciar_todos_definitivo.bat
  pause
  exit /b 1
)
call "%HERE%scripts\iniciar_todos_definitivo.bat"
pause
exit /b 0

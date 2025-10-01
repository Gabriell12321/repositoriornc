@echo off
chcp 65001 >nul
setlocal EnableExtensions

REM Localiza o iniciar_todos.bat dentro de scripts
set "ROOT=%~dp0"
set "LAUNCH=%ROOT%scripts\iniciar_todos.bat"

if not exist "%LAUNCH%" (
  echo [ERRO] Nao encontrei: %LAUNCH%
  echo Certifique-se de que esta pasta contem a subpasta "scripts" com o arquivo iniciar_todos.bat
  pause
  exit /b 1
)

REM Abre uma nova janela do CMD que permanece aberta (/k)
start "Iniciar todos - IPPEL" cmd /k "\"%LAUNCH%\""

exit /b 0

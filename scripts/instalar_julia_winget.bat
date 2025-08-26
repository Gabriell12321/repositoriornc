@echo off
chcp 65001>nul
echo Instalando Julia via winget (necessita Windows 10+/11 e winget)...
winget --version >nul 2>&1 || (
  echo [ERRO] winget nao encontrado. Abra Microsoft Store e instale "App Installer".
  pause & exit /b 1
)
winget install -e --id Julialang.Julia --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
  echo [AVISO] Falha na instalacao via winget. Tente instalar manualmente: https://julialang.org/downloads/
) else (
  echo Julia instalada. Se 'julia' nao for reconhecido, reinicie o terminal para atualizar o PATH.
)
pause
exit /b 0

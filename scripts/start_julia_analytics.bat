@echo off
chcp 65001>nul
setlocal EnableExtensions
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
set "JULIA_DIR=%ROOT%\services\julia_analytics"
if not exist "%JULIA_DIR%\src\server.jl" (
  echo [INFO] Projeto Julia nao encontrado em "%JULIA_DIR%".
  pause & exit /b 0
)
set "JULIA_EXE=julia"
"%JULIA_EXE%" --version >nul 2>&1
if errorlevel 1 (
  for %%P in ("%LOCALAPPDATA%\Programs\Julia-*\bin\julia.exe" "%ProgramFiles%\Julia-*\bin\julia.exe" "%ProgramFiles(x86)%\Julia-*\bin\julia.exe") do (
    for /f "delims=" %%F in ('dir /b /s "%%~P" 2^>nul') do (
      set "JULIA_EXE=%%F"
      goto :FOUND_JULIA
    )
  )
  :FOUND_JULIA
  if not exist "%JULIA_EXE%" (
    echo [AVISO] Julia nao encontrada no PATH nem nas pastas padrao.
    echo         Instale via scripts\instalar_julia_winget.bat ou informe o caminho de julia.exe.
    pause & exit /b 1
  )
)
pushd "%JULIA_DIR%" >nul
echo Iniciando Julia Analytics na porta 8082...
set JULIA_ANALYTICS_ADDR=127.0.0.1:8082
"%JULIA_EXE%" --project=. src\server.jl
if errorlevel 1 echo [ERRO] Julia Analytics saiu com %ERRORLEVEL% & echo. & pause
popd >nul
exit /b 0

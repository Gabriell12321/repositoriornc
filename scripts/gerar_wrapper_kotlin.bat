@echo off
chcp 65001>nul
setlocal EnableExtensions
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
set "KOTLIN_DIR=%ROOT%\services\kotlin_utils"
if not exist "%KOTLIN_DIR%\build.gradle.kts" (
  echo [ERRO] Projeto Kotlin nao encontrado em "%KOTLIN_DIR%".
  pause & exit /b 1
)
where gradle >nul 2>&1 || (
  echo [ERRO] Gradle nao encontrado no PATH. Instale: https://gradle.org/install/
  pause & exit /b 1
)
pushd "%KOTLIN_DIR%" >nul
echo Executando: gradle wrapper
gradle wrapper
if errorlevel 1 (
  echo [ERRO] Falha ao gerar wrapper.
  popd >nul & pause & exit /b 1
) else (
  echo OK: gradlew.bat criado.
)
popd >nul
pause
exit /b 0

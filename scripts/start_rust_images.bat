@echo off
chcp 65001>nul
setlocal EnableExtensions
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
set "RUST_DIR=%ROOT%\services\rust_images"
if not exist "%RUST_DIR%\Cargo.toml" (
  echo [INFO] Projeto Rust nao encontrado em "%RUST_DIR%".
  pause & exit /b 0
)
pushd "%RUST_DIR%" >nul
where cargo >nul 2>&1 || ( echo [AVISO] Cargo nao encontrado no PATH. Instale Rust: https://rustup.rs/ & pause & popd & exit /b 1 )
echo Encerrando instancia anterior (se houver)...
for /f "tokens=*" %%A in ('tasklist ^| findstr /I "rust_images.exe"') do set "_FOUND_RUST=1"
if defined _FOUND_RUST (
  taskkill /IM rust_images.exe /F >nul 2>&1
  timeout /t 1 /nobreak >nul
)
set "_FOUND_RUST="
echo Iniciando Rust Images na porta 8081...
set RUST_IMAGES_ADDR=127.0.0.1:8081
cargo run --release
if errorlevel 1 echo [ERRO] Rust Images saiu com %ERRORLEVEL% & echo. & pause
popd >nul
exit /b 0

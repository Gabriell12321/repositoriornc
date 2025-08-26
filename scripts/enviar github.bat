@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion

REM Detecta a raiz do repositório com base na pasta deste script (.. de scripts)
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO=%%~fI"

pushd "%REPO%" >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Nao foi possivel acessar a pasta do repositorio:
  echo        %REPO%
  echo Verifique o caminho e tente novamente.
  pause
  exit /b 1
)

where git >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Git nao encontrado no PATH. Instale o Git e tente novamente.
  pause
  popd >nul 2>&1
  exit /b 1
)

REM Limpar locks problemáticos
if exist ".git\index.lock" (
  echo Removendo index.lock...
  del /f /q ".git\index.lock" 2>nul
)

REM Abortar operações pendentes
if exist ".git\MERGE_HEAD" git merge --abort 2>nul
if exist ".git\REVERT_HEAD" git revert --abort 2>nul
if exist ".git\CHERRY_PICK_HEAD" git cherry-pick --abort 2>nul

REM Mensagem do commit: aceita parametro ou pergunta ao usuario (com fallback padrao)
set "MSG="
if "%~1"=="" (
  set /p MSG=Digite a mensagem do commit [padrao: chore: push automatico (script enviar github)]: 
  if "!MSG!"=="" set "MSG=chore: push automatico (script enviar github)"
) else (
  set "MSG=%*"
)

REM Configs para evitar travamentos em ambientes Windows/Drive e melhorar diagnósticos
git config --local gc.auto 0 >nul 2>&1
git config --local advice.detachedHead false >nul 2>&1
git config --local rerere.enabled true >nul 2>&1
git config --local pull.rebase false >nul 2>&1
git config --local fetch.prune true >nul 2>&1
git config --local core.longpaths true >nul 2>&1
git config --local http.postBuffer 524288000 >nul 2>&1

echo === STATUS ATUAL ===
git --no-pager status -sb
echo.

echo === ADD ===
git -c core.longpaths=true add -A
if errorlevel 1 goto :fail

echo === COMMIT ===
git commit --allow-empty -m "%MSG%"
if errorlevel 1 goto :fail

REM Determina branch padrao (master/main)
for /f "tokens=*" %%B in ('git rev-parse --abbrev-ref HEAD 2^>nul') do set "CUR_BRANCH=%%B"
if "%CUR_BRANCH%"=="HEAD" set "CUR_BRANCH=master"
if "%CUR_BRANCH%"=="" set "CUR_BRANCH=master"
REM Se origin/main existe, preferir main
for /f "tokens=2" %%R in ('git ls-remote --heads origin refs/heads/main 2^>nul') do set "HAS_MAIN=%%R"
if not "%HAS_MAIN%"=="" set "CUR_BRANCH=main"

echo === PULL (autostash, sem rebase) ===
git pull --autostash origin %CUR_BRANCH%
if errorlevel 1 goto :fail

echo === PUSH ===
git push -u origin HEAD:%CUR_BRANCH%
if errorlevel 1 goto :fail

echo.
echo === LAST LOCAL ===
git --no-pager log -1 --oneline
echo.
echo === REMOTE HEAD ===
git ls-remote origin -h refs/heads/%CUR_BRANCH%
echo.
echo [OK] Concluido.
goto :end

:fail
echo.
echo [ERRO] O processo de commit/push encontrou um erro. Revise as mensagens acima.
echo Dica: se houver conflitos, resolva-os e rode novamente este script.
exit /b 1

:end
popd >nul 2>&1
exit /b 0

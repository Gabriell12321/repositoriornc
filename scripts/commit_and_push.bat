@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Detecta a raiz do repositório com base na pasta deste script (.. de scripts)
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO=%%~fI"
for %%I in ("%REPO%") do set "REPO_SF=%%~sI"
if not exist "%REPO%\.git" (
  REM tenta fallback para short path caso 8.3 esteja habilitado
  if exist "%REPO_SF%\.git" set "REPO=%REPO_SF%"
)

REM Mensagem do commit (aceita parâmetros). Padrão: "atualização julia"
if "%~1"=="" (
  set "MSG=atualização julia"
)
if not "%~1"=="" (
  set "MSG=%*"
)

set "LOG=%REPO%\logs\git_push_msg.log"

REM Garante que a pasta de logs exista
if not exist "%REPO%\logs" (
  mkdir "%REPO%\logs" 2>nul
)

echo ==== COMMIT+PUSH %DATE% %TIME% ==== > "%LOG%"
echo repo: %REPO% >> "%LOG%"
echo message: %MSG% >> "%LOG%"
where git >> "%LOG%" 2>>&1
git --version >> "%LOG%" 2>>&1

pushd "%REPO%" >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Nao foi possivel acessar "%REPO%" >> "%LOG%"
  echo DONE >> "%LOG%"
  exit /b 1
)

echo ---- CWD ---- >> "%LOG%"
cd >> "%LOG%"
echo ---- GIT DIR CHECK ---- >> "%LOG%"
if exist ".git" (echo .git FOUND >> "%LOG%") else (echo .git NOT FOUND >> "%LOG%")

echo ---- STATUS BEFORE ---- >> "%LOG%"
git --no-pager status -sb >> "%LOG%" 2>>&1

echo ---- ADD ---- >> "%LOG%"
git -c core.longpaths=true add -A >> "%LOG%" 2>>&1

echo ---- COMMIT ---- >> "%LOG%"
git commit --allow-empty -m "%MSG%" >> "%LOG%" 2>>&1

echo ---- PULL (rebase/autostash) ---- >> "%LOG%"
git pull --rebase --autostash origin master >> "%LOG%" 2>>&1

echo ---- PUSH ---- >> "%LOG%"
git push origin HEAD:master >> "%LOG%" 2>>&1

echo ---- LAST LOCAL ---- >> "%LOG%"
git --no-pager log -1 --oneline >> "%LOG%" 2>>&1

echo ---- REMOTE HEAD ---- >> "%LOG%"
git ls-remote origin -h refs/heads/master >> "%LOG%" 2>>&1

popd >nul 2>&1
echo DONE >> "%LOG%"
exit /b 0

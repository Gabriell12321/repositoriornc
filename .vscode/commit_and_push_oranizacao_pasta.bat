@echo off
setlocal enabledelayedexpansion

rem Repo absolute path (quotes not needed for -C as we pass quoted when used)
set "REPO=g:\My Drive\Trabalhos pendentes\rncs\RELATORIO DE NÃO CONFORMIDADE IPPEL"
set "LOG=%REPO%\logs\git_push_oranizacao.log"
if not exist "%REPO%\logs" mkdir "%REPO%\logs" >nul 2>&1

echo ==== GIT COMMIT/PUSH (oranização de pasta) %DATE% %TIME% ==== > "%LOG%"
echo repo: %REPO%>> "%LOG%"

where git >> "%LOG%" 2>>&1
git --version >> "%LOG%" 2>>&1

if not exist "%REPO%\.git" (
  echo ERROR: Not a git repository: %REPO% >> "%LOG%"
  echo Not a git repository. See %LOG%
  exit /b 1
)

rem Ensure remote origin exists; if missing, set to the provided GitHub URL
git -C "%REPO%" remote get-url origin >nul 2>&1
if errorlevel 1 (
  git -C "%REPO%" remote add origin https://github.com/Gabriell12321/repositoriornc >> "%LOG%" 2>>&1
)
git -C "%REPO%" remote -v >> "%LOG%" 2>>&1

rem Show short status and branch
git -C "%REPO%" status -sb >> "%LOG%" 2>>&1
for /f "usebackq delims=" %%B in (`git -C "%REPO%" rev-parse --abbrev-ref HEAD 2^>^&1`) do set "BRANCH=%%B"
if "%BRANCH%"=="HEAD" set "BRANCH=master"
echo branch: %BRANCH%>> "%LOG%"

rem Stage and commit with the exact message if there are changes
git -C "%REPO%" add -A >> "%LOG%" 2>>&1
git -C "%REPO%" diff --cached --quiet
if errorlevel 1 (
  git -C "%REPO%" commit -m "oranização de pasta" >> "%LOG%" 2>>&1
) else (
  echo no staged changes to commit >> "%LOG%"
)

rem Pull rebase and push
git -C "%REPO%" fetch --all --tags >> "%LOG%" 2>>&1
git -C "%REPO%" pull --rebase --autostash origin %BRANCH% >> "%LOG%" 2>>&1
git -C "%REPO%" push origin HEAD:%BRANCH% >> "%LOG%" 2>>&1
set PUSH_RC=%ERRORLEVEL%

if not "%PUSH_RC%"=="0" (
  echo Push failed with code %PUSH_RC% >> "%LOG%"
  echo Push failed. See log: %LOG%
  exit /b %PUSH_RC%
)

echo DONE >> "%LOG%"
echo Commit and push completed. Log: %LOG%
exit /b 0


@echo off
setlocal enabledelayedexpansion

REM Detect repo root from this script folder (.. from scripts)
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO=%%~fI"
for %%I in ("%REPO%") do set "REPO_SF=%%~sI"
if not exist "%REPO%\.git" (
	if exist "%REPO_SF%\.git" set "REPO=%REPO_SF%"
)
set "LOG=%REPO%\logs\git_push_descriptive.log"

REM Descriptive commit message (no 'linguagens pronta')
set "MSG=feat(services): integrações multi-idioma + robustez em Julia analytics e groups (validações, cache TTL, testes)"

echo ==== COMMIT+PUSH (descriptive) %DATE% %TIME% ==== > "%LOG%"
echo repo: %REPO% >> "%LOG%"
where git >> "%LOG%" 2>>&1
git --version >> "%LOG%" 2>>&1

pushd "%REPO%" >nul 2>&1
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

echo ---- PUSH ---- >> "%LOG%"
git push -v origin HEAD:master >> "%LOG%" 2>>&1

echo ---- LAST LOCAL ---- >> "%LOG%"
git --no-pager log -1 --oneline >> "%LOG%" 2>>&1

echo ---- REMOTE HEAD ---- >> "%LOG%"
git ls-remote origin -h refs/heads/master >> "%LOG%" 2>>&1

popd >nul 2>&1
echo DONE >> "%LOG%"
exit /b 0

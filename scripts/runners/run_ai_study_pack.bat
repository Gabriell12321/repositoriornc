@echo off
setlocal enabledelayedexpansion

REM Resolve workspace root as two levels up from this script (scripts\runners\..\..)
set "ROOT=%~dp0..\.."
pushd "%ROOT%" >NUL 2>&1

if exist ".venv\Scripts\python.exe" (
    echo Using venv Python: .venv\Scripts\python.exe
    ".venv\Scripts\python.exe" "scripts\generate_ai_study_pack.py"
) else (
    echo Using system Python: python
    python "scripts\generate_ai_study_pack.py"
)
set ERR=%ERRORLEVEL%

popd >NUL 2>&1
exit /b %ERR%

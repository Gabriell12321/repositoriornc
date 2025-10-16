@echo off
setlocal enabledelayedexpansion
set REPO="g:\My Drive\Trabalhos pendentes\rncs\RELATORIO DE NÃO CONFORMIDADE IPPEL"
set LOG=logs\git_push.log

echo ==== GIT PUSH (no commit) %DATE% %TIME% ==== > %LOG%
echo repo: %REPO% >> %LOG%
where git >> %LOG% 2>>&1
git --version >> %LOG% 2>>&1
git -C %REPO% remote -v >> %LOG% 2>>&1
git -C %REPO% status -sb >> %LOG% 2>>&1
git -C %REPO% fetch --all --tags >> %LOG% 2>>&1
git -C %REPO% pull --rebase --autostash origin master >> %LOG% 2>>&1
git -C %REPO% push origin HEAD:master >> %LOG% 2>>&1
git -C %REPO% tag -f versao-funcionando >> %LOG% 2>>&1
git -C %REPO% push -f origin versao-funcionando >> %LOG% 2>>&1
echo DONE >> %LOG%
exit /b 0

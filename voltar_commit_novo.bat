@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
echo ========================================
echo    VOLTAR PARA UM COMMIT ANTERIOR
echo ========================================
echo.

:: Verificar se estamos em um repositório Git
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo ERRO: Este diretório não é um repositório Git!
    echo Certifique-se de estar na pasta do projeto.
    pause
    exit /b 1
)

echo Buscando commits do repositório...
echo.

:: Mostrar os últimos 20 commits
echo ========================================
echo           COMMITS DISPONÍVEIS
echo ========================================

:: Criar lista de commits e hashes
git --no-pager log --oneline --decorate -20 > commits_temp.txt

:: Mostrar commits numerados e salvar hashes
set counter=1
del hashes_temp.txt 2>nul
for /f "tokens=1,* delims= " %%a in (commits_temp.txt) do (
    echo !counter!. %%a %%b
    echo %%a >> hashes_temp.txt
    set /a counter+=1
)

echo.
echo ========================================

:ask_choice
:: Pedir para escolher o commit
set /p escolha="Digite o número do commit para voltar (1-%counter%, ou 'q' para sair): "

if /i "!escolha!"=="q" (
    echo Operação cancelada.
    goto :cleanup
)

:: Verificar se é número
set "num_check=!escolha!"
set "is_num=1"
for /f "delims=0123456789" %%i in ("!num_check!") do set "is_num=0"
if "!is_num!"=="0" (
    echo ERRO: Digite apenas números!
    echo.
    goto :ask_choice
)

:: Verificar range
if !escolha! LSS 1 (
    echo ERRO: Digite um número maior que 0!
    echo.
    goto :ask_choice
)

set /a max_num=!counter!-1
if !escolha! GTR !max_num! (
    echo ERRO: Digite um número entre 1 e !max_num!!
    echo.
    goto :ask_choice
)

:: Obter o hash do commit escolhido
set line_count=1
for /f "tokens=*" %%a in (hashes_temp.txt) do (
    if !line_count! equ !escolha! (
        set commit_hash=%%a
        goto :found_hash
    )
    set /a line_count+=1
)

:found_hash
if "!commit_hash!"=="" (
    echo ERRO: Não foi possível encontrar o commit!
    goto :cleanup
)

echo.
echo ========================================
echo Commit selecionado: !commit_hash!
echo ========================================

:: Mostrar detalhes do commit
echo Detalhes do commit:
git --no-pager show --stat !commit_hash!
echo.

:: Confirmar a operação
echo ATENÇÃO: Esta operação irá:
echo 1. Resetar o repositório para o commit !commit_hash!
echo 2. Forçar o push para o GitHub (REESCREVE O HISTÓRICO!)
echo 3. Todos os commits posteriores serão PERDIDOS!
echo.

:ask_confirm
set /p confirma="Tem certeza que deseja continuar? (SIM/nao): "
if /i "!confirma!"=="SIM" goto :do_reset
if /i "!confirma!"=="sim" goto :do_reset
if /i "!confirma!"=="s" goto :do_reset
if /i "!confirma!"=="" goto :ask_confirm
if /i "!confirma!"=="nao" goto :cleanup
if /i "!confirma!"=="n" goto :cleanup
echo Digite 'SIM' para confirmar ou 'nao' para cancelar.
goto :ask_confirm

:do_reset
echo.
echo ========================================
echo       EXECUTANDO RESET...
echo ========================================

:: Limpar locks se existirem
if exist ".git\index.lock" (
    echo Removendo lock file...
    del /f /q ".git\index.lock" 2>nul
)

:: Fazer backup do branch atual
echo Criando backup do estado atual...
git branch backup-antes-reset-!commit_hash! 2>nul

:: Resetar para o commit escolhido
echo Resetando para o commit !commit_hash!...
git reset --hard !commit_hash!

if errorlevel 1 (
    echo ERRO: Falha ao resetar para o commit!
    goto :cleanup
)

echo Reset local concluído com sucesso!
echo.

:: Confirmar push forçado
echo ========================================
echo       PUSH FORÇADO PARA GITHUB
echo ========================================
echo.
echo Agora será feito o push forçado para o GitHub.
echo Isso irá SOBRESCREVER o histórico remoto!
echo.

:ask_push
set /p push_confirma="Confirma o push forçado? (SIM/nao): "
if /i "!push_confirma!"=="SIM" goto :do_push
if /i "!push_confirma!"=="sim" goto :do_push
if /i "!push_confirma!"=="s" goto :do_push
if /i "!push_confirma!"=="" goto :ask_push
if /i "!push_confirma!"=="nao" goto :push_cancelled
if /i "!push_confirma!"=="n" goto :push_cancelled
echo Digite 'SIM' para confirmar ou 'nao' para cancelar.
goto :ask_push

:do_push
:: Fazer push forçado
echo Fazendo push forçado para origin...
git push origin HEAD --force

if errorlevel 1 (
    echo ERRO: Falha no push forçado!
    echo O reset local foi mantido.
    echo Para desfazer, use: git reset --hard backup-antes-reset-!commit_hash!
    goto :cleanup
)

echo.
echo ========================================
echo           SUCESSO!
echo ========================================
echo.
echo O repositório foi resetado com sucesso para:
git --no-pager log -1 --oneline
echo.
echo O backup do estado anterior foi salvo em: backup-antes-reset-!commit_hash!
echo Para voltar ao estado anterior (se necessário):
echo git reset --hard backup-antes-reset-!commit_hash!
echo.
goto :cleanup

:push_cancelled
echo Push cancelado. O reset local foi mantido.
echo Para desfazer o reset local, use: git reset --hard backup-antes-reset-!commit_hash!
goto :cleanup

:cleanup
:: Limpar arquivos temporários
if exist commits_temp.txt del commits_temp.txt 2>nul
if exist hashes_temp.txt del hashes_temp.txt 2>nul

echo.
pause
exit /b 0

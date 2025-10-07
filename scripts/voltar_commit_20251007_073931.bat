@echo off
chcp 65001 >nul
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

:: Mostrar os últimos 20 commits com numeração
echo ========================================
echo           COMMITS DISPONÍVEIS
echo ========================================
git --no-pager log --oneline --decorate -20 > temp_commits.txt

:: Criar arquivo numerado
set /a counter=1
echo. > commits_numerados.txt
for /f "delims=" %%i in (temp_commits.txt) do (
    echo !counter!. %%i >> commits_numerados.txt
    set /a counter+=1
)

:: Mostrar commits numerados
type commits_numerados.txt
echo.
echo ========================================

:: Pedir para escolher o commit
set /p escolha="Digite o número do commit para voltar (ou 'q' para sair): "

if /i "%escolha%"=="q" (
    echo Operação cancelada.
    goto :cleanup
)

:: Validar se é um número
echo %escolha%| findstr /r "^[1-9][0-9]*$" >nul
if errorlevel 1 (
    echo ERRO: Digite um número válido!
    goto :cleanup
)

:: Verificar se o número está no range
if %escolha% gtr 20 (
    echo ERRO: Número muito alto! Escolha entre 1 e 20.
    goto :cleanup
)

:: Extrair o hash do commit escolhido
set /a linha=%escolha%
set counter=1
for /f "tokens=2 delims=. " %%i in (commits_numerados.txt) do (
    if !counter! equ %linha% (
        set commit_hash=%%i
        goto :found
    )
    set /a counter+=1
)

:found
if "%commit_hash%"=="" (
    echo ERRO: Não foi possível encontrar o commit!
    goto :cleanup
)

echo.
echo ========================================
echo Commit selecionado: %commit_hash%
echo ========================================

:: Mostrar detalhes do commit
echo Detalhes do commit:
git --no-pager show --stat %commit_hash%
echo.

:: Confirmar a operação
echo ATENÇÃO: Esta operação irá:
echo 1. Resetar o repositório para o commit %commit_hash%
echo 2. Forçar o push para o GitHub (REESCREVE O HISTÓRICO!)
echo 3. Todos os commits posteriores serão PERDIDOS!
echo.
set /p confirma="Tem certeza que deseja continuar? (digite 'SIM' para confirmar): "

if /i not "%confirma%"=="SIM" (
    echo Operação cancelada por segurança.
    goto :cleanup
)

echo.
echo ========================================
echo       EXECUTANDO RESET...
echo ========================================

:: Fazer backup do branch atual
echo Criando backup do estado atual...
git branch backup-antes-reset 2>nul

:: Resetar para o commit escolhido
echo Resetando para o commit %commit_hash%...
git reset --hard %commit_hash%

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
set /p push_confirma="Confirma o push forçado? (digite 'SIM' para confirmar): "

if /i not "%push_confirma%"=="SIM" (
    echo Push cancelado. O reset local foi mantido.
    echo Para desfazer o reset local, use: git reset --hard backup-antes-reset
    goto :cleanup
)

:: Fazer push forçado
echo Fazendo push forçado para origin...
git push origin HEAD --force

if errorlevel 1 (
    echo ERRO: Falha no push forçado!
    echo O reset local foi mantido.
    echo Para desfazer, use: git reset --hard backup-antes-reset
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
echo O backup do estado anterior foi salvo em: backup-antes-reset
echo Para voltar ao estado anterior (se necessário):
echo git reset --hard backup-antes-reset
echo.

:cleanup
:: Limpar arquivos temporários
if exist temp_commits.txt del temp_commits.txt
if exist commits_numerados.txt del commits_numerados.txt

echo.
pause

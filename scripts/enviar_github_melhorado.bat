@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion

echo ========================================
echo    ENVIAR PARA GITHUB - VERSÃO 2.0
echo ========================================

REM Detecta a raiz do repositório
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO=%%~fI"

pushd "%REPO%" >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Não foi possível acessar a pasta do repositório:
    echo        %REPO%
    pause
    exit /b 1
)

REM Verificar se Git está instalado
where git >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Git não encontrado no PATH. Instale o Git e tente novamente.
    pause
    popd >nul 2>&1
    exit /b 1
)

REM Limpar locks e estados problemáticos
echo Verificando e limpando estados Git problemáticos...
if exist ".git\index.lock" (
    echo Removendo index.lock...
    del /f /q ".git\index.lock" 2>nul
)

if exist ".git\COMMIT_EDITMSG" (
    echo Limpando commit em andamento...
    del /f /q ".git\COMMIT_EDITMSG" 2>nul
)

if exist ".git\MERGE_HEAD" (
    echo Abortando merge em andamento...
    git merge --abort 2>nul
)

if exist ".git\REVERT_HEAD" (
    echo Abortando revert em andamento...
    git revert --abort 2>nul
)

if exist ".git\CHERRY_PICK_HEAD" (
    echo Abortando cherry-pick em andamento...
    git cherry-pick --abort 2>nul
)

REM Configurar Git para lidar com caminhos longos
git config core.longpaths true

REM Mensagem do commit
set "MSG="
if "%~1"=="" (
    set /p MSG=Digite a mensagem do commit: 
    if "!MSG!"=="" set "MSG=Atualização automática"
) else (
    set "MSG=%*"
)

echo.
echo ========================================
echo           STATUS ATUAL
echo ========================================
git --no-pager status -sb
echo.

echo ========================================
echo       ADICIONANDO ARQUIVOS
echo ========================================
git add -A
if errorlevel 1 (
    echo [ERRO] Falha ao adicionar arquivos.
    goto :fail
)

echo Arquivos adicionados com sucesso!
echo.

echo ========================================
echo         FAZENDO COMMIT
echo ========================================
git commit -m "!MSG!"
if errorlevel 1 (
    echo [AVISO] Nenhuma alteração para commit ou erro no commit.
    echo Tentando commit vazio...
    git commit --allow-empty -m "!MSG!"
    if errorlevel 1 goto :fail
)

echo Commit realizado com sucesso!
echo.

echo ========================================
echo      SINCRONIZANDO COM GITHUB
echo ========================================

REM Verificar se origin existe
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo Configurando remote origin...
    git remote add origin https://github.com/Gabriell12321/repositoriornc.git
    if errorlevel 1 (
        echo [ERRO] Falha ao adicionar remote origin.
        goto :fail
    )
)

echo Fazendo pull para sincronizar...
git pull --rebase --autostash origin master
if errorlevel 1 (
    echo [AVISO] Problemas no pull. Tentando push direto...
)

echo Enviando para GitHub...
git push -u origin HEAD:master
if errorlevel 1 (
    echo Tentando push forçado...
    git push -u origin HEAD:master --force
    if errorlevel 1 goto :fail
)

echo.
echo ========================================
echo            SUCESSO!
echo ========================================
echo.
echo Último commit local:
git --no-pager log -1 --oneline
echo.
echo Status do remote:
git ls-remote origin -h refs/heads/master 2>nul
echo.
echo [✓] Envio para GitHub concluído com sucesso!

goto :end

:fail
echo.
echo ========================================
echo            ERRO!
echo ========================================
echo.
echo [✗] O processo encontrou um erro.
echo.
echo Possíveis soluções:
echo 1. Verifique sua conexão com a internet
echo 2. Confirme suas credenciais do GitHub
echo 3. Verifique se o repositório remoto existe
echo 4. Execute novamente o script
echo.
pause
popd >nul 2>&1
exit /b 1

:end
echo.
echo Pressione qualquer tecla para continuar...
pause >nul
popd >nul 2>&1
exit /b 0

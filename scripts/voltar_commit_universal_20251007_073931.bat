@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion
title Voltar Commit Universal
echo ========================================
echo   VOLTAR COMMIT E ENVIAR - UNIVERSAL
echo ========================================
echo.
echo Este script funciona para qualquer projeto Git!
echo.
echo Pressione CTRL+C para sair a qualquer momento.
echo.

:: Verificar se estamos em um repositório Git
echo Verificando se este diretorio e um repositorio Git...
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo        REPOSITORIO NAO ENCONTRADO
    echo ========================================
    echo.
    echo ERRO: Este diretorio nao e um repositorio Git!
    echo.
    echo Pasta atual: %CD%
    echo.
    echo Deseja inicializar um repositorio Git aqui? 
    set /p init_git="Digite 's' para SIM ou 'n' para NAO: "
    if /i "!init_git!"=="s" (
        echo.
        echo Inicializando repositorio Git...
        git init
        if errorlevel 1 (
            echo ERRO: Falha ao inicializar Git!
            echo Verifique se o Git esta instalado.
            pause
            exit /b 1
        )
        echo Repositorio Git inicializado com sucesso!
        echo.
    ) else (
        echo.
        echo Operacao cancelada.
        echo Certifique-se de estar na pasta do projeto com Git.
        echo.
        pause
        exit /b 1
    )
)

:: Verificar se existe remote origin
echo Verificando remote origin...
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo    CONFIGURAR REPOSITORIO REMOTO
    echo ========================================
    echo.
    echo Nao foi encontrado um remote 'origin' configurado.
    echo.
    echo Exemplos de URLs:
    echo - https://github.com/usuario/repositorio.git
    echo - https://gitlab.com/usuario/repositorio.git
    echo - https://bitbucket.org/usuario/repositorio.git
    echo.
    set /p repo_url="Cole a URL do repositorio remoto: "
    
    if "!repo_url!"=="" (
        echo.
        echo ERRO: URL nao pode estar vazia!
        echo.
        pause
        exit /b 1
    )
    
    echo.
    echo Configurando remote origin...
    git remote add origin "!repo_url!"
    if errorlevel 1 (
        echo ERRO: Falha ao configurar remote!
        echo Verifique se a URL esta correta.
        echo.
        pause
        exit /b 1
    )
    echo Remote configurado com sucesso!
    echo.
) else (
    echo.
    echo Remote atual:
    git remote get-url origin
    echo.
    set /p change_remote="Deseja alterar o remote? (s/n): "
    if /i "!change_remote!"=="s" (
        set /p new_repo_url="Nova URL do repositorio: "
        if not "!new_repo_url!"=="" (
            git remote set-url origin "!new_repo_url!"
            echo Remote atualizado!
            echo.
        )
    )
)

:: Verificar branch padrão
echo Verificando branch padrão...
git branch -r | findstr "origin/main" >nul
if not errorlevel 1 (
    set default_branch=main
) else (
    git branch -r | findstr "origin/master" >nul
    if not errorlevel 1 (
        set default_branch=master
    ) else (
        set /p default_branch="Digite o nome do branch padrão (main/master): "
        if "!default_branch!"=="" set default_branch=main
    )
)

echo Branch padrão detectado: !default_branch!
echo.

echo Buscando commits do repositorio...
echo.

:: Mostrar os últimos 30 commits com numeração
echo ========================================
echo           COMMITS DISPONIVEIS
echo ========================================

:: Buscar commits
echo Carregando lista de commits...
git --no-pager log --oneline --decorate -30 > commits_temp.txt 2>&1
if errorlevel 1 (
    echo.
    echo ERRO: Nao foi possivel buscar commits.
    echo.
    echo Verificando se ha commits no repositorio...
    git log --oneline -1 >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ERRO: Repositorio nao possui commits!
        echo Faca pelo menos um commit antes de usar este script.
        echo.
        echo Exemplo:
        echo   git add .
        echo   git commit -m "Primeiro commit"
        echo.
        pause
        exit /b 1
    ) else (
        echo Problema inesperado ao buscar commits.
        type commits_temp.txt
        echo.
        pause
        exit /b 1
    )
)

:: Verificar se o arquivo de commits tem conteúdo
if not exist commits_temp.txt (
    echo ERRO: Arquivo de commits nao criado!
    pause
    exit /b 1
)

:: Contar linhas do arquivo
set commit_count=0
for /f %%i in ('type commits_temp.txt ^| find /c /v ""') do set commit_count=%%i

if !commit_count! equ 0 (
    echo.
    echo ERRO: Nenhum commit encontrado no repositorio!
    echo.
    pause
    exit /b 1
)

:: Mostrar commits numerados
set counter=1
del hashes_temp.txt 2>nul
for /f "tokens=1,* delims= " %%a in (commits_temp.txt) do (
    echo !counter!. %%a %%b
    echo %%a >> hashes_temp.txt
    set /a counter+=1
)

if !counter! equ 1 (
    echo Nenhum commit encontrado!
    goto :cleanup
)

echo.
echo ========================================

:ask_choice
:: Pedir para escolher o commit
set /a max_num=!counter!-1
set /p escolha="Digite o número do commit para voltar (1-!max_num!, ou 'q' para sair): "

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
git --no-pager show --stat !commit_hash! 2>nul
echo.

:: Confirmar a operação
echo ⚠️  ATENÇÃO: Esta operação irá:
echo 1. Resetar o repositório para o commit !commit_hash!
echo 2. Forçar o push para o repositório remoto
echo 3. REESCREVER O HISTÓRICO! Todos os commits posteriores serão PERDIDOS!
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
for /f %%i in ('git rev-parse --abbrev-ref HEAD 2^>nul') do set current_branch=%%i
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
echo       PUSH FORÇADO PARA REPOSITÓRIO
echo ========================================
echo.
echo Repositório remoto: 
git remote get-url origin
echo Branch alvo: !default_branch!
echo.
echo Agora será feito o push forçado para o repositório remoto.
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
echo Fazendo push forçado para origin/!default_branch!...
git push origin HEAD:!default_branch! --force

if errorlevel 1 (
    echo ERRO: Falha no push forçado!
    echo.
    echo Possíveis causas:
    echo - Problemas de autenticação
    echo - Repositório remoto não existe
    echo - Sem permissão para push forçado
    echo.
    echo O reset local foi mantido.
    echo Para desfazer: git reset --hard backup-antes-reset-!commit_hash!
    goto :cleanup
)

echo.
echo ========================================
echo           ✅ SUCESSO!
echo ========================================
echo.
echo O repositório foi resetado e enviado com sucesso para:
git remote get-url origin
echo.
echo Commit atual:
git --no-pager log -1 --oneline
echo.
echo 📦 Backup criado: backup-antes-reset-!commit_hash!
echo 🔄 Para desfazer: git reset --hard backup-antes-reset-!commit_hash!
echo.
goto :cleanup

:push_cancelled
echo Push cancelado. O reset local foi mantido.
echo Para desfazer o reset: git reset --hard backup-antes-reset-!commit_hash!
goto :cleanup

:cleanup
:: Limpar arquivos temporários
if exist commits_temp.txt del commits_temp.txt 2>nul
if exist hashes_temp.txt del hashes_temp.txt 2>nul

echo.
echo Pressione qualquer tecla para sair...
pause >nul
exit /b 0

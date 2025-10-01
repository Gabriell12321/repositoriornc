@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
echo ========================================
echo    ENVIAR PARA GITHUB - UNIVERSAL
echo ========================================
echo.
echo Este script funciona para qualquer projeto Git!
echo.

:: Verificar se estamos em um repositório Git
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo ERRO: Este diretório não é um repositório Git!
    echo.
    set /p init_git="Deseja inicializar um repositório Git aqui? (s/n): "
    if /i "!init_git!"=="s" (
        git init
        echo Repositório Git inicializado!
        echo.
    ) else (
        echo Certifique-se de estar na pasta do projeto com Git.
        pause
        exit /b 1
    )
)

:: Verificar e configurar remote origin
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo ========================================
    echo    CONFIGURAR REPOSITÓRIO REMOTO
    echo ========================================
    echo.
    echo Não foi encontrado um remote 'origin' configurado.
    echo.
    echo 📝 Exemplos de URLs:
    echo • https://github.com/usuario/repositorio.git
    echo • https://gitlab.com/usuario/repositorio.git
    echo • https://bitbucket.org/usuario/repositorio.git
    echo.
    set /p repo_url="Cole a URL do repositório remoto: "
    
    if "!repo_url!"=="" (
        echo ERRO: URL não pode estar vazia!
        pause
        exit /b 1
    )
    
    echo Configurando remote origin...
    git remote add origin "!repo_url!"
    if errorlevel 1 (
        echo ERRO: Falha ao configurar remote!
        pause
        exit /b 1
    )
    echo ✅ Remote configurado com sucesso!
    echo.
) else (
    echo 📡 Remote atual:
    git remote get-url origin
    echo.
    set /p change_remote="Deseja alterar o remote? (s/n): "
    if /i "!change_remote!"=="s" (
        set /p new_repo_url="Nova URL do repositório: "
        if not "!new_repo_url!"=="" (
            git remote set-url origin "!new_repo_url!"
            echo ✅ Remote atualizado!
            echo.
        )
    )
)

:: Detectar branch padrão
echo 🔍 Verificando branch padrão...
git ls-remote --symref origin HEAD 2>nul | findstr "refs/heads/" >branch_temp.txt
if exist branch_temp.txt (
    for /f "tokens=2 delims=/" %%a in (branch_temp.txt) do set default_branch=%%a
    del branch_temp.txt
) else (
    :: Fallback: verificar branches remotos conhecidos
    git branch -r 2>nul | findstr "origin/main" >nul
    if not errorlevel 1 (
        set default_branch=main
    ) else (
        git branch -r 2>nul | findstr "origin/master" >nul
        if not errorlevel 1 (
            set default_branch=master
        ) else (
            set /p default_branch="Digite o nome do branch padrão (main/master): "
            if "!default_branch!"=="" set default_branch=main
        )
    )
)

echo 🌿 Branch padrão: !default_branch!
echo.

:: Limpar possíveis locks e estados problemáticos
echo 🧹 Limpando estados Git problemáticos...
if exist ".git\index.lock" (
    echo Removendo index.lock...
    del /f /q ".git\index.lock" 2>nul
)

if exist ".git\MERGE_HEAD" (
    echo Abortando merge em andamento...
    git merge --abort 2>nul
)

if exist ".git\REVERT_HEAD" (
    echo Abortando revert em andamento...
    git revert --abort 2>nul
)

:: Configurar Git para caminhos longos
git config core.longpaths true 2>nul

:: Solicitar mensagem de commit
echo ========================================
echo        MENSAGEM DO COMMIT
echo ========================================
echo.
if not "%~1"=="" (
    set "commit_msg=%*"
    echo 💬 Mensagem (via parâmetro): !commit_msg!
) else (
    set /p commit_msg="💬 Digite a mensagem do commit: "
    if "!commit_msg!"=="" set commit_msg=Atualização automática
)

echo.
echo ========================================
echo        STATUS ATUAL DO PROJETO
echo ========================================
git --no-pager status -sb
echo.

:: Verificar se há alterações para commit
git diff --cached --quiet && git diff --quiet
if not errorlevel 1 (
    echo ℹ️  Nenhuma alteração detectada.
    set /p force_commit="Deseja fazer um commit vazio? (s/n): "
    if /i not "!force_commit!"=="s" (
        echo Operação cancelada.
        goto :cleanup
    )
    set empty_commit=--allow-empty
) else (
    set empty_commit=
)

echo ========================================
echo       ADICIONANDO ARQUIVOS
echo ========================================
git add -A
if errorlevel 1 (
    echo ❌ ERRO: Falha ao adicionar arquivos.
    goto :fail
)

echo ✅ Arquivos adicionados com sucesso!
echo.

echo ========================================
echo         FAZENDO COMMIT
echo ========================================
git commit !empty_commit! -m "!commit_msg!"
if errorlevel 1 (
    echo ❌ ERRO: Falha no commit.
    goto :fail
)

echo ✅ Commit realizado com sucesso!
echo.

echo ========================================
echo    SINCRONIZANDO COM REPOSITÓRIO
echo ========================================

:: Tentar fazer pull primeiro (se o remote existir)
git ls-remote origin !default_branch! >nul 2>&1
if not errorlevel 1 (
    echo 📥 Fazendo pull para sincronizar...
    git pull --rebase --autostash origin !default_branch! 2>nul
    if errorlevel 1 (
        echo ⚠️  Conflitos detectados ou problemas no pull.
        echo Tentando push direto...
    )
)

echo 📤 Enviando para !default_branch!...
git push -u origin HEAD:!default_branch!
if errorlevel 1 (
    echo ⚠️  Push normal falhou. Tentando push forçado...
    echo.
    echo ⚠️  ATENÇÃO: Push forçado reescreve o histórico remoto!
    set /p force_push="Confirma push forçado? (s/n): "
    if /i "!force_push!"=="s" (
        git push -u origin HEAD:!default_branch! --force
        if errorlevel 1 goto :fail
    ) else (
        echo Push cancelado.
        goto :fail
    )
)

echo.
echo ========================================
echo            ✅ SUCESSO!
echo ========================================
echo.
echo 🎉 Projeto enviado com sucesso para:
git remote get-url origin
echo.
echo 📝 Último commit:
git --no-pager log -1 --oneline
echo.
echo 🌐 Branch: !default_branch!
echo 📊 Status remoto:
git ls-remote origin --heads !default_branch! 2>nul
echo.

goto :cleanup

:fail
echo.
echo ========================================
echo            ❌ ERRO!
echo ========================================
echo.
echo 🚨 O processo encontrou um erro.
echo.
echo 💡 Possíveis soluções:
echo • Verifique sua conexão com a internet
echo • Confirme suas credenciais do Git
echo • Verifique se o repositório remoto existe
echo • Certifique-se de ter permissões de escrita
echo • Execute novamente o script
echo.

:cleanup
echo.
echo Pressione qualquer tecla para continuar...
pause >nul
exit /b 0

param([
    string]$Message = "chore: sync"
)

# Non-interactive PowerShell script to stage, commit, and push changes
Write-Output "==== START $(Get-Date -Format o) ====";
Write-Output "PWD before:";
Get-Location | Out-String | Write-Output

Set-Location -LiteralPath 'G:\My Drive\Trabalhos pendentes\rncs\RELATORIO DE NÃO CONFORMIDADE IPPEL'

Write-Output "Repo path:";
Get-Location | Out-String | Write-Output

Write-Output "Staging all changes...";
git add -A

Write-Output "Committing... $Message";
git commit -m "$Message"

Write-Output "Pulling latest (rebase, autostash)...";
git pull --rebase --autostash origin master

Write-Output "Pushing HEAD to origin/master...";
git push origin HEAD:master

Write-Output "\nLast local commit:";
git --no-pager log -1 --pretty=oneline

Write-Output "\nWorking tree status:";
git --no-pager status --porcelain=v1 -uall
Write-Output "==== END $(Get-Date -Format o) ====";

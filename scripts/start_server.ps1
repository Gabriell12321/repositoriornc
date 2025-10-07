# Script para iniciar o servidor RNC
Write-Host "🚀 Iniciando Servidor RNC..." -ForegroundColor Green
Write-Host ""

try {
    # Tenta usar Python global
    python server_form.py
}
catch {
    Write-Host "❌ Erro ao iniciar servidor: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Pressione qualquer tecla para continuar..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
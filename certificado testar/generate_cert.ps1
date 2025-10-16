# Script PowerShell para gerar certificado SSL
param(
    [string]$CertDir,
    [string]$CertFile,
    [string]$CertCrt
)

try {
    Write-Host "[PS] Gerando certificado SSL autoassinado..." -ForegroundColor Cyan
    
    # Gerar certificado com IP correto
    $cert = New-SelfSignedCertificate `
        -DnsName 'rnc.ippel.com.br', 'localhost', '127.0.0.1', '172.25.100.105' `
        -CertStoreLocation 'Cert:\CurrentUser\My' `
        -KeyAlgorithm RSA `
        -KeyLength 4096 `
        -NotAfter (Get-Date).AddYears(10) `
        -FriendlyName 'RNC IPPEL SSL Certificate - Servidor 172.25.100.105'
    
    Write-Host "[PS] Certificado criado! Thumbprint: $($cert.Thumbprint)" -ForegroundColor Green
    
    # Caminho do certificado
    $certPath = "Cert:\CurrentUser\My\$($cert.Thumbprint)"
    
    # Exportar como CER
    Write-Host "[PS] Exportando certificado..." -ForegroundColor Cyan
    Export-Certificate -Cert $certPath -FilePath $CertCrt -Type CERT | Out-Null
    
    # Converter para PEM usando certutil
    Write-Host "[PS] Convertendo para PEM..." -ForegroundColor Cyan
    $result = & certutil -encode $CertCrt $CertFile 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Erro ao converter para PEM: $result"
    }
    
    Write-Host "[PS] Certificado PEM gerado: $CertFile" -ForegroundColor Green
    
    # Exportar PFX para extrair chave privada depois
    Write-Host "[PS] Exportando PFX..." -ForegroundColor Cyan
    $password = ConvertTo-SecureString -String 'temp' -Force -AsPlainText
    $pfxPath = Join-Path $CertDir "ippel_temp.pfx"
    Export-PfxCertificate -Cert $certPath -FilePath $pfxPath -Password $password | Out-Null
    
    Write-Host "[PS] Certificado exportado com sucesso!" -ForegroundColor Green
    
    exit 0
    
} catch {
    Write-Host "[PS] ERRO: $_" -ForegroundColor Red
    Write-Host "[PS] Detalhes: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

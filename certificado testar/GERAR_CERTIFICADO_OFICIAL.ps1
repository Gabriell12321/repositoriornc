# Script para gerar CERTIFICADO OFICIAL para GPO
# Este certificado será instalado em todos os PCs da rede

param(
    [string]$OutputDir = ".",
    [string]$Password = "IPPEL@2025#RNC"
)

try {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  GERANDO CERTIFICADO OFICIAL IPPEL RNC" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "[1/4] Gerando certificado SSL..." -ForegroundColor Yellow
    
    # Gerar certificado com IP correto do servidor
    $cert = New-SelfSignedCertificate `
        -DnsName 'rnc.ippel.com.br', 'localhost', '172.25.100.105' `
        -CertStoreLocation 'Cert:\CurrentUser\My' `
        -KeyAlgorithm RSA `
        -KeyLength 4096 `
        -NotAfter (Get-Date).AddYears(10) `
        -FriendlyName 'IPPEL RNC - Servidor 172.25.100.105' `
        -KeyUsage DigitalSignature, KeyEncipherment `
        -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.1")
    
    $thumbprint = $cert.Thumbprint
    Write-Host "[OK] Certificado gerado! Thumbprint: $thumbprint" -ForegroundColor Green
    
    # Caminho do certificado
    $certPath = "Cert:\CurrentUser\My\$thumbprint"
    
    Write-Host ""
    Write-Host "[2/4] Exportando certificado PFX (com senha)..." -ForegroundColor Yellow
    
    # Converter senha
    $securePassword = ConvertTo-SecureString -String $Password -Force -AsPlainText
    
    # Exportar PFX (para instalar via GPO)
    $pfxFile = Join-Path $OutputDir "IPPEL_RNC_Official.pfx"
    Export-PfxCertificate -Cert $certPath -FilePath $pfxFile -Password $securePassword | Out-Null
    Write-Host "[OK] PFX exportado: $pfxFile" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "[3/4] Exportando certificado CER (publico)..." -ForegroundColor Yellow
    
    # Exportar CER (certificado público)
    $cerFile = Join-Path $OutputDir "IPPEL_RNC_Official.cer"
    Export-Certificate -Cert $certPath -FilePath $cerFile -Type CERT | Out-Null
    Write-Host "[OK] CER exportado: $cerFile" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "[4/4] Convertendo para PEM..." -ForegroundColor Yellow
    
    # Converter para PEM (para servidor)
    $pemFile = Join-Path $OutputDir "IPPEL_RNC_Official.pem"
    & certutil -encode $cerFile $pemFile | Out-Null
    Write-Host "[OK] PEM exportado: $pemFile" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  CERTIFICADO GERADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Arquivos gerados:" -ForegroundColor Cyan
    Write-Host "  1. IPPEL_RNC_Official.pfx (para GPO)" -ForegroundColor White
    Write-Host "  2. IPPEL_RNC_Official.cer (publico)" -ForegroundColor White
    Write-Host "  3. IPPEL_RNC_Official.pem (servidor)" -ForegroundColor White
    Write-Host ""
    Write-Host "SENHA DO CERTIFICADO:" -ForegroundColor Yellow
    Write-Host "  $Password" -ForegroundColor White
    Write-Host ""
    Write-Host "Para instalar via GPO:" -ForegroundColor Cyan
    Write-Host "  1. Abra: Group Policy Management" -ForegroundColor White
    Write-Host "  2. Edite a GPO desejada" -ForegroundColor White
    Write-Host "  3. Va em: Computer Configuration > Policies >" -ForegroundColor White
    Write-Host "     Windows Settings > Security Settings >" -ForegroundColor White
    Write-Host "     Public Key Policies > Trusted Root Certification Authorities" -ForegroundColor White
    Write-Host "  4. Clique com botao direito > Import" -ForegroundColor White
    Write-Host "  5. Selecione: IPPEL_RNC_Official.cer" -ForegroundColor White
    Write-Host "  6. Execute: gpupdate /force nos clientes" -ForegroundColor White
    Write-Host ""
    Write-Host "URL de acesso:" -ForegroundColor Cyan
    Write-Host "  https://172.25.100.105:5001" -ForegroundColor White
    Write-Host ""
    
    exit 0
    
} catch {
    Write-Host ""
    Write-Host "[ERRO] Falha ao gerar certificado!" -ForegroundColor Red
    Write-Host "Detalhes: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    exit 1
}

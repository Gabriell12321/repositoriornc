# 🔐 CERTIFICADO SSL PARA SISTEMA RNC IPPEL

Este diretório contém o script para gerar e instalar o certificado SSL autoassinado do sistema RNC.

## 📋 Como Usar

### ⚠️ ANTES DE COMEÇAR - TESTE:

**IMPORTANTE:** Teste primeiro para garantir que tudo funciona!

1. **Teste PowerShell**: **duplo clique** em `TESTE_POWERSHELL.bat`
   - Deve gerar certificado de teste
   - Se aparecer "SUCESSO!", está OK para continuar
   - Se aparecer "ERRO!", veja "Solução de Problemas" abaixo

2. **Teste Script**: **duplo clique** em `TESTE_SIMPLES.bat`
   - Deve aparecer mensagem e NÃO fechar
   - Se fechar sozinho, use o Método Manual abaixo

### 1️⃣ Executar o Script

**OPÇÃO 1 - MAIS FÁCIL:**
- Dê **duplo clique** em: `EXECUTAR_AQUI.bat`
- Clique em "Sim" quando pedir permissão de administrador
- Pronto!

**OPÇÃO 2 - MANUAL:**
1. Pressione `Win + X` e escolha "Terminal (Admin)" ou "PowerShell (Admin)"
2. Digite: `cd "i:\Informatica\RNC em Produção\repositoriornc-d25fe14acd0148664f67c4d9940f057b894cd479\certificado testar"`
3. Digite: `.\gerar_e_instalar_certificado.bat`
4. Pressione Enter

### 2️⃣ O que o Script Faz

O script realiza automaticamente:

✅ **Gera certificado SSL autoassinado** (válido por 10 anos)
- Algoritmo: RSA 4096 bits
- Domínios cobertos: rnc.ippel.com.br, localhost, 127.0.0.1, 172.26.0.75

✅ **Adiciona entrada no arquivo hosts**
- `172.26.0.75 rnc.ippel.com.br`

✅ **Importa certificado no Windows**
- Adiciona na loja de certificados raiz confiáveis
- Chrome e Edge aceitarão automaticamente

✅ **Cria arquivos necessários**
- `certs/ippel_cert.pem` - Certificado público
- `certs/ippel_key.pem` - Chave privada (se OpenSSL disponível)
- `certs/ippel_combined.pem` - Certificado + chave combinados

## 🌐 Configurar Firefox

O Firefox usa sua própria loja de certificados. Você tem 2 opções:

### Opção A: Aceitar Exceção (Mais Rápido)

1. Acesse: `https://rnc.ippel.com.br:5001`
2. Clique em **"Avançado..."**
3. Clique em **"Aceitar o risco e continuar"**
4. ✅ Pronto!

### Opção B: Importar Certificado (Permanente)

1. Abra o Firefox
2. Digite na barra: `about:preferences#privacy`
3. Role até **"Certificados"** → Clique em **"Ver certificados..."**
4. Vá na aba **"Autoridades"**
5. Clique em **"Importar..."**
6. Navegue até: `certificado testar\certs\ippel_cert.pem`
7. Marque: ✅ **"Confiar nesta CA para identificar sites"**
8. Clique em **"OK"**
9. Reinicie o Firefox

## 🚀 Acessar o Sistema

Após configurar, acesse:

- 🌐 **https://rnc.ippel.com.br:5001** (recomendado)
- 🌐 **https://172.26.0.75:5001**
- 🌐 **https://localhost:5001**

## 📁 Estrutura de Arquivos

```
certificado testar/
├── EXECUTAR_AQUI.bat                  ← ⭐ Execute este! (mais fácil)
├── TESTE_POWERSHELL.bat               ← Teste primeiro (recomendado)
├── TESTE_SIMPLES.bat                  ← Teste se janela não fecha
├── gerar_e_instalar_certificado.bat   ← Script principal
├── generate_cert.ps1                  ← Script PowerShell auxiliar
├── importar_no_firefox.bat            ← Guia para Firefox
├── README.md                          ← Você está aqui
└── certs/                             ← Criado automaticamente
    ├── ippel_cert.pem                 ← Certificado público
    ├── ippel_key.pem                  ← Chave privada (se OpenSSL)
    └── ippel_combined.pem             ← Certificado + chave
```

## ❓ Solução de Problemas

### "Erro: Execute como Administrador"
- Clique com botão direito no .bat → "Executar como administrador"

### Firefox ainda mostra aviso
- Use a Opção A (aceitar exceção) ou Opção B (importar certificado)
- O aviso é esperado para certificados autoassinados

### Chrome/Edge ainda mostra aviso
- Verifique se o script foi executado como administrador
- Execute novamente o script
- Reinicie o navegador

### "OpenSSL não encontrado"
- Normal! O script funcionará sem o OpenSSL
- O certificado será gerado usando PowerShell
- Tudo funcionará normalmente

## 🔒 Segurança

- ✅ Certificado **autoassinado** - seguro para uso interno
- ✅ Válido por **10 anos**
- ✅ Algoritmo **RSA 4096 bits**
- ✅ **Não expor** fora da rede interna da empresa

## 📞 Suporte

Se encontrar problemas:

1. Execute o script novamente como administrador
2. Verifique se o servidor está rodando
3. Teste com diferentes navegadores
4. Limpe o cache do navegador (Ctrl+Shift+Del)

---

**Data de criação:** 14/10/2025  
**Validade:** 10 anos  
**Empresa:** IPPEL  
**Sistema:** RNC - Relatório de Não Conformidade

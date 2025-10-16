# 🔐 CERTIFICADO OFICIAL PARA GPO - IPPEL RNC

## 📋 Informações do Certificado

- **Servidor:** https://172.25.100.105:5001
- **Validade:** 10 anos
- **Algoritmo:** RSA 4096 bits
- **Domínios cobertos:** 
  - 172.25.100.105
  - rnc.ippel.com.br
  - localhost

## 🚀 Como Gerar o Certificado Oficial

### Passo 1: Gerar Certificado

1. **Execute como Administrador:**
   - Clique com botão direito em: `GERAR_CERTIFICADO_OFICIAL.bat`
   - Selecione: "Executar como administrador"

2. **Aguarde a geração**
   - O processo leva alguns segundos
   - Não feche a janela

3. **Anote a senha:**
   ```
   SENHA: IPPEL@2025#RNC
   ```

### Passo 2: Arquivos Gerados

Serão criados em: `certificado_oficial/`

1. **`IPPEL_RNC_Official.cer`** ← Use este para GPO!
   - Certificado público
   - Instalar em: Trusted Root Certification Authorities

2. **`IPPEL_RNC_Official.pfx`** (opcional)
   - Certificado com chave privada
   - Senha: `IPPEL@2025#RNC`

3. **`IPPEL_RNC_Official.pem`**
   - Para o servidor (se necessário)

## 🏢 Instalar via GPO (Group Policy)

### Método 1: Via GPMC (Recomendado)

1. **Abrir Group Policy Management Console:**
   ```
   Win + R → gpmc.msc → Enter
   ```

2. **Criar ou Editar GPO:**
   - Clique com botão direito na OU desejada
   - "Create a GPO in this domain, and Link it here..." ou edite uma existente

3. **Navegar até Certificados:**
   ```
   Computer Configuration
     └─ Policies
        └─ Windows Settings
           └─ Security Settings
              └─ Public Key Policies
                 └─ Trusted Root Certification Authorities
   ```

4. **Importar Certificado:**
   - Clique com botão direito em "Trusted Root Certification Authorities"
   - Selecione: "Import..."
   - Navegue até: `certificado_oficial\IPPEL_RNC_Official.cer`
   - Clique em "Next" → "Next" → "Finish"

5. **Aplicar GPO:**
   - Feche o editor de GPO
   - No GPMC, clique com botão direito na GPO
   - Selecione: "Enforced" (opcional, mas recomendado)

6. **Forçar atualização nos clientes:**
   ```cmd
   gpupdate /force
   ```

### Método 2: Via Script (Distribuição Rápida)

Você pode criar um script para executar em cada PC:

```batch
@echo off
certutil -addstore -f "Root" "\\servidor\share\IPPEL_RNC_Official.cer"
echo Certificado instalado!
pause
```

## 🖥️ Verificar Instalação

### No Cliente:

1. **Verificar certificado instalado:**
   ```
   Win + R → certmgr.msc → Enter
   ```

2. **Navegar até:**
   ```
   Trusted Root Certification Authorities
     └─ Certificates
        └─ Procurar por: "IPPEL RNC"
   ```

3. **Testar acesso:**
   - Abrir navegador
   - Acessar: `https://172.25.100.105:5001`
   - **NÃO deve** aparecer aviso de segurança

## 🔒 Segurança

### Senha do Certificado:
```
IPPEL@2025#RNC
```

**⚠️ IMPORTANTE:**
- Guarde esta senha em local seguro
- Não compartilhe o arquivo `.pfx` sem necessidade
- O arquivo `.cer` é público e pode ser distribuído

## 📝 Instruções para TI

### 1. Gerar Certificado (Este PC/Servidor)
```
Execute: GERAR_CERTIFICADO_OFICIAL.bat
```

### 2. Configurar GPO (Domain Controller)
```
1. Copiar IPPEL_RNC_Official.cer para DC
2. Abrir GPMC
3. Importar em: Computer Config > Public Key Policies > Trusted Root
4. Link GPO para OU desejada
```

### 3. Atualizar Clientes
```batch
# Em cada cliente ou via script remoto:
gpupdate /force
```

### 4. Validar
```
# Acessar de qualquer cliente:
https://172.25.100.105:5001
```

## 🌐 URLs de Acesso

Após instalação do certificado via GPO, os usuários podem acessar:

- **Principal:** https://172.25.100.105:5001
- **Alternativo (se configurado DNS):** https://rnc.ippel.com.br:5001

## ❓ Solução de Problemas

### Certificado não aparece nos clientes
```
1. Verificar se GPO está linkada à OU correta
2. Executar: gpresult /r (verificar GPOs aplicadas)
3. Forçar update: gpupdate /force
4. Reiniciar computador
```

### Ainda aparece aviso no navegador
```
1. Limpar cache do navegador (Ctrl+Shift+Del)
2. Verificar se certificado está em "Trusted Root"
3. Reiniciar navegador
```

### Firefox ainda mostra aviso
```
Firefox usa sua própria loja de certificados.
Opção 1: Aceitar exceção manualmente
Opção 2: Configurar Firefox para usar certificados do Windows
```

## 📞 Suporte

**Gerado em:** 14/10/2025  
**Empresa:** IPPEL  
**Sistema:** RNC - Relatório de Não Conformidade  
**Servidor:** 172.25.100.105:5001

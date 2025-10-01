# 🌐 ACESSO LOCAL VIA IP - SISTEMA IPPEL

## 📋 Visão Geral

O sistema IPPEL agora permite acesso aos relatórios de não conformidades (RNCs) diretamente via IP local, permitindo que stakeholders acessem os relatórios sem necessidade de login ou instalação de software.

## 🚀 Como Funciona

### 1. **Servidor Local**
- O sistema roda em `http://[SEU_IP]:5000`
- Acessível por qualquer dispositivo na mesma rede
- Links únicos para cada RNC

### 2. **Links Seguros**
- Cada RNC recebe um token único
- Código de acesso de 6 dígitos
- Expiração automática (30 dias)
- Limite de acessos configurável

### 3. **Acesso Público**
- URL: `http://[SEU_IP]:5000/rnc/view/[TOKEN]`
- Interface responsiva
- Funciona em celulares, tablets e computadores

## 🛠️ Configuração

### **Passo 1: Iniciar o Sistema**
```bash
# Windows
start_local.bat

# Linux/Mac
python main_system.py
```

### **Passo 2: Verificar IP Local**
O sistema mostrará automaticamente:
```
🌐 INFORMAÇÕES DE REDE - SISTEMA IPPEL
============================================================
📱 IP Local: 192.168.1.100
🌍 URL do Servidor: http://192.168.1.100:5000
📋 Interface Web: http://192.168.1.100:5000
📧 Links de RNC: http://192.168.1.100:5000/rnc/view/[TOKEN]
```

### **Passo 3: Configurar Firewall**
- **Windows**: Permitir Python na porta 5000
- **Linux**: `sudo ufw allow 5000`
- **Mac**: Configurar Firewall do Sistema

## 📧 Envio de Links

### **Via Email**
1. Preencher formulário de RNC
2. Clicar no botão 📧 (Enviar por Email)
3. Inserir email do destinatário
4. Sistema gera link único automaticamente
5. Email é enviado com link e código de acesso

### **Exemplo de Email Enviado**
```
📧 Assunto: RNC2024-0001 - Falha no equipamento

🔗 Acesse o RNC Completo:
   [📋 Ver RNC Completo]

   Código de Acesso: ABC123
   Válido até: 2024-02-15
   🌐 Acesse via: http://192.168.1.100:5000
```

## 🔐 Segurança

### **Medidas Implementadas**
- ✅ Tokens únicos de 32 caracteres
- ✅ Códigos de acesso de 6 dígitos
- ✅ Expiração automática
- ✅ Limite de acessos
- ✅ Log de auditoria
- ✅ Validação de IP

### **Recomendações**
- 🔒 Use apenas em redes confiáveis
- 🔒 Monitore logs de acesso
- 🔒 Faça backup regular do banco
- 🔒 Mantenha o sistema atualizado

## 📱 Acesso em Dispositivos

### **Computador**
- Abrir navegador
- Acessar: `http://[SEU_IP]:5000/rnc/view/[TOKEN]`
- Inserir código de acesso
- Visualizar RNC completo

### **Celular/Tablet**
- Abrir navegador móvel
- Acessar o mesmo link
- Interface responsiva automaticamente
- Funciona offline após carregamento

### **Exemplo de URL**
```
http://192.168.1.100:5000/rnc/view/abc123def456ghi789
```

## 🔧 Solução de Problemas

### **Problema: Não consegue acessar**
**Solução:**
1. Verificar se servidor está rodando
2. Confirmar IP correto
3. Verificar firewall
4. Testar na mesma rede

### **Problema: Link expirado**
**Solução:**
1. Gerar novo link
2. Enviar novo email
3. Verificar data de expiração

### **Problema: Código não funciona**
**Solução:**
1. Verificar se código está correto
2. Confirmar maiúsculas/minúsculas
3. Tentar novamente
4. Solicitar novo código

## 📊 Monitoramento

### **Logs de Acesso**
- Data/hora de acesso
- IP do dispositivo
- User-Agent (navegador)
- Sucesso/falha do acesso

### **Estatísticas**
- Número de acessos por link
- Dispositivos mais usados
- Horários de pico
- Links mais acessados

## 🎯 Vantagens

### **Para a IPPEL**
- ✅ Controle total sobre acessos
- ✅ Rastreamento completo
- ✅ Sem necessidade de contas
- ✅ Interface profissional

### **Para Stakeholders**
- ✅ Acesso direto e rápido
- ✅ Sem instalação necessária
- ✅ Funciona em qualquer dispositivo
- ✅ Interface familiar

### **Para o Processo**
- ✅ Comunicação eficiente
- ✅ Redução de emails
- ✅ Centralização de informações
- ✅ Auditoria completa

## 🚀 Próximos Passos

### **Melhorias Planejadas**
- 🔄 Notificações push
- 🔄 Assinatura digital
- 🔄 Comentários em tempo real
- 🔄 Versão offline
- 🔄 Integração com WhatsApp

### **Expansão**
- 🌍 Acesso via internet
- 📱 App móvel nativo
- 🔗 Integração com outros sistemas
- 📊 Dashboard de analytics

---

## 📞 Suporte

Para dúvidas ou problemas:
- 📧 Email: suporte@ippel.com.br
- 📱 WhatsApp: (11) 99999-9999
- 🌐 Sistema: http://[SEU_IP]:5000/suporte

---

**Sistema IPPEL - Relatórios de Não Conformidades**  
*Versão Local - Acesso via IP* 
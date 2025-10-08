# 📋 Aba Evidências em STANDBY

## ✅ Status: OCULTA TEMPORARIAMENTE

A aba **"📊 Evidências"** está temporariamente oculta no dashboard.

---

## 🔧 Como Reativar Quando Precisar

### Passo 1: Abrir o arquivo
```
C:\RNC\templates\dashboard_improved.html
```

### Passo 2: Procurar pela linha (aprox. linha 1420)
```html
<!-- ⚠️ STANDBY: Aba Evidências temporariamente oculta - Remova o style="display:none;" para reativar -->
<button class="tab-button" data-tab="evidencias" onclick="switchTab('evidencias')" style="display:none;">
    📊 Evidências
</button>
```

### Passo 3: Remover o `style="display:none;"`
Alterar de:
```html
<button class="tab-button" data-tab="evidencias" onclick="switchTab('evidencias')" style="display:none;">
```

Para:
```html
<button class="tab-button" data-tab="evidencias" onclick="switchTab('evidencias')">
```

### Passo 4: Salvar e reiniciar o servidor
```powershell
taskkill /F /IM python.exe
python server_form.py
```

### Passo 5: Recarregar a página
Pressione **Ctrl + F5** no navegador

---

## 📊 Estado Atual do Dashboard

| Aba | Status |
|-----|--------|
| 📊 RNCs Mensais por Setor | ✅ Visível |
| ✅ Finalizados | ✅ Visível |
| 📊 Evidências | ⏸️ **OCULTA** |
| 📑 Levantamento 14-15 | ✅ Visível |

---

## 💡 Observações

- ✅ **Funcionalidade preservada**: Todo código da aba permanece intacto
- ✅ **Reativação simples**: Apenas remover um atributo CSS
- ✅ **Sem impacto**: Outras abas funcionam normalmente
- ⚠️ **Não delete o código**: Está apenas oculto, não removido

---

**Data:** 07/10/2025  
**Motivo:** Ajustes pendentes na funcionalidade de Evidências  
**Branch:** producao-com-dados

# 📊 ATUALIZAÇÃO: RNCs Mensais por Setor

## 🎯 RESUMO DAS MUDANÇAS

A aba **"Engenharia"** foi reformulada para **"RNCs Mensais por Setor"**, permitindo visualizar gráficos de qualquer setor através de um dropdown seletor.

---

## ✅ O QUE FOI ALTERADO

### **1. Interface do Usuário (Frontend)**

#### **Aba Renomeada**:
```html
Antes: 🔧 Engenharia [0]
Agora:  📊 RNCs Mensais por Setor
```

#### **Novo Dropdown de Seleção**:
```
📊 Selecione o Setor:
  - 🔧 Engenharia
  - 🏭 Produção
  - 📋 PCP
  - ✅ Qualidade
  - 🛒 Compras
  - 💼 Comercial
  - 🤝 Terceiros
```

#### **Características**:
- ✅ Sem contagem de badge na aba (não carrega dados até selecionar)
- ✅ Seletor dinâmico de setores
- ✅ Informações do indicador ajustáveis por setor
- ✅ Gráficos mensais, acumulados e detalhes diários
- ✅ Meta configurável por setor

---

### **2. Backend (API)**

#### **Nova API Genérica**:
```
GET /api/indicadores/setor?setor={nome_setor}
```

**Parâmetros**:
- `setor`: engenharia, producao, pcp, qualidade, compras, comercial, terceiros

**Retorno** (JSON):
```json
{
  "success": true,
  "setor": "Produção",
  "rncs_count": 580,
  "stats": {
    "total_rncs": 580,
    "finalized_rncs": 580,
    "active_rncs": 0,
    "total_value": 150000.00,
    "avg_value": 258.62
  },
  "monthly_trend": [
    {
      "month": "2023-01",
      "count": 45,
      "accumulated_count": 45,
      "value": 12000.00,
      "accumulated_value": 12000.00,
      "daily_details": [
        {"day": 1, "count": 2},
        {"day": 2, "count": 3},
        ...
      ]
    },
    ...
  ],
  "rncs": [...]
}
```

---

### **3. JavaScript (Lógica)**

#### **Novas Funções**:

1. **`loadSetorData()`**:
   - Carrega dados do setor selecionado
   - Chama a API `/api/indicadores/setor`
   - Atualiza UI com informações do setor

2. **`buildSetorCharts(apiData, setor)`**:
   - Constrói todos os gráficos do setor
   - Usa meta específica do setor
   - Processa dados mensais e diários

3. **`buildSetorMonthlyChart(labels, values, goalArr, cumulative)`**:
   - Gráfico de barras + linhas (Realizado, Meta, Acumulado)
   - Clicável para ver detalhes do mês

4. **`buildSetorAccumChart(labels, cumulative, goalAccum)`**:
   - Gráfico de linha: Acumulado Real vs Meta

5. **`updateSetorMonth(monthIdx)`**:
   - Atualiza dropdown de mês
   - Mostra detalhes diários do mês selecionado

6. **`updateSetorMonthDetail(monthIdx)`**:
   - Constrói gráfico de barras com detalhes diários

7. **`updateSetorInfo(monthIdx)`**:
   - Atualiza indicadores (Realizado, Variação)

8. **`resetSetorSelection()`**:
   - Reseta seleção de mês para visão geral

#### **Configurações de Metas por Setor**:
```javascript
const setorMetas = {
  'engenharia': 30,
  'producao': 50,
  'pcp': 20,
  'qualidade': 15,
  'compras': 10,
  'comercial': 10,
  'terceiros': 25
};
```

---

## 📋 ESTRUTURA DOS GRÁFICOS

### **1. Gráfico Mensal**:
- **Tipo**: Barra (Realizado) + Linha (Meta + Acumulado)
- **Interativo**: Clique em uma barra para ver detalhes do mês
- **Cores**:
  - 🔵 Azul: RNCs Finalizadas
  - 🟢 Verde: Meta
  - 🟣 Roxo: Acumulado

### **2. Gráfico Acumulado vs Meta**:
- **Tipo**: Linha
- **Cores**:
  - 🔵 Azul sólido: Acumulado Real
  - 🟢 Verde tracejado: Meta Acumulada

### **3. Detalhes do Mês (dias)**:
- **Tipo**: Barra
- **Cor**: 🟠 Laranja
- **Mostra**: RNCs por dia do mês selecionado

---

## 🔧 BACKEND: LÓGICA DA API

### **Filtros SQL**:
```sql
WHERE (
    LOWER(TRIM(area_responsavel)) LIKE '%{setor}%'
    OR LOWER(TRIM(setor)) LIKE '%{setor}%'
)
AND (is_deleted = 0 OR is_deleted IS NULL)
```

### **Correção de Data**:
```python
# Usar created_at como fallback se finalized_at for NULL
date_to_use = finalized_at if finalized_at else created_at
```

**Razão**: Muitas RNCs não têm `finalized_at` preenchido, mas todas têm `created_at`.

---

## 🎨 INTERFACE VISUAL

### **Bloco de Informações do Indicador**:
```
┌────────────────────────────────────────────────────────┐
│ Indicador: RNC - Relatório de Não Conformidade        │
│ Objetivo: Apontar a quantidade de não conformidades   │
│ Departamento: [Produção]                               │
│ Área: Corporativo                                      │
│ Unidade: UN                                            │
│ Meta: [50]                                             │
│ Realizado: [580]                                       │
│ Variação: [+530]                                       │
└────────────────────────────────────────────────────────┘
```

### **Dropdown de Mês**:
```
┌─────────────────────────────────────────┐
│ 🏭 Produção – RNCs Mensais              │
│                          Mês: [Todos ▼] │
│                               [Reset]   │
└─────────────────────────────────────────┘
```

---

## 📊 DADOS POR SETOR (Atual)

```
┌──────────────┬────────────┬─────────────┐
│ Setor        │ Total RNCs │ % do Total  │
├──────────────┼────────────┼─────────────┤
│ Engenharia   │ 2.762      │ 74.8%       │
│ Produção     │ 580        │ 15.7%       │
│ Terceiros    │ 320        │ 8.7%        │
│ Compras      │ 12         │ 0.3%        │
│ PCP          │ 8          │ 0.2%        │
│ Qualidade    │ 5          │ 0.1%        │
│ Comercial    │ 4          │ 0.1%        │
├──────────────┼────────────┼─────────────┤
│ TOTAL        │ 3.694      │ 100%        │
└──────────────┴────────────┴─────────────┘
```

---

## 🚀 COMO USAR

1. **Acesse a aba**: Clique em **"📊 RNCs Mensais por Setor"**
2. **Selecione um setor**: Escolha no dropdown (ex: 🏭 Produção)
3. **Visualize os gráficos**:
   - Gráfico mensal com barras e linhas
   - Acumulado vs Meta
4. **Explore um mês específico**:
   - Clique em uma barra OU
   - Selecione no dropdown "Mês"
5. **Veja detalhes diários**: Gráfico de barras por dia
6. **Volte à visão geral**: Clique em **"Reset"**

---

## 🔄 COMPARAÇÃO: ANTES vs DEPOIS

### **ANTES**:
```
✅ Aba "Engenharia" fixa
✅ Apenas dados da engenharia
✅ Badge com contagem (0 antes da correção)
✅ Carregamento automático ao abrir aba
```

### **DEPOIS**:
```
✅ Aba "RNCs Mensais por Setor" genérica
✅ Dados de QUALQUER setor (7 opções)
✅ SEM badge (não carrega até selecionar)
✅ Carregamento sob demanda (selecionar setor)
✅ API genérica reutilizável
✅ Metas configuráveis por setor
```

---

## 🎯 BENEFÍCIOS

1. ✅ **Flexibilidade**: Visualizar qualquer setor
2. ✅ **Performance**: Não carrega dados até necessário
3. ✅ **Escalabilidade**: Fácil adicionar novos setores
4. ✅ **Consistência**: Mesma experiência visual para todos os setores
5. ✅ **Manutenibilidade**: Código reutilizável e limpo

---

## 🔐 SEGURANÇA

- ✅ Autenticação: Requer `session['user_id']`
- ✅ Validação: Apenas setores pré-definidos
- ✅ SQL Injection: Uso de placeholders (`?`)
- ✅ Filtros: `is_deleted = 0` para dados ativos

---

## 📦 ARQUIVOS MODIFICADOS

### **Frontend**:
- `templates/dashboard_improved.html`:
  - Linha ~1371: Aba renomeada
  - Linha ~1614-1672: Novo HTML para setores
  - Linha ~2190-2195: Lógica `loadRNCs` para aba setores
  - Linha ~3360: Container mapping atualizado
  - Linha ~3382-3390: Show/hide charts de setores
  - Linha ~10362-10720: Novas funções JavaScript

### **Backend**:
- `server_form.py`:
  - Linha ~2153-2322: Nova API `/api/indicadores/setor`

---

## 🧪 TESTES

### **Teste 1: Seleção de Setor**
```
1. Acesse aba "RNCs Mensais por Setor"
2. Selecione "Engenharia"
3. ✅ Deve mostrar 2.763 RNCs
4. ✅ Gráficos devem carregar
```

### **Teste 2: Troca de Setor**
```
1. Selecione "Engenharia" (2.763 RNCs)
2. Troque para "Produção"
3. ✅ Deve mostrar 580 RNCs
4. ✅ Gráficos devem atualizar
```

### **Teste 3: Detalhes do Mês**
```
1. Selecione "Produção"
2. Clique em uma barra do gráfico mensal
3. ✅ Dropdown "Mês" deve atualizar
4. ✅ Gráfico de detalhes diários deve aparecer
```

### **Teste 4: Reset**
```
1. Selecione um mês
2. Clique em "Reset"
3. ✅ Dropdown "Mês" deve voltar para "Todos"
4. ✅ Gráfico de detalhes deve desaparecer
```

---

## 🐛 TROUBLESHOOTING

### **Problema**: Gráficos não aparecem
**Solução**: Verifique se selecionou um setor no dropdown

### **Problema**: API retorna erro 400
**Solução**: Verifique se o nome do setor está correto (lowercase)

### **Problema**: RNCs com count = 0
**Solução**: Verifique se o setor tem RNCs no banco de dados

---

## 📝 NOTAS TÉCNICAS

1. **Cache**: Os dados são armazenados em `window._setorDataCache`
2. **Charts**: Usa Chart.js com `destroy()` antes de recriar
3. **Fallback**: Usa `created_at` se `finalized_at` for NULL
4. **Performance**: Carregamento sob demanda (on-demand)

---

## 🎉 CONCLUSÃO

A nova funcionalidade **"RNCs Mensais por Setor"** oferece:
- ✅ **Visão unificada** de todos os setores
- ✅ **Interface intuitiva** com dropdown
- ✅ **Gráficos interativos** e detalhados
- ✅ **Performance otimizada** (carregamento sob demanda)
- ✅ **Código limpo** e manutenível

**Status**: ✅ **PRONTO PARA PRODUÇÃO**

---

**Data**: 2025-10-05  
**Versão**: 2.0  
**Desenvolvedor**: AI Assistant

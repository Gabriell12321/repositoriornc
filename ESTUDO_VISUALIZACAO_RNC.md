# 📋 ESTUDO COMPLETO DA VISUALIZAÇÃO DE RNC

## 🎯 Análise da Interface Atual

### 📁 Estrutura de Arquivos de Visualização

**Templates de Visualização Identificados:**
- `view_rnc_full.html` - Template principal usado (linha 462 de routes/rnc.py)
- `view_rnc.html` - Template alternativo
- `view_rnc_print.html` - Versão para impressão
- `view_rnc_pdf_js.html` - Versão para geração de PDF
- `view_rnc_public.html` - Versão pública

### 🔄 Rota Principal
**URL:** `/rnc/<int:rnc_id>`
**Função:** `view_rnc(rnc_id)` em `routes/rnc.py` linha 387

**Query SQL utilizada:**
```sql
SELECT r.*,
       u.name as user_name,
       au.name as assigned_user_name,
       u.department as user_department,
       au.department as assigned_user_department
FROM rncs r
LEFT JOIN users u ON r.user_id = u.id
LEFT JOIN users au ON r.assigned_user_id = au.id
WHERE r.id = ?
```

### 🎨 Layout Visual Identificado na Imagem

**1. Header Superior:**
- Logo IPPEL (esquerda)
- Título: "Relatório De Não Conformidades Internas – RNC"
- Código: "FQ - 002"
- Número da RNC destacado em vermelho
- Data de emissão
- Conformidades internas RNC

**2. Seção de Informações Principais:**
```
DES.    | [valor]  | MP.     | [valor] | REV.      | [valor]
POS.    | [valor]  | CV.     | [valor] | MOD.      | [valor]
EQUIPAMENTO | [valor] | CONJUNTO | [valor] | CLIENTE | [valor]
```

**3. Seção de Responsabilidade:**
- ÁREA RESPONSÁVEL (setor)
- ASSINATURA GERENTE
- ASSINATURA LÍDER SETOR
- INSPECTOR
- DATA EMISSÃO
- VALOR

**4. Tabelas de Processo:**
- DESCRIÇÃO DA NÃO CONFORMIDADE
- INSTRUÇÃO PARA RETRABALHO  
- CAUSA DA RNC
- AÇÃO A SER TOMADA

**5. Seção de Disposição:**
- DISPOSIÇÃO DO MATERIAL NÃO CONFORME
- DISPOSIÇÃO DO DESTINATÁRIO
- Assinaturas: INSPEÇÃO, ENGENHARIA, INSPEÇÃO
- Campos de VISTO com data

### 🔍 Problemas Identificados

**1. Campo ÁREA RESPONSÁVEL (linha 681):**
```html
<td>{{ rnc.department or rnc.user_department or '-' }}</td>
```
- ❌ Atualmente usa `rnc.department` (campo da tabela users)
- ✅ Deveria usar `rnc.setor` (campo da tabela rncs com dados do TXT)

**2. Campo de Responsável:**
- ❌ Template não mostra explicitamente o responsável
- ✅ Deveria mostrar `rnc.responsavel` do TXT

**3. Query da Rota:**
- ❌ Está fazendo JOIN com users para pegar department
- ✅ Deveria pegar setor e responsavel direto da tabela rncs

### 📊 Campos Mapeados do TXT

**Campos disponíveis na tabela `rncs`:**
- `responsavel` - Nome do responsável real do TXT
- `setor` - Setor real do TXT
- `inspetor` - Inspetor
- `material` - Material
- `quantity` - Quantidade
- `drawing` - Desenho
- E outros...

### 🎨 Características Visuais

**Cores utilizadas:**
- Vermelho primário: `#C1272D` (cabeçalhos)
- Azul escuro: `#2c3e50` (texto)
- Cinza claro: `#f8f9fa` (fundo)

**Layout:**
- Design tipo formulário impresso
- Tabelas estruturadas
- Logo da empresa no header
- Campos organizados em seções lógicas

### 🔧 Funcionalidades Identificadas

**Botões de Ação:**
- ← Voltar (vermelho)
- ✏️ Editar
- 🖨️ Imprimir (verde)
- 📄 Baixar PDF (vermelho)

**URLs de ação:**
- `/rnc/<id>/edit` - Edição
- `/rnc/<id>/print` - Impressão
- `/rnc/<id>/download-pdf` - Download PDF

### 📋 Seções do Formulário

**1. Dados Básicos:**
- Desenho, MP, Revisão
- Posição, CV, Modelo
- Equipamento, Conjunto, Cliente

**2. Dados de Responsabilidade:**
- Área Responsável
- Assinaturas (Gerente, Líder, Inspetor)
- Data de Emissão
- Valor

**3. Processo de RNC:**
- Item 1: Descrição da Não Conformidade
- Item 2: Instrução para Retrabalho
- Item 3: Causa da RNC
- Item 4: Ação a ser Tomada

**4. Disposição:**
- Material Não Conforme
- Destinatário
- Vistos com datas

### 🎯 Conclusões

**Template Principal:** `view_rnc_full.html`
**Estilo:** Design profissional tipo formulário impresso
**Layout:** Bem estruturado com seções claras
**Problema:** Campos não estão puxando dados corretos do TXT
**Solução:** Ajustar query e template para usar campos da tabela rncs

**Estado Atual:** ✅ Interface bem desenhada e funcional
**Necessidade:** 🔧 Apenas correção dos dados exibidos (responsável e setor)
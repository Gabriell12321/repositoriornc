# 🎮 Dashboard Interativo IPPEL

Sistema de dashboard moderno e interativo para o controle de RNCs (Relatórios de Não Conformidade).

## 🎯 Características do Dashboard

### 🎨 Design Moderno
- **Interface gamificada** com animações suaves
- **Cards interativos** com hover effects
- **Gradientes coloridos** e glassmorphism
- **Responsivo** para mobile e desktop
- **Animações CSS** para melhor UX

### 📊 Estatísticas Visuais
- **Cards de estatísticas** clicáveis
- **Contadores em tempo real**
- **Filtros interativos** por status
- **Gráficos visuais** com cores

### 🎮 Funcionalidades Interativas

#### **Cards de Estatísticas**
- **📊 Total de RNCs**: Mostra o número total
- **⏳ Pendentes**: RNCs em andamento
- **✅ Concluídos**: RNCs finalizados
- **Clique nos cards** para filtrar a lista

#### **Cards de Ação**
- **📝 Criar Novo RNC**: Vai para o formulário
- **📋 Ver Todos os RNCs**: Lista completa
- **Hover effects** com animações

#### **Lista de RNCs**
- **Cards individuais** para cada RNC
- **Status coloridos** (Pendente/Concluído)
- **Informações detalhadas**:
  - Número do RNC
  - Título
  - Data de criação
  - Status atual

## 🚀 Como Usar

### 1. **Acesso**
```
http://IP:5001
```

### 2. **Login**
- Use qualquer usuário cadastrado:
  - `joao@ippel.com.br` / `joao123`
  - `maria@ippel.com.br` / `maria123`
  - `pedro@ippel.com.br` / `pedro123`
  - `ana@ippel.com.br` / `ana123`

### 3. **Dashboard**
Após o login, você verá:

#### **Header**
- Logo IPPEL
- Nome do usuário
- Departamento
- Botão de logout

#### **Estatísticas**
- Cards clicáveis com números
- Cores diferentes por categoria
- Animações ao passar o mouse

#### **Ações**
- Botões grandes e intuitivos
- Descrições claras
- Efeitos visuais

#### **Lista de RNCs**
- Últimos 5 RNCs criados
- Status visual
- Clique para ver detalhes

## 🎨 Elementos Visuais

### **Cores**
- **Azul**: Total de RNCs
- **Laranja**: Pendentes
- **Verde**: Concluídos
- **Vermelho**: Ações importantes

### **Animações**
- **fadeInUp**: Entrada suave dos elementos
- **hover**: Elevação dos cards
- **transform**: Movimentos suaves
- **transition**: Transições fluidas

### **Glassmorphism**
- **Backdrop blur**: Efeito de vidro
- **Transparência**: Elementos translúcidos
- **Sombras**: Profundidade visual

## 📱 Responsividade

### **Desktop**
- Grid de 3 colunas para estatísticas
- Layout amplo e espaçado
- Hover effects completos

### **Mobile**
- Grid de 1 coluna
- Layout compacto
- Touch-friendly

## 🔄 Fluxo de Navegação

### **Login → Dashboard**
1. Acesse `http://IP:5001`
2. Faça login
3. Redirecionamento automático para dashboard

### **Dashboard → Formulário**
1. Clique em "Criar Novo RNC"
2. Vai para o formulário
3. Preencha e salve

### **Formulário → Dashboard**
1. Clique no botão "🏠" (casa)
2. Volta ao dashboard
3. Veja o novo RNC na lista

## 🛠️ Funcionalidades Técnicas

### **APIs Utilizadas**
- `/api/user/info`: Informações do usuário
- `/api/rnc/list`: Lista de RNCs
- `/api/logout`: Logout

### **JavaScript**
- **Async/await**: Requisições assíncronas
- **DOM manipulation**: Atualização dinâmica
- **Event listeners**: Interatividade
- **Error handling**: Tratamento de erros

### **CSS**
- **Grid layout**: Layout responsivo
- **Flexbox**: Alinhamentos
- **CSS animations**: Animações suaves
- **Media queries**: Responsividade

## 🎯 Benefícios

### **Para Usuários**
- **Interface intuitiva** e fácil de usar
- **Feedback visual** imediato
- **Navegação clara** e lógica
- **Estatísticas em tempo real**

### **Para Administradores**
- **Visão geral** rápida
- **Controle de acesso** por usuário
- **Dados organizados** e acessíveis
- **Relatórios visuais**

## 🔧 Personalização

### **Cores**
Edite as variáveis CSS no arquivo `server_form.py`:
```css
.stat-card.total::before { background: linear-gradient(90deg, #007bff, #6610f2); }
.stat-card.pending::before { background: linear-gradient(90deg, #ffc107, #fd7e14); }
.stat-card.completed::before { background: linear-gradient(90deg, #28a745, #20c997); }
```

### **Animações**
Ajuste as durações no CSS:
```css
.fade-in { animation: fadeInUp 0.6s ease-out; }
.stat-card { transition: all 0.3s ease; }
```

### **Layout**
Modifique o grid no CSS:
```css
.stats-grid { grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
```

## 📞 Suporte

### **Problemas Comuns**
1. **Dashboard não carrega**: Verifique se o servidor está rodando
2. **RNCs não aparecem**: Faça login novamente
3. **Animações lentas**: Verifique a performance do navegador

### **Logs**
- Console do navegador (F12)
- Console do servidor Python
- Network tab para debug de APIs

## 🎉 Resultado Final

Um dashboard moderno, interativo e gamificado que torna o controle de RNCs uma experiência agradável e eficiente! 🚀 
# 4M Contabilidade - Dashboard Panel

Sistema de gestão contábil moderno e integrado para a 4M Contabilidade com interface visual atrativa e funcionalidades completas.

**Experience Qualities**:
1. Professional - Interface limpa e corporativa que transmite confiança e expertise
2. Efficient - Navegação intuitiva que acelera tarefas rotineiras dos contadores
3. Modern - Design contemporâneo com elementos visuais que destacam a inovação tecnológica

**Complexity Level**: Complex Application (advanced functionality, accounts)
Sistema robusto com múltiplos módulos integrados, autenticação de usuários, e painéis analíticos avançados para gestão contábil completa.

## Essential Features

**Sistema de Login**
- Functionality: Autenticação segura de usuários com diferentes níveis de acesso
- Purpose: Proteger dados sensíveis e personalizar experiência por função
- Trigger: Acesso inicial ao sistema
- Progression: Tela login → Validação credenciais → Dashboard principal → Módulos específicos
- Success criteria: Login seguro em <3s, sessão persistente, logout automático

**Dashboard Principal com Gráficos**
- Functionality: Visão consolidada de KPIs financeiros e operacionais com gráficos interativos
- Purpose: Fornecer insights rápidos para tomada de decisão estratégica
- Trigger: Login bem-sucedido ou navegação para home
- Progression: Login → Dashboard → Seleção período → Visualização gráficos → Drill-down detalhes
- Success criteria: Carregamento <2s, dados atualizados, interatividade fluida

**Módulo Contabilidade**
- Functionality: Gestão de plano de contas, lançamentos contábeis e balancetes
- Purpose: Centralizar operações contábeis core do negócio
- Trigger: Seleção do módulo no menu principal
- Progression: Acesso módulo → Lista contas/lançamentos → Criar/editar → Validação → Confirmação
- Success criteria: Lançamentos precisos, relatórios corretos, auditoria completa

**Módulo Clientes**
- Functionality: Cadastro e gestão completa de clientes com histórico
- Purpose: Centralizar informações cliente para atendimento personalizado
- Trigger: Menu clientes ou busca específica
- Progression: Lista clientes → Detalhes/novo → Formulário → Validação → Salvamento
- Success criteria: Busca rápida, dados completos, histórico preservado

**Módulos Especializados (Fiscal, RH, Finanças, etc.)**
- Functionality: Áreas específicas com funcionalidades dedicadas
- Purpose: Organizar workflows por departamento/especialidade
- Trigger: Seleção no menu lateral
- Progression: Módulo → Funcionalidade específica → Execução tarefa → Resultados
- Success criteria: Fluxos otimizados, integração entre módulos, relatórios específicos

## Edge Case Handling

- **Sessão Expirada**: Redirecionamento automático para login com mensagem clara
- **Dados Incompletos**: Validação em tempo real com orientações específicas
- **Conexão Perdida**: Modo offline com sincronização automática quando reconectado
- **Permissões Insuficientes**: Mensagens claras sobre limitações de acesso
- **Backup/Recuperação**: Sistema automático de backup com recuperação de dados

## Design Direction

Interface corporativa moderna que transmite profissionalismo e confiança, com elementos visuais limpos que facilitam o trabalho diário. Design minimalista mas funcional, priorizando eficiência sobre decoração.

## Color Selection

Complementary (opposite colors) - Combinação de vermelhos vibrantes com tons neutros para criar contraste profissional e destacar elementos importantes.

- **Primary Color**: Vermelho corporativo moderno (oklch(0.55 0.22 15)) - transmite energia, determinação e marca forte
- **Secondary Colors**: Cinza escuro (oklch(0.25 0 0)) para textos e neutro claro (oklch(0.96 0 0)) para backgrounds
- **Accent Color**: Vermelho vibrante (oklch(0.65 0.25 20)) para CTAs e elementos interativos importantes
- **Foreground/Background Pairings**: 
  - Background Branco (oklch(1 0 0)): Texto escuro (oklch(0.2 0 0)) - Ratio 16.0:1 ✓
  - Primary Red (oklch(0.55 0.22 15)): Texto branco (oklch(1 0 0)) - Ratio 5.2:1 ✓
  - Secondary Gray (oklch(0.25 0 0)): Texto branco (oklch(1 0 0)) - Ratio 12.8:1 ✓
  - Accent Red (oklch(0.65 0.25 20)): Texto branco (oklch(1 0 0)) - Ratio 4.8:1 ✓

## Font Selection

Tipografia corporativa clara e legível que transmite seriedade e modernidade, usando Inter para interface e números para garantir legibilidade em relatórios financeiros.

- **Typographic Hierarchy**: 
  - H1 (Logo/Título Principal): Inter Bold/32px/tight letter spacing
  - H2 (Títulos de Módulo): Inter Semibold/24px/normal spacing  
  - H3 (Seções): Inter Medium/18px/normal spacing
  - Body (Conteúdo Geral): Inter Regular/16px/relaxed line height
  - Small (Labels/Metadados): Inter Regular/14px/tight line height

## Animations

Animações sutis e funcionais que melhoram a experiência sem distrair do trabalho, com transições suaves entre módulos e feedback visual para ações importantes.

- **Purposeful Meaning**: Micro-interações que confirmam ações críticas como salvamento e validações, com movimento que guia o olhar para informações importantes
- **Hierarchy of Movement**: Navegação entre módulos com transições suaves, loading states para operações pesadas, hover effects em elementos interativos

## Component Selection

- **Components**: Sidebar para navegação principal, Cards para métricas do dashboard, Tables para listagens de dados, Forms para cadastros, Dialogs para confirmações críticas, Charts (Recharts) para visualizações
- **Customizations**: Componentes de métrica personalizados, tabelas com filtros avançados, sidebar colapsível adaptativa
- **States**: Botões com estados loading para operações assíncronas, inputs com validação inline, tabelas com estados empty, loading e error
- **Icon Selection**: Phosphor icons para consistência - Calculator para contabilidade, Users para clientes, ChartBar para relatórios, Gear para configurações
- **Spacing**: Sistema baseado em 8px (space-2, space-4, space-6) para consistência visual
- **Mobile**: Sidebar colapsível em hamburguer menu, cards empilhados verticalmente, tabelas com scroll horizontal, formulários simplificados
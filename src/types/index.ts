// User management types
export interface User {
  id: string
  username: string
  name: string
  email: string
  role: UserRole
  permissions: Permission[]
  isActive: boolean
  createdAt: string
  lastLogin?: string
  createdBy?: string
}

export type UserRole = 
  | 'admin'       // Elvio - controle total
  | 'fiscal'      // Acesso módulos fiscais
  | 'financeiro'  // Acesso módulos financeiros
  | 'contabil'    // Acesso contabilidade
  | 'rh'          // Acesso recursos humanos
  | 'gerencial'   // Acesso relatórios gerenciais
  | 'recepcao'    // Acesso recepção e clientes
  | 'readonly'    // Apenas leitura

export type Permission = 
  | 'users.create'
  | 'users.edit'
  | 'users.delete'
  | 'users.view'
  | 'dashboard.view'
  | 'clientes.view'
  | 'clientes.edit'
  | 'contabilidade.view'
  | 'contabilidade.edit'
  | 'financas.view'
  | 'financas.edit'
  | 'fiscal.view'
  | 'fiscal.edit'
  | 'rh.view'
  | 'rh.edit'
  | 'gerencial.view'
  | 'gerencial.edit'
  | 'processos.view'
  | 'processos.edit'
  | 'recepcao.view'
  | 'recepcao.edit'
  | 'cadastro.view'
  | 'cadastro.edit'
  | 'aprendizado.view'
  | 'geral.view'
  | 'geral.edit'

// Real-time dashboard types
export interface DashboardMetrics {
  totalClientes: number
  clientesAtivos: number
  documentosPendentes: number
  vencimentosProximos: number
  tarefasPendentes: number
  alertasImportantes: number
  lastUpdated: string
}

export interface RealtimeUpdate {
  id: string
  type: 'client_added' | 'document_updated' | 'task_completed' | 'alert_created'
  title: string
  description: string
  timestamp: string
  userId: string
  userName: string
}

// Module types
export type ModuleType = 
  | 'dashboard' 
  | 'clientes' 
  | 'contabilidade' 
  | 'financas' 
  | 'fiscal' 
  | 'rh' 
  | 'geral' 
  | 'gerencial' 
  | 'processos' 
  | 'recepcao' 
  | 'aprendizado'
  | 'cadastro'
  | 'admin' // Admin panel for user management

// Role permissions mapping
export const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  admin: [
    'users.create', 'users.edit', 'users.delete', 'users.view',
    'dashboard.view', 'clientes.view', 'clientes.edit',
    'contabilidade.view', 'contabilidade.edit',
    'financas.view', 'financas.edit',
    'fiscal.view', 'fiscal.edit',
    'rh.view', 'rh.edit',
    'gerencial.view', 'gerencial.edit',
    'processos.view', 'processos.edit',
    'recepcao.view', 'recepcao.edit',
    'cadastro.view', 'cadastro.edit',
    'aprendizado.view',
    'geral.view', 'geral.edit'
  ],
  fiscal: [
    'dashboard.view', 'fiscal.view', 'fiscal.edit',
    'clientes.view', 'cadastro.view', 'cadastro.edit'
  ],
  financeiro: [
    'dashboard.view', 'financas.view', 'financas.edit',
    'clientes.view', 'cadastro.view', 'gerencial.view'
  ],
  contabil: [
    'dashboard.view', 'contabilidade.view', 'contabilidade.edit',
    'clientes.view', 'cadastro.view', 'cadastro.edit'
  ],
  rh: [
    'dashboard.view', 'rh.view', 'rh.edit',
    'clientes.view'
  ],
  gerencial: [
    'dashboard.view', 'gerencial.view', 'gerencial.edit',
    'clientes.view', 'financas.view', 'fiscal.view', 'contabilidade.view'
  ],
  recepcao: [
    'dashboard.view', 'recepcao.view', 'recepcao.edit',
    'clientes.view', 'clientes.edit', 'cadastro.view'
  ],
  readonly: [
    'dashboard.view', 'clientes.view', 'aprendizado.view'
  ]
}

// Module permissions mapping
export const MODULE_PERMISSIONS: Record<ModuleType, Permission> = {
  dashboard: 'dashboard.view',
  clientes: 'clientes.view',
  contabilidade: 'contabilidade.view',
  financas: 'financas.view',
  fiscal: 'fiscal.view',
  rh: 'rh.view',
  geral: 'geral.view',
  gerencial: 'gerencial.view',
  processos: 'processos.view',
  recepcao: 'recepcao.view',
  aprendizado: 'aprendizado.view',
  cadastro: 'cadastro.view',
  admin: 'users.view'
}
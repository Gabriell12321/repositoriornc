import { useState } from 'react'
import Sidebar from './Sidebar'
import DashboardHome from './DashboardHome'
import ModuleClientes from './modules/ModuleClientes'
import ModuleContabilidade from './modules/ModuleContabilidade'
import ModuleFinancas from './modules/ModuleFinancas'
import ModuleFiscal from './modules/ModuleFiscal'
import ModuleRH from './modules/ModuleRH'
import ModuleGeral from './modules/ModuleGeral'
import ModuleGerencial from './modules/ModuleGerencial'
import ModuleProcessos from './modules/ModuleProcessos'
import ModuleRecepcao from './modules/ModuleRecepcao'
import ModuleAprendizado from './modules/ModuleAprendizado'
import ModuleCadastro from './modules/ModuleCadastro'

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

interface DashboardProps {
  user: {name: string, role: string}
  onLogout: () => void
}

export default function Dashboard({ user, onLogout }: DashboardProps) {
  const [activeModule, setActiveModule] = useState<ModuleType>('dashboard')

  const renderModule = () => {
    switch (activeModule) {
      case 'dashboard':
        return <DashboardHome />
      case 'clientes':
        return <ModuleClientes />
      case 'contabilidade':
        return <ModuleContabilidade />
      case 'financas':
        return <ModuleFinancas />
      case 'fiscal':
        return <ModuleFiscal />
      case 'rh':
        return <ModuleRH />
      case 'geral':
        return <ModuleGeral />
      case 'gerencial':
        return <ModuleGerencial />
      case 'processos':
        return <ModuleProcessos />
      case 'recepcao':
        return <ModuleRecepcao />
      case 'aprendizado':
        return <ModuleAprendizado />
      case 'cadastro':
        return <ModuleCadastro />
      default:
        return <DashboardHome />
    }
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar 
        activeModule={activeModule}
        onModuleChange={setActiveModule}
        user={user}
        onLogout={onLogout}
      />
      <main className="flex-1 overflow-auto">
        {renderModule()}
      </main>
    </div>
  )
}
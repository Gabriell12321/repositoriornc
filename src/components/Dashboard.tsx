import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
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

  const handleModuleChange = (module: ModuleType) => {
    setActiveModule(module)
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-background via-background to-muted/20">
      <Sidebar 
        activeModule={activeModule}
        onModuleChange={handleModuleChange}
        user={user}
        onLogout={onLogout}
      />
      <main className="flex-1 overflow-auto">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeModule}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ 
              duration: 0.4,
              ease: [0.25, 0.46, 0.45, 0.94]
            }}
            className="h-full"
          >
            {renderModule()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  )
}
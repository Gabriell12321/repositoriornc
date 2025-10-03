import { ModuleType } from './Dashboard'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { 
  Building, 
  ChartBar, 
  Users, 
  Calculator, 
  CurrencyDollar, 
  FileText, 
  Gear, 
  PresentationChart, 
  GitBranch, 
  Phone, 
  UserList, 
  GraduationCap,
  SignOut
} from '@phosphor-icons/react'

interface SidebarProps {
  activeModule: ModuleType
  onModuleChange: (module: ModuleType) => void
  user: {name: string, role: string}
  onLogout: () => void
}

const menuItems = [
  { id: 'dashboard' as ModuleType, label: 'Dashboard', icon: ChartBar },
  { id: 'cadastro' as ModuleType, label: 'Cadastro', icon: UserList },
  { id: 'clientes' as ModuleType, label: 'Clientes', icon: Users },
  { id: 'contabilidade' as ModuleType, label: 'Contabilidade', icon: Calculator },
  { id: 'financas' as ModuleType, label: 'Finanças', icon: CurrencyDollar },
  { id: 'fiscal' as ModuleType, label: 'Fiscal', icon: FileText },
  { id: 'geral' as ModuleType, label: 'Geral', icon: Gear },
  { id: 'gerencial' as ModuleType, label: 'Gerencial', icon: PresentationChart },
  { id: 'processos' as ModuleType, label: 'Processos Internos', icon: GitBranch },
  { id: 'recepcao' as ModuleType, label: 'Recepção', icon: Phone },
  { id: 'rh' as ModuleType, label: 'Recursos Humanos', icon: Users },
  { id: 'aprendizado' as ModuleType, label: 'Aprendizado e Crescimento', icon: GraduationCap },
]

export default function Sidebar({ activeModule, onModuleChange, user, onLogout }: SidebarProps) {
  return (
    <motion.div 
      className="w-64 bg-gradient-to-b from-card via-card to-muted/10 backdrop-blur-sm border-r border-border/50 flex flex-col shadow-xl"
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }}
    >
      {/* Header */}
      <motion.div 
        className="p-6 border-b border-border/30"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <div className="flex items-center space-x-3">
          <motion.div 
            className="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-xl flex items-center justify-center shadow-lg"
            whileHover={{ scale: 1.05, rotate: 5 }}
            whileTap={{ scale: 0.95 }}
          >
            <Building size={26} className="text-primary-foreground" />
          </motion.div>
          <div>
            <h1 className="font-bold text-xl text-foreground bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">4M</h1>
            <p className="text-sm text-muted-foreground font-medium">Contabilidade</p>
          </div>
        </div>
      </motion.div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item, index) => {
          const Icon = item.icon
          const isActive = activeModule === item.id
          return (
            <motion.div
              key={item.id}
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.3, delay: 0.1 + index * 0.05 }}
            >
              <motion.div
                whileHover={{ x: 4 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  variant={isActive ? "default" : "ghost"}
                  className={`w-full justify-start text-left h-11 transition-all duration-300 group ${
                    isActive 
                      ? 'bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-lg transform scale-[1.02]' 
                      : 'text-foreground hover:bg-secondary/70 hover:shadow-sm hover:transform hover:scale-[1.01]'
                  }`}
                  onClick={() => onModuleChange(item.id)}
                >
                  <motion.div
                    animate={isActive ? { scale: 1.1 } : { scale: 1 }}
                    transition={{ duration: 0.3 }}
                    className="group-hover:scale-110 transition-transform duration-200"
                  >
                    <Icon size={20} className="mr-3" />
                  </motion.div>
                  <span className="text-sm font-medium">{item.label}</span>
                </Button>
              </motion.div>
            </motion.div>
          )
        })}
      </nav>

      {/* User Profile */}
      <motion.div 
        className="p-4 border-t border-border"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <motion.div 
          className="flex items-center space-x-3 mb-3"
          whileHover={{ scale: 1.02 }}
        >
          <Avatar className="h-8 w-8">
            <AvatarFallback className="bg-primary text-primary-foreground text-sm">
              {user.name.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-foreground truncate">{user.name}</p>
            <p className="text-xs text-muted-foreground truncate">{user.role}</p>
          </div>
        </motion.div>
        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Button 
            variant="outline" 
            size="sm" 
            className="w-full transition-all duration-200"
            onClick={onLogout}
          >
            <SignOut size={16} className="mr-2" />
            Sair
          </Button>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
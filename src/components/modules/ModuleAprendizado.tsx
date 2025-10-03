import { useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Users, BookOpen, ChartLineUp } from '@phosphor-icons/react'

type SubmoduleType = 'cursos-colaboradores' | 'cursos-treinamentos' | 'situacao-treinamentos'

export default function ModuleAprendizado() {
  const [activeSubmodule, setActiveSubmodule] = useState<SubmoduleType | null>(null)

  const submodules = [
    {
      id: 'cursos-colaboradores' as SubmoduleType,
      title: 'Cursos Colaboradores',
      description: 'Gestão de cursos por colaborador',
      icon: Users,
      color: 'bg-blue-50 text-blue-600'
    },
    {
      id: 'cursos-treinamentos' as SubmoduleType,
      title: 'Cursos e Treinamentos',
      description: 'Catálogo de cursos e treinamentos',
      icon: BookOpen,
      color: 'bg-green-50 text-green-600'
    },
    {
      id: 'situacao-treinamentos' as SubmoduleType,
      title: 'Situação de Treinamentos',
      description: 'Status e progresso dos treinamentos',
      icon: ChartLineUp,
      color: 'bg-purple-50 text-purple-600'
    }
  ]

  const renderSubmoduleContent = (submodule: SubmoduleType) => {
    const content = {
      'cursos-colaboradores': {
        title: 'Cursos Colaboradores',
        description: 'Gerencie os cursos atribuídos a cada colaborador, acompanhe o progresso individual e mantenha o histórico de capacitações da equipe.'
      },
      'cursos-treinamentos': {
        title: 'Cursos e Treinamentos',
        description: 'Catálogo completo de cursos e treinamentos disponíveis, com descrições, objetivos e requisitos para cada programa de capacitação.'
      },
      'situacao-treinamentos': {
        title: 'Situação de Treinamentos',
        description: 'Acompanhe o status geral dos treinamentos, visualize métricas de conclusão e identifique oportunidades de melhoria no programa de capacitação.'
      }
    }

    const currentContent = content[submodule]

    return (
      <motion.div 
        className="space-y-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h2 className="text-2xl font-semibold text-foreground">{currentContent.title}</h2>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <Card>
            <CardContent className="p-6">
              <p className="text-muted-foreground">
                {currentContent.description}
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    )
  }

  if (activeSubmodule) {
    return (
      <motion.div 
        className="p-6 space-y-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <motion.div 
          className="flex items-center space-x-4"
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.4 }}
        >
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button
              variant="outline"
              onClick={() => setActiveSubmodule(null)}
              className="text-muted-foreground hover:text-foreground transition-colors duration-200"
            >
              ← Voltar
            </Button>
          </motion.div>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Aprendizado e Crescimento</h1>
            <p className="text-muted-foreground">Desenvolvimento e capacitação da equipe</p>
          </div>
        </motion.div>
        
        {renderSubmoduleContent(activeSubmodule)}
      </motion.div>
    )
  }

  return (
    <motion.div 
      className="p-6 space-y-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="text-3xl font-bold text-foreground">Aprendizado e Crescimento</h1>
        <p className="text-muted-foreground">Desenvolvimento e capacitação da equipe</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {submodules.map((submodule, index) => {
          const Icon = submodule.icon
          return (
            <motion.div
              key={submodule.id}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ 
                duration: 0.4, 
                delay: 0.1 + index * 0.1,
                ease: "easeOut"
              }}
            >
              <motion.div
                whileHover={{ 
                  scale: 1.02,
                  y: -5,
                  transition: { duration: 0.2 }
                }}
                whileTap={{ scale: 0.98 }}
              >
                <Card 
                  className="cursor-pointer hover:shadow-lg transition-all duration-300 border-2 hover:border-primary/20"
                  onClick={() => setActiveSubmodule(submodule.id)}
                >
                  <CardHeader>
                    <div className="flex items-center space-x-3">
                      <motion.div 
                        className={`p-2 rounded-lg ${submodule.color}`}
                        whileHover={{ rotate: 5, scale: 1.1 }}
                        transition={{ duration: 0.2 }}
                      >
                        <Icon size={24} />
                      </motion.div>
                      <div>
                        <CardTitle className="text-lg">{submodule.title}</CardTitle>
                        <CardDescription>{submodule.description}</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <motion.div
                      whileHover={{ x: 5 }}
                      transition={{ duration: 0.2 }}
                    >
                      <Button variant="ghost" className="w-full justify-start text-muted-foreground hover:text-foreground transition-colors duration-200">
                        Acessar módulo →
                      </Button>
                    </motion.div>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          )
        })}
      </div>
    </motion.div>
  )
}
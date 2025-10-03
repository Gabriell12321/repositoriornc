import { useState } from 'react'
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
    switch (submodule) {
      case 'cursos-colaboradores':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Cursos Colaboradores</h2>
            <Card>
              <CardContent className="p-6">
                <p className="text-muted-foreground">
                  Gerencie os cursos atribuídos a cada colaborador, acompanhe o progresso individual
                  e mantenha o histórico de capacitações da equipe.
                </p>
              </CardContent>
            </Card>
          </div>
        )
      
      case 'cursos-treinamentos':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Cursos e Treinamentos</h2>
            <Card>
              <CardContent className="p-6">
                <p className="text-muted-foreground">
                  Catálogo completo de cursos e treinamentos disponíveis, com descrições,
                  objetivos e requisitos para cada programa de capacitação.
                </p>
              </CardContent>
            </Card>
          </div>
        )
      
      case 'situacao-treinamentos':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Situação de Treinamentos</h2>
            <Card>
              <CardContent className="p-6">
                <p className="text-muted-foreground">
                  Acompanhe o status geral dos treinamentos, visualize métricas de conclusão
                  e identifique oportunidades de melhoria no programa de capacitação.
                </p>
              </CardContent>
            </Card>
          </div>
        )
      
      default:
        return null
    }
  }

  if (activeSubmodule) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            onClick={() => setActiveSubmodule(null)}
            className="text-muted-foreground hover:text-foreground"
          >
            ← Voltar
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Aprendizado e Crescimento</h1>
            <p className="text-muted-foreground">Desenvolvimento e capacitação da equipe</p>
          </div>
        </div>
        
        {renderSubmoduleContent(activeSubmodule)}
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Aprendizado e Crescimento</h1>
        <p className="text-muted-foreground">Desenvolvimento e capacitação da equipe</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {submodules.map((submodule) => {
          const Icon = submodule.icon
          return (
            <Card 
              key={submodule.id}
              className="cursor-pointer hover:shadow-md transition-shadow duration-200"
              onClick={() => setActiveSubmodule(submodule.id)}
            >
              <CardHeader>
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${submodule.color}`}>
                    <Icon size={24} />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{submodule.title}</CardTitle>
                    <CardDescription>{submodule.description}</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Button variant="ghost" className="w-full justify-start text-muted-foreground hover:text-foreground">
                  Acessar módulo →
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
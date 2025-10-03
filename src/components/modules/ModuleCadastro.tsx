import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  Users, 
  Fire, 
  Receipt, 
  ChartBar, 
  Storefront, 
  MapPin, 
  Plant, 
  Calculator, 
  UserCheck 
} from '@phosphor-icons/react'

type SubmoduleType = 'doc-associacao' | 'doc-bombeiro' | 'doc-lucro-presumido' | 'doc-lucro-real' | 'doc-mei' | 'doc-prefeitura' | 'doc-rural' | 'doc-simples' | 'situacao-clientes'

export default function ModuleCadastro() {
  const [activeSubmodule, setActiveSubmodule] = useState<SubmoduleType | null>(null)

  const submodules = [
    {
      id: 'doc-associacao' as SubmoduleType,
      title: 'Documentação Associação',
      description: 'Documentos de associações e entidades',
      icon: Users,
      color: 'bg-blue-50 text-blue-600'
    },
    {
      id: 'doc-bombeiro' as SubmoduleType,
      title: 'Documentação Bombeiro',
      description: 'Auto de vistoria do corpo de bombeiros',
      icon: Fire,
      color: 'bg-red-50 text-red-600'
    },
    {
      id: 'doc-lucro-presumido' as SubmoduleType,
      title: 'Documentação Lucro Presumido',
      description: 'Documentos para empresas do lucro presumido',
      icon: Receipt,
      color: 'bg-green-50 text-green-600'
    },
    {
      id: 'doc-lucro-real' as SubmoduleType,
      title: 'Documentação Lucro Real',
      description: 'Documentos para empresas do lucro real',
      icon: ChartBar,
      color: 'bg-purple-50 text-purple-600'
    },
    {
      id: 'doc-mei' as SubmoduleType,
      title: 'Documentação MEI',
      description: 'Documentos para microempreendedores',
      icon: Storefront,
      color: 'bg-orange-50 text-orange-600'
    },
    {
      id: 'doc-prefeitura' as SubmoduleType,
      title: 'Documentação Prefeitura',
      description: 'Documentos municipais e licenças',
      icon: MapPin,
      color: 'bg-indigo-50 text-indigo-600'
    },
    {
      id: 'doc-rural' as SubmoduleType,
      title: 'Documentação Rural',
      description: 'Documentos para produtores rurais',
      icon: Plant,
      color: 'bg-emerald-50 text-emerald-600'
    },
    {
      id: 'doc-simples' as SubmoduleType,
      title: 'Documentação Simples',
      description: 'Documentos para empresas do Simples Nacional',
      icon: Calculator,
      color: 'bg-cyan-50 text-cyan-600'
    },
    {
      id: 'situacao-clientes' as SubmoduleType,
      title: 'Situação de Clientes',
      description: 'Status e situação dos clientes',
      icon: UserCheck,
      color: 'bg-pink-50 text-pink-600'
    }
  ]

  const renderSubmoduleContent = (submodule: SubmoduleType) => {
    switch (submodule) {
      case 'doc-associacao':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Documentação Associação</h2>
            <Card>
              <CardContent className="p-6">
                <p className="text-muted-foreground">
                  Gerencie documentos específicos para associações, fundações e outras entidades 
                  do terceiro setor, incluindo estatutos, atas e documentos de constituição.
                </p>
              </CardContent>
            </Card>
          </div>
        )
      
      case 'doc-bombeiro':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Documentação Bombeiro</h2>
            <Card>
              <CardContent className="p-6">
                <p className="text-muted-foreground">
                  Controle de autos de vistoria do corpo de bombeiros, certificados de segurança 
                  e documentos relacionados à prevenção de incêndios.
                </p>
              </CardContent>
            </Card>
          </div>
        )
      
      case 'doc-lucro-presumido':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Documentação Lucro Presumido</h2>
            <Card>
              <CardContent className="p-6">
                <p className="text-muted-foreground">
                  Documentos específicos para empresas optantes pelo regime de tributação 
                  Lucro Presumido, incluindo declarações e comprovantes fiscais.
                </p>
              </CardContent>
            </Card>
          </div>
        )
      
      case 'doc-lucro-real':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Documentação Lucro Real</h2>
            <Card>
              <CardContent className="p-6">
                <p className="text-muted-foreground">
                  Gestão de documentos para empresas do Lucro Real, incluindo livros contábeis, 
                  balanços e demonstrativos financeiros obrigatórios.
                </p>
              </CardContent>
            </Card>
          </div>
        )
      
      case 'doc-mei':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Documentação MEI</h2>
            <Card>
              <CardContent className="p-6">
                <p className="text-muted-foreground">
                  Documentos para microempreendedores individuais, incluindo CCMEI, 
                  relatórios mensais e declarações anuais.
                </p>
              </CardContent>
            </Card>
          </div>
        )
      
      case 'doc-prefeitura':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Documentação Prefeitura</h2>
            <Card>
              <CardContent className="p-6">
                <p className="text-muted-foreground">
                  Controle de documentos municipais, alvarás de funcionamento, licenças 
                  e autorizações expedidas pela prefeitura.
                </p>
              </CardContent>
            </Card>
          </div>
        )
      
      case 'doc-rural':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Documentação Rural</h2>
            <Card>
              <CardContent className="p-6">
                <p className="text-muted-foreground">
                  Documentos específicos para produtores rurais, incluindo ITR, 
                  CCIR e documentos do INCRA.
                </p>
              </CardContent>
            </Card>
          </div>
        )
      
      case 'doc-simples':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Documentação Simples</h2>
            <Card>
              <CardContent className="p-6">
                <p className="text-muted-foreground">
                  Gestão de documentos para empresas optantes pelo Simples Nacional, 
                  incluindo DAS e relatórios de faturamento.
                </p>
              </CardContent>
            </Card>
          </div>
        )
      
      case 'situacao-clientes':
        return (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Situação de Clientes</h2>
            <Card>
              <CardContent className="p-6">
                <p className="text-muted-foreground">
                  Acompanhe o status geral dos clientes, pendências documentais, 
                  situação fiscal e compliance regulatório.
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
            <h1 className="text-3xl font-bold text-foreground">Cadastro</h1>
            <p className="text-muted-foreground">Cadastros básicos do sistema</p>
          </div>
        </div>
        
        {renderSubmoduleContent(activeSubmodule)}
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Cadastro</h1>
        <p className="text-muted-foreground">Cadastros básicos do sistema</p>
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
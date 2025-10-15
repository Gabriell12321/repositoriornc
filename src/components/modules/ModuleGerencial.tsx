import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Building, Gear, Users, Clipboard } from '@phosphor-icons/react'

export default function ModuleGerencial() {
  return (
    <div className="p-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Gerencial</h1>
        <p className="text-muted-foreground">Relatórios e análises gerenciais</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Relatórios Financeiros</CardTitle>
            <CardDescription>Análises financeiras</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Relatórios de desempenho financeiro</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Dashboard Executivo</CardTitle>
            <CardDescription>Visão estratégica</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Indicadores para tomada de decisão</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Análise de Tendências</CardTitle>
            <CardDescription>Projeções e cenários</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Análise preditiva de dados</p>
          </CardContent>
        </Card>
      </div>

      {/* Seção de Melhorias */}
      <div className="mt-12">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-foreground mb-2">Melhorias</h2>
          <p className="text-muted-foreground">Gestão de melhorias organizacionais</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Building className="text-primary" size={24} />
                </div>
                <div>
                  <CardTitle>Melhorias Estrutura</CardTitle>
                  <CardDescription>Melhorias na estrutura organizacional</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Gestão de melhorias na estrutura física, organizacional e infraestrutura
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Gear className="text-primary" size={24} />
                </div>
                <div>
                  <CardTitle>Melhorias Funcionalidade</CardTitle>
                  <CardDescription>Melhorias funcionais e operacionais</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Otimização de funcionalidades, processos e sistemas operacionais
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Users className="text-primary" size={24} />
                </div>
                <div>
                  <CardTitle>Melhorias Setor</CardTitle>
                  <CardDescription>Melhorias específicas por setor</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Melhorias direcionadas para setores específicos da empresa
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Clipboard className="text-primary" size={24} />
                </div>
                <div>
                  <CardTitle>Plano de Melhorias</CardTitle>
                  <CardDescription>Planejamento estratégico de melhorias</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Planejamento, acompanhamento e controle de planos de melhorias
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
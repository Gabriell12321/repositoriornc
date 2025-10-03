import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ModuleGerencial() {
  return (
    <div className="p-6 space-y-6">
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
    </div>
  )
}
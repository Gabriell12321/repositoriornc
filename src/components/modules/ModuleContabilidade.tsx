import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ModuleContabilidade() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Contabilidade</h1>
        <p className="text-muted-foreground">Gestão completa de operações contábeis</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Plano de Contas</CardTitle>
            <CardDescription>Estrutura contábil da empresa</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Configure e gerencie o plano de contas</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Lançamentos</CardTitle>
            <CardDescription>Registros contábeis</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Efetue lançamentos contábeis</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Balancetes</CardTitle>
            <CardDescription>Relatórios contábeis</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Gere balancetes e demonstrativos</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
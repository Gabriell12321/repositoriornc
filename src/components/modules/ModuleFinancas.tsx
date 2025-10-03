import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ModuleFinancas() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Finanças</h1>
        <p className="text-muted-foreground">Controle financeiro e fluxo de caixa</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Fluxo de Caixa</CardTitle>
            <CardDescription>Controle de entradas e saídas</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Acompanhe o movimento financeiro</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Contas a Pagar</CardTitle>
            <CardDescription>Obrigações financeiras</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Gerencie pagamentos pendentes</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Contas a Receber</CardTitle>
            <CardDescription>Valores a receber</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Controle de recebimentos</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
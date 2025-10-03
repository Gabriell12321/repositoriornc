import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ModuleFiscal() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Fiscal</h1>
        <p className="text-muted-foreground">Gestão de obrigações fiscais e tributárias</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Declarações</CardTitle>
            <CardDescription>Declarações fiscais</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Prepare e envie declarações</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Apuração de Impostos</CardTitle>
            <CardDescription>Cálculo tributário</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Calcule impostos devidos</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Obrigações Acessórias</CardTitle>
            <CardDescription>Entregas obrigatórias</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Acompanhe prazos e entregas</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
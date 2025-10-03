import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ModuleRH() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Recursos Humanos</h1>
        <p className="text-muted-foreground">Gestão de pessoas e folha de pagamento</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Funcionários</CardTitle>
            <CardDescription>Cadastro de funcionários</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Gerencie dados dos funcionários</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Folha de Pagamento</CardTitle>
            <CardDescription>Processamento da folha</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Calcule salários e encargos</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Obrigações Trabalhistas</CardTitle>
            <CardDescription>eSocial e outras obrigações</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Cumpra obrigações trabalhistas</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
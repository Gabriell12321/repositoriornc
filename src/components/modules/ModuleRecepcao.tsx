import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ModuleRecepcao() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Recepção</h1>
        <p className="text-muted-foreground">Atendimento e relacionamento com clientes</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Agenda</CardTitle>
            <CardDescription>Agendamento de reuniões</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Gerencie agenda de atendimentos</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Chamados</CardTitle>
            <CardDescription>Suporte ao cliente</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Registre e acompanhe solicitações</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>CRM</CardTitle>
            <CardDescription>Relacionamento com clientes</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Fortaleça relacionamentos</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
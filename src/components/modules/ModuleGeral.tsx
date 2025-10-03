import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ModuleGeral() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Geral</h1>
        <p className="text-muted-foreground">Configurações e operações gerais do sistema</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Configurações</CardTitle>
            <CardDescription>Configurações do sistema</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Configure parâmetros gerais</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Backup</CardTitle>
            <CardDescription>Backup de dados</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Gerencie backups do sistema</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Usuários</CardTitle>
            <CardDescription>Gestão de usuários</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Controle acesso ao sistema</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
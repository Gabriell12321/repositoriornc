import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ModuleAprendizado() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Aprendizado e Crescimento</h1>
        <p className="text-muted-foreground">Desenvolvimento e capacitação da equipe</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Treinamentos</CardTitle>
            <CardDescription>Capacitação da equipe</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Organize programas de treinamento</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Certificações</CardTitle>
            <CardDescription>Qualificações profissionais</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Acompanhe certificações da equipe</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Base de Conhecimento</CardTitle>
            <CardDescription>Documentação e manuais</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Centralize conhecimento da empresa</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
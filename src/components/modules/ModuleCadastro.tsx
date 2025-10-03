import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ModuleCadastro() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Cadastro</h1>
        <p className="text-muted-foreground">Cadastros básicos do sistema</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Empresas</CardTitle>
            <CardDescription>Cadastro de empresas</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Registre dados das empresas</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Fornecedores</CardTitle>
            <CardDescription>Cadastro de fornecedores</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Gerencie fornecedores</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Produtos/Serviços</CardTitle>
            <CardDescription>Catálogo de ofertas</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Cadastre produtos e serviços</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
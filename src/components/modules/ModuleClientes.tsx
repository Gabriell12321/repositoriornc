import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  MagnifyingGlass, 
  Plus, 
  Eye, 
  PencilSimple, 
  Trash,
  Users,
  PresentationChart,
  FileText,
  Table as TableIcon,
  Calculator,
  Buildings
} from '@phosphor-icons/react'
import { useKV } from '@github/spark/hooks'

interface Cliente {
  id: string
  nome: string
  cnpj: string
  email: string
  telefone: string
  status: 'ativo' | 'inativo'
  servicos: string[]
}

// Component for Presentations section
function ApresentacoesSection() {
  const presentations = [
    'Apresentação Associação',
    'Apresentação do MEI',
    'Apresentação do Simples Nacional',
    'Apresentação Escritório',
    'Apresentação Lucro Presumido',
    'Apresentação Lucro Real',
    'Apresentação Rural'
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {presentations.map((presentation, index) => (
        <Card key={index} className="hover:shadow-md transition-shadow cursor-pointer">
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <PresentationChart size={20} className="text-primary" />
              </div>
              <CardTitle className="text-sm">{presentation}</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-3">
              Material de apresentação para clientes
            </p>
            <div className="flex gap-2">
              <Button size="sm" variant="outline">
                <Eye size={14} className="mr-1" />
                Ver
              </Button>
              <Button size="sm" variant="outline">
                <FileText size={14} className="mr-1" />
                Download
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// Component for Documents section
function DocumentosSection() {
  const documents = [
    'Certidões Negativas',
    'Planilha Documentos Faltantes',
    'Planilha Fisco Contábil'
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {documents.map((document, index) => (
        <Card key={index} className="hover:shadow-md transition-shadow cursor-pointer">
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                <FileText size={20} className="text-accent" />
              </div>
              <CardTitle className="text-sm">{document}</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-3">
              Documentação e controles necessários
            </p>
            <div className="flex gap-2">
              <Button size="sm" variant="outline">
                <Eye size={14} className="mr-1" />
                Abrir
              </Button>
              <Button size="sm" variant="outline">
                <PencilSimple size={14} className="mr-1" />
                Editar
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// Component for Tables section
function TabelasSection() {
  const tables = [
    'Tabela Controle de Férias',
    'Tabela Recursos Humanos',
    'Tabela Simples Nacional'
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {tables.map((table, index) => (
        <Card key={index} className="hover:shadow-md transition-shadow cursor-pointer">
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-secondary/20 rounded-lg flex items-center justify-center">
                <TableIcon size={20} className="text-secondary-foreground" />
              </div>
              <CardTitle className="text-sm">{table}</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-3">
              Tabela de controle e gestão
            </p>
            <div className="flex gap-2">
              <Button size="sm" variant="outline">
                <Eye size={14} className="mr-1" />
                Ver
              </Button>
              <Button size="sm" variant="outline">
                <PencilSimple size={14} className="mr-1" />
                Editar
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// Component for Taxation section
function TributacaoSection() {
  const taxation = [
    'Tributação Lucro Presumido',
    'Tributação Lucro Real', 
    'Tributação MEI',
    'Tributação Simples Nacional'
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {taxation.map((tax, index) => (
        <Card key={index} className="hover:shadow-md transition-shadow cursor-pointer">
          <CardHeader className="pb-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-chart-1/10 rounded-lg flex items-center justify-center">
                <Calculator size={20} className="text-chart-1" />
              </div>
              <CardTitle className="text-sm">{tax}</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-3">
              Informações sobre tributação
            </p>
            <div className="flex gap-2">
              <Button size="sm" variant="outline">
                <Eye size={14} className="mr-1" />
                Ver
              </Button>
              <Button size="sm" variant="outline">
                <Calculator size={14} className="mr-1" />
                Calcular
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

export default function ModuleClientes() {
  const [clientes, setClientes] = useKV<Cliente[]>('clientes', [])
  const [searchTerm, setSearchTerm] = useState('')

  const filteredClientes = (clientes || []).filter(cliente =>
    cliente.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    cliente.cnpj.includes(searchTerm) ||
    cliente.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Clientes</h1>
          <p className="text-muted-foreground">Gerencie clientes e recursos relacionados</p>
        </div>
        <Button>
          <Plus size={20} className="mr-2" />
          Novo Cliente
        </Button>
      </div>

      <Tabs defaultValue="listagem" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="listagem">
            <Users size={16} className="mr-2" />
            Listagem
          </TabsTrigger>
          <TabsTrigger value="apresentacoes">
            <PresentationChart size={16} className="mr-2" />
            Apresentações
          </TabsTrigger>
          <TabsTrigger value="documentos">
            <FileText size={16} className="mr-2" />
            Documentos
          </TabsTrigger>
          <TabsTrigger value="tabelas">
            <TableIcon size={16} className="mr-2" />
            Tabelas
          </TabsTrigger>
          <TabsTrigger value="tributacao">
            <Calculator size={16} className="mr-2" />
            Tributação
          </TabsTrigger>
        </TabsList>

        <TabsContent value="listagem" className="space-y-6">
          {/* Search */}
          <Card>
            <CardContent className="pt-6">
              <div className="relative">
                <MagnifyingGlass className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por nome, CNPJ ou email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </CardContent>
          </Card>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Total de Clientes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-primary">{(clientes || []).length}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Clientes Ativos</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">
                  {(clientes || []).filter(c => c.status === 'ativo').length}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Novos este Mês</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-accent">12</div>
              </CardContent>
            </Card>
          </div>

          {/* Client Table */}
          <Card>
            <CardHeader>
              <CardTitle>Lista de Clientes</CardTitle>
              <CardDescription>
                {filteredClientes.length} cliente(s) encontrado(s)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nome</TableHead>
                    <TableHead>CNPJ</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Serviços</TableHead>
                    <TableHead className="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredClientes.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                        Nenhum cliente encontrado
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredClientes.map((cliente) => (
                      <TableRow key={cliente.id}>
                        <TableCell className="font-medium">{cliente.nome}</TableCell>
                        <TableCell>{cliente.cnpj}</TableCell>
                        <TableCell>{cliente.email}</TableCell>
                        <TableCell>
                          <Badge variant={cliente.status === 'ativo' ? 'default' : 'secondary'}>
                            {cliente.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1 flex-wrap">
                            {cliente.servicos.map((servico, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {servico}
                              </Badge>
                            ))}
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button variant="ghost" size="sm">
                              <Eye size={16} />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <PencilSimple size={16} />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Trash size={16} />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="apresentacoes" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Apresentações para Clientes</CardTitle>
              <CardDescription>
                Material de apresentação organizado por tipo de cliente
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ApresentacoesSection />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="documentos" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Documentos e Planilhas</CardTitle>
              <CardDescription>
                Documentação necessária e controles de processos
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DocumentosSection />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tabelas" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Tabelas de Controle</CardTitle>
              <CardDescription>
                Tabelas para gestão e controle de processos
              </CardDescription>
            </CardHeader>
            <CardContent>
              <TabelasSection />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tributacao" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Informações de Tributação</CardTitle>
              <CardDescription>
                Recursos e cálculos relacionados à tributação
              </CardDescription>
            </CardHeader>
            <CardContent>
              <TributacaoSection />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
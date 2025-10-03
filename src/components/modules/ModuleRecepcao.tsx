import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useKV } from '@github/spark/hooks'
import { FileText, Warning, Users, Plus, Calendar, PhoneCall, ChatCircle, Eye } from '@phosphor-icons/react'
import { toast } from 'sonner'

interface PendingDocument {
  id: string
  clientName: string
  documentType: string
  dueDate: string
  priority: 'alta' | 'media' | 'baixa'
  status: 'pendente' | 'em_andamento' | 'concluido'
  description?: string
}

interface NewClient {
  id: string
  name: string
  email: string
  phone: string
  company: string
  dateAdded: string
  status: 'novo' | 'em_analise' | 'aprovado' | 'rejeitado'
  notes?: string
}

export default function ModuleRecepcao() {
  const [pendingDocs, setPendingDocs] = useKV<PendingDocument[]>('pending-documents', [
    {
      id: '1',
      clientName: 'João Silva Ltda',
      documentType: 'Declaração de Rendimentos',
      dueDate: '2024-02-15',
      priority: 'alta',
      status: 'pendente',
      description: 'Documentos necessários para fechamento do imposto de renda'
    },
    {
      id: '2',
      clientName: 'Maria Santos ME',
      documentType: 'Notas Fiscais Janeiro',
      dueDate: '2024-02-10',
      priority: 'media',
      status: 'em_andamento',
      description: 'Faltam 3 notas fiscais do período'
    }
  ])

  const [newClients, setNewClients] = useKV<NewClient[]>('new-clients', [
    {
      id: '1',
      name: 'Carlos Eduardo',
      email: 'carlos@empresa.com',
      phone: '(11) 99999-9999',
      company: 'Tech Solutions Ltda',
      dateAdded: '2024-02-01',
      status: 'novo',
      notes: 'Interessado em serviços de contabilidade completa'
    },
    {
      id: '2',
      name: 'Ana Paula',
      email: 'ana@consultoria.com',
      phone: '(11) 88888-8888',
      company: 'Consultoria AP',
      dateAdded: '2024-01-30',
      status: 'em_analise',
      notes: 'Precisa de revisão de documentos societários'
    }
  ])

  const [isDocDialogOpen, setIsDocDialogOpen] = useState(false)
  const [isClientDialogOpen, setIsClientDialogOpen] = useState(false)
  const [selectedDoc, setSelectedDoc] = useState<PendingDocument | null>(null)
  const [selectedClient, setSelectedClient] = useState<NewClient | null>(null)

  const [newDocForm, setNewDocForm] = useState({
    clientName: '',
    documentType: '',
    dueDate: '',
    priority: 'media' as 'alta' | 'media' | 'baixa',
    description: ''
  })

  const [newClientForm, setNewClientForm] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    notes: ''
  })

  const addPendingDocument = () => {
    if (!newDocForm.clientName || !newDocForm.documentType || !newDocForm.dueDate) {
      toast.error('Preencha todos os campos obrigatórios')
      return
    }

    const newDoc: PendingDocument = {
      id: Date.now().toString(),
      ...newDocForm,
      status: 'pendente'
    }

    setPendingDocs(current => [...(current || []), newDoc])
    setNewDocForm({
      clientName: '',
      documentType: '',
      dueDate: '',
      priority: 'media',
      description: ''
    })
    setIsDocDialogOpen(false)
    toast.success('Pendência de documento adicionada')
  }

  const addNewClient = () => {
    if (!newClientForm.name || !newClientForm.email || !newClientForm.phone) {
      toast.error('Preencha todos os campos obrigatórios')
      return
    }

    const client: NewClient = {
      id: Date.now().toString(),
      ...newClientForm,
      dateAdded: new Date().toISOString().split('T')[0],
      status: 'novo'
    }

    setNewClients(current => [...(current || []), client])
    setNewClientForm({
      name: '',
      email: '',
      phone: '',
      company: '',
      notes: ''
    })
    setIsClientDialogOpen(false)
    toast.success('Novo cliente adicionado')
  }

  const updateDocumentStatus = (id: string, status: PendingDocument['status']) => {
    setPendingDocs(current => 
      (current || []).map(doc => doc.id === id ? { ...doc, status } : doc)
    )
    toast.success('Status do documento atualizado')
  }

  const updateClientStatus = (id: string, status: NewClient['status']) => {
    setNewClients(current => 
      (current || []).map(client => client.id === id ? { ...client, status } : client)
    )
    toast.success('Status do cliente atualizado')
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'alta': return 'destructive'
      case 'media': return 'default'
      case 'baixa': return 'secondary'
      default: return 'default'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pendente': return 'destructive'
      case 'em_andamento': return 'default'
      case 'concluido': return 'secondary'
      case 'novo': return 'default'
      case 'em_analise': return 'secondary'
      case 'aprovado': return 'secondary'
      case 'rejeitado': return 'destructive'
      default: return 'default'
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Recepção</h1>
        <p className="text-muted-foreground">Atendimento, documentos e relacionamento com clientes</p>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="documents">Documentos Pendentes</TabsTrigger>
          <TabsTrigger value="clients">Novos Clientes</TabsTrigger>
          <TabsTrigger value="services">Serviços</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Documentos Pendentes</CardTitle>
                <Warning className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-primary">{(pendingDocs || []).filter(d => d.status === 'pendente').length}</div>
                <p className="text-xs text-muted-foreground">
                  {(pendingDocs || []).filter(d => d.priority === 'alta').length} alta prioridade
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Novos Clientes</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-primary">{(newClients || []).filter(c => c.status === 'novo').length}</div>
                <p className="text-xs text-muted-foreground">
                  {(newClients || []).filter(c => c.status === 'em_analise').length} em análise
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Agendamentos Hoje</CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">5</div>
                <p className="text-xs text-muted-foreground">2 reuniões pendentes</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Chamados Abertos</CardTitle>
                <ChatCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">3</div>
                <p className="text-xs text-muted-foreground">1 urgente</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="documents" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Controle de Pendências - Documentos</h2>
            <Dialog open={isDocDialogOpen} onOpenChange={setIsDocDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Nova Pendência
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Adicionar Pendência de Documento</DialogTitle>
                  <DialogDescription>
                    Registre um novo documento pendente para controle.
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="client-name" className="text-right">Cliente</Label>
                    <Input
                      id="client-name"
                      value={newDocForm.clientName}
                      onChange={(e) => setNewDocForm(prev => ({...prev, clientName: e.target.value}))}
                      className="col-span-3"
                      placeholder="Nome do cliente"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="doc-type" className="text-right">Documento</Label>
                    <Input
                      id="doc-type"
                      value={newDocForm.documentType}
                      onChange={(e) => setNewDocForm(prev => ({...prev, documentType: e.target.value}))}
                      className="col-span-3"
                      placeholder="Tipo de documento"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="due-date" className="text-right">Prazo</Label>
                    <Input
                      id="due-date"
                      type="date"
                      value={newDocForm.dueDate}
                      onChange={(e) => setNewDocForm(prev => ({...prev, dueDate: e.target.value}))}
                      className="col-span-3"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="priority" className="text-right">Prioridade</Label>
                    <Select value={newDocForm.priority} onValueChange={(value: 'alta' | 'media' | 'baixa') => setNewDocForm(prev => ({...prev, priority: value}))}>
                      <SelectTrigger className="col-span-3">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="alta">Alta</SelectItem>
                        <SelectItem value="media">Média</SelectItem>
                        <SelectItem value="baixa">Baixa</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="description" className="text-right">Observações</Label>
                    <Textarea
                      id="description"
                      value={newDocForm.description}
                      onChange={(e) => setNewDocForm(prev => ({...prev, description: e.target.value}))}
                      className="col-span-3"
                      placeholder="Detalhes adicionais..."
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button onClick={addPendingDocument}>Adicionar</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Cliente</TableHead>
                    <TableHead>Documento</TableHead>
                    <TableHead>Prazo</TableHead>
                    <TableHead>Prioridade</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(pendingDocs || []).map((doc) => (
                    <TableRow key={doc.id}>
                      <TableCell className="font-medium">{doc.clientName}</TableCell>
                      <TableCell>{doc.documentType}</TableCell>
                      <TableCell>{new Date(doc.dueDate).toLocaleDateString('pt-BR')}</TableCell>
                      <TableCell>
                        <Badge variant={getPriorityColor(doc.priority) as any}>
                          {doc.priority}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusColor(doc.status) as any}>
                          {doc.status.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setSelectedDoc(doc)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Select
                            value={doc.status}
                            onValueChange={(value: PendingDocument['status']) => updateDocumentStatus(doc.id, value)}
                          >
                            <SelectTrigger className="w-32">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="pendente">Pendente</SelectItem>
                              <SelectItem value="em_andamento">Em andamento</SelectItem>
                              <SelectItem value="concluido">Concluído</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="clients" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Lista de Novos Clientes</h2>
            <Dialog open={isClientDialogOpen} onOpenChange={setIsClientDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Novo Cliente
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Adicionar Novo Cliente</DialogTitle>
                  <DialogDescription>
                    Registre um novo cliente em potencial.
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="name" className="text-right">Nome</Label>
                    <Input
                      id="name"
                      value={newClientForm.name}
                      onChange={(e) => setNewClientForm(prev => ({...prev, name: e.target.value}))}
                      className="col-span-3"
                      placeholder="Nome completo"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="email" className="text-right">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={newClientForm.email}
                      onChange={(e) => setNewClientForm(prev => ({...prev, email: e.target.value}))}
                      className="col-span-3"
                      placeholder="email@exemplo.com"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="phone" className="text-right">Telefone</Label>
                    <Input
                      id="phone"
                      value={newClientForm.phone}
                      onChange={(e) => setNewClientForm(prev => ({...prev, phone: e.target.value}))}
                      className="col-span-3"
                      placeholder="(11) 99999-9999"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="company" className="text-right">Empresa</Label>
                    <Input
                      id="company"
                      value={newClientForm.company}
                      onChange={(e) => setNewClientForm(prev => ({...prev, company: e.target.value}))}
                      className="col-span-3"
                      placeholder="Nome da empresa"
                    />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="notes" className="text-right">Observações</Label>
                    <Textarea
                      id="notes"
                      value={newClientForm.notes}
                      onChange={(e) => setNewClientForm(prev => ({...prev, notes: e.target.value}))}
                      className="col-span-3"
                      placeholder="Observações sobre o cliente..."
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button onClick={addNewClient}>Adicionar</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nome</TableHead>
                    <TableHead>Empresa</TableHead>
                    <TableHead>Contato</TableHead>
                    <TableHead>Data</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(newClients || []).map((client) => (
                    <TableRow key={client.id}>
                      <TableCell className="font-medium">{client.name}</TableCell>
                      <TableCell>{client.company}</TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div>{client.email}</div>
                          <div className="text-muted-foreground">{client.phone}</div>
                        </div>
                      </TableCell>
                      <TableCell>{new Date(client.dateAdded).toLocaleDateString('pt-BR')}</TableCell>
                      <TableCell>
                        <Badge variant={getStatusColor(client.status) as any}>
                          {client.status.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setSelectedClient(client)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Select
                            value={client.status}
                            onValueChange={(value: NewClient['status']) => updateClientStatus(client.id, value)}
                          >
                            <SelectTrigger className="w-32">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="novo">Novo</SelectItem>
                              <SelectItem value="em_analise">Em análise</SelectItem>
                              <SelectItem value="aprovado">Aprovado</SelectItem>
                              <SelectItem value="rejeitado">Rejeitado</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="services" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-primary" />
                  Agenda
                </CardTitle>
                <CardDescription>Agendamento de reuniões</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Gerencie agenda de atendimentos</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PhoneCall className="h-5 w-5 text-primary" />
                  Chamados
                </CardTitle>
                <CardDescription>Suporte ao cliente</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Registre e acompanhe solicitações</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-primary" />
                  CRM
                </CardTitle>
                <CardDescription>Relacionamento com clientes</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Fortaleça relacionamentos</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Document Details Dialog */}
      <Dialog open={!!selectedDoc} onOpenChange={() => setSelectedDoc(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Detalhes do Documento</DialogTitle>
          </DialogHeader>
          {selectedDoc && (
            <div className="space-y-4">
              <div>
                <Label>Cliente</Label>
                <p className="text-sm text-muted-foreground">{selectedDoc.clientName}</p>
              </div>
              <div>
                <Label>Documento</Label>
                <p className="text-sm text-muted-foreground">{selectedDoc.documentType}</p>
              </div>
              <div>
                <Label>Prazo</Label>
                <p className="text-sm text-muted-foreground">{new Date(selectedDoc.dueDate).toLocaleDateString('pt-BR')}</p>
              </div>
              <div>
                <Label>Prioridade</Label>
                <p className="text-sm">
                  <Badge variant={getPriorityColor(selectedDoc.priority) as any}>
                    {selectedDoc.priority}
                  </Badge>
                </p>
              </div>
              <div>
                <Label>Status</Label>
                <p className="text-sm">
                  <Badge variant={getStatusColor(selectedDoc.status) as any}>
                    {selectedDoc.status.replace('_', ' ')}
                  </Badge>
                </p>
              </div>
              {selectedDoc.description && (
                <div>
                  <Label>Observações</Label>
                  <p className="text-sm text-muted-foreground">{selectedDoc.description}</p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Client Details Dialog */}
      <Dialog open={!!selectedClient} onOpenChange={() => setSelectedClient(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Detalhes do Cliente</DialogTitle>
          </DialogHeader>
          {selectedClient && (
            <div className="space-y-4">
              <div>
                <Label>Nome</Label>
                <p className="text-sm text-muted-foreground">{selectedClient.name}</p>
              </div>
              <div>
                <Label>Email</Label>
                <p className="text-sm text-muted-foreground">{selectedClient.email}</p>
              </div>
              <div>
                <Label>Telefone</Label>
                <p className="text-sm text-muted-foreground">{selectedClient.phone}</p>
              </div>
              <div>
                <Label>Empresa</Label>
                <p className="text-sm text-muted-foreground">{selectedClient.company}</p>
              </div>
              <div>
                <Label>Data de Cadastro</Label>
                <p className="text-sm text-muted-foreground">{new Date(selectedClient.dateAdded).toLocaleDateString('pt-BR')}</p>
              </div>
              <div>
                <Label>Status</Label>
                <p className="text-sm">
                  <Badge variant={getStatusColor(selectedClient.status) as any}>
                    {selectedClient.status.replace('_', ' ')}
                  </Badge>
                </p>
              </div>
              {selectedClient.notes && (
                <div>
                  <Label>Observações</Label>
                  <p className="text-sm text-muted-foreground">{selectedClient.notes}</p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
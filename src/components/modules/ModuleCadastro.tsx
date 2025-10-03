import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useKV } from '@github/spark/hooks'
import { toast } from 'sonner'
import { 
  Users, 
  Fire, 
  Receipt, 
  ChartBar, 
  Storefront, 
  MapPin, 
  Plant, 
  Calculator, 
  UserCheck,
  Plus,
  Pencil,
  Trash,
  Eye,
  Download
} from '@phosphor-icons/react'

type SubmoduleType = 'doc-associacao' | 'doc-bombeiro' | 'doc-lucro-presumido' | 'doc-lucro-real' | 'doc-mei' | 'doc-prefeitura' | 'doc-rural' | 'doc-simples' | 'situacao-clientes'

interface Document {
  id: string
  clienteId: string
  clienteNome: string
  tipo: string
  numero?: string
  dataVencimento?: string
  dataEmissao?: string
  status: 'pendente' | 'em-andamento' | 'concluido' | 'vencido'
  observacoes?: string
  arquivo?: string
}

interface Cliente {
  id: string
  nome: string
  cpfCnpj: string
  email?: string
  telefone?: string
  endereco?: string
  tipoEmpresa: string
  status: 'ativo' | 'inativo' | 'pendente'
  dataUltimaAtualizacao: string
}

export default function ModuleCadastro() {
  const [activeSubmodule, setActiveSubmodule] = useState<SubmoduleType | null>(null)
  const [documents, setDocuments] = useKV<Document[]>('cadastro-documents', [])
  const [clientes, setClientes] = useKV<Cliente[]>('cadastro-clientes', [])
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [editingItem, setEditingItem] = useState<string | null>(null)
  const [formData, setFormData] = useState<{[key: string]: string}>({})

  const submodules = [
    {
      id: 'doc-associacao' as SubmoduleType,
      title: 'Documentação Associação',
      description: 'Documentos de associações e entidades',
      icon: Users,
      color: 'bg-blue-50 text-blue-600'
    },
    {
      id: 'doc-bombeiro' as SubmoduleType,
      title: 'Documentação Bombeiro',
      description: 'Auto de vistoria do corpo de bombeiros',
      icon: Fire,
      color: 'bg-red-50 text-red-600'
    },
    {
      id: 'doc-lucro-presumido' as SubmoduleType,
      title: 'Documentação Lucro Presumido',
      description: 'Documentos para empresas do lucro presumido',
      icon: Receipt,
      color: 'bg-green-50 text-green-600'
    },
    {
      id: 'doc-lucro-real' as SubmoduleType,
      title: 'Documentação Lucro Real',
      description: 'Documentos para empresas do lucro real',
      icon: ChartBar,
      color: 'bg-purple-50 text-purple-600'
    },
    {
      id: 'doc-mei' as SubmoduleType,
      title: 'Documentação MEI',
      description: 'Documentos para microempreendedores',
      icon: Storefront,
      color: 'bg-orange-50 text-orange-600'
    },
    {
      id: 'doc-prefeitura' as SubmoduleType,
      title: 'Documentação Prefeitura',
      description: 'Documentos municipais e licenças',
      icon: MapPin,
      color: 'bg-indigo-50 text-indigo-600'
    },
    {
      id: 'doc-rural' as SubmoduleType,
      title: 'Documentação Rural',
      description: 'Documentos para produtores rurais',
      icon: Plant,
      color: 'bg-emerald-50 text-emerald-600'
    },
    {
      id: 'doc-simples' as SubmoduleType,
      title: 'Documentação Simples',
      description: 'Documentos para empresas do Simples Nacional',
      icon: Calculator,
      color: 'bg-cyan-50 text-cyan-600'
    },
    {
      id: 'situacao-clientes' as SubmoduleType,
      title: 'Situação de Clientes',
      description: 'Status e situação dos clientes',
      icon: UserCheck,
      color: 'bg-pink-50 text-pink-600'
    }
  ]

  const handleAddDocument = () => {
    if (!activeSubmodule || activeSubmodule === 'situacao-clientes') return
    
    const newDocument: Document = {
      id: Date.now().toString(),
      clienteId: formData.clienteId || '',
      clienteNome: formData.clienteNome || '',
      tipo: getDocumentTypeForSubmodule(activeSubmodule),
      numero: formData.numero || '',
      dataVencimento: formData.dataVencimento || '',
      dataEmissao: formData.dataEmissao || new Date().toISOString().split('T')[0],
      status: formData.status as 'pendente' | 'em-andamento' | 'concluido' | 'vencido' || 'pendente',
      observacoes: formData.observacoes || '',
      arquivo: formData.arquivo || ''
    }

    setDocuments(current => [...(current || []), newDocument])
    setFormData({})
    setShowAddDialog(false)
    toast.success('Documento adicionado com sucesso!')
  }

  const handleAddCliente = () => {
    const newCliente: Cliente = {
      id: Date.now().toString(),
      nome: formData.nome || '',
      cpfCnpj: formData.cpfCnpj || '',
      email: formData.email || '',
      telefone: formData.telefone || '',
      endereco: formData.endereco || '',
      tipoEmpresa: formData.tipoEmpresa || '',
      status: formData.status as 'ativo' | 'inativo' | 'pendente' || 'ativo',
      dataUltimaAtualizacao: new Date().toISOString().split('T')[0]
    }

    setClientes(current => [...(current || []), newCliente])
    setFormData({})
    setShowAddDialog(false)
    toast.success('Cliente adicionado com sucesso!')
  }

  const handleEditDocument = (doc: Document) => {
    setEditingItem(doc.id)
    setFormData({
      clienteId: doc.clienteId,
      clienteNome: doc.clienteNome,
      numero: doc.numero || '',
      dataVencimento: doc.dataVencimento || '',
      dataEmissao: doc.dataEmissao || '',
      status: doc.status,
      observacoes: doc.observacoes || '',
      arquivo: doc.arquivo || ''
    })
    setShowAddDialog(true)
  }

  const handleEditCliente = (cliente: Cliente) => {
    setEditingItem(cliente.id)
    setFormData({
      nome: cliente.nome,
      cpfCnpj: cliente.cpfCnpj,
      email: cliente.email || '',
      telefone: cliente.telefone || '',
      endereco: cliente.endereco || '',
      tipoEmpresa: cliente.tipoEmpresa,
      status: cliente.status
    })
    setShowAddDialog(true)
  }

  const handleUpdateDocument = () => {
    if (!editingItem) return

    setDocuments(current => 
      (current || []).map(doc => 
        doc.id === editingItem
          ? { 
              ...doc, 
              ...formData, 
              dataUltimaAtualizacao: new Date().toISOString().split('T')[0],
              observacoes: formData.observacoes || doc.observacoes,
              arquivo: formData.arquivo || doc.arquivo
            }
          : doc
      )
    )
    
    setEditingItem(null)
    setFormData({})
    setShowAddDialog(false)
    toast.success('Documento atualizado com sucesso!')
  }

  const handleUpdateCliente = () => {
    if (!editingItem) return

    setClientes(current => 
      (current || []).map(cliente => 
        cliente.id === editingItem 
          ? { 
              ...cliente, 
              nome: formData.nome || cliente.nome,
              cpfCnpj: formData.cpfCnpj || cliente.cpfCnpj,
              email: formData.email || cliente.email,
              telefone: formData.telefone || cliente.telefone,
              endereco: formData.endereco || cliente.endereco,
              tipoEmpresa: formData.tipoEmpresa || cliente.tipoEmpresa,
              status: formData.status as 'ativo' | 'inativo' | 'pendente' || cliente.status,
              dataUltimaAtualizacao: new Date().toISOString().split('T')[0]
            }
          : cliente
      )
    )
    
    setEditingItem(null)
    setFormData({})
    setShowAddDialog(false)
    toast.success('Cliente atualizado com sucesso!')
  }

  const handleDeleteDocument = (id: string) => {
    setDocuments(current => (current || []).filter(doc => doc.id !== id))
    toast.success('Documento removido com sucesso!')
  }

  const handleDeleteCliente = (id: string) => {
    setClientes(current => (current || []).filter(cliente => cliente.id !== id))
    toast.success('Cliente removido com sucesso!')
  }

  const getDocumentTypeForSubmodule = (submodule: SubmoduleType): string => {
    const types = {
      'doc-associacao': 'Associação',
      'doc-bombeiro': 'Bombeiro',
      'doc-lucro-presumido': 'Lucro Presumido',
      'doc-lucro-real': 'Lucro Real',
      'doc-mei': 'MEI',
      'doc-prefeitura': 'Prefeitura',
      'doc-rural': 'Rural',
      'doc-simples': 'Simples Nacional'
    }
    return types[submodule] || ''
  }

  const getStatusColor = (status: string) => {
    const colors = {
      'pendente': 'bg-yellow-100 text-yellow-800',
      'em-andamento': 'bg-blue-100 text-blue-800',
      'concluido': 'bg-green-100 text-green-800',
      'vencido': 'bg-red-100 text-red-800',
      'ativo': 'bg-green-100 text-green-800',
      'inativo': 'bg-gray-100 text-gray-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const filteredDocuments = (documents || []).filter(doc => 
    activeSubmodule && activeSubmodule !== 'situacao-clientes' 
      ? doc.tipo === getDocumentTypeForSubmodule(activeSubmodule)
      : true
  )

  const renderSubmoduleContent = (submodule: SubmoduleType) => {
    if (submodule === 'situacao-clientes') {
      return (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-semibold text-foreground">Situação de Clientes</h2>
            <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
              <DialogTrigger asChild>
                <Button onClick={() => { setEditingItem(null); setFormData({}); }}>
                  <Plus size={16} className="mr-2" />
                  Novo Cliente
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>{editingItem ? 'Editar Cliente' : 'Novo Cliente'}</DialogTitle>
                  <DialogDescription>
                    {editingItem ? 'Edite as informações do cliente' : 'Adicione um novo cliente ao sistema'}
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="nome">Nome/Razão Social</Label>
                      <Input
                        id="nome"
                        value={formData.nome || ''}
                        onChange={(e) => setFormData(prev => ({...prev, nome: e.target.value}))}
                        placeholder="Nome completo ou razão social"
                      />
                    </div>
                    <div>
                      <Label htmlFor="cpfCnpj">CPF/CNPJ</Label>
                      <Input
                        id="cpfCnpj"
                        value={formData.cpfCnpj || ''}
                        onChange={(e) => setFormData(prev => ({...prev, cpfCnpj: e.target.value}))}
                        placeholder="000.000.000-00 ou 00.000.000/0001-00"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email || ''}
                        onChange={(e) => setFormData(prev => ({...prev, email: e.target.value}))}
                        placeholder="email@exemplo.com"
                      />
                    </div>
                    <div>
                      <Label htmlFor="telefone">Telefone</Label>
                      <Input
                        id="telefone"
                        value={formData.telefone || ''}
                        onChange={(e) => setFormData(prev => ({...prev, telefone: e.target.value}))}
                        placeholder="(11) 99999-9999"
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="endereco">Endereço</Label>
                    <Input
                      id="endereco"
                      value={formData.endereco || ''}
                      onChange={(e) => setFormData(prev => ({...prev, endereco: e.target.value}))}
                      placeholder="Endereço completo"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="tipoEmpresa">Tipo de Empresa</Label>
                      <Select value={formData.tipoEmpresa || ''} onValueChange={(value) => setFormData(prev => ({...prev, tipoEmpresa: value}))}>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione o tipo" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="mei">MEI</SelectItem>
                          <SelectItem value="simples">Simples Nacional</SelectItem>
                          <SelectItem value="lucro-presumido">Lucro Presumido</SelectItem>
                          <SelectItem value="lucro-real">Lucro Real</SelectItem>
                          <SelectItem value="associacao">Associação</SelectItem>
                          <SelectItem value="rural">Rural</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="status">Status</Label>
                      <Select value={formData.status || 'ativo'} onValueChange={(value) => setFormData(prev => ({...prev, status: value}))}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="ativo">Ativo</SelectItem>
                          <SelectItem value="inativo">Inativo</SelectItem>
                          <SelectItem value="pendente">Pendente</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowAddDialog(false)}>Cancelar</Button>
                  <Button onClick={editingItem ? handleUpdateCliente : handleAddCliente}>
                    {editingItem ? 'Salvar' : 'Adicionar'}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Lista de Clientes</CardTitle>
              <CardDescription>Gerencie todos os clientes cadastrados no sistema</CardDescription>
            </CardHeader>
            <CardContent>
              {(clientes || []).length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <UserCheck size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Nenhum cliente cadastrado ainda.</p>
                  <p className="text-sm">Clique em "Novo Cliente" para começar.</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nome/Razão Social</TableHead>
                      <TableHead>CPF/CNPJ</TableHead>
                      <TableHead>Tipo</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Última Atualização</TableHead>
                      <TableHead className="text-right">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(clientes || []).map((cliente) => (
                      <TableRow key={cliente.id}>
                        <TableCell className="font-medium">{cliente.nome}</TableCell>
                        <TableCell>{cliente.cpfCnpj}</TableCell>
                        <TableCell className="capitalize">{cliente.tipoEmpresa}</TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(cliente.status)}>
                            {cliente.status}
                          </Badge>
                        </TableCell>
                        <TableCell>{new Date(cliente.dataUltimaAtualizacao).toLocaleDateString('pt-BR')}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEditCliente(cliente)}
                            >
                              <Pencil size={16} />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteCliente(cliente.id)}
                              className="text-destructive hover:text-destructive"
                            >
                              <Trash size={16} />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>
      )
    }

    // Para todos os outros submódulos de documentação
    const submoduleInfo = submodules.find(s => s.id === submodule)
    const documentType = getDocumentTypeForSubmodule(submodule)

    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-semibold text-foreground">{submoduleInfo?.title}</h2>
          <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
            <DialogTrigger asChild>
              <Button onClick={() => { setEditingItem(null); setFormData({}); }}>
                <Plus size={16} className="mr-2" />
                Novo Documento
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>{editingItem ? 'Editar Documento' : 'Novo Documento'}</DialogTitle>
                <DialogDescription>
                  {editingItem ? 'Edite as informações do documento' : `Adicione um novo documento de ${documentType}`}
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="clienteNome">Cliente</Label>
                    <Input
                      id="clienteNome"
                      value={formData.clienteNome || ''}
                      onChange={(e) => setFormData(prev => ({...prev, clienteNome: e.target.value}))}
                      placeholder="Nome do cliente"
                    />
                  </div>
                  <div>
                    <Label htmlFor="numero">Número do Documento</Label>
                    <Input
                      id="numero"
                      value={formData.numero || ''}
                      onChange={(e) => setFormData(prev => ({...prev, numero: e.target.value}))}
                      placeholder="Número ou protocolo"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="dataEmissao">Data de Emissão</Label>
                    <Input
                      id="dataEmissao"
                      type="date"
                      value={formData.dataEmissao || new Date().toISOString().split('T')[0]}
                      onChange={(e) => setFormData(prev => ({...prev, dataEmissao: e.target.value}))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="dataVencimento">Data de Vencimento</Label>
                    <Input
                      id="dataVencimento"
                      type="date"
                      value={formData.dataVencimento || ''}
                      onChange={(e) => setFormData(prev => ({...prev, dataVencimento: e.target.value}))}
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="status">Status</Label>
                  <Select value={formData.status || 'pendente'} onValueChange={(value) => setFormData(prev => ({...prev, status: value}))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pendente">Pendente</SelectItem>
                      <SelectItem value="em-andamento">Em Andamento</SelectItem>
                      <SelectItem value="concluido">Concluído</SelectItem>
                      <SelectItem value="vencido">Vencido</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="observacoes">Observações</Label>
                  <Textarea
                    id="observacoes"
                    value={formData.observacoes || ''}
                    onChange={(e) => setFormData(prev => ({...prev, observacoes: e.target.value}))}
                    placeholder="Observações adicionais sobre o documento"
                    rows={3}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowAddDialog(false)}>Cancelar</Button>
                <Button onClick={editingItem ? handleUpdateDocument : handleAddDocument}>
                  {editingItem ? 'Salvar' : 'Adicionar'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Documentos de {documentType}</CardTitle>
            <CardDescription>{submoduleInfo?.description}</CardDescription>
          </CardHeader>
          <CardContent>
            {filteredDocuments.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Receipt size={48} className="mx-auto mb-4 opacity-50" />
                <p>Nenhum documento cadastrado ainda.</p>
                <p className="text-sm">Clique em "Novo Documento" para começar.</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Cliente</TableHead>
                    <TableHead>Número</TableHead>
                    <TableHead>Data Emissão</TableHead>
                    <TableHead>Vencimento</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredDocuments.map((doc) => (
                    <TableRow key={doc.id}>
                      <TableCell className="font-medium">{doc.clienteNome}</TableCell>
                      <TableCell>{doc.numero || '-'}</TableCell>
                      <TableCell>{doc.dataEmissao ? new Date(doc.dataEmissao).toLocaleDateString('pt-BR') : '-'}</TableCell>
                      <TableCell>{doc.dataVencimento ? new Date(doc.dataVencimento).toLocaleDateString('pt-BR') : '-'}</TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(doc.status)}>
                          {doc.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditDocument(doc)}
                          >
                            <Pencil size={16} />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteDocument(doc.id)}
                            className="text-destructive hover:text-destructive"
                          >
                            <Trash size={16} />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  if (activeSubmodule) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            onClick={() => {
              setActiveSubmodule(null)
              setShowAddDialog(false)
              setEditingItem(null)
              setFormData({})
            }}
            className="text-muted-foreground hover:text-foreground"
          >
            ← Voltar
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Cadastro</h1>
            <p className="text-muted-foreground">Cadastros básicos do sistema</p>
          </div>
        </div>
        
        {renderSubmoduleContent(activeSubmodule)}
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Cadastro</h1>
        <p className="text-muted-foreground">Cadastros básicos do sistema</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {submodules.map((submodule) => {
          const Icon = submodule.icon
          return (
            <Card 
              key={submodule.id}
              className="cursor-pointer hover:shadow-md transition-shadow duration-200"
              onClick={() => setActiveSubmodule(submodule.id)}
            >
              <CardHeader>
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${submodule.color}`}>
                    <Icon size={24} />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{submodule.title}</CardTitle>
                    <CardDescription>{submodule.description}</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Button variant="ghost" className="w-full justify-start text-muted-foreground hover:text-foreground">
                  Acessar módulo →
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
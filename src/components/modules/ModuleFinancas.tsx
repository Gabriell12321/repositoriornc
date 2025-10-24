import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useKV } from '@github/spark/hooks'
import { Plus, Receipt, TrendUp, Wallet, Users, ArrowUp, ArrowDown } from '@phosphor-icons/react'

interface CashMovement {
  id: string
  date: string
  description: string
  type: 'entrada' | 'saida'
  amount: number
  category: string
}

interface Fee {
  id: string
  clientName: string
  service: string
  amount: number
  status: 'pendente' | 'pago' | 'vencido'
  dueDate: string
  createdDate: string
}

interface Invoice {
  id: string
  clientName: string
  services: string[]
  amount: number
  status: 'rascunho' | 'enviada' | 'paga' | 'vencida'
  issueDate: string
  dueDate: string
}

export default function ModuleFinancas() {
  const [cashMovements, setCashMovements] = useKV<CashMovement[]>('cash-movements', [])
  const [fees, setFees] = useKV<Fee[]>('fees', [])
  const [invoices, setInvoices] = useKV<Invoice[]>('invoices', [])
  
  const [newMovement, setNewMovement] = useState({
    description: '',
    type: 'entrada' as 'entrada' | 'saida',
    amount: '',
    category: ''
  })
  
  const [newFee, setNewFee] = useState({
    clientName: '',
    service: '',
    amount: '',
    dueDate: ''
  })
  
  const [newInvoice, setNewInvoice] = useState({
    clientName: '',
    services: [''],
    amount: '',
    dueDate: ''
  })

  const addCashMovement = () => {
    if (newMovement.description && newMovement.amount && newMovement.category) {
      const movement: CashMovement = {
        id: Date.now().toString(),
        date: new Date().toISOString().split('T')[0],
        description: newMovement.description,
        type: newMovement.type,
        amount: parseFloat(newMovement.amount),
        category: newMovement.category
      }
      setCashMovements(current => [...(current || []), movement])
      setNewMovement({ description: '', type: 'entrada', amount: '', category: '' })
    }
  }

  const addFee = () => {
    if (newFee.clientName && newFee.service && newFee.amount && newFee.dueDate) {
      const fee: Fee = {
        id: Date.now().toString(),
        clientName: newFee.clientName,
        service: newFee.service,
        amount: parseFloat(newFee.amount),
        status: 'pendente',
        dueDate: newFee.dueDate,
        createdDate: new Date().toISOString().split('T')[0]
      }
      setFees(current => [...(current || []), fee])
      setNewFee({ clientName: '', service: '', amount: '', dueDate: '' })
    }
  }

  const addInvoice = () => {
    if (newInvoice.clientName && newInvoice.amount && newInvoice.dueDate) {
      const invoice: Invoice = {
        id: Date.now().toString(),
        clientName: newInvoice.clientName,
        services: newInvoice.services.filter(s => s.trim()),
        amount: parseFloat(newInvoice.amount),
        status: 'rascunho',
        issueDate: new Date().toISOString().split('T')[0],
        dueDate: newInvoice.dueDate
      }
      setInvoices(current => [...(current || []), invoice])
      setNewInvoice({ clientName: '', services: [''], amount: '', dueDate: '' })
    }
  }

  const updateFeeStatus = (feeId: string, status: Fee['status']) => {
    setFees(current => 
      (current || []).map(fee => 
        fee.id === feeId ? { ...fee, status } : fee
      )
    )
  }

  const updateInvoiceStatus = (invoiceId: string, status: Invoice['status']) => {
    setInvoices(current => 
      (current || []).map(invoice => 
        invoice.id === invoiceId ? { ...invoice, status } : invoice
      )
    )
  }

  const totalCash = (cashMovements || []).reduce((total, movement) => {
    return total + (movement.type === 'entrada' ? movement.amount : -movement.amount)
  }, 0)

  const totalPendingFees = (fees || [])
    .filter(fee => fee.status === 'pendente')
    .reduce((total, fee) => total + fee.amount, 0)

  const totalInvoices = (invoices || []).reduce((total, invoice) => total + invoice.amount, 0)

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Finanças</h1>
        <p className="text-muted-foreground">Gestão completa do financeiro da empresa</p>
      </div>

      {/* Resumo Financeiro */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Saldo em Caixa</CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">
              R$ {totalCash.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Honorários Pendentes</CardTitle>
            <Plus className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-accent">
              R$ {totalPendingFees.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Faturado</CardTitle>
            <TrendUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-chart-2">
              R$ {totalInvoices.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="caixa" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="caixa">Caixa</TabsTrigger>
          <TabsTrigger value="honorarios">Controle de Honorários</TabsTrigger>
          <TabsTrigger value="faturamento">Faturamento</TabsTrigger>
        </TabsList>

        {/* Aba Caixa */}
        <TabsContent value="caixa" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Movimentação de Caixa</h2>
            <Dialog>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Nova Movimentação
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Nova Movimentação</DialogTitle>
                  <DialogDescription>
                    Registre uma entrada ou saída de caixa
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="movement-description">Descrição</Label>
                    <Input
                      id="movement-description"
                      value={newMovement.description}
                      onChange={(e) => setNewMovement(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Descrição da movimentação"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="movement-type">Tipo</Label>
                      <Select value={newMovement.type} onValueChange={(value: 'entrada' | 'saida') => setNewMovement(prev => ({ ...prev, type: value }))}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="entrada">Entrada</SelectItem>
                          <SelectItem value="saida">Saída</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="movement-amount">Valor</Label>
                      <Input
                        id="movement-amount"
                        type="number"
                        step="0.01"
                        value={newMovement.amount}
                        onChange={(e) => setNewMovement(prev => ({ ...prev, amount: e.target.value }))}
                        placeholder="0,00"
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="movement-category">Categoria</Label>
                    <Select value={newMovement.category} onValueChange={(value) => setNewMovement(prev => ({ ...prev, category: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione uma categoria" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="honorarios">Honorários</SelectItem>
                        <SelectItem value="despesas-operacionais">Despesas Operacionais</SelectItem>
                        <SelectItem value="investimentos">Investimentos</SelectItem>
                        <SelectItem value="impostos">Impostos</SelectItem>
                        <SelectItem value="outros">Outros</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button onClick={addCashMovement} className="w-full">
                    Registrar Movimentação
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Últimas Movimentações</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {(cashMovements || []).slice(-10).reverse().map((movement) => (
                  <div key={movement.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-full ${movement.type === 'entrada' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                        {movement.type === 'entrada' ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />}
                      </div>
                      <div>
                        <p className="font-medium">{movement.description}</p>
                        <p className="text-sm text-muted-foreground">{movement.category} • {movement.date}</p>
                      </div>
                    </div>
                    <div className={`font-semibold ${movement.type === 'entrada' ? 'text-green-600' : 'text-red-600'}`}>
                      {movement.type === 'entrada' ? '+' : '-'}R$ {movement.amount.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </div>
                  </div>
                ))}
                {(cashMovements || []).length === 0 && (
                  <p className="text-center text-muted-foreground py-8">
                    Nenhuma movimentação registrada
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aba Controle de Honorários */}
        <TabsContent value="honorarios" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Controle de Honorários</h2>
            <Dialog>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Novo Honorário
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Novo Honorário</DialogTitle>
                  <DialogDescription>
                    Registre um novo honorário a receber
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="fee-client">Cliente</Label>
                    <Input
                      id="fee-client"
                      value={newFee.clientName}
                      onChange={(e) => setNewFee(prev => ({ ...prev, clientName: e.target.value }))}
                      placeholder="Nome do cliente"
                    />
                  </div>
                  <div>
                    <Label htmlFor="fee-service">Serviço</Label>
                    <Input
                      id="fee-service"
                      value={newFee.service}
                      onChange={(e) => setNewFee(prev => ({ ...prev, service: e.target.value }))}
                      placeholder="Descrição do serviço"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="fee-amount">Valor</Label>
                      <Input
                        id="fee-amount"
                        type="number"
                        step="0.01"
                        value={newFee.amount}
                        onChange={(e) => setNewFee(prev => ({ ...prev, amount: e.target.value }))}
                        placeholder="0,00"
                      />
                    </div>
                    <div>
                      <Label htmlFor="fee-due-date">Data de Vencimento</Label>
                      <Input
                        id="fee-due-date"
                        type="date"
                        value={newFee.dueDate}
                        onChange={(e) => setNewFee(prev => ({ ...prev, dueDate: e.target.value }))}
                      />
                    </div>
                  </div>
                  <Button onClick={addFee} className="w-full">
                    Registrar Honorário
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Honorários Registrados</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {(fees || []).map((fee) => (
                  <div key={fee.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Users className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="font-medium">{fee.clientName}</p>
                        <p className="text-sm text-muted-foreground">{fee.service}</p>
                        <p className="text-xs text-muted-foreground">Venc: {fee.dueDate}</p>
                      </div>
                    </div>
                    <div className="text-right space-y-2">
                      <div className="font-semibold">
                        R$ {fee.amount.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                      </div>
                      <div className="flex space-x-2">
                        <Badge 
                          variant={fee.status === 'pago' ? 'default' : fee.status === 'vencido' ? 'destructive' : 'secondary'}
                        >
                          {fee.status}
                        </Badge>
                        <Select value={fee.status} onValueChange={(value: Fee['status']) => updateFeeStatus(fee.id, value)}>
                          <SelectTrigger className="w-24 h-6 text-xs">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="pendente">Pendente</SelectItem>
                            <SelectItem value="pago">Pago</SelectItem>
                            <SelectItem value="vencido">Vencido</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>
                ))}
                {(fees || []).length === 0 && (
                  <p className="text-center text-muted-foreground py-8">
                    Nenhum honorário registrado
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aba Faturamento */}
        <TabsContent value="faturamento" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Faturamento</h2>
            <Dialog>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Nova Fatura
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Nova Fatura</DialogTitle>
                  <DialogDescription>
                    Crie uma nova fatura para um cliente
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="invoice-client">Cliente</Label>
                    <Input
                      id="invoice-client"
                      value={newInvoice.clientName}
                      onChange={(e) => setNewInvoice(prev => ({ ...prev, clientName: e.target.value }))}
                      placeholder="Nome do cliente"
                    />
                  </div>
                  <div>
                    <Label htmlFor="invoice-services">Serviços</Label>
                    {newInvoice.services.map((service, index) => (
                      <div key={index} className="flex space-x-2 mt-2">
                        <Input
                          value={service}
                          onChange={(e) => {
                            const newServices = [...newInvoice.services]
                            newServices[index] = e.target.value
                            setNewInvoice(prev => ({ ...prev, services: newServices }))
                          }}
                          placeholder="Descrição do serviço"
                        />
                        {index === newInvoice.services.length - 1 && (
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => setNewInvoice(prev => ({ ...prev, services: [...prev.services, ''] }))}
                          >
                            <Plus className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="invoice-amount">Valor Total</Label>
                      <Input
                        id="invoice-amount"
                        type="number"
                        step="0.01"
                        value={newInvoice.amount}
                        onChange={(e) => setNewInvoice(prev => ({ ...prev, amount: e.target.value }))}
                        placeholder="0,00"
                      />
                    </div>
                    <div>
                      <Label htmlFor="invoice-due-date">Data de Vencimento</Label>
                      <Input
                        id="invoice-due-date"
                        type="date"
                        value={newInvoice.dueDate}
                        onChange={(e) => setNewInvoice(prev => ({ ...prev, dueDate: e.target.value }))}
                      />
                    </div>
                  </div>
                  <Button onClick={addInvoice} className="w-full">
                    Criar Fatura
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Faturas Emitidas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {(invoices || []).map((invoice) => (
                  <div key={invoice.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Receipt className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="font-medium">{invoice.clientName}</p>
                        <p className="text-sm text-muted-foreground">
                          {invoice.services.join(', ')}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Emissão: {invoice.issueDate} • Venc: {invoice.dueDate}
                        </p>
                      </div>
                    </div>
                    <div className="text-right space-y-2">
                      <div className="font-semibold">
                        R$ {invoice.amount.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                      </div>
                      <div className="flex space-x-2">
                        <Badge 
                          variant={
                            invoice.status === 'paga' ? 'default' : 
                            invoice.status === 'vencida' ? 'destructive' : 
                            invoice.status === 'enviada' ? 'secondary' : 'outline'
                          }
                        >
                          {invoice.status}
                        </Badge>
                        <Select value={invoice.status} onValueChange={(value: Invoice['status']) => updateInvoiceStatus(invoice.id, value)}>
                          <SelectTrigger className="w-24 h-6 text-xs">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="rascunho">Rascunho</SelectItem>
                            <SelectItem value="enviada">Enviada</SelectItem>
                            <SelectItem value="paga">Paga</SelectItem>
                            <SelectItem value="vencida">Vencida</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>
                ))}
                {(invoices || []).length === 0 && (
                  <p className="text-center text-muted-foreground py-8">
                    Nenhuma fatura emitida
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
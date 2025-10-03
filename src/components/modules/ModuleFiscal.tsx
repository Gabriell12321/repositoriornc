import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useKV } from '@github/spark/hooks'
import { FileText, Calculator, CurrencyDollar, Building, TrendUp, Receipt, File, Warning, CheckCircle } from '@phosphor-icons/react'

interface FiscalDifference {
  id: string
  description: string
  contabilValue: number
  fiscalValue: number
  difference: number
  status: 'pending' | 'resolved'
  date: string
}

interface RetentionRecord {
  id: string
  client: string
  service: string
  grossValue: number
  retentionType: string
  retentionRate: number
  retentionValue: number
  date: string
}

interface TaxationRecord {
  id: string
  type: string
  regime: string
  baseValue: number
  rate: number
  taxValue: number
  dueDate: string
  status: 'calculated' | 'paid' | 'overdue'
}

export default function ModuleFiscal() {
  const [differences, setDifferences] = useKV<FiscalDifference[]>('fiscal-differences', [])
  const [retentions, setRetentions] = useKV<RetentionRecord[]>('fiscal-retentions', [])
  const [taxationRecords, setTaxationRecords] = useKV<TaxationRecord[]>('taxation-records', [])
  const [selectedRegime, setSelectedRegime] = useState('')

  const addDifference = (difference: Omit<FiscalDifference, 'id'>) => {
    setDifferences(current => [...(current || []), { ...difference, id: Date.now().toString() }])
  }

  const addRetention = (retention: Omit<RetentionRecord, 'id'>) => {
    setRetentions(current => [...(current || []), { ...retention, id: Date.now().toString() }])
  }

  const addTaxation = (taxation: Omit<TaxationRecord, 'id'>) => {
    setTaxationRecords(current => [...(current || []), { ...taxation, id: Date.now().toString() }])
  }

  const taxRegimes = [
    { value: 'simples', label: 'Simples Nacional', description: 'Regime simplificado para micro e pequenas empresas' },
    { value: 'presumido', label: 'Lucro Presumido', description: 'Tributação com base em presunção de lucro' },
    { value: 'real', label: 'Lucro Real', description: 'Tributação sobre o lucro efetivo' },
    { value: 'mei', label: 'MEI', description: 'Microempreendedor Individual' },
    { value: 'associacao', label: 'Associação', description: 'Entidades sem fins lucrativos' },
    { value: 'rural', label: 'Atividade Rural', description: 'Produtor rural pessoa física ou jurídica' }
  ]

  const retentionTypes = [
    { value: 'irrf', label: 'IRRF', rate: 1.5 },
    { value: 'iss', label: 'ISS', rate: 5.0 },
    { value: 'inss', label: 'INSS', rate: 11.0 },
    { value: 'csll', label: 'CSLL', rate: 1.0 },
    { value: 'cofins', label: 'COFINS', rate: 3.0 },
    { value: 'pis', label: 'PIS', rate: 0.65 }
  ]

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Fiscal</h1>
        <p className="text-muted-foreground">Gestão completa de obrigações fiscais e tributárias</p>
      </div>

      <Tabs defaultValue="differences" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="differences">Diferenças</TabsTrigger>
          <TabsTrigger value="retentions">Retenções</TabsTrigger>
          <TabsTrigger value="taxation">Tributação</TabsTrigger>
          <TabsTrigger value="spreadsheet">Planilha Fisco</TabsTrigger>
        </TabsList>

        <TabsContent value="differences" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-semibold">Diferenças Fisco x Contábil</h2>
            <Dialog>
              <DialogTrigger asChild>
                <Button>
                  <Warning className="mr-2 h-4 w-4" />
                  Nova Diferença
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Registrar Diferença</DialogTitle>
                  <DialogDescription>
                    Registre uma diferença entre os valores contábeis e fiscais
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={(e) => {
                  e.preventDefault()
                  const formData = new FormData(e.target as HTMLFormElement)
                  const contabilValue = Number(formData.get('contabilValue'))
                  const fiscalValue = Number(formData.get('fiscalValue'))
                  addDifference({
                    description: formData.get('description') as string,
                    contabilValue,
                    fiscalValue,
                    difference: contabilValue - fiscalValue,
                    status: 'pending',
                    date: new Date().toISOString().split('T')[0]
                  })
                }} className="space-y-4">
                  <div>
                    <Label htmlFor="description">Descrição</Label>
                    <Input name="description" placeholder="Ex: Depreciação acelerada..." required />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="contabilValue">Valor Contábil</Label>
                      <Input name="contabilValue" type="number" step="0.01" required />
                    </div>
                    <div>
                      <Label htmlFor="fiscalValue">Valor Fiscal</Label>
                      <Input name="fiscalValue" type="number" step="0.01" required />
                    </div>
                  </div>
                  <Button type="submit">Registrar Diferença</Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid gap-4">
            {(differences || []).map((diff) => (
              <Card key={diff.id}>
                <CardContent className="p-4">
                  <div className="flex justify-between items-start">
                    <div className="space-y-2">
                      <h3 className="font-semibold">{diff.description}</h3>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Contábil:</span>
                          <p className="font-medium">R$ {diff.contabilValue.toLocaleString('pt-BR')}</p>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Fiscal:</span>
                          <p className="font-medium">R$ {diff.fiscalValue.toLocaleString('pt-BR')}</p>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Diferença:</span>
                          <p className={`font-medium ${diff.difference > 0 ? 'text-red-600' : 'text-green-600'}`}>
                            R$ {Math.abs(diff.difference).toLocaleString('pt-BR')}
                          </p>
                        </div>
                      </div>
                    </div>
                    <Badge variant={diff.status === 'resolved' ? 'default' : 'secondary'}>
                      {diff.status === 'resolved' ? 'Resolvida' : 'Pendente'}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="retentions" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-semibold">Controle de Retenções</h2>
            <Dialog>
              <DialogTrigger asChild>
                <Button>
                  <Receipt className="mr-2 h-4 w-4" />
                  Nova Retenção
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Registrar Retenção</DialogTitle>
                  <DialogDescription>
                    Registre uma retenção de imposto sobre serviços
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={(e) => {
                  e.preventDefault()
                  const formData = new FormData(e.target as HTMLFormElement)
                  const grossValue = Number(formData.get('grossValue'))
                  const retentionType = formData.get('retentionType') as string
                  const rate = retentionTypes.find(t => t.value === retentionType)?.rate || 0
                  addRetention({
                    client: formData.get('client') as string,
                    service: formData.get('service') as string,
                    grossValue,
                    retentionType,
                    retentionRate: rate,
                    retentionValue: (grossValue * rate) / 100,
                    date: formData.get('date') as string
                  })
                }} className="space-y-4">
                  <div>
                    <Label htmlFor="client">Cliente</Label>
                    <Input name="client" required />
                  </div>
                  <div>
                    <Label htmlFor="service">Serviço</Label>
                    <Input name="service" required />
                  </div>
                  <div>
                    <Label htmlFor="grossValue">Valor Bruto</Label>
                    <Input name="grossValue" type="number" step="0.01" required />
                  </div>
                  <div>
                    <Label htmlFor="retentionType">Tipo de Retenção</Label>
                    <Select name="retentionType" required>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione o tipo" />
                      </SelectTrigger>
                      <SelectContent>
                        {retentionTypes.map((type) => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label} ({type.rate}%)
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="date">Data</Label>
                    <Input name="date" type="date" required />
                  </div>
                  <Button type="submit">Registrar Retenção</Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Cliente</TableHead>
                <TableHead>Serviço</TableHead>
                <TableHead>Valor Bruto</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Alíquota</TableHead>
                <TableHead>Valor Retido</TableHead>
                <TableHead>Data</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(retentions || []).map((retention) => (
                <TableRow key={retention.id}>
                  <TableCell>{retention.client}</TableCell>
                  <TableCell>{retention.service}</TableCell>
                  <TableCell>R$ {retention.grossValue.toLocaleString('pt-BR')}</TableCell>
                  <TableCell>{retention.retentionType.toUpperCase()}</TableCell>
                  <TableCell>{retention.retentionRate}%</TableCell>
                  <TableCell>R$ {retention.retentionValue.toLocaleString('pt-BR')}</TableCell>
                  <TableCell>{new Date(retention.date).toLocaleDateString('pt-BR')}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TabsContent>

        <TabsContent value="taxation" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-semibold">Regimes de Tributação</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {taxRegimes.map((regime) => (
              <Card key={regime.value} className="cursor-pointer hover:shadow-md transition-shadow" 
                    onClick={() => setSelectedRegime(regime.value)}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Building className="h-5 w-5" />
                    {regime.label}
                  </CardTitle>
                  <CardDescription>{regime.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" size="sm">Ver Detalhes</Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {selectedRegime && (
            <Card>
              <CardHeader>
                <CardTitle>Calculadora - {taxRegimes.find(r => r.value === selectedRegime)?.label}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="baseValue">Valor Base</Label>
                    <Input type="number" step="0.01" placeholder="0,00" />
                  </div>
                  <div>
                    <Label htmlFor="period">Período</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="monthly">Mensal</SelectItem>
                        <SelectItem value="quarterly">Trimestral</SelectItem>
                        <SelectItem value="annual">Anual</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <Button>
                  <Calculator className="mr-2 h-4 w-4" />
                  Calcular Impostos
                </Button>
              </CardContent>
            </Card>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Tributação ISS</CardTitle>
                <CardDescription>Imposto Sobre Serviços</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Alíquota padrão:</span>
                    <span className="font-medium">2% a 5%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Base de cálculo:</span>
                    <span className="font-medium">Valor do serviço</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Tributação Rural</CardTitle>
                <CardDescription>Atividades do agronegócio</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>ITR:</span>
                    <span className="font-medium">0,03% a 20%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>FUNRURAL:</span>
                    <span className="font-medium">2,3%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="spreadsheet" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-semibold">Planilha Fisco Contábil</h2>
            <Button>
              <File className="mr-2 h-4 w-4" />
              Exportar Planilha
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendUp className="h-5 w-5" />
                  Total de Diferenças
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {(differences || []).length}
                </div>
                <p className="text-sm text-muted-foreground">
                  {(differences || []).filter(d => d.status === 'pending').length} pendentes
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CurrencyDollar className="h-5 w-5" />
                  Valor Total Retido
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  R$ {(retentions || []).reduce((sum, r) => sum + r.retentionValue, 0).toLocaleString('pt-BR')}
                </div>
                <p className="text-sm text-muted-foreground">
                  Este mês
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5" />
                  Conformidade
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  98%
                </div>
                <p className="text-sm text-muted-foreground">
                  Obrigações em dia
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Resumo Fiscal Mensal</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Imposto</TableHead>
                    <TableHead>Base de Cálculo</TableHead>
                    <TableHead>Alíquota</TableHead>
                    <TableHead>Valor Calculado</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell>IRPJ</TableCell>
                    <TableCell>R$ 100.000,00</TableCell>
                    <TableCell>15%</TableCell>
                    <TableCell>R$ 15.000,00</TableCell>
                    <TableCell><Badge variant="default">Calculado</Badge></TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>CSLL</TableCell>
                    <TableCell>R$ 100.000,00</TableCell>
                    <TableCell>9%</TableCell>
                    <TableCell>R$ 9.000,00</TableCell>
                    <TableCell><Badge variant="default">Calculado</Badge></TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>PIS</TableCell>
                    <TableCell>R$ 200.000,00</TableCell>
                    <TableCell>1,65%</TableCell>
                    <TableCell>R$ 3.300,00</TableCell>
                    <TableCell><Badge variant="secondary">Pendente</Badge></TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>COFINS</TableCell>
                    <TableCell>R$ 200.000,00</TableCell>
                    <TableCell>7,6%</TableCell>
                    <TableCell>R$ 15.200,00</TableCell>
                    <TableCell><Badge variant="secondary">Pendente</Badge></TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
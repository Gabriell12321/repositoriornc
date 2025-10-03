import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { useKV } from '@github/spark/hooks'
import { Plus, Calculator, FileText, TrendDown, ChartBar } from '@phosphor-icons/react'
import { toast } from 'sonner'

interface ContaContabil {
  id: string
  codigo: string
  nome: string
  tipo: 'ATIVO' | 'PASSIVO' | 'PATRIMONIO' | 'RECEITA' | 'DESPESA'
  categoria: string
  saldo: number
}

interface LancamentoContabil {
  id: string
  data: string
  conta: string
  debito: number
  credito: number
  historico: string
}

interface ItemDepreciacao {
  id: string
  bem: string
  valorOriginal: number
  vidaUtil: number
  taxaAnual: number
  depreciacaoAcumulada: number
  valorResidual: number
}

export default function ModuleContabilidade() {
  const [activeTab, setActiveTab] = useState('balanco-patrimonial')
  const [contasContabeis, setContasContabeis] = useKV<ContaContabil[]>('contas-contabeis', [
    { id: '1', codigo: '1.1.01.001', nome: 'Caixa', tipo: 'ATIVO', categoria: 'Circulante', saldo: 15000 },
    { id: '2', codigo: '1.1.01.002', nome: 'Bancos', tipo: 'ATIVO', categoria: 'Circulante', saldo: 45000 },
    { id: '3', codigo: '1.2.01.001', nome: 'Imobilizado', tipo: 'ATIVO', categoria: 'Não Circulante', saldo: 120000 },
    { id: '4', codigo: '2.1.01.001', nome: 'Fornecedores', tipo: 'PASSIVO', categoria: 'Circulante', saldo: 25000 },
    { id: '5', codigo: '3.1.01.001', nome: 'Capital Social', tipo: 'PATRIMONIO', categoria: 'Patrimônio Líquido', saldo: 150000 },
    { id: '6', codigo: '4.1.01.001', nome: 'Receita de Vendas', tipo: 'RECEITA', categoria: 'Operacional', saldo: 80000 },
    { id: '7', codigo: '5.1.01.001', nome: 'Custo das Vendas', tipo: 'DESPESA', categoria: 'Operacional', saldo: 35000 }
  ])
  
  const [itensDepreciacao, setItensDepreciacao] = useKV<ItemDepreciacao[]>('itens-depreciacao', [
    { 
      id: '1', 
      bem: 'Computadores', 
      valorOriginal: 25000, 
      vidaUtil: 5, 
      taxaAnual: 20, 
      depreciacaoAcumulada: 10000, 
      valorResidual: 15000 
    },
    { 
      id: '2', 
      bem: 'Móveis e Utensílios', 
      valorOriginal: 15000, 
      vidaUtil: 10, 
      taxaAnual: 10, 
      depreciacaoAcumulada: 4500, 
      valorResidual: 10500 
    }
  ])

  const [novaConta, setNovaConta] = useState({
    codigo: '',
    nome: '',
    tipo: '' as ContaContabil['tipo'],
    categoria: '',
    saldo: 0
  })

  const [novoItemDepreciacao, setNovoItemDepreciacao] = useState({
    bem: '',
    valorOriginal: 0,
    vidaUtil: 0,
    taxaAnual: 0
  })

  const adicionarConta = () => {
    if (!novaConta.codigo || !novaConta.nome || !novaConta.tipo) {
      toast.error('Preencha todos os campos obrigatórios')
      return
    }

    const conta: ContaContabil = {
      id: Date.now().toString(),
      ...novaConta
    }

    setContasContabeis(current => [...(current || []), conta])
    setNovaConta({ codigo: '', nome: '', tipo: '' as ContaContabil['tipo'], categoria: '', saldo: 0 })
    toast.success('Conta adicionada com sucesso!')
  }

  const adicionarItemDepreciacao = () => {
    if (!novoItemDepreciacao.bem || novoItemDepreciacao.valorOriginal <= 0) {
      toast.error('Preencha todos os campos obrigatórios')
      return
    }

    const item: ItemDepreciacao = {
      id: Date.now().toString(),
      ...novoItemDepreciacao,
      depreciacaoAcumulada: 0,
      valorResidual: novoItemDepreciacao.valorOriginal
    }

    setItensDepreciacao(current => [...(current || []), item])
    setNovoItemDepreciacao({ bem: '', valorOriginal: 0, vidaUtil: 0, taxaAnual: 0 })
    toast.success('Item de depreciação adicionado!')
  }

  // Cálculos para Balanço Patrimonial
  const ativo = (contasContabeis || []).filter(c => c.tipo === 'ATIVO')
  const passivo = (contasContabeis || []).filter(c => c.tipo === 'PASSIVO')
  const patrimonio = (contasContabeis || []).filter(c => c.tipo === 'PATRIMONIO')
  
  const totalAtivo = ativo.reduce((sum, conta) => sum + conta.saldo, 0)
  const totalPassivo = passivo.reduce((sum, conta) => sum + conta.saldo, 0)
  const totalPatrimonio = patrimonio.reduce((sum, conta) => sum + conta.saldo, 0)

  // Cálculos para DRE
  const receitas = (contasContabeis || []).filter(c => c.tipo === 'RECEITA')
  const despesas = (contasContabeis || []).filter(c => c.tipo === 'DESPESA')
  
  const totalReceitas = receitas.reduce((sum, conta) => sum + conta.saldo, 0)
  const totalDespesas = despesas.reduce((sum, conta) => sum + conta.saldo, 0)
  const lucroLiquido = totalReceitas - totalDespesas

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Contabilidade</h1>
        <p className="text-muted-foreground">Gestão completa de operações contábeis</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid grid-cols-4 w-full">
          <TabsTrigger value="balanco-patrimonial" className="flex items-center gap-2">
            <ChartBar size={16} />
            Balanço Patrimonial
          </TabsTrigger>
          <TabsTrigger value="dre" className="flex items-center gap-2">
            <TrendDown size={16} />
            DRE
          </TabsTrigger>
          <TabsTrigger value="depreciacao" className="flex items-center gap-2">
            <Calculator size={16} />
            Depreciação
          </TabsTrigger>
          <TabsTrigger value="plano-contas" className="flex items-center gap-2">
            <FileText size={16} />
            Plano de Contas
          </TabsTrigger>
        </TabsList>

        <TabsContent value="balanco-patrimonial" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ChartBar className="text-primary" />
                Balanço Patrimonial
              </CardTitle>
              <CardDescription>Demonstração da situação patrimonial da empresa</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* ATIVO */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-foreground">ATIVO</h3>
                  <div className="space-y-2">
                    {ativo.map(conta => (
                      <div key={conta.id} className="flex justify-between items-center p-3 bg-muted rounded-lg">
                        <div>
                          <p className="font-medium">{conta.nome}</p>
                          <p className="text-sm text-muted-foreground">{conta.codigo} - {conta.categoria}</p>
                        </div>
                        <span className="font-semibold text-primary">
                          R$ {conta.saldo.toLocaleString('pt-BR')}
                        </span>
                      </div>
                    ))}
                    <div className="flex justify-between items-center p-3 bg-primary/10 rounded-lg border">
                      <span className="font-bold">TOTAL DO ATIVO</span>
                      <span className="font-bold text-primary text-lg">
                        R$ {totalAtivo.toLocaleString('pt-BR')}
                      </span>
                    </div>
                  </div>
                </div>

                {/* PASSIVO + PATRIMÔNIO LÍQUIDO */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-foreground">PASSIVO</h3>
                  <div className="space-y-2">
                    {passivo.map(conta => (
                      <div key={conta.id} className="flex justify-between items-center p-3 bg-muted rounded-lg">
                        <div>
                          <p className="font-medium">{conta.nome}</p>
                          <p className="text-sm text-muted-foreground">{conta.codigo} - {conta.categoria}</p>
                        </div>
                        <span className="font-semibold text-red-600">
                          R$ {conta.saldo.toLocaleString('pt-BR')}
                        </span>
                      </div>
                    ))}
                  </div>

                  <h3 className="text-lg font-semibold text-foreground mt-6">PATRIMÔNIO LÍQUIDO</h3>
                  <div className="space-y-2">
                    {patrimonio.map(conta => (
                      <div key={conta.id} className="flex justify-between items-center p-3 bg-muted rounded-lg">
                        <div>
                          <p className="font-medium">{conta.nome}</p>
                          <p className="text-sm text-muted-foreground">{conta.codigo} - {conta.categoria}</p>
                        </div>
                        <span className="font-semibold text-green-600">
                          R$ {conta.saldo.toLocaleString('pt-BR')}
                        </span>
                      </div>
                    ))}
                    <div className="flex justify-between items-center p-3 bg-primary/10 rounded-lg border">
                      <span className="font-bold">TOTAL PASSIVO + PL</span>
                      <span className="font-bold text-primary text-lg">
                        R$ {(totalPassivo + totalPatrimonio).toLocaleString('pt-BR')}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dre" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendDown className="text-primary" />
                Demonstração do Resultado do Exercício (DRE)
              </CardTitle>
              <CardDescription>Demonstração do resultado financeiro da empresa</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-w-2xl">
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold text-green-600">RECEITAS</h3>
                  {receitas.map(conta => (
                    <div key={conta.id} className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                      <div>
                        <p className="font-medium">{conta.nome}</p>
                        <p className="text-sm text-muted-foreground">{conta.codigo}</p>
                      </div>
                      <span className="font-semibold text-green-600">
                        R$ {conta.saldo.toLocaleString('pt-BR')}
                      </span>
                    </div>
                  ))}
                  <div className="flex justify-between items-center p-3 bg-green-100 rounded-lg border">
                    <span className="font-bold">TOTAL DAS RECEITAS</span>
                    <span className="font-bold text-green-600 text-lg">
                      R$ {totalReceitas.toLocaleString('pt-BR')}
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  <h3 className="text-lg font-semibold text-red-600">DESPESAS</h3>
                  {despesas.map(conta => (
                    <div key={conta.id} className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                      <div>
                        <p className="font-medium">{conta.nome}</p>
                        <p className="text-sm text-muted-foreground">{conta.codigo}</p>
                      </div>
                      <span className="font-semibold text-red-600">
                        (R$ {conta.saldo.toLocaleString('pt-BR')})
                      </span>
                    </div>
                  ))}
                  <div className="flex justify-between items-center p-3 bg-red-100 rounded-lg border">
                    <span className="font-bold">TOTAL DAS DESPESAS</span>
                    <span className="font-bold text-red-600 text-lg">
                      (R$ {totalDespesas.toLocaleString('pt-BR')})
                    </span>
                  </div>
                </div>

                <div className="flex justify-between items-center p-4 bg-primary/10 rounded-lg border-2 border-primary">
                  <span className="font-bold text-lg">RESULTADO LÍQUIDO</span>
                  <span className={`font-bold text-xl ${lucroLiquido >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {lucroLiquido >= 0 ? 'R$ ' : '(R$ '}
                    {Math.abs(lucroLiquido).toLocaleString('pt-BR')}
                    {lucroLiquido < 0 ? ')' : ''}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="depreciacao" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="text-primary" />
                Controle de Depreciação
              </CardTitle>
              <CardDescription>Gestão e cálculo da depreciação de bens</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Formulário para adicionar item */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-muted rounded-lg">
                <Input
                  placeholder="Nome do bem"
                  value={novoItemDepreciacao.bem}
                  onChange={(e) => setNovoItemDepreciacao(prev => ({ ...prev, bem: e.target.value }))}
                />
                <Input
                  type="number"
                  placeholder="Valor original"
                  value={novoItemDepreciacao.valorOriginal || ''}
                  onChange={(e) => setNovoItemDepreciacao(prev => ({ ...prev, valorOriginal: Number(e.target.value) }))}
                />
                <Input
                  type="number"
                  placeholder="Vida útil (anos)"
                  value={novoItemDepreciacao.vidaUtil || ''}
                  onChange={(e) => setNovoItemDepreciacao(prev => ({ ...prev, vidaUtil: Number(e.target.value) }))}
                />
                <Button onClick={adicionarItemDepreciacao} className="flex items-center gap-2">
                  <Plus size={16} />
                  Adicionar
                </Button>
              </div>

              {/* Tabela de depreciação */}
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Bem</TableHead>
                    <TableHead>Valor Original</TableHead>
                    <TableHead>Vida Útil</TableHead>
                    <TableHead>Taxa Anual</TableHead>
                    <TableHead>Depreciação Acumulada</TableHead>
                    <TableHead>Valor Residual</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(itensDepreciacao || []).map(item => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{item.bem}</TableCell>
                      <TableCell>R$ {item.valorOriginal.toLocaleString('pt-BR')}</TableCell>
                      <TableCell>{item.vidaUtil} anos</TableCell>
                      <TableCell>{item.taxaAnual}%</TableCell>
                      <TableCell className="text-red-600">
                        R$ {item.depreciacaoAcumulada.toLocaleString('pt-BR')}
                      </TableCell>
                      <TableCell className="text-green-600">
                        R$ {item.valorResidual.toLocaleString('pt-BR')}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="plano-contas" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="text-primary" />
                Plano de Contas
              </CardTitle>
              <CardDescription>Estrutura e organização das contas contábeis</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Formulário para adicionar conta */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 p-4 bg-muted rounded-lg">
                <Input
                  placeholder="Código da conta"
                  value={novaConta.codigo}
                  onChange={(e) => setNovaConta(prev => ({ ...prev, codigo: e.target.value }))}
                />
                <Input
                  placeholder="Nome da conta"
                  value={novaConta.nome}
                  onChange={(e) => setNovaConta(prev => ({ ...prev, nome: e.target.value }))}
                />
                <Select value={novaConta.tipo} onValueChange={(value: ContaContabil['tipo']) => 
                  setNovaConta(prev => ({ ...prev, tipo: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ATIVO">Ativo</SelectItem>
                    <SelectItem value="PASSIVO">Passivo</SelectItem>
                    <SelectItem value="PATRIMONIO">Patrimônio</SelectItem>
                    <SelectItem value="RECEITA">Receita</SelectItem>
                    <SelectItem value="DESPESA">Despesa</SelectItem>
                  </SelectContent>
                </Select>
                <Input
                  placeholder="Categoria"
                  value={novaConta.categoria}
                  onChange={(e) => setNovaConta(prev => ({ ...prev, categoria: e.target.value }))}
                />
                <Input
                  type="number"
                  placeholder="Saldo inicial"
                  value={novaConta.saldo || ''}
                  onChange={(e) => setNovaConta(prev => ({ ...prev, saldo: Number(e.target.value) }))}
                />
                <Button onClick={adicionarConta} className="flex items-center gap-2">
                  <Plus size={16} />
                  Adicionar
                </Button>
              </div>

              {/* Tabela de contas */}
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Código</TableHead>
                    <TableHead>Nome da Conta</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Categoria</TableHead>
                    <TableHead>Saldo</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(contasContabeis || []).map(conta => (
                    <TableRow key={conta.id}>
                      <TableCell className="font-mono">{conta.codigo}</TableCell>
                      <TableCell className="font-medium">{conta.nome}</TableCell>
                      <TableCell>
                        <Badge variant={
                          conta.tipo === 'ATIVO' ? 'default' :
                          conta.tipo === 'PASSIVO' ? 'destructive' :
                          conta.tipo === 'PATRIMONIO' ? 'secondary' :
                          conta.tipo === 'RECEITA' ? 'default' : 'outline'
                        }>
                          {conta.tipo}
                        </Badge>
                      </TableCell>
                      <TableCell>{conta.categoria}</TableCell>
                      <TableCell className={
                        conta.tipo === 'ATIVO' || conta.tipo === 'RECEITA' ? 'text-green-600' : 
                        conta.tipo === 'PASSIVO' || conta.tipo === 'DESPESA' ? 'text-red-600' : 
                        'text-blue-600'
                      }>
                        R$ {conta.saldo.toLocaleString('pt-BR')}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
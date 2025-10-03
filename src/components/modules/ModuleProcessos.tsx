import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useKV } from '@github/spark/hooks'
import { Plus, Target, TrendUp, CheckCircle, Clock, Warning, ChartBar, Users, Calendar, Star } from '@phosphor-icons/react'

interface ImprovementPlan {
  id: string
  title: string
  description: string
  category: string
  priority: 'baixa' | 'media' | 'alta' | 'critica'
  status: 'planejado' | 'em-andamento' | 'concluido' | 'pausado'
  responsible: string
  startDate: string
  endDate: string
  progress: number
  actions: ImprovementAction[]
  metrics: string[]
  expectedResults: string
  resources: string
  createdAt: string
}

interface ImprovementAction {
  id: string
  description: string
  completed: boolean
  dueDate: string
  responsible: string
}

export default function ModuleProcessos() {
  const [improvementPlans, setImprovementPlans] = useKV<ImprovementPlan[]>('improvement-plans', [])
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [editingPlan, setEditingPlan] = useState<ImprovementPlan | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('todos')
  
  const [newPlan, setNewPlan] = useState({
    title: '',
    description: '',
    category: '',
    priority: 'media' as const,
    responsible: '',
    startDate: '',
    endDate: '',
    expectedResults: '',
    resources: '',
    metrics: ''
  })

  const handleAddPlan = () => {
    if (!newPlan.title || !newPlan.description) return

    const plan: ImprovementPlan = {
      id: Date.now().toString(),
      title: newPlan.title,
      description: newPlan.description,
      category: newPlan.category,
      priority: newPlan.priority,
      status: 'planejado',
      responsible: newPlan.responsible,
      startDate: newPlan.startDate,
      endDate: newPlan.endDate,
      progress: 0,
      actions: [],
      metrics: newPlan.metrics ? newPlan.metrics.split(',').map(m => m.trim()).filter(Boolean) : [],
      expectedResults: newPlan.expectedResults,
      resources: newPlan.resources,
      createdAt: new Date().toISOString()
    }

    setImprovementPlans(current => [...(current || []), plan])
    setNewPlan({
      title: '',
      description: '',
      category: '',
      priority: 'media',
      responsible: '',
      startDate: '',
      endDate: '',
      expectedResults: '',
      resources: '',
      metrics: ''
    })
    setIsAddDialogOpen(false)
  }

  const updatePlanProgress = (planId: string, progress: number) => {
    setImprovementPlans(current =>
      (current || []).map(plan =>
        plan.id === planId 
          ? { ...plan, progress, status: progress === 100 ? 'concluido' : plan.status }
          : plan
      )
    )
  }

  const updatePlanStatus = (planId: string, status: ImprovementPlan['status']) => {
    setImprovementPlans(current =>
      (current || []).map(plan =>
        plan.id === planId ? { ...plan, status } : plan
      )
    )
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critica': return 'bg-red-100 text-red-800 border-red-200'
      case 'alta': return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'media': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'baixa': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'concluido': return 'bg-green-100 text-green-800 border-green-200'
      case 'em-andamento': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'pausado': return 'bg-red-100 text-red-800 border-red-200'
      case 'planejado': return 'bg-gray-100 text-gray-800 border-gray-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const filteredPlans = selectedCategory === 'todos' 
    ? (improvementPlans || []) 
    : (improvementPlans || []).filter(plan => plan.category === selectedCategory)

  const categories = ['Estrutura', 'Funcionalidade', 'Setor', 'Processos', 'Qualidade', 'Tecnologia']
  
  const overallProgress = (improvementPlans || []).length > 0 
    ? (improvementPlans || []).reduce((acc, plan) => acc + plan.progress, 0) / (improvementPlans || []).length 
    : 0

  const completedPlans = (improvementPlans || []).filter(plan => plan.status === 'concluido').length
  const inProgressPlans = (improvementPlans || []).filter(plan => plan.status === 'em-andamento').length

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Processos Internos</h1>
        <p className="text-muted-foreground">Otimização e controle de processos</p>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="improvement">Plano de Melhoria Contínua</TabsTrigger>
          <TabsTrigger value="quality">Controle de Qualidade</TabsTrigger>
          <TabsTrigger value="audit">Auditoria</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Fluxos de Trabalho</CardTitle>
                <CardDescription>Automação de processos</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Configure workflows automatizados</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Controle de Qualidade</CardTitle>
                <CardDescription>Padrões e procedimentos</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Monitore qualidade dos serviços</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Auditoria Interna</CardTitle>
                <CardDescription>Revisão de processos</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Audite e melhore processos</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="improvement" className="space-y-6">
          {/* Métricas do Plano de Melhoria */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total de Planos</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{(improvementPlans || []).length}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Concluídos</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{completedPlans}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Em Andamento</CardTitle>
                <Clock className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">{inProgressPlans}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Progresso Geral</CardTitle>
                <TrendUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{Math.round(overallProgress)}%</div>
                <Progress value={overallProgress} className="mt-2" />
              </CardContent>
            </Card>
          </div>

          {/* Controles e Filtros */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex items-center gap-4">
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filtrar por categoria" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todas as categorias</SelectItem>
                  {categories.map(category => (
                    <SelectItem key={category} value={category}>{category}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Novo Plano de Melhoria
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Criar Plano de Melhoria Contínua</DialogTitle>
                  <DialogDescription>
                    Defina um novo plano para melhoria contínua dos processos
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="title">Título do Plano</Label>
                      <Input
                        id="title"
                        value={newPlan.title}
                        onChange={(e) => setNewPlan(prev => ({...prev, title: e.target.value}))}
                        placeholder="Ex: Otimização do processo de folha de pagamento"
                      />
                    </div>
                    <div>
                      <Label htmlFor="category">Categoria</Label>
                      <Select value={newPlan.category} onValueChange={(value) => setNewPlan(prev => ({...prev, category: value}))}>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione a categoria" />
                        </SelectTrigger>
                        <SelectContent>
                          {categories.map(category => (
                            <SelectItem key={category} value={category}>{category}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="description">Descrição</Label>
                    <Textarea
                      id="description"
                      value={newPlan.description}
                      onChange={(e) => setNewPlan(prev => ({...prev, description: e.target.value}))}
                      placeholder="Descreva detalhadamente o plano de melhoria..."
                      rows={3}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="priority">Prioridade</Label>
                      <Select value={newPlan.priority} onValueChange={(value: any) => setNewPlan(prev => ({...prev, priority: value}))}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="baixa">Baixa</SelectItem>
                          <SelectItem value="media">Média</SelectItem>
                          <SelectItem value="alta">Alta</SelectItem>
                          <SelectItem value="critica">Crítica</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="responsible">Responsável</Label>
                      <Input
                        id="responsible"
                        value={newPlan.responsible}
                        onChange={(e) => setNewPlan(prev => ({...prev, responsible: e.target.value}))}
                        placeholder="Nome do responsável"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="startDate">Data de Início</Label>
                      <Input
                        id="startDate"
                        type="date"
                        value={newPlan.startDate}
                        onChange={(e) => setNewPlan(prev => ({...prev, startDate: e.target.value}))}
                      />
                    </div>
                    <div>
                      <Label htmlFor="endDate">Data Prevista</Label>
                      <Input
                        id="endDate"
                        type="date"
                        value={newPlan.endDate}
                        onChange={(e) => setNewPlan(prev => ({...prev, endDate: e.target.value}))}
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="expectedResults">Resultados Esperados</Label>
                    <Textarea
                      id="expectedResults"
                      value={newPlan.expectedResults}
                      onChange={(e) => setNewPlan(prev => ({...prev, expectedResults: e.target.value}))}
                      placeholder="Descreva os resultados esperados com esta melhoria..."
                      rows={2}
                    />
                  </div>

                  <div>
                    <Label htmlFor="resources">Recursos Necessários</Label>
                    <Textarea
                      id="resources"
                      value={newPlan.resources}
                      onChange={(e) => setNewPlan(prev => ({...prev, resources: e.target.value}))}
                      placeholder="Liste os recursos necessários (pessoal, tecnologia, orçamento...)"
                      rows={2}
                    />
                  </div>

                  <div>
                    <Label htmlFor="metrics">Métricas de Sucesso</Label>
                    <Input
                      id="metrics"
                      value={newPlan.metrics}
                      onChange={(e) => setNewPlan(prev => ({...prev, metrics: e.target.value}))}
                      placeholder="Ex: Redução de 30% no tempo, Aumento de 20% na satisfação (separar por vírgula)"
                    />
                  </div>

                  <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                      Cancelar
                    </Button>
                    <Button onClick={handleAddPlan}>
                      Criar Plano
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          {/* Lista de Planos de Melhoria */}
          <div className="grid gap-4">
            {filteredPlans.length === 0 ? (
              <Card className="p-8 text-center">
                <div className="text-muted-foreground">
                  <Target className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-medium mb-2">Nenhum plano de melhoria encontrado</h3>
                  <p className="text-sm">Crie seu primeiro plano de melhoria contínua para começar.</p>
                </div>
              </Card>
            ) : (
              filteredPlans.map((plan) => (
                <Card key={plan.id} className="p-6">
                  <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                    <div className="flex-1 space-y-3">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="text-lg font-semibold">{plan.title}</h3>
                        <Badge className={getPriorityColor(plan.priority)}>
                          {plan.priority}
                        </Badge>
                        <Badge className={getStatusColor(plan.status)}>
                          {plan.status}
                        </Badge>
                      </div>
                      
                      <p className="text-muted-foreground text-sm">{plan.description}</p>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div className="flex items-center gap-2">
                          <Users className="h-4 w-4 text-muted-foreground" />
                          <span className="text-muted-foreground">Responsável:</span>
                          <span>{plan.responsible || 'Não definido'}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4 text-muted-foreground" />
                          <span className="text-muted-foreground">Prazo:</span>
                          <span>{plan.endDate ? new Date(plan.endDate).toLocaleDateString('pt-BR') : 'Não definido'}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <ChartBar className="h-4 w-4 text-muted-foreground" />
                          <span className="text-muted-foreground">Categoria:</span>
                          <span>{plan.category}</span>
                        </div>
                      </div>

                      {plan.metrics.length > 0 && (
                        <div className="space-y-2">
                          <span className="text-sm font-medium text-muted-foreground">Métricas de Sucesso:</span>
                          <div className="flex flex-wrap gap-1">
                            {plan.metrics.map((metric, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                <Star className="h-3 w-3 mr-1" />
                                {metric}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="lg:w-64 space-y-3">
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium">Progresso</span>
                          <span className="text-sm text-muted-foreground">{plan.progress}%</span>
                        </div>
                        <Progress value={plan.progress} />
                      </div>

                      <div className="flex flex-wrap gap-2">
                        <Input
                          type="number"
                          min="0"
                          max="100"
                          value={plan.progress}
                          onChange={(e) => updatePlanProgress(plan.id, parseInt(e.target.value) || 0)}
                          className="w-20 h-8 text-xs"
                          placeholder="0-100"
                        />
                        <Select value={plan.status} onValueChange={(status: any) => updatePlanStatus(plan.id, status)}>
                          <SelectTrigger className="w-32 h-8 text-xs">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="planejado">Planejado</SelectItem>
                            <SelectItem value="em-andamento">Em Andamento</SelectItem>
                            <SelectItem value="pausado">Pausado</SelectItem>
                            <SelectItem value="concluido">Concluído</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>

                  {plan.expectedResults && (
                    <div className="mt-4 p-3 bg-muted/50 rounded-lg">
                      <h4 className="text-sm font-medium mb-1">Resultados Esperados:</h4>
                      <p className="text-xs text-muted-foreground">{plan.expectedResults}</p>
                    </div>
                  )}
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        <TabsContent value="quality" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Controle de Qualidade</CardTitle>
              <CardDescription>Padrões e procedimentos de qualidade</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Funcionalidade em desenvolvimento. Aqui você poderá gerenciar:
              </p>
              <ul className="mt-3 space-y-1 text-sm text-muted-foreground">
                <li>• Checklists de qualidade</li>
                <li>• Auditorias de processo</li>
                <li>• Indicadores de performance</li>
                <li>• Padrões de qualidade</li>
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audit" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Auditoria Interna</CardTitle>
              <CardDescription>Revisão e auditoria de processos</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Funcionalidade em desenvolvimento. Aqui você poderá gerenciar:
              </p>
              <ul className="mt-3 space-y-1 text-sm text-muted-foreground">
                <li>• Cronograma de auditorias</li>
                <li>• Relatórios de auditoria</li>
                <li>• Não conformidades</li>
                <li>• Planos de ação corretiva</li>
              </ul>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
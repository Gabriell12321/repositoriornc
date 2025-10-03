import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'
import { TrendUp, TrendDown, Users, Calculator, CurrencyDollar, FileText } from '@phosphor-icons/react'
import { ErrorBoundary } from './ErrorBoundary'
import ChartWrapper from './ChartWrapper'

const monthlyRevenue = [
  { month: 'Jan', value: 65000 },
  { month: 'Fev', value: 72000 },
  { month: 'Mar', value: 68000 },
  { month: 'Abr', value: 78000 },
  { month: 'Mai', value: 82000 },
  { month: 'Jun', value: 85000 },
]

const clientsByService = [
  { name: 'Contabilidade', value: 45, color: '#d42c2c' },
  { name: 'Fiscal', value: 35, color: '#e84545' },
  { name: 'RH', value: 25, color: '#a82222' },
  { name: 'Consultoria', value: 15, color: '#f45656' },
]

const kpiData = [
  {
    title: 'Clientes Ativos',
    value: '127',
    change: '+12%',
    trend: 'up',
    icon: Users,
    description: 'vs. mês anterior'
  },
  {
    title: 'Receita Mensal',
    value: 'R$ 85.000',
    change: '+8%',
    trend: 'up',
    icon: CurrencyDollar,
    description: 'vs. mês anterior'
  },
  {
    title: 'Processos Abertos',
    value: '43',
    change: '-5%',
    trend: 'down',
    icon: FileText,
    description: 'vs. mês anterior'
  },
  {
    title: 'Declarações',
    value: '28',
    change: '+15%',
    trend: 'up',
    icon: Calculator,
    description: 'este mês'
  }
]

export default function DashboardHome() {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">Visão geral dos indicadores da 4M Contabilidade</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiData.map((kpi, index) => {
          const Icon = kpi.icon
          return (
            <Card key={index} className="relative overflow-hidden">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {kpi.title}
                </CardTitle>
                <Icon size={20} className="text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">{kpi.value}</div>
                <div className="flex items-center text-xs">
                  {kpi.trend === 'up' ? (
                    <TrendUp size={16} className="text-green-600 mr-1" />
                  ) : (
                    <TrendDown size={16} className="text-red-600 mr-1" />
                  )}
                  <span className={kpi.trend === 'up' ? 'text-green-600' : 'text-red-600'}>
                    {kpi.change}
                  </span>
                  <span className="text-muted-foreground ml-1">{kpi.description}</span>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <ErrorBoundary>
          <Card>
            <CardHeader>
              <CardTitle>Receita Mensal</CardTitle>
              <CardDescription>
                Evolução da receita nos últimos 6 meses
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ChartWrapper>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={monthlyRevenue} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                    <XAxis 
                      dataKey="month" 
                      tick={{ fontSize: 12, fill: '#6b7280' }}
                      axisLine={{ stroke: '#e5e7eb' }}
                      tickLine={{ stroke: '#e5e7eb' }}
                    />
                    <YAxis 
                      tick={{ fontSize: 12, fill: '#6b7280' }}
                      axisLine={{ stroke: '#e5e7eb' }}
                      tickLine={{ stroke: '#e5e7eb' }}
                      tickFormatter={(value) => `R$ ${(value / 1000).toFixed(0)}k`}
                    />
                    <Tooltip 
                      formatter={(value: number) => [`R$ ${value.toLocaleString()}`, 'Receita']}
                      labelStyle={{ color: '#374151' }}
                      contentStyle={{ 
                        backgroundColor: '#ffffff', 
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#d42c2c" 
                      strokeWidth={3}
                      dot={{ fill: '#d42c2c', strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, stroke: '#d42c2c', strokeWidth: 2, fill: '#ffffff' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </ChartWrapper>
            </CardContent>
          </Card>
        </ErrorBoundary>

        {/* Service Distribution */}
        <ErrorBoundary>
          <Card>
            <CardHeader>
              <CardTitle>Distribuição por Serviço</CardTitle>
              <CardDescription>
                Quantidade de clientes por tipo de serviço
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ChartWrapper>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart margin={{ top: 20, right: 20, left: 20, bottom: 20 }}>
                    <Pie
                      data={clientsByService}
                      cx="50%"
                      cy="50%"
                      outerRadius={90}
                      innerRadius={30}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      labelLine={false}
                    >
                      {clientsByService.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={entry.color} 
                          stroke="#ffffff" 
                          strokeWidth={2}
                        />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value: number) => [value, 'Clientes']}
                      contentStyle={{ 
                        backgroundColor: '#ffffff', 
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </ChartWrapper>
            </CardContent>
          </Card>
        </ErrorBoundary>
      </div>

      {/* Activity Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Atividades Recentes</CardTitle>
          <CardDescription>
            Resumo das principais atividades do sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-primary rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Nova declaração fiscal processada</p>
                <p className="text-xs text-muted-foreground">Cliente: Empresa ABC Ltda - 2 horas atrás</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-accent rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Relatório mensal gerado</p>
                <p className="text-xs text-muted-foreground">Balancete consolidado - 4 horas atrás</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-chart-3 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Novo cliente cadastrado</p>
                <p className="text-xs text-muted-foreground">Startup Tech Solutions - 6 horas atrás</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-chart-4 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Backup automático concluído</p>
                <p className="text-xs text-muted-foreground">Todos os dados seguros - 8 horas atrás</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
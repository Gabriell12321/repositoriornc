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
    <div className="p-8 space-y-8 bg-gradient-to-br from-background via-background/95 to-muted/10 min-h-screen">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          Dashboard
        </h1>
        <p className="text-lg text-muted-foreground">Visão geral dos indicadores da 4M Contabilidade</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiData.map((kpi, index) => {
          const Icon = kpi.icon
          return (
            <Card key={index} className="relative overflow-hidden group hover:shadow-2xl transition-all duration-500 hover:scale-[1.02]">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-sm font-semibold text-muted-foreground">
                  {kpi.title}
                </CardTitle>
                <div className="p-2 rounded-lg bg-gradient-to-br from-primary/10 to-accent/10 group-hover:from-primary/20 group-hover:to-accent/20 transition-all duration-300">
                  <Icon size={22} className="text-primary" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-foreground mb-2">{kpi.value}</div>
                <div className="flex items-center text-sm">
                  {kpi.trend === 'up' ? (
                    <TrendUp size={18} className="text-emerald-600 mr-1" />
                  ) : (
                    <TrendDown size={18} className="text-red-500 mr-1" />
                  )}
                  <span className={`font-semibold ${kpi.trend === 'up' ? 'text-emerald-600' : 'text-red-500'}`}>
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
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Revenue Chart */}
        <ErrorBoundary>
          <Card className="hover:shadow-xl transition-all duration-500 group">
            <CardHeader className="pb-6">
              <CardTitle className="text-xl font-semibold text-foreground group-hover:text-primary transition-colors duration-300">
                Receita Mensal
              </CardTitle>
              <CardDescription className="text-base">
                Evolução da receita nos últimos 6 meses
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ChartWrapper>
                <ResponsiveContainer width="100%" height={320}>
                  <LineChart data={monthlyRevenue} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    <defs>
                      <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#d42c2c" stopOpacity={0.1}/>
                        <stop offset="95%" stopColor="#d42c2c" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.2} stroke="#e2e8f0" />
                    <XAxis 
                      dataKey="month" 
                      tick={{ fontSize: 13, fill: '#64748b', fontWeight: 500 }}
                      axisLine={{ stroke: '#e2e8f0', strokeWidth: 1 }}
                      tickLine={{ stroke: '#e2e8f0' }}
                    />
                    <YAxis 
                      tick={{ fontSize: 13, fill: '#64748b', fontWeight: 500 }}
                      axisLine={{ stroke: '#e2e8f0', strokeWidth: 1 }}
                      tickLine={{ stroke: '#e2e8f0' }}
                      tickFormatter={(value) => `R$ ${(value / 1000).toFixed(0)}k`}
                    />
                    <Tooltip 
                      formatter={(value: number) => [`R$ ${value.toLocaleString()}`, 'Receita']}
                      labelStyle={{ color: '#1e293b', fontWeight: 600 }}
                      contentStyle={{ 
                        backgroundColor: '#ffffff', 
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px',
                        boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                        padding: '12px'
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="value" 
                      stroke="url(#lineGradient)" 
                      strokeWidth={4}
                      dot={{ fill: '#d42c2c', strokeWidth: 3, r: 5 }}
                      activeDot={{ r: 7, stroke: '#d42c2c', strokeWidth: 3, fill: '#ffffff' }}
                      fill="url(#revenueGradient)"
                    />
                    <defs>
                      <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="#d42c2c"/>
                        <stop offset="100%" stopColor="#e84545"/>
                      </linearGradient>
                    </defs>
                  </LineChart>
                </ResponsiveContainer>
              </ChartWrapper>
            </CardContent>
          </Card>
        </ErrorBoundary>

        {/* Service Distribution */}
        <ErrorBoundary>
          <Card className="hover:shadow-xl transition-all duration-500 group">
            <CardHeader className="pb-6">
              <CardTitle className="text-xl font-semibold text-foreground group-hover:text-primary transition-colors duration-300">
                Distribuição por Serviço
              </CardTitle>
              <CardDescription className="text-base">
                Quantidade de clientes por tipo de serviço
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ChartWrapper>
                <ResponsiveContainer width="100%" height={320}>
                  <PieChart margin={{ top: 20, right: 20, left: 20, bottom: 20 }}>
                    <Pie
                      data={clientsByService}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      innerRadius={40}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      labelLine={false}
                      stroke="#ffffff"
                      strokeWidth={3}
                    >
                      {clientsByService.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={entry.color} 
                        />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value: number) => [value, 'Clientes']}
                      labelStyle={{ color: '#1e293b', fontWeight: 600 }}
                      contentStyle={{ 
                        backgroundColor: '#ffffff', 
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px',
                        boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                        padding: '12px'
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
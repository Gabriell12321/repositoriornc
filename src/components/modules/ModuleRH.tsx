import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { UserCheck, FileText, Calendar, Shield, Calculator, Table, Users, Clock, CurrencyDollar, BookOpen, Warning, CheckCircle } from '@phosphor-icons/react'

export default function ModuleRH() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Recursos Humanos</h1>
        <p className="text-muted-foreground">Gestão completa de pessoas, contratos e folha de pagamento</p>
      </div>

      <Tabs defaultValue="controles" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="controles">Controles</TabsTrigger>
          <TabsTrigger value="custos">Custos</TabsTrigger>
          <TabsTrigger value="documentacao">Documentação</TabsTrigger>
          <TabsTrigger value="tabelas">Tabelas</TabsTrigger>
        </TabsList>

        <TabsContent value="controles" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Controle Contrato Experiência */}
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <UserCheck size={20} className="text-primary" />
                  <CardTitle className="text-lg">Contratos de Experiência</CardTitle>
                </div>
                <CardDescription>Controle de períodos e prorrogações</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Vencendo em 7 dias</span>
                  <Badge variant="destructive">3</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Vencendo em 30 dias</span>
                  <Badge variant="secondary">8</Badge>
                </div>
                <Button variant="outline" size="sm" className="w-full mt-3">
                  <Clock size={16} className="mr-2" />
                  Gerenciar Contratos
                </Button>
              </CardContent>
            </Card>

            {/* Controle de Documentos */}
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <FileText size={20} className="text-primary" />
                  <CardTitle className="text-lg">Controle de Documentos</CardTitle>
                </div>
                <CardDescription>Documentação trabalhista completa</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Pendentes</span>
                  <Badge variant="destructive">5</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Vencendo</span>
                  <Badge variant="secondary">12</Badge>
                </div>
                <Button variant="outline" size="sm" className="w-full mt-3">
                  <Warning size={16} className="mr-2" />
                  Ver Pendências
                </Button>
              </CardContent>
            </Card>

            {/* Controle Exames Periódicos */}
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Shield size={20} className="text-primary" />
                  <CardTitle className="text-lg">Exames Periódicos</CardTitle>
                </div>
                <CardDescription>Medicina e segurança do trabalho</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Vencidos</span>
                  <Badge variant="destructive">2</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Próximos 30 dias</span>
                  <Badge variant="secondary">15</Badge>
                </div>
                <Button variant="outline" size="sm" className="w-full mt-3">
                  <Calendar size={16} className="mr-2" />
                  Agendar Exames
                </Button>
              </CardContent>
            </Card>

            {/* Controle Férias */}
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Calendar size={20} className="text-primary" />
                  <CardTitle className="text-lg">Controle de Férias</CardTitle>
                </div>
                <CardDescription>Períodos aquisitivos e concessivos</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Vencendo</span>
                  <Badge variant="destructive">4</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Programadas</span>
                  <Badge variant="outline">18</Badge>
                </div>
                <Button variant="outline" size="sm" className="w-full mt-3">
                  <Calendar size={16} className="mr-2" />
                  Programar Férias
                </Button>
              </CardContent>
            </Card>

            {/* PPRA e PCMSO */}
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Shield size={20} className="text-primary" />
                  <CardTitle className="text-lg">PPRA e PCMSO</CardTitle>
                </div>
                <CardDescription>Programas de segurança e saúde</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">PPRA Atualizado</span>
                  <CheckCircle size={16} className="text-green-600" />
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">PCMSO Atualizado</span>
                  <CheckCircle size={16} className="text-green-600" />
                </div>
                <Button variant="outline" size="sm" className="w-full mt-3">
                  <FileText size={16} className="mr-2" />
                  Gerenciar Programas
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="custos" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Custo Empregada Doméstica */}
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Calculator size={20} className="text-primary" />
                  <CardTitle className="text-lg">Empregada Doméstica</CardTitle>
                </div>
                <CardDescription>Cálculo de custos eSocial Doméstico</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-2xl font-bold text-primary">R$ 1.847,32</div>
                <div className="text-sm text-muted-foreground">Custo total mensal médio</div>
                <Button variant="outline" size="sm" className="w-full mt-3">
                  <Calculator size={16} className="mr-2" />
                  Calcular Custos
                </Button>
              </CardContent>
            </Card>

            {/* Custo Funcionário Empresa x CEI */}
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <CurrencyDollar size={20} className="text-primary" />
                  <CardTitle className="text-lg">Empresa x CEI</CardTitle>
                </div>
                <CardDescription>Comparativo de custos trabalhistas</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm">Empresa:</span>
                  <span className="font-semibold">68,5%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">CEI:</span>
                  <span className="font-semibold">45,2%</span>
                </div>
                <Button variant="outline" size="sm" className="w-full mt-3">
                  <Calculator size={16} className="mr-2" />
                  Comparar Custos
                </Button>
              </CardContent>
            </Card>

            {/* Custo Funcionário Simples Nacional */}
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Calculator size={20} className="text-primary" />
                  <CardTitle className="text-lg">Simples Nacional</CardTitle>
                </div>
                <CardDescription>Custos para empresas do Simples</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-2xl font-bold text-primary">47,8%</div>
                <div className="text-sm text-muted-foreground">Encargos sobre salário</div>
                <Button variant="outline" size="sm" className="w-full mt-3">
                  <Calculator size={16} className="mr-2" />
                  Calcular Encargos
                </Button>
              </CardContent>
            </Card>

            {/* Custo Pró-Labore */}
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Users size={20} className="text-primary" />
                  <CardTitle className="text-lg">Pró-Labore</CardTitle>
                </div>
                <CardDescription>Cálculo de pró-labore e encargos</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm">INSS Empresa:</span>
                  <span className="font-semibold">20%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">INSS Sócio:</span>
                  <span className="font-semibold">11%</span>
                </div>
                <Button variant="outline" size="sm" className="w-full mt-3">
                  <Calculator size={16} className="mr-2" />
                  Calcular Pró-Labore
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="documentacao" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Documentação Contratação */}
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <FileText size={20} className="text-primary" />
                  <CardTitle>Documentação para Contratação</CardTitle>
                </div>
                <CardDescription>Lista completa de documentos necessários</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold text-sm mb-2">Documentos Pessoais</h4>
                    <ul className="text-sm space-y-1 text-muted-foreground">
                      <li>• RG e CPF</li>
                      <li>• Carteira de Trabalho</li>
                      <li>• Título de Eleitor</li>
                      <li>• Certificado Militar</li>
                      <li>• Comprovante Residência</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold text-sm mb-2">Documentos Técnicos</h4>
                    <ul className="text-sm space-y-1 text-muted-foreground">
                      <li>• Atestado de Saúde Ocupacional</li>
                      <li>• Certificados/Diplomas</li>
                      <li>• Declaração Escolaridade</li>
                      <li>• Foto 3x4</li>
                      <li>• Dados Bancários</li>
                    </ul>
                  </div>
                </div>
                <Button variant="outline" className="w-full">
                  <BookOpen size={16} className="mr-2" />
                  Ver Lista Completa
                </Button>
              </CardContent>
            </Card>

            {/* Checklist Admissional */}
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <CheckCircle size={20} className="text-primary" />
                  <CardTitle>Checklist Admissional</CardTitle>
                </div>
                <CardDescription>Processo completo de admissão</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Documentos coletados</span>
                    <CheckCircle size={16} className="text-green-600" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">ASO realizado</span>
                    <CheckCircle size={16} className="text-green-600" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Contrato assinado</span>
                    <Warning size={16} className="text-yellow-600" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">eSocial S-2200</span>
                    <Warning size={16} className="text-red-600" />
                  </div>
                </div>
                <Button variant="outline" className="w-full">
                  <FileText size={16} className="mr-2" />
                  Novo Processo
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="tabelas" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Tabelas INSS */}
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Table size={20} className="text-primary" />
                  <CardTitle>Tabelas INSS</CardTitle>
                </div>
                <CardDescription>Contribuições vigentes 2024</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Até R$ 1.412,00</span>
                    <span className="font-semibold">7,5%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>R$ 1.412,01 a R$ 2.666,68</span>
                    <span className="font-semibold">9%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>R$ 2.666,69 a R$ 4.000,03</span>
                    <span className="font-semibold">12%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>R$ 4.000,04 a R$ 7.786,02</span>
                    <span className="font-semibold">14%</span>
                  </div>
                </div>
                <Button variant="outline" size="sm" className="w-full">
                  <Table size={16} className="mr-2" />
                  Ver Tabela Completa
                </Button>
              </CardContent>
            </Card>

            {/* Salário Família */}
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Users size={20} className="text-primary" />
                  <CardTitle>Salário Família</CardTitle>
                </div>
                <CardDescription>Valores e critérios 2024</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Até R$ 1.819,26</span>
                    <span className="font-semibold">R$ 62,04</span>
                  </div>
                  <div className="text-xs text-muted-foreground mt-2">
                    Por filho de até 14 anos ou inválido
                  </div>
                </div>
                <Button variant="outline" size="sm" className="w-full">
                  <Calculator size={16} className="mr-2" />
                  Calcular Benefício
                </Button>
              </CardContent>
            </Card>

            {/* FGTS */}
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <CurrencyDollar size={20} className="text-primary" />
                  <CardTitle>FGTS</CardTitle>
                </div>
                <CardDescription>Alíquotas e informações</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>FGTS</span>
                    <span className="font-semibold">8%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Multa Rescisória</span>
                    <span className="font-semibold">40%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Contribuição Social</span>
                    <span className="font-semibold">0,5%</span>
                  </div>
                </div>
                <Button variant="outline" size="sm" className="w-full">
                  <Table size={16} className="mr-2" />
                  Ver Tabelas
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
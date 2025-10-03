import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Eye, Target, Shield, Heart } from '@phosphor-icons/react'

export default function ModuleGeral() {
  return (
    <div className="p-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Geral</h1>
        <p className="text-muted-foreground">Informações institucionais e operações gerais do sistema</p>
      </div>

      {/* Company Information Section */}
      <div className="space-y-6">
        <h2 className="text-2xl font-semibold text-foreground border-b border-border pb-2">
          4M Contabilidade - Informações Institucionais
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="md:col-span-2">
            <CardHeader className="flex flex-row items-center space-y-0 pb-4">
              <Eye className="w-6 h-6 text-primary mr-3" />
              <div>
                <CardTitle className="text-xl">Visão</CardTitle>
                <CardDescription>Nossa perspectiva de futuro</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-foreground leading-relaxed">
                Ser a empresa de contabilidade de referência no mercado, reconhecida pela excelência 
                em serviços, inovação tecnológica e relacionamento próximo com nossos clientes, 
                contribuindo para o crescimento sustentável dos negócios que atendemos.
              </p>
            </CardContent>
          </Card>

          <Card className="md:col-span-2">
            <CardHeader className="flex flex-row items-center space-y-0 pb-4">
              <Target className="w-6 h-6 text-primary mr-3" />
              <div>
                <CardTitle className="text-xl">Missão</CardTitle>
                <CardDescription>Nosso propósito e razão de existir</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-foreground leading-relaxed">
                Fornecer soluções contábeis, fiscais e financeiras de alta qualidade, 
                utilizando tecnologia de ponta e conhecimento especializado para otimizar 
                a gestão empresarial de nossos clientes, garantindo compliance e 
                contribuindo para o sucesso de seus negócios.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center space-y-0 pb-4">
              <Shield className="w-6 h-6 text-primary mr-3" />
              <div>
                <CardTitle className="text-xl">Política</CardTitle>
                <CardDescription>Nossos princípios operacionais</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-foreground">
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span>Manter absoluta confidencialidade das informações dos clientes</span>
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span>Seguir rigorosamente as normas contábeis e fiscais vigentes</span>
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span>Promover educação continuada da equipe</span>
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span>Investir constantemente em tecnologia e processos</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center space-y-0 pb-4">
              <Heart className="w-6 h-6 text-primary mr-3" />
              <div>
                <CardTitle className="text-xl">Valores</CardTitle>
                <CardDescription>O que nos guia</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-foreground">
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-accent rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span><strong>Ética:</strong> Transparência em todas as relações</span>
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-accent rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span><strong>Excelência:</strong> Busca constante pela qualidade</span>
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-accent rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span><strong>Inovação:</strong> Soluções modernas e eficientes</span>
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-accent rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span><strong>Comprometimento:</strong> Dedicação aos resultados</span>
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-accent rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span><strong>Respeito:</strong> Valorização de pessoas e diversidade</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* System Operations Section */}
      <div className="space-y-6">
        <h2 className="text-2xl font-semibold text-foreground border-b border-border pb-2">
          Operações do Sistema
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Configurações</CardTitle>
              <CardDescription>Configurações do sistema</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Configure parâmetros gerais do sistema</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Backup</CardTitle>
              <CardDescription>Backup de dados</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Gerencie backups e restauração de dados</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Usuários</CardTitle>
              <CardDescription>Gestão de usuários</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Controle de acesso e permissões</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
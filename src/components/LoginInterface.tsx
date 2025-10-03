import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/hooks/useAuth'
import { Building } from '@phosphor-icons/react'
import { toast } from 'sonner'
import { ROLE_PERMISSIONS } from '@/types'

export default function LoginInterface() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { users, login, createUser } = useAuth()

  // Debug log to see users state
  useEffect(() => {
    console.log('LoginInterface - users loaded:', users?.length, users?.map(u => u.username))
  }, [users])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      console.log('Login attempt for:', username)
      
      // For Elvio admin login
      if (username === 'elvio' && password === 'admin123') {
        // Find or create Elvio user
        let user = users?.find(u => u.username === 'elvio' && u.isActive)
        
        if (!user) {
          console.log('Creating Elvio user')
          const elvioAdmin = {
            username: 'elvio',
            name: 'Elvio - Administrador Master',
            email: 'elvio@4mcontabilidade.com.br',
            role: 'admin' as const,
            isActive: true
          }
          user = createUser(elvioAdmin)
        }

        console.log('Logging in user:', user.username)
        login(user)
        toast.success(`Bem-vindo, ${user.name}!`)
        return
      }

      // For other users
      const user = users?.find(u => u.username === username && u.isActive)
      
      if (!user) {
        toast.error('Usuário não encontrado ou inativo')
        return
      }

      login(user)
      toast.success(`Bem-vindo, ${user.name}!`)
      
    } catch (error) {
      console.error('Login error:', error)
      toast.error('Erro ao fazer login')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/20 to-primary/5 flex items-center justify-center p-4">
      <Card className="w-full max-w-lg shadow-2xl border-0 bg-gradient-to-br from-card/95 to-card/90 backdrop-blur-sm">
        <CardHeader className="space-y-4 text-center pb-8">
          <div className="flex items-center justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-primary to-accent rounded-2xl flex items-center justify-center shadow-lg transform hover:scale-105 transition-transform duration-300">
              <Building size={32} className="text-primary-foreground" />
            </div>
          </div>
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            4M Contabilidade
          </CardTitle>
          <p className="text-lg text-muted-foreground">Entre com suas credenciais</p>
        </CardHeader>
        <CardContent className="px-8 pb-8">
          <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-3">
              <Label htmlFor="username" className="text-sm font-semibold text-foreground">Usuário</Label>
              <Input
                id="username"
                type="text"
                placeholder="Digite seu usuário"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="h-12 text-base border-2 focus:border-primary transition-all duration-300 bg-background/50"
              />
            </div>
            <div className="space-y-3">
              <Label htmlFor="password" className="text-sm font-semibold text-foreground">Senha</Label>
              <Input
                id="password"
                type="password"
                placeholder="Digite sua senha"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="h-12 text-base border-2 focus:border-primary transition-all duration-300 bg-background/50"
              />
            </div>
            <Button 
              type="submit" 
              className="w-full h-12 text-base font-semibold bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02]" 
              disabled={isLoading}
            >
              {isLoading ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>
          
          {/* Debug info */}
          {users && users.length > 0 && (
            <div className="mt-6 p-4 bg-secondary/50 rounded-xl border border-border/30">
              <p className="text-sm text-muted-foreground mb-3 font-medium">
                <strong>Usuários disponíveis:</strong>
              </p>
              <div className="space-y-2">
                {users.map(user => (
                  <div key={user.id} className="text-sm bg-background/30 p-2 rounded-lg">
                    <strong className="text-foreground">{user.username}</strong> - {user.name} ({user.role}) 
                    {user.username === 'elvio' && <span className="text-emerald-600 font-semibold"> - Admin disponível</span>}
                  </div>
                ))}
              </div>
            </div>
          )}

        </CardContent>
      </Card>
    </div>
  )
}
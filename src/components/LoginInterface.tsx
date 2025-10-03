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
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center">
              <Building size={28} className="text-primary-foreground" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold">4M Contabilidade</CardTitle>
          <p className="text-muted-foreground">Entre com suas credenciais</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Usuário</Label>
              <Input
                id="username"
                type="text"
                placeholder="Digite seu usuário"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                type="password"
                placeholder="Digite sua senha"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <Button 
              type="submit" 
              className="w-full" 
              disabled={isLoading}
            >
              {isLoading ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>
          
          {/* Debug info */}
          {users && users.length > 0 && (
            <div className="mt-4 p-3 bg-muted rounded-lg">
              <p className="text-xs text-muted-foreground mb-2">
                <strong>Usuários disponíveis:</strong>
              </p>
              <div className="space-y-1">
                {users.map(user => (
                  <div key={user.id} className="text-xs">
                    <strong>{user.username}</strong> - {user.name} ({user.role}) 
                    {user.username === 'elvio' && <span className="text-green-600"> - Admin disponível</span>}
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
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/hooks/useAuth'
import { Building, User, Lock, Eye, EyeSlash } from '@phosphor-icons/react'
import { toast } from 'sonner'
import { motion } from 'framer-motion'
import { ROLE_PERMISSIONS } from '@/types'

export default function LoginInterface() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [focusedField, setFocusedField] = useState<string | null>(null)
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
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-primary/5 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-4 -left-4 w-72 h-72 bg-gradient-to-br from-primary/10 to-accent/10 rounded-full blur-3xl"
          animate={{
            x: [0, 50, 0],
            y: [0, -30, 0],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute -bottom-4 -right-4 w-96 h-96 bg-gradient-to-br from-accent/8 to-primary/8 rounded-full blur-3xl"
          animate={{
            x: [0, -30, 0],
            y: [0, 40, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute top-1/2 left-1/4 w-64 h-64 bg-gradient-to-br from-primary/5 to-accent/5 rounded-full blur-2xl"
          animate={{
            rotate: [0, 360],
            scale: [1, 1.3, 1],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ 
          duration: 0.6, 
          ease: "easeOut",
          type: "spring",
          stiffness: 100
        }}
      >
        <Card className="w-full max-w-lg shadow-2xl border-0 bg-gradient-to-br from-card/98 to-card/95 backdrop-blur-lg relative overflow-hidden">
          {/* Card glow effect */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5 pointer-events-none" />
          <div className="absolute inset-[1px] bg-gradient-to-br from-card/95 to-card/90 rounded-[calc(0.75rem-1px)] backdrop-blur-sm" />
          
          <div className="relative z-10">
            <CardHeader className="space-y-6 text-center pb-8 pt-10">
              <motion.div 
                className="flex items-center justify-center mb-8"
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ 
                  duration: 0.8, 
                  delay: 0.2,
                  type: "spring",
                  stiffness: 200
                }}
              >
                <div className="relative">
                  <motion.div 
                    className="w-20 h-20 bg-gradient-to-br from-primary via-primary to-accent rounded-3xl flex items-center justify-center shadow-2xl"
                    whileHover={{ scale: 1.05, rotate: 5 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Building size={40} className="text-primary-foreground" />
                  </motion.div>
                  <div className="absolute inset-0 bg-gradient-to-br from-primary to-accent rounded-3xl blur-xl opacity-30 -z-10" />
                </div>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <CardTitle className="text-4xl font-bold bg-gradient-to-r from-primary via-primary to-accent bg-clip-text text-transparent mb-2">
                  4M Contabilidade
                </CardTitle>
                <motion.div
                  className="w-24 h-1 bg-gradient-to-r from-primary to-accent rounded-full mx-auto mb-4"
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{ duration: 0.8, delay: 0.6 }}
                />
                <p className="text-lg text-muted-foreground font-medium">
                  Sistema de Gestão Empresarial
                </p>
              </motion.div>
            </CardHeader>
            
            <CardContent className="px-10 pb-10">
              <motion.form 
                onSubmit={handleLogin} 
                className="space-y-8"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.8 }}
              >
                <motion.div 
                  className="space-y-3"
                  whileHover={{ scale: 1.01 }}
                  transition={{ duration: 0.2 }}
                >
                  <Label htmlFor="username" className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <User size={16} className="text-primary" />
                    Usuário
                  </Label>
                  <div className="relative">
                    <Input
                      id="username"
                      type="text"
                      placeholder="Digite seu usuário"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      onFocus={() => setFocusedField('username')}
                      onBlur={() => setFocusedField(null)}
                      required
                      className={`h-14 text-base border-2 transition-all duration-300 bg-background/60 pl-12 rounded-xl ${
                        focusedField === 'username' 
                          ? 'border-primary shadow-lg shadow-primary/20 bg-background/80' 
                          : 'border-border hover:border-primary/50'
                      }`}
                    />
                    <User 
                      size={20} 
                      className={`absolute left-4 top-1/2 transform -translate-y-1/2 transition-colors duration-300 ${
                        focusedField === 'username' ? 'text-primary' : 'text-muted-foreground'
                      }`} 
                    />
                  </div>
                </motion.div>
                
                <motion.div 
                  className="space-y-3"
                  whileHover={{ scale: 1.01 }}
                  transition={{ duration: 0.2 }}
                >
                  <Label htmlFor="password" className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <Lock size={16} className="text-primary" />
                    Senha
                  </Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Digite sua senha"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      onFocus={() => setFocusedField('password')}
                      onBlur={() => setFocusedField(null)}
                      required
                      className={`h-14 text-base border-2 transition-all duration-300 bg-background/60 pl-12 pr-12 rounded-xl ${
                        focusedField === 'password' 
                          ? 'border-primary shadow-lg shadow-primary/20 bg-background/80' 
                          : 'border-border hover:border-primary/50'
                      }`}
                    />
                    <Lock 
                      size={20} 
                      className={`absolute left-4 top-1/2 transform -translate-y-1/2 transition-colors duration-300 ${
                        focusedField === 'password' ? 'text-primary' : 'text-muted-foreground'
                      }`} 
                    />
                    <motion.button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-4 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-primary transition-colors duration-300"
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {showPassword ? <EyeSlash size={20} /> : <Eye size={20} />}
                    </motion.button>
                  </div>
                </motion.div>
                
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  transition={{ duration: 0.2 }}
                >
                  <Button 
                    type="submit" 
                    className="w-full h-14 text-base font-semibold bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 shadow-xl hover:shadow-2xl transition-all duration-300 rounded-xl border-0" 
                    disabled={isLoading}
                  >
                    <motion.span
                      animate={{ opacity: isLoading ? 0.7 : 1 }}
                      transition={{ duration: 0.2 }}
                    >
                      {isLoading ? (
                        <div className="flex items-center gap-3">
                          <motion.div
                            className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full"
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                          />
                          Entrando...
                        </div>
                      ) : (
                        'Entrar'
                      )}
                    </motion.span>
                  </Button>
                </motion.div>
              </motion.form>
              
              {/* Debug info with improved styling */}
              {users && users.length > 0 && (
                <motion.div 
                  className="mt-8"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 1.2 }}
                >
                  <div className="p-6 bg-gradient-to-br from-secondary/40 to-secondary/20 rounded-2xl border border-border/40 backdrop-blur-sm">
                    <p className="text-sm text-muted-foreground mb-4 font-semibold flex items-center gap-2">
                      <Building size={16} className="text-primary" />
                      Usuários disponíveis no sistema:
                    </p>
                    <div className="space-y-3">
                      {users.map(user => (
                        <motion.div 
                          key={user.id} 
                          className="text-sm bg-background/60 p-4 rounded-xl border border-border/30 hover:bg-background/80 transition-all duration-300"
                          whileHover={{ scale: 1.02, y: -2 }}
                          transition={{ duration: 0.2 }}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <strong className="text-foreground text-base">{user.username}</strong>
                              <p className="text-muted-foreground">{user.name} ({user.role})</p>
                            </div>
                            {user.username === 'elvio' && (
                              <span className="px-3 py-1 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white text-xs font-semibold rounded-full">
                                Admin
                              </span>
                            )}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </CardContent>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}
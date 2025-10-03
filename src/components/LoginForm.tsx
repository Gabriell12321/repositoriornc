import { useState } from 'react'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Building, User, Lock } from '@phosphor-icons/react'

interface LoginFormProps {
  onLogin: (userData: {name: string, role: string}) => void
}

export default function LoginForm({ onLogin }: LoginFormProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (isLoading) return
    setIsLoading(true)
    
    if (username === 'elvio' && password === 'admin123') {
      const userData = {
        name: 'Elvio',
        role: 'Administrador'
      }
      onLogin(userData)
    } else {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 to-accent/5 flex items-center justify-center p-4">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <Card className="w-full max-w-md shadow-xl">
          <CardHeader className="text-center space-y-4">
            <motion.div 
              className="mx-auto w-16 h-16 bg-primary rounded-xl flex items-center justify-center"
              initial={{ rotate: -180, scale: 0 }}
              animate={{ rotate: 0, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Building size={32} className="text-primary-foreground" />
            </motion.div>
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.4 }}
            >
              <CardTitle className="text-2xl font-bold text-foreground">4M Contabilidade</CardTitle>
              <CardDescription className="text-muted-foreground">
                Sistema de Gestão Contábil
              </CardDescription>
            </motion.div>
          </CardHeader>
          <CardContent>
            <motion.form 
              onSubmit={handleSubmit} 
              className="space-y-4"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.6 }}
            >
              <div className="space-y-2">
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="username"
                    type="text"
                    placeholder="Nome de usuário"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="pl-10 transition-all duration-200 focus:scale-[1.02]"
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="Senha"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10 transition-all duration-200 focus:scale-[1.02]"
                    required
                  />
                </div>
              </div>
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button 
                  type="submit" 
                  className="w-full transition-all duration-200" 
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <motion.span
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="inline-block mr-2"
                    >
                      ⟳
                    </motion.span>
                  ) : null}
                  {isLoading ? 'Entrando...' : 'Entrar'}
                </Button>
              </motion.div>
            </motion.form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
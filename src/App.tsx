import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import LoginForm from './components/LoginForm'
import Dashboard from './components/Dashboard'
import { ErrorBoundary } from './components/ErrorBoundary'
import { FullPageLoading } from './components/LoadingSpinner'
import { useKV } from '@github/spark/hooks'

function App() {
  const [currentUser, setCurrentUser] = useKV<{name: string, role: string} | null>('current-user', null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Add initialization delay to prevent rapid API calls
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  const handleLogin = useCallback((userData: {name: string, role: string}) => {
    try {
      setCurrentUser(userData)
      setError(null)
    } catch (err) {
      setError('Erro ao fazer login. Tente novamente.')
      console.error('Login error:', err)
    }
  }, [setCurrentUser])

  const handleLogout = useCallback(() => {
    try {
      setCurrentUser(null)
      setError(null)
    } catch (err) {
      setError('Erro ao fazer logout. Tente novamente.')
      console.error('Logout error:', err)
    }
  }, [setCurrentUser])

  const handleRetry = useCallback(() => {
    setError(null)
    setIsLoading(true)
    
    // Add a small delay before retrying to prevent rapid requests
    setTimeout(() => {
      setIsLoading(false)
    }, 2000)
  }, [])

  if (isLoading) {
    return <FullPageLoading message="Iniciando sistema..." />
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <motion.div 
          className="text-center space-y-4 max-w-md"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="space-y-2">
            <h2 className="text-xl font-semibold text-destructive">Ops! Algo deu errado</h2>
            <p className="text-muted-foreground text-sm">{error}</p>
            <p className="text-muted-foreground text-xs">
              Se o problema persistir, aguarde alguns minutos antes de tentar novamente.
            </p>
          </div>
          <motion.button 
            onClick={handleRetry}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors duration-200"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Tentar Novamente
          </motion.button>
        </motion.div>
      </div>
    )
  }

  return (
    <ErrorBoundary>
      <AnimatePresence mode="wait">
        {!currentUser ? (
          <motion.div
            key="login"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <LoginForm onLogin={handleLogin} />
          </motion.div>
        ) : (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Dashboard user={currentUser} onLogout={handleLogout} />
          </motion.div>
        )}
      </AnimatePresence>
    </ErrorBoundary>
  )
}

export default App
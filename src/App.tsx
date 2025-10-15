import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Dashboard from './components/Dashboard'
import LoginInterface from './components/LoginInterface'
import RateLimitDetector from './components/RateLimitDetector'
import { useAuth } from './hooks/useAuth'

export default function App() {
  const [isLoading, setIsLoading] = useState(true)
  const { currentUser, logout } = useAuth()

  // Debug logs for user state changes
  useEffect(() => {
    console.log('App.tsx: currentUser mudou:', currentUser ? currentUser.username : 'null')
  }, [currentUser])

  useEffect(() => {
    // Simulate initial loading
    const timer = setTimeout(() => {
      setIsLoading(false)
      console.log('App.tsx: Loading concluído')
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  const handleLogout = () => {
    console.log('App.tsx: Logout solicitado')
    logout()
  }

  console.log('App.tsx: Renderizando - isLoading:', isLoading, 'currentUser:', currentUser ? currentUser.username : 'null')

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          <p className="text-muted-foreground">Carregando...</p>
        </div>
      </div>
    )
  }

  return (
    <RateLimitDetector>
      <AnimatePresence mode="wait">
        {!currentUser ? (
          <motion.div
            key="login"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <LoginInterface />
          </motion.div>
        ) : (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Dashboard user={{ name: currentUser.name, role: currentUser.role }} onLogout={handleLogout} />
          </motion.div>
        )}
      </AnimatePresence>
    </RateLimitDetector>
  )
}
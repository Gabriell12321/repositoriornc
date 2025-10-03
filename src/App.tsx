import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import LoginForm from './components/LoginForm'
import Dashboard from './components/Dashboard'
import { FullPageLoading } from './components/LoadingSpinner'
import { useKV } from '@github/spark/hooks'

function App() {
  const [currentUser, setCurrentUser] = useKV<{name: string, role: string} | null>('current-user', null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  const handleLogin = useCallback((userData: {name: string, role: string}) => {
    setCurrentUser(userData)
  }, [setCurrentUser])

  const handleLogout = useCallback(() => {
    setCurrentUser(null)
  }, [setCurrentUser])

  if (isLoading) {
    return <FullPageLoading message="Iniciando sistema..." />
  }

  return (
    <div className="min-h-screen">
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
    </div>
  )
}

export default App
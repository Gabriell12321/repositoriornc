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

  // Simple initialization
  useEffect(() => {
    // Just a brief loading to show the loading state, then proceed
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 500)

    return () => clearTimeout(timer)
  }, [])

  const handleLogin = useCallback((userData: {name: string, role: string}) => {
    try {
      setCurrentUser(userData)
    } catch (err) {
      console.error('Login error:', err)
    }
  }, [setCurrentUser])

  const handleLogout = useCallback(() => {
    try {
      setCurrentUser(null)
    } catch (err) {
      console.error('Logout error:', err)
    }
  }, [setCurrentUser])

  if (isLoading) {
    return <FullPageLoading message="Iniciando sistema..." />
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
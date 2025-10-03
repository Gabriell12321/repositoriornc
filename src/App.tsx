import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useKV } from '@github/spark/hooks'
import Dashboard from './components/Dashboard'
import LoginInterface from './components/LoginInterface'
import { FullPageLoading } from './components/LoadingSpinner'
import RateLimitDetector from './components/RateLimitDetector'

export default function App() {
  const [currentUser, setCurrentUser] = useKV<{name: string, role: string} | null>('current-user', null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 500)

    return () => clearTimeout(timer)
  }, [])

  const handleLogout = () => {
    setCurrentUser(null)
  }

  if (isLoading) {
    return <FullPageLoading message="Carregando sistema..." />
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
            <Dashboard user={currentUser} onLogout={handleLogout} />
          </motion.div>
        )}
      </AnimatePresence>
    </RateLimitDetector>
  )
}
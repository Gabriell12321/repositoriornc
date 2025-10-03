import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import LoginForm from './components/LoginForm'
import Dashboard from './components/Dashboard'
import RateLimitWarning from './components/RateLimitWarning'
import { ErrorBoundary } from './components/ErrorBoundary'
import { FullPageLoading } from './components/LoadingSpinner'
import { useKV } from '@github/spark/hooks'

// Utility para controle de rate limiting simples
class SimpleRateLimit {
  private requests: number[] = []
  private maxRequests: number
  private windowMs: number

  constructor(maxRequests: number = 5, windowMs: number = 60000) {
    this.maxRequests = maxRequests
    this.windowMs = windowMs
  }

  canMakeRequest(): boolean {
    const now = Date.now()
    // Remove requests outside the time window
    this.requests = this.requests.filter(timestamp => now - timestamp < this.windowMs)
    return this.requests.length < this.maxRequests
  }

  recordRequest(): void {
    this.requests.push(Date.now())
  }

  getWaitTime(): number {
    if (this.requests.length === 0) return 0
    const oldestRequest = Math.min(...this.requests)
    return Math.max(0, this.windowMs - (Date.now() - oldestRequest))
  }

  reset(): void {
    this.requests = []
  }
}

function App() {
  const [currentUser, setCurrentUser] = useKV<{name: string, role: string} | null>('current-user', null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  
  const rateLimiter = useRef(new SimpleRateLimit(5, 60000)) // Max 5 requests per minute  
  const initRef = useRef(false)
  const maxRetries = 2

  // Safe initialization with rate limiting
  useEffect(() => {
    if (initRef.current) return
    initRef.current = true

    const initialize = async () => {
      try {
        if (!rateLimiter.current.canMakeRequest()) {
          const waitTime = rateLimiter.current.getWaitTime()
          setError(`Muitas tentativas. Aguarde ${Math.ceil(waitTime / 1000)} segundos.`)
          setIsLoading(false)
          return
        }

        rateLimiter.current.recordRequest()
        
        // Add delay with jitter to prevent thundering herd
        const baseDelay = 500 + Math.random() * 1000 // Reduced from 1000-3000 to 500-1500
        const retryDelay = Math.min(baseDelay * Math.pow(1.3, retryCount), 8000) // Reduced multiplier and max delay
        
        await new Promise(resolve => setTimeout(resolve, retryDelay))
        
        setIsLoading(false)
        setError(null)
        setRetryCount(0)
      } catch (err) {
        console.error('Initialization error:', err)
        
        if (retryCount < maxRetries && rateLimiter.current.canMakeRequest()) {
          setRetryCount(prev => prev + 1)
          setError(`Conectando... (tentativa ${retryCount + 1}/${maxRetries})`)
          
          // Exponential backoff for retries
          const retryDelay = Math.min(2000 * Math.pow(2, retryCount), 15000)
          setTimeout(() => {
            initRef.current = false
            initialize()
          }, retryDelay)
        } else {
          setError('Não foi possível conectar. Tente novamente em alguns minutos.')
          setIsLoading(false)
        }
      }
    }

    initialize()
  }, [retryCount])

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
    if (!rateLimiter.current.canMakeRequest()) {
      const waitTime = rateLimiter.current.getWaitTime()
      setError(`Muitas tentativas. Aguarde ${Math.ceil(waitTime / 1000)} segundos.`)
      return
    }

    setError(null)
    setIsLoading(true)
    setRetryCount(0)
    initRef.current = false
    
    // Small delay before retry
    setTimeout(() => {
      if (initRef.current === false) {
        initRef.current = true
        // Trigger re-initialization
        window.location.reload()
      }
    }, 1000)
  }, [])

  if (isLoading) {
    const message = retryCount > 0 
      ? `Reconectando... (${retryCount}/${maxRetries})`
      : "Iniciando sistema..."
    return <FullPageLoading message={message} />
  }

  if (error) {
    const canRetry = rateLimiter.current.canMakeRequest() && retryCount < maxRetries
    const waitTime = rateLimiter.current.getWaitTime()
    
    return (
      <RateLimitWarning
        message={error}
        waitTime={waitTime}
        onRetry={handleRetry}
        canRetry={canRetry}
      />
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
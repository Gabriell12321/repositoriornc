import { useState, useEffect, useCallback, useRef } from 'react'
import { useRateLimiter } from './useRateLimiter'

interface ConnectionState {
  isConnected: boolean
  isConnecting: boolean
  error: string | null
  retryCount: number
  lastConnectionAttempt: number
}

/**
 * Hook para gerenciar conexão e prevenir erro 429
 */
export function useConnection() {
  const [state, setState] = useState<ConnectionState>({
    isConnected: false,
    isConnecting: true,
    error: null,
    retryCount: 0,
    lastConnectionAttempt: 0
  })

  const isInitialized = useRef(false)
  const maxRetries = 5
  const baseDelay = 1000

  // Rate limiter configurado para prevenir erro 429
  const rateLimiter = useRateLimiter({
    maxRequests: 3,
    windowMs: 10000, // 10 segundos
    retryDelay: 2000
  })

  const calculateDelay = useCallback((retryCount: number) => {
    // Exponential backoff with jitter
    const exponentialDelay = baseDelay * Math.pow(2, Math.min(retryCount, 6))
    const jitter = Math.random() * 1000
    return Math.min(exponentialDelay + jitter, 30000) // Max 30 seconds
  }, [])

  const testConnection = useCallback(async (): Promise<boolean> => {
    try {
      // Simulate connection test - replace with actual connectivity check if needed
      await new Promise(resolve => setTimeout(resolve, 500))
      return true
    } catch (error) {
      console.error('Connection test failed:', error)
      return false
    }
  }, [])

  const connect = useCallback(async () => {
    if (!rateLimiter.canMakeRequest()) {
      const waitTime = rateLimiter.getWaitTime()
      setState(prev => ({
        ...prev,
        error: `Muitas tentativas. Aguarde ${Math.ceil(waitTime / 1000)} segundos.`,
        isConnecting: false
      }))
      return
    }

    setState(prev => ({
      ...prev,
      isConnecting: true,
      error: null,
      lastConnectionAttempt: Date.now()
    }))

    try {
      const isConnected = await rateLimiter.makeRequest(testConnection)
      
      if (isConnected) {
        setState(prev => ({
          ...prev,
          isConnected: true,
          isConnecting: false,
          error: null,
          retryCount: 0
        }))
      } else {
        throw new Error('Connection failed')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Connection failed'
      
      setState(prev => {
        const newRetryCount = prev.retryCount + 1
        
        if (newRetryCount >= maxRetries) {
          return {
            ...prev,
            isConnecting: false,
            error: 'Não foi possível conectar. Tente novamente em alguns minutos.',
            retryCount: newRetryCount
          }
        }

        // Schedule automatic retry
        const delay = calculateDelay(newRetryCount)
        setTimeout(() => {
          if (!isInitialized.current) return
          connect()
        }, delay)

        return {
          ...prev,
          isConnecting: false,
          error: `Reconectando... (${newRetryCount}/${maxRetries})`,
          retryCount: newRetryCount
        }
      })
    }
  }, [rateLimiter, testConnection, calculateDelay, maxRetries])

  const reconnect = useCallback(() => {
    setState(prev => ({
      ...prev,
      retryCount: 0,
      error: null
    }))
    rateLimiter.reset()
    connect()
  }, [connect, rateLimiter])

  const disconnect = useCallback(() => {
    setState({
      isConnected: false,
      isConnecting: false,
      error: null,
      retryCount: 0,
      lastConnectionAttempt: 0
    })
    rateLimiter.reset()
  }, [rateLimiter])

  // Initialize connection on mount
  useEffect(() => {
    if (isInitialized.current) return
    isInitialized.current = true

    // Add small random delay to prevent thundering herd
    const initialDelay = Math.random() * 2000 + 1000
    setTimeout(() => {
      if (isInitialized.current) {
        connect()
      }
    }, initialDelay)

    return () => {
      isInitialized.current = false
    }
  }, [connect])

  return {
    ...state,
    connect: reconnect,
    disconnect,
    canRetry: state.retryCount < maxRetries && rateLimiter.canMakeRequest()
  }
}
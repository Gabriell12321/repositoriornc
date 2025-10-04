import { useEffect, useState, ReactNode } from 'react'
import RateLimitWarning from './RateLimitWarning'

interface RateLimitDetectorProps {
  children: ReactNode
}

export default function RateLimitDetector({ children }: RateLimitDetectorProps) {
  const [hasRateLimit, setHasRateLimit] = useState(false)
  const [waitTime, setWaitTime] = useState(0)

  useEffect(() => {
    // Simple check for 429 errors
    const checkFor429 = () => {
      // Check if URL contains 429 or if document title indicates error
      const url = window.location.href
      const title = document.title
      
      if (url.includes('429') || title.includes('429') || title.includes('something went wrong')) {
        setHasRateLimit(true)
        setWaitTime(30000) // 30 seconds
        return true
      }
      return false
    }

    // Check immediately
    if (checkFor429()) return

    // Listen for navigation or error events
    const handlePageError = () => {
      if (checkFor429()) return
    }

    // Simple polling to check for error state - reduced frequency to prevent rate limits
    const errorCheckInterval = setInterval(() => {
      if (document.body?.textContent?.includes('something went wrong') ||
          document.body?.textContent?.includes('429')) {
        setHasRateLimit(true)
        setWaitTime(30000)
        clearInterval(errorCheckInterval)
      }
    }, 5000) // Changed from 2 seconds to 5 seconds

    window.addEventListener('error', handlePageError)
    window.addEventListener('unhandledrejection', handlePageError)
    
    return () => {
      window.removeEventListener('error', handlePageError)
      window.removeEventListener('unhandledrejection', handlePageError)
      clearInterval(errorCheckInterval)
    }
  }, [])

  useEffect(() => {
    if (hasRateLimit && waitTime > 0) {
      const timer = setInterval(() => {
        setWaitTime(prev => {
          if (prev <= 1000) {
            return 0
          }
          return prev - 1000
        })
      }, 1000)

      return () => clearInterval(timer)
    }
  }, [hasRateLimit, waitTime])

  const handleRetry = () => {
    setHasRateLimit(false)
    setWaitTime(0)
    // Try to reload the page
    setTimeout(() => {
      window.location.reload()
    }, 500)
  }

  if (hasRateLimit) {
    return (
      <RateLimitWarning
        message="O sistema detectou um erro de conectividade (Erro 429). Isso geralmente acontece quando há muitas tentativas de acesso simultâneas."
        waitTime={waitTime}
        onRetry={handleRetry}
        canRetry={waitTime <= 5000} // Allow retry when wait time is low
      />
    )
  }

  return <>{children}</>
}
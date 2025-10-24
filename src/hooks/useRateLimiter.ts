import { useRef, useCallback } from 'react'

interface RateLimiterOptions {
  maxRequests: number
  windowMs: number
  retryDelay?: number
}

interface RequestInfo {
  timestamp: number
  count: number
}

/**
 * Hook para controle de rate limiting e prevenção do erro 429
 */
export function useRateLimiter(options: RateLimiterOptions) {
  const { maxRequests, windowMs, retryDelay = 1000 } = options
  const requestsRef = useRef<RequestInfo[]>([])
  const lastRetryRef = useRef<number>(0)

  const canMakeRequest = useCallback((): boolean => {
    const now = Date.now()
    
    // Remove requests outside the time window
    requestsRef.current = requestsRef.current.filter(
      req => now - req.timestamp < windowMs
    )

    // Check if we're under the limit
    const currentRequests = requestsRef.current.reduce(
      (sum, req) => sum + req.count, 0
    )

    return currentRequests < maxRequests
  }, [maxRequests, windowMs])

  const makeRequest = useCallback(async <T>(
    requestFn: () => Promise<T>
  ): Promise<T> => {
    const now = Date.now()

    // Check retry delay
    if (now - lastRetryRef.current < retryDelay) {
      throw new Error('Rate limit: Too many requests. Please wait.')
    }

    if (!canMakeRequest()) {
      lastRetryRef.current = now
      throw new Error('Rate limit exceeded. Please wait before making more requests.')
    }

    // Record this request
    requestsRef.current.push({
      timestamp: now,
      count: 1
    })

    try {
      const result = await requestFn()
      return result
    } catch (error) {
      // If we get a 429, update our retry timer
      if (error instanceof Error && error.message.includes('429')) {
        lastRetryRef.current = now
      }
      throw error
    }
  }, [canMakeRequest, retryDelay])

  const getWaitTime = useCallback((): number => {
    if (requestsRef.current.length === 0) return 0
    
    const now = Date.now()
    const oldestRequest = Math.min(...requestsRef.current.map(r => r.timestamp))
    const waitTime = Math.max(0, windowMs - (now - oldestRequest))
    
    return Math.max(waitTime, retryDelay - (now - lastRetryRef.current))
  }, [windowMs, retryDelay])

  const reset = useCallback(() => {
    requestsRef.current = []
    lastRetryRef.current = 0
  }, [])

  return {
    canMakeRequest,
    makeRequest,
    getWaitTime,
    reset
  }
}
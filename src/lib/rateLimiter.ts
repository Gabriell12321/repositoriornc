/**
 * Simple rate limiter to prevent API abuse
 * Helps avoid 429 (Too Many Requests) errors
 */
class RateLimiter {
  private requests: number[] = []
  private readonly maxRequests: number
  private readonly windowMs: number

  constructor(maxRequests: number = 10, windowMs: number = 60000) {
    this.maxRequests = maxRequests
    this.windowMs = windowMs
  }

  canMakeRequest(): boolean {
    const now = Date.now()
    
    // Remove old requests outside the window
    this.requests = this.requests.filter(time => now - time < this.windowMs)
    
    // Check if we can make a new request
    if (this.requests.length < this.maxRequests) {
      this.requests.push(now)
      return true
    }
    
    return false
  }

  getRemainingRequests(): number {
    const now = Date.now()
    this.requests = this.requests.filter(time => now - time < this.windowMs)
    return Math.max(0, this.maxRequests - this.requests.length)
  }

  getResetTime(): number {
    if (this.requests.length === 0) return 0
    return this.requests[0] + this.windowMs
  }
}

// Global rate limiter instance
const globalRateLimiter = new RateLimiter(10, 60000) // 10 requests per minute

/**
 * Wrapper for API calls with rate limiting
 */
export async function withRateLimit<T>(
  operation: () => Promise<T>,
  errorMessage: string = 'Too many requests. Please wait a moment.'
): Promise<T> {
  if (!globalRateLimiter.canMakeRequest()) {
    throw new Error(errorMessage)
  }

  try {
    return await operation()
  } catch (error) {
    // If we get a 429 error, add extra delay
    if (error instanceof Error && error.message.includes('429')) {
      // Wait a bit before allowing more requests
      await new Promise(resolve => setTimeout(resolve, 5000))
    }
    throw error
  }
}

export { globalRateLimiter }
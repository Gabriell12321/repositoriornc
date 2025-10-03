import { useEffect, useState } from 'react'

/**
 * Debounced hook to prevent rapid consecutive calls
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

/**
 * Throttled hook to limit the frequency of function calls
 */
export function useThrottle<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): T {
  const [isThrottled, setIsThrottled] = useState(false)

  const throttledFunc = ((...args: Parameters<T>) => {
    if (!isThrottled) {
      func(...args)
      setIsThrottled(true)
      setTimeout(() => {
        setIsThrottled(false)
      }, delay)
    }
  }) as T

  return throttledFunc
}

/**
 * Rate-limited state hook to prevent API spam
 */
export function useRateLimitedState<T>(
  initialValue: T,
  delay: number = 500
): [T, (value: T | ((prev: T) => T)) => void] {
  const [value, setValue] = useState<T>(initialValue)
  const [pendingValue, setPendingValue] = useState<T>(initialValue)
  const debouncedValue = useDebounce(pendingValue, delay)

  useEffect(() => {
    setValue(debouncedValue)
  }, [debouncedValue])

  const setRateLimitedValue = (newValue: T | ((prev: T) => T)) => {
    if (typeof newValue === 'function') {
      setPendingValue((prev) => (newValue as (prev: T) => T)(prev))
    } else {
      setPendingValue(newValue)
    }
  }

  return [value, setRateLimitedValue]
}
import { ReactNode, useEffect, useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { LoadingSpinner } from './LoadingSpinner'

interface ChartWrapperProps {
  children: ReactNode
  fallback?: ReactNode
}

export default function ChartWrapper({ children, fallback }: ChartWrapperProps) {
  const [isReady, setIsReady] = useState(false)
  const [hasError, setHasError] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Wait for DOM to be ready and ensure container is mounted
    const checkReady = () => {
      if (containerRef.current && document.readyState === 'complete') {
        setIsReady(true)
      } else {
        setTimeout(checkReady, 50)
      }
    }

    // Wait a bit more for stability
    const timer = setTimeout(checkReady, 200)

    return () => clearTimeout(timer)
  }, [])

  const handleError = (error?: Error) => {
    console.warn('Chart rendering error:', error)
    setHasError(true)
  }

  // Handle SVG rendering errors globally
  useEffect(() => {
    const handleSVGError = (event: Event) => {
      if (event.target instanceof SVGElement || 
          (event.target instanceof HTMLElement && event.target.querySelector('svg'))) {
        handleError(new Error('SVG rendering error'))
      }
    }

    window.addEventListener('error', handleSVGError, true)
    return () => window.removeEventListener('error', handleSVGError, true)
  }, [])

  if (hasError) {
    return (
      <div className="w-full h-[300px] flex items-center justify-center bg-muted/20 rounded-lg border border-dashed border-muted-foreground/20">
        <div className="text-center space-y-3">
          <div className="w-12 h-12 mx-auto bg-muted rounded-full flex items-center justify-center">
            <span className="text-muted-foreground text-lg">📊</span>
          </div>
          <div>
            <p className="text-muted-foreground text-sm font-medium">Gráfico temporariamente indisponível</p>
            <p className="text-muted-foreground text-xs">Os dados estão sendo processados</p>
          </div>
          <button 
            onClick={() => {
              setHasError(false)
              setIsReady(false)
              setTimeout(() => setIsReady(true), 300)
            }}
            className="text-xs text-primary hover:underline transition-colors duration-200"
          >
            Tentar novamente
          </button>
        </div>
      </div>
    )
  }

  if (!isReady) {
    return (
      <div ref={containerRef} className="w-full h-[300px] flex items-center justify-center">
        <LoadingSpinner size="md" message="Carregando gráfico..." />
      </div>
    )
  }

  return (
    <motion.div
      ref={containerRef}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      onError={() => handleError()}
      className="w-full"
    >
      {children}
    </motion.div>
  )
}
import { motion } from 'framer-motion'
import { Warning, Clock, ArrowClockwise } from '@phosphor-icons/react'

interface RateLimitWarningProps {
  message: string
  waitTime?: number
  onRetry?: () => void
  canRetry?: boolean
}

export default function RateLimitWarning({ 
  message, 
  waitTime = 0, 
  onRetry, 
  canRetry = false 
}: RateLimitWarningProps) {
  const formatWaitTime = (seconds: number) => {
    if (seconds < 60) return `${seconds} segundos`
    const minutes = Math.ceil(seconds / 60)
    return `${minutes} minuto${minutes > 1 ? 's' : ''}`
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <motion.div 
        className="text-center space-y-6 max-w-md"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <motion.div
          className="mx-auto w-20 h-20 bg-amber-100 rounded-full flex items-center justify-center"
          initial={{ rotate: -10 }}
          animate={{ rotate: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Warning size={40} className="text-amber-600" />
        </motion.div>

        <div className="space-y-3">
          <h2 className="text-2xl font-semibold text-foreground">
            Sistema Ocupado
          </h2>
          <p className="text-muted-foreground text-sm leading-relaxed">
            {message}
          </p>
          
          {waitTime > 0 && (
            <motion.div 
              className="bg-muted/50 rounded-lg p-4 flex items-center gap-3"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Clock size={20} className="text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                Tente novamente em: <strong>{formatWaitTime(Math.ceil(waitTime / 1000))}</strong>
              </span>
            </motion.div>
          )}

          <div className="text-xs text-muted-foreground bg-muted/30 rounded-lg p-3 text-left">
            <p className="font-medium mb-1">Por que isso acontece?</p>
            <p>
              Para manter o sistema estável e rápido para todos os usuários, 
              limitamos o número de tentativas de conexão simultâneas.
            </p>
          </div>
        </div>

        {onRetry && (
          <motion.button 
            onClick={onRetry}
            disabled={!canRetry}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-all duration-200 ${
              !canRetry
                ? 'bg-muted text-muted-foreground cursor-not-allowed'
                : 'bg-primary text-primary-foreground hover:bg-primary/90 shadow-md hover:shadow-lg'
            }`}
            whileHover={canRetry ? { scale: 1.02 } : {}}
            whileTap={canRetry ? { scale: 0.98 } : {}}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <ArrowClockwise size={16} />
            {!canRetry ? 'Aguarde...' : 'Tentar Novamente'}
          </motion.button>
        )}

        <p className="text-xs text-muted-foreground">
          Se o problema persistir, entre em contato com o suporte técnico
        </p>
      </motion.div>
    </div>
  )
}
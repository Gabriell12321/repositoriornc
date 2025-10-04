import { useKV } from '@github/spark/hooks'
import { DashboardMetrics, RealtimeUpdate } from '@/types'
import { useEffect } from 'react'

export function useRealtime() {
  const [metrics, setMetrics] = useKV<DashboardMetrics>('dashboard-metrics', {
    totalClientes: 0,
    clientesAtivos: 0,
    documentosPendentes: 0,
    vencimentosProximos: 0,
    tarefasPendentes: 0,
    alertasImportantes: 0,
    lastUpdated: new Date().toISOString()
  })

  const [updates, setUpdates] = useKV<RealtimeUpdate[]>('realtime-updates', [])

  const updateMetrics = (newMetrics: Partial<DashboardMetrics>) => {
    setMetrics(current => {
      const defaultMetrics = {
        totalClientes: 0,
        clientesAtivos: 0,
        documentosPendentes: 0,
        vencimentosProximos: 0,
        tarefasPendentes: 0,
        alertasImportantes: 0,
        lastUpdated: new Date().toISOString()
      }
      
      return {
        ...(current || defaultMetrics),
        ...newMetrics,
        lastUpdated: new Date().toISOString()
      }
    })
  }

  const addUpdate = (update: Omit<RealtimeUpdate, 'id' | 'timestamp'>) => {
    const newUpdate: RealtimeUpdate = {
      ...update,
      id: Date.now().toString(),
      timestamp: new Date().toISOString()
    }

    setUpdates(current => [newUpdate, ...(current || [])].slice(0, 50)) // Keep last 50 updates
  }

  const clearUpdates = () => {
    setUpdates([])
  }

  // Remove automatic updates to prevent rate limiting issues
  // In production, use WebSocket or Server-Sent Events for real-time updates

  return {
    metrics,
    updates,
    updateMetrics,
    addUpdate,
    clearUpdates
  }
}
import { createContext, useContext, useEffect, useMemo, useState, useCallback } from 'react'
import { fetchPersonas, fetchSignals, performAction, isMockMode, getMeta } from '../api/client'

const AppContext = createContext(null)

const STORAGE_KEY = 'kbc-signalengine-state'

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

export function AppProvider({ children }) {
  const persisted = loadState()

  const [personas, setPersonas] = useState([])
  const [activePersonaId, setActivePersonaId] = useState(persisted.activePersonaId ?? null)
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [resolved, setResolved] = useState(persisted.resolved ?? {})
  const [history, setHistory] = useState(persisted.history ?? [])

  useEffect(() => {
    let alive = true
    setLoading(true)
    fetchPersonas()
      .then((data) => {
        if (!alive) return
        setPersonas(data)
        setActivePersonaId((current) => current ?? data[0]?.id ?? null)
      })
      .catch((e) => alive && setError(e.message))
      .finally(() => alive && setLoading(false))
    return () => {
      alive = false
    }
  }, [])

  useEffect(() => {
    if (!activePersonaId) return
    let alive = true
    setLoading(true)
    fetchSignals(activePersonaId)
      .then((data) => alive && setSignals(data))
      .catch((e) => alive && setError(e.message))
      .finally(() => alive && setLoading(false))
    return () => {
      alive = false
    }
  }, [activePersonaId])

  useEffect(() => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ activePersonaId, resolved, history }),
    )
  }, [activePersonaId, resolved, history])

  const activePersona = useMemo(
    () => personas.find((p) => p.id === activePersonaId) ?? null,
    [personas, activePersonaId],
  )

  const rankedSignals = useMemo(
    () => [...signals].sort((a, b) => b.signal_score - a.signal_score),
    [signals],
  )

  const signalStatus = useCallback(
    (signalId) => resolved[signalId] ?? 'nieuw',
    [resolved],
  )

  const resolveSignal = useCallback(
    async (signal) => {
      const result = await performAction(activePersonaId, signal.id, signal.solution.action_type)
      setResolved((prev) => ({ ...prev, [signal.id]: result.status }))
      setHistory((prev) => [
        {
          signalId: signal.id,
          title: signal.solution.title,
          cta: signal.solution.cta,
          benefit: signal.solution.estimated_benefit,
          at: new Date().toISOString(),
        },
        ...prev,
      ])
      return result
    },
    [activePersonaId],
  )

  const resetDemo = useCallback(() => {
    setResolved({})
    setHistory([])
  }, [])

  const value = {
    personas,
    activePersona,
    activePersonaId,
    setActivePersonaId,
    signals,
    rankedSignals,
    loading,
    error,
    signalStatus,
    resolveSignal,
    history,
    resetDemo,
    isMockMode,
    meta: getMeta(),
  }

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useApp() {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp moet binnen AppProvider gebruikt worden')
  return ctx
}

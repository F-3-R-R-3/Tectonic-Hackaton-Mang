import { createContext, useContext, useEffect, useMemo, useState, useCallback } from 'react'
import {
  getMe,
  login as apiLogin,
  logout as apiLogout,
  performAction,
} from '../api/client'

const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [user, setUser] = useState(null)
  const [persona, setPersona] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [resolved, setResolved] = useState({})
  const [history, setHistory] = useState([])

  useEffect(() => {
    let alive = true
    getMe()
      .then((data) => {
        if (!alive || !data) return
        setUser(data.user)
        setPersona(data.persona)
      })
      .catch((e) => alive && setError(e.message))
      .finally(() => alive && setLoading(false))
    return () => {
      alive = false
    }
  }, [])

  const login = useCallback(async (username, password) => {
    const account = await apiLogin(username, password)
    setUser(account)
    const data = await getMe()
    setPersona(data.persona)
    setResolved({})
    setHistory([])
    return account
  }, [])

  const logout = useCallback(async () => {
    await apiLogout()
    setUser(null)
    setPersona(null)
    setResolved({})
    setHistory([])
  }, [])

  const rankedSignals = useMemo(
    () => (persona ? [...persona.signals].sort((a, b) => b.signal_score - a.signal_score) : []),
    [persona],
  )

  const signalStatus = useCallback(
    (signalId) => resolved[signalId] ?? 'nieuw',
    [resolved],
  )

  const resolveSignal = useCallback(
    async (signal) => {
      const result = await performAction(persona.id, signal.id, signal.solution.action_type)
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
    [persona],
  )

  const resetDemo = useCallback(() => {
    setResolved({})
    setHistory([])
  }, [])

  const value = {
    user,
    persona,
    activePersona: persona,
    isAuthenticated: Boolean(user),
    rankedSignals,
    loading,
    error,
    signalStatus,
    resolveSignal,
    history,
    resetDemo,
    login,
    logout,
  }

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useApp() {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp moet binnen AppProvider gebruikt worden')
  return ctx
}

/*
 * API-client voor de KBC SignalEngine.
 *
 * De website haalt al haar data uit de echte dataset (data/fake.db) via de
 * Python-API in `src/tectonic_hackaton_mang/server.py`. Er is geen mock meer:
 * de app werkt enkel met de data uit de GitHub-functies.
 *
 * Auth: na login bewaren we een sessietoken (Bearer). De server controleert dat
 * een klant enkel zijn eigen signalen kan opvragen (autorisatie / IDOR).
 *
 * Start de API met:
 *   uv run python -m tectonic_hackaton_mang.server --port 8000
 */
const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
const TOKEN_KEY = 'kbc-signalengine-token'

let token = typeof localStorage !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null

export function getToken() {
  return token
}

function setToken(value) {
  token = value
  if (typeof localStorage === 'undefined') return
  if (value) localStorage.setItem(TOKEN_KEY, value)
  else localStorage.removeItem(TOKEN_KEY)
}

async function request(path, { auth = true, ...options } = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers ?? {}) }
  if (auth && token) headers.Authorization = `Bearer ${token}`

  let res
  try {
    res = await fetch(`${API_BASE}${path}`, { ...options, headers })
  } catch {
    const err = new Error('Geen verbinding met de KBC-API. Draait de server op ' + API_BASE + '?')
    err.status = 0
    throw err
  }

  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err = new Error(data.error ?? `API-fout ${res.status}`)
    err.status = res.status
    throw err
  }
  return data
}

export async function login(username, password) {
  const data = await request('/api/auth/login', {
    auth: false,
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
  setToken(data.token)
  return data.user
}

export async function logout() {
  try {
    if (token) await request('/api/auth/logout', { method: 'POST' })
  } catch {
    /* token toch lokaal wissen */
  }
  setToken(null)
}

export async function getMe() {
  if (!token) return null
  try {
    return await request('/api/me')
  } catch (err) {
    if (err.status === 401) {
      setToken(null)
      return null
    }
    throw err
  }
}

export async function fetchDemoLogins() {
  const data = await request('/api/auth/demo-logins', { auth: false })
  return data.accounts
}

export async function health() {
  return request('/api/health', { auth: false })
}

export async function fetchSignals(personaId) {
  const data = await request(`/api/users/${encodeURIComponent(personaId)}/signals`)
  return data.signals
}

export async function performAction(personaId, signalId, actionType) {
  return request(
    `/api/users/${encodeURIComponent(personaId)}/signals/${encodeURIComponent(signalId)}/act`,
    { method: 'POST', body: JSON.stringify({ action_type: actionType }) },
  )
}

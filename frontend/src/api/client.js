import mockData from '../data/mock.json'

/*
 * API-contract (afgesproken met de back-end / Deel 4):
 *
 *   GET  /users                         -> Persona[]
 *   GET  /users/{id}/signals            -> Signal[]
 *   POST /users/{id}/signals/{sid}/act  -> { status, message }
 *
 * Zolang de FastAPI back-end nog niet klaar is draait alles op mock.json.
 * Zet VITE_USE_MOCK=false in een .env bestand om de echte API te gebruiken.
 */
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'
const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

const LATENCY_MS = 220

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`API-fout ${res.status} op ${path}`)
  }
  return res.json()
}

export async function fetchPersonas() {
  if (USE_MOCK) {
    await delay(LATENCY_MS)
    return mockData.personas
  }
  return request('/users')
}

export async function fetchSignals(personaId) {
  if (USE_MOCK) {
    await delay(LATENCY_MS)
    const persona = mockData.personas.find((p) => p.id === personaId)
    return persona?.signals ?? []
  }
  return request(`/users/${personaId}/signals`)
}

export async function performAction(personaId, signalId, actionType) {
  if (USE_MOCK) {
    await delay(500)
    return {
      status: 'opgelost',
      message: `Actie "${actionType}" uitgevoerd voor signaal ${signalId}.`,
    }
  }
  return request(`/users/${personaId}/signals/${signalId}/act`, {
    method: 'POST',
    body: JSON.stringify({ action_type: actionType }),
  })
}

export function getMeta() {
  return mockData.meta
}

export const isMockMode = USE_MOCK

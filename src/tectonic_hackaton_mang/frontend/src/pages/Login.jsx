import { useEffect, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { fetchDemoLogins } from '../api/client'
import { IconSignal, IconShield, IconArrowRight, IconCheck } from '../components/Icons'

export default function Login() {
  const { login, isAuthenticated, loading } = useApp()
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [accounts, setAccounts] = useState([])

  useEffect(() => {
    fetchDemoLogins()
      .then(setAccounts)
      .catch(() => setAccounts([]))
  }, [])

  if (!loading && isAuthenticated) {
    return <Navigate to="/app" replace />
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await login(username.trim(), password)
      navigate('/app', { replace: true })
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  function fill(account) {
    setUsername(account.username)
    setPassword('')
    setError(null)
  }

  return (
    <div className="login-page">
      <aside className="login-brand">
        <div className="login-brand__inner">
          <span className="eyebrow" style={{ color: '#7fd4f5' }}>
            Mijn KBC
          </span>
          <h1>
            KBC SignalEngine
            <br />
            ziet wat jij mist.
          </h1>
          <p>
            Meld je aan met je KBC-account. We tonen meteen de signalen die op jou
            van toepassing zijn — van herkend probleem tot directe oplossing.
          </p>
          <ul className="login-brand__list">
            <li>
              <IconSignal size={18} /> Gepersonaliseerd per gezin
            </li>
            <li>
              <IconShield size={18} /> Beveiligd: enkel jouw eigen gegevens
            </li>
            <li>
              <IconCheck size={18} /> Eén klik naar de oplossing
            </li>
          </ul>
        </div>
      </aside>

      <main className="login-panel">
        <form className="login-card" onSubmit={handleSubmit}>
          <span className="brand" style={{ color: 'var(--kbc-navy)', marginBottom: 18 }}>
            <span className="brand__mark">
              K<span className="brand__k">B</span>C
            </span>
            SignalEngine
          </span>

          <h2>Welkom terug</h2>
          <p className="muted">Meld je aan om je signalen te bekijken.</p>

          {error && (
            <div className="login-error" role="alert">
              {error}
            </div>
          )}

          <label className="field">
            <span>Gebruikersnaam</span>
            <input
              type="text"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="bv. sofie.janssen"
              required
            />
          </label>

          <label className="field">
            <span>Wachtwoord</span>
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Je wachtwoord"
              required
            />
          </label>

          <button className="btn btn--block btn--lg" type="submit" disabled={busy}>
            {busy ? 'Aanmelden…' : (
              <>
                Aanmelden <IconArrowRight size={18} />
              </>
            )}
          </button>

          {accounts.length > 0 && (
            <details className="login-demo">
              <summary>Demo-accounts ({accounts.length})</summary>
              <p className="soft">Klik een gezin om de gebruikersnaam in te vullen.</p>
              <ul>
                {accounts.map((a) => (
                  <li key={a.username}>
                    <button type="button" onClick={() => fill(a)}>
                      <strong>{a.name}</strong>
                      <span>{a.persona_label}</span>
                      <code>{a.username}</code>
                    </button>
                  </li>
                ))}
              </ul>
              <p className="soft">
                Wachtwoorden: <code>Voornaam2026!</code> (bv. <code>Sofie2026!</code>)
              </p>
            </details>
          )}

          <p className="login-legal">
            Dit is een demo op synthetische data. Gebruik geen echte
            KBC-gegevens.
          </p>
        </form>
      </main>
    </div>
  )
}

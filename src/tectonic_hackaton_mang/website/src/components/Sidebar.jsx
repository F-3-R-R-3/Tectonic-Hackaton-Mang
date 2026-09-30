import { NavLink, useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import {
  IconHome,
  IconCard,
  IconSend,
  IconPiggy,
  IconShield,
  IconSignal,
} from './Icons'

export default function Sidebar() {
  const { persona, user, rankedSignals, signalStatus, resetDemo, logout } = useApp()
  const navigate = useNavigate()

  const openCount = rankedSignals.filter((s) => signalStatus(s.id) !== 'opgelost').length

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <aside className="sidebar">
      <div className="account-card">
        <div className="account-card__top">
          <div className="avatar">{persona?.initials ?? '??'}</div>
          <div>
            <strong>{persona?.name ?? user?.name}</strong>
            <span>{persona?.persona_label ?? user?.persona_label}</span>
          </div>
        </div>
        <div className="account-card__meta">
          <span>@{user?.username}</span>
          {persona?.city && <span>{persona.city}</span>}
        </div>
        <button className="btn btn--light btn--sm btn--block" type="button" onClick={handleLogout}>
          Afmelden
        </button>
      </div>

      <nav className="side-nav">
        <div className="side-nav__label">Mijn KBC</div>
        <NavLink to="/app" end>
          <IconHome size={18} />
          Overzicht
        </NavLink>
        <NavLink to="/app?tab=rekeningen">
          <IconCard size={18} />
          Rekeningen
        </NavLink>
        <NavLink to="/app?tab=betalingen">
          <IconSend size={18} />
          Betalingen
        </NavLink>
        <NavLink to="/app?tab=sparen">
          <IconPiggy size={18} />
          Sparen
        </NavLink>
        <NavLink to="/app?tab=verzekeringen">
          <IconShield size={18} />
          Verzekeringen
        </NavLink>
        <div className="side-nav__label" style={{ marginTop: 6 }}>
          SignalEngine
        </div>
        <NavLink to="/app" end>
          <IconSignal size={18} />
          Signalen
          {openCount > 0 && <span className="pill">{openCount}</span>}
        </NavLink>
      </nav>

      <button className="btn btn--ghost btn--sm btn--block" type="button" onClick={resetDemo}>
        Demo resetten
      </button>
    </aside>
  )
}

import { NavLink } from 'react-router-dom'
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
  const {
    personas,
    activePersonaId,
    setActivePersonaId,
    rankedSignals,
    signalStatus,
    resetDemo,
  } = useApp()

  const openCount = rankedSignals.filter((s) => signalStatus(s.id) !== 'opgelost').length

  return (
    <aside className="sidebar">
      <div className="persona-switch">
        <h4>Demo-persona</h4>
        <label className="sr-only" htmlFor="persona">
          Kies persona
        </label>
        <select
          id="persona"
          value={activePersonaId ?? ''}
          onChange={(e) => setActivePersonaId(e.target.value)}
        >
          {personas.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} — {p.persona_label}
            </option>
          ))}
        </select>
        <p className="persona-switch__hint">
          Wissel van klant om de personalisatie te tonen (Deel 4).
        </p>
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

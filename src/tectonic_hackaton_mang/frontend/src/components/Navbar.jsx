import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { IconSearch, IconBell, IconMenu, IconClose } from './Icons'

const NAV = [
  { to: '/app', label: 'Mijn KBC', end: true },
  { to: '/app?tab=betalingen', label: 'Betalingen' },
  { to: '/app?tab=sparen', label: 'Sparen & Beleggen' },
  { to: '/app?tab=verzekeringen', label: 'Verzekeringen' },
]

export default function Navbar() {
  const { activePersona } = useApp()
  const [open, setOpen] = useState(false)

  return (
    <header className={`site-header ${open ? 'is-open' : ''}`}>
      <div className="container site-header__inner">
        <Link to="/" className="brand" onClick={() => setOpen(false)}>
          <span className="brand__mark">
            K<span className="brand__k">B</span>C
          </span>
          SignalEngine
        </Link>

        <nav className="site-nav">
          {NAV.map((item) => (
            <NavLink
              key={item.label}
              to={item.to}
              className={({ isActive }) => (isActive && item.to === '/app' ? 'is-active' : '')}
              onClick={() => setOpen(false)}
            >
              {item.label}
            </NavLink>
          ))}
          <NavLink to="/app" className="is-active" onClick={() => setOpen(false)}>
            SignalEngine
          </NavLink>
        </nav>

        <div className="site-header__right">
          <label className="header-search">
            <IconSearch size={16} />
            <input placeholder="Zoek in Mijn KBC" aria-label="Zoeken" />
          </label>
          <button className="btn btn--ghost btn--sm" type="button" style={{ borderColor: 'rgba(255,255,255,.25)', color: '#fff' }}>
            <IconBell size={16} />
            Meldingen
          </button>
          {activePersona && (
            <div className="header-user">
              <div className="header-user__name">
                {activePersona.name}
                <div className="header-user__sub">{activePersona.persona_label}</div>
              </div>
              <div className="avatar">{activePersona.initials}</div>
            </div>
          )}
          <button
            className="nav-toggle"
            type="button"
            aria-label="Menu"
            onClick={() => setOpen((v) => !v)}
          >
            {open ? <IconClose /> : <IconMenu />}
          </button>
        </div>
      </div>
    </header>
  )
}

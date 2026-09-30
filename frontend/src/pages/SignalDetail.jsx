import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import ScoreRing from '../components/ScoreRing'
import FlowStepper from '../components/FlowStepper'
import ActionModal from '../components/ActionModal'
import {
  categoryIcon,
  IconSignal,
  IconProblem,
  IconSolution,
  IconArrowLeft,
  IconArrowRight,
  IconCheck,
} from '../components/Icons'

const IMPACT_LABEL = { hoog: 'Hoge impact', middel: 'Gemiddelde impact', laag: 'Lage impact' }
const URGENCY_LABEL = { hoog: 'Dringend', middel: 'Binnenkort', laag: 'Rustig' }
const CATEGORY_LABEL = {
  slapend_geld: 'Slapend geld',
  mobiliteit: 'Mobiliteit',
  sparen: 'Sparen',
  administratie: 'Administratie',
}

function Trend({ trend }) {
  const map = { up: '↑', down: '↓', flat: '→' }
  return <span className={`trend trend--${trend}`}>{map[trend] ?? ''}</span>
}

export default function SignalDetail() {
  const { signalId } = useParams()
  const navigate = useNavigate()
  const { rankedSignals, loading, signalStatus, resolveSignal, activePersona } = useApp()
  const [modalOpen, setModalOpen] = useState(false)

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        Laden…
      </div>
    )
  }

  const signal = rankedSignals.find((s) => s.id === signalId)

  if (!signal) {
    return (
      <div className="empty">
        <h2>Signaal niet gevonden</h2>
        <p>Dit signaal bestaat niet (meer) voor deze klant.</p>
        <Link to="/app" className="btn">
          Terug naar overzicht
        </Link>
      </div>
    )
  }

  const CatIcon = categoryIcon(signal.category)
  const done = signalStatus(signal.id) === 'opgelost'

  return (
    <div className="stack">
      <div className="breadcrumb">
        <Link to="/app">SignalEngine</Link>
        <span>/</span>
        <span>{CATEGORY_LABEL[signal.category]}</span>
        <span>/</span>
        <span className="muted">{signal.title}</span>
      </div>

      <button className="btn btn--ghost btn--sm" type="button" onClick={() => navigate('/app')} style={{ alignSelf: 'flex-start' }}>
        <IconArrowLeft size={16} /> Terug naar overzicht
      </button>

      <div className="detail-head">
        <ScoreRing score={signal.signal_score} />
        <div>
          <div className="row" style={{ marginBottom: 8 }}>
            <span className="chip chip--blue">
              <CatIcon size={14} /> {CATEGORY_LABEL[signal.category]}
            </span>
            <span className={`chip chip--${signal.impact === 'hoog' ? 'red' : signal.impact === 'middel' ? 'orange' : 'blue'}`}>
              {IMPACT_LABEL[signal.impact]}
            </span>
            <span className="chip">{URGENCY_LABEL[signal.urgency]}</span>
          </div>
          <h1>{signal.title}</h1>
          <p>Gedetecteerd op {signal.detected_at} voor {activePersona?.name}</p>
        </div>
      </div>

      <FlowStepper active={3} />

      {/* 1. SIGNAAL */}
      <section className="flow-block">
        <span className="flow-block__tag">
          <IconSignal size={16} /> Stap 1 · Signaal
        </span>
        <h2>{signal.signal.headline}</h2>
        <p>{signal.signal.summary}</p>
        <div className="evidence">
          {signal.signal.evidence.map((e) => (
            <div className="evidence__row" key={e.label}>
              <span className="evidence__label">{e.label}</span>
              <span className="evidence__value">
                {e.value} <Trend trend={e.trend} />
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* 2. PROBLEEM */}
      <section className="flow-block flow-block--problem">
        <span className="flow-block__tag">
          <IconProblem size={16} /> Stap 2 · Probleem
        </span>
        <h2>{signal.problem.headline}</h2>
        <p>{signal.problem.description}</p>
        <span className="impact-banner">
          <IconProblem size={16} /> {signal.problem.impact_label}
        </span>
        <ul className="consequence-list">
          {signal.problem.consequences.map((c) => (
            <li key={c}>{c}</li>
          ))}
        </ul>
      </section>

      {/* 3. OPLOSSING */}
      <section className="flow-block flow-block--solution">
        <span className="flow-block__tag">
          <IconSolution size={16} /> Stap 3 · Oplossing
        </span>
        <h2>{signal.solution.title}</h2>
        <p>{signal.solution.description}</p>
        <ol className="solution-steps">
          {signal.solution.steps.map((s) => (
            <li key={s}>{s}</li>
          ))}
        </ol>

        <div className="solution-cta">
          {done ? (
            <div className="done-banner" style={{ margin: 0, flex: 1 }}>
              <div className="check-circle">
                <IconCheck size={20} />
              </div>
              <div>
                <h3>Deze oplossing is al uitgevoerd</h3>
                <p>{signal.solution.estimated_benefit}</p>
              </div>
            </div>
          ) : (
            <>
              <button className="btn btn--lg" type="button" onClick={() => setModalOpen(true)}>
                {signal.solution.cta} <IconArrowRight size={18} />
              </button>
              <span className="chip chip--green">{signal.solution.estimated_benefit}</span>
            </>
          )}
        </div>
      </section>

      {modalOpen && (
        <ActionModal
          signal={signal}
          onClose={() => setModalOpen(false)}
          onConfirm={resolveSignal}
        />
      )}
    </div>
  )
}

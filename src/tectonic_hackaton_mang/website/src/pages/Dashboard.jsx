import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import SignalCard from '../components/SignalCard'
import FlowStrip from '../components/FlowStrip'
import KateFab from '../components/KateFab'
import { IconSignal, IconCheck, IconEuro } from '../components/Icons'

function Loading() {
  return (
    <div className="loading">
      <div className="spinner" />
      Signalen ophalen…
    </div>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const {
    activePersona,
    rankedSignals,
    loading,
    signalStatus,
    history,
    user,
  } = useApp()

  if (loading || !activePersona) return <Loading />

  const open = rankedSignals.filter((s) => signalStatus(s.id) !== 'opgelost')
  const done = rankedSignals.filter((s) => signalStatus(s.id) === 'opgelost')
  const topScore = rankedSignals[0]?.signal_score ?? 0

  const kateText = open.length
    ? `Hallo ${activePersona.name}. Ik zie ${open.length} signalen voor jou. Het belangrijkste is: ${open[0].title}. ${open[0].problem.headline}. Ik stel voor: ${open[0].solution.cta}.`
    : `Hallo ${activePersona.name}. Er zijn momenteel geen open signalen. Alles is opgelost.`

  return (
    <div className="stack">
      <div className="hero">
        <div className="row" style={{ justifyContent: 'space-between' }}>
          <span className="eyebrow" style={{ color: '#7fd4f5' }}>
            KBC SignalEngine
          </span>
          <span className="chip chip--green">Live data · data/fake.db</span>
        </div>
        <h1>Hallo {activePersona.name.split(' ')[0]}, we zagen {open.length} dingen voor jou</h1>
        <p>
          Hieronder staat wat we detecteerden, wat het probleem is en hoe we het
          meteen oplossen. Je hoeft alleen te beslissen.
        </p>
        <div className="hero__chips">
          <span className="chip">{activePersona.persona_label}</span>
          <span className="chip">
            {activePersona.city} · {activePersona.age} jaar
          </span>
          {activePersona.why_persona.map((w) => (
            <span className="chip" key={w}>
              {w}
            </span>
          ))}
          {user && <span className="chip">@{user.username}</span>}
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat">
          <div className="stat__label">Open signalen</div>
          <div className="stat__value">
            {open.length} <small>van {rankedSignals.length}</small>
          </div>
        </div>
        <div className="stat">
          <div className="stat__label">Hoogste signaalscore</div>
          <div className="stat__value">
            {topScore} <small>/ 100</small>
          </div>
        </div>
        <div className="stat">
          <div className="stat__label">Afgehandeld in deze sessie</div>
          <div className="stat__value">{done.length}</div>
        </div>
      </div>

      <FlowStrip />

      <div className="section-head">
        <h2>
          <IconSignal size={20} /> Gedetecteerde signalen
        </h2>
        <span className="chip chip--blue">
          Gerangschikt op impact × urgentie
        </span>
      </div>

      {open.length === 0 ? (
        <div className="card card--pad empty">
          <div className="check-circle" style={{ margin: '0 auto 12px' }}>
            <IconCheck />
          </div>
          <h3>Geen open signalen</h3>
          <p>Je bent helemaal bij. We melden ons zodra er iets verandert.</p>
        </div>
      ) : (
        <div className="signal-list">
          {open.map((signal) => (
            <SignalCard
              key={signal.id}
              signal={signal}
              status={signalStatus(signal.id)}
              onOpen={(id) => navigate(`/app/signaal/${id}`)}
            />
          ))}
        </div>
      )}

      {done.length > 0 && (
        <>
          <div className="section-head" style={{ marginTop: 10 }}>
            <h2>
              <IconCheck size={20} /> Opgelost
            </h2>
          </div>
          <div className="signal-list">
            {done.map((signal) => (
              <SignalCard
                key={signal.id}
                signal={signal}
                status="opgelost"
                onOpen={(id) => navigate(`/app/signaal/${id}`)}
              />
            ))}
          </div>
        </>
      )}

      {history.length > 0 && (
        <>
          <div className="section-head" style={{ marginTop: 10 }}>
            <h2>
              <IconEuro size={20} /> Uitgevoerde acties
            </h2>
          </div>
          <div className="card card--pad">
            <div className="stack" style={{ gap: 12 }}>
              {history.map((h, i) => (
                <div className="evidence__row" key={`${h.signalId}-${i}`}>
                  <span className="evidence__label">{h.title}</span>
                  <span className="evidence__value">{h.benefit}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      <KateFab text={kateText} />
    </div>
  )
}

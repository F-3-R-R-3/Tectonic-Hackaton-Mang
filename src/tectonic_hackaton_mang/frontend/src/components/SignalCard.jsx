import ScoreRing from './ScoreRing'
import { categoryIcon, IconArrowRight, IconCheck } from './Icons'

const IMPACT_LABEL = { hoog: 'Hoge impact', middel: 'Gemiddelde impact', laag: 'Lage impact' }
const URGENCY_LABEL = { hoog: 'Dringend', middel: 'Binnenkort', laag: 'Rustig' }
const CATEGORY_LABEL = {
  slapend_geld: 'Slapend geld',
  mobiliteit: 'Mobiliteit',
  sparen: 'Sparen',
  administratie: 'Administratie',
}

export default function SignalCard({ signal, status, onOpen }) {
  const CatIcon = categoryIcon(signal.category)
  const done = status === 'opgelost'

  return (
    <article
      className={`signal-card signal-card--${signal.impact} ${done ? 'signal-card--done' : ''}`}
      onClick={() => onOpen(signal.id)}
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onOpen(signal.id)}
      role="button"
      tabIndex={0}
    >
      <div className={`signal-card__cat cat--${signal.category}`}>
        <CatIcon size={24} />
      </div>

      <div className="signal-card__body">
        <h3 className="signal-card__title">{signal.title}</h3>
        <p className="signal-card__summary">{signal.signal.summary}</p>

        <div className="signal-card__tags">
          <span className={`chip chip--${signal.impact === 'hoog' ? 'red' : signal.impact === 'middel' ? 'orange' : 'blue'}`}>
            {IMPACT_LABEL[signal.impact]}
          </span>
          <span className="chip">{URGENCY_LABEL[signal.urgency]}</span>
          <span className="chip chip--blue">{CATEGORY_LABEL[signal.category]}</span>
          {done && (
            <span className="chip chip--green">
              <IconCheck size={13} /> Opgelost
            </span>
          )}
        </div>
      </div>

      <div className="signal-card__side">
        <ScoreRing score={signal.signal_score} />
        <span className="signal-card__impact">{signal.problem.impact_label}</span>
        <span className="signal-card__arrow">
          <IconArrowRight />
        </span>
      </div>
    </article>
  )
}

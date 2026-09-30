import { useState } from 'react'
import { categoryIcon, IconCheck, IconArrowRight, IconClose } from './Icons'

export default function ActionModal({ signal, onClose, onConfirm }) {
  const [phase, setPhase] = useState('confirm')
  const CatIcon = categoryIcon(signal.category)

  async function handleConfirm() {
    setPhase('working')
    try {
      await onConfirm(signal)
      setPhase('done')
    } catch {
      setPhase('confirm')
    }
  }

  return (
    <div className="overlay" onClick={onClose} role="presentation">
      <div
        className={`modal ${phase === 'done' ? 'modal--success' : ''}`}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        {phase === 'done' ? (
          <>
            <div className="modal__icon">
              <IconCheck size={28} />
            </div>
            <h2 id="modal-title">Geregeld!</h2>
            <p>
              {signal.solution.title} is uitgevoerd. {signal.solution.estimated_benefit}. Je
              krijgt een bevestiging in Mijn KBC.
            </p>
            <div className="done-banner" style={{ marginTop: 6 }}>
              <div className="check-circle">
                <IconCheck size={20} />
              </div>
              <div>
                <h3>Signaal afgehandeld</h3>
                <p>We laten dit signaal niet opnieuw zien tenzij er iets verandert.</p>
              </div>
            </div>
            <div className="modal__actions">
              <button className="btn btn--success" type="button" onClick={onClose}>
                Terug naar overzicht
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="modal__icon">
              <CatIcon size={28} />
            </div>
            <h2 id="modal-title">{signal.solution.cta}</h2>
            <p>{signal.solution.description}</p>

            <div className="evidence" style={{ gridTemplateColumns: '1fr' }}>
              <div className="evidence__row">
                <span className="evidence__label">Oplossing</span>
                <span className="evidence__value">{signal.solution.title}</span>
              </div>
              <div className="evidence__row">
                <span className="evidence__label">Voordeel</span>
                <span className="evidence__value">{signal.solution.estimated_benefit}</span>
              </div>
            </div>

            <div className="modal__actions">
              <button className="btn btn--ghost" type="button" onClick={onClose} disabled={phase === 'working'}>
                Annuleren
              </button>
              <button className="btn" type="button" onClick={handleConfirm} disabled={phase === 'working'}>
                {phase === 'working' ? 'Bezig…' : (
                  <>
                    Bevestig <IconArrowRight size={16} />
                  </>
                )}
              </button>
            </div>
          </>
        )}
        <button
          className="sr-only"
          type="button"
          onClick={onClose}
          aria-label="Sluiten"
        >
          <IconClose />
        </button>
      </div>
    </div>
  )
}

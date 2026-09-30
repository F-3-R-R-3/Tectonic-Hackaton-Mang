import { Link } from 'react-router-dom'
import {
  IconSolution,
  IconArrowRight,
  IconShield,
  IconSparkle,
} from '../components/Icons'

export default function Landing() {
  return (
    <>
      <section className="landing-hero" id="top">
        <div className="container landing-hero__grid">
          <div>
            <span className="eyebrow" style={{ color: '#7fd4f5' }}>
              Nieuw in Mijn KBC
            </span>
            <h1>
              KBC SignalEngine ziet wat jij mist.
              <br />
              En lost het meteen op.
            </h1>
            <p className="lead">
              We analyseren je transacties, abonnementen, profiel en zoekgedrag om
              herkenbare situaties te detecteren. Elk signaal vertalen we naar het
              echte probleem — met één concrete oplossing.
            </p>
            <div className="landing-actions">
              <Link to="/app" className="btn btn--light btn--lg">
                Open mijn SignalEngine <IconArrowRight size={18} />
              </Link>
            </div>
            <div className="landing-stats">
              <div>
                <strong>2,3M</strong>
                <span>KBC-klanten</span>
              </div>
              <div>
                <strong>4</strong>
                <span>signaaltypes</span>
              </div>
              <div>
                <strong>1 klik</strong>
                <span>naar de oplossing</span>
              </div>
            </div>
          </div>

          <div>
            <div className="phone">
              <div className="phone__screen">
                <div className="phone__bar">
                  <small>Goedemorgen</small>
                  <strong>Familie De Smet</strong>
                </div>
                <div className="phone__body">
                  <div className="phone__sig phone__sig--warn">
                    <b>Verhuizing gedetecteerd</b>
                    <span>3 polissen staan nog op je oude adres</span>
                  </div>
                  <div className="phone__sig">
                    <b>Autokost onoverzichtelijk</b>
                    <span>€ 52 / maand te veel</span>
                  </div>
                  <div className="phone__sig phone__sig--good">
                    <b>Abonnementen-audit</b>
                    <span>€ 132 / jaar terug</span>
                  </div>
                  <div className="phone__sig">
                    <b>Dynamisch spaarplan</b>
                    <span>Start in 1 klik</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="landing-section landing-section--alt">
        <div className="container">
          <div className="center">
            <span className="eyebrow" style={{ justifyContent: 'center' }}>
              Waarom
            </span>
            <h2>Gebouwd rond de klant, niet rond producten</h2>
          </div>
          <div className="feature-grid">
            <div className="feature">
              <div className="feature__ico">
                <IconSparkle size={24} />
              </div>
              <h3>Gepersonaliseerd</h3>
              <p>
                Een student krijgt andere signalen dan een gezin of een gepensioneerde.
                SignalEngine rangschikt op impact en urgentie.
              </p>
            </div>
            <div className="feature">
              <div className="feature__ico">
                <IconShield size={24} />
              </div>
              <h3>Privacy-veilig</h3>
              <p>
                Alles draait op synthetische data met een vaste seed. Geen echte
                klantgegevens, volledig reproduceerbaar.
              </p>
            </div>
            <div className="feature">
              <div className="feature__ico">
                <IconSolution size={24} />
              </div>
              <h3>Altijd een actie</h3>
              <p>
                Geen melding zonder oplossing. Elk signaal eindigt in een knop die
                het probleem meteen wegneemt.
              </p>
            </div>
          </div>

          <div className="cta-band">
            <div>
              <h2>Klaar om je eigen signalen te zien?</h2>
              <p>Kies een demo-persona en doorloop de volledige flow.</p>
            </div>
            <Link to="/app" className="btn btn--light btn--lg">
              Start de demo <IconArrowRight size={18} />
            </Link>
          </div>
        </div>
      </section>
    </>
  )
}

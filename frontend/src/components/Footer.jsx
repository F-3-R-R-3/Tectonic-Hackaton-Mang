import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container">
        <div className="site-footer__grid">
          <div className="site-footer__brand">
            <Link to="/" className="brand" style={{ marginBottom: 12 }}>
              <span className="brand__mark">
                K<span className="brand__k">B</span>C
              </span>
              SignalEngine
            </Link>
            <p>
              Proof-of-concept voor de Tectonic Hackathon 2026. Van signaal naar
              probleem naar oplossing, rechtstreeks in Mijn KBC.
            </p>
          </div>
          <div>
            <h5>Producten</h5>
            <a href="#top">Rekeningen</a>
            <a href="#top">Betalingen</a>
            <a href="#top">Sparen &amp; Beleggen</a>
            <a href="#top">Verzekeringen</a>
          </div>
          <div>
            <h5>SignalEngine</h5>
            <a href="#top">Hoe het werkt</a>
            <a href="#top">Signalen</a>
            <a href="#top">Privacy</a>
            <a href="#top">Veiligheid</a>
          </div>
          <div>
            <h5>Over</h5>
            <a href="#top">Over KBC</a>
            <a href="#top">Contact</a>
            <a href="#top">Jobs</a>
            <a href="#top">Cookiebeleid</a>
          </div>
        </div>
        <div className="site-footer__bottom">
          <span>© 2026 KBC SignalEngine — demo, geen echte bankgegevens.</span>
          <span>Synthetische data · vaste seed · privacy-veilig</span>
        </div>
      </div>
    </footer>
  )
}

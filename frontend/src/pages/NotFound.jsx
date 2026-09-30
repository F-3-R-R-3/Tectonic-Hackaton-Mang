import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="container">
      <div className="empty" style={{ padding: '120px 20px' }}>
        <h1>Pagina niet gevonden</h1>
        <p>Deze pagina bestaat niet in Mijn KBC.</p>
        <Link to="/app" className="btn">
          Naar SignalEngine
        </Link>
      </div>
    </div>
  )
}

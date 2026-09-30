export default function ScoreRing({ score, label = 'signaalscore' }) {
  const level = score >= 80 ? 'high' : score >= 60 ? 'mid' : 'low'
  return (
    <div
      className={`score score--${level}`}
      style={{ '--pct': score }}
      role="img"
      aria-label={`${label}: ${score} van 100`}
      title={`${label}: ${score}/100`}
    >
      <span className="score__inner">{score}</span>
    </div>
  )
}

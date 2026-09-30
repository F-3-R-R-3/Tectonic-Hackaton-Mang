export default function FlowStrip() {
  const steps = [
    {
      n: '1',
      title: 'Signaal',
      text: 'We detecteren iets opvallends in je transacties, profiel of zoekgedrag.',
    },
    {
      n: '2',
      title: 'Probleem',
      text: 'We vertalen het signaal naar het echte risico of geldverlies voor jou.',
    },
    {
      n: '3',
      title: 'Oplossing',
      text: 'Eén concrete actie die het meteen oplost — jij klikt, wij regelen.',
    },
  ]
  return (
    <div className="flow-strip">
      {steps.map((s) => (
        <div className="flow-strip__item" key={s.n}>
          <div className="flow-strip__num">{s.n}</div>
          <h4>{s.title}</h4>
          <p>{s.text}</p>
        </div>
      ))}
    </div>
  )
}

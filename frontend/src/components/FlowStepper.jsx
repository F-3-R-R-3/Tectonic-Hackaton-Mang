export default function FlowStepper({ active = 3 }) {
  const steps = ['Signaal', 'Probleem', 'Oplossing']
  return (
    <div className="stepper" aria-label="Signaal naar oplossing">
      {steps.map((label, i) => (
        <div className={`step ${i < active ? 'step--done' : ''}`} key={label}>
          <div className="step__dot">{i + 1}</div>
          <div className="step__label">{label}</div>
          <div className="step__line" />
        </div>
      ))}
    </div>
  )
}

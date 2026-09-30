import { useEffect, useRef, useState } from 'react'
import { IconMic } from './Icons'

export default function KateFab({ text }) {
  const [speaking, setSpeaking] = useState(false)
  const supported = typeof window !== 'undefined' && 'speechSynthesis' in window
  const utterRef = useRef(null)

  useEffect(() => {
    return () => {
      if (supported) window.speechSynthesis.cancel()
    }
  }, [supported])

  function toggle() {
    if (!supported) return
    if (speaking) {
      window.speechSynthesis.cancel()
      setSpeaking(false)
      return
    }
    const u = new SpeechSynthesisUtterance(text)
    u.lang = 'nl-BE'
    u.rate = 1
    u.onend = () => setSpeaking(false)
    u.onerror = () => setSpeaking(false)
    utterRef.current = u
    window.speechSynthesis.cancel()
    window.speechSynthesis.speak(u)
    setSpeaking(true)
  }

  return (
    <button
      className={`kate-fab ${speaking ? 'is-speaking' : ''}`}
      type="button"
      onClick={toggle}
      title={supported ? 'Laat Kate de signalen voorlezen' : 'Spraak niet ondersteund'}
      disabled={!supported}
    >
      <span className="kate-fab__dot">
        <IconMic size={16} />
      </span>
      {speaking ? 'Kate stopt' : 'Kate leest voor'}
    </button>
  )
}

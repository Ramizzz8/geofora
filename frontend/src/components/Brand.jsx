import { useEffect, useState } from 'react'

const NAME = 'GEOFORA'
const STORAGE_KEY = 'geofora:titulo'
const VARIANTS = { orbita: 'Órbita', coordenadas: 'Coordenadas' }
const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&@'
const SCRAMBLE_MS = 45

export function formatCoords(lat, lng) {
  const ns = lat >= 0 ? 'N' : 'S'
  const eo = lng >= 0 ? 'E' : 'O'
  return `${Math.abs(lat).toFixed(2)}° ${ns} · ${Math.abs(lng).toFixed(2)}° ${eo}`
}

function readVariant() {
  try {
    const v = localStorage.getItem(STORAGE_KEY)
    return v in VARIANTS ? v : 'orbita'
  } catch {
    return 'orbita'
  }
}

// La "O" de GEO convertida en un planeta con un satélite en órbita
function OrbitO() {
  return (
    <svg className="orbit-o" viewBox="0 0 100 100" aria-hidden="true">
      <defs>
        <radialGradient id="planet" cx="35%" cy="32%" r="75%">
          <stop offset="0%" stopColor="#9fd4ff" />
          <stop offset="55%" stopColor="#2f6fd6" />
          <stop offset="100%" stopColor="#0a1a44" />
        </radialGradient>
      </defs>
      <circle cx="50" cy="50" r="30" fill="url(#planet)" />
      <path id="orbit" d="M 6 50 a 44 16 -20 1 0 88 0 a 44 16 -20 1 0 -88 0" fill="none"
        stroke="rgba(160, 200, 255, 0.45)" strokeWidth="2" transform="rotate(-20 50 50)" />
      <circle r="5" fill="#ffd27a">
        <animateMotion dur="6s" repeatCount="indefinite" rotate="auto">
          <mpath href="#orbit" />
        </animateMotion>
      </circle>
    </svg>
  )
}

function useScramble(active) {
  const [text, setText] = useState(NAME)
  useEffect(() => {
    if (!active) return setText(NAME)
    let frame = 0
    const id = setInterval(() => {
      frame += 1
      const solved = Math.floor(frame / 3) // cada letra se descifra tras 3 cambios
      setText(NAME.split('').map((ch, i) => (i < solved ? ch : GLYPHS[(frame * 7 + i * 13) % GLYPHS.length])).join(''))
      if (solved >= NAME.length) clearInterval(id)
    }, SCRAMBLE_MS)
    return () => clearInterval(id)
  }, [active])
  return text
}

export default function Brand({ view }) {
  const [variant, setVariant] = useState(readVariant)
  const scrambled = useScramble(variant === 'coordenadas')

  const toggle = () => {
    const next = variant === 'orbita' ? 'coordenadas' : 'orbita'
    setVariant(next)
    try {
      localStorage.setItem(STORAGE_KEY, next)
    } catch {
      // sin almacenamiento el cambio dura hasta recargar
    }
  }

  return (
    <header className="brand" data-variant={variant}>
      {variant === 'orbita' ? (
        <h1 aria-label={NAME}>
          <span aria-hidden="true">GE</span>
          <OrbitO />
          <span aria-hidden="true">FORA</span>
        </h1>
      ) : (
        <h1 aria-label={NAME} className="scramble">
          <span aria-hidden="true">{scrambled}</span>
        </h1>
      )}
      <p className="tagline">
        {variant === 'coordenadas' && view ? formatCoords(view.lat, view.lng) : 'El mundo, país a país'}
      </p>
      <button type="button" className="brand-switch" onClick={toggle}
        aria-label={`Cambiar estilo del título (ahora: ${VARIANTS[variant]})`}>
        {VARIANTS[variant === 'orbita' ? 'coordenadas' : 'orbita']} ↻
      </button>
    </header>
  )
}

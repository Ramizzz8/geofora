import { useLang } from '../i18n'

const ORBIT_TILT = 'rotate(-20 50 50)'

function Satellite() {
  return (
    <circle className="satellite" r="5" fill="#ffd27a">
      <animateMotion dur="6s" repeatCount="indefinite">
        <mpath href="#orbit" />
      </animateMotion>
    </circle>
  )
}

// La "O" de GEO convertida en un planeta con un satélite en órbita. La órbita y el
// satélite se dibujan dos veces: detrás del planeta (este los tapa) y delante, pero
// recortados a la mitad de la elipse más cercana a quien mira.
function OrbitO() {
  return (
    <svg className="orbit-o" viewBox="0 0 100 100" aria-hidden="true">
      <defs>
        <radialGradient id="planet" cx="35%" cy="32%" r="75%">
          <stop offset="0%" stopColor="#9fd4ff" />
          <stop offset="55%" stopColor="#2f6fd6" />
          <stop offset="100%" stopColor="#0a1a44" />
        </radialGradient>
        <path id="orbit" d="M 6 50 a 44 16 0 1 0 88 0 a 44 16 0 1 0 -88 0" />
        <clipPath id="orbit-front">
          <rect x="-10" y="50" width="120" height="60" transform={ORBIT_TILT} />
        </clipPath>
      </defs>
      <g transform={ORBIT_TILT}>
        <use href="#orbit" fill="none" stroke="rgba(160, 200, 255, 0.45)" strokeWidth="2" />
        <Satellite />
      </g>
      <circle cx="50" cy="50" r="30" fill="url(#planet)" />
      <g clipPath="url(#orbit-front)">
        <g transform={ORBIT_TILT}>
          <use href="#orbit" fill="none" stroke="rgba(160, 200, 255, 0.45)" strokeWidth="2" />
          <Satellite />
        </g>
      </g>
    </svg>
  )
}

export default function Brand() {
  const { t } = useLang()
  return (
    <header className="brand">
      <h1 aria-label="GEOFORA">
        <span aria-hidden="true">GE</span>
        <OrbitO />
        <span aria-hidden="true">FORA</span>
      </h1>
      <p className="tagline">{t('tagline')}</p>
      <p className="promise">{t('promise')}</p>
    </header>
  )
}

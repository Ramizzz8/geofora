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

export default function Brand() {
  return (
    <header className="brand">
      <h1 aria-label="GEOFORA">
        <span aria-hidden="true">GE</span>
        <OrbitO />
        <span aria-hidden="true">FORA</span>
      </h1>
      <p className="tagline">El mundo, país a país</p>
    </header>
  )
}

const W = 96
const H = 28
const PAD = 3

// Minigráfica de evolución dibujada a mano: no hace falta una librería para una línea
export default function Sparkline({ series }) {
  const years = series.map(([y]) => y)
  const values = series.map(([, v]) => v)
  const [minY, maxY] = [Math.min(...years), Math.max(...years)]
  const [minV, maxV] = [Math.min(...values), Math.max(...values)]
  const x = (y) => (maxY === minY ? W / 2 : PAD + ((y - minY) / (maxY - minY)) * (W - 2 * PAD))
  const y = (v) => (maxV === minV ? H / 2 : H - PAD - ((v - minV) / (maxV - minV)) * (H - 2 * PAD))
  const [lastYear, lastValue] = series[series.length - 1]
  return (
    <svg className="sparkline" width={W} height={H} viewBox={`0 0 ${W} ${H}`} role="img"
      aria-label={minY === maxY ? `Dato de ${minY}` : `Evolución ${minY}–${maxY}`}>
      {series.length > 1 && (
        <polyline points={series.map(([yr, v]) => `${x(yr).toFixed(1)},${y(v).toFixed(1)}`).join(' ')}
          fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" strokeLinecap="round" />
      )}
      <circle cx={x(lastYear)} cy={y(lastValue)} r="2.6" fill="var(--accent)" />
    </svg>
  )
}

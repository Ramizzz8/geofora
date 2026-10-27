const HOT = [255, 170, 51] // tinte del país con más noticias
const MAX_ALPHA = 0.65 // nunca opaco: la textura de la Tierra se sigue viendo

export function heatColor(count, max) {
  // raíz cuadrada: unos pocos países acaparan casi todas las noticias
  const t = max > 0 ? Math.sqrt(Math.min(count / max, 1)) : 0
  const alpha = Math.round(t * MAX_ALPHA * 100) / 100
  return `rgba(${HOT.join(', ')}, ${alpha})`
}

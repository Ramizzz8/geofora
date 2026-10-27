const BASE = [38, 52, 84] // país sin noticias
const HOT = [255, 170, 51] // país con más noticias

export function heatColor(count, max) {
  // raíz cuadrada: unos pocos países acaparan casi todas las noticias
  const t = max > 0 ? Math.sqrt(Math.min(count / max, 1)) : 0
  const [r, g, b] = BASE.map((c, i) => Math.round(c + (HOT[i] - c) * t))
  return `rgb(${r}, ${g}, ${b})`
}

import { useEffect, useRef } from 'react'

const STARS_PER_PX = 1 / 2600 // densidad: ~800 estrellas en una pantalla de escritorio
const TWINKLERS = 70
const FRAME_MS = 50 // ~20 fps bastan para un parpadeo suave

function makeStars(w, h) {
  const n = Math.round(w * h * STARS_PER_PX)
  return Array.from({ length: n }, (_, i) => ({
    x: Math.random() * w,
    y: Math.random() * h,
    r: Math.random() < 0.92 ? Math.random() * 0.9 + 0.2 : Math.random() * 1.2 + 1,
    a: Math.random() * 0.6 + 0.25,
    hue: Math.random() < 0.15 ? 30 : Math.random() < 0.3 ? 220 : 0, // algunas cálidas y frías
    phase: Math.random() * Math.PI * 2,
    twinkle: i < TWINKLERS,
  }))
}

export default function Starfield() {
  const ref = useRef()

  useEffect(() => {
    const canvas = ref.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    const reduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    let stars = []
    let raf = 0
    let last = 0

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      canvas.width = window.innerWidth * dpr
      canvas.height = window.innerHeight * dpr
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      stars = makeStars(window.innerWidth, window.innerHeight)
      draw(0)
    }

    const draw = (t) => {
      ctx.clearRect(0, 0, window.innerWidth, window.innerHeight)
      for (const s of stars) {
        const a = s.twinkle && !reduced ? s.a * (0.55 + 0.45 * Math.sin(t / 900 + s.phase)) : s.a
        ctx.fillStyle = s.hue ? `hsla(${s.hue}, 80%, 85%, ${a})` : `rgba(255, 255, 255, ${a})`
        ctx.beginPath()
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2)
        ctx.fill()
      }
    }

    const loop = (t) => {
      if (t - last > FRAME_MS) {
        draw(t)
        last = t
      }
      raf = requestAnimationFrame(loop)
    }

    resize()
    window.addEventListener('resize', resize)
    if (!reduced) raf = requestAnimationFrame(loop)
    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return <canvas ref={ref} className="starfield" aria-hidden="true" />
}

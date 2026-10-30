import { useEffect } from 'react'

// Expone la posición del ratón (-1..1) como variables CSS --mx y --my para que los
// elementos del modo portada se desplacen un poco, cada uno a su profundidad.
export function useParallax(ref, active) {
  useEffect(() => {
    const el = ref.current
    if (!el || !active) return
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) return
    let frame = 0
    const onMove = (e) => {
      cancelAnimationFrame(frame)
      frame = requestAnimationFrame(() => {
        el.style.setProperty('--mx', ((e.clientX / window.innerWidth) * 2 - 1).toFixed(3))
        el.style.setProperty('--my', ((e.clientY / window.innerHeight) * 2 - 1).toFixed(3))
      })
    }
    window.addEventListener('mousemove', onMove)
    return () => {
      cancelAnimationFrame(frame)
      window.removeEventListener('mousemove', onMove)
      el.style.setProperty('--mx', '0')
      el.style.setProperty('--my', '0')
    }
  }, [ref, active])
}

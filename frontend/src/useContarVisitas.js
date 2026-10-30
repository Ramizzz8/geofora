import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

// El script de GoatCounter carga en diferido: si aún no está, la visita espera a que termine
function contar(path) {
  if (window.goatcounter?.count) {
    window.goatcounter.count({ path })
    return
  }
  document.querySelector('script[data-goatcounter]')
    ?.addEventListener('load', () => window.goatcounter?.count?.({ path }), { once: true })
}

// React Router cambia de ruta sin recargar la página, así que cada ruta se cuenta a mano
export function useContarVisitas() {
  const { pathname } = useLocation()
  useEffect(() => { contar(pathname) }, [pathname])
}

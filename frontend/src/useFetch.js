import { useEffect, useState } from 'react'

// Cada sección pide sus propios datos: un fallo en una no afecta a las demás.
export function useFetch(fetcher, key) {
  const [state, setState] = useState({ data: null, error: null, loading: true })
  useEffect(() => {
    let alive = true
    setState({ data: null, error: null, loading: true })
    fetcher(key)
      .then((data) => alive && setState({ data, error: null, loading: false }))
      .catch((error) => alive && setState({ data: null, error, loading: false }))
    return () => { alive = false }
  }, [fetcher, key])
  return state
}

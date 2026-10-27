import { formatDate } from '../../format'

export default function Section({ title, state, children }) {
  const { data, error, loading } = state
  return (
    <section className="section">
      <h3>{title}</h3>
      {loading && <p className="muted loading">Cargando…</p>}
      {error && <p className="muted">{error.message || 'No disponible ahora mismo'}</p>}
      {data && (
        <>
          {data.stale && <p className="stale">Datos del {formatDate(data.fetched_at)}</p>}
          {children(data)}
        </>
      )}
    </section>
  )
}

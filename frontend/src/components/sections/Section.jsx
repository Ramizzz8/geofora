import { formatDate } from '../../format'
import { useLang } from '../../i18n'

export default function Section({ title, state, children }) {
  const { data, error, loading } = state
  const { lang, t } = useLang()
  return (
    <section className="section">
      <h3>{title}</h3>
      {loading && <p className="muted loading">{t('loading')}</p>}
      {error && <p className="muted">{t('unavailable', { section: title })}</p>}
      {data && (
        <>
          {data.stale && <p className="stale">{t('staleData', { date: formatDate(data.fetched_at, lang) })}</p>}
          {children(data)}
        </>
      )}
    </section>
  )
}

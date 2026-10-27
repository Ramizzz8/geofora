import { useState } from 'react'
import { getNews } from '../../api'
import { languageName, timeAgo } from '../../format'
import { useFetch } from '../../useFetch'
import Section from './Section'

function Headline({ a }) {
  const [original, setOriginal] = useState(false)
  return (
    <li className="news-item">
      <a href={a.url} target="_blank" rel="noopener noreferrer">{original ? a.title_original : a.title}</a>
      <div className="meta">
        <span>{a.domain}</span> · <span>{timeAgo(a.seen_at)}</span>
      </div>
      {a.translated && (
        <div className="meta translated">
          Traducido automáticamente · idioma original: {languageName(a.language)}{' '}
          <button type="button" className="link-button" onClick={() => setOriginal(!original)}>
            {original ? 'Ver traducción' : 'Ver original'}
          </button>
        </div>
      )}
    </li>
  )
}

export default function NewsSection({ slug }) {
  const state = useFetch(getNews, slug)
  return (
    <Section title="Noticias" state={state}>
      {(data) => data.articles.length === 0 ? (
        <p className="muted">No hay noticias recientes de este país</p>
      ) : (
        <>
          {data.range === '7d' && <p className="muted small">Mostrando noticias de los últimos 7 días</p>}
          <ul className="news">{data.articles.map((a) => <Headline key={a.url} a={a} />)}</ul>
          <p className="source">Fuente: GDELT Project</p>
        </>
      )}
    </Section>
  )
}

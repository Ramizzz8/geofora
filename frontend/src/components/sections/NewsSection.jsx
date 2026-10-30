import { useState } from 'react'
import { getNews } from '../../api'
import { languageName, timeAgo } from '../../format'
import { useFetch } from '../../useFetch'
import Section from './Section'

// tonos para las tarjetas sin foto: cada medio conserva siempre el mismo
const TEXT_CARD_HUES = [210, 265, 330, 20, 160, 45]

const VISIBLE_CARDS = 6 // además de la destacada; el resto, al pulsar «Ver más»

function hueFor(domain) {
  let h = 0
  for (const ch of domain) h = (h * 31 + ch.charCodeAt(0)) >>> 0
  return TEXT_CARD_HUES[h % TEXT_CARD_HUES.length]
}

function Translated({ a, original, onToggle }) {
  if (!a.translated) return null
  return (
    <div className="meta translated">
      Traducido automáticamente · idioma original: {languageName(a.language)}{' '}
      <button type="button" className="link-button" onClick={onToggle}>
        {original ? 'Ver traducción' : 'Ver original'}
      </button>
    </div>
  )
}

function NewsCard({ a, hero = false }) {
  const [original, setOriginal] = useState(false)
  const [broken, setBroken] = useState(false)
  const image = a.image && !broken ? a.image : null
  const kind = hero ? 'news-hero' : 'news-card'
  return (
    <article
      className={`${kind} ${image ? '' : `${kind}--text`}`}
      style={image ? undefined : { '--card-hue': hueFor(a.domain) }}
    >
      <a href={a.url} target="_blank" rel="noopener noreferrer" className="news-link">
        {image && (
          <img src={image} alt="" loading="lazy" referrerPolicy="no-referrer" onError={() => setBroken(true)} />
        )}
        <div className="news-body">
          <span className="news-source">{a.domain} · {timeAgo(a.seen_at)}</span>
          <h4>{original ? a.title_original : a.title}</h4>
        </div>
      </a>
      <Translated a={a} original={original} onToggle={() => setOriginal(!original)} />
    </article>
  )
}

function NewsGrid({ articles }) {
  const [expanded, setExpanded] = useState(false)
  const hidden = articles.length - VISIBLE_CARDS
  const shown = expanded ? articles : articles.slice(0, VISIBLE_CARDS)
  return (
    <>
      <div className="news-grid">{shown.map((a) => <NewsCard key={a.url} a={a} />)}</div>
      {hidden > 0 && (
        <button type="button" className="more-button" onClick={() => setExpanded(!expanded)}>
          {expanded ? 'Ver menos' : `Ver más noticias (${hidden})`}
        </button>
      )}
    </>
  )
}

export default function NewsSection({ slug }) {
  const state = useFetch(getNews, slug)
  return (
    <Section title="Noticias" state={state}>
      {(data) => {
        if (data.articles.length === 0) return <p className="muted">No hay noticias recientes de este país</p>
        const hero = data.articles.find((a) => a.image)
        const rest = data.articles.filter((a) => a !== hero)
        return (
          <>
            {data.updated_at && <p className="muted small">Actualizado {timeAgo(data.updated_at)}</p>}
            {data.range === '7d' && <p className="muted small">Mostrando noticias de los últimos 7 días</p>}
            {hero && <NewsCard a={hero} hero />}
            <NewsGrid articles={rest} />
            <p className="source">Fuente: GDELT Project · las fotos pertenecen a cada medio</p>
          </>
        )
      }}
    </Section>
  )
}

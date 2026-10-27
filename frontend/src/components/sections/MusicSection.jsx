import { getMusic } from '../../api'
import { useFetch } from '../../useFetch'
import Section from './Section'

const SOURCES = { chart: 'Last.fm · Deezer', artists: 'MusicBrainz · Deezer' }

export default function MusicSection({ slug }) {
  const state = useFetch(getMusic, slug)
  return (
    <Section title="Música" state={state}>
      {(data) => data.source === 'none' ? (
        <p className="muted">Aún no tenemos música de aquí</p>
      ) : (
        <>
          {data.source === 'artists' && <p className="muted small">Artistas de este país</p>}
          <ol className="tracks">
            {data.items.map((t, i) => (
              <li key={`${t.artist}-${t.title}-${i}`}>
                <a href={t.link} target="_blank" rel="noopener noreferrer">
                  {t.title ? <><b>{t.title}</b> · {t.artist}</> : <b>{t.artist}</b>}
                </a>
                {t.preview_url && <audio controls preload="none" src={t.preview_url} />}
              </li>
            ))}
          </ol>
          <p className="source">Fuente: {SOURCES[data.source]}</p>
        </>
      )}
    </Section>
  )
}

import { useEffect, useRef, useState } from 'react'
import { getMusic } from '../../api'
import { useFetch } from '../../useFetch'
import Section from './Section'

const SOURCES = { chart: 'Apple Music · fragmentos: Deezer', artists: 'MusicBrainz · Deezer' }

function Track({ t, rank, playing, progress, onToggle }) {
  const name = t.title ?? t.artist
  return (
    <li className={`track ${playing ? 'track--playing' : ''}`}>
      <span className="track-rank">{rank}</span>
      <div className="track-cover">
        {t.image ? <img src={t.image} alt="" loading="lazy" /> : <span className="track-cover-empty">♪</span>}
        {t.preview_url && (
          <button type="button" className="track-play" onClick={onToggle}
            aria-label={`${playing ? 'Pausar' : 'Reproducir'} ${name}`} aria-pressed={playing}>
            {playing ? <span className="eq" aria-hidden="true"><i /><i /><i /></span> : <span aria-hidden="true">▶</span>}
          </button>
        )}
      </div>
      <div className="track-info">
        <a href={t.link} target="_blank" rel="noopener noreferrer" className="track-title">{name}</a>
        {t.title && <span className="track-meta">{t.artist}</span>}
        {playing && <span className="track-progress" style={{ '--p': progress }} aria-hidden="true" />}
      </div>
    </li>
  )
}

function TrackList({ items }) {
  const audio = useRef(null)
  const [playing, setPlaying] = useState(null)
  const [progress, setProgress] = useState(0)

  useEffect(() => () => audio.current?.pause(), [])

  const toggle = (i) => {
    const el = audio.current
    if (playing === i) {
      el.pause()
      setPlaying(null)
      return
    }
    el.src = items[i].preview_url
    setProgress(0)
    setPlaying(i)
    el.play().catch(() => setPlaying(null))
  }

  return (
    <>
      {/* un solo reproductor para toda la lista: al pulsar otra canción, la anterior se para */}
      <audio ref={audio} preload="none" onEnded={() => setPlaying(null)}
        onTimeUpdate={(e) => setProgress(e.currentTarget.currentTime / (e.currentTarget.duration || 30))} />
      <ol className="tracks">
        {items.map((t, i) => (
          <Track key={`${t.artist}-${t.title}-${i}`} t={t} rank={i + 1} playing={playing === i}
            progress={progress} onToggle={() => toggle(i)} />
        ))}
      </ol>
    </>
  )
}

export default function MusicSection({ slug }) {
  const state = useFetch(getMusic, slug)
  return (
    <Section title="Música" state={state}>
      {(data) => data.source === 'none' ? (
        <p className="muted">Aún no tenemos música de aquí</p>
      ) : (
        <>
          <p className="muted small">{data.source === 'chart' ? 'Lo más escuchado en Apple Music en este país' : 'Artistas de este país'}</p>
          <TrackList items={data.items} />
          <p className="source">Fuente: {SOURCES[data.source]}</p>
        </>
      )}
    </Section>
  )
}

import { useEffect, useRef, useState } from 'react'
import { getMusic } from '../../api'
import { useLang } from '../../i18n'
import { useFetch } from '../../useFetch'
import Section from './Section'


function Track({ t, rank, playing, progress, onToggle }) {
  const { t: tr } = useLang()
  const name = t.title ?? t.artist
  return (
    <li className={`track ${playing ? 'track--playing' : ''}`}>
      <span className="track-rank">{rank}</span>
      <div className="track-cover">
        {t.image ? <img src={t.image} alt="" loading="lazy" /> : <span className="track-cover-empty">♪</span>}
        {t.preview_url && (
          <button type="button" className="track-play" onClick={onToggle}
            aria-label={tr(playing ? 'pause' : 'play', { name })} aria-pressed={playing}>
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
  const { t } = useLang()
  return (
    <Section title={t('music')} state={state}>
      {(data) => data.source === 'none' ? (
        <p className="muted">{t('noMusic')}</p>
      ) : (
        <>
          <p className="muted small">{t(data.source === 'chart' ? 'musicChart' : 'musicArtists')}</p>
          <TrackList items={data.items} />
          <p className="source">{t(data.source === 'chart' ? 'musicSourceChart' : 'musicSourceArtists')}</p>
        </>
      )}
    </Section>
  )
}

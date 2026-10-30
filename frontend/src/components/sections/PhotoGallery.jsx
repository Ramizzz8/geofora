import { useLang } from '../../i18n'

export default function PhotoGallery({ photos }) {
  const { t } = useLang()
  if (!photos?.length) return null
  return (
    <section className="section">
      <h3>{t('photos')}</h3>
      <div className="gallery">
        {photos.map((p) => (
          <figure key={p.thumb}>
            <a href={p.page} target="_blank" rel="noopener noreferrer">
              <img src={p.thumb} alt="" loading="lazy" />
            </a>
            <figcaption>{p.author} · {p.license}</figcaption>
          </figure>
        ))}
      </div>
      <p className="source">{t('photosSource')}</p>
    </section>
  )
}

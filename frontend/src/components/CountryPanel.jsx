import { getCountry, getPhotos } from '../api'
import { useFetch } from '../useFetch'
import CountryHeader from './CountryHeader'
import CultureSection from './sections/CultureSection'
import MusicSection from './sections/MusicSection'
import PhotoGallery from './sections/PhotoGallery'
import NewsSection from './sections/NewsSection'

// fallbackName: nombre del mapa para territorios sin ficha (Somalilandia, Chipre del Norte)
export default function CountryPanel({ slug, fallbackName, onClose, children }) {
  const { data: country, error, loading } = useFetch(getCountry, slug)
  const notFound = error?.status === 404
  // las fotos son opcionales: si fallan, el panel sigue sin portada ni galería
  const photos = useFetch(getPhotos, slug).data?.photos ?? []

  return (
    <aside className="panel" aria-label="Información del país">
      <button type="button" className="close" onClick={onClose} aria-label="Cerrar">×</button>
      <div className="panel-scroll">
        {loading && <p className="muted loading">Cargando…</p>}
        {country && (
          <>
            <CountryHeader country={country} cover={photos[0]} />
            <NewsSection slug={slug} />
            <MusicSection slug={slug} />
            <CultureSection slug={slug} />
            <PhotoGallery photos={photos} />
          </>
        )}
        {notFound && fallbackName && (
          <header className="country-header">
            <h2>{fallbackName}</h2>
            <p className="muted">Aún no tenemos datos de este territorio.</p>
          </header>
        )}
        {notFound && !fallbackName && (
          <div className="not-found">
            <h2>País no encontrado</h2>
            {children}
          </div>
        )}
        {error && !notFound && <p className="muted">No se pudo cargar el país. Inténtalo de nuevo.</p>}
      </div>
    </aside>
  )
}

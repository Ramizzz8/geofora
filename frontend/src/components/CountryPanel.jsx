import { getCountry, getPhotos } from '../api'
import { useLang } from '../i18n'
import { useFetch } from '../useFetch'
import CountryHeader from './CountryHeader'
import CultureSection from './sections/CultureSection'
import EconomySection from './sections/EconomySection'
import OrganizationsSection from './sections/OrganizationsSection'
import MusicSection from './sections/MusicSection'
import PhotoGallery from './sections/PhotoGallery'
import NewsSection from './sections/NewsSection'

// fallbackName: nombre del mapa para territorios sin ficha (Somalilandia, Chipre del Norte)
export default function CountryPanel({ slug, fallbackName, onClose, children, organizations, activeOrg, onToggleOrg }) {
  const { t } = useLang()
  const { data: country, error, loading } = useFetch(getCountry, slug)
  const notFound = error?.status === 404
  // las fotos son opcionales: si fallan, el panel sigue sin portada ni galería
  const photos = useFetch(getPhotos, slug).data?.photos ?? []

  return (
    <aside className="panel" aria-label={t('countryPanel')}>
      <button type="button" className="close" onClick={onClose} aria-label={t('close')}>×</button>
      <div className="panel-scroll">
        {loading && <p className="muted loading">{t('loading')}</p>}
        {country && (
          <>
            <CountryHeader country={country} cover={photos[0]} />
            <OrganizationsSection data={organizations} iso3={country.iso3} active={activeOrg} onToggle={onToggleOrg} />
            <NewsSection slug={slug} />
            <EconomySection slug={slug} />
            <MusicSection slug={slug} />
            <CultureSection slug={slug} />
            <PhotoGallery photos={photos} />
          </>
        )}
        {notFound && fallbackName && (
          <header className="country-header">
            <h2>{fallbackName}</h2>
            <p className="muted">{t('noTerritoryData')}</p>
          </header>
        )}
        {notFound && !fallbackName && (
          <div className="not-found">
            <h2>{t('notFound')}</h2>
            {children}
          </div>
        )}
        {error && !notFound && <p className="muted">{t('countryError')}</p>}
      </div>
    </aside>
  )
}

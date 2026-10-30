import { countryName, translator } from './i18n'

// Título de la pestaña; en español coincide con el que manda el servidor (backend/app/seo.py)
export function pageTitle({ lang, slug, country, legal = false }) {
  const t = translator(lang)
  if (legal) return `${t('legalLink')} · GEOFORA`
  if (country) return t('titleCountry', { name: countryName(country, lang) })
  if (slug) return `${t('notFound')} · GEOFORA`
  return `GEOFORA: ${t('tagline').toLowerCase()}`
}

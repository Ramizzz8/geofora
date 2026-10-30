export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

const SERVER_DOWN = 'El servidor no responde ahora mismo. Inténtalo de nuevo en unos minutos.'

async function get(path) {
  const res = await fetch(`/api${path}`)
  if (!res.ok) {
    let detail = null
    try {
      detail = (await res.json()).detail
    } catch {
      // cuerpo sin JSON (p. ej. una página de error de Caddy): se usa el mensaje genérico
    }
    throw new ApiError(res.status, detail ?? SERVER_DOWN)
  }
  return res.json()
}

export const getCountries = () => get('/countries')
export const getCountry = (slug) => get(`/country/${encodeURIComponent(slug)}`)
export const getHeatmap = () => get('/heatmap')
const langQuery = (lang) => (lang === 'en' ? '?lang=en' : '')
export const getNews = (slug, lang) => get(`/country/${encodeURIComponent(slug)}/news${langQuery(lang)}`)
export const getMusic = (slug) => get(`/country/${encodeURIComponent(slug)}/music`)
export const getCulture = (slug, lang) => get(`/country/${encodeURIComponent(slug)}/culture${langQuery(lang)}`)
export const getPhotos = (slug) => get(`/country/${encodeURIComponent(slug)}/photos`)
export const getEconomy = (slug) => get(`/country/${encodeURIComponent(slug)}/economy`)
export const getOrganizations = () => get('/organizations')

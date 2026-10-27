export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function get(path) {
  const res = await fetch(`/api${path}`)
  if (!res.ok) {
    let detail = res.statusText
    try {
      detail = (await res.json()).detail ?? detail
    } catch {
      // cuerpo sin JSON: se queda el statusText
    }
    throw new ApiError(res.status, detail)
  }
  return res.json()
}

export const getCountries = () => get('/countries')
export const getCountry = (slug) => get(`/country/${slug}`)
export const getHeatmap = () => get('/heatmap')
export const getNews = (slug) => get(`/country/${slug}/news`)
export const getMusic = (slug) => get(`/country/${slug}/music`)
export const getCulture = (slug) => get(`/country/${slug}/culture`)
export const getPhotos = (slug) => get(`/country/${slug}/photos`)

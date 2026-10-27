import { vi } from 'vitest'

// routes: { '/api/country/japon': body | { status, body } }
export function mockApi(routes) {
  const fetch = vi.fn(async (url) => {
    const r = routes[url]
    if (r === undefined) return new Response('{"detail":"no mock"}', { status: 500 })
    const { status = 200, body } = r && r.status ? r : { body: r }
    return new Response(JSON.stringify(body), { status })
  })
  vi.stubGlobal('fetch', fetch)
  return fetch
}

export const JAPON = {
  iso3: 'JPN', iso2: 'JP', slug: 'japon', name_es: 'Japón', name_en: 'Japan', capital: 'Tokyo',
  languages: ['Japanese'], currencies: ['JPY'], population: 125836021, timezones: ['UTC+09:00'],
  flag_svg: 'https://flagcdn.com/jp.svg',
}

export const NOW_S = Date.now() / 1000

export const NEWS_EMPTY = { range: '7d', articles: [], updated_at: null }
export const MUSIC_NONE = { source: 'none', items: [], fetched_at: NOW_S, stale: false }
export const CULTURE = {
  extract: 'Japón es un país insular', thumbnail: null,
  page_url: 'https://es.wikipedia.org/wiki/Jap%C3%B3n', culture_url: null, fetched_at: NOW_S, stale: false,
}

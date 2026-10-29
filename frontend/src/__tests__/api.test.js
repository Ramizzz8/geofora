import { afterEach, expect, test, vi } from 'vitest'
import { ApiError, getCountry, getNews } from '../api'

afterEach(() => vi.unstubAllGlobals())

test('getCountry lanza ApiError con el status en 404', async () => {
  vi.stubGlobal('fetch', vi.fn(async () => new Response('{"detail":"País no encontrado"}', { status: 404 })))
  await expect(getCountry('narnia')).rejects.toMatchObject({ name: 'ApiError', status: 404 })
  await expect(getCountry('narnia')).rejects.toBeInstanceOf(ApiError)
})

test('getNews pide la ruta del país y devuelve el JSON', async () => {
  const fetch = vi.fn(async () => new Response('{"articles":[]}', { status: 200 }))
  vi.stubGlobal('fetch', fetch)
  expect(await getNews('japon')).toEqual({ articles: [] })
  expect(fetch).toHaveBeenCalledWith('/api/country/japon/news')
})

test('un error sin JSON (502 de Caddy) da un mensaje en español', async () => {
  vi.stubGlobal('fetch', vi.fn(async () => new Response('<html>Bad Gateway</html>', { status: 502, statusText: 'Bad Gateway' })))
  await expect(getNews('japon')).rejects.toMatchObject({
    status: 502, message: 'El servidor no responde ahora mismo. Inténtalo de nuevo en unos minutos.',
  })
})

test('se mantiene el mensaje en español que envía la API', async () => {
  vi.stubGlobal('fetch', vi.fn(async () => new Response('{"detail":"Música no disponible ahora mismo"}', { status: 503 })))
  await expect(getNews('japon')).rejects.toMatchObject({ message: 'Música no disponible ahora mismo' })
})

test('el nombre del país va codificado en la URL', async () => {
  const fetch = vi.fn(async () => new Response('{}', { status: 200 }))
  vi.stubGlobal('fetch', fetch)
  await getNews('a b/c')
  expect(fetch).toHaveBeenCalledWith('/api/country/a%20b%2Fc/news')
})

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

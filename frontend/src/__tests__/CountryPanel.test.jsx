import { render, screen } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import CountryPanel from '../components/CountryPanel'
import { CULTURE, JAPON, MUSIC_NONE, NEWS_EMPTY, mockApi } from './mockApi'

afterEach(() => vi.unstubAllGlobals())

const ok = {
  '/api/country/japon': JAPON,
  '/api/country/japon/news': NEWS_EMPTY,
  '/api/country/japon/music': MUSIC_NONE,
  '/api/country/japon/culture': CULTURE,
}

test('muestra la ficha básica', async () => {
  mockApi(ok)
  render(<CountryPanel slug="japon" onClose={() => {}} />)
  expect(await screen.findByRole('heading', { name: 'Japón' })).toBeInTheDocument()
  expect(screen.getByText('Tokyo')).toBeInTheDocument()
  expect(screen.getByText('JPY')).toBeInTheDocument()
})

test('país inexistente muestra "País no encontrado"', async () => {
  mockApi({ '/api/country/narnia': { status: 404, body: { detail: 'País no encontrado' } } })
  render(<CountryPanel slug="narnia" onClose={() => {}} />)
  expect(await screen.findByText('País no encontrado')).toBeInTheDocument()
})

test('territorio sin ficha muestra su nombre del mapa', async () => {
  mockApi({ '/api/country/somaliland': { status: 404, body: { detail: 'País no encontrado' } } })
  render(<CountryPanel slug="somaliland" fallbackName="Somaliland" onClose={() => {}} />)
  expect(await screen.findByRole('heading', { name: 'Somaliland' })).toBeInTheDocument()
  expect(screen.getByText(/Aún no tenemos datos/)).toBeInTheDocument()
})

test('un fallo en música no impide ver las noticias', async () => {
  mockApi({ ...ok, '/api/country/japon/music': { status: 503, body: { detail: 'Música no disponible ahora mismo' } } })
  render(<CountryPanel slug="japon" onClose={() => {}} />)
  expect(await screen.findByText('No hay noticias recientes de este país')).toBeInTheDocument()
  expect(await screen.findByText('Música no disponible ahora mismo')).toBeInTheDocument()
  expect(await screen.findByText('Japón es un país insular')).toBeInTheDocument()
})

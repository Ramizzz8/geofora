import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import Brand from '../components/Brand'
import CountryPanel from '../components/CountryPanel'
import LegalPage from '../components/LegalPage'
import SearchBox from '../components/SearchBox'
import SiteFooter from '../components/SiteFooter'
import { getCulture, getNews } from '../api'
import { currencyNames, economyValue, languageNames, timeAgo } from '../format'
import { LangProvider, initialLang } from '../i18n'
import { CULTURE, JAPON, MUSIC_NONE, NEWS_EMPTY, mockApi } from './mockApi'

beforeEach(() => localStorage.clear())
afterEach(() => vi.unstubAllGlobals())

const inEnglish = (ui) => {
  localStorage.setItem('geofora:lang', 'en')
  return render(<MemoryRouter><LangProvider>{ui}</LangProvider></MemoryRouter>)
}

test('sin elección usa el idioma del navegador; lo elegido tiene prioridad', () => {
  expect(initialLang('es-CO')).toBe('es')
  expect(initialLang('fr-FR')).toBe('en')
  localStorage.setItem('geofora:lang', 'es')
  expect(initialLang('en-US')).toBe('es')
})

test('el selector cambia el idioma, lo recuerda y actualiza el documento', async () => {
  localStorage.setItem('geofora:lang', 'es')
  render(<MemoryRouter><LangProvider><Brand /><SiteFooter /></LangProvider></MemoryRouter>)
  expect(screen.getByText('El monitor de actualidad internacional')).toBeInTheDocument()
  await userEvent.click(screen.getByRole('button', { name: 'English' }))
  expect(screen.getByText('The international news monitor')).toBeInTheDocument()
  expect(screen.getByRole('link', { name: 'Legal notice and privacy' })).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'English' })).toHaveAttribute('aria-pressed', 'true')
  expect(localStorage.getItem('geofora:lang')).toBe('en')
  expect(document.documentElement.lang).toBe('en')
})

test('formatos en inglés', () => {
  expect(economyValue({ id: 'gdp', unit: 'usd', value: 4.435e12 }, 'en')).toBe('US$4.4 trillion')
  expect(economyValue({ id: 'gdp', unit: 'usd', value: 17.78e9 }, 'en')).toBe('US$17.8 billion')
  expect(economyValue({ id: 'gdp_pc', unit: 'usd', value: 35951.04 }, 'en')).toBe('US$35,951')
  expect(economyValue({ id: 'inflation', unit: 'pct', value: 3.21 }, 'en')).toBe('3.2%')
  expect(economyValue({ id: 'debt', unit: 'pct_gdp', value: 234.9 }, 'en')).toBe('234.9% of GDP')
  expect(languageNames(['jpn'], ['Japanese'], 'en')).toBe('Japanese')
  expect(currencyNames(['JPY'], ['¥'], 'en')).toBe('Japanese Yen (¥)')
  expect(timeAgo(1000, 'en', 1000 * 1000 + 3 * 3600 * 1000)).toBe('3 hours ago')
})

test('las peticiones llevan el idioma solo cuando es inglés', async () => {
  const fetch = mockApi({})
  await getNews('japon').catch(() => {})
  await getNews('japon', 'en').catch(() => {})
  await getCulture('japon', 'en').catch(() => {})
  expect(fetch.mock.calls.map(([u]) => u)).toEqual([
    '/api/country/japon/news', '/api/country/japon/news?lang=en', '/api/country/japon/culture?lang=en',
  ])
})

test('el panel se muestra en inglés con el nombre inglés del país', async () => {
  mockApi({
    '/api/country/japon': JAPON,
    '/api/country/japon/news?lang=en': NEWS_EMPTY,
    '/api/country/japon/music': MUSIC_NONE,
    '/api/country/japon/culture?lang=en': CULTURE,
    '/api/country/japon/economy': { stale: false, fetched_at: 1, indicators: [] },
  })
  inEnglish(<CountryPanel slug="japon" onClose={() => {}} />)
  expect(await screen.findByRole('heading', { name: 'Japan' })).toBeInTheDocument()
  expect(screen.getByText('Capital')).toBeInTheDocument()
  expect(screen.getByText('Japanese Yen')).toBeInTheDocument()
  expect(await screen.findByText('No recent news from this country')).toBeInTheDocument()
  expect(await screen.findByText('No music from here yet')).toBeInTheDocument()
  expect(await screen.findByText('No recent economic data')).toBeInTheDocument()
})

test('el buscador encuentra por el nombre en cualquier idioma y lo muestra en el activo', async () => {
  mockApi({ '/api/countries': [{ iso3: 'JPN', slug: 'japon', name_es: 'Japón', name_en: 'Japan' }] })
  inEnglish(<SearchBox onSelect={() => {}} />)
  expect(screen.getByRole('combobox')).toHaveAttribute('placeholder', 'Search country…')
  await userEvent.type(screen.getByRole('combobox'), 'japon')
  expect(await screen.findByRole('option', { name: 'Japan' })).toBeInTheDocument()
})

test('la página legal está en inglés y menciona que el idioma se recuerda', () => {
  inEnglish(<LegalPage onClose={() => {}} />)
  expect(screen.getByRole('heading', { name: 'Legal notice' })).toBeInTheDocument()
  expect(screen.getByRole('heading', { name: 'Privacy policy' })).toBeInTheDocument()
  expect(screen.getByText(/does not use cookies/i)).toBeInTheDocument()
  expect(screen.getByText(/language you choose/i)).toBeInTheDocument()
})

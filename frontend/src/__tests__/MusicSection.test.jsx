import { render, screen } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import MusicSection from '../components/sections/MusicSection'
import { MUSIC_NONE, NOW_S, mockApi } from './mockApi'

afterEach(() => vi.unstubAllGlobals())

test('sin música muestra el mensaje honesto', async () => {
  mockApi({ '/api/country/japon/music': MUSIC_NONE })
  render(<MusicSection slug="japon" />)
  expect(await screen.findByText('Aún no tenemos música de aquí')).toBeInTheDocument()
})

test('modo artistas lleva subtítulo y audio si hay preview', async () => {
  mockApi({ '/api/country/japon/music': {
    source: 'artists', fetched_at: NOW_S, stale: false,
    items: [{ title: null, artist: 'Ahmad Zahir', preview_url: 'https://cdn/p.mp3', link: 'https://mb/a' }],
  } })
  const { container } = render(<MusicSection slug="japon" />)
  expect(await screen.findByText('Artistas de este país')).toBeInTheDocument()
  expect(screen.getByText('Ahmad Zahir')).toBeInTheDocument()
  expect(container.querySelector('audio')).toHaveAttribute('src', 'https://cdn/p.mp3')
})

test('datos caducados muestran su fecha', async () => {
  mockApi({ '/api/country/japon/music': { ...MUSIC_NONE, stale: true, fetched_at: Date.UTC(2026, 9, 20) / 1000 } })
  render(<MusicSection slug="japon" />)
  expect(await screen.findByText(/Datos del 20\/10\/2026/)).toBeInTheDocument()
})

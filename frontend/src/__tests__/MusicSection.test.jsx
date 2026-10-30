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
  render(<MusicSection slug="japon" />)
  expect(await screen.findByText('Artistas de este país')).toBeInTheDocument()
  expect(screen.getByText('Ahmad Zahir')).toBeInTheDocument()
  // el audio se carga al pulsar: aquí basta con que haya botón para reproducir
  expect(screen.getByRole('button', { name: 'Reproducir Ahmad Zahir' })).toBeInTheDocument()
})

test('datos caducados muestran su fecha', async () => {
  mockApi({ '/api/country/japon/music': { ...MUSIC_NONE, stale: true, fetched_at: Date.UTC(2026, 9, 20) / 1000 } })
  render(<MusicSection slug="japon" />)
  expect(await screen.findByText(/Datos del 20\/10\/2026/)).toBeInTheDocument()
})

const CHART = {
  source: 'chart', fetched_at: NOW_S, stale: false,
  items: [
    { title: 'Nutshell', artist: 'Alice In Chains', listeners: 58213, image: 'https://img/1.jpg', preview_url: '/api/music/preview/1', link: 'https://d/1' },
    { title: 'B.Y.O.B.', artist: 'System Of A Down', listeners: 57000, image: 'https://img/2.jpg', preview_url: '/api/music/preview/2', link: 'https://d/2' },
    { title: 'Sin fragmento', artist: 'Alguien', listeners: null, image: null, preview_url: null, link: 'https://d/3' },
  ],
}

test('ranking con número, portada y oyentes', async () => {
  mockApi({ '/api/country/japon/music': CHART })
  const { container } = render(<MusicSection slug="japon" />)
  expect(await screen.findByText('Nutshell')).toBeInTheDocument()
  expect(screen.getByText('58.213 oyentes')).toBeInTheDocument()
  expect(container.querySelectorAll('.track img')[0]).toHaveAttribute('src', 'https://img/1.jpg')
  expect([...container.querySelectorAll('.track-rank')].map((n) => n.textContent)).toEqual(['1', '2', '3'])
})

test('un único reproductor: la canción que suena se destaca y se puede pausar', async () => {
  const { default: userEvent } = await import('@testing-library/user-event')
  const play = vi.spyOn(window.HTMLMediaElement.prototype, 'play').mockResolvedValue()
  const pause = vi.spyOn(window.HTMLMediaElement.prototype, 'pause').mockImplementation(() => {})
  mockApi({ '/api/country/japon/music': CHART })
  const { container } = render(<MusicSection slug="japon" />)
  await screen.findByText('Nutshell')
  expect(container.querySelectorAll('audio')).toHaveLength(1)
  expect(screen.queryByRole('button', { name: 'Reproducir Sin fragmento' })).toBeNull()

  await userEvent.click(screen.getByRole('button', { name: 'Reproducir B.Y.O.B.' }))
  expect(play).toHaveBeenCalled()
  expect(container.querySelector('audio')).toHaveAttribute('src', '/api/music/preview/2')
  const tracks = container.querySelectorAll('.track')
  expect(tracks[1]).toHaveClass('track--playing')
  expect(tracks[0]).not.toHaveClass('track--playing')

  await userEvent.click(screen.getByRole('button', { name: 'Pausar B.Y.O.B.' }))
  expect(pause).toHaveBeenCalled()
  expect(tracks[1]).not.toHaveClass('track--playing')
})

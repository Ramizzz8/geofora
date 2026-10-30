import { render, screen } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import EconomySection from '../components/sections/EconomySection'
import Sparkline from '../components/Sparkline'
import { NOW_S, mockApi } from './mockApi'

afterEach(() => vi.unstubAllGlobals())

const THIS_YEAR = new Date().getFullYear()

test('muestra cada indicador con su año y una minigráfica', async () => {
  mockApi({ '/api/country/japon/economy': { stale: false, fetched_at: NOW_S, indicators: [
    { id: 'gdp', label: 'PIB', unit: 'usd', year: THIS_YEAR - 1, value: 4.4e12, series: [[2010, 5.7e12], [2020, 5e12], [THIS_YEAR - 1, 4.4e12]] },
    { id: 'inflation', label: 'Inflación', unit: 'pct', year: 2011, value: 0.5, series: [[2011, 0.5]] },
  ] } })
  const { container } = render(<EconomySection slug="japon" />)
  expect(await screen.findByText('4,4 billones de US$')).toBeInTheDocument()
  expect(screen.getByText(`(${THIS_YEAR - 1})`)).toBeInTheDocument()
  expect(container.querySelectorAll('svg.sparkline')).toHaveLength(2)
  // un dato muy antiguo se marca para que no parezca actual
  expect(screen.getByText('(2011)')).toHaveClass('old')
})

test('sin indicadores lo dice', async () => {
  mockApi({ '/api/country/japon/economy': { stale: false, fetched_at: NOW_S, indicators: [] } })
  render(<EconomySection slug="japon" />)
  expect(await screen.findByText('Sin datos económicos recientes')).toBeInTheDocument()
})

test('la minigráfica dibuja un punto por año y marca el último', () => {
  const { container } = render(<Sparkline series={[[2010, 1], [2015, 3], [2020, 2]]} />)
  const points = container.querySelector('polyline').getAttribute('points').trim().split(/\s+/)
  expect(points).toHaveLength(3)
  expect(container.querySelector('circle')).not.toBeNull()
  expect(container.querySelector('svg')).toHaveAttribute('aria-label', 'Evolución 2010–2020')
})

test('con un solo dato no hay línea, solo el punto', () => {
  const { container } = render(<Sparkline series={[[2011, 0.5]]} />)
  expect(container.querySelector('polyline')).toBeNull()
  expect(container.querySelector('circle')).not.toBeNull()
})

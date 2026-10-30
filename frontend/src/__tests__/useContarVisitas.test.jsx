import { act, render } from '@testing-library/react'
import { MemoryRouter, useNavigate } from 'react-router-dom'
import { afterEach, expect, test, vi } from 'vitest'
import { useContarVisitas } from '../useContarVisitas'

let navegar
function Prueba() {
  useContarVisitas()
  navegar = useNavigate()
  return null
}

afterEach(() => {
  delete window.goatcounter
  document.querySelector('script[data-goatcounter]')?.remove()
})

test('cuenta la primera carga y cada cambio de ruta', () => {
  window.goatcounter = { count: vi.fn() }
  render(<MemoryRouter initialEntries={['/']}><Prueba /></MemoryRouter>)
  act(() => navegar('/pais/japon'))
  act(() => navegar('/legal'))
  expect(window.goatcounter.count.mock.calls.map(([v]) => v.path)).toEqual(['/', '/pais/japon', '/legal'])
})

test('si el script aún no ha cargado, la visita se cuenta al terminar de cargar', () => {
  const script = document.createElement('script')
  script.setAttribute('data-goatcounter', 'https://stats.example/count')
  document.head.append(script)
  render(<MemoryRouter initialEntries={['/legal']}><Prueba /></MemoryRouter>)
  window.goatcounter = { count: vi.fn() }
  script.dispatchEvent(new Event('load'))
  expect(window.goatcounter.count).toHaveBeenCalledWith({ path: '/legal' })
})

test('sin el script (por ejemplo, con un bloqueador) la web sigue funcionando', () => {
  expect(() => render(<MemoryRouter><Prueba /></MemoryRouter>)).not.toThrow()
})

import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import Brand, { formatCoords } from '../components/Brand'

beforeEach(() => localStorage.clear())
afterEach(() => vi.useRealTimers())

test('formatea coordenadas con hemisferio', () => {
  expect(formatCoords(33.9391, 67.71)).toBe('33.94° N · 67.71° E')
  expect(formatCoords(-12.5, -77.03)).toBe('12.50° S · 77.03° O')
})

test('empieza en la versión órbita y el botón cambia a coordenadas y lo recuerda', async () => {
  const { container, unmount } = render(<Brand view={{ lat: 10, lng: 20 }} />)
  expect(container.querySelector('.brand')).toHaveAttribute('data-variant', 'orbita')
  expect(screen.getByRole('heading', { name: 'GEOFORA' })).toBeInTheDocument()
  await userEvent.click(screen.getByRole('button', { name: /Cambiar estilo del título/ }))
  expect(container.querySelector('.brand')).toHaveAttribute('data-variant', 'coordenadas')
  expect(screen.getByText('10.00° N · 20.00° E')).toBeInTheDocument()
  unmount()
  const again = render(<Brand view={{ lat: 0, lng: 0 }} />)
  expect(again.container.querySelector('.brand')).toHaveAttribute('data-variant', 'coordenadas')
})

test('el descifrado termina mostrando GEOFORA', () => {
  vi.useFakeTimers()
  localStorage.setItem('geofora:titulo', 'coordenadas')
  render(<Brand view={null} />)
  act(() => { vi.advanceTimersByTime(3000) })
  expect(screen.getByRole('heading', { name: 'GEOFORA' })).toHaveTextContent('GEOFORA')
})

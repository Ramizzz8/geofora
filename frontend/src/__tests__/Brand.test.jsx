import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import Brand from '../components/Brand'

test('el título es GEOFORA con la O como planeta en órbita', () => {
  const { container } = render(<Brand />)
  expect(screen.getByRole('heading', { name: 'GEOFORA' })).toBeInTheDocument()
  expect(container.querySelector('.orbit-o animateMotion')).not.toBeNull()
  expect(screen.getByText('El mundo, país a país')).toBeInTheDocument()
})

test('ya no hay botón para cambiar el estilo del título', () => {
  render(<Brand />)
  expect(screen.queryByRole('button')).toBeNull()
})

test('el satélite se dibuja detrás del planeta y solo la mitad delantera de la órbita va encima', () => {
  const { container } = render(<Brand />)
  const svg = container.querySelector('.orbit-o')
  const shapes = [...svg.querySelectorAll(':scope > circle, :scope > g')]
  const topLevel = (el) => shapes.find((s) => s.contains(el))
  const planet = svg.querySelector('circle[fill="url(#planet)"]')
  const satellites = svg.querySelectorAll('.satellite')
  expect(satellites).toHaveLength(2)
  // el de detrás va antes que el planeta (queda tapado por él)
  expect(shapes.indexOf(topLevel(satellites[0]))).toBeLessThan(shapes.indexOf(planet))
  // el de delante va después, recortado a la mitad delantera
  const front = topLevel(satellites[1])
  expect(shapes.indexOf(front)).toBeGreaterThan(shapes.indexOf(planet))
  expect(front.getAttribute('clip-path')).toMatch(/url\(#/)
})

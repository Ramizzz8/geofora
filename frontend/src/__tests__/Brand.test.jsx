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

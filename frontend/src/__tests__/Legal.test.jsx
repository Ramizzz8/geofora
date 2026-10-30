import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, test } from 'vitest'
import LegalPage from '../components/LegalPage'
import SiteFooter from '../components/SiteFooter'

test('el aviso legal identifica al titular con un correo de contacto', () => {
  render(<MemoryRouter><LegalPage onClose={() => {}} /></MemoryRouter>)
  expect(screen.getByRole('heading', { name: 'Aviso legal' })).toBeInTheDocument()
  expect(screen.getByText(/Andrés Ramírez/)).toBeInTheDocument()
  const mail = screen.getAllByRole('link', { name: 'ajulianrague@gmail.com' })[0]
  expect(mail).toHaveAttribute('href', 'mailto:ajulianrague@gmail.com')
})

test('la política de privacidad explica que no hay cookies y qué terceros reciben la IP', () => {
  render(<MemoryRouter><LegalPage onClose={() => {}} /></MemoryRouter>)
  expect(screen.getByRole('heading', { name: 'Política de privacidad' })).toBeInTheDocument()
  expect(screen.getByText(/no usa cookies/i)).toBeInTheDocument()
  for (const tercero of ['flagcdn.com', 'Wikimedia', 'Deezer']) {
    expect(screen.getAllByText(new RegExp(tercero)).length).toBeGreaterThan(0)
  }
  expect(screen.getByRole('link', { name: 'GoatCounter' })).toHaveAttribute('href', 'https://www.goatcounter.com')
  expect(screen.getByRole('link', { name: /Agencia Española de Protección de Datos/ })).toHaveAttribute('href', 'https://www.aepd.es')
})

test('el pie enlaza al aviso legal y a la privacidad', () => {
  render(<MemoryRouter><SiteFooter /></MemoryRouter>)
  expect(screen.getByRole('link', { name: 'Aviso legal y privacidad' })).toHaveAttribute('href', '/legal')
})

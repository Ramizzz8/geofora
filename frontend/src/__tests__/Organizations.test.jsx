import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test, vi } from 'vitest'
import OrganizationsSection, { OrgBanner } from '../components/sections/OrganizationsSection'

const ORGS = {
  generated: '2026-10-30',
  organizations: [
    { id: 'onu', short: 'ONU', name: 'Organización de las Naciones Unidas', description: 'Paz.', members: ['ESP', 'JPN', 'MAR'] },
    { id: 'otan', short: 'OTAN', name: 'Organización del Tratado del Atlántico Norte', description: 'Alianza.', members: ['ESP', 'USA'] },
    { id: 'ua', short: 'UA', name: 'Unión Africana', description: 'África.', members: ['MAR'] },
  ],
}

test('solo muestra las organizaciones a las que pertenece el país', () => {
  render(<OrganizationsSection data={ORGS} iso3="ESP" active={null} onToggle={() => {}} />)
  expect(screen.getByRole('button', { name: /ONU/ })).toBeInTheDocument()
  expect(screen.getByRole('button', { name: /OTAN/ })).toBeInTheDocument()
  expect(screen.queryByRole('button', { name: /UA/ })).toBeNull()
  expect(screen.getByRole('button', { name: /OTAN/ })).toHaveAttribute('title', 'Organización del Tratado del Atlántico Norte. Alianza.')
})

test('al pulsar una organización se pide resaltarla en el globo', async () => {
  const onToggle = vi.fn()
  render(<OrganizationsSection data={ORGS} iso3="ESP" active="otan" onToggle={onToggle} />)
  expect(screen.getByRole('button', { name: /OTAN/ })).toHaveAttribute('aria-pressed', 'true')
  await userEvent.click(screen.getByRole('button', { name: /ONU/ }))
  expect(onToggle).toHaveBeenCalledWith('onu')
})

test('un país sin organizaciones de la lista lo indica', () => {
  render(<OrganizationsSection data={ORGS} iso3="ATA" active={null} onToggle={() => {}} />)
  expect(screen.getByText('No pertenece a ninguna de las organizaciones que seguimos')).toBeInTheDocument()
})

test('el aviso del globo dice cuántos miembros resalta y permite quitarlo', async () => {
  const onClear = vi.fn()
  render(<OrgBanner org={ORGS.organizations[1]} onClear={onClear} />)
  expect(screen.getByText(/Miembros de OTAN \(2\)/)).toBeInTheDocument()
  await userEvent.click(screen.getByRole('button', { name: 'Quitar resaltado' }))
  expect(onClear).toHaveBeenCalled()
})

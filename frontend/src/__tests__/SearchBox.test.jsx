import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, expect, test, vi } from 'vitest'
import SearchBox from '../components/SearchBox'
import { mockApi } from './mockApi'

afterEach(() => vi.unstubAllGlobals())

const COUNTRIES = [
  { iso3: 'AFG', slug: 'afganistan', name_es: 'Afganistán' },
  { iso3: 'JPN', slug: 'japon', name_es: 'Japón' },
  { iso3: 'JAM', slug: 'jamaica', name_es: 'Jamaica' },
]

test('encuentra sin tildes ni mayúsculas', async () => {
  mockApi({ '/api/countries': COUNTRIES })
  render(<SearchBox onSelect={() => {}} />)
  await userEvent.type(screen.getByRole('combobox'), 'AFGAN')
  expect(await screen.findByRole('option', { name: 'Afganistán' })).toBeInTheDocument()
  expect(screen.queryByRole('option', { name: 'Japón' })).not.toBeInTheDocument()
})

test('Enter elige el primer resultado', async () => {
  mockApi({ '/api/countries': COUNTRIES })
  const onSelect = vi.fn()
  render(<SearchBox onSelect={onSelect} />)
  await userEvent.type(screen.getByRole('combobox'), 'japon')
  await screen.findByRole('option', { name: 'Japón' })
  await userEvent.keyboard('{Enter}')
  expect(onSelect).toHaveBeenCalledWith('japon')
})

test('las flechas cambian la selección', async () => {
  mockApi({ '/api/countries': COUNTRIES })
  const onSelect = vi.fn()
  render(<SearchBox onSelect={onSelect} />)
  await userEvent.type(screen.getByRole('combobox'), 'ja')
  await screen.findByRole('option', { name: 'Jamaica' })
  await userEvent.keyboard('{ArrowDown}{Enter}')
  expect(onSelect).toHaveBeenCalledWith('japon')
})

test('muestra como mucho 8 resultados', async () => {
  const many = Array.from({ length: 12 }, (_, i) => ({ iso3: `A${i}`, slug: `a${i}`, name_es: `Atlantis ${i}` }))
  mockApi({ '/api/countries': many })
  render(<SearchBox onSelect={() => {}} />)
  await userEvent.type(screen.getByRole('combobox'), 'atl')
  await screen.findAllByRole('option')
  expect(screen.getAllByRole('option')).toHaveLength(8)
})

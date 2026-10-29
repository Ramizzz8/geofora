import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, expect, test, vi } from 'vitest'
import NewsSection from '../components/sections/NewsSection'
import { NEWS_EMPTY, NOW_S, mockApi } from './mockApi'

afterEach(() => vi.unstubAllGlobals())

const article = {
  url: 'https://aljazeera.net/a', title: 'Japón presenta un plan', title_original: 'اليابان تعلن خطة',
  language: 'ar', translated: true, domain: 'aljazeera.net', seen_at: NOW_S - 3 * 3600,
}

test('sin noticias muestra el mensaje', async () => {
  mockApi({ '/api/country/japon/news': NEWS_EMPTY })
  render(<NewsSection slug="japon" />)
  expect(await screen.findByText('No hay noticias recientes de este país')).toBeInTheDocument()
})

test('titular traducido con marca y botón "Ver original"', async () => {
  mockApi({ '/api/country/japon/news': { range: '48h', articles: [article], updated_at: NOW_S } })
  render(<NewsSection slug="japon" />)
  expect(await screen.findByText('Japón presenta un plan')).toBeInTheDocument()
  expect(screen.getByText(/Traducido automáticamente · idioma original: árabe/)).toBeInTheDocument()
  expect(screen.getByText(/aljazeera.net/)).toBeInTheDocument()
  expect(screen.getByText(/hace 3 horas/)).toBeInTheDocument()
  await userEvent.click(screen.getByRole('button', { name: 'Ver original' }))
  expect(screen.getByText('اليابان تعلن خطة')).toBeInTheDocument()
})

test('rango ampliado avisa de los 7 días', async () => {
  mockApi({ '/api/country/japon/news': { range: '7d', articles: [{ ...article, translated: false, title: 'x' }], updated_at: NOW_S } })
  render(<NewsSection slug="japon" />)
  expect(await screen.findByText('Mostrando noticias de los últimos 7 días')).toBeInTheDocument()
})

const withImage = (i, image) => ({
  url: `https://m/${i}`, title: `Titular ${i}`, title_original: `Titular ${i}`, language: 'es',
  translated: false, domain: 'medio.com', seen_at: NOW_S - 600, image,
})

test('la primera noticia con foto es la destacada', async () => {
  mockApi({ '/api/country/japon/news': { range: '48h', updated_at: NOW_S, articles: [
    withImage(1, null), withImage(2, 'https://img/2.jpg'), withImage(3, 'https://img/3.jpg'),
  ] } })
  const { container } = render(<NewsSection slug="japon" />)
  await screen.findByText('Titular 2')
  const hero = container.querySelector('.news-hero')
  expect(hero.querySelector('img')).toHaveAttribute('src', 'https://img/2.jpg')
  expect(hero).toHaveTextContent('Titular 2')
  expect(container.querySelectorAll('.news-card')).toHaveLength(2)
})

test('si la foto falla, la tarjeta queda solo con texto', async () => {
  const { fireEvent } = await import('@testing-library/react')
  mockApi({ '/api/country/japon/news': { range: '48h', updated_at: NOW_S, articles: [
    withImage(1, 'https://img/1.jpg'), withImage(2, 'https://img/rota.jpg'),
  ] } })
  const { container } = render(<NewsSection slug="japon" />)
  await screen.findByText('Titular 2')
  const card = container.querySelector('.news-card')
  fireEvent.error(card.querySelector('img'))
  expect(card.querySelector('img')).toBeNull()
  expect(card).toHaveClass('news-card--text')
})

test('muestra cuándo se actualizaron las noticias', async () => {
  mockApi({ '/api/country/japon/news': { range: '48h', updated_at: NOW_S - 20 * 60, articles: [withImage(1, null)] } })
  render(<NewsSection slug="japon" />)
  expect(await screen.findByText(/Actualizado hace 20 minutos/)).toBeInTheDocument()
})

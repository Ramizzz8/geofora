import { expect, test } from 'vitest'
import { pageTitle } from '../pageTitle'

const JAPON = { name_es: 'Japón', name_en: 'Japan' }

test('título de cada ruta en español, igual que el que envía el servidor', () => {
  expect(pageTitle({ lang: 'es' })).toBe('GEOFORA: el monitor de actualidad internacional')
  expect(pageTitle({ lang: 'es', legal: true })).toBe('Aviso legal y privacidad · GEOFORA')
  expect(pageTitle({ lang: 'es', slug: 'japon', country: JAPON })).toBe('Japón: noticias, música y economía · GEOFORA')
})

test('título de cada ruta en inglés', () => {
  expect(pageTitle({ lang: 'en' })).toBe('GEOFORA: the international news monitor')
  expect(pageTitle({ lang: 'en', legal: true })).toBe('Legal notice and privacy · GEOFORA')
  expect(pageTitle({ lang: 'en', slug: 'japon', country: JAPON })).toBe('Japan: news, music and economy · GEOFORA')
})

test('un slug que no está en el mapa se indica como no encontrado', () => {
  expect(pageTitle({ lang: 'es', slug: 'narnia' })).toBe('País no encontrado · GEOFORA')
  expect(pageTitle({ lang: 'en', slug: 'narnia' })).toBe('Country not found · GEOFORA')
})

import { expect, test } from 'vitest'
import { canonicalSlug, currencyNames, escapeHtml, languageNames } from '../format'

test('idiomas en español a partir de su código', () => {
  expect(languageNames(['jpn'], ['Japanese'])).toBe('Japonés')
  expect(languageNames(['prs', 'pus', 'tuk'], ['Dari', 'Pashto', 'Turkmen'])).toBe('Darí, pastún, turcomano')
})

test('si el navegador no conoce el código se queda el nombre original', () => {
  expect(languageNames(['ara', 'ber'], ['Arabic', 'Berber'])).toBe('Árabe, Berber')
})

test('sin códigos (datos antiguos) muestra los nombres tal cual', () => {
  expect(languageNames([], ['Japanese'])).toBe('Japanese')
})

test('monedas en español y el código si no hay traducción', () => {
  expect(currencyNames(['JPY'])).toBe('Yen japonés')
  expect(currencyNames(['AUD', 'TVD'])).toBe('Dólar australiano, TVD')
})

test('slug canónico sin tildes, mayúsculas ni espacios', () => {
  expect(canonicalSlug('Afganistán')).toBe('afganistan')
  expect(canonicalSlug('costa de marfil')).toBe('costa-de-marfil')
  expect(canonicalSlug('japon')).toBe('japon')
})

test('escapa HTML para la etiqueta del globo', () => {
  expect(escapeHtml('<img src=x onerror=alert(1)> & "a"')).toBe('&lt;img src=x onerror=alert(1)&gt; &amp; &quot;a&quot;')
})

test('la moneda lleva su símbolo cuando lo hay y no repite el código', () => {
  expect(currencyNames(['JPY'], ['¥'])).toBe('Yen japonés (¥)')
  expect(currencyNames(['MAD'], ['د.م.'])).toBe('Dírham marroquí (د.م.)')
  expect(currencyNames(['XYZ'], ['XYZ'])).toBe('XYZ')
  expect(currencyNames(['EUR'], [])).toBe('Euro')
})

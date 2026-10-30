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

test('valores económicos en formato español', async () => {
  const { economyValue } = await import('../format')
  expect(economyValue({ id: 'gdp', unit: 'usd', value: 4.435e12 })).toBe('4,4 billones de US$')
  expect(economyValue({ id: 'gdp', unit: 'usd', value: 17.78e9 })).toBe('17,8 mil millones de US$')
  expect(economyValue({ id: 'gdp', unit: 'usd', value: 57.3e6 })).toBe('57,3 millones de US$')
  expect(economyValue({ id: 'gdp_pc', unit: 'usd', value: 35951.04 })).toBe('35.951 US$')
  expect(economyValue({ id: 'inflation', unit: 'pct', value: -6.62 })).toBe('-6,6 %')
  expect(economyValue({ id: 'debt', unit: 'pct_gdp', value: 234.9 })).toBe('234,9 % del PIB')
})

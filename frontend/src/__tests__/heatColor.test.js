import { expect, test } from 'vitest'
import { heatColor } from '../heatColor'

test('sin noticias y con el máximo dan colores distintos', () => {
  expect(heatColor(0, 10)).not.toBe(heatColor(10, 10))
})

test('max 0 no falla', () => {
  expect(() => heatColor(5, 0)).not.toThrow()
  expect(heatColor(5, 0)).toBe(heatColor(0, 0))
})

test('un país sin noticias es transparente para que se vea la Tierra', () => {
  expect(heatColor(0, 10)).toMatch(/rgba\(.*, 0\)$/)
})

test('el país con más noticias tiene un tinte visible pero deja ver la textura', () => {
  const alpha = Number(heatColor(10, 10).match(/, ([\d.]+)\)$/)[1])
  expect(alpha).toBeGreaterThan(0.4)
  expect(alpha).toBeLessThan(0.8)
})

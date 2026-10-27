import { expect, test } from 'vitest'
import { heatColor } from '../heatColor'

test('sin noticias y con el máximo dan colores distintos', () => {
  expect(heatColor(0, 10)).not.toBe(heatColor(10, 10))
})

test('max 0 no falla', () => {
  expect(() => heatColor(5, 0)).not.toThrow()
  expect(heatColor(5, 0)).toBe(heatColor(0, 0))
})

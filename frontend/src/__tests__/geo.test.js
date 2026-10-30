import { expect, test } from 'vitest'
import { center } from '../geo'

const poly = (coords) => ({ geometry: { type: 'Polygon', coordinates: [coords] } })

test('centro de un país normal', () => {
  expect(center(poly([[60, 30], [70, 30], [70, 38], [60, 38]]))).toEqual({ lat: 34, lng: 65 })
})

test('país que cruza el antimeridiano (Fiyi) se centra cerca de 180°, no en 0°', () => {
  const fiji = {
    geometry: {
      type: 'MultiPolygon',
      coordinates: [
        [[[177, -18], [180, -18], [180, -16], [177, -16]]],
        [[[-180, -17], [-179, -17], [-179, -16], [-180, -16]]],
      ],
    },
  }
  const c = center(fiji)
  expect(Math.abs(Math.abs(c.lng) - 179)).toBeLessThan(1)
  expect(c.lat).toBe(-17)
})

test('se considera ampliado solo al acercarse por debajo de la distancia inicial', async () => {
  const { isZoomedIn } = await import('../geo')
  expect(isZoomedIn(2.5, 2.5)).toBe(false)
  expect(isZoomedIn(3.2, 2.5)).toBe(false) // más pequeño que al inicio: sigue el modo portada
  expect(isZoomedIn(2.47, 2.5)).toBe(false) // pequeñas variaciones al girar no cuentan
  expect(isZoomedIn(2.2, 2.5)).toBe(true)
})

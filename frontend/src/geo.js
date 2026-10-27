// Centro aproximado del país a partir de la caja que envuelve sus polígonos.
// Si la caja ocupa más de 180° de longitud (Rusia, Fiyi), el país cruza el
// antimeridiano: se calcula en [0, 360) para no acabar mirando a lng 0.
export function center(feature) {
  const rings = feature.geometry.type === 'Polygon'
    ? feature.geometry.coordinates
    : feature.geometry.coordinates.flat()
  const points = rings.flat()

  const box = (lngOf) => {
    let minLat = 90, maxLat = -90, minLng = Infinity, maxLng = -Infinity
    for (const [lng, lat] of points) {
      const x = lngOf(lng)
      minLat = Math.min(minLat, lat); maxLat = Math.max(maxLat, lat)
      minLng = Math.min(minLng, x); maxLng = Math.max(maxLng, x)
    }
    return { lat: (minLat + maxLat) / 2, lng: (minLng + maxLng) / 2, span: maxLng - minLng }
  }

  const plain = box((lng) => lng)
  if (plain.span <= 180) return { lat: plain.lat, lng: plain.lng }
  const wrapped = box((lng) => (lng < 0 ? lng + 360 : lng))
  return { lat: wrapped.lat, lng: wrapped.lng > 180 ? wrapped.lng - 360 : wrapped.lng }
}

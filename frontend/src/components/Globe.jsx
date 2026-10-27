import { useEffect, useMemo, useRef, useState } from 'react'
import GlobeGL from 'react-globe.gl'
import { MeshPhongMaterial } from 'three'
import { getHeatmap } from '../api'
import { heatColor } from '../heatColor'

const HEATMAP_REFRESH_MS = 10 * 60 * 1000

function useWindowSize() {
  const [size, setSize] = useState({ w: window.innerWidth, h: window.innerHeight })
  useEffect(() => {
    const onResize = () => setSize({ w: window.innerWidth, h: window.innerHeight })
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])
  return size
}

// centro aproximado del país a partir de la caja que envuelve sus polígonos
function center(feature) {
  const rings = feature.geometry.type === 'Polygon'
    ? feature.geometry.coordinates
    : feature.geometry.coordinates.flat()
  let minLat = 90, maxLat = -90, minLng = 180, maxLng = -180
  for (const [lng, lat] of rings.flat()) {
    minLat = Math.min(minLat, lat); maxLat = Math.max(maxLat, lat)
    minLng = Math.min(minLng, lng); maxLng = Math.max(maxLng, lng)
  }
  return { lat: (minLat + maxLat) / 2, lng: (minLng + maxLng) / 2 }
}

const PANEL_SPACE = 470 // ancho del panel lateral + margen
const MOBILE_LAT_SHIFT = 22

export default function Globe({ onSelect, selectedIso3, panelOpen = false }) {
  const globeRef = useRef()
  const { w, h } = useWindowSize()
  // en escritorio el globo se aparta para no quedar tapado por el panel
  const width = panelOpen && w >= 768 ? w - PANEL_SPACE : w
  const [features, setFeatures] = useState([])
  const [counts, setCounts] = useState({})
  const [hovered, setHovered] = useState(null)
  const material = useMemo(() => new MeshPhongMaterial({ color: '#0b1730', shininess: 8 }), [])

  useEffect(() => {
    fetch('/data/countries.geojson').then((r) => r.json()).then((g) => setFeatures(g.features))
  }, [])

  useEffect(() => {
    const load = () => getHeatmap().then((d) => setCounts(d.counts)).catch(() => {})
    load()
    const id = setInterval(load, HEATMAP_REFRESH_MS)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    const controls = globeRef.current?.controls()
    if (!controls) return
    controls.autoRotate = true
    controls.autoRotateSpeed = 0.35
    // deja de girar en cuanto el usuario toca el globo
    const stop = () => { controls.autoRotate = false }
    controls.addEventListener('start', stop)
    return () => controls.removeEventListener('start', stop)
  }, [features.length])

  useEffect(() => {
    const f = features.find((x) => x.properties.iso3 === selectedIso3)
    if (!f || !globeRef.current) return
    globeRef.current.controls().autoRotate = false
    const { lat, lng } = center(f)
    // en móvil la hoja inferior tapa la mitad de abajo: se mira algo más al sur
    const shift = window.innerWidth < 768 ? MOBILE_LAT_SHIFT : 0
    globeRef.current.pointOfView({ lat: lat - shift, lng, altitude: 1.9 }, 900)
  }, [selectedIso3, features])

  const max = useMemo(() => Math.max(0, ...Object.values(counts)), [counts])

  return (
    <GlobeGL
      ref={globeRef}
      width={width}
      height={h}
      backgroundColor="rgba(0,0,0,0)"
      globeMaterial={material}
      showAtmosphere
      atmosphereColor="#5b8cff"
      atmosphereAltitude={0.18}
      polygonsData={features}
      polygonCapColor={(f) =>
        f.properties.iso3 === selectedIso3 ? '#7cc4ff'
          : f === hovered ? '#a9d6ff'
            : heatColor(counts[f.properties.iso3] ?? 0, max)}
      polygonSideColor={() => 'rgba(20, 40, 80, 0.6)'}
      polygonStrokeColor={() => 'rgba(150, 190, 255, 0.35)'}
      polygonAltitude={(f) => (f === hovered || f.properties.iso3 === selectedIso3 ? 0.03 : 0.008)}
      polygonsTransitionDuration={250}
      polygonLabel={(f) => {
        const n = counts[f.properties.iso3] ?? 0
        return `<div class="globe-label"><b>${f.properties.name_es}</b><br>${n} noticias en 24 h</div>`
      }}
      onPolygonHover={setHovered}
      onPolygonClick={(f) => onSelect(f.properties.slug)}
    />
  )
}

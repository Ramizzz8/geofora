import { useEffect, useMemo, useRef, useState } from 'react'
import GlobeGL from 'react-globe.gl'
import { getHeatmap } from '../api'
import { center, isZoomedIn } from '../geo'
import { escapeHtml } from '../format'
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

const PANEL_SPACE = 570 // ancho del panel lateral + margen
const MOBILE_LAT_SHIFT = 22

export default function Globe({ features = [], onSelect, selectedIso3, panelOpen = false, onZoomedChange }) {
  const globeRef = useRef()
  const { w, h } = useWindowSize()
  // en escritorio el globo se aparta para no quedar tapado por el panel
  const width = panelOpen && w >= 768 ? w - PANEL_SPACE : w
  const [counts, setCounts] = useState({})
  const [hovered, setHovered] = useState(null)
  // distancia inicial de la cámara: por encima de ella (o igual) la web está en modo portada
  const initialAltitude = useRef(null)
  const zoomed = useRef(false)

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
    <div className="globe-wrap">
    <GlobeGL
      ref={globeRef}
      width={width}
      height={h}
      backgroundColor="rgba(0,0,0,0)"
      // NASA Blue Marble (julio de 2004): color real, dominio público
      globeImageUrl="/textures/earth-blue-marble.jpg"
      showAtmosphere
      atmosphereColor="#5b8cff"
      atmosphereAltitude={0.18}
      polygonsData={features}
      polygonCapColor={(f) =>
        f.properties.iso3 === selectedIso3 ? 'rgba(124, 196, 255, 0.45)'
          : f === hovered ? 'rgba(169, 214, 255, 0.3)'
            : heatColor(counts[f.properties.iso3] ?? 0, max)}
      polygonSideColor={() => 'rgba(124, 196, 255, 0.15)'}
      polygonStrokeColor={() => 'rgba(255, 255, 255, 0.28)'}
      polygonAltitude={(f) => (f === hovered || f.properties.iso3 === selectedIso3 ? 0.03 : 0.008)}
      polygonsTransitionDuration={250}
      polygonLabel={(f) => {
        const n = counts[f.properties.iso3] ?? 0
        return `<div class="globe-label"><b>${escapeHtml(f.properties.name_es)}</b><br>${n} noticias en 24 h</div>`
      }}
      onZoom={({ altitude }) => {
        initialAltitude.current ??= altitude
        const now = isZoomedIn(altitude, initialAltitude.current)
        if (now !== zoomed.current) {
          zoomed.current = now
          onZoomedChange?.(now)
        }
      }}
      onPolygonHover={setHovered}
      onPolygonClick={(f) => onSelect(f.properties.slug)}
    />
    </div>
  )
}

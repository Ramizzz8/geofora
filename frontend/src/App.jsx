import { useEffect, useRef, useState } from 'react'
import { useParallax } from './useParallax'
import { canonicalSlug } from './format'
import { useNavigate, useParams, Routes, Route } from 'react-router-dom'
import CountryPanel from './components/CountryPanel'
import Globe from './components/Globe'
import SearchBox from './components/SearchBox'
import Brand from './components/Brand'
import Starfield from './components/Starfield'
import LegalPage from './components/LegalPage'
import SiteFooter from './components/SiteFooter'

function Home({ legal = false }) {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [features, setFeatures] = useState([])
  const [zoomed, setZoomed] = useState(false)
  // modo portada: globo a su tamaño inicial o más lejos y ningún panel abierto
  const hero = !slug && !legal && !zoomed
  const appRef = useRef(null)
  useParallax(appRef, hero)

  useEffect(() => {
    fetch('/data/countries.geojson').then((r) => r.json()).then((g) => setFeatures(g.features))
  }, [])

  const selected = features.find((f) => f.properties.slug === slug)
  const goTo = (s) => navigate(`/pais/${s}`)

  // /pais/afganistán → /pais/afganistan, para que el globo encuentre el país
  useEffect(() => {
    if (slug && canonicalSlug(slug) !== slug) navigate(`/pais/${canonicalSlug(slug)}`, { replace: true })
  }, [slug, navigate])

  return (
    <div className={`app ${hero ? 'app--hero' : ''}`} ref={appRef}>
      <Starfield />
      <Brand />
      <SearchBox onSelect={goTo} hero={hero} />
      <Globe features={features} onSelect={goTo} selectedIso3={selected?.properties.iso3 ?? null} panelOpen={Boolean(slug) || legal} onZoomedChange={setZoomed} />
      {legal && <LegalPage onClose={() => navigate('/')} />}
      <SiteFooter />
      {slug && (
        <CountryPanel
          key={slug}
          slug={slug}
          fallbackName={selected?.properties.name_es}
          onClose={() => navigate('/')}
        >
          <SearchBox onSelect={goTo} />
        </CountryPanel>
      )}
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/pais/:slug" element={<Home />} />
      <Route path="/legal" element={<Home legal />} />
    </Routes>
  )
}

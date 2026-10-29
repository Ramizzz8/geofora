import { useEffect, useState } from 'react'
import { canonicalSlug } from './format'
import { useNavigate, useParams, Routes, Route } from 'react-router-dom'
import CountryPanel from './components/CountryPanel'
import Globe from './components/Globe'
import SearchBox from './components/SearchBox'
import Brand from './components/Brand'
import Starfield from './components/Starfield'

function Home() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [features, setFeatures] = useState([])

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
    <div className="app">
      <Starfield />
      <Brand />
      <SearchBox onSelect={goTo} />
      <Globe features={features} onSelect={goTo} selectedIso3={selected?.properties.iso3 ?? null} panelOpen={Boolean(slug)} />
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
    </Routes>
  )
}

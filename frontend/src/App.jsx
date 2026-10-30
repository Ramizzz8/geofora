import { useEffect, useState } from 'react'
import { canonicalSlug } from './format'
import { useNavigate, useParams, Routes, Route } from 'react-router-dom'
import CountryPanel from './components/CountryPanel'
import Globe from './components/Globe'
import SearchBox from './components/SearchBox'
import Brand from './components/Brand'
import Starfield from './components/Starfield'
import LegalPage from './components/LegalPage'
import SiteFooter from './components/SiteFooter'
import { OrgBanner } from './components/sections/OrganizationsSection'
import { getOrganizations } from './api'
import { useFetch } from './useFetch'

function Home({ legal = false }) {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [features, setFeatures] = useState([])
  const [zoomed, setZoomed] = useState(false)
  const organizations = useFetch(getOrganizations, 'todas').data
  const [activeOrg, setActiveOrg] = useState(null)
  const highlighted = organizations?.organizations.find((o) => o.id === activeOrg) ?? null
  const toggleOrg = (id) => setActiveOrg((current) => (current === id ? null : id))
  // modo portada: globo a su tamaño inicial o más lejos y ningún panel abierto
  const hero = !slug && !legal && !zoomed

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
    <div className={`app ${hero ? 'app--hero' : ''}`}>
      <Starfield />
      <Brand />
      <SearchBox onSelect={goTo} hero={hero} />
      <Globe features={features} onSelect={goTo} selectedIso3={selected?.properties.iso3 ?? null} panelOpen={Boolean(slug) || legal} onZoomedChange={setZoomed}
        highlight={highlighted?.members} />
      {highlighted && <OrgBanner org={highlighted} onClear={() => setActiveOrg(null)} />}
      {legal && <LegalPage onClose={() => navigate('/')} />}
      <SiteFooter />
      {slug && (
        <CountryPanel
          key={slug}
          slug={slug}
          fallbackName={selected?.properties.name_es}
          onClose={() => navigate('/')}
          organizations={organizations}
          activeOrg={activeOrg}
          onToggleOrg={toggleOrg}
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

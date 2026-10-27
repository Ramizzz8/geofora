import { useEffect, useState } from 'react'
import { useNavigate, useParams, Routes, Route } from 'react-router-dom'
import Globe from './components/Globe'

function Home() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [features, setFeatures] = useState([])

  useEffect(() => {
    fetch('/data/countries.geojson').then((r) => r.json()).then((g) => setFeatures(g.features))
  }, [])

  const selected = features.find((f) => f.properties.slug === slug)

  return (
    <div className="app">
      <header className="brand">
        <h1>GEOFORA</h1>
        <p>El mundo, país a país</p>
      </header>
      <Globe onSelect={(s) => navigate(`/pais/${s}`)} selectedIso3={selected?.properties.iso3 ?? null} />
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

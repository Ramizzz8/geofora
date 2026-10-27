import { useEffect, useId, useMemo, useState } from 'react'
import { getCountries } from '../api'

const MAX_RESULTS = 8

// misma normalización que el slug del backend: sin tildes ni mayúsculas
const norm = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim()

export default function SearchBox({ onSelect }) {
  const [countries, setCountries] = useState([])
  const [query, setQuery] = useState('')
  const [active, setActive] = useState(0)
  const listId = useId()

  useEffect(() => {
    getCountries().then(setCountries).catch(() => {})
  }, [])

  const results = useMemo(() => {
    const q = norm(query)
    if (!q) return []
    return countries
      .map((c) => ({ ...c, key: norm(c.name_es) }))
      .filter((c) => c.key.includes(q))
      .sort((a, b) => Number(!a.key.startsWith(q)) - Number(!b.key.startsWith(q)) || a.key.localeCompare(b.key))
      .slice(0, MAX_RESULTS)
  }, [countries, query])

  const choose = (c) => {
    onSelect(c.slug)
    setQuery('')
  }

  const onKeyDown = (e) => {
    if (!results.length) return
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setActive((i) => (i + 1) % results.length)
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setActive((i) => (i - 1 + results.length) % results.length)
    } else if (e.key === 'Enter') {
      choose(results[active])
    } else if (e.key === 'Escape') {
      setQuery('')
    }
  }

  return (
    <div className="search">
      <input
        role="combobox"
        aria-expanded={results.length > 0}
        aria-controls={listId}
        aria-label="Buscar país"
        placeholder="Buscar país…"
        value={query}
        onChange={(e) => { setQuery(e.target.value); setActive(0) }}
        onKeyDown={onKeyDown}
      />
      {results.length > 0 && (
        <ul id={listId} role="listbox" className="search-results">
          {results.map((c, i) => (
            <li
              key={c.iso3}
              role="option"
              aria-selected={i === active}
              onMouseDown={(e) => { e.preventDefault(); choose(c) }}
              onMouseEnter={() => setActive(i)}
            >
              {c.name_es}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

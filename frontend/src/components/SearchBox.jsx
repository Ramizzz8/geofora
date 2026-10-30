import { useEffect, useId, useMemo, useState } from 'react'
import { getCountries } from '../api'
import { countryName, suggestionsFor, useLang } from '../i18n'

const MAX_RESULTS = 8
const SUGGESTION_MS = 2600

// misma normalización que el slug del backend: sin tildes ni mayúsculas
const norm = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim()

export default function SearchBox({ onSelect, hero = false }) {
  const { lang, t } = useLang()
  const suggestions = suggestionsFor(lang)
  const [countries, setCountries] = useState([])
  const [query, setQuery] = useState('')
  const [active, setActive] = useState(0)
  const listId = useId()
  const [suggestion, setSuggestion] = useState(0)

  // en modo portada el texto de ayuda va proponiendo países para invitar a buscar
  useEffect(() => {
    if (!hero) return
    const id = setInterval(() => setSuggestion((i) => (i + 1) % suggestions.length), SUGGESTION_MS)
    return () => clearInterval(id)
  }, [hero, suggestions])

  useEffect(() => {
    getCountries().then(setCountries).catch(() => {})
  }, [])

  const results = useMemo(() => {
    const q = norm(query)
    if (!q) return []
    return countries
      // se encuentra por el nombre en cualquier idioma y se ordena por el del idioma activo
      .map((c) => ({
        ...c,
        name: countryName(c, lang),
        key: norm(countryName(c, lang)),
        anyName: norm(`${c.name_es} ${c.name_en ?? ''}`),
      }))
      .filter((c) => c.anyName.includes(q))
      .sort((a, b) => Number(!a.key.startsWith(q)) - Number(!b.key.startsWith(q)) || a.key.localeCompare(b.key))
      .slice(0, MAX_RESULTS)
  }, [countries, query, lang])

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
        aria-label={t('searchLabel')}
        placeholder={hero ? t('searchTry', { name: suggestions[suggestion] }) : t('searchPlaceholder')}
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
              {c.name}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

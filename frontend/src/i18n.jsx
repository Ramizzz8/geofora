import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const STORAGE_KEY = 'geofora:lang'

const MESSAGES = {
  es: {
    tagline: 'El mundo, país a país',
    legalLink: 'Aviso legal y privacidad',
    searchLabel: 'Buscar país',
    searchPlaceholder: 'Buscar país…',
    searchTry: 'Prueba con {name}…',
    close: 'Cerrar',
    loading: 'Cargando…',
    unavailable: '{section} no disponible ahora mismo',
    staleData: 'Datos del {date}',
    countryPanel: 'Información del país',
    countryError: 'No se pudo cargar el país. Inténtalo de nuevo.',
    notFound: 'País no encontrado',
    noTerritoryData: 'Aún no tenemos datos de este territorio.',
    flagOf: 'Bandera de {name}',
    capital: 'Capital',
    languages: 'Idiomas',
    currency: 'Moneda',
    population: 'Población',
    localTime: 'Hora local',
    news: 'Noticias',
    noNews: 'No hay noticias recientes de este país',
    updated: 'Actualizado {when}',
    last7Days: 'Mostrando noticias de los últimos 7 días',
    translatedFrom: 'Traducido automáticamente · idioma original: {lang}',
    showOriginal: 'Ver original',
    showTranslation: 'Ver traducción',
    moreNews: 'Ver más noticias ({n})',
    lessNews: 'Ver menos',
    newsSource: 'Fuente: GDELT Project · las fotos pertenecen a cada medio',
    economy: 'Economía',
    noEconomy: 'Sin datos económicos recientes',
    economySource: 'Fuente: Banco Mundial · deuda pública: FMI',
    'eco.gdp': 'PIB',
    'eco.gdp_pc': 'PIB per cápita',
    'eco.inflation': 'Inflación',
    'eco.unemployment': 'Paro',
    'eco.debt': 'Deuda pública',
    music: 'Música',
    noMusic: 'Aún no tenemos música de aquí',
    musicChart: 'Lo más escuchado en Apple Music en este país',
    musicArtists: 'Artistas de este país',
    musicSourceChart: 'Fuente: Apple Music · fragmentos: Deezer',
    musicSourceArtists: 'Fuente: MusicBrainz · Deezer',
    play: 'Reproducir {name}',
    pause: 'Pausar {name}',
    culture: 'Cultura',
    readMore: 'Leer más en Wikipedia',
    countryCulture: 'Cultura del país',
    cultureSource: 'Fuente: Wikipedia',
    photos: 'Fotos',
    photosSource: 'Fuente: Wikivoyage y Wikimedia Commons',
    organizations: 'Organizaciones',
    noOrganizations: 'No pertenece a ninguna de las organizaciones que seguimos',
    orgsHint: 'Pulsa una para ver todos sus miembros en el globo.',
    orgsSource: 'Fuente: Wikidata, revisado el {date}',
    orgMembers: 'Miembros de {org} ({n})',
    orgClear: 'Quitar resaltado',
    globeNews: '{n} noticias en 24 h',
    suggestions: ['Japón', 'Sudán', 'Perú', 'Mongolia', 'Islandia', 'Kenia', 'Vietnam', 'Marruecos'],
  },
  en: {
    tagline: 'The world, country by country',
    legalLink: 'Legal notice and privacy',
    searchLabel: 'Search country',
    searchPlaceholder: 'Search country…',
    searchTry: 'Try {name}…',
    close: 'Close',
    loading: 'Loading…',
    unavailable: '{section} unavailable right now',
    staleData: 'Data from {date}',
    countryPanel: 'Country information',
    countryError: 'The country could not be loaded. Please try again.',
    notFound: 'Country not found',
    noTerritoryData: 'We have no data for this territory yet.',
    flagOf: 'Flag of {name}',
    capital: 'Capital',
    languages: 'Languages',
    currency: 'Currency',
    population: 'Population',
    localTime: 'Local time',
    news: 'News',
    noNews: 'No recent news from this country',
    updated: 'Updated {when}',
    last7Days: 'Showing news from the last 7 days',
    translatedFrom: 'Automatically translated · original language: {lang}',
    showOriginal: 'Show original',
    showTranslation: 'Show translation',
    moreNews: 'Show more news ({n})',
    lessNews: 'Show less',
    newsSource: 'Source: GDELT Project · photos belong to each outlet',
    economy: 'Economy',
    noEconomy: 'No recent economic data',
    economySource: 'Source: World Bank · public debt: IMF',
    'eco.gdp': 'GDP',
    'eco.gdp_pc': 'GDP per capita',
    'eco.inflation': 'Inflation',
    'eco.unemployment': 'Unemployment',
    'eco.debt': 'Public debt',
    music: 'Music',
    noMusic: 'No music from here yet',
    musicChart: 'Most played on Apple Music in this country',
    musicArtists: 'Artists from this country',
    musicSourceChart: 'Source: Apple Music · previews: Deezer',
    musicSourceArtists: 'Source: MusicBrainz · Deezer',
    play: 'Play {name}',
    pause: 'Pause {name}',
    culture: 'Culture',
    readMore: 'Read more on Wikipedia',
    countryCulture: 'Culture of the country',
    cultureSource: 'Source: Wikipedia',
    photos: 'Photos',
    photosSource: 'Source: Wikivoyage and Wikimedia Commons',
    organizations: 'Organizations',
    noOrganizations: 'It does not belong to any of the organizations we follow',
    orgsHint: 'Click one to see all its members on the globe.',
    orgsSource: 'Source: Wikidata, reviewed on {date}',
    orgMembers: '{org} members ({n})',
    orgClear: 'Clear highlight',
    globeNews: '{n} news items in 24 h',
    suggestions: ['Japan', 'Sudan', 'Peru', 'Mongolia', 'Iceland', 'Kenya', 'Vietnam', 'Morocco'],
  },
}

function translator(lang) {
  return (key, params = {}) =>
    String(MESSAGES[lang][key]).replace(/\{(\w+)\}/g, (_, name) => params[name] ?? '')
}

export const suggestionsFor = (lang) => MESSAGES[lang].suggestions

// Nombre de un país u organización en el idioma activo
export const countryName = (c, lang) => (lang === 'en' ? c.name_en ?? c.name_es : c.name_es)

export function initialLang(browserLang = navigator.language) {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved in MESSAGES) return saved
  } catch {
    // sin almacenamiento se decide por el idioma del navegador
  }
  return browserLang?.toLowerCase().startsWith('es') ? 'es' : 'en'
}

// Sin LangProvider (por ejemplo en pruebas de un componente suelto) todo va en español
const LangContext = createContext({ lang: 'es', t: translator('es'), setLang: () => {} })

export const useLang = () => useContext(LangContext)

export function LangProvider({ children }) {
  const [lang, setLangState] = useState(() => initialLang())

  useEffect(() => {
    document.documentElement.lang = lang
  }, [lang])

  const value = useMemo(() => ({
    lang,
    t: translator(lang),
    setLang: (next) => {
      setLangState(next)
      try {
        localStorage.setItem(STORAGE_KEY, next)
      } catch {
        // sin almacenamiento el cambio dura hasta recargar
      }
    },
  }), [lang])

  return <LangContext.Provider value={value}>{children}</LangContext.Provider>
}

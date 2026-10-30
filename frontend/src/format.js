const LOCALES = { es: 'es-ES', en: 'en-GB' }
const relative = (lang) => new Intl.RelativeTimeFormat(lang, { numeric: 'auto' })
const displayLanguages = (lang) => new Intl.DisplayNames([lang], { type: 'language' })
const displayCurrencies = (lang) => new Intl.DisplayNames([lang], { type: 'currency' })

export function timeAgo(epochSeconds, lang = 'es', now = Date.now()) {
  const diff = epochSeconds * 1000 - now
  const hours = Math.round(diff / 3_600_000)
  if (Math.abs(hours) < 1) return relative(lang).format(Math.round(diff / 60_000), 'minute')
  if (Math.abs(hours) < 48) return relative(lang).format(hours, 'hour')
  return relative(lang).format(Math.round(hours / 24), 'day')
}

export function languageName(code, lang = 'es') {
  try {
    return displayLanguages(lang).of(code)
  } catch {
    return code
  }
}

export const formatDate = (epochSeconds, lang = 'es') =>
  new Date(epochSeconds * 1000).toLocaleDateString(LOCALES[lang])

// REST Countries da husos como "UTC+05:30"; se calcula la hora sin depender de IANA
export function localTime(timezone, now = new Date()) {
  const m = /^UTC(?:([+-])(\d{2}):(\d{2}))?$/.exec(timezone ?? '')
  if (!m) return null
  const offsetMin = m[1] ? (m[1] === '-' ? -1 : 1) * (Number(m[2]) * 60 + Number(m[3])) : 0
  const t = new Date(now.getTime() + offsetMin * 60_000)
  return `${String(t.getUTCHours()).padStart(2, '0')}:${String(t.getUTCMinutes()).padStart(2, '0')}`
}

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1)

// Traduce con el navegador; si no conoce un código lo devuelve tal cual y entonces se
// usa el nombre original (en inglés) que viene en los datos.
export function languageNames(codes, names, lang = 'es') {
  if (!codes?.length) return names.join(', ')
  const display = displayLanguages(lang)
  return capitalize(codes.map((c, i) => {
    const name = display.of(c)
    return name && name !== c ? name : names[i] ?? c
  }).join(', '))
}

export function currencyNames(codes, symbols = [], lang = 'es') {
  const display = displayCurrencies(lang)
  return capitalize(codes.map((c, i) => {
    const name = display.of(c) ?? c
    const symbol = symbols[i]
    return symbol && symbol !== c ? `${name} (${symbol})` : name
  }).join(', '))
}

// Misma normalización que slugify en el backend
export function canonicalSlug(slug) {
  return slug.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
}

const HTML_ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }

export function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (ch) => HTML_ESCAPES[ch])
}

const decimals = (lang, digits) =>
  new Intl.NumberFormat(LOCALES[lang], { minimumFractionDigits: digits, maximumFractionDigits: digits })

// En español un billón es un millón de millones; en inglés, «trillion»
const MONEY_SCALES = {
  es: [[1e12, 'billones'], [1e9, 'mil millones'], [1e6, 'millones']],
  en: [[1e12, 'trillion'], [1e9, 'billion'], [1e6, 'million']],
}

export function economyValue({ id, unit, value }, lang = 'es') {
  const one = decimals(lang, 1)
  const none = decimals(lang, 0)
  const en = lang === 'en'
  if (unit === 'pct') return en ? `${one.format(value)}%` : `${one.format(value)} %`
  if (unit === 'pct_gdp') return en ? `${one.format(value)}% of GDP` : `${one.format(value)} % del PIB`
  const scale = id === 'gdp' && MONEY_SCALES[lang].find(([d]) => Math.abs(value) >= d)
  if (scale) {
    const amount = one.format(value / scale[0])
    return en ? `US$${amount} ${scale[1]}` : `${amount} ${scale[1]} de US$`
  }
  return en ? `US$${none.format(value)}` : `${none.format(value)} US$`
}

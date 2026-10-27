const relative = new Intl.RelativeTimeFormat('es', { numeric: 'auto' })
const languages = new Intl.DisplayNames(['es'], { type: 'language' })

export function timeAgo(epochSeconds, now = Date.now()) {
  const diff = epochSeconds * 1000 - now
  const hours = Math.round(diff / 3_600_000)
  if (Math.abs(hours) < 1) return relative.format(Math.round(diff / 60_000), 'minute')
  if (Math.abs(hours) < 48) return relative.format(hours, 'hour')
  return relative.format(Math.round(hours / 24), 'day')
}

export function languageName(code) {
  try {
    return languages.of(code)
  } catch {
    return code
  }
}

export const formatDate = (epochSeconds) => new Date(epochSeconds * 1000).toLocaleDateString('es-ES')

// REST Countries da husos como "UTC+05:30"; se calcula la hora sin depender de IANA
export function localTime(timezone, now = new Date()) {
  const m = /^UTC(?:([+-])(\d{2}):(\d{2}))?$/.exec(timezone ?? '')
  if (!m) return null
  const offsetMin = m[1] ? (m[1] === '-' ? -1 : 1) * (Number(m[2]) * 60 + Number(m[3])) : 0
  const t = new Date(now.getTime() + offsetMin * 60_000)
  return `${String(t.getUTCHours()).padStart(2, '0')}:${String(t.getUTCMinutes()).padStart(2, '0')}`
}

import { localTime } from '../format'

export default function CountryHeader({ country, cover }) {
  const facts = [
    ['Capital', country.capital],
    ['Idiomas', country.languages.join(', ')],
    ['Moneda', country.currencies.join(', ')],
    ['Población', country.population?.toLocaleString('es-ES')],
    ['Hora local', localTime(country.timezones[0])],
  ].filter(([, v]) => v)

  return (
    <header className="country-header">
      <div className="country-cover">
        {cover && <img src={cover.thumb} alt="" />}
      </div>
      <div className="title-row">
        {country.flag_svg && <img className="flag" src={country.flag_svg} alt={`Bandera de ${country.name_es}`} />}
        <h2>{country.name_es}</h2>
      </div>
      <dl className="facts">
        {facts.map(([k, v]) => (
          <div key={k}><dt>{k}</dt><dd>{v}</dd></div>
        ))}
      </dl>
    </header>
  )
}

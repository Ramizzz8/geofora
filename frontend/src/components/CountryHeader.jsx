import { currencyNames, languageNames, localTime } from '../format'
import { countryName, useLang } from '../i18n'

export default function CountryHeader({ country, cover }) {
  const { lang, t } = useLang()
  const name = countryName(country, lang)
  const facts = [
    [t('capital'), country.capital],
    [t('languages'), languageNames(country.language_codes, country.languages, lang)],
    [t('currency'), currencyNames(country.currencies, country.currency_symbols, lang)],
    [t('population'), country.population?.toLocaleString(lang === 'en' ? 'en-GB' : 'es-ES')],
    [t('localTime'), localTime(country.timezones[0])],
  ].filter(([, v]) => v)

  return (
    <header className="country-header">
      <div className="country-cover">
        {cover && <img src={cover.thumb} alt="" />}
      </div>
      <div className="title-row">
        {country.flag_svg && <img className="flag" src={country.flag_svg} alt={t('flagOf', { name })} />}
        <h2>{name}</h2>
      </div>
      <dl className="facts">
        {facts.map(([k, v]) => (
          <div key={k}><dt>{k}</dt><dd>{v}</dd></div>
        ))}
      </dl>
    </header>
  )
}

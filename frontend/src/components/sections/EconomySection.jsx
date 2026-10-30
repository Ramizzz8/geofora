import { getEconomy } from '../../api'
import { economyValue } from '../../format'
import { useLang } from '../../i18n'
import { useFetch } from '../../useFetch'
import Sparkline from '../Sparkline'
import Section from './Section'

const OLD_AFTER_YEARS = 3 // un dato de hace más años se marca para que no parezca actual

export default function EconomySection({ slug }) {
  const state = useFetch(getEconomy, slug)
  const { lang, t } = useLang()
  const thisYear = new Date().getFullYear()
  return (
    <Section title={t('economy')} state={state}>
      {(data) => data.indicators.length === 0 ? (
        <p className="muted">{t('noEconomy')}</p>
      ) : (
        <>
          <ul className="economy">
            {data.indicators.map((i) => (
              <li key={i.id}>
                <span className="eco-label">{t(`eco.${i.id}`)}</span>
                <span className="eco-value">
                  {economyValue(i, lang)}{' '}
                  <span className={`eco-year ${thisYear - i.year > OLD_AFTER_YEARS ? 'old' : ''}`}>({i.year})</span>
                </span>
                <Sparkline series={i.series} />
              </li>
            ))}
          </ul>
          <p className="source">{t('economySource')}</p>
        </>
      )}
    </Section>
  )
}

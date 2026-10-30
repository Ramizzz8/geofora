import { getEconomy } from '../../api'
import { economyValue } from '../../format'
import { useFetch } from '../../useFetch'
import Sparkline from '../Sparkline'
import Section from './Section'

const OLD_AFTER_YEARS = 3 // un dato de hace más años se marca para que no parezca actual

export default function EconomySection({ slug }) {
  const state = useFetch(getEconomy, slug)
  const thisYear = new Date().getFullYear()
  return (
    <Section title="Economía" state={state}>
      {(data) => data.indicators.length === 0 ? (
        <p className="muted">Sin datos económicos recientes</p>
      ) : (
        <>
          <ul className="economy">
            {data.indicators.map((i) => (
              <li key={i.id}>
                <span className="eco-label">{i.label}</span>
                <span className="eco-value">
                  {economyValue(i)}{' '}
                  <span className={`eco-year ${thisYear - i.year > OLD_AFTER_YEARS ? 'old' : ''}`}>({i.year})</span>
                </span>
                <Sparkline series={i.series} />
              </li>
            ))}
          </ul>
          <p className="source">Fuente: Banco Mundial · deuda pública: FMI</p>
        </>
      )}
    </Section>
  )
}

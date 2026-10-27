import { getCulture } from '../../api'
import { useFetch } from '../../useFetch'
import Section from './Section'

export default function CultureSection({ slug }) {
  const state = useFetch(getCulture, slug)
  return (
    <Section title="Cultura" state={state}>
      {(data) => (
        <>
          {data.thumbnail && <img className="culture-img" src={data.thumbnail} alt="" loading="lazy" />}
          <p>{data.extract}</p>
          <p className="links">
            <a href={data.page_url} target="_blank" rel="noopener noreferrer">Leer más en Wikipedia</a>
            {data.culture_url && (
              <> · <a href={data.culture_url} target="_blank" rel="noopener noreferrer">Cultura del país</a></>
            )}
          </p>
          <p className="source">Fuente: Wikipedia</p>
        </>
      )}
    </Section>
  )
}

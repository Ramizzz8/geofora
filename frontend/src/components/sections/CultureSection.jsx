import { useCallback } from 'react'
import { getCulture } from '../../api'
import { useLang } from '../../i18n'
import { useFetch } from '../../useFetch'
import Section from './Section'

export default function CultureSection({ slug }) {
  const { lang, t } = useLang()
  const state = useFetch(useCallback((s) => getCulture(s, lang), [lang]), slug)
  return (
    <Section title={t('culture')} state={state}>
      {(data) => (
        <>
          {data.thumbnail && <img className="culture-img" src={data.thumbnail} alt="" loading="lazy" />}
          <p>{data.extract}</p>
          <p className="links">
            <a href={data.page_url} target="_blank" rel="noopener noreferrer">{t('readMore')}</a>
            {data.culture_url && (
              <> · <a href={data.culture_url} target="_blank" rel="noopener noreferrer">{t('countryCulture')}</a></>
            )}
          </p>
          <p className="source">{t('cultureSource')}</p>
        </>
      )}
    </Section>
  )
}

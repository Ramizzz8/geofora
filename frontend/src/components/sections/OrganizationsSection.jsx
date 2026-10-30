import { formatDate } from '../../format'
import { useLang } from '../../i18n'

const short = (o, lang) => (lang === 'en' ? o.short_en ?? o.short : o.short)
const fullName = (o, lang) => (lang === 'en' ? o.name_en ?? o.name : o.name)
const description = (o, lang) => (lang === 'en' ? o.description_en ?? o.description : o.description)

export default function OrganizationsSection({ data, iso3, active, onToggle }) {
  const { lang, t } = useLang()
  if (!data) return null
  const orgs = data.organizations.filter((o) => o.members.includes(iso3))
  return (
    <section className="section">
      <h3>{t('organizations')}</h3>
      {orgs.length === 0 ? (
        <p className="muted">{t('noOrganizations')}</p>
      ) : (
        <>
          <div className="org-chips">
            {orgs.map((o) => (
              <button key={o.id} type="button" className="org-chip" aria-pressed={active === o.id}
                title={`${fullName(o, lang)}. ${description(o, lang)}`} onClick={() => onToggle(o.id)}>
                {short(o, lang)}
              </button>
            ))}
          </div>
          <p className="muted small">{t('orgsHint')}</p>
        </>
      )}
      <p className="source">{t('orgsSource', { date: formatDate(Date.parse(data.generated) / 1000, lang) })}</p>
    </section>
  )
}

export function OrgBanner({ org, onClear }) {
  const { lang, t } = useLang()
  return (
    <div className="org-banner" role="status">
      <span>{t('orgMembers', { org: short(org, lang), n: org.members.length })}</span>
      <button type="button" onClick={onClear} aria-label={t('orgClear')}>×</button>
    </div>
  )
}

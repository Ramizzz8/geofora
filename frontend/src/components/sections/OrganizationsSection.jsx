import { formatDate } from '../../format'

export default function OrganizationsSection({ data, iso3, active, onToggle }) {
  if (!data) return null
  const orgs = data.organizations.filter((o) => o.members.includes(iso3))
  return (
    <section className="section">
      <h3>Organizaciones</h3>
      {orgs.length === 0 ? (
        <p className="muted">No pertenece a ninguna de las organizaciones que seguimos</p>
      ) : (
        <>
          <div className="org-chips">
            {orgs.map((o) => (
              <button key={o.id} type="button" className="org-chip" aria-pressed={active === o.id}
                title={`${o.name}. ${o.description}`} onClick={() => onToggle(o.id)}>
                {o.short}
              </button>
            ))}
          </div>
          <p className="muted small">Pulsa una para ver todos sus miembros en el globo.</p>
        </>
      )}
      <p className="source">Fuente: Wikidata, revisado el {formatDate(Date.parse(data.generated) / 1000)}</p>
    </section>
  )
}

export function OrgBanner({ org, onClear }) {
  return (
    <div className="org-banner" role="status">
      <span>Miembros de {org.short} ({org.members.length})</span>
      <button type="button" onClick={onClear} aria-label="Quitar resaltado">×</button>
    </div>
  )
}

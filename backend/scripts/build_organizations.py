"""Genera data/organizations.json con los miembros actuales de cada organización.

Fuente: Wikidata. Un país es miembro si tiene «miembro de» (P463) la organización, o si la
organización tiene «tiene como parte» (P527) al país, en ambos casos sin fecha de fin.
Se ejecuta a mano (python -m scripts.build_organizations), se revisa el resultado y se versiona.
"""
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

import httpx

from app.http import USER_AGENT

SPARQL_URL = "https://query.wikidata.org/sparql"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "organizations.json"
COUNTRIES = ROOT / "data" / "countries.json"

ORGANIZATIONS = [
    {"id": "onu", "qid": "Q1065", "short": "ONU", "name": "Organización de las Naciones Unidas",
     "description": "Organización mundial de Estados para la paz, la seguridad y la cooperación internacional.",
     "short_en": "UN", "name_en": "United Nations",
     "description_en": "Global organization of states for peace, security and international cooperation."},
    {"id": "ue", "qid": "Q458", "short": "UE", "name": "Unión Europea",
     "description": "Unión política y económica de Estados europeos con mercado único y, en la mayoría, moneda común.",
     "short_en": "EU", "name_en": "European Union",
     "description_en": "Political and economic union of European states with a single market and, for most members, a common currency."},
    {"id": "otan", "qid": "Q7184", "short": "OTAN", "name": "Organización del Tratado del Atlántico Norte",
     "description": "Alianza militar de defensa colectiva entre países de Europa y América del Norte.",
     "short_en": "NATO", "name_en": "North Atlantic Treaty Organization",
     "description_en": "Collective defence alliance between countries of Europe and North America."},
    {"id": "g7", "qid": "Q1764511", "short": "G7", "name": "Grupo de los Siete",
     "description": "Foro de siete grandes economías industrializadas.",
     "short_en": "G7", "name_en": "Group of Seven",
     "description_en": "Forum of seven major industrialised economies."},
    {"id": "g20", "qid": "Q19771", "short": "G20", "name": "Grupo de los Veinte",
     "description": "Foro de las principales economías desarrolladas y emergentes del mundo.",
     "short_en": "G20", "name_en": "Group of Twenty",
     "description_en": "Forum of the world's main developed and emerging economies."},
    {"id": "brics", "qid": "Q243630", "short": "BRICS", "name": "BRICS",
     "description": "Agrupación de grandes economías emergentes, iniciada por Brasil, Rusia, India, China y Sudáfrica.",
     "short_en": "BRICS", "name_en": "BRICS",
     "description_en": "Group of major emerging economies, started by Brazil, Russia, India, China and South Africa."},
    {"id": "opep", "qid": "Q7795", "short": "OPEP", "name": "Organización de Países Exportadores de Petróleo",
     "description": "Coordina la política petrolera de grandes países productores.",
     "short_en": "OPEC", "name_en": "Organization of the Petroleum Exporting Countries",
     "description_en": "Coordinates the oil policy of major producing countries."},
    {"id": "ocde", "qid": "Q41550", "short": "OCDE", "name": "Organización para la Cooperación y el Desarrollo Económicos",
     "description": "Organización de economías desarrolladas que coordina políticas económicas y sociales.",
     "short_en": "OECD", "name_en": "Organisation for Economic Co-operation and Development",
     "description_en": "Organization of developed economies that coordinates economic and social policy."},
    {"id": "mercosur", "qid": "Q4264", "short": "Mercosur", "name": "Mercado Común del Sur",
     "description": "Bloque comercial de América del Sur.",
     "short_en": "Mercosur", "name_en": "Southern Common Market",
     "description_en": "Trade bloc of South America."},
    {"id": "asean", "qid": "Q7768", "short": "ASEAN", "name": "Asociación de Naciones de Asia Sudoriental",
     "description": "Organización regional de cooperación política y económica del Sudeste Asiático.",
     "short_en": "ASEAN", "name_en": "Association of Southeast Asian Nations",
     "description_en": "Regional organization for political and economic cooperation in Southeast Asia."},
    {"id": "ua", "qid": "Q7159", "short": "UA", "name": "Unión Africana",
     "description": "Organización continental de los Estados de África.",
     "short_en": "AU", "name_en": "African Union",
     "description_en": "Continental organization of the states of Africa."},
    {"id": "liga-arabe", "qid": "Q7172", "short": "Liga Árabe", "name": "Liga de los Estados Árabes",
     "description": "Organización regional de Estados árabes de Oriente Medio y el norte de África.",
     "short_en": "Arab League", "name_en": "League of Arab States",
     "description_en": "Regional organization of Arab states of the Middle East and North Africa."},
    {"id": "commonwealth", "qid": "Q7785", "short": "Commonwealth", "name": "Mancomunidad de Naciones",
     "description": "Asociación de Estados, en su mayoría antiguos territorios del Imperio británico.",
     "short_en": "Commonwealth", "name_en": "Commonwealth of Nations",
     "description_en": "Association of states, most of them former territories of the British Empire."},
    {"id": "apec", "qid": "Q170481", "short": "APEC", "name": "Foro de Cooperación Económica Asia-Pacífico",
     "description": "Foro de economías de la cuenca del Pacífico para el comercio y la inversión.",
     "short_en": "APEC", "name_en": "Asia-Pacific Economic Cooperation",
     "description_en": "Forum of Pacific Rim economies for trade and investment."},
]

# Entidades de Wikidata que son miembro pero no tienen código ISO: el Reino de Dinamarca y
# los Países Bajos (Q55, la parte europea del Reino)
KINGDOMS = {"Q29999": "NLD", "Q55": "NLD", "Q756617": "DNK"}

# Errores de Wikidata revisados a mano (octubre de 2026). Se guardan en el JSON con su motivo.
CORRECTIONS = {
    "brics": {"remove": ["BGD", "BHR", "BLR", "DZA", "SAU"],
              "reason": "Bangladés, Baréin, Bielorrusia y Argelia son socios o candidatos; Arabia Saudí fue invitada en 2023 y no ha confirmado su adhesión"},
    "opep": {"remove": ["AGO"], "reason": "Angola salió de la OPEP en enero de 2024"},
    "mercosur": {"remove": ["MEX", "VEN"], "reason": "México no es miembro; Venezuela está suspendida desde 2016"},
    "asean": {"remove": ["AUS", "PNG"], "reason": "Australia es socio externo y Papúa Nueva Guinea, observador"},
    "commonwealth": {"add": ["GBR"], "reason": "Wikidata no registra al Reino Unido como miembro"},
    "ua": {"reason": "La República Árabe Saharaui Democrática es miembro de la UA, pero no se asocia al territorio "
                     "del Sáhara Occidental del mapa para no tomar partido en un territorio en disputa"},
}

QUERY = """
SELECT DISTINCT ?org ?country ?iso WHERE {
  VALUES ?org { %s }
  { ?country p:P463 ?st . ?st ps:P463 ?org . FILTER NOT EXISTS { ?st pq:P582 ?end } }
  UNION
  { ?org p:P527 ?st . ?st ps:P527 ?country . FILTER NOT EXISTS { ?st pq:P582 ?end } }
  OPTIONAL { ?country wdt:P298 ?iso . }
}
"""


def members_from_sparql(rows: list[dict], known: set[str]) -> dict[str, list[str]]:
    members: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        qid = row["org"]["value"].rsplit("/", 1)[1]
        country = row.get("country", {}).get("value", "").rsplit("/", 1)[-1]
        iso = row["iso"]["value"] if "iso" in row else KINGDOMS.get(country)
        if iso in known:
            members[qid].add(iso)
    return {qid: sorted(isos) for qid, isos in members.items()}


def apply_corrections(members: dict[str, list[str]], corrections: dict) -> dict[str, list[str]]:
    fixed = {}
    for org_id, isos in members.items():
        c = corrections.get(org_id, {})
        fixed[org_id] = sorted((set(isos) - set(c.get("remove", []))) | set(c.get("add", [])))
    return fixed


def main() -> None:
    known = {c["iso3"] for c in json.loads(COUNTRIES.read_text(encoding="utf-8"))}
    query = QUERY % " ".join(f"wd:{o['qid']}" for o in ORGANIZATIONS)
    with httpx.Client(timeout=120, headers={"User-Agent": USER_AGENT}) as client:
        r = client.get(SPARQL_URL, params={"query": query, "format": "json"})
        r.raise_for_status()
    by_qid = members_from_sparql(r.json()["results"]["bindings"], known)
    members = apply_corrections({o["id"]: by_qid.get(o["qid"], []) for o in ORGANIZATIONS}, CORRECTIONS)
    out = {
        "source": "Wikidata (miembro de P463 / tiene como parte P527, sin fecha de fin), con correcciones revisadas",
        "generated": date.today().isoformat(),
        "corrections": {k: v["reason"] for k, v in CORRECTIONS.items()},
        "organizations": [
            {k: v for k, v in o.items() if k != "qid"} | {"members": members[o["id"]]}
            for o in ORGANIZATIONS
        ],
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for o in out["organizations"]:
        print(f"{o['short']:<13} {len(o['members']):>3}  {' '.join(o['members']) if len(o['members']) <= 40 else ''}")


if __name__ == "__main__":
    main()

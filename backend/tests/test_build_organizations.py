from scripts.build_organizations import ORGANIZATIONS, members_from_sparql


def binding(org_qid, iso3):
    return {"org": {"value": f"http://www.wikidata.org/entity/{org_qid}"}, "country": {"value": "http://www.wikidata.org/entity/Q1"}, "iso": {"value": iso3}}


def test_groups_members_by_organization_and_keeps_known_countries():
    rows = [binding("Q7184", "ESP"), binding("Q7184", "FRA"), binding("Q458", "ESP"),
            binding("Q458", "ESP"),  # repetido (miembro por las dos vías)
            binding("Q458", "XXX")]  # código que no está en nuestros países
    members = members_from_sparql(rows, known={"ESP", "FRA"})
    assert members == {"Q7184": ["ESP", "FRA"], "Q458": ["ESP"]}


def test_every_organization_has_spanish_name_and_description():
    for org in ORGANIZATIONS:
        assert org["id"] and org["qid"].startswith("Q")
        assert org["short"] and org["name"] and org["description"]


def test_kingdoms_count_as_their_country():
    rows = [{"org": {"value": "http://www.wikidata.org/entity/Q458"},
             "country": {"value": "http://www.wikidata.org/entity/Q55"}}]  # Países Bajos, sin ISO en Wikidata
    assert members_from_sparql(rows, known={"NLD"}) == {"Q458": ["NLD"]}


def test_corrections_are_applied_and_recorded():
    from scripts.build_organizations import apply_corrections
    members = {"brics": ["BLR", "BRA", "CHN"], "commonwealth": ["AUS"]}
    corrections = {
        "brics": {"remove": ["BLR"], "reason": "socio, no miembro"},
        "commonwealth": {"add": ["GBR"], "reason": "falta en Wikidata"},
    }
    fixed = apply_corrections(members, corrections)
    assert fixed == {"brics": ["BRA", "CHN"], "commonwealth": ["AUS", "GBR"]}

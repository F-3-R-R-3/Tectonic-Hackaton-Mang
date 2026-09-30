"""Bouw het SignalEngine-contract (JSON) uit de echte dataset + functies.

Dit is de brug tussen de back-end en de React-website. Het gebruikt **de echte
functies** uit ``backend/signals/`` (``find_recurring_expenses`` en
``analyze_home_purchase``) en de gedeelde leeslaag ``backend/data/`` om per klant
een set **signalen** te bouwen volgens de flow * signaal ➜ probleem ➜ oplossing *.

Gebruik:
    uv run python -m tectonic_hackaton_mang.backend.website_api            # print JSON
    uv run python -m tectonic_hackaton_mang.backend.website_api --out out.json
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import defaultdict
from datetime import UTC, datetime

from .data.connection import get_db
from .data.readers import (
    klant_naam,
    load_abonnementen,
    load_klanten,
    load_spaar_interacties,
    load_verzekeringen,
    load_zoekopdrachten,
    reference_date,
)
from .data.transactions import Transaction, load_transactions, months_covered
from .signals.home_purchase import analyze_home_purchase
from .signals.recurring_expenses import find_recurring_expenses

PERSONA_LABELS = {
    "student": "Student",
    "gezin": "Gezin met kinderen",
    "gepensioneerd": "Gepensioneerde",
    "koppel": "Koppel",
    "alleenstaand": "Alleenstaande professional",
}

DEMO_LABELS = {
    "student": "Student",
    "jonge_starter": "Jonge starter",
    "gezin": "Gezin met kinderen",
    "alleenstaande_professional": "Alleenstaande professional",
    "gepensioneerde": "Gepensioneerde",
}

AUTO_KEYWORDS = ("q8", "shell", "total", "bosch", "autokeuring", "autogarage", "tank", "banden")

HOUSE_GOALS = {"huis", "woning", "renovatie", "verbouwing", "verbouw", "woonsparen"}


def euro(value: float) -> str:
    """Formatteer als '€ 1.234,56' (Belgische notatie)."""
    text = f"{value:,.2f}"
    return "€ " + text.replace(",", " ").replace(".", ",")


def _score(value: float, low: float, high: float, base: int = 55, top: int = 96) -> int:
    if high <= low:
        return base
    ratio = max(0.0, min(1.0, (value - low) / (high - low)))
    return int(round(base + ratio * (top - base)))


def _impact(value: float, high: float) -> str:
    if value >= high:
        return "hoog"
    if value >= high / 2:
        return "middel"
    return "laag"


# ---------------------------------------------------------------------------
# Signaal-builders — elk signaal volgt signaal ➜ probleem ➜ oplossing
# ---------------------------------------------------------------------------
def _signal_slapend_geld(block: dict) -> dict | None:
    dormant = [s for s in block["subscriptions"] if s["dormant"]]
    if not dormant:
        return None
    monthly = round(sum(s["monthly_cost"] for s in dormant), 2)
    yearly = round(sum(s["yearly_cost"] for s in dormant), 2)
    names = [s["name"] for s in dormant]
    evidence = []
    for s in dormant[:4]:
        last = s["last_used"] or "nooit gebruikt"
        evidence.append(
            {
                "label": s["name"],
                "value": f"{euro(s['monthly_cost'])} / maand · laatst {last}",
                "trend": "down",
            }
        )
    evidence.append(
        {"label": "Totaal slapend", "value": f"{euro(yearly)} / jaar", "trend": "up"}
    )
    return {
        "type": "slapend_geld_abonnement",
        "source_function": "find_recurring_expenses",
        "title": f"Je betaalt voor {len(dormant)} abonnement(en) die je amper gebruikt",
        "category": "slapend_geld",
        "signal_score": _score(yearly, 40, 700),
        "impact": _impact(yearly, 300),
        "urgency": "middel" if yearly >= 150 else "laag",
        "detected_at": None,
        "signal": {
            "headline": "Signaal: slapend geld",
            "summary": (
                f"{len(dormant)} actieve abonnement(en) — {', '.join(names[:3])} — "
                f"werden al minstens 90 dagen niet meer gebruikt. Samen {euro(yearly)} per jaar."
            ),
            "evidence": evidence,
        },
        "problem": {
            "headline": "Probleem: geld verdwijnt naar vergeten abonnementen",
            "description": (
                "Kleine maandelijkse bedragen vallen niet op, maar samen kosten ze je elk "
                "jaar een mooi bedrag. Je gebruikt ze niet meer actief."
            ),
            "impact_label": f"{euro(yearly)} / jaar",
            "consequences": [
                "Je betaalt voor iets dat je niet gebruikt",
                "Moeilijk op te merken tussen andere transacties",
                "Geld dat je liever in je spaardoel steekt",
            ],
        },
        "solution": {
            "id": "sol_subscription_audit",
            "title": "Abonnementen-audit",
            "description": (
                "Overzicht van al je terugkerende betalingen met een stop-knop per "
                "abonnement. Wij regelen de opzegging voor je."
            ),
            "cta": f"Stop {names[0]}",
            "action_type": "cancel_subscription",
            "estimated_benefit": f"{euro(yearly)} / jaar terug",
            "steps": [
                "Je ziet alle slapende abonnementen op een rij",
                "Kies wat je wil houden en wat niet",
                "Wij versturen de opzegging namens jou",
            ],
        },
    }


def _signal_verhuizing(klant: dict, verzekeringen: list[dict]) -> dict | None:
    active = [v for v in verzekeringen if v["actief"]]
    if not klant.get("verhuisd_recent") or not active:
        return None
    evidence = [
        {
            "label": v["type"].capitalize(),
            "value": v["polisadres"],
            "trend": "flat",
        }
        for v in active
    ]
    evidence.append(
        {
            "label": "Nieuwe woonplaats",
            "value": f"{klant['woonplaats']} {klant['postcode']}",
            "trend": "up",
        }
    )
    yearly = round(sum(v["maandpremie"] for v in active) * 12, 2)
    return {
        "type": "verhuizing_zonder_adresupdate",
        "source_function": "dataset.py (verzekeringen)",
        "title": "Verhuizing gedetecteerd, polisadressen niet bijgewerkt",
        "category": "administratie",
        "signal_score": _score(len(active), 1, 4, base=78, top=96),
        "impact": "hoog",
        "urgency": "hoog",
        "detected_at": None,
        "signal": {
            "headline": "Signaal: je bent verhuisd",
            "summary": (
                f"Je verhuisde recent naar {klant['woonplaats']}, maar {len(active)} "
                f"verzekeringspolis(se) staan nog op een ander adres."
            ),
            "evidence": evidence,
        },
        "problem": {
            "headline": "Probleem: verzekeringen dekken mogelijk het verkeerde adres",
            "description": (
                "Bij een verhuizing moeten je brand-, inboedel- en familiale verzekering "
                "het nieuwe adres volgen. Zolang dat niet gebeurd is, loop je risico op "
                "een weigering bij schade."
            ),
            "impact_label": f"Risico op niet-gedekt bij schade · premies {euro(yearly)}/jaar",
            "consequences": [
                "Schadegeval kan geweigerd worden omdat het adres niet klopt",
                "Je juridische briefwisseling komt op het oude adres aan",
                "Polissen lopen naast je nieuwe situatie",
            ],
        },
        "solution": {
            "id": "sol_auto_address_sync",
            "title": "Auto-Address Sync",
            "description": (
                "We werken in één klik alle KBC-polisadressen bij naar je nieuwe woonst "
                "en bezorgen je een bevestiging per e-mail."
            ),
            "cta": f"{len(active)} adres(sen) nu bijwerken",
            "action_type": "auto_address_sync",
            "estimated_benefit": "Alles correct gedekt vanaf vandaag",
            "steps": [
                f"We halen je {len(active)} polis(sen) op die nog op het oude adres staan",
                f"Je bevestigt het nieuwe adres ({klant['woonplaats']})",
                "Wij versturen de wijziging en je krijgt een bevestiging",
            ],
        },
    }


def _signal_mobiliteit(klant: dict, transacties: list[Transaction], covered: int) -> dict | None:
    if not klant.get("heeft_auto"):
        return None
    auto = [
        t
        for t in transacties
        if (t.category and "auto" in str(t.category).lower())
        or any(k in t.name.lower() for k in AUTO_KEYWORDS)
    ]
    total = round(sum(abs(t.amount) for t in auto), 2)
    if total <= 0:
        return None
    monthly = round(total / max(1, covered), 2)
    benchmark = 298.0
    diff = round(max(monthly - benchmark, 0.0), 2)
    evidence = [
        {"label": "Autokosten laatste periode", "value": euro(total), "trend": "up"},
        {"label": "Gemiddeld per maand", "value": euro(monthly), "trend": "up"},
        {"label": "Vergelijkbare profielen", "value": euro(benchmark) + " / maand", "trend": "flat"},
    ]
    return {
        "type": "autokosten_onoverzichtelijk",
        "source_function": "transactions.py + dataset.py",
        "title": "Totale autokost is onoverzichtelijk",
        "category": "mobiliteit",
        "signal_score": _score(monthly, 120, 600, base=62, top=88),
        "impact": _impact(monthly, 400),
        "urgency": "middel",
        "detected_at": None,
        "signal": {
            "headline": "Signaal: je autokosten lopen op",
            "summary": (
                f"Je auto kost je gemiddeld {euro(monthly)} per maand, verspreid over "
                f"brandstof, verzekering, keuring en onderhoud. Het totaal is nergens zichtbaar."
            ),
            "evidence": evidence,
        },
        "problem": {
            "headline": "Probleem: je weet niet wat de auto écht kost",
            "description": (
                "Zonder totaalbeeld is het onmogelijk om te besparen op verzekering, "
                "brandstof of een goedkopere oplossing. Kosten blijven verspreid over "
                "losse afschriften."
            ),
            "impact_label": (
                f"Gemiddeld {euro(diff)} / maand te veel" if diff else "Kosten onzichtbaar"
            ),
            "consequences": [
                "Je betaalt mogelijk te veel premie voor je rijprofiel",
                "Onderhoud en keuring worden telkens een verrassing",
                "Geen vergelijking met andere profielen mogelijk",
            ],
        },
        "solution": {
            "id": "sol_mobility_dashboard",
            "title": "Mobiliteits-dashboard",
            "description": (
                "Eén overzicht van alle autokosten per maand, met een bespaartip zodra "
                "een kost boven het gemiddelde uitkomt."
            ),
            "cta": "Open mijn mobiliteits-dashboard",
            "action_type": "mobility_dashboard",
            "estimated_benefit": (
                f"Gemiddeld {euro(diff)} / maand besparen" if diff else "Volledig overzicht"
            ),
            "steps": [
                "We bundelen alle autogerelateerde transacties",
                "Je ziet je maandtotaal naast vergelijkbare profielen",
                "We stellen concrete bespaarkansen voor",
            ],
        },
    }


def _signal_student(klant: dict, block: dict) -> dict | None:
    if klant.get("gezinssituatie") != "student":
        return None
    candidates = [
        s
        for s in block["subscriptions"]
        if s["active"] and s["category"] in ("streaming", "sport", "software")
    ]
    if not candidates:
        return None
    yearly = round(sum(s["yearly_cost"] for s in candidates), 2)
    evidence = [
        {"label": s["name"], "value": f"{euro(s['monthly_cost'])} / maand", "trend": "flat"}
        for s in candidates[:4]
    ]
    return {
        "type": "slapend_geld_abonnement",
        "source_function": "find_recurring_expenses",
        "title": "Studentenkorting blijft onbenut",
        "category": "slapend_geld",
        "signal_score": _score(yearly, 50, 400, base=52, top=74),
        "impact": "laag",
        "urgency": "laag",
        "detected_at": None,
        "signal": {
            "headline": "Signaal: je betaalt het volle tarief",
            "summary": (
                f"Je bent student, maar betaalt voor {len(candidates)} diensten het "
                f"standaardtarief in plaats van het verlaagde studententarief."
            ),
            "evidence": evidence,
        },
        "problem": {
            "headline": "Probleem: je laat korting liggen",
            "description": (
                "Als student kom je in aanmerking voor verlaagde tarieven, maar die "
                "worden niet automatisch toegepast."
            ),
            "impact_label": f"Tot {euro(yearly)} / jaar",
            "consequences": [
                "Je betaalt maandelijks te veel",
                "Korting moet je zelf aanvragen",
                "Geld dat naar je spaardoel kon gaan",
            ],
        },
        "solution": {
            "id": "sol_subscription_audit",
            "title": "Abonnementen-audit",
            "description": (
                "We checken je terugkerende betalingen en zetten de kortingen aan waar "
                "je recht op hebt."
            ),
            "cta": "Zet studentenkorting aan",
            "action_type": "cancel_subscription",
            "estimated_benefit": f"Tot {euro(yearly)} / jaar terug",
            "steps": [
                "We overlopen je abonnementen",
                "We markeren waar een studententarief bestaat",
                "Wij vragen de korting voor je aan",
            ],
        },
    }


def _signal_sparen(profile: dict) -> dict | None:
    advice = profile["advice"]
    signals = profile["signals"]
    status = advice["status"]
    goal = signals.get("savings_goal")
    capacity = advice["effective_monthly_saving"]
    target = advice["savings_target"]
    current = advice["current_savings"]
    months = advice["months_to_save"]

    if status == "not_ready":
        return {
            "type": "geen_concreet_spaarplan",
            "source_function": "analyze_home_purchase",
            "title": "Je vaste kosten blokkeren een spaarplan",
            "category": "sparen",
            "signal_score": 70,
            "impact": "middel",
            "urgency": "middel",
            "detected_at": None,
            "signal": {
                "headline": "Signaal: geen ruimte om te sparen",
                "summary": (
                    "Je hebt onvoldoende vast inkomen of je uitgaven zijn hoger dan je "
                    "inkomen. Sparen lukt pas als de vaste kosten dalen."
                ),
                "evidence": [
                    {"label": "Maandinkomen", "value": euro(signals["monthly_income"]), "trend": "flat"},
                    {"label": "Maanduitgaven", "value": euro(signals["monthly_expenses"]), "trend": "up"},
                    {"label": "Vaste kosten", "value": euro(signals["monthly_fixed_costs"]), "trend": "up"},
                ],
            },
            "problem": {
                "headline": "Probleem: negatieve spaarcapaciteit",
                "description": (
                    "Zolang je vaste kosten hoger zijn dan wat je overhoudt, groeit je "
                    "buffer niet en schuift elk doel verder weg."
                ),
                "impact_label": "Geen ruimte om te sparen",
                "consequences": [
                    "Je buffer groeit niet",
                    "Onnodige maandelijkse druk",
                    "Doelen blijven buiten bereik",
                ],
            },
            "solution": {
                "id": "sol_subscription_audit",
                "title": "Vaste-kosten-audit",
                "description": (
                    "We overlopen je abonnementen en verzekeringen en snijden in de "
                    "slapende kosten, zodat er ruimte komt om te sparen."
                ),
                "cta": "Verlaag mijn vaste kosten",
                "action_type": "cancel_subscription",
                "estimated_benefit": "Ruimte om te sparen creëren",
                "steps": [
                    "We tonen je vaste kosten per maand",
                    "We markeren wat je kan schrappen",
                    "Wij regelen de opzeggingen",
                ],
            },
        }

    if status == "ready_to_buy":
        title = "Je kan een woning kopen"
        headline = "Signaal: je bent klaar om te kopen"
        summary = advice["summary"]
        solution_title = "Woningkrediet opstarten"
        cta = "Bekijk mijn leencapaciteit"
        action_type = "start_mortgage"
        benefit = f"Leencapaciteit tot {euro(advice['max_loan'])}"
    else:
        title = "Je spaart, maar zonder concreet plan"
        headline = "Signaal: spaardoel zonder strategie"
        summary = advice["summary"]
        solution_title = "Dynamisch spaarplan"
        cta = "Start mijn spaarplan"
        action_type = "start_savings_plan"
        benefit = (
            f"Doel bereikt in {months} maanden"
            if months is not None
            else "Haalbaar maandbedrag voorstellen"
        )

    if goal and str(goal).lower() in HOUSE_GOALS:
        title = "Je wil een woning, maar het traject ontbreekt"
        headline = "Signaal: woningdoel zonder strategie"

    evidence = [
        {"label": "Maandelijks overschot", "value": euro(capacity), "trend": "flat"},
        {"label": "Huidig spaargeld", "value": euro(current), "trend": "flat"},
        {"label": "Doelbedrag", "value": euro(target), "trend": "flat"},
    ]
    if months is not None:
        evidence.append(
            {"label": "Verwachte haalbaarheid", "value": f"{months} maanden", "trend": "down"}
        )
    if signals.get("housing_queries"):
        evidence.append(
            {
                "label": "Zoekopdrachten",
                "value": f"{len(signals['housing_queries'])}x over wonen",
                "trend": "up",
            }
        )

    return {
        "type": "geen_concreet_spaarplan",
        "source_function": "analyze_home_purchase",
        "title": title,
        "category": "sparen",
        "signal_score": _score(capacity, 100, 1500, base=64, top=90),
        "impact": "hoog" if status == "ready_to_buy" else "middel",
        "urgency": "middel",
        "detected_at": None,
        "signal": {"headline": headline, "summary": summary, "evidence": evidence},
        "problem": {
            "headline": "Probleem: je doel blijft buiten bereik zonder traject",
            "description": (
                "Zonder vast spaarbedrag en een realistische timing schuift je doel elk "
                "jaar op. Je geld verliest bovendien waarde op een gewone spaarrekening."
            ),
            "impact_label": (
                f"Doel bereikt in {months} maanden"
                if months is not None
                else "Doel schuift elk jaar op"
            ),
            "consequences": [
                "Geen zicht op wanneer je genoeg hebt",
                "Overschot verdampt aan dagelijkse uitgaven",
                "Geen gebruik van een voordeliger spaarformule",
            ],
        },
        "solution": {
            "id": "sol_dynamic_savings",
            "title": solution_title,
            "description": (
                "Op basis van je overschot en je doel stellen we een haalbaar maandbedrag "
                "en een tijdslijn voor, en richten we een automatische overschrijving in."
            ),
            "cta": cta,
            "action_type": action_type,
            "estimated_benefit": benefit,
            "steps": [
                f"We bepalen een haalbaar maandbedrag ({euro(capacity)})",
                "Je kiest je doel en streefdatum",
                "We richten de automatische overschrijving in",
            ],
        },
    }


# ---------------------------------------------------------------------------
# Persona's bouwen
# ---------------------------------------------------------------------------
def _persona_label(klant: dict, tag: str | None) -> str:
    if tag:
        return DEMO_LABELS.get(tag, PERSONA_LABELS.get(klant["gezinssituatie"], "Klant"))
    return PERSONA_LABELS.get(klant["gezinssituatie"], "Klant")


def _why_persona(klant: dict, signals: list[dict], tag: str | None) -> list[str]:
    reasons: list[str] = []
    situatie = klant["gezinssituatie"]
    if situatie == "student":
        reasons.append("Studentenprofiel")
    if klant.get("aantal_kinderen"):
        reasons.append(f"{klant['aantal_kinderen']} kinderen")
    if klant.get("verhuisd_recent"):
        reasons.append("Recent verhuisd")
    if klant.get("heeft_auto"):
        reasons.append("Heeft een auto")
    if klant.get("spaardoel"):
        reasons.append(f"Spaardoel: {klant['spaardoel']}")
    categories = {s["category"] for s in signals}
    if "slapend_geld" in categories:
        reasons.append("Slapende abonnementen gedetecteerd")
    if "sparen" in categories:
        reasons.append("Spaaranalyse uitgevoerd")
    return reasons[:4] or ["Actieve klant in de dataset"]


def _demo_tags(conn: sqlite3.Connection) -> dict[int, str]:
    # De demo-persona's dragen hun tag in database.py; we leiden ze af uit id.
    from .data.generate import DEMO_PERSONAS

    return {p.id: p.tag for p in DEMO_PERSONAS}


def build_personas(conn: sqlite3.Connection) -> dict:
    klanten = load_klanten(conn)
    recurring = find_recurring_expenses(conn)
    home = analyze_home_purchase(conn)
    reference = reference_date(conn)

    blocks = {int(c["customer"]): c for c in recurring.get("customers", [])}
    profiles = {int(p["customer"]): p for p in home.get("profiles", [])}

    verz_by_klant: dict[int, list[dict]] = defaultdict(list)
    for v in load_verzekeringen(conn):
        verz_by_klant[int(v["klant_id"])].append(v)

    loaded = load_transactions(conn)
    tx_by_klant: dict[int, list[Transaction]] = defaultdict(list)
    if loaded is not None:
        for t in loaded[1]:
            if t.customer is not None:
                try:
                    tx_by_klant[int(t.customer)].append(t)
                except (TypeError, ValueError):
                    continue

    tags = _demo_tags(conn)
    personas: list[dict] = []

    for klant_id, klant in sorted(klanten.items()):
        block = blocks.get(klant_id, {"subscriptions": [], "dormant_count": 0})
        profile = profiles.get(klant_id)
        transactions = tx_by_klant.get(klant_id, [])
        covered = months_covered(transactions) if transactions else 1

        candidates = [
            _signal_verhuizing(klant, verz_by_klant.get(klant_id, [])),
            _signal_slapend_geld(block),
            _signal_mobiliteit(klant, transactions, covered),
            _signal_sparen(profile) if profile else None,
            _signal_student(klant, block),
        ]
        signals = []
        for sig in candidates:
            if sig is None:
                continue
            sig["id"] = f"sig_{klant_id}_{sig['type']}"
            sig["detected_at"] = (sig["detected_at"] or reference.isoformat())
            sig["status"] = "nieuw"
            signals.append(sig)
        signals.sort(key=lambda s: s["signal_score"], reverse=True)

        savings = profile["advice"]["current_savings"] if profile else 0.0
        persona = {
            "id": f"p_{klant_id}",
            "customer_id": klant_id,
            "name": klant_naam(klant),
            "initials": (klant.get("voornaam", "?")[:1] + klant.get("achternaam", "?")[:1]).upper(),
            "persona_type": klant["gezinssituatie"],
            "persona_label": _persona_label(klant, tags.get(klant_id)),
            "age": klant["leeftijd"],
            "family_situation": klant["gezinssituatie"],
            "city": klant["woonplaats"],
            "customer_since": None,
            "is_demo": bool(klant.get("is_demo")),
            "accounts": {"spaarrekening": round(savings, 2)},
            "monthly_income": profile["signals"]["monthly_income"] if profile else klant["inkomen_maand"],
            "monthly_expenses": profile["signals"]["monthly_expenses"] if profile else None,
            "why_persona": _why_persona(klant, signals, tags.get(klant_id)),
            "signals": signals,
        }
        personas.append(persona)

    # Demo-persona's eerst, daarna op aantal/score.
    personas.sort(
        key=lambda p: (not p["is_demo"], -len(p["signals"]), p["customer_id"])
    )

    return {
        "meta": {
            "generated_at": datetime.now(tz=UTC).isoformat(),
            "source": "live",
            "reference_date": reference.isoformat(),
            "customer_count": len(personas),
            "signal_count": sum(len(p["signals"]) for p in personas),
            "note": "Gebouwd uit data/fake.db via find_recurring_expenses + analyze_home_purchase.",
        },
        "personas": personas,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Bouw SignalEngine-contract uit de dataset.")
    parser.add_argument("--out", help="Schrijf JSON naar dit bestand i.p.v. stdout.")
    args = parser.parse_args()

    conn = get_db()
    try:
        payload = build_personas(conn)
    finally:
        conn.close()

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.out:
        from pathlib import Path

        Path(args.out).write_text(text, encoding="utf-8")
        print(f"geschreven: {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()

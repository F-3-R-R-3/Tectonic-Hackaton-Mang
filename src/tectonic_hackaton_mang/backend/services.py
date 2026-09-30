"""Service-laag: verbindt dataset, signaal-output en API-contract.

Bevat géén FastAPI- of startup-logica — alleen data ophalen en
omzetten naar de JSON-vorm die de frontend verwacht.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import OUTPUT_DIR
from .data.connection import get_db
from .data.readers import load_klanten, load_spaar_interacties, reference_date

# Gezinssituatie → persona-label zoals in de UI.
_PERSONA_LABELS: dict[str, str] = {
    "student": "Student",
    "alleenstaand": "Alleenstaande professional",
    "gezin": "Gezin met kinderen",
    "koppel": "Koppel",
    "gepensioneerd": "Gepensioneerde",
}


def _initials(voornaam: str, achternaam: str) -> str:
    parts = [p for p in (voornaam, achternaam) if p]
    return "".join(p[0].upper() for p in parts)[:2] or "?"


def _persona_id(klant_id: int) -> str:
    return str(klant_id)


def _parse_user_id(user_id: str | int) -> int:
    return int(user_id)


def _savings_balance(conn, klant_id: int) -> float:
    balances = [
        row["saldo_na"]
        for row in load_spaar_interacties(conn)
        if row["klant_id"] == klant_id and row.get("saldo_na") is not None
    ]
    return float(balances[-1]) if balances else 0.0


def list_users(*, demo_only: bool = True) -> list[dict[str, Any]]:
    """GET /users — persona's uit de database."""
    conn = get_db()
    try:
        klanten = load_klanten(conn)
        users: list[dict[str, Any]] = []
        for kid, k in klanten.items():
            if demo_only and not k.get("is_demo"):
                continue
            situatie = str(k.get("gezinssituatie") or "alleenstaand")
            voornaam = str(k.get("voornaam") or "")
            achternaam = str(k.get("achternaam") or "")
            users.append(
                {
                    "id": _persona_id(kid),
                    "name": f"{voornaam} {achternaam}".strip(),
                    "initials": _initials(voornaam, achternaam),
                    "persona_type": situatie,
                    "persona_label": _PERSONA_LABELS.get(situatie, situatie.title()),
                    "age": int(k.get("leeftijd") or 0),
                    "family_situation": situatie,
                    "city": str(k.get("woonplaats") or ""),
                    "customer_since": None,
                    "accounts": {
                        "zichtrekening": None,
                        "spaarrekening": _savings_balance(conn, kid),
                        "beleggingen": None,
                    },
                    "monthly_income": float(k.get("inkomen_maand") or 0.0),
                    "monthly_expenses": None,
                    "why_persona": [
                        f"Profiel: {situatie}",
                        f"Woonplaats: {k.get('woonplaats')}",
                        *(
                            [f"Spaardoel: {k['spaardoel']}"]
                            if k.get("spaardoel")
                            else []
                        ),
                    ],
                }
            )
        return users
    finally:
        conn.close()


def _load_signal_outputs() -> list[dict[str, Any]]:
    """Lees alle JSON-bestanden uit ``output/`` (geschreven door export)."""
    if not OUTPUT_DIR.exists():
        return []
    results: list[dict[str, Any]] = []
    for path in sorted(OUTPUT_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            data["_source_file"] = path.name
            results.append(data)
    return results


def _signal_from_dormant(customer: dict[str, Any], ref: str) -> dict[str, Any] | None:
    dormant = [s for s in customer.get("subscriptions", []) if s.get("dormant")]
    if not dormant:
        return None
    monthly = float(customer.get("dormant_monthly_total") or 0.0)
    names = ", ".join(s.get("name", "?") for s in dormant[:3])
    return {
        "id": f"sig_dormant_{customer.get('customer')}",
        "type": "slapend_abonnement",
        "title": "Slapende abonnementen kosten je geld",
        "subtitle": "Slapend geldverlies",
        "category": "slapend_geld",
        "signal_score": min(95, 55 + len(dormant) * 8),
        "impact": "hoog" if monthly >= 30 else "middel",
        "urgency": "hoog" if monthly >= 50 else "middel",
        "status": "nieuw",
        "detected_at": ref,
        "signal": {
            "headline": "Signaal: ongebruikte abonnementen",
            "summary": (
                f"Je hebt {len(dormant)} actieve abonnement(en) die al ≥ 90 dagen "
                f"niet gebruikt zijn ({names}). Dat kost ±€{monthly:.2f}/maand."
            ),
            "evidence": [
                {
                    "label": s.get("name", "?"),
                    "value": f"€{float(s.get('monthly_cost') or 0):.2f}/maand",
                    "trend": "up",
                }
                for s in dormant[:4]
            ],
        },
        "problem": {
            "headline": "Probleem: je betaalt voor diensten die je niet gebruikt",
            "description": (
                "Slapende abonnementen blijven doorlopen zolang je ze niet stopzet. "
                "Dat eet stilaan je budget op."
            ),
            "impact_label": f"±€{monthly:.2f} / maand verspild",
            "consequences": [
                "Maandelijkse kosten zonder voordeel",
                "Moeilijker sparen voor je doelen",
                "Overzicht op vaste lasten verdwijnt",
            ],
        },
        "solution": {
            "id": "sol_subscription_audit",
            "title": "Abonnementen-audit",
            "description": (
                "Bekijk je slapende abonnementen en zet overbodige in één klik stop."
            ),
            "cta": f"{len(dormant)} abonnement(en) bekijken",
            "action_type": "subscription_audit",
            "estimated_benefit": f"Tot €{monthly * 12:.0f} / jaar besparen",
            "steps": [
                "We tonen je slapende abonnementen",
                "Jij kiest welke je wil stopzetten",
                "Wij begeleiden de opzegging",
            ],
        },
    }


def _signal_from_home(profile: dict[str, Any], ref: str) -> dict[str, Any] | None:
    advice = profile.get("advice") or {}
    status = advice.get("status")
    if status in (None, "not_ready"):
        return None
    signals = profile.get("signals") or {}
    months = advice.get("months_to_save")
    summary = advice.get("summary") or "We hebben een spaaradvies voor jou."
    score = {
        "ready_to_buy": 92,
        "on_track": 84,
        "saving_for_goal": 78,
        "start_saving": 70,
    }.get(status, 65)
    return {
        "id": f"sig_home_{profile.get('customer')}",
        "type": "spaarplan_wonen",
        "title": "Gepersonaliseerd spaarplan beschikbaar",
        "subtitle": "Geen concreet spaarplan",
        "category": "sparen",
        "signal_score": score,
        "impact": "hoog" if status in ("ready_to_buy", "on_track") else "middel",
        "urgency": "middel",
        "status": "nieuw",
        "detected_at": ref,
        "signal": {
            "headline": "Signaal: spaargedrag en wooninteresse",
            "summary": summary,
            "evidence": [
                {
                    "label": "Maandelijks inkomen",
                    "value": f"€{float(signals.get('monthly_income') or 0):.0f}",
                    "trend": "flat",
                },
                {
                    "label": "Spaarcapaciteit",
                    "value": f"€{float(signals.get('savings_capacity') or 0):.0f}/maand",
                    "trend": "up",
                },
                {
                    "label": "Huidig spaargeld",
                    "value": f"€{float(advice.get('current_savings') or 0):.0f}",
                    "trend": "flat",
                },
                *(
                    [
                        {
                            "label": "Maanden tot doel",
                            "value": str(months),
                            "trend": "down",
                        }
                    ]
                    if months is not None
                    else []
                ),
            ],
        },
        "problem": {
            "headline": "Probleem: wel een doel, geen haalbare strategie",
            "description": (
                "Zonder concreet spaarplan is het moeilijk om te weten of je op schema "
                "zit voor een woning of ander spaardoel."
            ),
            "impact_label": advice.get("summary", "Spaarplan ontbreekt")[:80],
            "consequences": [
                "Je spaart mogelijk te weinig of te grillig",
                "Geen zicht op wanneer het doel haalbaar is",
                "Kansen op KBC-spaarproducten blijven liggen",
            ],
        },
        "solution": {
            "id": "sol_dynamic_savings",
            "title": "Dynamisch spaarplan",
            "description": (
                "Een traject op maat van je overschot, spaardoel en tijdshorizon."
            ),
            "cta": "Start mijn spaarplan",
            "action_type": "dynamic_savings_plan",
            "estimated_benefit": (
                f"Doel bereikt rond {advice['ready_date']}"
                if advice.get("ready_date")
                else "Duidelijk spaartraject"
            ),
            "steps": [
                "We berekenen je maandelijkse spaarruimte",
                "Je bevestigt het spaardoel",
                "We zetten een automatisch spaarplan klaar",
            ],
        },
    }


def list_signals_for_user(user_id: str | int) -> list[dict[str, Any]]:
    """GET /users/{id}/signals — signalen uit ``output/*.json`` voor één klant."""
    customer_id = _parse_user_id(user_id)
    conn = get_db()
    try:
        ref = reference_date(conn).isoformat()
        klanten = load_klanten(conn)
        if customer_id not in klanten:
            raise KeyError(f"Onbekende gebruiker: {user_id}")
    finally:
        conn.close()

    signals: list[dict[str, Any]] = []
    for payload in _load_signal_outputs():
        for customer in payload.get("customers") or []:
            if int(customer.get("customer", -1)) != customer_id:
                continue
            card = _signal_from_dormant(customer, ref)
            if card:
                signals.append(card)
        for profile in payload.get("profiles") or []:
            if int(profile.get("customer", -1)) != customer_id:
                continue
            card = _signal_from_home(profile, ref)
            if card:
                signals.append(card)

    signals.sort(key=lambda s: s.get("signal_score", 0), reverse=True)
    return signals


def perform_action(
    user_id: str | int,
    signal_id: str,
    action_type: str,
) -> dict[str, str]:
    """POST /users/{id}/signals/{sid}/act — demo-stub."""
    _ = list_signals_for_user(user_id)  # valideert dat de user bestaat
    return {
        "status": "opgelost",
        "message": f'Actie "{action_type}" uitgevoerd voor signaal {signal_id}.',
    }


def output_ready(output_dir: Path = OUTPUT_DIR) -> bool:
    return output_dir.exists() and any(output_dir.glob("*.json"))

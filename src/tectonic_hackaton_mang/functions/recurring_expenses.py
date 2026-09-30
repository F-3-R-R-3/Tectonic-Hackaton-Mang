"""Terugkerende uitgaven (abonnementen) uit de fake-dataset.

Leest de echte ``abonnementen``-tabel (zie ``database.py``): naam, bedrag,
frequentie, start_datum, laatste_gebruik, actief en categorie. Detecteert ook
**slapende** abonnementen: actief maar al een tijd niet gebruikt.

Output: per klant een overzicht met de abonnementen, klaar voor de website.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict

from ..dataset import klant_naam, load_abonnementen, load_klanten, reference_date

DORMANT_DAYS = 90


def _subscription(row: dict, reference) -> dict:
    amount = row["bedrag"]
    is_yearly = row["frequentie"] == "jaarlijks"
    monthly_cost = amount / 12 if is_yearly else amount
    last_used = row["laatste_gebruik"]
    days_since = (reference - last_used).days if last_used else None
    dormant = row["actief"] and (last_used is None or days_since >= DORMANT_DAYS)
    return {
        "name": row["naam"],
        "frequency": "yearly" if is_yearly else "monthly",
        "amount": round(amount, 2),
        "currency": "EUR",
        "category": row["categorie"],
        "active": row["actief"],
        "start_date": row["start_datum"].isoformat() if row["start_datum"] else None,
        "last_used": last_used.isoformat() if last_used else None,
        "days_since_last_use": days_since,
        "dormant": dormant,
        "monthly_cost": round(monthly_cost, 2),
        "yearly_cost": round(monthly_cost * 12, 2),
    }


def _customer_block(klant_id: int, klant: dict | None, rows: list[dict], reference) -> dict:
    subscriptions = sorted(
        (_subscription(row, reference) for row in rows),
        key=lambda s: s["yearly_cost"],
        reverse=True,
    )
    active = [s for s in subscriptions if s["active"]]
    dormant = [s for s in active if s["dormant"]]
    return {
        "customer": klant_id,
        "customer_name": klant_naam(klant),
        "monthly_total": round(sum(s["monthly_cost"] for s in active), 2),
        "yearly_total": round(sum(s["yearly_cost"] for s in active), 2),
        "monthly_count": sum(1 for s in active if s["frequency"] == "monthly"),
        "yearly_count": sum(1 for s in active if s["frequency"] == "yearly"),
        "dormant_count": len(dormant),
        "dormant_monthly_total": round(sum(s["monthly_cost"] for s in dormant), 2),
        "subscriptions": subscriptions,
    }


def find_recurring_expenses(conn: sqlite3.Connection) -> dict:
    """Lijst van terugkerende uitgaven per klant, incl. slapende abonnementen."""
    klanten = load_klanten(conn)
    rows = load_abonnementen(conn)
    if not rows:
        return {
            "title": "Terugkerende uitgaven",
            "message": "Geen abonnementen gevonden in de dataset.",
            "count": 0,
            "customers": [],
        }

    reference = reference_date(conn)
    grouped: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[int(row["klant_id"])].append(row)

    customers = [
        _customer_block(klant_id, klanten.get(klant_id), items, reference)
        for klant_id, items in sorted(grouped.items())
    ]

    total_monthly = round(sum(c["monthly_total"] for c in customers), 2)
    dormant_count = sum(c["dormant_count"] for c in customers)
    return {
        "title": "Terugkerende uitgaven",
        "message": (
            f"{sum(len(c['subscriptions']) for c in customers)} abonnementen bij "
            f"{len(customers)} klanten ({dormant_count} slapend)."
        ),
        "source_table": "abonnementen",
        "reference_date": reference.isoformat(),
        "count": sum(len(c["subscriptions"]) for c in customers),
        "customer_count": len(customers),
        "monthly_total": total_monthly,
        "yearly_total": round(total_monthly * 12, 2),
        "dormant_count": dormant_count,
        "customers": customers,
    }


FUNCTIONS = [find_recurring_expenses]

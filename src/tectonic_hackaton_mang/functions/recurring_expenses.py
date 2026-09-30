"""Detecteer terugkerende uitgaven (abonnementen) in de dataset.

Zowel **maandelijkse** als **jaarlijkse** terugkerende uitgaven worden herkend.
De functie is schema-onafhankelijk (zie ``tectonic_hackaton_mang.transactions``).

Output: een dict met een lijst ``subscriptions`` die de website kan inlezen.
Elk item heeft een ``frequency`` (``"monthly"`` of ``"yearly"``).
"""

from __future__ import annotations

import sqlite3

from ..transactions import expenses_are_negative, load_transactions, recurring_groups


def find_recurring_expenses(conn: sqlite3.Connection) -> dict:
    """Vind maandelijkse en jaarlijkse terugkerende uitgaven (abonnementen)."""
    loaded = load_transactions(conn)
    if loaded is None:
        return {
            "title": "Terugkerende uitgaven",
            "message": "Geen transactietabel gevonden in de dataset.",
            "count": 0,
            "monthly_count": 0,
            "yearly_count": 0,
            "subscriptions": [],
        }
    table, transactions = loaded
    if not transactions:
        return {
            "title": "Terugkerende uitgaven",
            "message": f"Geen bruikbare transacties gevonden in '{table}'.",
            "count": 0,
            "monthly_count": 0,
            "yearly_count": 0,
            "subscriptions": [],
        }

    negatives = expenses_are_negative(transactions)
    expenses = [t for t in transactions if (t.amount < 0) == negatives]
    subscriptions = recurring_groups(expenses)
    subscriptions.sort(key=lambda s: s["yearly_cost"], reverse=True)
    monthly_count = sum(1 for s in subscriptions if s["frequency"] == "monthly")
    yearly_count = sum(1 for s in subscriptions if s["frequency"] == "yearly")
    monthly_total = round(sum(s["monthly_cost"] for s in subscriptions), 2)
    return {
        "title": "Terugkerende uitgaven",
        "message": (
            f"{len(subscriptions)} terugkerende uitgaven gevonden "
            f"({monthly_count} maandelijks, {yearly_count} jaarlijks)."
        ),
        "source_table": table,
        "count": len(subscriptions),
        "monthly_count": monthly_count,
        "yearly_count": yearly_count,
        "monthly_total": monthly_total,
        "yearly_total": round(monthly_total * 12, 2),
        "subscriptions": subscriptions,
    }


FUNCTIONS = [find_recurring_expenses]

"""Analyseer of iemand best kan sparen of een huis kan kopen.

Signalen die we combineren:
  * vast inkomen (terugkerende inkomsten);
  * activiteit rond Immoweb / vastgoed;
  * overschrijvingen naar de spaarrekening;
  * positieve spaarcapaciteit (inkomen - uitgaven);
  * vaste kosten (terugkerende uitgaven).

Daaruit volgt een concreet advies: hoeveel de persoon moet sparen, welk bedrag
aan down payment + kosten nodig is, en welk bedrag aan lening haalbaar is.

De functie is schema-onafhankelijk (zie ``tectonic_hackaton_mang.transactions``).
Als er een klant-kolom bestaat, krijgt elke klant een apart profiel.
"""

from __future__ import annotations

import math
import sqlite3
from collections import defaultdict
from datetime import date

from ..transactions import (
    REAL_ESTATE_KEYWORDS,
    SAVINGS_KEYWORDS,
    Transaction,
    expenses_are_negative,
    load_transactions,
    matches_keywords,
    months_covered,
    recurring_groups,
)

# --- Aannames (pas aan naar gelang de use-case) -----------------------------
TARGET_HOME_PRICE = 300_000.0
DOWN_PAYMENT_PCT = 0.10
CLOSING_COSTS_PCT = 0.10
MAX_DEBT_RATIO = 0.40
ANNUAL_INTEREST_RATE = 0.035
LOAN_TERM_YEARS = 25
MIN_SAVINGS_TRANSFER_MONTHS = 3


def _annuity(monthly_payment: float, annual_rate: float, years: int) -> float:
    """Hoofdsom van een lening bij een vaste maandelijkse aflossing."""
    periods = years * 12
    if periods <= 0:
        return 0.0
    rate = annual_rate / 12
    if rate == 0:
        return monthly_payment * periods
    return monthly_payment * (1 - (1 + rate) ** -periods) / rate


def _add_months(day: date, months: int) -> date:
    month_index = day.month - 1 + months
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def _savings_transfers(transactions: list[Transaction]) -> dict:
    hits = [
        t
        for t in transactions
        if matches_keywords(t.name, SAVINGS_KEYWORDS)
        or matches_keywords(t.category, SAVINGS_KEYWORDS)
    ]
    total = round(sum(abs(t.amount) for t in hits), 2)
    covered = months_covered(transactions)
    return {
        "count": len(hits),
        "months": len({(t.date.year, t.date.month) for t in hits}),
        "total": total,
        "monthly_average": round(total / covered, 2),
        "frequent": len({(t.date.year, t.date.month) for t in hits}) >= MIN_SAVINGS_TRANSFER_MONTHS,
    }


def _real_estate_activity(transactions: list[Transaction]) -> dict:
    hits = [
        t
        for t in transactions
        if matches_keywords(t.name, REAL_ESTATE_KEYWORDS)
        or matches_keywords(t.category, REAL_ESTATE_KEYWORDS)
    ]
    return {
        "count": len(hits),
        "total": round(sum(abs(t.amount) for t in hits), 2),
        "active": len(hits) > 0,
    }


def _analyze_profile(customer: str | None, transactions: list[Transaction]) -> dict:
    negatives = expenses_are_negative(transactions)
    income = [t for t in transactions if (t.amount > 0) == negatives]
    expenses = [t for t in transactions if (t.amount < 0) == negatives]
    covered = months_covered(transactions)

    income_groups = recurring_groups(income)
    fixed_income = bool(income_groups)
    if income_groups:
        monthly_income = sum(g["monthly_cost"] for g in income_groups)
    else:
        monthly_income = sum(abs(t.amount) for t in income) / covered

    # Geld dat naar de spaarrekening gaat is geen kost maar sparen.
    spending = [
        t
        for t in expenses
        if not matches_keywords(t.name, SAVINGS_KEYWORDS)
        and not matches_keywords(t.category, SAVINGS_KEYWORDS)
    ]
    expense_groups = recurring_groups(spending)
    monthly_fixed_costs = sum(g["monthly_cost"] for g in expense_groups)
    monthly_expenses = sum(abs(t.amount) for t in spending) / covered

    savings = _savings_transfers(transactions)
    real_estate = _real_estate_activity(transactions)

    monthly_income = round(monthly_income, 2)
    monthly_expenses = round(monthly_expenses, 2)
    savings_capacity = round(monthly_income - monthly_expenses, 2)
    positive_capacity = savings_capacity > 0

    down_payment = round(TARGET_HOME_PRICE * DOWN_PAYMENT_PCT, 2)
    closing_costs = round(TARGET_HOME_PRICE * CLOSING_COSTS_PCT, 2)
    total_needed = round(down_payment + closing_costs, 2)

    max_monthly_payment = round(monthly_income * MAX_DEBT_RATIO, 2)
    max_loan = round(_annuity(max_monthly_payment, ANNUAL_INTEREST_RATE, LOAN_TERM_YEARS), 2)
    affordable_home_price = round(max_loan / (1 - DOWN_PAYMENT_PCT), 2)
    gap_to_target = round(TARGET_HOME_PRICE - affordable_home_price, 2)

    effective_saving = round(max(savings_capacity, savings["monthly_average"], 0.0), 2)
    if effective_saving > 0:
        months_to_save = math.ceil(total_needed / effective_saving)
        ready_date = _add_months(transactions[-1].date.date(), months_to_save).isoformat()
    else:
        months_to_save = None
        ready_date = None

    if not fixed_income or not positive_capacity:
        status = "not_ready"
        summary = (
            "Onvoldoende vast inkomen of negatieve spaarcapaciteit. "
            "Verlaag eerst de vaste kosten voor je aan een woning denkt."
        )
    elif affordable_home_price >= TARGET_HOME_PRICE:
        status = "ready_to_buy"
        summary = (
            f"Vast inkomen, positieve spaarcapaciteit en een haalbare lening: "
            f"je kan een woning tot ±€{affordable_home_price:,.0f} kopen."
        )
    elif real_estate["active"]:
        status = "on_track"
        summary = (
            f"Je bent actief op vastgoed en spaart structureel. "
            f"Met ±€{effective_saving:,.0f}/maand spaar je in {months_to_save} maanden "
            f"het benodigde startkapitaal bij elkaar."
        )
    else:
        status = "start_saving"
        summary = (
            f"Je kan ±€{effective_saving:,.0f}/maand opzijzetten. "
            f"Begin met sparen voor de down payment van €{down_payment:,.0f}."
        )

    return {
        "customer": customer if customer is not None else "alle klanten",
        "signals": {
            "fixed_income": fixed_income,
            "monthly_income": monthly_income,
            "income_sources": [
                {"name": g["name"], "frequency": g["frequency"], "monthly_cost": g["monthly_cost"]}
                for g in income_groups
            ],
            "monthly_expenses": monthly_expenses,
            "monthly_fixed_costs": round(monthly_fixed_costs, 2),
            "savings_transfers": savings,
            "real_estate_activity": real_estate,
            "savings_capacity": savings_capacity,
            "positive_savings_capacity": positive_capacity,
        },
        "advice": {
            "status": status,
            "summary": summary,
            "target_home_price": TARGET_HOME_PRICE,
            "down_payment_required": down_payment,
            "closing_costs": closing_costs,
            "total_needed": total_needed,
            "max_monthly_payment": max_monthly_payment,
            "max_loan": max_loan,
            "affordable_home_price": affordable_home_price,
            "gap_to_target": gap_to_target,
            "effective_monthly_saving": effective_saving,
            "months_to_save": months_to_save,
            "ready_date": ready_date,
        },
    }


def analyze_home_purchase(conn: sqlite3.Connection) -> dict:
    """Analyseer spaarcapaciteit en haalbaarheid van een woningaankoop."""
    loaded = load_transactions(conn)
    if loaded is None:
        return {
            "title": "Spaar- en woonanalyse",
            "message": "Geen transactietabel gevonden in de dataset.",
            "count": 0,
            "profiles": [],
        }
    table, transactions = loaded
    if not transactions:
        return {
            "title": "Spaar- en woonanalyse",
            "message": f"Geen bruikbare transacties gevonden in '{table}'.",
            "count": 0,
            "profiles": [],
        }

    grouped: dict[str | None, list[Transaction]] = defaultdict(list)
    for entry in transactions:
        grouped[entry.customer].append(entry)

    profiles = [
        _analyze_profile(customer, entries)
        for customer, entries in sorted(grouped.items(), key=lambda kv: str(kv[0]))
    ]
    return {
        "title": "Spaar- en woonanalyse",
        "message": f"{len(profiles)} profiel(en) geanalyseerd.",
        "source_table": table,
        "assumptions": {
            "target_home_price": TARGET_HOME_PRICE,
            "down_payment_pct": DOWN_PAYMENT_PCT,
            "closing_costs_pct": CLOSING_COSTS_PCT,
            "max_debt_ratio": MAX_DEBT_RATIO,
            "annual_interest_rate": ANNUAL_INTEREST_RATE,
            "loan_term_years": LOAN_TERM_YEARS,
        },
        "count": len(profiles),
        "profiles": profiles,
    }


FUNCTIONS = [analyze_home_purchase]

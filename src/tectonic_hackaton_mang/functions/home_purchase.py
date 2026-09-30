"""Analyseer of iemand best kan sparen of een huis kan kopen.

Gebruikt de echte fake-dataset (zie ``database.py``):
  * ``klanten`` — inkomen, spaardoel, gezinssituatie;
  * ``transacties`` — maandelijkse uitgaven en terugkerend inkomen;
  * ``abonnementen`` + ``verzekeringen`` — vaste kosten;
  * ``spaarrekening_interacties`` — stortingen, opnames, saldo en 'bekeken';
  * ``zoekopdrachten`` — interesse in wonen/sparen (bv. via Immoweb of Kate).

Daaruit volgt een concreet advies: of de persoon best begint te sparen, of een
huis kan kopen, hoeveel die moet sparen en welke lening haalbaar is. Elke klant
krijgt een eigen profiel.
"""

from __future__ import annotations

import math
import sqlite3
from collections import defaultdict
from datetime import date

from ..dataset import (
    klant_naam,
    load_abonnementen,
    load_klanten,
    load_spaar_interacties,
    load_verzekeringen,
    load_zoekopdrachten,
    reference_date,
)
from ..transactions import (
    Transaction,
    load_transactions,
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

HOUSING_KEYWORDS = (
    "woning",
    "woon",
    "immoweb",
    "immo",
    "hypotheek",
    "lening",
    "kopen",
    "renovatie",
    "verbouw",
)
SAVING_KEYWORDS = (
    "spaar",
    "sparen",
    "rente",
    "spaardoel",
    "beleggen",
    "pensioen",
    "buffer",
)
HOUSE_GOALS = {"huis", "woning", "woonsparen", "renovatie", "verbouwing", "verbouw"}


def _annuity(monthly_payment: float, annual_rate: float, years: int) -> float:
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


def _matches(text: object, keywords: tuple[str, ...]) -> bool:
    lowered = str(text).lower()
    return any(keyword in lowered for keyword in keywords)


def _savings_activity(rows: list[dict], covered: int) -> dict:
    deposits = [r for r in rows if r["type"] == "storting" and r["bedrag"]]
    total = round(sum(abs(r["bedrag"]) for r in deposits), 2)
    months = len({(r["datum"].year, r["datum"].month) for r in deposits if r["datum"]})
    balances = [r["saldo_na"] for r in rows if r["saldo_na"] is not None]
    latest = max(
        (r for r in rows if r["saldo_na"] is not None),
        key=lambda r: r["datum"] or date.min,
        default=None,
    )
    return {
        "deposit_count": len(deposits),
        "deposit_months": months,
        "deposit_total": total,
        "monthly_average": round(total / covered, 2),
        "frequent": months >= MIN_SAVINGS_TRANSFER_MONTHS,
        "views": sum(1 for r in rows if r["type"] == "bekeken"),
        "current_balance": round(latest["saldo_na"], 2) if latest else None,
        "max_balance": round(max(balances), 2) if balances else None,
    }


def _analyze_profile(
    klant_id: int,
    klant: dict,
    transactions: list[Transaction],
    abos: list[dict],
    verzekeringen: list[dict],
    spaar: list[dict],
    zoek: list[dict],
    reference: date,
) -> dict:
    covered = months_covered(transactions) if transactions else 1

    income = [t for t in transactions if t.amount > 0]
    expenses = [t for t in transactions if t.amount < 0]
    income_groups = recurring_groups(income)
    monthly_income = klant.get("inkomen_maand") or 0.0
    if not monthly_income and income_groups:
        monthly_income = sum(g["monthly_cost"] for g in income_groups)
    fixed_income = monthly_income > 0
    monthly_expenses = round(sum(abs(t.amount) for t in expenses) / covered, 2)

    abo_monthly = round(
        sum(
            (a["bedrag"] / 12 if a["frequentie"] == "jaarlijks" else a["bedrag"])
            for a in abos
            if a["actief"]
        ),
        2,
    )
    insurance_monthly = round(sum(v["maandpremie"] for v in verzekeringen if v["actief"]), 2)
    monthly_fixed_costs = round(abo_monthly + insurance_monthly, 2)

    savings = _savings_activity(spaar, covered)
    current_savings = savings["current_balance"] or 0.0

    housing_queries = [z["query"] for z in zoek if _matches(z["query"], HOUSING_KEYWORDS)]
    saving_queries = [z["query"] for z in zoek if _matches(z["query"], SAVING_KEYWORDS)]
    goal = klant.get("spaardoel")
    personal_goal = klant.get("spaardoel_bedrag")
    wants_house = bool(goal and str(goal).lower() in HOUSE_GOALS) or bool(housing_queries)

    savings_capacity = round(monthly_income - monthly_expenses, 2)
    positive_capacity = savings_capacity > 0
    effective_saving = round(max(savings_capacity, savings["monthly_average"], 0.0), 2)

    down_payment = round(TARGET_HOME_PRICE * DOWN_PAYMENT_PCT, 2)
    closing_costs = round(TARGET_HOME_PRICE * CLOSING_COSTS_PCT, 2)
    start_capital = round(down_payment + closing_costs, 2)
    savings_target = round(personal_goal, 2) if personal_goal else start_capital

    max_monthly_payment = round(monthly_income * MAX_DEBT_RATIO, 2)
    max_loan = round(_annuity(max_monthly_payment, ANNUAL_INTEREST_RATE, LOAN_TERM_YEARS), 2)
    affordable_home_price = round(max_loan / (1 - DOWN_PAYMENT_PCT), 2)
    gap_to_target = round(TARGET_HOME_PRICE - affordable_home_price, 2)

    remaining = max(savings_target - current_savings, 0.0)
    if effective_saving > 0 and remaining > 0:
        months_to_save = math.ceil(remaining / effective_saving)
        ready_date = _add_months(reference, months_to_save).isoformat()
    elif remaining <= 0:
        months_to_save = 0
        ready_date = reference.isoformat()
    else:
        months_to_save = None
        ready_date = None

    if not fixed_income or not positive_capacity:
        status = "not_ready"
        summary = (
            "Onvoldoende vast inkomen of negatieve spaarcapaciteit. "
            "Verlaag eerst de vaste kosten voor je aan een woning denkt."
        )
    elif affordable_home_price >= TARGET_HOME_PRICE and current_savings >= down_payment:
        status = "ready_to_buy"
        summary = (
            f"Vast inkomen, positieve spaarcapaciteit en voldoende spaargeld: "
            f"je kan een woning tot ±€{affordable_home_price:,.0f} kopen."
        )
    elif wants_house:
        status = "on_track"
        summary = (
            f"Je wil een woning en spaart ±€{effective_saving:,.0f}/maand. "
            f"Met je huidige spaargeld (±€{current_savings:,.0f}) is het doel van "
            f"€{savings_target:,.0f} bereikt in {months_to_save} maanden."
        )
    elif personal_goal:
        status = "saving_for_goal"
        if months_to_save == 0:
            summary = (
                f"Je doel '{goal}' van €{savings_target:,.0f} is al bereikt "
                f"(spaargeld ±€{current_savings:,.0f})."
            )
        else:
            summary = (
                f"Je spaart ±€{effective_saving:,.0f}/maand. Je doel '{goal}' van "
                f"€{savings_target:,.0f} is bereikt in {months_to_save} maanden."
            )
    else:
        status = "start_saving"
        summary = (
            f"Je kan ±€{effective_saving:,.0f}/maand opzijzetten. "
            f"Begin met sparen voor de down payment van €{down_payment:,.0f}."
        )

    return {
        "customer": klant_id,
        "customer_name": klant_naam(klant),
        "signals": {
            "fixed_income": fixed_income,
            "monthly_income": round(monthly_income, 2),
            "income_sources": [
                {"name": g["name"], "frequency": g["frequency"], "monthly_cost": g["monthly_cost"]}
                for g in income_groups
            ],
            "monthly_expenses": monthly_expenses,
            "monthly_fixed_costs": monthly_fixed_costs,
            "subscriptions_monthly": abo_monthly,
            "insurance_monthly": insurance_monthly,
            "savings_activity": savings,
            "savings_capacity": savings_capacity,
            "positive_savings_capacity": positive_capacity,
            "wants_house": wants_house,
            "savings_goal": goal,
            "personal_goal_amount": round(personal_goal, 2) if personal_goal else None,
            "housing_queries": housing_queries,
            "saving_queries": saving_queries,
        },
        "advice": {
            "status": status,
            "summary": summary,
            "target_home_price": TARGET_HOME_PRICE,
            "down_payment_required": down_payment,
            "closing_costs": closing_costs,
            "start_capital_needed": start_capital,
            "savings_target": savings_target,
            "current_savings": round(current_savings, 2),
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
    """Analyseer spaarcapaciteit en haalbaarheid van een woningaankoop per klant."""
    klanten = load_klanten(conn)
    if not klanten:
        return {
            "title": "Spaar- en woonanalyse",
            "message": "Geen klanten gevonden in de dataset.",
            "count": 0,
            "profiles": [],
        }

    loaded = load_transactions(conn)
    tx_by_klant: dict[int, list[Transaction]] = defaultdict(list)
    if loaded is not None:
        for t in loaded[1]:
            if t.customer is not None:
                tx_by_klant[int(t.customer)].append(t)

    abos: dict[int, list[dict]] = defaultdict(list)
    for a in load_abonnementen(conn):
        abos[int(a["klant_id"])].append(a)
    verzekeringen: dict[int, list[dict]] = defaultdict(list)
    for v in load_verzekeringen(conn):
        verzekeringen[int(v["klant_id"])].append(v)
    spaar: dict[int, list[dict]] = defaultdict(list)
    for s in load_spaar_interacties(conn):
        spaar[int(s["klant_id"])].append(s)
    zoek: dict[int, list[dict]] = defaultdict(list)
    for z in load_zoekopdrachten(conn):
        zoek[int(z["klant_id"])].append(z)

    reference = reference_date(conn)
    profiles = [
        _analyze_profile(
            klant_id,
            klant,
            tx_by_klant.get(klant_id, []),
            abos.get(klant_id, []),
            verzekeringen.get(klant_id, []),
            spaar.get(klant_id, []),
            zoek.get(klant_id, []),
            reference,
        )
        for klant_id, klant in sorted(klanten.items())
    ]

    return {
        "title": "Spaar- en woonanalyse",
        "message": f"{len(profiles)} profiel(en) geanalyseerd.",
        "source_table": "klanten + transacties + abonnementen + spaarrekening_interacties",
        "reference_date": reference.isoformat(),
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

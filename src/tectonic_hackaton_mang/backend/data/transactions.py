"""Gedeelde helpers om de fake-dataset te lezen.

Deze module is schema-onafhankelijk: ze zoekt zelf de transactietabel en de
relevante kolommen (datum, bedrag, naam, optioneel categorie en klant), met
zowel NL- als EN-kolomnamen. Alle functies in ``functions/`` bouwen hierop
verder, zodat we de detectie-logica maar op één plek onderhouden.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from statistics import median, pstdev

TABLE_HINTS = (
    "transacti",
    "transaction",
    "betaling",
    "payment",
    "uitgave",
    "expense",
    "verrichting",
    "rekening",
)

COLUMN_HINTS = {
    "date": ("datum", "date", "tijd", "time", "timestamp", "boekdatum", "verwerkingsdatum"),
    "amount": ("bedrag", "amount", "value", "waarde", "prijs", "price", "som"),
    "name": (
        "tegenpartij",
        "naam",
        "name",
        "merchant",
        "handelaar",
        "omschrijving",
        "beschrijving",
        "description",
        "detail",
        "mededeling",
        "counterparty",
    ),
    "category": ("categorie", "category", "type", "subcategorie", "rubriek"),
    "customer": ("klant", "customer", "gebruiker", "user", "persoon", "client", "rekeninghouder"),
}

DATE_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d.%m.%Y",
    "%Y%m%d",
)

# interval in dagen, minimum aantal betalingen en minimum aantal periodes
FREQUENCY_RULES = {
    "monthly": {"low": 25, "high": 35, "min_occurrences": 3, "min_periods": 3},
    "yearly": {"low": 330, "high": 400, "min_occurrences": 2, "min_periods": 2},
}

SAVINGS_KEYWORDS = ("spaar", "savings", "épargne", "epargne", "spaarrekening")
REAL_ESTATE_KEYWORDS = ("immoweb", "immo", "vastgoed", "immobilien", "real estate")


@dataclass
class Transaction:
    date: datetime
    amount: float
    name: str
    category: str | None
    customer: str | None


def columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
    return [row["name"] for row in rows]


def pick(cols: list[str], hints: tuple[str, ...]) -> str | None:
    lowered = {c.lower(): c for c in cols}
    for hint in hints:
        for low, original in lowered.items():
            if hint == low:
                return original
    for hint in hints:
        for low, original in lowered.items():
            if hint in low:
                return original
    return None


def find_transaction_table(conn: sqlite3.Connection) -> tuple[str, dict] | None:
    """Kies de meest waarschijnlijke transactietabel + kolom-mapping."""
    tables = [
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        )
    ]
    best: tuple[int, str, dict] | None = None
    for table in tables:
        cols = columns(conn, table)
        mapping = {key: pick(cols, hints) for key, hints in COLUMN_HINTS.items()}
        if not mapping["date"] or not mapping["amount"]:
            continue
        score = 0
        if any(hint in table.lower() for hint in TABLE_HINTS):
            score += 2
        score += 2  # heeft datum + bedrag
        if mapping["name"]:
            score += 1
        if mapping["category"]:
            score += 1
        if mapping["customer"]:
            score += 1
        if best is None or score > best[0]:
            best = (score, table, mapping)
    if best is None:
        return None
    return best[1], best[2]


def parse_date(value: object) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        ts = value / 1000 if value > 1e11 else value
        try:
            return datetime.fromtimestamp(ts, tz=UTC).replace(tzinfo=None)
        except (OverflowError, OSError, ValueError):
            return None
    text = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)  # noqa: DTZ007
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text).replace(tzinfo=None)
    except ValueError:
        return None


def parse_amount(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = re.sub(r"[^\d,.\-]", "", str(value))
    if text.count(",") == 1 and text.count(".") == 0:
        text = text.replace(",", ".")
    else:
        text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def normalize_name(name: object) -> str:
    text = str(name).lower().strip()
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"[^a-z0-9.\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def clean_display_name(name: object) -> str:
    text = re.sub(r"\s+", " ", str(name)).strip()
    text = re.sub(r"\s*\d{3,}.*$", "", text).strip()
    return text or str(name).strip()


def matches_keywords(text: object, keywords: tuple[str, ...]) -> bool:
    lowered = str(text).lower()
    return any(keyword in lowered for keyword in keywords)


def detect_frequency(dates: list[datetime]) -> tuple[str | None, float, float]:
    """Geef (frequentie, mediaan interval in dagen, confidence).

    Frequentie is ``"monthly"`` of ``"yearly"`` (of ``None`` als het geen
    terugkerend patroon is).
    """
    if len(dates) < 2:
        return None, 0.0, 0.0
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    intervals = [i for i in intervals if i > 0]
    if not intervals:
        return None, 0.0, 0.0
    mid = median(intervals)
    for frequency, rule in FREQUENCY_RULES.items():
        if not rule["low"] <= mid <= rule["high"]:
            continue
        if len(dates) < rule["min_occurrences"]:
            continue
        if frequency == "monthly":
            periods = {(d.year, d.month) for d in dates}
        else:
            periods = {d.year for d in dates}
        if len(periods) < rule["min_periods"]:
            continue
        spread = pstdev(intervals) if len(intervals) > 1 else 0.0
        interval_conf = max(0.0, 1.0 - (spread / mid) / 0.15)
        period_conf = min(1.0, len(periods) / (rule["min_periods"] * 2))
        return frequency, mid, round(min(interval_conf, period_conf), 2)
    return None, mid, 0.0


def load_transactions(conn: sqlite3.Connection) -> tuple[str, list[Transaction]] | None:
    """Lees alle bruikbare transacties uit de dataset.

    Geeft ``(tabelnaam, transacties)`` terug, of ``None`` als er geen
    transactietabel gevonden is.
    """
    found = find_transaction_table(conn)
    if found is None:
        return None
    table, mapping = found
    if not re.match(r'^[a-zA-Z0-9_]+$', str(table)):
        raise ValueError("Invalid input")
    result: list[Transaction] = []
    for row in conn.execute(f'SELECT * FROM "{table}"').fetchall():
        date = parse_date(row[mapping["date"]])
        amount = parse_amount(row[mapping["amount"]])
        if date is None or amount is None or amount == 0:
            continue
        name = clean_display_name(row[mapping["name"]]) if mapping["name"] else ""
        category = row[mapping["category"]] if mapping["category"] else None
        customer = row[mapping["customer"]] if mapping["customer"] else None
        result.append(Transaction(date, amount, name, category, customer))
    return table, result


def expenses_are_negative(transactions: list[Transaction]) -> bool:
    """Bepaal of uitgaven als negatieve bedragen in de data staan."""
    return sum(1 for t in transactions if t.amount < 0) >= len(transactions) / 2


def months_covered(transactions: list[Transaction]) -> int:
    """Aantal verschillende maanden dat de data beslaat (minimaal 1)."""
    periods = {(t.date.year, t.date.month) for t in transactions}
    return max(1, len(periods))


def recurring_groups(transactions: list[Transaction]) -> list[dict]:
    """Groepeer transacties per tegenpartij en hou de terugkerende over.

    Geeft per terugkerende tegenpartij een dict met o.a. ``frequency``,
    ``average_amount``, ``monthly_cost`` en ``yearly_cost``.
    """
    groups: dict[str, list[Transaction]] = {}
    for entry in transactions:
        key = normalize_name(entry.name)
        if key:
            groups.setdefault(key, []).append(entry)

    results: list[dict] = []
    for entries in groups.values():
        entries.sort(key=lambda e: e.date)
        dates = [e.date for e in entries]
        frequency, interval, confidence = detect_frequency(dates)
        if frequency is None:
            continue
        amounts = [abs(e.amount) for e in entries]
        average = sum(amounts) / len(amounts)
        if average <= 0:
            continue
        if frequency == "yearly":
            monthly_cost, yearly_cost = average / 12, average
        else:
            monthly_cost, yearly_cost = average, average * 12
        names = [e.name for e in entries]
        categories = [e.category for e in entries if e.category]
        last_seen = dates[-1]
        results.append(
            {
                "name": max(set(names), key=names.count),
                "frequency": frequency,
                "average_amount": round(average, 2),
                "currency": "EUR",
                "category": max(set(categories), key=categories.count) if categories else None,
                "occurrences": len(entries),
                "months_active": len({(d.year, d.month) for d in dates}),
                "interval_days": round(interval, 1),
                "first_seen": dates[0].date().isoformat(),
                "last_seen": last_seen.date().isoformat(),
                "next_expected": (last_seen + timedelta(days=round(interval))).date().isoformat(),
                "monthly_cost": round(monthly_cost, 2),
                "yearly_cost": round(yearly_cost, 2),
                "confidence": confidence,
            }
        )
    return results

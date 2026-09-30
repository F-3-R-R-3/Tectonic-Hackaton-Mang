"""Typed readers voor de echte fake-dataset (zie ``database.py``).

Deze module kent het schema van ``data/fake.db`` en geeft de rijen als gewone
dicts terug (datums als ``date``, bedragen als ``float``), zodat de functies in
``functions/`` geen SQL-kolomnamen meer hoeven te raden.

Tabellen: ``klanten``, ``transacties``, ``abonnementen``, ``zoekopdrachten``,
``spaarrekening_interacties`` en ``verzekeringen``.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, date, datetime

from .transactions import parse_amount, parse_date


def _to_date(value: object) -> date | None:
    parsed = parse_date(value)
    return parsed.date() if parsed else None


def _to_amount(value: object) -> float | None:
    return parse_amount(value)


def _rows(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def load_klanten(conn: sqlite3.Connection) -> dict[int, dict]:
    """Alle klanten, keyed op ``id``."""
    klanten: dict[int, dict] = {}
    for row in conn.execute("SELECT * FROM klanten ORDER BY id"):
        data = dict(row)
        klanten[int(data["id"])] = data
    return klanten


def klant_naam(klant: dict | None) -> str:
    if not klant:
        return "onbekend"
    return f"{klant.get('voornaam', '')} {klant.get('achternaam', '')}".strip()


def load_abonnementen(conn: sqlite3.Connection) -> list[dict]:
    rows = _rows(conn, "SELECT * FROM abonnementen ORDER BY klant_id, naam")
    for row in rows:
        row["start_datum"] = _to_date(row.get("start_datum"))
        row["laatste_gebruik"] = _to_date(row.get("laatste_gebruik"))
        row["bedrag"] = _to_amount(row.get("bedrag")) or 0.0
        row["actief"] = bool(row.get("actief"))
    return rows


def load_spaar_interacties(conn: sqlite3.Connection) -> list[dict]:
    rows = _rows(conn, "SELECT * FROM spaarrekening_interacties ORDER BY klant_id, datum")
    for row in rows:
        row["datum"] = _to_date(row.get("datum"))
        row["bedrag"] = _to_amount(row.get("bedrag"))
        row["saldo_na"] = _to_amount(row.get("saldo_na"))
    return rows


def load_zoekopdrachten(conn: sqlite3.Connection) -> list[dict]:
    rows = _rows(conn, "SELECT * FROM zoekopdrachten ORDER BY klant_id, datum")
    for row in rows:
        row["datum"] = _to_date(row.get("datum"))
    return rows


def load_verzekeringen(conn: sqlite3.Connection) -> list[dict]:
    rows = _rows(conn, "SELECT * FROM verzekeringen ORDER BY klant_id, type")
    for row in rows:
        row["maandpremie"] = _to_amount(row.get("maandpremie")) or 0.0
        row["actief"] = bool(row.get("actief"))
    return rows


def reference_date(conn: sqlite3.Connection) -> date:
    """De 'vandaag' van de dataset = laatste datum die erin voorkomt."""
    latest: date | None = None
    for table, column in (
        ("transacties", "datum"),
        ("spaarrekening_interacties", "datum"),
        ("zoekopdrachten", "datum"),
    ):
        value = conn.execute(f"SELECT MAX({column}) FROM {table}").fetchone()[0]
        parsed = _to_date(value)
        if parsed and (latest is None or parsed > latest):
            latest = parsed
    return latest or datetime.now(tz=UTC).date()

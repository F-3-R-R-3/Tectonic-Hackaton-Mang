from __future__ import annotations

import sqlite3

from ..config import DB_PATH


def get_db() -> sqlite3.Connection:
    """Open de gedeelde fake-dataset en geef een connectie terug.

    Rijen zijn te lezen via de kolomnaam, bv. ``row["bedrag"]``.
    Overschrijf het pad indien nodig met de env-variabele ``KBC_DB``.
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database niet gevonden op '{DB_PATH}'. "
            "Zet de fake dataset in de data/ map of stel KBC_DB in."
        )
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

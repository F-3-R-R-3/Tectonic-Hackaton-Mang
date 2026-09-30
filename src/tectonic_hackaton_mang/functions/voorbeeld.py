"""Sjabloon voor een eigen functie-bestand.

Kopieer dit bestand naar ``<jouw_naam>.py`` en bouw er je eigen functies in.
Regels:
  * elke functie krijgt de db-connectie binnen als eerste argument;
  * elke functie geeft een JSON-serialiseerbare dict terug;
  * zet je functies in de lijst ``FUNCTIONS`` onderaan.
"""

from __future__ import annotations

import sqlite3


def dataset_overzicht(conn: sqlite3.Connection) -> dict:
    """Voorbeeld: toont de tabellen die in de dataset zitten."""
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall()
    return {
        "title": "Dataset overzicht",
        "message": f"{len(rows)} tabellen gevonden.",
        "tables": [row["name"] for row in rows],
    }


FUNCTIONS = [dataset_overzicht]

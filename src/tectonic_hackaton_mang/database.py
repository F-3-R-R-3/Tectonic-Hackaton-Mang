"""Genereer de gedeelde fake KBC-dataset als SQLite (`data/fake.db`).

Reproduceerbaar via vaste seed. Bevat alle demo-persona's in één database
met scripted verhaallijnen (signaal ➜ probleem ➜ oplossing).

Gebruik:
    uv run python -m tectonic_hackaton_mang.database
"""

from __future__ import annotations

import random
import sqlite3
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "fake.db"
SEED = 2026
TODAY = date(2026, 9, 30)

# Extra klanten bovenop de 5 demo-persona's — genoeg volume voor een overtuigende demo.
N_FILLER_KLANTEN = 45
MAANDEN_HISTORIE = 12


SCHEMA = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS zoekopdrachten;
DROP TABLE IF EXISTS spaarrekening_interacties;
DROP TABLE IF EXISTS verzekeringen;
DROP TABLE IF EXISTS abonnementen;
DROP TABLE IF EXISTS transacties;
DROP TABLE IF EXISTS klanten;

CREATE TABLE klanten (
    id              INTEGER PRIMARY KEY,
    voornaam        TEXT    NOT NULL,
    achternaam      TEXT    NOT NULL,
    leeftijd        INTEGER NOT NULL,
    gezinssituatie  TEXT    NOT NULL,  -- alleenstaand | koppel | gezin | student | gepensioneerd
    woonplaats      TEXT    NOT NULL,
    postcode        TEXT    NOT NULL,
    inkomen_maand   REAL    NOT NULL,  -- netto referentie-inkomen
    heeft_auto      INTEGER NOT NULL DEFAULT 0,
    aantal_kinderen INTEGER NOT NULL DEFAULT 0,
    verhuisd_recent INTEGER NOT NULL DEFAULT 0,  -- 1 = verhuisd in laatste 3 maanden
    spaardoel       TEXT,                      -- bv. huis, vakantie, auto, pensioen
    spaardoel_bedrag REAL,
    is_demo         INTEGER NOT NULL DEFAULT 0  -- 1 = scripted verhaallijn voor de demo
);

CREATE TABLE transacties (
    id              INTEGER PRIMARY KEY,
    klant_id        INTEGER NOT NULL REFERENCES klanten(id),
    datum           TEXT    NOT NULL,  -- ISO YYYY-MM-DD
    bedrag          REAL    NOT NULL,  -- positief = inkomen, negatief = uitgave
    categorie       TEXT    NOT NULL,
    omschrijving    TEXT    NOT NULL,
    tegenpartij     TEXT
);

CREATE TABLE abonnementen (
    id              INTEGER PRIMARY KEY,
    klant_id        INTEGER NOT NULL REFERENCES klanten(id),
    naam            TEXT    NOT NULL,
    bedrag          REAL    NOT NULL,
    frequentie      TEXT    NOT NULL,  -- maandelijks | jaarlijks
    start_datum     TEXT    NOT NULL,
    laatste_gebruik TEXT,              -- NULL = nooit gebruikt sinds start
    actief          INTEGER NOT NULL DEFAULT 1,
    categorie       TEXT    NOT NULL   -- streaming | sport | software | mobiliteit | overig
);

CREATE TABLE zoekopdrachten (
    id              INTEGER PRIMARY KEY,
    klant_id        INTEGER NOT NULL REFERENCES klanten(id),
    query           TEXT    NOT NULL,
    datum           TEXT    NOT NULL,
    kanaal          TEXT    NOT NULL DEFAULT 'app'  -- app | web | kate
);

CREATE TABLE spaarrekening_interacties (
    id              INTEGER PRIMARY KEY,
    klant_id        INTEGER NOT NULL REFERENCES klanten(id),
    datum           TEXT    NOT NULL,
    type            TEXT    NOT NULL,  -- storting | opname | bekeken | doel_aangemaakt
    bedrag          REAL,              -- NULL bij 'bekeken'
    saldo_na        REAL,
    notitie         TEXT
);

CREATE TABLE verzekeringen (
    id              INTEGER PRIMARY KEY,
    klant_id        INTEGER NOT NULL REFERENCES klanten(id),
    type            TEXT    NOT NULL,  -- brand | auto | familiale | hospitalisatie
    polisnummer     TEXT    NOT NULL,
    polisadres      TEXT    NOT NULL,
    maandpremie     REAL    NOT NULL,
    actief          INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_trans_klant ON transacties(klant_id);
CREATE INDEX idx_trans_datum ON transacties(datum);
CREATE INDEX idx_trans_cat   ON transacties(categorie);
CREATE INDEX idx_abo_klant   ON abonnementen(klant_id);
CREATE INDEX idx_zoek_klant  ON zoekopdrachten(klant_id);
CREATE INDEX idx_spaar_klant ON spaarrekening_interacties(klant_id);
CREATE INDEX idx_verz_klant  ON verzekeringen(klant_id);
"""


@dataclass(frozen=True)
class DemoPersona:
    """Scripted verhaallijn — ids 1..5 zijn gereserveerd voor de demo."""

    id: int
    voornaam: str
    achternaam: str
    leeftijd: int
    gezinssituatie: str
    woonplaats: str
    postcode: str
    inkomen_maand: float
    heeft_auto: bool
    aantal_kinderen: int
    verhuisd_recent: bool
    spaardoel: str | None
    spaardoel_bedrag: float | None
    tag: str  # enkel voor logging / docs, niet in DB


DEMO_PERSONAS: list[DemoPersona] = [
    DemoPersona(
        id=1,
        voornaam="Emma",
        achternaam="Peeters",
        leeftijd=21,
        gezinssituatie="student",
        woonplaats="Leuven",
        postcode="3000",
        inkomen_maand=950.0,  # kot + jobstudent
        heeft_auto=False,
        aantal_kinderen=0,
        verhuisd_recent=False,
        spaardoel=None,
        spaardoel_bedrag=None,
        tag="student",  # slapende abo's + studentenkorting
    ),
    DemoPersona(
        id=2,
        voornaam="Thomas",
        achternaam="Vermeulen",
        leeftijd=26,
        gezinssituatie="alleenstaand",
        woonplaats="Antwerpen",
        postcode="2000",
        inkomen_maand=2650.0,  # eerste vaste job
        heeft_auto=False,
        aantal_kinderen=0,
        verhuisd_recent=False,
        spaardoel="huis",
        spaardoel_bedrag=25000.0,
        tag="jonge_starter",  # spaardoel zonder strategie
    ),
    DemoPersona(
        id=3,
        voornaam="Sofie",
        achternaam="Janssen",
        leeftijd=38,
        gezinssituatie="gezin",
        woonplaats="Gent",
        postcode="9000",
        inkomen_maand=4200.0,  # gezinsinkomen (gezamenlijk zicht)
        heeft_auto=True,
        aantal_kinderen=2,
        verhuisd_recent=True,  # verhuis → polisadres verouderd
        spaardoel="vakantie",
        spaardoel_bedrag=4000.0,
        tag="gezin",  # auto-kosten + Auto-Address Sync
    ),
    DemoPersona(
        id=4,
        voornaam="Lars",
        achternaam="Declercq",
        leeftijd=34,
        gezinssituatie="alleenstaand",
        woonplaats="Brussel",
        postcode="1000",
        inkomen_maand=3800.0,
        heeft_auto=True,
        aantal_kinderen=0,
        verhuisd_recent=False,
        spaardoel=None,
        spaardoel_bedrag=None,
        tag="alleenstaande_professional",  # slapend geld, hoge vaste lasten
    ),
    DemoPersona(
        id=5,
        voornaam="Marie",
        achternaam="Claeys",
        leeftijd=68,
        gezinssituatie="gepensioneerd",
        woonplaats="Brugge",
        postcode="8000",
        inkomen_maand=1850.0,  # pensioen
        heeft_auto=False,
        aantal_kinderen=0,
        verhuisd_recent=False,
        spaardoel="pensioen_buffer",
        spaardoel_bedrag=10000.0,
        tag="gepensioneerde",  # spaarplan op maat
    ),
]


VOORNAMEN = [
    "Noah", "Olivia", "Arthur", "Louise", "Leon", "Mila", "Finn", "Ella",
    "Jules", "Nora", "Lucas", "Alice", "Adam", "Juliette", "Vince", "Lina",
    "Mats", "Jade", "Seppe", "Fleur", "Tuur", "Noor", "Warre", "Amélie",
]
ACHTERNAMEN = [
    "Janssens", "Maes", "Jacobs", "Mertens", "Willems", "Claes", "Goossens",
    "Wouters", "De Smet", "Dubois", "Lambert", "Dupont", "Verstraeten",
    "Smets", "Hermans", "Michiels", "Aerts", "Desmet", "Pauwels", "Coppens",
]
WOONPLAATSEN = [
    ("Brussel", "1000"), ("Antwerpen", "2000"), ("Gent", "9000"),
    ("Leuven", "3000"), ("Brugge", "8000"), ("Mechelen", "2800"),
    ("Hasselt", "3500"), ("Kortrijk", "8500"), ("Oostende", "8400"),
    ("Aalst", "9300"), ("Sint-Niklaas", "9100"), ("Genk", "3600"),
]
GEZINSSITUATIES = ["alleenstaand", "koppel", "gezin", "student", "gepensioneerd"]

ABO_CATALOGUS = [
    ("Netflix", 15.99, "streaming"),
    ("Spotify", 10.99, "streaming"),
    ("Disney+", 8.99, "streaming"),
    ("Amazon Prime", 4.99, "streaming"),
    ("Basic-Fit", 26.99, "sport"),
    ("Jims Fitness", 39.99, "sport"),
    ("Adobe Creative Cloud", 59.99, "software"),
    ("Microsoft 365", 7.00, "software"),
    ("iCloud+", 2.99, "software"),
    ("Strava Summit", 5.99, "sport"),
    ("HelloFresh", 49.99, "overig"),
    ("Cambio Mobility", 12.00, "mobiliteit"),
    ("VRT MAX+", 3.99, "streaming"),
    ("Play Sports", 19.95, "streaming"),
    ("The Economist", 12.50, "overig"),
]

TRANSACTIE_CATS_UITGAVE = [
    ("boodschappen", ["Colruyt", "Delhaize", "Aldi", "Carrefour", "Albert Heijn"]),
    ("horeca", ["Starbucks", "Quick", "McDonald's", "Lunch Garden", "Bar Bouillon"]),
    ("mobiliteit", ["NMBS", "De Lijn", "Uber", "Bolt", "Parking.gent"]),
    ("auto", ["Q8", "Shell", "TotalEnergies", "Bosch Car Service", "Autokeuring"]),
    ("wonen", ["Fluvius", "Telenet", "Proximus", "Water-link", "Syndicus"]),
    ("kleding", ["Zara", "H&M", "About You", "Zalando", "Torfs"]),
    ("gezondheid", ["Apotheek", "Dokter", "Mutualiteit remgeld", "Dentist"]),
    ("vrije_tijd", ["Kinepolis", "Ticketmaster", "Decathlon", "Fnac"]),
    ("kinderen", ["DreamLand", "Schoolfactuur", "Kinderopvang", "Sportclub kids"]),
]

ZOEK_QUERIES_ALGEMEEN = [
    "spaarrekening rente", "overzicht rekeningen", "kaart blokkeren",
    "contact KBC", "app installeren", "betalingslimiet verhogen",
]


def _d(days_ago: int) -> str:
    return (TODAY - timedelta(days=days_ago)).isoformat()


def _month_starts(n: int) -> list[date]:
    """Eerste dag van de laatste n maanden (inclusief huidige maand)."""
    starts: list[date] = []
    y, m = TODAY.year, TODAY.month
    for _ in range(n):
        starts.append(date(y, m, 1))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return list(reversed(starts))


def _rand_day_in_month(rng: random.Random, month_start: date) -> date:
    if month_start.month == 12:
        nxt = date(month_start.year + 1, 1, 1)
    else:
        nxt = date(month_start.year, month_start.month + 1, 1)
    last = (nxt - timedelta(days=1)).day
    return date(month_start.year, month_start.month, rng.randint(1, last))


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)


def insert_klant(conn: sqlite3.Connection, **fields) -> int:
    cols = ", ".join(fields)
    placeholders = ", ".join("?" for _ in fields)
    cur = conn.execute(
        f"INSERT INTO klanten ({cols}) VALUES ({placeholders})",
        tuple(fields.values()),
    )
    return int(cur.lastrowid)


def seed_demo_klanten(conn: sqlite3.Connection) -> None:
    for p in DEMO_PERSONAS:
        insert_klant(
            conn,
            id=p.id,
            voornaam=p.voornaam,
            achternaam=p.achternaam,
            leeftijd=p.leeftijd,
            gezinssituatie=p.gezinssituatie,
            woonplaats=p.woonplaats,
            postcode=p.postcode,
            inkomen_maand=p.inkomen_maand,
            heeft_auto=int(p.heeft_auto),
            aantal_kinderen=p.aantal_kinderen,
            verhuisd_recent=int(p.verhuisd_recent),
            spaardoel=p.spaardoel,
            spaardoel_bedrag=p.spaardoel_bedrag,
            is_demo=1,
        )


def seed_filler_klanten(conn: sqlite3.Connection, rng: random.Random) -> list[int]:
    ids: list[int] = []
    next_id = len(DEMO_PERSONAS) + 1
    for i in range(N_FILLER_KLANTEN):
        situatie = rng.choice(GEZINSSITUATIES)
        plaats, post = rng.choice(WOONPLAATSEN)
        if situatie == "student":
            leeftijd = rng.randint(18, 25)
            inkomen = rng.uniform(700, 1200)
            kids = 0
            auto = False
        elif situatie == "gepensioneerd":
            leeftijd = rng.randint(65, 82)
            inkomen = rng.uniform(1400, 2400)
            kids = 0
            auto = rng.random() < 0.4
        elif situatie == "gezin":
            leeftijd = rng.randint(30, 50)
            inkomen = rng.uniform(3200, 5500)
            kids = rng.randint(1, 3)
            auto = rng.random() < 0.85
        else:
            leeftijd = rng.randint(24, 55)
            inkomen = rng.uniform(2000, 4500)
            kids = 0
            auto = rng.random() < 0.55

        spaardoel = None
        spaardoel_bedrag = None
        if rng.random() < 0.35:
            spaardoel = rng.choice(["huis", "vakantie", "auto", "renovatie", "buffer"])
            spaardoel_bedrag = round(rng.choice([2000, 5000, 10000, 15000, 25000]), 2)

        kid = insert_klant(
            conn,
            id=next_id + i,
            voornaam=rng.choice(VOORNAMEN),
            achternaam=rng.choice(ACHTERNAMEN),
            leeftijd=leeftijd,
            gezinssituatie=situatie,
            woonplaats=plaats,
            postcode=post,
            inkomen_maand=round(inkomen, 2),
            heeft_auto=int(auto),
            aantal_kinderen=kids,
            verhuisd_recent=int(rng.random() < 0.08),
            spaardoel=spaardoel,
            spaardoel_bedrag=spaardoel_bedrag,
            is_demo=0,
        )
        ids.append(kid)
    return ids


def _add_inkomen(
    rows: list[tuple],
    klant_id: int,
    maanden: list[date],
    bedrag: float,
    omschrijving: str,
    tegenpartij: str,
    dag: int = 1,
) -> None:
    for ms in maanden:
        d = date(ms.year, ms.month, min(dag, 28))
        rows.append(
            (klant_id, d.isoformat(), round(bedrag, 2), "inkomen", omschrijving, tegenpartij)
        )


def _add_random_uitgaven(
    rows: list[tuple],
    rng: random.Random,
    klant_id: int,
    maanden: list[date],
    per_maand: int,
    *,
    include_auto: bool = False,
    include_kids: bool = False,
) -> None:
    for ms in maanden:
        for _ in range(per_maand):
            cats = list(TRANSACTIE_CATS_UITGAVE)
            if not include_auto:
                cats = [c for c in cats if c[0] != "auto"]
            if not include_kids:
                cats = [c for c in cats if c[0] != "kinderen"]
            cat, merchants = rng.choice(cats)
            merchant = rng.choice(merchants)
            if cat == "boodschappen":
                bedrag = -round(rng.uniform(15, 95), 2)
            elif cat == "auto":
                bedrag = -round(rng.uniform(40, 120), 2)
            elif cat == "wonen":
                bedrag = -round(rng.uniform(30, 180), 2)
            elif cat == "kinderen":
                bedrag = -round(rng.uniform(20, 150), 2)
            else:
                bedrag = -round(rng.uniform(5, 60), 2)
            d = _rand_day_in_month(rng, ms)
            rows.append(
                (klant_id, d.isoformat(), bedrag, cat, f"Betaling {merchant}", merchant)
            )


def _abo_payments(
    rows: list[tuple],
    klant_id: int,
    maanden: list[date],
    naam: str,
    bedrag: float,
    start: date,
) -> None:
    for ms in maanden:
        if ms < date(start.year, start.month, 1):
            continue
        pay_day = date(ms.year, ms.month, min(start.day, 28))
        rows.append(
            (
                klant_id,
                pay_day.isoformat(),
                -round(bedrag, 2),
                "abonnement",
                f"Abonnement {naam}",
                naam,
            )
        )


def seed_transacties_en_abos(
    conn: sqlite3.Connection,
    rng: random.Random,
    klant_ids: list[int],
) -> None:
    maanden = _month_starts(MAANDEN_HISTORIE)
    tx_rows: list[tuple] = []
    abo_rows: list[tuple] = []

    # --- Demo 1: Student Emma — veel kleine / slapende abonnementen ---
    _add_inkomen(tx_rows, 1, maanden, 550, "Studietoelage", "Vlaanderen")
    _add_inkomen(tx_rows, 1, maanden, 400, "Loon jobstudent", "Horeca BV")
    _add_random_uitgaven(tx_rows, rng, 1, maanden, per_maand=10)
    student_abos = [
        ("Spotify", 5.99, "streaming", _d(400), _d(3), True),       # actief gebruikt
        ("Netflix", 15.99, "streaming", _d(500), _d(200), True),     # slapend
        ("Disney+", 8.99, "streaming", _d(300), None, True),         # nooit
        ("Basic-Fit", 26.99, "sport", _d(250), _d(180), True),       # slapend
        ("Adobe Creative Cloud", 24.99, "software", _d(180), None, True),  # trial vergeten
        ("iCloud+", 2.99, "software", _d(600), _d(5), True),
    ]
    for naam, bedrag, cat, start, last, actief in student_abos:
        abo_rows.append((1, naam, bedrag, "maandelijks", start, last, int(actief), cat))
        _abo_payments(tx_rows, 1, maanden, naam, bedrag, date.fromisoformat(start))

    # --- Demo 2: Jonge starter Thomas — spaardoel huis, geen strategie ---
    _add_inkomen(tx_rows, 2, maanden, 2650, "Salaris", "TechStart NV")
    _add_random_uitgaven(tx_rows, rng, 2, maanden, per_maand=14)
    starter_abos = [
        ("Spotify", 10.99, "streaming", _d(200), _d(2), True),
        ("Netflix", 15.99, "streaming", _d(220), _d(4), True),
        ("Microsoft 365", 7.00, "software", _d(150), _d(10), True),
    ]
    for naam, bedrag, cat, start, last, actief in starter_abos:
        abo_rows.append((2, naam, bedrag, "maandelijks", start, last, int(actief), cat))
        _abo_payments(tx_rows, 2, maanden, naam, bedrag, date.fromisoformat(start))
    # Huur
    for ms in maanden:
        tx_rows.append(
            (2, date(ms.year, ms.month, 1).isoformat(), -850.0, "wonen", "Huur appartement", "Immo Antwerpen")
        )

    # --- Demo 3: Gezin Sofie — auto + verhuis + kinderen ---
    _add_inkomen(tx_rows, 3, maanden, 2400, "Salaris Sofie", "Stad Gent")
    _add_inkomen(tx_rows, 3, maanden, 1800, "Salaris partner", "Volvo Cars")
    _add_random_uitgaven(
        tx_rows, rng, 3, maanden, per_maand=18, include_auto=True, include_kids=True
    )
    # Extra zware autokosten (signaal mobiliteit)
    for ms in maanden:
        tx_rows.append(
            (
                3,
                _rand_day_in_month(rng, ms).isoformat(),
                -round(rng.uniform(90, 140), 2),
                "auto",
                "Tankbeurt Q8",
                "Q8",
            )
        )
        if rng.random() < 0.4:
            tx_rows.append(
                (
                    3,
                    _rand_day_in_month(rng, ms).isoformat(),
                    -round(rng.uniform(80, 350), 2),
                    "auto",
                    "Onderhoud / herstelling",
                    "Bosch Car Service",
                )
            )
    # Verhuis-kosten recent
    tx_rows.append((3, _d(45), -1200.0, "wonen", "Verhuisfirma", "MoveIt Gent"))
    tx_rows.append((3, _d(40), -450.0, "wonen", "Waarborg nieuwe woning", "Immo Gent"))
    gezin_abos = [
        ("Netflix", 22.99, "streaming", _d(700), _d(1), True),
        ("Spotify Family", 17.99, "streaming", _d(500), _d(2), True),
        ("Play Sports", 19.95, "streaming", _d(400), _d(90), True),  # semi-slapend
        ("HelloFresh", 59.99, "overig", _d(100), _d(95), True),      # vergeten
    ]
    for naam, bedrag, cat, start, last, actief in gezin_abos:
        abo_rows.append((3, naam, bedrag, "maandelijks", start, last, int(actief), cat))
        _abo_payments(tx_rows, 3, maanden, naam, bedrag, date.fromisoformat(start))
    # Hypotheek / lening
    for ms in maanden:
        tx_rows.append(
            (3, date(ms.year, ms.month, 5).isoformat(), -980.0, "wonen", "Hypotheekafbetaling", "KBC Krediet")
        )

    # --- Demo 4: Professional Lars — hoge vaste kosten + slapende abo's ---
    _add_inkomen(tx_rows, 4, maanden, 3800, "Salaris", "Deloitte")
    _add_random_uitgaven(tx_rows, rng, 4, maanden, per_maand=12, include_auto=True)
    for ms in maanden:
        tx_rows.append(
            (4, date(ms.year, ms.month, 1).isoformat(), -1350.0, "wonen", "Huur loft Brussel", "Immoweb Landlord")
        )
        tx_rows.append(
            (
                4,
                _rand_day_in_month(rng, ms).isoformat(),
                -round(rng.uniform(70, 110), 2),
                "auto",
                "Tankbeurt",
                "Shell",
            )
        )
    lars_abos = [
        ("Jims Fitness", 39.99, "sport", _d(400), _d(320), True),        # slapend
        ("The Economist", 12.50, "overig", _d(600), None, True),         # nooit
        ("Netflix", 15.99, "streaming", _d(800), _d(3), True),
        ("Spotify", 10.99, "streaming", _d(800), _d(1), True),
        ("Adobe Creative Cloud", 59.99, "software", _d(350), _d(300), True),  # slapend
        ("Amazon Prime", 4.99, "streaming", _d(200), _d(15), True),
        ("Cambio Mobility", 12.00, "mobiliteit", _d(180), _d(160), True),     # slapend
    ]
    for naam, bedrag, cat, start, last, actief in lars_abos:
        abo_rows.append((4, naam, bedrag, "maandelijks", start, last, int(actief), cat))
        _abo_payments(tx_rows, 4, maanden, naam, bedrag, date.fromisoformat(start))

    # --- Demo 5: Gepensioneerde Marie — pensioen + spaargeld ---
    _add_inkomen(tx_rows, 5, maanden, 1850, "Wettelijk pensioen", "FPD Pensioenen")
    _add_random_uitgaven(tx_rows, rng, 5, maanden, per_maand=8)
    marie_abos = [
        ("VRT MAX+", 3.99, "streaming", _d(200), _d(5), True),
        ("Netflix", 15.99, "streaming", _d(100), _d(7), True),
    ]
    for naam, bedrag, cat, start, last, actief in marie_abos:
        abo_rows.append((5, naam, bedrag, "maandelijks", start, last, int(actief), cat))
        _abo_payments(tx_rows, 5, maanden, naam, bedrag, date.fromisoformat(start))
    for ms in maanden:
        tx_rows.append(
            (5, date(ms.year, ms.month, 1).isoformat(), -620.0, "wonen", "Huur appartement", "Woonmaatschappij")
        )

    # --- Filler-klanten ---
    for kid in klant_ids:
        row = conn.execute(
            "SELECT inkomen_maand, heeft_auto, aantal_kinderen, gezinssituatie FROM klanten WHERE id = ?",
            (kid,),
        ).fetchone()
        inkomen, auto, kids, situatie = row
        label = "Pensioen" if situatie == "gepensioneerd" else "Salaris"
        partij = "FPD Pensioenen" if situatie == "gepensioneerd" else "Werkgever BV"
        _add_inkomen(tx_rows, kid, maanden, float(inkomen), label, partij)
        _add_random_uitgaven(
            tx_rows,
            rng,
            kid,
            maanden,
            per_maand=rng.randint(8, 16),
            include_auto=bool(auto),
            include_kids=kids > 0,
        )
        n_abos = rng.randint(1, 4)
        chosen = rng.sample(ABO_CATALOGUS, n_abos)
        for naam, bedrag, cat in chosen:
            start_days = rng.randint(60, 700)
            start = _d(start_days)
            # ~25% slapend
            if rng.random() < 0.25:
                last = _d(rng.randint(90, 250)) if rng.random() < 0.7 else None
            else:
                last = _d(rng.randint(0, 20))
            abo_rows.append((kid, naam, bedrag, "maandelijks", start, last, 1, cat))
            _abo_payments(tx_rows, kid, maanden, naam, bedrag, date.fromisoformat(start))

    conn.executemany(
        """INSERT INTO transacties
           (klant_id, datum, bedrag, categorie, omschrijving, tegenpartij)
           VALUES (?, ?, ?, ?, ?, ?)""",
        tx_rows,
    )
    conn.executemany(
        """INSERT INTO abonnementen
           (klant_id, naam, bedrag, frequentie, start_datum, laatste_gebruik, actief, categorie)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        abo_rows,
    )


def seed_zoekopdrachten(conn: sqlite3.Connection, rng: random.Random, klant_ids: list[int]) -> None:
    rows: list[tuple] = []

    # Student → studentenkorting / abo's
    for q, days in [
        ("studentenkorting abonnementen", 12),
        ("Spotify student", 11),
        ("abonnementen opzeggen", 8),
        ("overzicht vaste kosten", 5),
    ]:
        rows.append((1, q, _d(days), "app"))

    # Starter → spaardoel huis
    for q, days in [
        ("spaarrekening huis kopen", 20),
        ("hoeveel sparen per maand", 18),
        ("woonsparen KBC", 15),
        ("spaardoel aanmaken", 10),
        ("rente spaarboekje", 3),
    ]:
        rows.append((2, q, _d(days), rng.choice(["app", "web", "kate"])))

    # Gezin → verhuis + verzekering + auto
    for q, days in [
        ("adres wijzigen verzekering", 40),
        ("verhuis melden KBC", 38),
        ("brandverzekering nieuw adres", 35),
        ("totale autokost berekenen", 14),
        ("autoverzekering overzicht", 10),
    ]:
        rows.append((3, q, _d(days), rng.choice(["app", "web"])))

    # Professional → slapend geld
    for q, days in [
        ("vaste kosten verlagen", 25),
        ("abonnementen die ik niet gebruik", 22),
        ("overzicht domiciliëringen", 7),
    ]:
        rows.append((4, q, _d(days), "app"))

    # Gepensioneerde → spaarplan
    for q, days in [
        ("spaarplan pensioen", 30),
        ("veilig beleggen senioren", 20),
        ("rente op spaargeld", 8),
        ("Kate spaaradvies", 4),
    ]:
        rows.append((5, q, _d(days), rng.choice(["app", "kate"])))

    for kid in klant_ids:
        for _ in range(rng.randint(0, 4)):
            rows.append(
                (
                    kid,
                    rng.choice(ZOEK_QUERIES_ALGEMEEN),
                    _d(rng.randint(1, 180)),
                    rng.choice(["app", "web"]),
                )
            )

    conn.executemany(
        "INSERT INTO zoekopdrachten (klant_id, query, datum, kanaal) VALUES (?, ?, ?, ?)",
        rows,
    )


def seed_spaar(conn: sqlite3.Connection, rng: random.Random, klant_ids: list[int]) -> None:
    rows: list[tuple] = []

    # Thomas: vaak kijken, weinig storten → geen concreet spaarplan
    saldo = 1800.0
    rows.append((2, _d(60), "doel_aangemaakt", None, saldo, "Spaardoel: huis €25.000"))
    for days, typ, bedrag in [
        (55, "bekeken", None),
        (48, "bekeken", None),
        (40, "storting", 100.0),
        (33, "bekeken", None),
        (25, "bekeken", None),
        (18, "opname", -50.0),
        (12, "bekeken", None),
        (5, "bekeken", None),
        (2, "bekeken", None),
    ]:
        if bedrag:
            saldo += bedrag
        rows.append((2, _d(days), typ, bedrag, round(saldo, 2), None))

    # Sofie: spaardoel vakantie, regelmatig
    saldo = 1200.0
    rows.append((3, _d(90), "doel_aangemaakt", None, saldo, "Spaardoel: vakantie €4.000"))
    for days in [80, 70, 60, 50, 40, 30, 20, 10]:
        bedrag = 150.0
        saldo += bedrag
        rows.append((3, _d(days), "storting", bedrag, round(saldo, 2), None))

    # Marie: groot spaarsaldo, zoekt advies
    saldo = 42000.0
    rows.append((5, _d(120), "doel_aangemaakt", None, saldo, "Spaardoel: pensioenbuffer €10.000"))
    for days, typ, bedrag in [
        (100, "bekeken", None),
        (70, "storting", 200.0),
        (45, "bekeken", None),
        (20, "bekeken", None),
        (6, "storting", 200.0),
    ]:
        if bedrag:
            saldo += bedrag
        rows.append((5, _d(days), typ, bedrag, round(saldo, 2), None))

    # Emma: bijna geen spaarinteractie
    rows.append((1, _d(90), "bekeken", None, 120.0, None))

    # Lars: spaart niet actief
    rows.append((4, _d(200), "bekeken", None, 8500.0, None))

    for kid in klant_ids:
        if rng.random() < 0.4:
            saldo = round(rng.uniform(100, 15000), 2)
            for _ in range(rng.randint(1, 5)):
                typ = rng.choice(["bekeken", "bekeken", "storting", "opname"])
                bedrag = None
                if typ == "storting":
                    bedrag = round(rng.uniform(25, 300), 2)
                    saldo += bedrag
                elif typ == "opname":
                    bedrag = -round(rng.uniform(20, 200), 2)
                    saldo = max(0, saldo + bedrag)
                rows.append((kid, _d(rng.randint(1, 200)), typ, bedrag, round(saldo, 2), None))

    conn.executemany(
        """INSERT INTO spaarrekening_interacties
           (klant_id, datum, type, bedrag, saldo_na, notitie)
           VALUES (?, ?, ?, ?, ?, ?)""",
        rows,
    )


def seed_verzekeringen(conn: sqlite3.Connection, rng: random.Random, klant_ids: list[int]) -> None:
    rows: list[tuple] = []

    # Sofie: verhuisd, polisadressen nog op OUD adres (signaal Auto-Address Sync)
    oud = "Veldstraat 12, 9000 Gent"
    rows.append((3, "brand", "BR-2021-88421", oud, 28.50, 1))
    rows.append((3, "auto", "AU-2019-33102", oud, 62.00, 1))
    rows.append((3, "familiale", "FA-2020-11009", oud, 9.90, 1))

    rows.append((4, "brand", "BR-2018-22011", "Rue de la Loi 45, 1000 Brussel", 35.00, 1))
    rows.append((4, "auto", "AU-2022-99881", "Rue de la Loi 45, 1000 Brussel", 55.00, 1))
    rows.append((5, "brand", "BR-2010-10001", "Langestraat 3, 8000 Brugge", 22.00, 1))
    rows.append((5, "hospitalisatie", "HO-2015-44002", "Langestraat 3, 8000 Brugge", 45.00, 1))

    for kid in klant_ids:
        k = conn.execute(
            "SELECT woonplaats, postcode, heeft_auto, verhuisd_recent FROM klanten WHERE id = ?",
            (kid,),
        ).fetchone()
        woonplaats, postcode, auto, verhuisd = k
        adres = f"Straat {rng.randint(1, 120)}, {postcode} {woonplaats}"
        if verhuisd:
            # verouderd polisadres
            andere = rng.choice([w for w in WOONPLAATSEN if w[0] != woonplaats])
            adres = f"Oudebaan {rng.randint(1, 80)}, {andere[1]} {andere[0]}"
        rows.append((kid, "brand", f"BR-F-{kid:04d}", adres, round(rng.uniform(18, 40), 2), 1))
        if auto:
            rows.append((kid, "auto", f"AU-F-{kid:04d}", adres, round(rng.uniform(40, 90), 2), 1))
        if rng.random() < 0.3:
            rows.append(
                (kid, "hospitalisatie", f"HO-F-{kid:04d}", adres, round(rng.uniform(30, 70), 2), 1)
            )

    conn.executemany(
        """INSERT INTO verzekeringen
           (klant_id, type, polisnummer, polisadres, maandpremie, actief)
           VALUES (?, ?, ?, ?, ?, ?)""",
        rows,
    )


def generate(db_path: Path = DB_PATH) -> dict[str, int]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    rng = random.Random(SEED)
    conn = sqlite3.connect(db_path)
    try:
        create_schema(conn)
        seed_demo_klanten(conn)
        filler_ids = seed_filler_klanten(conn, rng)
        seed_transacties_en_abos(conn, rng, filler_ids)
        seed_zoekopdrachten(conn, rng, filler_ids)
        seed_spaar(conn, rng, filler_ids)
        seed_verzekeringen(conn, rng, filler_ids)
        conn.commit()

        counts = {
            "klanten": conn.execute("SELECT COUNT(*) FROM klanten").fetchone()[0],
            "transacties": conn.execute("SELECT COUNT(*) FROM transacties").fetchone()[0],
            "abonnementen": conn.execute("SELECT COUNT(*) FROM abonnementen").fetchone()[0],
            "zoekopdrachten": conn.execute("SELECT COUNT(*) FROM zoekopdrachten").fetchone()[0],
            "spaarrekening_interacties": conn.execute(
                "SELECT COUNT(*) FROM spaarrekening_interacties"
            ).fetchone()[0],
            "verzekeringen": conn.execute("SELECT COUNT(*) FROM verzekeringen").fetchone()[0],
        }
    finally:
        conn.close()
    return counts


def main() -> None:
    counts = generate()
    print(f"Database geschreven: {DB_PATH}")
    print(f"Seed: {SEED}")
    print("Demo-persona's (is_demo=1):")
    for p in DEMO_PERSONAS:
        print(f"  id={p.id}  {p.voornaam} {p.achternaam:12}  -> {p.tag}")
    print("Rijen:")
    for table, n in counts.items():
        print(f"  {table:28} {n}")


if __name__ == "__main__":
    main()

# Tectonic-Hackaton-Mang
Repo for the 2026 tectonic hackaton for team Mang

# Projectinhoud:
We maken een interactieve functie in de KBC-app na, dit ter illustratie van een toekomstig mogelijke implementatie.
We moeten dus de kbc website nabouwen en daarin een testversie van die feauture verwerken.
# 🚀 KBC SignalEngine

> **Tectonic Hackathon 2026** — KBC Challenge PoC[cite: 1]
KBC SignalEngine analyseert transacties, zoekgedrag en profieldata om automatisch herkenbare situaties te detecteren en direct concrete oplossingen te bieden voor 2,3M KBC-klanten[cite: 3, 4].

---

## 📌 Werking: Signaal ➔ Probleem ➔ Oplossing
### 1. Signalen (Data-input)
* Inkomsten & uitgaven[cite: 4]
* Leeftijd & familiesituatie[cite: 4]
* Abonnementen (looptijd & frequentie)[cite: 4]
* Autokosten
* Spaarrekening-interactie & zoekopdrachten[cite: 4]
* Verhuisdata & aankopen[cite: 4]

### 2. Bekende Problemen
* **Slapend geldverlies:** Actieve betalingen voor vergeten of oude abonnementen.
* **Onoverzichtelijke mobiliteit:** Geen zicht op de totale autokost.
* **Geen concreet spaarplan:** Wel een spaardoel (huis, vakantie), geen haalbare strategie.
* **Administratieve frictie:** Adreswijziging verzekeringen vergeten bij verhuizing.

### 3. Probleemoplossing
* **Abonnementen-audit:** Direct overzicht van slapende kosten met stopzet-knop.
* **Mobiliteits-dashboard:** Totale autokost in één oogopslag.
* **Dynamisch spaarplan:** Gepersonaliseerd traject op basis van overschot en doel.
* **Auto-Address Sync:** 1-click update van polisadressen bij verhuisdetectie.

---

## 🧩 Projectopdeling (Werkpakketten)

### Deel 1 — Fake dataset creëren
Synthetische KBC-data genereren die realistisch genoeg is om signalen in te herkennen.
* Transacties: inkomsten/uitgaven, categorie, bedrag, frequentie
* Profieldata: leeftijd, gezinssituatie, woonplaats
* Abonnementen: looptijd, bedrag, laatste gebruik
* Zoekgedrag & spaarrekening-interactie
* Randvoorwaarden: privacy-veilig (geen echte data), reproduceerbaar (vaste seed), genoeg volume voor een overtuigende demo
* **Beslissing:** we maken **1 gedeelde dataset** met alle persona's erin (geen aparte datasets per user type). Elke persona krijgt wel een scripted "verhaallijn" zodat de demo het probleem meteen duidelijk maakt.

### Deel 2 — Dataset klassificeren naar user types
Regels en/of ML om klanten in herkenbare persona's te verdelen.
* Voorbeeldpersona's: student, jonge starter, alleenstaande professional, gezin met kinderen, gepensioneerde
* Signalen mappen op persona-kenmerken (bv. gezin + verhuizing + autokosten)
* Aanpak: start regelgebaseerd (uitlegbaar en snel), later eventueel clustering/ML
* **Denk mee:** houd het uitlegbaar — bij elke classificatie moet je kunnen tonen *waarom* iemand die persona krijgt.

### Deel 3 — User interface creëren
Nabouw van de KBC-app/webinterface met de SignalEngine-feature erin.
* React front-end, responsive, in KBC-huisstijl
* Overzichtsscherm met gedetecteerde signalen
* Detailkaarten per probleem met een directe actie-knop (abonnement stopzetten, spaarplan starten, ...)
* **Beslissing:** we bouwen meteen een echte **React-app (Vite)** i.p.v. een losse static mock, maar de front-end start op **hardcoded mock-JSON** zodat we niet moeten wachten op de back-end. Daarna vervangen we de mock door de echte FastAPI-calls.
* **Denk mee:** houd de flow **signaal ➔ probleem ➔ oplossing** centraal in elke stap van de UI.

### Deel 4 — Wat krijgt elke user?
Personalisatie: welke meldingen en oplossingen tonen we per persona.
* Prioritering/ranking van signalen (impact vs. urgentie)
* Relevante oplossing per persona (student ➔ goedkoper abonnement, gezin ➔ verhuis-sync, ...)
* Drempel/timing: niet spammen, alleen zinvolle signalen
* **Denk mee:** definieer een "signal score" en een expliciete mapping **persona ➔ mogelijke acties**.

| Persona | Herkenningssignaal | Mogelijke oplossing |
| --- | --- | --- |
| Student | Laag inkomen, veel kleine abonnementen | Abonnementen-audit / studentenkorting |
| Jonge starter | Eerste loon, spaardoel | Dynamisch spaarplan |
| Gezin | Kinderen, verhuizing, autokosten | Auto-Address Sync + mobiliteits-dashboard |
| Alleenstaande professional | Weinig vrije tijd, hoge vaste kosten | Slapend geld-detectie |
| Gepensioneerde | Vast pensioen, spaargeld | Spaarplan op maat |

---

## 👥 Plan van aanpak — 4 personen parallel

We werken met **4 mensen tegelijk**, ongeveer 1 werkstroom per deel. Om elkaar niet te blokkeren bevriezen we eerst de **gedeelde contracten** en werken we daarna onafhankelijk verder.

### Stap 0 — Contracten bevriezen (samen, ±30 min)
Voordat iemand begint, leggen we vast:
1. **Datacontract** — exacte JSON-vorm van de gedeelde dataset (klant, transacties, abonnementen, profiel).
2. **Signaal-/persona-contract** — hoe een geclassificeerde user + gedetecteerd signaal eruitziet.
3. **API-contract** — welke endpoints de front-end nodig heeft (bv. `GET /users`, `GET /users/{id}/signals`).

Zolang deze vastliggen kan iedereen met mock-data werken zonder op elkaar te wachten.

### Werkstromen

| Persoon | Werkstroom | Levert op | Blokkeert op |
| --- | --- | --- | --- |
| A | **Deel 1** — Fake dataset generator | `data/dataset.json` (1 gedeelde dataset) | Datacontract |
| B | **Deel 2** — Classificatie + signal score | persona + signalen per user | Datacontract |
| C | **Deel 3** — React UI (mock ➔ echte API) | werkende KBC-app met SignalEngine | API-contract |
| D | **Deel 4** — Personalisatie + integratie (FastAPI) | ranking + "wat krijgt de user" logica | Signaal-contract |

### Afspraken
* **Git:** per werkstroom een eigen branch (`feat/dataset`, `feat/classifier`, `feat/ui`, `feat/personalization`), via PR naar `main`. Nooit direct op `main`.
* **Mock eerst:** de front-end (C) en integratie (D) gebruiken een gecommitte `mock.json` zolang de echte data/API nog niet klaar is.
* **Dagelijkse sync:** korte check of de contracten nog kloppen; wijzig je een contract, meld het meteen aan de groep.
* **Demo-verhaallijn:** 1 persona volledig uitwerken tot een klikbare flow is belangrijker dan alle persona's half.

### Volgorde & afhankelijkheden
```
Stap 0 (contracten)
   ├─► A: dataset ──► B: classificatie ──► D: personalisatie ──► C: UI integreert
   └─► C: UI-bouw op mock.json (parallel vanaf minuut 1)
```

---

## 🧱 Projectstructuur & functies bouwen

De fake-dataset komt als **SQLite-bestand** in `data/fake.db`. Functies die de data
verwerken schrijven **JSON-bestanden** naar `output/`, die de website inleest.

```
src/tectonic_hackaton_mang/
├── db.py                  # gedeelde helper: get_db() opent de dataset
├── transactions.py        # gedeelde helpers: tabel/kolommen detecteren + parsen
├── functions/             # ⭐ hier bouw je functies, 1 bestand per persoon/feature
│   ├── __init__.py
│   ├── voorbeeld.py       # sjabloon + voorbeeldfunctie
│   ├── recurring_expenses.py  # terugkerende uitgaven / abonnementen
│   └── home_purchase.py   # spaar- en woonanalyse
└── export.py              # draait alle functies → schrijft output/*.json
data/
└── fake.db                # fake-dataset (SQLite)
output/
└── *.json                 # output voor de website (gegenereerd, niet gecommit)
```

> 🧰 **`transactions.py`** is de gedeelde laag: `load_transactions(conn)` detecteert
> zelf de transactietabel en de kolommen (NL/EN) en geeft `Transaction`-objecten terug.
> Gebruik die i.p.v. zelf SQL-kolomnamen te raden.

> ⚠️ **Naam van het bestand:** gebruik `data/fake.db`, **niet** `db.sqlite3` — die
> laatste staat in `.gitignore` en zou dus niet gedeeld worden via git.

### Zo werkt het
1. **`db.py`** — iedereen gebruikt dezelfde helper. `get_db()` geeft een SQLite-connectie
   terug waarvan de rijen via de kolomnaam te lezen zijn (`row["amount"]`).
2. **`functions/`** — elke persoon maakt zijn **eigen bestand** (bv. `abonnementen.py`).
   Aparte bestanden = geen merge-conflicten.
3. **`export.py`** — roept automatisch alle functies aan en schrijft per functie een JSON
   naar `output/`.

### Een functie toevoegen
1. Kopieer `functions/voorbeeld.py` naar `functions/<jouw_bestand>.py`.
2. Schrijf je functie: krijgt de connectie binnen, geeft een **JSON-serialiseerbare dict**
   terug.
3. Zet je functie in de lijst `FUNCTIONS` onderaan het bestand.

```python
def slapende_abonnementen(conn: sqlite3.Connection) -> dict:
    rows = conn.execute("SELECT * FROM abonnementen WHERE laatste_gebruik < ...").fetchall()
    return {
        "title": "Slapend geldverlies",
        "message": f"{len(rows)} abonnementen ongebruikt.",
        "items": [dict(row) for row in rows],
    }

FUNCTIONS = [slapende_abonnementen]
```

### Runnen
```bash
uv run python -m tectonic_hackaton_mang.export
```
Dit schrijft `output/<bestand>__<functie>.json`, klaar om door de website gelezen te worden.

### Beschikbare functies

#### `find_recurring_expenses` — terugkerende uitgaven / abonnementen
`functions/recurring_expenses.py` → output: `output/recurring_expenses__find_recurring_expenses.json`

Detecteert **maandelijkse én jaarlijkse** terugkerende uitgaven (abonnementen) op basis
van historiek. Ze is **schema-onafhankelijk**: de functie zoekt zelf de transactietabel en
de kolommen voor datum, bedrag, naam en (optioneel) categorie, met zowel NL- als EN-kolomnamen.

```json
{
  "title": "Terugkerende uitgaven",
  "message": "3 terugkerende uitgaven gevonden (2 maandelijks, 1 jaarlijks).",
  "source_table": "transacties",
  "count": 3,
  "monthly_count": 2,
  "yearly_count": 1,
  "monthly_total": 33.23,
  "yearly_total": 398.76,
  "subscriptions": [
    {
      "name": "NETFLIX.COM",
      "frequency": "monthly",
      "average_amount": 13.99,
      "currency": "EUR",
      "category": "Entertainment",
      "occurrences": 6,
      "months_active": 6,
      "interval_days": 31,
      "first_seen": "2026-01-05",
      "last_seen": "2026-06-05",
      "next_expected": "2026-07-06",
      "monthly_cost": 13.99,
      "yearly_cost": 167.88,
      "confidence": 0.92
    },
    {
      "name": "Amazon Prime Jaar",
      "frequency": "yearly",
      "average_amount": 99.0,
      "currency": "EUR",
      "category": "Entertainment",
      "occurrences": 2,
      "months_active": 2,
      "interval_days": 365,
      "first_seen": "2025-09-01",
      "last_seen": "2026-09-01",
      "next_expected": "2027-09-01",
      "monthly_cost": 8.25,
      "yearly_cost": 99.0,
      "confidence": 0.5
    }
  ]
}
```

**Velden per abonnement**

| Veld | Betekenis |
| --- | --- |
| `name` | Naam van de handelaar/tegenpartij (opgeschoond) |
| `frequency` | `"monthly"` of `"yearly"` |
| `average_amount` | Gemiddeld bedrag per betaling |
| `currency` | Valuta (voorlopig altijd `"EUR"`) |
| `category` | Categorie indien aanwezig in de data, anders `null` |
| `occurrences` | Aantal betalingen in de dataset |
| `months_active` | Aantal verschillende maanden waarin betaald |
| `interval_days` | Mediaan interval tussen betalingen (dagen) |
| `first_seen` / `last_seen` | Eerste/laatste betaling (`YYYY-MM-DD`) |
| `next_expected` | Verwachte volgende betaling |
| `monthly_cost` | Kost per maand (jaarlijks bedrag wordt door 12 gedeeld) |
| `yearly_cost` | Kost per jaar (maandelijks bedrag × 12) |
| `confidence` | Zekerheid van de detectie (0.0 – 1.0) |

De website leest `subscriptions` om de lijst te tonen (filter op `frequency`), en
`monthly_total` / `yearly_total` (+ `monthly_count` / `yearly_count`) voor het
"slapend geld"-overzicht.

#### `analyze_home_purchase` — spaar- en woonanalyse
`functions/home_purchase.py` → output: `output/home_purchase__analyze_home_purchase.json`

Combineert signalen om te bepalen of iemand best **begint te sparen** of een **huis kan
kopen**, en hoeveel die persoon moet sparen voor een lening. Signalen:

* **vast inkomen** — terugkerende maandelijkse inkomsten;
* **Immoweb/vastgoed-activiteit** — transacties met bv. "immoweb" of "immo";
* **overschrijvingen naar de spaarrekening** — op basis van naam/categorie;
* **positieve spaarcapaciteit** — maandinkomen − maanduitgaven (spaargeld telt niet als kost);
* **vaste kosten** — terugkerende uitgaven.

Bestaat er een klant-kolom, dan krijgt **elke klant een eigen profiel**.

**Aannames** (bovenaan `home_purchase.py` aanpasbaar): woningprijs €300.000, 10% down
payment, 10% kosten, max. 40% schuldenlast, 3,5% rente, 25 jaar looptijd. Ze staan ook
in het veld `assumptions`.

```json
{
  "title": "Spaar- en woonanalyse",
  "message": "1 profiel(en) geanalyseerd.",
  "assumptions": { "target_home_price": 300000.0, "down_payment_pct": 0.1, "closing_costs_pct": 0.1,
                   "max_debt_ratio": 0.4, "annual_interest_rate": 0.035, "loan_term_years": 25 },
  "count": 1,
  "profiles": [
    {
      "customer": "C001",
      "signals": {
        "fixed_income": true,
        "monthly_income": 2500.0,
        "income_sources": [ { "name": "Werkgever NV", "frequency": "monthly", "monthly_cost": 2500.0 } ],
        "monthly_expenses": 914.5,
        "monthly_fixed_costs": 914.0,
        "savings_transfers": { "count": 6, "months": 6, "total": 1200.0,
                               "monthly_average": 200.0, "frequent": true },
        "real_estate_activity": { "count": 3, "total": 3.0, "active": true },
        "savings_capacity": 1585.5,
        "positive_savings_capacity": true
      },
      "advice": {
        "status": "on_track",
        "summary": "Je bent actief op vastgoed en spaart structureel. Met ±€1.586/maand spaar je in 38 maanden het benodigde startkapitaal bij elkaar.",
        "target_home_price": 300000.0,
        "down_payment_required": 30000.0,
        "closing_costs": 30000.0,
        "total_needed": 60000.0,
        "max_monthly_payment": 1000.0,
        "max_loan": 199750.88,
        "affordable_home_price": 221945.42,
        "gap_to_target": 78054.58,
        "effective_monthly_saving": 1585.5,
        "months_to_save": 38,
        "ready_date": "2029-06-01"
      }
    }
  ]
}
```

**`advice.status`** is één van:
`ready_to_buy` (kan doelwoning betalen), `on_track` (vast inkomen + positieve capaciteit),
`start_saving` (kan sparen, maar nog niet op weg), `not_ready` (geen vast inkomen of
negatieve capaciteit).

---

## 🛠️ Tech Stack & Partners

* **Back-end:** Python, FastAPI, Google Cloud (Vertex AI)[cite: 10]
* **Front-end:** React
* **ElevenLabs:** Gesproken audio-updates van Kate[cite: 8]
* **Aikido Security:** Geauditeerd op IDOR en autorisatielogica[cite: 6]

---

## 🔒 Security Score (Aikido)

* **Baseline Score:** [Voeg toe][cite: 7]
* **Resolved Issues:** [Voeg toe][cite: 7]
* **Final Score:** [Voeg toe][cite: 7]

---

## ⚙️ Quickstart

```bash
git clone [https://github.com/jouw-team/kbc-signal-engine.git](https://github.com/jouw-team/kbc-signal-engine.git)
cd kbc-signal-engine

# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend
cd ../frontend
npm install
npm run dev
# Instalatie tutortial
vind je hier [SETUP.md](SETUP.md)

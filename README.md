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

## 👥 Team & werkverdeling

We zijn met **4 mensen** en werken elk aan een eigen stuk, zodat we elkaar niet blokkeren.

| Persoon | Rol | Waar |
| --- | --- | --- |
| 1 | **Database** — fake-dataset genereren en onderhouden | `src/tectonic_hackaton_mang/backend/data/` → `data/fake.db` |
| 2 | **Functies** — signalen detecteren uit de data | `src/tectonic_hackaton_mang/backend/signals/` |
| 3 | **Functies** — signalen detecteren uit de data | `src/tectonic_hackaton_mang/backend/signals/` |
| 4 | **Website** — KBC-app bouwen op de JSON-output | `src/tectonic_hackaton_mang/frontend/` |

### Afspraken
* **Eén bron van data:** de database-persoon beheert `backend/data/generate.py` + `data/fake.db`; de anderen lezen enkel via `backend/data/readers.py`.
* **Eén functie per bestand:** de twee functie-makers werken elk in hun **eigen bestand** in `backend/signals/` → geen merge-conflicten.
* **Contract = JSON-output:** de website leest `output/*.json`. Wijzig je de vorm van een output, meld het meteen aan de website-persoon.
* **Git:** eigen branch per stuk (`feat/db`, `feat/functie-x`, `feat/website`), via PR naar `main`. Nooit direct op `main`.
* **Sync:** korte check of de output-contracten nog kloppen voor je iets wijzigt.

### Datastroom
```
data/generate.py ──► data/fake.db ──► data/readers.py ──► signals/*.py ──► output/*.json ──► frontend
```

---

## 🧱 Projectstructuur & functies bouwen

Alle code leeft onder `src/tectonic_hackaton_mang/`, opgedeeld in een **backend** (Python)
en een **frontend** (React-website). De fake-dataset staat als SQLite-bestand in
`data/fake.db`; de signalen schrijven **JSON** naar `output/`, die de website inleest.

```
src/tectonic_hackaton_mang/
├── __init__.py / __main__.py      # entrypoint: draait de export
├── backend/                       # 🐍 Python-backend
│   ├── config.py                  # paden (DB_PATH, OUTPUT_DIR)
│   ├── export.py                  # draait alle signalen → output/*.json
│   ├── data/                      # datalaag
│   │   ├── connection.py          # get_db() opent de dataset
│   │   ├── generate.py            # genereert data/fake.db (database-persoon)
│   │   ├── readers.py             # typed readers per tabel (klanten, abonnementen, ...)
│   │   └── transactions.py        # generieke transactie-helpers
│   └── signals/                   # ⭐ hier bouwen de twee functie-makers, 1 bestand p.p.
│       ├── __init__.py
│       ├── example.py             # sjabloon + voorbeeldfunctie
│       ├── recurring_expenses.py  # terugkerende uitgaven / abonnementen
│       └── home_purchase.py       # spaar- en woonanalyse
└── frontend/                      # 🌐 KBC-website (React + Vite, website-persoon)
data/
└── fake.db                        # fake-dataset (SQLite, gegenereerd door generate.py)
output/
└── *.json                         # output voor de website (gegenereerd, niet gecommit)
```

> 🗄️ **`backend/data/generate.py`** genereert `data/fake.db` (vaste seed, reproduceerbaar).
> Opnieuw genereren: `uv run python -m tectonic_hackaton_mang.backend.data.generate`.
>
> 🧰 **`backend/data/readers.py`** is de gedeelde leeslaag: `load_klanten`,
> `load_abonnementen`, `load_spaar_interacties`, `load_zoekopdrachten`, `load_verzekeringen`.
> Gebruik die i.p.v. zelf SQL te schrijven. `transactions.py` detecteert daarnaast generiek
> de transactiekolommen en geeft `Transaction`-objecten terug.

> ⚠️ **Naam van het bestand:** gebruik `data/fake.db`, **niet** `db.sqlite3` — die
> laatste staat in `.gitignore` en zou dus niet gedeeld worden via git.

### Zo werkt het
1. **`data/connection.py`** — `get_db()` geeft een SQLite-connectie waarvan de rijen via de
   kolomnaam te lezen zijn (`row["bedrag"]`). **`data/readers.py`** bouwt daarop en geeft
   kant-en-klare dicts per tabel terug.
2. **`signals/`** — de twee functie-makers werken elk in hun **eigen bestand**
   (bv. `recurring_expenses.py`, `home_purchase.py`). Aparte bestanden = geen merge-conflicten.
3. **`backend/export.py`** — roept automatisch alle signalen aan en schrijft per functie een
   JSON naar `output/`, die de website inleest.

### Een functie toevoegen
1. Kopieer `backend/signals/example.py` naar `backend/signals/<jouw_bestand>.py`.
2. Schrijf je functie: krijgt de connectie binnen, geeft een **JSON-serialiseerbare dict**
   terug.
3. Zet je functie in de lijst `FUNCTIONS` onderaan het bestand.

```python
from ..data.readers import load_abonnementen, reference_date

def slapende_abonnementen(conn: sqlite3.Connection) -> dict:
    reference = reference_date(conn)
    slapend = [
        a for a in load_abonnementen(conn)
        if a["actief"] and (a["laatste_gebruik"] is None
                            or (reference - a["laatste_gebruik"]).days >= 90)
    ]
    return {
        "title": "Slapend geldverlies",
        "message": f"{len(slapend)} slapende abonnementen.",
        "items": [{"klant_id": a["klant_id"], "naam": a["naam"], "bedrag": a["bedrag"]} for a in slapend],
    }

FUNCTIONS = [slapende_abonnementen]
```

### Runnen
```bash
# Alle signalen draaien en JSON wegschrijven
uv run python -m tectonic_hackaton_mang

# (equivalent, expliciet pad naar de export)
uv run python -m tectonic_hackaton_mang.backend.export
```
Dit schrijft `output/<bestand>__<functie>.json`, klaar om door de website gelezen te worden.

### Beschikbare functies

#### `find_recurring_expenses` — terugkerende uitgaven / abonnementen
`backend/signals/recurring_expenses.py` → output: `output/recurring_expenses__find_recurring_expenses.json`

Leest de echte **`abonnementen`**-tabel en geeft **per klant** een overzicht. Detecteert
ook **slapende abonnementen**: nog actief, maar al **≥ 90 dagen** niet gebruikt (of nooit).

```json
{
  "title": "Terugkerende uitgaven",
  "message": "131 abonnementen bij 50 klanten (36 slapend).",
  "source_table": "abonnementen",
  "reference_date": "2026-09-30",
  "count": 131,
  "customer_count": 50,
  "monthly_total": 2438.16,
  "yearly_total": 29257.92,
  "dormant_count": 36,
  "customers": [
    {
      "customer": 1,
      "customer_name": "Emma Peeters",
      "monthly_total": 85.94,
      "yearly_total": 1031.28,
      "monthly_count": 6,
      "yearly_count": 0,
      "dormant_count": 4,
      "dormant_monthly_total": 76.96,
      "subscriptions": [
        {
          "name": "Basic-Fit",
          "frequency": "monthly",
          "amount": 26.99,
          "currency": "EUR",
          "category": "sport",
          "active": true,
          "start_date": "2026-01-23",
          "last_used": "2026-04-03",
          "days_since_last_use": 180,
          "dormant": true,
          "monthly_cost": 26.99,
          "yearly_cost": 323.88
        }
      ]
    }
  ]
}
```

**Velden per abonnement**

| Veld | Betekenis |
| --- | --- |
| `name` | Naam van het abonnement |
| `frequency` | `"monthly"` of `"yearly"` |
| `amount` | Bedrag per betaling (zoals in de data) |
| `currency` | Valuta (voorlopig altijd `"EUR"`) |
| `category` | `streaming` / `sport` / `software` / `mobiliteit` / `overig` |
| `active` | Nog actief volgens de data |
| `start_date` | Startdatum van het abonnement |
| `last_used` | Laatste gebruik (`null` = nooit) |
| `days_since_last_use` | Dagen sinds laatste gebruik (`null` = nooit) |
| `dormant` | Slapend: actief maar ≥ 90 dagen ongebruikt |
| `monthly_cost` | Kost per maand (jaarlijks bedrag ÷ 12) |
| `yearly_cost` | Kost per jaar (maandelijks bedrag × 12) |

Per klant: `monthly_total` / `yearly_total` (enkel actieve abonnementen),
`monthly_count` / `yearly_count`, `dormant_count` en `dormant_monthly_total`.
De website leest `customers` en toont voor de ingelogde klant de lijst met
"stopzetten"-knop bij `dormant: true`.

#### `analyze_home_purchase` — spaar- en woonanalyse
`backend/signals/home_purchase.py` → output: `output/home_purchase__analyze_home_purchase.json`

Combineert de echte signalen om te bepalen of iemand best **begint te sparen** of een
**huis kan kopen**, en hoeveel die moet sparen. Bronnen: `klanten` (inkomen, spaardoel),
`transacties` (uitgaven + terugkerend inkomen), `abonnementen` + `verzekeringen` (vaste
kosten), `spaarrekening_interacties` (stortingen, saldo, 'bekeken') en `zoekopdrachten`
(interesse in wonen/sparen, bv. via Immoweb of Kate). **Elke klant krijgt een profiel.**

**Aannames** (bovenaan `home_purchase.py` aanpasbaar): woningprijs €300.000, 10% down
payment, 10% kosten, max. 40% schuldenlast, 3,5% rente, 25 jaar looptijd. Ze staan ook
in het veld `assumptions`.

```json
{
  "title": "Spaar- en woonanalyse",
  "message": "50 profiel(en) geanalyseerd.",
  "source_table": "klanten + transacties + abonnementen + spaarrekening_interacties",
  "reference_date": "2026-09-30",
  "assumptions": { "target_home_price": 300000.0, "down_payment_pct": 0.1, "closing_costs_pct": 0.1,
                   "max_debt_ratio": 0.4, "annual_interest_rate": 0.035, "loan_term_years": 25 },
  "count": 50,
  "profiles": [
    {
      "customer": 2,
      "customer_name": "Thomas Vermeulen",
      "signals": {
        "fixed_income": true,
        "monthly_income": 2650.0,
        "income_sources": [ { "name": "TechStart NV", "frequency": "monthly", "monthly_cost": 2650.0 } ],
        "monthly_expenses": 1442.34,
        "monthly_fixed_costs": 33.98,
        "subscriptions_monthly": 33.98,
        "insurance_monthly": 0,
        "savings_activity": { "deposit_count": 1, "deposit_months": 1, "deposit_total": 100.0,
                              "monthly_average": 8.33, "frequent": false, "views": 7,
                              "current_balance": 1850.0, "max_balance": 1900.0 },
        "savings_capacity": 1207.66,
        "positive_savings_capacity": true,
        "wants_house": true,
        "savings_goal": "huis",
        "personal_goal_amount": 25000.0,
        "housing_queries": ["spaarrekening huis kopen", "woonsparen KBC"],
        "saving_queries": ["spaarrekening huis kopen", "hoeveel sparen per maand", "woonsparen KBC", "spaardoel aanmaken", "rente spaarboekje"]
      },
      "advice": {
        "status": "on_track",
        "summary": "Je wil een woning en spaart ±€1.208/maand. Met je huidige spaargeld (±€1.850) is het doel van €25.000 bereikt in 20 maanden.",
        "target_home_price": 300000.0,
        "down_payment_required": 30000.0,
        "closing_costs": 30000.0,
        "start_capital_needed": 60000.0,
        "savings_target": 25000.0,
        "current_savings": 1850.0,
        "max_monthly_payment": 1060.0,
        "max_loan": 211735.94,
        "affordable_home_price": 235262.16,
        "gap_to_target": 64737.84,
        "effective_monthly_saving": 1207.66,
        "months_to_save": 20,
        "ready_date": "2028-05-01"
      }
    }
  ]
}
```

**`advice.status`** is één van:
`ready_to_buy` (kan doelwoning + down payment betalen), `on_track` (wil een huis en spaart),
`saving_for_goal` (spaart voor een ander doel, bv. vakantie of pensioen), `start_saving`
(kan sparen, geen concreet doel), `not_ready` (geen vast inkomen of negatieve capaciteit).

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
git clone https://github.com/F-3-R-R-3/Tectonic-Hackaton-Mang.git
cd Tectonic-Hackaton-Mang

# Backend: genereer de fake-dataset en draai de signalen → output/*.json
uv run python -m tectonic_hackaton_mang.backend.data.generate
uv run python -m tectonic_hackaton_mang

# Frontend (KBC-website)
cd src/tectonic_hackaton_mang/frontend
npm install
npm run dev
```

Installatietutorial vind je in [SETUP.md](SETUP.md).

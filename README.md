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

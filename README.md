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

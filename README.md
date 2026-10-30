# Credit Card Fraud Detection — ML + OCR + BI

Système intelligent de détection de fraude sur transactions financières combinant **machine learning**, **reconnaissance optique de caractères (OCR)** et **data visualisation interactive**.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?logo=flask)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-orange?logo=scikit-learn)
![Plotly](https://img.shields.io/badge/Plotly-5.18-3F4F75?logo=plotly)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Vue d'ensemble

Ce projet permet d'analyser une transaction financière de deux façons :
- **Manuellement** via un formulaire web
- **Automatiquement** depuis un reçu ou screenshot uploadé (OCR)

Le modèle **Random Forest** prédit en temps réel si la transaction est frauduleuse ou légitime. Toutes les prédictions sont loggées, exportables vers **Power BI**, et visualisables via un **rapport Plotly interactif**.

---

## Fonctionnalités

- Prédiction de fraude en temps réel
- **OCR** — scan de reçus/screenshots pour auto-remplir le formulaire
- **Dashboard web** intégré avec Chart.js (`/dashboard`)
- **Export CSV** pour Power BI (`/export`)
- **Endpoint JSON** pour outils BI tiers (`/api/stats`)
- **Rapport HTML interactif** généré avec Plotly (`generate_report.py`)
- Log automatique de chaque prédiction
- Déployable sur Heroku / Render / Railway

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| ML Model | Random Forest (scikit-learn) |
| OCR | Tesseract + pytesseract + OpenCV + Pillow |
| Backend | Flask 3.0 + Gunicorn |
| Data Viz | Plotly (rapport HTML) + Chart.js (dashboard web) |
| BI Export | CSV + JSON endpoint (compatible Power BI) |
| Frontend | HTML5 + Bootstrap 4 |

---

## Structure du projet

```
├── app.py                    # Flask app (predict, OCR, export, dashboard)
├── train_model.py            # Entraînement du modèle Random Forest
├── generate_report.py        # Génération rapport Plotly HTML
├── inspect_model.py          # Inspection du modèle
├── models/
│   ├── fraud_model.pkl       # Modèle entraîné
│   └── scaler.pkl            # StandardScaler
├── templates/
│   ├── index.html            # Interface principale + OCR upload
│   └── dashboard.html        # Dashboard live (Chart.js)
├── reports/
│   └── fraud_report.html     # Rapport BI interactif (généré)
├── data/
│   └── predictions_log.csv   # Log des prédictions (généré)
├── notebook/
│   └── fraud_detection_with_visualizations.ipynb
├── POWERBI_GUIDE.md          # Guide connexion Power BI
├── requirements.txt
└── Procfile
```

---

## Installation

### 1. Cloner le repo

```bash
git clone https://github.com/KodsLamouchi322/credit-card-fraud-detection-ml.git
cd credit-card-fraud-detection-ml
```

### 2. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 3. Installer Tesseract OCR (Windows)

Télécharger l'installeur : [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

Chemin par défaut : `C:\Program Files\Tesseract-OCR\tesseract.exe`

### 4. Lancer l'application

```bash
python app.py
```

Ouvrir `http://localhost:5000`

---

## Utilisation

### Prédiction manuelle
Remplis le formulaire avec les données de la transaction et clique **Analyze Transaction**.

### Prédiction par OCR
Upload un reçu ou screenshot contenant les données de transaction — les champs sont extraits automatiquement.

### Générer le rapport BI
```bash
python generate_report.py
```
Ouvre `reports/fraud_report.html` dans le navigateur.

### Connecter Power BI
- **Import CSV** : télécharge depuis `http://localhost:5000/export`
- **Connecteur Web live** : `http://localhost:5000/export`

Voir [POWERBI_GUIDE.md](POWERBI_GUIDE.md) pour le détail.

---

## Champs d'entrée

| Champ | Description |
|-------|-------------|
| `amount` | Montant de la transaction |
| `oldbalanceOrg` | Solde expéditeur avant |
| `newbalanceOrig` | Solde expéditeur après |
| `oldbalanceDest` | Solde destinataire avant |
| `newbalanceDest` | Solde destinataire après |
| `type` | PAYMENT · TRANSFER · CASH_OUT · DEPOSIT · CASH_IN |

---

## Rapport BI — Visuels inclus

- **5 KPI cards** — Total, Fraudes, Légitimes, Taux de fraude, Montant moyen fraude
- **Donut chart** — Répartition Fraude / Légitime
- **Barres empilées** — Fraudes par type de transaction
- **Scatter plot** — Montant vs Solde (coloré par résultat)
- **Timeline** — Évolution cumulative des transactions
- **Tableau** — 15 dernières transactions analysées

---

## Patterns de fraude détectés

Le modèle détecte principalement les fraudes sur **TRANSFER** et **CASH_OUT** avec :
- Compte source vidé entièrement (`newbalanceOrig = 0`)
- Montant = solde avant (`amount = oldbalanceOrg`)
- Solde destination suspect (`newbalanceDest = 0` ou = montant)

---

## Déploiement

```
web: gunicorn app:app
```

Compatible Heroku, Render, Railway. Voir [DEPLOYMENT.md](DEPLOYMENT.md).

---

## License

MIT License

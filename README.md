# Credit Card Fraud Detection — ML Web App

A machine learning web application that detects fraudulent financial transactions in real time, built with Python, scikit-learn, and Flask.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?logo=flask)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-orange?logo=scikit-learn)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Overview

This project trains a **Random Forest** classifier on financial transaction data to predict whether a transaction is fraudulent or legitimate. The trained model is served through a clean Flask web interface where users can input transaction details and get an instant prediction.

---

## Features

- Real-time fraud prediction via a web form
- Trained on a large financial transactions dataset
- Handles class imbalance with `class_weight='balanced'`
- Feature scaling with `StandardScaler`
- REST-ready `/predict` endpoint
- Deployable to Heroku / Render / Railway

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| ML Model | Random Forest (scikit-learn) |
| API / Backend | Flask 3.0 |
| Preprocessing | StandardScaler, NumPy, Pandas |
| Deployment | Gunicorn + Procfile |
| Notebook | Jupyter (visualizations) |

---

## Project Structure

```
├── app.py                  # Flask application
├── train_model.py          # Model training script
├── inspect_model.py        # Model inspection utility
├── models/
│   ├── fraud_model.pkl     # Trained Random Forest model
│   └── scaler.pkl          # Fitted StandardScaler
├── templates/
│   └── index.html          # Web interface
├── notebook/
│   └── fraud_detection_with_visualizations.ipynb
├── requirements.txt
└── Procfile                # For deployment
```

---

## Input Features

| Feature | Description |
|---------|-------------|
| `amount` | Transaction amount |
| `oldbalanceOrg` | Sender balance before transaction |
| `newbalanceOrig` | Sender balance after transaction |
| `oldbalanceDest` | Receiver balance before transaction |
| `newbalanceDest` | Receiver balance after transaction |
| `type` | Transaction type (PAYMENT, TRANSFER, CASH_OUT, DEPOSIT, CASH_IN) |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/KodsLamouchi322/credit-card-fraud-detection-ml.git
cd credit-card-fraud-detection-ml
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Train the model (optional — pre-trained model included)

```bash
python train_model.py
```

> Requires the dataset at `Data/AIML Dataset.csv`

### 4. Run the app

```bash
python app.py
```

Open your browser at `http://localhost:5000`

---

## Deployment

The project is ready for deployment on platforms like **Heroku**, **Render**, or **Railway** via the included `Procfile`:

```
web: gunicorn app:app
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## Model Performance

The model is evaluated using:
- Classification Report (Precision, Recall, F1-score)
- Confusion Matrix
- ROC AUC Score

Training details and visualizations are available in the [notebook](notebook/fraud_detection_with_visualizations.ipynb).

---

## License

This project is open source under the [MIT License](LICENSE).

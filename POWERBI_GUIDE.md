# Power BI Integration Guide

This guide explains how to connect Power BI to the Fraud Detection app.

---

## Method 1 — Import CSV (Offline)

1. Run the Flask app: `python app.py`
2. Make a few predictions at `http://localhost:5000`
3. Download the CSV: click **"Export CSV for Power BI"** on the homepage, or go to `http://localhost:5000/export`
4. Open **Power BI Desktop**
5. Click **Home → Get Data → Text/CSV**
6. Select the downloaded `fraud_predictions.csv`
7. Click **Load**

---

## Method 2 — Live Web Connector (Auto-refresh)

1. Run the Flask app: `python app.py`
2. Open **Power BI Desktop**
3. Click **Home → Get Data → Web**
4. Enter URL: `http://localhost:5000/export`
5. Click **OK → Load**
6. Set refresh interval: **Home → Refresh**

> For production, replace `localhost:5000` with your deployed URL (Heroku, Render, etc.)

---

## CSV Columns Reference

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | DateTime | When the prediction was made |
| `amount` | Decimal | Transaction amount |
| `oldbalanceOrg` | Decimal | Sender balance before transaction |
| `newbalanceOrig` | Decimal | Sender balance after transaction |
| `oldbalanceDest` | Decimal | Receiver balance before transaction |
| `newbalanceDest` | Decimal | Receiver balance after transaction |
| `type` | Text | PAYMENT / TRANSFER / CASH_OUT / DEPOSIT / CASH_IN |
| `prediction` | Integer | 0 = Legitimate, 1 = Fraudulent |
| `result` | Text | "Fraudulent" or "Not Fraudulent" |

---

## Recommended Visualizations in Power BI

### KPI Cards
- Total Transactions → `COUNT(prediction)`
- Total Fraudulent → `SUM(prediction)`
- Fraud Rate → `DIVIDE(SUM(prediction), COUNT(prediction))`

### Charts
| Chart Type | X-axis | Y-axis / Values |
|-----------|--------|-----------------|
| Donut Chart | `result` | Count of transactions |
| Stacked Bar | `type` | Count split by `result` |
| Line Chart | `timestamp` | Count of predictions over time |
| Scatter Plot | `amount` | `oldbalanceOrg` colored by `result` |
| Table | All columns | Filtered by `prediction = 1` |

### Suggested DAX Measures
```dax
Fraud Rate % = DIVIDE(SUM(fraud_predictions[prediction]), COUNT(fraud_predictions[prediction])) * 100

Avg Fraud Amount = CALCULATE(AVERAGE(fraud_predictions[amount]), fraud_predictions[prediction] = 1)

Total Fraudulent = CALCULATE(COUNT(fraud_predictions[prediction]), fraud_predictions[prediction] = 1)
```

---

## Built-in Web Dashboard

The app also includes a built-in analytics dashboard (no Power BI needed):

```
http://localhost:5000/dashboard
```

Features:
- KPI cards (Total, Fraudulent, Legitimate, Fraud Rate)
- Donut chart (Fraud vs Legitimate)
- Stacked bar chart by transaction type
- Recent predictions table

from flask import Flask, render_template, request, jsonify, send_file, Response
import joblib
import numpy as np
import pandas as pd
import os
import csv
from datetime import datetime
from io import StringIO

app = Flask(__name__)

# Charger le modèle pré-entraîné
model = joblib.load('models/fraud_model.pkl')
scaler = joblib.load('models/scaler.pkl')

# Fichier de log des prédictions
PREDICTIONS_LOG = 'data/predictions_log.csv'
LOG_HEADERS = ['timestamp', 'amount', 'oldbalanceOrg', 'newbalanceOrig',
               'oldbalanceDest', 'newbalanceDest', 'type', 'prediction', 'result']

def ensure_log_file():
    """Crée le fichier de log s'il n'existe pas."""
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(PREDICTIONS_LOG):
        with open(PREDICTIONS_LOG, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(LOG_HEADERS)

def log_prediction(amount, oldbalanceOrg, newbalanceOrig, oldbalanceDest,
                   newbalanceDest, transaction_type, prediction, result):
    """Enregistre chaque prédiction dans le fichier CSV."""
    ensure_log_file()
    with open(PREDICTIONS_LOG, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            amount, oldbalanceOrg, newbalanceOrig,
            oldbalanceDest, newbalanceDest,
            transaction_type, int(prediction), result
        ])

def get_stats():
    """Calcule les statistiques pour le dashboard."""
    ensure_log_file()
    try:
        df = pd.read_csv(PREDICTIONS_LOG)
        if df.empty:
            return None
        total = len(df)
        fraudulent = int(df['prediction'].sum())
        legitimate = total - fraudulent
        fraud_rate = round((fraudulent / total) * 100, 1) if total > 0 else 0
        by_type = df.groupby('type')['prediction'].agg(['count', 'sum']).reset_index()
        by_type.columns = ['type', 'total', 'fraudulent']
        by_type['fraud_rate'] = (by_type['fraudulent'] / by_type['total'] * 100).round(1)
        recent = df.tail(10).to_dict('records')
        return {
            'total': total,
            'fraudulent': fraudulent,
            'legitimate': legitimate,
            'fraud_rate': fraud_rate,
            'by_type': by_type.to_dict('records'),
            'recent': recent
        }
    except Exception:
        return None

@app.route('/')
def home():
    stats = get_stats()
    return render_template('index.html', stats=stats)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        amount = float(request.form['amount'])
        oldbalanceOrg = float(request.form['oldbalanceOrg'])
        newbalanceOrig = float(request.form['newbalanceOrig'])
        oldbalanceDest = float(request.form['oldbalanceDest'])
        newbalanceDest = float(request.form['newbalanceDest'])
        transaction_type = request.form['type']

        transaction_type_encoded = encode_transaction_type(transaction_type)
        features = np.array([[amount, oldbalanceOrg, newbalanceOrig,
                               oldbalanceDest, newbalanceDest, transaction_type_encoded]])
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]

        result = 'Fraudulent' if prediction == 1 else 'Not Fraudulent'

        # Log la prédiction pour Power BI
        log_prediction(amount, oldbalanceOrg, newbalanceOrig,
                       oldbalanceDest, newbalanceDest,
                       transaction_type, prediction, result)

        stats = get_stats()
        return render_template('index.html',
                               prediction_text=f'The transaction is: {result}',
                               prediction_class='danger' if prediction == 1 else 'success',
                               stats=stats)

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/export')
def export_csv():
    """Télécharge le CSV des prédictions — à connecter dans Power BI."""
    ensure_log_file()
    try:
        df = pd.read_csv(PREDICTIONS_LOG)
        output = StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=fraud_predictions.csv',
                'Access-Control-Allow-Origin': '*'
            }
        )
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/stats')
def api_stats():
    """Endpoint JSON pour Power BI ou tout autre outil BI."""
    stats = get_stats()
    if stats:
        return jsonify(stats)
    return jsonify({'message': 'No predictions yet', 'total': 0})

@app.route('/dashboard')
def dashboard():
    """Page dashboard avec visualisations intégrées."""
    stats = get_stats()
    return render_template('dashboard.html', stats=stats)

def encode_transaction_type(transaction_type):
    types = {'PAYMENT': 0, 'TRANSFER': 1, 'CASH_OUT': 2, 'DEPOSIT': 3, 'CASH_IN': 4}
    return types.get(transaction_type, 0)

if __name__ == '__main__':
    ensure_log_file()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

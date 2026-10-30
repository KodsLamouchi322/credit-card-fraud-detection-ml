from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Charger le modèle pré-entraîné
model = joblib.load('models/fraud_model.pkl')
scaler = joblib.load('models/scaler.pkl')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Récupérer les données envoyées par le formulaire
    try:
        amount = float(request.form['amount'])
        oldbalanceOrg = float(request.form['oldbalanceOrg'])
        newbalanceOrig = float(request.form['newbalanceOrig'])
        oldbalanceDest = float(request.form['oldbalanceDest'])
        newbalanceDest = float(request.form['newbalanceDest'])
        transaction_type = request.form['type']

        # Préparer les données pour la prédiction
        transaction_type_encoded = encode_transaction_type(transaction_type)
        features = np.array([[amount, oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest, transaction_type_encoded]])

        # Normaliser les données
        features_scaled = scaler.transform(features)

        # Faire la prédiction
        prediction = model.predict(features_scaled)

        result = 'Fraudulent' if prediction == 1 else 'Not Fraudulent'

        return render_template('index.html', prediction_text=f'The transaction is: {result}')

    except Exception as e:
        return jsonify({'error': str(e)})

def encode_transaction_type(transaction_type):
    # Encode the transaction type manually or using a predefined dictionary
    types = {'PAYMENT': 0, 'TRANSFER': 1, 'CASH_OUT': 2, 'DEPOSIT': 3, 'CASH_IN': 4}
    return types.get(transaction_type, 0)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

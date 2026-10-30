from flask import Flask, render_template, request, jsonify, send_file, Response
import joblib
import numpy as np
import pandas as pd
import os
import csv
import re
from datetime import datetime
from io import StringIO

# OCR imports
import pytesseract
from PIL import Image
import cv2

app = Flask(__name__)

# Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Charger le modèle pré-entraîné
model = joblib.load('models/fraud_model.pkl')
scaler = joblib.load('models/scaler.pkl')

# Fichier de log des prédictions
PREDICTIONS_LOG = 'data/predictions_log.csv'
LOG_HEADERS = ['timestamp', 'amount', 'oldbalanceOrg', 'newbalanceOrig',
               'oldbalanceDest', 'newbalanceDest', 'type', 'prediction', 'result']

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_log_file():
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(PREDICTIONS_LOG):
        with open(PREDICTIONS_LOG, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(LOG_HEADERS)

def log_prediction(amount, oldbalanceOrg, newbalanceOrig, oldbalanceDest,
                   newbalanceDest, transaction_type, prediction, result):
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

def encode_transaction_type(transaction_type):
    types = {'PAYMENT': 0, 'TRANSFER': 1, 'CASH_OUT': 2, 'DEPOSIT': 3, 'CASH_IN': 4}
    return types.get(transaction_type.upper(), 0)

# ─────────────────────────────────────────────
# OCR — Image preprocessing & field extraction
# ─────────────────────────────────────────────

def preprocess_image(image_path):
    """Améliore l'image pour maximiser la précision OCR."""
    img = cv2.imread(image_path)
    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Agrandissement x2 (améliore la lecture des petits caractères)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    # Réduction du bruit
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    # Binarisation adaptative
    gray = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 2
    )
    return gray

def extract_fields_from_text(text):
    """
    Tente d'extraire les champs financiers depuis le texte OCR brut.
    Fonctionne sur des reçus, relevés, screenshots de transactions.
    """
    text_upper = text.upper()
    fields = {
        'amount': '',
        'oldbalanceOrg': '',
        'newbalanceOrig': '',
        'oldbalanceDest': '',
        'newbalanceDest': '',
        'type': ''
    }

    # ── Montant principal ──────────────────────────────────────────
    # Ex: "Amount: 1500.00" / "Total: $1,500.00" / "AMOUNT 1500"
    amount_patterns = [
        r'(?:AMOUNT|TOTAL|MONTANT|AMT)[^\d]*(\d[\d,\.]+)',
        r'\$\s*(\d[\d,\.]+)',
        r'(?:USD|EUR)\s*(\d[\d,\.]+)',
    ]
    for pat in amount_patterns:
        m = re.search(pat, text_upper)
        if m:
            fields['amount'] = m.group(1).replace(',', '')
            break

    # ── Solde avant (expéditeur) ───────────────────────────────────
    # Ex: "Old Balance: 5000" / "Balance Before: 5000" / "Prev Balance"
    old_orig_patterns = [
        r'(?:OLD\s*BAL(?:ANCE)?|BALANCE\s*BEFORE|PREV(?:IOUS)?\s*BAL(?:ANCE)?|SOLDE\s*AVANT)[^\d]*(\d[\d,\.]+)',
        r'(?:ORIGIN|FROM|SOURCE)[^\d]*OLD[^\d]*(\d[\d,\.]+)',
    ]
    for pat in old_orig_patterns:
        m = re.search(pat, text_upper)
        if m:
            fields['oldbalanceOrg'] = m.group(1).replace(',', '')
            break

    # ── Solde après (expéditeur) ───────────────────────────────────
    new_orig_patterns = [
        r'(?:NEW\s*BAL(?:ANCE)?|BALANCE\s*AFTER|SOLDE\s*APR[EÈ]S|UPDATED\s*BAL(?:ANCE)?)[^\d]*(\d[\d,\.]+)',
        r'(?:AVAILABLE|REMAINING)\s*BAL(?:ANCE)?[^\d]*(\d[\d,\.]+)',
    ]
    for pat in new_orig_patterns:
        m = re.search(pat, text_upper)
        if m:
            fields['newbalanceOrig'] = m.group(1).replace(',', '')
            break

    # ── Soldes destinataire ────────────────────────────────────────
    dest_old_patterns = [
        r'(?:DEST(?:INATION)?\s*OLD|RECIPIENT\s*PREV|BENEFI\w*\s*BAL(?:ANCE)?)[^\d]*(\d[\d,\.]+)',
    ]
    for pat in dest_old_patterns:
        m = re.search(pat, text_upper)
        if m:
            fields['oldbalanceDest'] = m.group(1).replace(',', '')
            break

    dest_new_patterns = [
        r'(?:DEST(?:INATION)?\s*NEW|RECIPIENT\s*NEW|TO\s*BAL(?:ANCE)?)[^\d]*(\d[\d,\.]+)',
    ]
    for pat in dest_new_patterns:
        m = re.search(pat, text_upper)
        if m:
            fields['newbalanceDest'] = m.group(1).replace(',', '')
            break

    # ── Type de transaction ────────────────────────────────────────
    type_keywords = ['CASH_OUT', 'CASH OUT', 'CASHOUT',
                     'TRANSFER', 'PAYMENT', 'CASH_IN', 'CASH IN', 'DEPOSIT']
    type_map = {
        'CASH_OUT': 'CASH_OUT', 'CASH OUT': 'CASH_OUT', 'CASHOUT': 'CASH_OUT',
        'TRANSFER': 'TRANSFER',
        'PAYMENT': 'PAYMENT',
        'CASH_IN': 'CASH_IN', 'CASH IN': 'CASH_IN',
        'DEPOSIT': 'DEPOSIT'
    }
    for kw in type_keywords:
        if kw in text_upper:
            fields['type'] = type_map[kw]
            break

    return fields

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

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

@app.route('/ocr', methods=['POST'])
def ocr_upload():
    """
    Reçoit une image, extrait les champs via OCR,
    et retourne le formulaire pré-rempli pour validation.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file. Allowed: png, jpg, jpeg, bmp, tiff, webp'}), 400

    try:
        os.makedirs('data/uploads', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ocr_{timestamp}_{file.filename}"
        image_path = os.path.join('data/uploads', filename)
        file.save(image_path)

        # Prétraitement + OCR
        preprocessed = preprocess_image(image_path)
        ocr_text = pytesseract.image_to_string(
            preprocessed,
            config='--psm 6 --oem 3'  # psm 6 = bloc de texte uniforme
        )

        # Extraction des champs
        fields = extract_fields_from_text(ocr_text)

        # Nettoyage du fichier uploadé
        os.remove(image_path)

        stats = get_stats()
        return render_template('index.html',
                               ocr_fields=fields,
                               ocr_text=ocr_text.strip(),
                               ocr_success=True,
                               stats=stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export')
def export_csv():
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
    stats = get_stats()
    if stats:
        return jsonify(stats)
    return jsonify({'message': 'No predictions yet', 'total': 0})

@app.route('/dashboard')
def dashboard():
    stats = get_stats()
    return render_template('dashboard.html', stats=stats)

if __name__ == '__main__':
    ensure_log_file()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

"""
Script to train the fraud detection model and save it for the Flask application.
This script uses a subset of features that match what the Flask app expects.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
import os

print("Loading dataset...")
# Load the dataset
df = pd.read_csv('Data/AIML Dataset.csv')

print(f"Dataset loaded: {len(df)} rows")
print(f"Columns: {df.columns.tolist()}")

# Data cleaning
print("\nCleaning data...")
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.fillna(df.median(numeric_only=True), inplace=True)

# Encode transaction type
print("Encoding transaction types...")
type_mapping = {'PAYMENT': 0, 'TRANSFER': 1, 'CASH_OUT': 2, 'DEBIT': 3, 'CASH_IN': 4}
df['type_encoded'] = df['type'].map(type_mapping)

# Handle any unmapped types
if df['type_encoded'].isnull().any():
    print("Warning: Some transaction types were not mapped. Filling with 0.")
    df['type_encoded'].fillna(0, inplace=True)

# Select features that match what the Flask app expects
# Features: amount, oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest, type
feature_columns = ['amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest', 'type_encoded']
X = df[feature_columns]
y = df['isFraud']

print(f"\nFeatures shape: {X.shape}")
print(f"Target distribution:\n{y.value_counts()}")

# Split the data
print("\nSplitting data into train and test sets...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Scale the features
print("Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Random Forest model
print("\nTraining Random Forest model...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'  # Handle imbalanced data
)
model.fit(X_train_scaled, y_train)

# Evaluate the model
print("\nEvaluating model...")
y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

roc_auc = roc_auc_score(y_test, y_pred_proba)
print(f"\nROC AUC Score: {roc_auc:.4f}")

# Create models directory if it doesn't exist
print("\nSaving models...")
os.makedirs('models', exist_ok=True)

# Save the model and scaler
joblib.dump(model, 'models/fraud_model.pkl')
joblib.dump(scaler, 'models/scaler.pkl')

print("\n✓ Model saved to 'models/fraud_model.pkl'")
print("✓ Scaler saved to 'models/scaler.pkl'")
print("\nTraining complete! You can now run the Flask application with 'python app.py'")

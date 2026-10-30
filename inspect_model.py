"""
Script to inspect the trained fraud detection model
"""
import joblib
import numpy as np

print("=" * 60)
print("FRAUD DETECTION MODEL INSPECTION")
print("=" * 60)

# Load the model and scaler
print("\n📂 Loading model and scaler...")
model = joblib.load('models/fraud_model.pkl')
scaler = joblib.load('models/scaler.pkl')

print("✓ Model and scaler loaded successfully!\n")

# Model information
print("=" * 60)
print("MODEL INFORMATION")
print("=" * 60)
print(f"Model Type: {type(model).__name__}")
print(f"Number of estimators (trees): {model.n_estimators}")
print(f"Max depth: {model.max_depth}")
print(f"Number of features: {model.n_features_in_}")
print(f"Number of classes: {model.n_classes_}")
print(f"Classes: {model.classes_}")

# Feature importance
print("\n" + "=" * 60)
print("FEATURE IMPORTANCE")
print("=" * 60)
feature_names = ['amount', 'oldbalanceOrg', 'newbalanceOrig', 
                 'oldbalanceDest', 'newbalanceDest', 'type_encoded']

importances = model.feature_importances_
indices = np.argsort(importances)[::-1]

print("\nFeatures ranked by importance:")
for i, idx in enumerate(indices, 1):
    print(f"{i}. {feature_names[idx]:20s} : {importances[idx]:.4f} ({importances[idx]*100:.2f}%)")

# Scaler information
print("\n" + "=" * 60)
print("SCALER INFORMATION")
print("=" * 60)
print(f"Scaler Type: {type(scaler).__name__}")
print(f"Number of features: {scaler.n_features_in_}")
print(f"\nMean values used for scaling:")
for i, (name, mean) in enumerate(zip(feature_names, scaler.mean_)):
    print(f"  {name:20s} : {mean:.2f}")

print(f"\nStandard deviation values used for scaling:")
for i, (name, scale) in enumerate(zip(feature_names, scaler.scale_)):
    print(f"  {name:20s} : {scale:.2f}")

# Model parameters
print("\n" + "=" * 60)
print("ALL MODEL PARAMETERS")
print("=" * 60)
for param, value in model.get_params().items():
    print(f"{param:25s} : {value}")

print("\n" + "=" * 60)
print("INSPECTION COMPLETE")
print("=" * 60)

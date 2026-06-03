#!/usr/bin/env python
"""Ultra-fast model saving - minimal dependencies"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

print("🔨 Training model...")

# Load data
df = pd.read_pickle("data/interim/03_data_features.pkl")
print(f"✓ Loaded {len(df)} samples")

# Get features and label
exclude = ['label', 'category', 'participant', 'set', 'duration']
features = [c for c in df.columns if c not in exclude and df[c].dtype in [np.float64, np.int64]]
X = df[features].fillna(0)
y = df['label']

print(f"✓ Features: {len(features)}")
print(f"✓ Classes: {sorted(y.unique())}")

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

# Train
model = RandomForestClassifier(n_estimators=50, max_depth=15, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# Scores
print(f"✓ Train accuracy: {model.score(X_train, y_train):.4f}")
print(f"✓ Test accuracy: {model.score(X_test, y_test):.4f}")

# Save
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/trained_model.pkl")
print(f"✓ Model saved!")
print(f"✓ Size: {os.path.getsize('models/trained_model.pkl')/(1024*1024):.1f}MB")
print("\n✅ READY! Run: python app.py")

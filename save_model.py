#!/usr/bin/env python
"""
Model training and saving script - SIMPLIFIED VERSION
Run this FIRST before deploying
"""

import os
import sys
import joblib
from pathlib import Path

print("=" * 60)
print("🏋️  Exercise Detector - Model Training & Saving")
print("=" * 60)

try:
    # Check if model path exists
    model_dir = Path(__file__).parent / 'models'
    model_dir.mkdir(exist_ok=True)
    
    print("\n📍 Step 1: Loading training data...")
    import pandas as pd
    
    df = pd.read_pickle("data/interim/03_data_features.pkl")
    print(f"   ✓ Loaded {len(df)} training samples")
    
    print("\n📍 Step 2: Preparing features and labels...")
    
    # Define features (simplified - use all numeric columns except label)
    all_columns = df.columns.tolist()
    exclude_cols = ['label', 'category', 'participant', 'set', 'duration']
    features = [col for col in all_columns if col not in exclude_cols]
    
    X = df[features]
    y = df['label']
    print(f"   ✓ Features: {len(features)}")
    print(f"   ✓ Classes: {sorted(y.unique())}")
    print(f"   ✓ Data shape: {X.shape}")
    
    print("\n📍 Step 3: Splitting data...")
    from sklearn.model_selection import train_test_split
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    print(f"   ✓ Training set: {len(X_train)}")
    print(f"   ✓ Test set: {len(X_test)}")
    
    print("\n📍 Step 4: Training model...")
    from sklearn.ensemble import RandomForestClassifier
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    model.fit(X_train, y_train)
    
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"   ✓ Training accuracy: {train_score:.4f}")
    print(f"   ✓ Test accuracy: {test_score:.4f}")
    
    print("\n📍 Step 5: Saving model...")
    model_path = model_dir / 'trained_model.pkl'
    joblib.dump(model, str(model_path))
    model_size = os.path.getsize(model_path) / (1024*1024)
    print(f"   ✓ Model saved to: {model_path}")
    print(f"   ✓ Model size: {model_size:.2f} MB")
    
    print("\n" + "=" * 60)
    print("✅ MODEL READY FOR DEPLOYMENT!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. pip install -r requirements-deploy.txt")
    print("2. python app.py")
    print("3. Visit http://localhost:5000")
    print("=" * 60)

except FileNotFoundError as e:
    print(f"\n❌ ERROR: {e}")
    print("\nMake sure you've run the complete data pipeline:")
    print("1. src/data/make_dataset.py")
    print("2. src/features/build_features.py")
    print("3. src/features/remove_outliers.py")
    print("\nData should be at: data/interim/03_data_features.pkl")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

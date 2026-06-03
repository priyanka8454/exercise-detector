import pandas as pd

# Load training features
df = pd.read_pickle("data/interim/03_data_features.pkl")

# Get features used for training (exclude metadata and label)
exclude_cols = ['participant', 'label', 'category', 'set', 'duration', 'cluster']
feature_cols = [col for col in df.columns if col not in exclude_cols]

# Take first sample from each exercise class
sample_df = pd.DataFrame()
for label in df['label'].unique():
    class_data = df[df['label'] == label][feature_cols].head(1)
    sample_df = pd.concat([sample_df, class_data])

sample_df.to_csv("sample_with_features.csv", index=False)
print(f"✓ Created sample_with_features.csv with {len(sample_df)} rows and {len(feature_cols)} features")

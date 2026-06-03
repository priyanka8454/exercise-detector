import pandas as pd

# Load training features
df = pd.read_pickle("data/interim/03_data_features.pkl")
print("Shape:", df.shape)
print("\nColumn names:")
cols = df.columns.tolist()
print(cols)
print(f"\nTotal features: {len(cols)}")

# Export first row as CSV sample
sample = df.iloc[0:1].copy()
sample_dict = sample.to_dict(orient='list')
sample.to_csv("sample_processed_features.csv", index=False)
print("\n✓ Sample exported to sample_processed_features.csv")

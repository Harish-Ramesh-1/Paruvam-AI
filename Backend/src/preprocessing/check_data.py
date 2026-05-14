import pandas as pd

# Load final dataset
df = pd.read_csv(
    "src/data/processed/final.csv"
)

# =========================
# BASIC INFO
# =========================

print(df.head())

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nData Types:")
print(df.dtypes)

print("\nStatistics:")
print(df.describe())
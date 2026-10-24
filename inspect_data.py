
from pathlib import Path
import pandas as pd

data_dir = Path("challenge_data")

readings = pd.read_csv(data_dir / "vm_cpu_readings.csv.gz")
metadata = pd.read_csv(data_dir / "vm_metadata.csv.gz")

print("\n=== DATASET SHAPES ===")
print("Readings:", readings.shape)
print("Metadata:", metadata.shape)

print("\n=== MISSING VALUES ===")
print(readings.isna().sum())

print("\n=== DUPLICATES ===")
print("Duplicate VM/timestamp pairs:",
      readings.duplicated(["vm_id", "timestamp"]).sum())
print("Duplicate metadata VM IDs:",
      metadata["vm_id"].duplicated().sum())

print("\n=== TIME COVERAGE ===")
times = sorted(readings["timestamp"].unique())
print("Unique VMs:", readings["vm_id"].nunique())
print("Unique timestamps:", len(times))
print("First timestamp:", times[0])
print("Last timestamp:", times[-1])
print("First timestamp gaps:", pd.Series(times).diff().dropna().head(10).tolist())

print("\n=== CPU SUMMARY ===")
print(readings[["min_cpu", "avg_cpu", "max_cpu"]].describe())

print("\n=== METADATA CATEGORIES ===")
print(metadata["vm_category"].value_counts(dropna=False))
print("Metadata VM count:", metadata["vm_id"].nunique())

print("\n=== VM COUNT PER TIMESTAMP ===")
print(readings.groupby("timestamp")["vm_id"].nunique().describe())

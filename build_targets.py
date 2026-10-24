
from pathlib import Path
import pandas as pd

data_dir = Path("challenge_data")
output_dir = Path("reports")
output_dir.mkdir(exist_ok=True)

readings = pd.read_csv(data_dir / "vm_cpu_readings.csv.gz")

# Aggregate the VM-level observations at each timestamp.
targets = (
    readings.groupby("timestamp", as_index=False)
    .agg(
        active_vm_count=("vm_id", "nunique"),
        aggregate_cpu_utilization=("avg_cpu", "mean"),
    )
    .sort_values("timestamp")
    .reset_index(drop=True)
)

# Apply the required chronological split.
train = targets.iloc[:110].copy()
holdout = targets.iloc[110:].copy()

print("Target series shape:", targets.shape)
print("\nFirst five rows:")
print(targets.head().to_string(index=False))

print("\nLast five rows:")
print(targets.tail().to_string(index=False))

print("\nTraining timestamps:", len(train))
print("Holdout timestamps:", len(holdout))
print("Training ends at:", train["timestamp"].iloc[-1])
print("Holdout starts at:", holdout["timestamp"].iloc[0])
print("Holdout ends at:", holdout["timestamp"].iloc[-1])

print("\nTarget summary:")
print(targets[["active_vm_count", "aggregate_cpu_utilization"]].describe())

# Save the target series for reproducible analysis.
targets.to_csv(output_dir / "target_series.csv", index=False)
print("\nSaved reports/target_series.csv")

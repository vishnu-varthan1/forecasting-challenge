
import pandas as pd

targets = pd.read_csv("reports/target_series.csv")

train = targets.iloc[:110].copy()
holdout = targets.iloc[110:].copy()

assert len(train) == 110
assert len(holdout) == 24


last_active_count = float(train["active_vm_count"].iloc[-1])
last_cpu = float(train["aggregate_cpu_utilization"].iloc[-1])

predictions = pd.DataFrame({
    "timestamp": holdout["timestamp"].astype(int),
    "active_vm_count": [max(0, last_active_count)] * 24,
    "aggregate_cpu_utilization": [
        min(100.0, max(0.0, last_cpu))
    ] * 24,
})


assert list(predictions.columns) == [
    "timestamp",
    "active_vm_count",
    "aggregate_cpu_utilization",
]
assert len(predictions) == 24
assert predictions["timestamp"].is_monotonic_increasing
assert predictions["timestamp"].is_unique
assert predictions.select_dtypes("number").notna().all().all()
assert (predictions["active_vm_count"] >= 0).all()
assert predictions["aggregate_cpu_utilization"].between(0, 100).all()

predictions.to_csv("predictions.csv", index=False)

print("Created predictions.csv")
print(predictions.head())
print("\nRows:", len(predictions))
print("Timestamp range:",
      predictions["timestamp"].iloc[0],
      "to",
      predictions["timestamp"].iloc[-1])


import numpy as np
import pandas as pd

targets = pd.read_csv("reports/target_series.csv")
train = targets.iloc[:110].reset_index(drop=True)

SPLITS = [(62, 12), (74, 12), (86, 12), (98, 12)]
TARGETS = ["active_vm_count", "aggregate_cpu_utilization"]


def forecast(history, target, horizon, method):
    y = history[target].to_numpy(dtype=float)

    if method == "persistence":
        return np.full(horizon, y[-1])

    if method == "linear_trend":
        x = np.arange(len(y), dtype=float)
        slope, intercept = np.polyfit(x, y, 1)
        future_x = np.arange(len(y), len(y) + horizon, dtype=float)
        return intercept + slope * future_x

    raise ValueError(f"Unknown method: {method}")


def metrics(actual, predicted):
    error = np.asarray(actual) - np.asarray(predicted)
    return {
        "MAE": np.mean(np.abs(error)),
        "RMSE": np.sqrt(np.mean(error**2)),
    }


rows = []

for split, (end, horizon) in enumerate(SPLITS, start=1):
    history = train.iloc[:end]
    validation = train.iloc[end:end + horizon]

    for target in TARGETS:
        for method in ["persistence", "linear_trend"]:
            prediction = forecast(history, target, horizon, method)

            
            if target == "active_vm_count":
                prediction = np.maximum(0, prediction)
            else:
                prediction = np.clip(prediction, 0, 100)

            rows.append({
                "split": split,
                "target": target,
                "model": method,
                **metrics(validation[target].to_numpy(), prediction),
            })

results = pd.DataFrame(rows)

print("\n=== PER-SPLIT RESULTS ===")
print(results.to_string(index=False))

summary = (
    results.groupby(["target", "model"])[["MAE", "RMSE"]]
    .mean()
    .reset_index()
)

print("\n=== MEAN VALIDATION RESULTS ===")
print(summary.to_string(index=False))

results.to_csv("reports/trend_validation_results.csv", index=False)
summary.to_csv("reports/trend_validation_summary.csv", index=False)

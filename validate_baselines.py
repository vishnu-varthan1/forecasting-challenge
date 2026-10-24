
import numpy as np
import pandas as pd

targets = pd.read_csv("reports/target_series.csv")
train = targets.iloc[:110].reset_index(drop=True)

TARGETS = ["active_vm_count", "aggregate_cpu_utilization"]


SPLITS = [
    (62, 12),
    (74, 12),
    (86, 12),
    (98, 12),
]


def persistence_forecast(history, target, horizon):
    return np.repeat(float(history[target].iloc[-1]), horizon)


def moving_average_forecast(history, target, horizon, window=12):
    recent = history[target].astype(float).tail(window)
    return np.repeat(float(recent.mean()), horizon)


def calculate_metrics(actual, predicted):
    error = np.asarray(actual, dtype=float) - np.asarray(predicted, dtype=float)
    return {
        "MAE": float(np.mean(np.abs(error))),
        "RMSE": float(np.sqrt(np.mean(error**2))),
    }


results = []

for split_number, (train_end, horizon) in enumerate(SPLITS, start=1):
    history = train.iloc[:train_end]
    validation = train.iloc[train_end:train_end + horizon]

    for target in TARGETS:
        actual = validation[target].to_numpy()

        forecasts = {
            "persistence": persistence_forecast(
                history, target, horizon
            ),
            "moving_average_12": moving_average_forecast(
                history, target, horizon
            ),
        }

        for model_name, prediction in forecasts.items():
            results.append({
                "split": split_number,
                "train_rows": len(history),
                "validation_rows": len(validation),
                "target": target,
                "model": model_name,
                **calculate_metrics(actual, prediction),
            })

results = pd.DataFrame(results)

print("\n=== PER-SPLIT VALIDATION RESULTS ===")
print(results.to_string(index=False))

print("\n=== MEAN VALIDATION METRICS ===")
summary = (
    results.groupby(["target", "model"])[["MAE", "RMSE"]]
    .mean()
    .reset_index()
)
print(summary.to_string(index=False))

results.to_csv("reports/validation_results.csv", index=False)
summary.to_csv("reports/validation_summary.csv", index=False)

print("\nSaved validation results under reports/")

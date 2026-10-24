
from pathlib import Path

import numpy as np
import pandas as pd

targets = pd.read_csv("reports/target_series.csv")

train = targets.iloc[:110].copy()
holdout = targets.iloc[110:].copy()

TARGETS = ["active_vm_count", "aggregate_cpu_utilization"]


def persistence_forecast(train, horizon, target):
    """Repeat the last training observation."""
    return np.repeat(float(train[target].iloc[-1]), horizon)


def moving_average_forecast(train, horizon, target, window=12):
    """Repeat the mean of the last 12 training observations."""
    history = train[target].astype(float).tail(window)
    return np.repeat(float(history.mean()), horizon)


def metrics(actual, predicted):
    error = np.asarray(actual, dtype=float) - np.asarray(predicted, dtype=float)
    return {
        "MAE": np.mean(np.abs(error)),
        "RMSE": np.sqrt(np.mean(error**2)),
    }


results = []

for target in TARGETS:
    actual = holdout[target].to_numpy()

    forecasts = {
        "persistence": persistence_forecast(
            train, len(holdout), target
        ),
        "moving_average_12": moving_average_forecast(
            train, len(holdout), target
        ),
    }

    for model_name, predicted in forecasts.items():
        row = {
            "target": target,
            "model": model_name,
            **metrics(actual, predicted),
        }
        results.append(row)

results = pd.DataFrame(results)
print("\n=== HOLDOUT BASELINE RESULTS ===")
print(results.to_string(index=False))

print(
    "\nNote: these scores are diagnostic only. "
    "Do not select or tune the final model using the holdout."
)


Path("reports").mkdir(exist_ok=True)
results.to_csv("reports/holdout_baseline_diagnostics.csv", index=False)

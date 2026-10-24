
import numpy as np
import pandas as pd

targets = pd.read_csv("reports/target_series.csv")
predictions = pd.read_csv("predictions.csv")


actual = targets.iloc[110:].copy()

assert len(actual) == 24
assert len(predictions) == 24
assert predictions["timestamp"].tolist() == (
    actual["timestamp"].astype(int).tolist()
)

def calculate_metrics(y_true, y_pred):
    error = np.asarray(y_true, dtype=float) - np.asarray(y_pred, dtype=float)
    return {
        "MAE": np.mean(np.abs(error)),
        "RMSE": np.sqrt(np.mean(error ** 2)),
    }

for target in ["active_vm_count", "aggregate_cpu_utilization"]:
    scores = calculate_metrics(
        actual[target],
        predictions[target],
    )
    print(
        f"{target}: "
        f"MAE={scores['MAE']:.6f}, "
        f"RMSE={scores['RMSE']:.6f}"
    )

print("\nFinal evaluation completed. Model selection remains unchanged.")

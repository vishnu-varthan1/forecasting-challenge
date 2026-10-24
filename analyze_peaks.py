
import numpy as np
import pandas as pd

targets = pd.read_csv("reports/target_series.csv")
predictions = pd.read_csv("predictions.csv")

train = targets.iloc[:110]
actual = targets.iloc[110:].copy()

# Define peak CPU using the 90th percentile of training observations.
peak_threshold = train["aggregate_cpu_utilization"].quantile(0.90)

evaluation = actual[
    ["timestamp", "aggregate_cpu_utilization"]
].merge(
    predictions[
        ["timestamp", "aggregate_cpu_utilization"]
    ],
    on="timestamp",
    suffixes=("_actual", "_predicted"),
    validate="one_to_one",
)

evaluation["absolute_error"] = (
    evaluation["aggregate_cpu_utilization_actual"]
    - evaluation["aggregate_cpu_utilization_predicted"]
).abs()

peaks = evaluation[
    evaluation["aggregate_cpu_utilization_actual"] >= peak_threshold
]

print(f"Training-derived 90th percentile: {peak_threshold:.6f}%")
print(f"Holdout peak observations: {len(peaks)} of {len(evaluation)}")

if len(peaks):
    print(f"Peak-period MAE: {peaks['absolute_error'].mean():.6f} percentage points")
    print(
        "Peak-period RMSE: "
        f"{np.sqrt((peaks['absolute_error'] ** 2).mean()):.6f} percentage points"
    )
else:
    print("No holdout observations met the training-derived peak threshold.")

print(f"Overall holdout mean CPU: {evaluation['aggregate_cpu_utilization_actual'].mean():.6f}%")
print(f"Overall holdout maximum CPU: {evaluation['aggregate_cpu_utilization_actual'].max():.6f}%")

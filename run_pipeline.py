
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import pandas as pd


def generate_predictions(data_dir: Path) -> pd.DataFrame:
    readings_file = data_dir / "vm_cpu_readings.csv.gz"

    if not readings_file.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {readings_file}"
        )

    readings = pd.read_csv(readings_file)

    required = {"timestamp", "vm_id", "avg_cpu"}
    missing = required - set(readings.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    readings["timestamp"] = pd.to_numeric(
        readings["timestamp"], errors="raise"
    )
    readings["avg_cpu"] = pd.to_numeric(
        readings["avg_cpu"], errors="coerce"
    )


    readings = readings.drop_duplicates(
        subset=["timestamp", "vm_id"], keep="first"
    )

    targets = (
        readings.groupby("timestamp", as_index=False)
        .agg(
            active_vm_count=("vm_id", "nunique"),
            aggregate_cpu_utilization=("avg_cpu", "mean"),
        )
        .sort_values("timestamp")
        .reset_index(drop=True)
    )


    horizon = 24
    if len(targets) <= horizon:
        raise ValueError(
            "At least 25 distinct timestamps are required: "
            "one or more training observations plus 24 forecast timestamps."
        )

    train = targets.iloc[:-horizon]
    holdout = targets.iloc[-horizon:]


    active_count = train["active_vm_count"].iloc[-1]
    cpu_history = train["aggregate_cpu_utilization"].dropna()

    if cpu_history.empty:
        raise ValueError("No valid training CPU observations found.")

    last_cpu = float(cpu_history.iloc[-1])

    predictions = pd.DataFrame({
        "timestamp": holdout["timestamp"].to_numpy(),
        "active_vm_count": int(active_count),
        "aggregate_cpu_utilization": np.clip(last_cpu, 0, 100),
    })

    predictions["active_vm_count"] = (
        predictions["active_vm_count"].clip(lower=0).astype(int)
    )

    if not np.isfinite(
        predictions[
            ["active_vm_count", "aggregate_cpu_utilization"]
        ].to_numpy(dtype=float)
    ).all():
        raise ValueError("Predictions contain non-finite values.")

    return predictions[
        ["timestamp", "active_vm_count", "aggregate_cpu_utilization"]
    ]


def main():
    parser = ArgumentParser(
        description="Generate 24 cloud workload forecasts."
    )
    parser.add_argument("--data", type=Path, default=Path("challenge_data"))
    parser.add_argument("--output", type=Path, default=Path("predictions.csv"))
    args = parser.parse_args()

    predictions = generate_predictions(args.data)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(args.output, index=False)

    print(f"Created {args.output}")
    print(f"Forecast rows: {len(predictions)}")
    print(
        f"Timestamp range: {predictions['timestamp'].iloc[0]} "
        f"to {predictions['timestamp'].iloc[-1]}"
    )


if __name__ == "__main__":
    main()

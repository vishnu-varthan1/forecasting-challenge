# Cloud Workload Forecasting Challenge

An AI/ML engineering take-home project analyzing virtual-machine telemetry from the Microsoft Azure Public Dataset V2. The project investigates workload characteristics, compares time-series forecasting baselines, evaluates forecast accuracy, and develops capacity-planning recommendations.

## 1. Project Overview

The project forecasts two workload metrics at five-minute intervals:

- **`active_vm_count`** — the number of distinct VMs observed at each timestamp.
- **`aggregate_cpu_utilization`** — the mean of VM-level `avg_cpu` measurements at each timestamp, expressed as a percentage.

The supplied dataset contains 10,000 VMs, 134 readings per VM, and 1,340,000 CPU observations across 134 timestamps. The interval between the first and last timestamps is approximately 11.08 hours.

## 2. Environment Setup

Python 3.11 or newer is required.

### Windows PowerShell

Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project and development dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## 3. Dataset Setup

The fixed `data-v1` dataset is distributed through the challenge's GitHub release.

**Download:** [Azure Dataset v1 Release](https://github.com/atomityhq/forecasting-challenge/releases/tag/data-v1)

Download `data-v1.tar.gz` from the release and extract it into the repository's `challenge_data/` directory.

Expected dataset files:

```text
challenge_data/
├── vm_cpu_readings.csv.gz
├── vm_metadata.csv.gz
├── DATA_CARD.md
└── SHA256SUMS
```

On Linux or macOS, verify the downloaded files from inside `challenge_data/`:

```bash
cd challenge_data
sha256sum -c SHA256SUMS
cd ..
```

On Windows, use PowerShell's `Get-FileHash` and compare the hashes against `SHA256SUMS` if `sha256sum` is unavailable.

Use the exact dataset release specified by the assignment. Large archives and raw compressed datasets should remain local and must not be committed to the repository.

## 4. Generate the Required Predictions

After installing dependencies and extracting the dataset, run this single command from the repository root:

```powershell
python run_pipeline.py --data challenge_data --output predictions.csv
```

This is the primary prediction-generation command. It reads the CPU readings, constructs the aggregate workload time series, uses observations preceding the final 24 timestamps for forecasting, and writes `predictions.csv`.

The pipeline requires at least 25 distinct timestamps: at least one training observation and the final 24 forecast timestamps.

The output must contain exactly these columns:

```text
timestamp,active_vm_count,aggregate_cpu_utilization
```

The submission contract requires exactly 24 chronological rows, unique timestamps, finite numeric predictions, non-negative active VM counts, and CPU utilization between 0 and 100. No index column is included.

## 5. Analysis Workflow

The following commands reproduce the supporting analyses. Run them from the repository root after setting up the environment and dataset.

```powershell
python inspect_data.py
python build_targets.py
python validate_baselines.py
python validate_trend.py
python generate_predictions.py
python evaluate_final.py
python analyze_peaks.py
python analyze_capacity.py
python -m pytest -q
```

| Script | Purpose |
|---|---|
| `run_pipeline.py` | Generate the final forecast in one command |
| `inspect_data.py` | Inspect data quality, timestamps, VM coverage, and CPU distributions |
| `build_targets.py` | Construct the aggregate target time series |
| `validate_baselines.py` | Compare persistence and moving-average baselines using chronological validation |
| `validate_trend.py` | Evaluate a linear-trend candidate using chronological validation |
| `generate_predictions.py` | Generate the final forecast from the prepared target series |
| `evaluate_final.py` | Evaluate the frozen forecast against the holdout |
| `analyze_peaks.py` | Assess holdout observations against the training-derived peak threshold |
| `analyze_capacity.py` | Summarize training CPU statistics and illustrative headroom scenarios |

## 6. Validation Methodology

The first 110 observations are used for model development and time-aware validation. The final 24 observations are reserved for the two-hour forecast horizon.

Four chronological validation splits use training histories of 62, 74, 86, and 98 observations. Each split forecasts the following 12 observations. The data is not randomly shuffled.

Three forecasting approaches were compared:

- **Persistence:** repeats the most recent observed value.
- **Moving average (12):** repeats the mean of the latest 12 observations.
- **Linear trend:** fits a straight line to historical observations and extrapolates it into the forecast horizon.

Model selection uses only the chronological validation results from within the first 110 observations. The final 24 target values are not used for fitting or model selection.

## 7. Validation Results

Mean validation metrics for aggregate CPU utilization were:

| Model | MAE | RMSE |
|---|---:|---:|
| Persistence | 0.110890 | 0.134443 |
| Moving average (12) | 0.155652 | 0.174880 |
| Linear trend | 0.243576 | 0.263750 |

CPU forecast errors are measured in **percentage points**.

Persistence was selected because it achieved the lowest mean validation MAE and RMSE among the tested approaches. Its mean validation MAE was approximately 28.8% lower than that of the moving-average model and 54.5% lower than that of the linear-trend model.

The linear-trend approach performed better than persistence in the first validation split but substantially worse in the remaining three. This suggests that linear extrapolation was not robust for this short trace.

## 8. Final Holdout Results

The selected persistence model was fitted using the first 110 observations and evaluated against the final 24 observations.

| Forecast target | MAE | RMSE |
|---|---:|---:|
| Active VM count | 0.000000 | 0.000000 |
| Aggregate CPU utilization | 0.146782 | 0.184785 |

Aggregate CPU utilization achieved an MAE of 0.146782 percentage points and an RMSE of 0.184785 percentage points.

The active VM count remained constant at 10,000 throughout the trace. Its zero forecast error therefore reflects the constant target rather than demonstrated forecasting performance under VM arrivals or departures.

The holdout mean CPU utilization was 9.268988%, and the maximum was 9.635990%. The persistence forecast repeats the last CPU value from the training window, approximately 9.164556%.

## 9. Peak-Period Analysis

The 90th percentile of aggregate CPU utilization in the training window was 9.668362%. This threshold was calculated using training observations only.

None of the 24 holdout observations met or exceeded the threshold. The maximum holdout CPU utilization was 9.635990%, so peak-specific holdout MAE and RMSE could not be calculated.

The absence of qualifying peak observations limits conclusions about performance during workload surges. It does not demonstrate that persistence would remain accurate during sudden demand increases or sustained high utilization.

## 10. Capacity-Planning Recommendations

Training-window statistics were:

| Metric | Value |
|---|---:|
| Mean CPU utilization | 9.4141% |
| Median CPU utilization | 9.3781% |
| 95th-percentile CPU utilization | 9.8291% |
| 99th-percentile CPU utilization | 9.9049% |
| Maximum CPU utilization | 9.9122% |
| Active VM count | 10,000 |

Illustrative capacity factors under a proportional-demand assumption are:

- **50% target utilization:** 2.00× current demand.
- **60% target utilization:** approximately 1.67× current demand.
- **70% target utilization:** approximately 1.43× current demand.

These are planning scenarios, not validated production recommendations. Actual capacity requirements depend on expected workload growth, VM sizing, CPU contention, memory and network bottlenecks, service-level objectives, and recovery requirements.

Recommended practices include:

1. Monitor aggregate and per-VM CPU utilization, active VM counts, and service-level indicators.
2. Investigate scaling when utilization remains elevated or demand trends exceed validated thresholds.
3. Maintain enough headroom for demand increases, instance failures, and recovery operations.
4. Validate scaling policies with load tests and workloads containing realistic peaks and VM churn.
5. Recalculate forecasts as new observations arrive and evaluate performance across multiple time windows.

## 11. Repository Outputs

- `run_pipeline.py` — the single-command prediction pipeline.
- `predictions.csv` — the 24-row forecast with the required three columns.
- `reports/target_series.csv` — the constructed aggregate target series.
- `reports/validation_results.csv` and `reports/validation_summary.csv` — chronological baseline validation results.
- `reports/trend_validation_results.csv` and `reports/trend_validation_summary.csv` — linear-trend validation results.
- `reports/holdout_baseline_diagnostics.csv` — post-hoc diagnostic comparisons of baselines on the public holdout. These results are for transparency only and were not used for model selection or tuning.
- `reports/final_report.md` — detailed methodology, results, capacity-planning discussion, and limitations.

## 12. Tests

Run the automated test suite from the repository root:

```powershell
python -m pytest -q
```

The local test suite currently passes nine tests, including checks for prediction columns, row count, chronological timestamps, finite values, and allowed output ranges.

## 13. Limitations and Future Improvements

The trace covers approximately 11.08 hours and contains a constant active VM count with relatively limited variation in aggregate CPU utilization. It does not adequately demonstrate forecast performance during abrupt workload spikes, VM arrivals or departures, or sustained high-load conditions.

Future work should evaluate longer and more varied traces, include periods with genuine peak demand, and use repeated rolling-origin validation. Additional forecasting approaches may be investigated where justified by the data. Forecast monitoring, uncertainty estimation, and load testing should be considered before forecasts are used for production scaling decisions.

## 14. References and Assignment Instructions

- [Assignment instructions](ASSIGNMENT.md)
- [Dataset documentation](DATASET.md)
- [Submission requirements](SUBMISSION.md)
- [Microsoft Azure Public Dataset V2](https://github.com/Azure/AzurePublicDataset)
- [Challenge dataset release](https://github.com/atomityhq/forecasting-challenge/releases/tag/data-v1)

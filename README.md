# Cloud Workload Forecasting Challenge

An AI/ML engineering take-home project analyzing virtual-machine telemetry from the Microsoft Azure Public Dataset V2. This project explores workload characteristics, compares forecasting baselines, evaluates a reserved holdout, and develops capacity-planning recommendations.

## 1. Project Overview

The project forecasts two workload metrics at five-minute intervals:

- **`active_vm_count`** — the number of distinct VMs observed at each timestamp.
- **`aggregate_cpu_utilization`** — the mean of VM-level `avg_cpu` measurements at each timestamp, expressed as a percentage.

The supplied trace contains 10,000 VMs with 134 readings per VM, resulting in 1,340,000 CPU observations across 134 timestamps. The interval between the first and final timestamps is approximately 11.08 hours.

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

Download `data-v1.tar.gz` from the release and extract the dataset into the repository's `challenge_data/` directory.

The expected dataset files include:

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

On Windows, use PowerShell's `Get-FileHash` to compare file hashes against `SHA256SUMS` if `sha256sum` is unavailable.

Use the exact dataset release provided for this challenge. Do not substitute another dataset version. Large dataset archives and raw compressed data files should remain local rather than being committed to Git.

## 4. Generate the Required Predictions

After installing dependencies and extracting the dataset, run this single command from the repository root:

```powershell
python run_pipeline.py --data challenge_data --output predictions.csv
```

The pipeline reads the supplied CPU readings, constructs the aggregate workload time series, reserves the final 24 timestamps for forecasting, and writes `predictions.csv`.

The output contains exactly three columns:

```text
timestamp,active_vm_count,aggregate_cpu_utilization
```

The generated file must contain 24 chronological rows, with no duplicate timestamps or non-finite predictions. Active VM counts must be non-negative, and CPU utilization predictions must be between 0 and 100.

The persistence baseline uses training observations preceding the final 24 timestamps. Actual holdout target values are not used for model fitting or model selection.

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

The scripts serve these purposes:

| Script | Purpose |
|---|---|
| `inspect_data.py` | Inspect data quality, timestamps, VM coverage, and CPU distributions |
| `build_targets.py` | Construct the aggregate target time series |
| `validate_baselines.py` | Compare persistence and moving-average baselines using chronological validation |
| `validate_trend.py` | Evaluate a linear-trend candidate using chronological validation |
| `generate_predictions.py` | Generate the final 24-row forecast from the prepared target series |
| `evaluate_final.py` | Evaluate the frozen forecast against the holdout |
| `analyze_peaks.py` | Evaluate whether holdout observations meet the training-derived peak threshold |
| `analyze_capacity.py` | Summarize training CPU statistics and illustrative headroom scenarios |

The main prediction command is `python run_pipeline.py --data challenge_data --output predictions.csv`. The other scripts provide detailed analysis and validation.

## 6. Validation Methodology

The first 110 observations form the model development and validation window. The final 24 observations represent the two-hour forecast horizon.

Four chronological validation splits use training histories of 62, 74, 86, and 98 observations. Each split forecasts the next 12 observations. The series is not randomly shuffled.

Three CPU forecasting approaches were compared:

- **Persistence:** repeats the most recent observed value.
- **Moving average (12):** uses the mean of the latest 12 observations.
- **Linear trend:** fits a straight line to historical observations and extrapolates it into the forecast horizon.

Model selection uses chronological validation results entirely within the first 110 observations. The final 24 target values are held out for final evaluation and are not used to select the model.

## 7. Validation Results

Mean validation metrics for aggregate CPU utilization were:

| Model | MAE | RMSE |
|---|---:|---:|
| Persistence | 0.110890 | 0.134443 |
| Moving average (12) | 0.155652 | 0.174880 |
| Linear trend | 0.243576 | 0.263750 |

CPU forecast errors are measured in **percentage points**.

Persistence was selected because it achieved the lowest mean validation MAE and RMSE among the tested approaches. Its mean validation MAE was approximately 28.8% lower than the moving-average model and 54.5% lower than the linear-trend model.

The linear-trend model performed better in the first validation split but substantially worse in the remaining three, indicating that linear extrapolation was unreliable for this short trace.

## 8. Final Holdout Results

The selected persistence model was fitted using the first 110 observations and evaluated against the final 24 observations.

| Forecast target | MAE | RMSE |
|---|---:|---:|
| Active VM count | 0.000000 | 0.000000 |
| Aggregate CPU utilization | 0.146782 | 0.184785 |

Aggregate CPU utilization achieved an MAE of 0.146782 percentage points and an RMSE of 0.184785 percentage points.

Active VM count remained constant at 10,000 throughout the observed trace. Its zero forecast error therefore reflects the constant target rather than demonstrated performance under VM arrivals or departures.

The holdout mean CPU utilization was 9.268988%, and the maximum was 9.635990%. The persistence forecast repeats the last training CPU observation, approximately 9.164556%.

## 9. Peak-Period Analysis

The 90th percentile of aggregate CPU utilization in the training window was 9.668362%. This threshold was calculated using training observations only.

None of the 24 holdout observations met or exceeded the threshold. The maximum holdout CPU utilization was 9.635990%, so peak-specific holdout MAE and RMSE could not be calculated.

The absence of qualifying peak observations limits conclusions about model performance during workload surges. It does not demonstrate that persistence would remain accurate during sudden demand increases or sustained high utilization.

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

These factors are illustrative planning scenarios, not validated production recommendations. Actual capacity requirements depend on expected workload growth, VM sizing, CPU contention, memory and network bottlenecks, service-level objectives, and recovery requirements.

Recommended operational practices include:

1. Monitor aggregate and per-VM CPU utilization, active VM counts, and service-level indicators.
2. Investigate scaling when utilization remains elevated or demand trends exceed validated thresholds.
3. Maintain sufficient capacity headroom for demand increases, instance failures, and recovery operations.
4. Validate scaling policies using load tests and workloads containing realistic peaks and VM churn.
5. Recalculate forecasts as new observations arrive and measure performance over multiple time windows.

## 11. Repository Outputs

- `run_pipeline.py` — the single-command prediction pipeline.
- `predictions.csv` — the 24-row forecast with the required three columns.
- `reports/target_series.csv` — the constructed aggregate target series.
- `reports/validation_results.csv` and `reports/validation_summary.csv` — chronological baseline validation results.
- `reports/trend_validation_results.csv` and `reports/trend_validation_summary.csv` — linear-trend comparison results.
- `reports/final_report.md` — detailed methodology, results, capacity-planning discussion, and limitations.

## 12. Tests

Run the test suite from the repository root:

```powershell
python -m pytest -q
```

The current local test suite passes nine tests, including validation of prediction columns, row count, timestamps, numeric values, and allowed output ranges.

## 13. Limitations and Future Improvements

The trace covers approximately 11.08 hours and contains a constant active VM count and relatively limited variation in aggregate CPU utilization. It does not sufficiently demonstrate forecast performance during abrupt workload spikes, VM arrivals or departures, or sustained high-load conditions.

Future work should evaluate longer and more varied traces, include periods with genuine peak demand, and use repeated rolling-origin validation. Additional forecasting models may be investigated when justified by the available data. Forecast monitoring, uncertainty estimates, and load testing should be considered before forecasts are used for production scaling decisions.

## 14. References and Assignment Instructions

- [Assignment instructions](ASSIGNMENT.md)
- [Dataset documentation](DATASET.md)
- [Submission requirements](SUBMISSION.md)
- [Microsoft Azure Public Dataset V2](https://github.com/Azure/AzurePublicDataset)
- [Challenge dataset release](https://github.com/atomityhq/forecasting-challenge/releases/tag/data-v1)

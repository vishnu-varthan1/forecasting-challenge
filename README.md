# Cloud Workload Forecasting Challenge

An AI/ML take-home project analyzing virtual-machine telemetry from the Microsoft Azure Public Dataset V2. This implementation explores workload characteristics, compares time-series forecasting baselines, evaluates a reserved holdout, and develops capacity-planning recommendations.

## Project Overview

The project forecasts two workload metrics at five-minute intervals:

- **`active_vm_count`** — the number of distinct VMs observed at each timestamp.
- **`aggregate_cpu_utilization`** — the mean of VM-level `avg_cpu` measurements at each timestamp, expressed as a percentage.

The supplied trace contains 10,000 VMs with 134 readings per VM, resulting in 1,340,000 CPU observations across 134 timestamps. The period from the first to the final timestamp spans approximately 11.08 hours.

## Environment Setup

Python 3.11 or newer is required.

### Windows PowerShell

Create and activate a virtual environment:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
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

## Dataset Setup

The fixed `data-v1` dataset is distributed through the challenge's GitHub release.

**Download:** [Azure Dataset v1 Release](https://github.com/atomityhq/forecasting-challenge/releases/tag/data-v1)

Download `data-v1.tar.gz` and extract it into the repository's `challenge_data/` directory according to the release instructions. The expected dataset files include:

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

On Windows, use PowerShell's `Get-FileHash` and compare the results against `SHA256SUMS` if `sha256sum` is unavailable.

Do not substitute a different dataset version. The downloaded data archives should remain local rather than being committed to the repository.

## Analysis Workflow

Run these commands from the repository root after installing dependencies and extracting the dataset:

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

The scripts perform the following tasks:

| Script | Purpose |
|---|---|
| `inspect_data.py` | Inspect data quality, timestamps, VM coverage, and CPU distributions |
| `build_targets.py` | Construct the aggregate target time series |
| `validate_baselines.py` | Compare persistence and moving-average baselines using chronological validation |
| `validate_trend.py` | Evaluate a linear-trend candidate using chronological validation |
| `generate_predictions.py` | Generate the final 24-row forecast |
| `evaluate_final.py` | Evaluate the frozen forecast against the holdout |
| `analyze_peaks.py` | Evaluate whether holdout observations meet the training-derived peak threshold |
| `analyze_capacity.py` | Summarize training CPU statistics and illustrative headroom scenarios |

## Validation Methodology

The first 110 observations are used for model development and time-aware validation. The final 24 observations are held out for the two-hour forecast evaluation.

Four chronological validation splits are used, with training histories of 62, 74, 86, and 98 observations. Each split forecasts the next 12 observations. The data is not randomly shuffled.

Three CPU forecasting approaches were compared:

- **Persistence:** repeat the most recent observed value.
- **Moving average (12):** use the mean of the latest 12 observations.
- **Linear trend:** fit a straight line to the historical observations and extrapolate it.

Model selection uses the chronological validation results within the first 110 observations, not the final holdout results.

## Validation Results

Mean validation metrics for aggregate CPU utilization were:

| Model | MAE | RMSE |
|---|---:|---:|
| Persistence | 0.110890 | 0.134443 |
| Moving average (12) | 0.155652 | 0.174880 |
| Linear trend | 0.243576 | 0.263750 |

CPU forecast errors are measured in **percentage points**. Persistence was selected because it achieved the lowest mean validation MAE and RMSE among the tested candidates.

## Final Holdout Results

The selected persistence model was fitted using the first 110 observations and evaluated against the final 24 observations.

| Forecast target | MAE | RMSE |
|---|---:|---:|
| Active VM count | 0.000000 | 0.000000 |
| Aggregate CPU utilization | 0.146782 | 0.184785 |

The active VM count remained constant at 10,000 throughout the trace, so its zero forecast error reflects the constant target rather than demonstrated performance under VM churn.

The CPU model's MAE was 0.146782 percentage points, with an RMSE of 0.184785 percentage points.

## Peak-Period Analysis

The 90th percentile of aggregate CPU utilization in the training window was 9.668362%. This threshold was calculated using training observations only.

None of the 24 holdout observations met or exceeded the threshold. The maximum holdout CPU utilization was 9.635990%, so peak-specific holdout MAE and RMSE could not be calculated.

The absence of peak observations limits conclusions about performance during workload surges. It does not establish that the forecasting approach would remain accurate during sudden demand increases or sustained high utilization.

## Capacity-Planning Recommendations

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

- A 50% target utilization corresponds to 2.00× current demand.
- A 60% target utilization corresponds to approximately 1.67× current demand.
- A 70% target utilization corresponds to approximately 1.43× current demand.

These are planning scenarios, not validated production recommendations. Production capacity decisions require workload-specific load testing, service-level objectives, and consideration of memory, networking, CPU contention, failure recovery, and demand growth.

Monitor aggregate and per-VM CPU utilization, active VM counts, and service-level indicators. Use sustained demand patterns and validated thresholds when investigating scaling actions rather than relying on a single short-horizon forecast.

## Repository Outputs

- `predictions.csv` — the 24-row forecast with columns `timestamp`, `active_vm_count`, and `aggregate_cpu_utilization`.
- `reports/target_series.csv` — the constructed aggregate time series.
- `reports/validation_results.csv` and `reports/validation_summary.csv` — baseline validation results.
- `reports/trend_validation_results.csv` and `reports/trend_validation_summary.csv` — linear-trend validation results.
- `reports/final_report.md` — detailed methodology, evaluation results, capacity-planning discussion, and limitations.

## Tests

Run the test suite from the repository root:

```powershell
python -m pytest -q
```

The current test suite passes two tests.

## Limitations and Future Improvements

The trace covers approximately 11.08 hours and has a constant active VM count and relatively limited aggregate CPU variation. It does not adequately demonstrate forecast performance during abrupt workload spikes, VM arrivals or departures, or sustained high-load conditions.

Future work should evaluate longer and more varied traces, include periods with genuine peak demand, and use repeated rolling-origin validation. Additional forecasting methods may be investigated when justified by the available data. Forecast monitoring, uncertainty estimates, and load testing should be implemented before using forecasts for production scaling decisions.

## References and Assignment Instructions

- [Assignment instructions](ASSIGNMENT.md)
- [Dataset documentation](DATASET.md)
- [Submission requirements](SUBMISSION.md)
- [Microsoft Azure Public Dataset V2](https://github.com/Azure/AzurePublicDataset)
- [Challenge dataset release](https://github.com/atomityhq/forecasting-challenge/releases/tag/data-v1)

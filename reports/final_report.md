# Cloud Workload Forecasting and Analysis

## 1. Executive Summary

This project analyzes virtual-machine (VM) telemetry from the Microsoft Azure Public Dataset V2 and develops short-horizon forecasts for cloud workload demand. The two forecasting targets are active VM count and aggregate CPU utilization, sampled at five-minute intervals.

The dataset contains 1,340,000 CPU observations from 10,000 VMs across 134 timestamps. Data-quality checks found no missing values in the inspected columns, no duplicate VM–timestamp pairs, and no duplicate VM identifiers in the metadata.

Three forecasting approaches were compared: persistence, a 12-observation moving average, and a linear trend. Four chronological validation splits were evaluated within the first 110 observations. Persistence was selected for aggregate CPU utilization because it achieved the lowest mean validation MAE and RMSE among the tested approaches.

The final model was fitted using the 110-observation training window and generated 24 forecasts covering the final two hours. On the reserved holdout, aggregate CPU utilization achieved an MAE of 0.146782 percentage points and RMSE of 0.184785 percentage points. Active VM count was forecast exactly because the observed count remained constant at 10,000 throughout the trace.

The dataset is relatively stable and does not contain VM-count variation. Consequently, these results demonstrate a reproducible baseline workflow but do not establish performance under sudden traffic surges, VM churn, or sustained high utilization.

## 2. Problem Statement and Objectives

Cloud infrastructure operators need reliable estimates of near-term workload demand to plan capacity, maintain headroom, and make scaling decisions. Poor forecasts may lead to unnecessary infrastructure costs or insufficient capacity during periods of increased demand.

The objective of this project is to explore VM telemetry, construct aggregate time series, compare simple forecasting baselines using time-aware validation, evaluate a frozen model on a reserved holdout, and translate the findings into cautious capacity-planning recommendations.

The project has the following objectives:

- Examine dataset completeness, timestamp cadence, VM coverage, and CPU distributions.
- Construct active VM count and aggregate CPU utilization time series at five-minute intervals.
- Compare forecasting baselines without random shuffling or holdout leakage.
- Report MAE and RMSE for validation and final evaluation.
- Assess whether peak-period evaluation is possible with the reserved holdout.
- Provide reproducible scripts, prediction output, tests, and operational recommendations.

## 3. Dataset and Data Quality

### 3.1 Dataset overview

The supplied dataset contains two primary files: VM CPU readings and VM metadata. CPU readings contain timestamp, VM identifier, minimum CPU, maximum CPU, and average CPU measurements. Metadata provides additional VM characteristics.

The inspected data contains 1,340,000 CPU-reading rows, 10,000 unique VMs, and 134 distinct timestamps. Measurements are spaced at 300-second intervals, equivalent to five minutes. The first timestamp is 0 seconds and the last is 39,900 seconds, covering approximately 11.08 hours between the first and final observations.

### 3.2 Data-quality findings

The inspection identified the following:

- No missing values in the inspected readings and metadata fields.
- No duplicate VM–timestamp pairs in the CPU readings.
- No duplicate VM identifiers in the metadata.
- 10,000 distinct VMs at every timestamp.
- Consistent five-minute timestamp spacing.
- CPU values within the expected percentage range.

The metadata includes three workload categories: Delay-insensitive (6,180 VMs), Interactive (3,091 VMs), and Unknown (729 VMs).

### 3.3 CPU characteristics

Across the complete trace, average VM-level `avg_cpu` was approximately 9.3881%, with a standard deviation of approximately 14.2660 percentage points. The median was approximately 5.1051%, indicating that the distribution of individual VM CPU measurements is right-skewed.

The aggregate CPU target is much more stable than the individual VM measurements because it averages the VM-level `avg_cpu` values at each timestamp. Its overall mean was approximately 9.3881%, with a standard deviation of approximately 0.1950 percentage points.

The active VM count was 10,000 at every timestamp. This is an important dataset limitation: the count series provides little forecasting challenge and cannot demonstrate how a model responds to VM arrivals or departures.

## 4. Target Construction and Methodology

### 4.1 Forecasting targets

Two targets were constructed at each five-minute timestamp:

1. **Active VM count:** the number of distinct VMs with a reading at that timestamp, counting each VM no more than once.
2. **Aggregate CPU utilization:** the arithmetic mean of VM-level `avg_cpu` measurements at that timestamp, expressed as a percentage between 0 and 100.

The resulting time series contains 134 rows, with one row per timestamp.

### 4.2 Chronological split

The first 110 observations were designated as the training window. The final 24 observations were reserved as the two-hour holdout. The training window ends at timestamp 32,700 seconds; the holdout begins at 33,000 seconds and ends at 39,900 seconds.

Model comparison and selection used only chronological validation splits within the first 110 observations. The final 24 target values were excluded from fitting and model selection. After selecting the model, the final holdout was evaluated once to report generalization performance.

### 4.3 Forecasting approaches

**Persistence baseline:** repeats the last observed training value for every forecast step. This is a useful reference for a stable short time series.

**12-observation moving average:** forecasts using the mean of the most recent 12 observations, corresponding to one hour of history. Its performance varied across validation splits.

**Linear trend:** fits a straight line to the historical observations and extrapolates it into the forecast horizon. This approach can be sensitive to local fluctuations and may extrapolate changes that do not continue.

### 4.4 Evaluation metrics

Mean absolute error (MAE) measures the average magnitude of forecast errors. Root mean squared error (RMSE) penalizes larger errors more strongly. For CPU utilization, both metrics are expressed in percentage points.

Validation used four chronological splits, each forecasting the next 12 observations after a history of 62, 74, 86, or 98 observations. No random shuffling was used.

## 5. Validation Results and Model Selection

### 5.1 Mean validation performance

| Target | Model | MAE | RMSE |
|---|---|---:|---:|
| Aggregate CPU utilization | Persistence | 0.110890 | 0.134443 |
| Aggregate CPU utilization | Moving average (12) | 0.155652 | 0.174880 |
| Aggregate CPU utilization | Linear trend | 0.243576 | 0.263750 |
| Active VM count | Persistence | 0.000000 | 0.000000 |
| Active VM count | Moving average (12) | 0.000000 | 0.000000 |
| Active VM count | Linear trend | Approximately 0 | Approximately 0 |

Persistence was selected for aggregate CPU utilization because it achieved the lowest average MAE and RMSE across the four validation splits. Its mean MAE was approximately 28.8% lower than that of the moving-average baseline and approximately 54.5% lower than that of the linear-trend model.

The linear-trend model performed better than persistence in the first split but substantially worse in the remaining three splits. This inconsistency suggests that the observed short-term changes do not support reliable linear extrapolation.

The active VM count results are not evidence of general forecasting ability: the target is constant throughout the dataset. Persistence and the moving average therefore achieve zero error, while tiny linear-trend errors are numerical floating-point noise.

## 6. Final Holdout Evaluation

After model selection, persistence was fitted using all 110 training observations. The final 24 timestamps were then forecast without using their actual target values to fit or select the model.

| Target | Holdout MAE | Holdout RMSE |
|---|---:|---:|
| Active VM count | 0.000000 | 0.000000 |
| Aggregate CPU utilization | 0.146782 | 0.184785 |

The CPU MAE indicates an average absolute error of approximately 0.147 percentage points. The RMSE of approximately 0.185 percentage points is higher because it gives more weight to larger errors.

The holdout mean CPU utilization was 9.268988%, and the maximum was 9.635990%. The forecast was constant because persistence repeats the last training CPU observation, approximately 9.164556%.

These results show that persistence provides a reasonable short-horizon baseline for this particular stable trace. They should not be interpreted as proof that the same accuracy will hold under more variable production workloads.

## 7. Peak-Period Analysis

Peak periods were defined using the 90th percentile of aggregate CPU utilization in the training window. This training-derived threshold was 9.668362%, avoiding use of holdout values to define peak conditions.

None of the 24 holdout observations exceeded this threshold. The maximum holdout CPU utilization was 9.635990%, below the training-derived threshold. Therefore, peak-specific MAE and RMSE could not be calculated for this holdout.

This absence of qualifying peaks limits the evaluation of model behavior during high-load conditions. It does not demonstrate that persistence would perform well during traffic spikes, sustained high CPU utilization, or abrupt workload changes. Further testing requires traces containing more pronounced peaks and demand variation.

## 8. Capacity-Planning and Scaling Recommendations

### 8.1 Observed workload

Within the training window, mean aggregate CPU utilization was 9.4141%, median utilization was 9.3781%, the 95th percentile was 9.8291%, the 99th percentile was 9.9049%, and maximum utilization was 9.9122%. Active VM count remained at 10,000.

These figures describe this dataset and do not establish the capacity requirements of a real production service. Aggregate averages can conceal individual VMs with high CPU usage, and CPU utilization alone does not capture memory, storage, network, or latency constraints.

### 8.2 Illustrative headroom scenarios

Simple capacity factors can illustrate how utilization targets relate to required capacity under an idealized proportional-demand assumption:

- A 50% target utilization corresponds to a 2.00× capacity factor.
- A 60% target utilization corresponds to approximately 1.67×.
- A 70% target utilization corresponds to approximately 1.43×.

These are illustrative scenarios, not validated production recommendations. Actual capacity should be established through workload-specific load tests, service-level objectives, resource constraints, failure scenarios, and expected demand growth.

### 8.3 Recommended operational policy

1. Monitor aggregate and per-VM CPU, active VM count, and relevant service-level indicators continuously.
2. Trigger scaling investigations based on sustained utilization and demand trends rather than isolated measurements.
3. Maintain sufficient headroom for demand increases, instance failures, and recovery operations.
4. Reassess scaling thresholds through load testing and replay of workloads containing realistic peaks and VM churn.
5. Recalculate forecasts as new observations arrive and track performance across multiple time windows.
6. Avoid using a low aggregate CPU forecast as the sole signal for scaling decisions.

## 9. Limitations and Future Improvements

The dataset spans only approximately 11.08 hours and contains 134 observations. Its active VM count is constant, and aggregate CPU utilization varies only modestly. The holdout contains no observations above the training-derived peak threshold.

The evaluation compares simple baselines rather than a broad range of advanced forecasting methods. It does not establish performance during seasonal changes, large traffic surges, VM churn, or long-term workload shifts. The results also do not account directly for CPU contention, memory pressure, network bottlenecks, or application-level service objectives.

Future work should evaluate longer traces and additional workloads, include periods of genuine peak demand, and test models using repeated rolling-origin validation. Additional approaches could include seasonal-naive models where a defensible seasonal period exists, exponential smoothing, and models with workload metadata. Any additional model selection should remain confined to training and validation data.

The operational workflow should also include forecast monitoring, drift detection, uncertainty estimates, and load testing before the forecasts are used to automate scaling.

## 10. Reproducibility and Conclusion

The project includes scripts for data inspection, target construction, baseline validation, prediction generation, final holdout evaluation, peak analysis, and capacity analysis. The final prediction file contains 24 chronological rows with the required columns: `timestamp`, `active_vm_count`, and `aggregate_cpu_utilization`.

The current test suite passes two tests. Additional tests should verify prediction row count, chronological timestamps, uniqueness, finite values, and target ranges.

The main result is that persistence outperformed the tested moving-average and linear-trend alternatives for aggregate CPU utilization under the chosen chronological validation scheme. Final holdout CPU MAE and RMSE were 0.146782 and 0.184785 percentage points, respectively. The constant VM-count result and absence of holdout peaks are important limitations, so the findings should be treated as a baseline demonstration rather than a production capacity guarantee.
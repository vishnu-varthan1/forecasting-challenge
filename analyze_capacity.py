
import pandas as pd

targets = pd.read_csv("reports/target_series.csv")
train = targets.iloc[:110].copy()

cpu = train["aggregate_cpu_utilization"]

print("=== TRAINING-ONLY CAPACITY ANALYSIS ===")
print(f"Mean CPU utilization:   {cpu.mean():.4f}%")
print(f"Median CPU utilization: {cpu.median():.4f}%")
print(f"95th percentile CPU:    {cpu.quantile(0.95):.4f}%")
print(f"99th percentile CPU:    {cpu.quantile(0.99):.4f}%")
print(f"Maximum CPU utilization:{cpu.max():.4f}%")
print(f"Active VM count:        {train['active_vm_count'].iloc[-1]:.0f}")

print("\n=== ILLUSTRATIVE HEADROOM SCENARIOS ===")
for target_utilization in [50, 60, 70]:
    capacity_factor = 100 / target_utilization
    print(
        f"For a {target_utilization}% target utilization, "
        f"illustrative capacity factor = {capacity_factor:.2f}x current demand"
    )

print(
    "\nNote: These factors are illustrative planning scenarios, "
    "not production capacity recommendations. Validate using load tests, "
    "service-level objectives, and workload-specific limits."
)

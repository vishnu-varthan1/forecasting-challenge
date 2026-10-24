
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PREDICTIONS_FILE = ROOT / "predictions.csv"
READINGS_FILE = ROOT / "challenge_data" / "vm_cpu_readings.csv.gz"

EXPECTED_COLUMNS = [
    "timestamp",
    "active_vm_count",
    "aggregate_cpu_utilization",
]


@pytest.fixture(scope="module")
def predictions():
    assert PREDICTIONS_FILE.exists(), (
        "predictions.csv is missing. Run run_pipeline.py first."
    )
    return pd.read_csv(PREDICTIONS_FILE)


def test_required_columns(predictions):
    assert list(predictions.columns) == EXPECTED_COLUMNS


def test_exactly_24_forecasts(predictions):
    assert len(predictions) == 24


def test_expected_holdout_timestamps(predictions):
    assert READINGS_FILE.exists(), f"Dataset not found: {READINGS_FILE}"

    timestamps = pd.read_csv(
        READINGS_FILE, usecols=["timestamp"]
    )["timestamp"].dropna().unique()

    assert len(timestamps) >= 25

    expected = np.sort(timestamps)[-24:]

    np.testing.assert_array_equal(
        predictions["timestamp"].to_numpy(),
        expected,
    )


def test_timestamps_are_unique_and_chronological(predictions):
    timestamps = predictions["timestamp"]
    assert timestamps.is_unique
    assert timestamps.is_monotonic_increasing


def test_forecasts_are_finite(predictions):
    values = predictions[
        ["active_vm_count", "aggregate_cpu_utilization"]
    ].to_numpy(dtype=float)

    assert np.isfinite(values).all()


def test_active_vm_count_is_valid(predictions):
    counts = predictions["active_vm_count"]

    assert (counts >= 0).all()
    assert np.allclose(counts, np.round(counts))


def test_cpu_utilization_is_in_valid_range(predictions):
    cpu = predictions["aggregate_cpu_utilization"]
    assert cpu.between(0, 100).all()

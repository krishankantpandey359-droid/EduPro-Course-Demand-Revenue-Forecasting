from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_chronological_backtest import run_backtest


def test_bundled_data_backtest_creates_reproducible_reports(tmp_path):
    results, report = run_backtest(ROOT / "data", tmp_path, test_months=3)
    assert len(results) == 6
    assert set(results["Target"]) == {"EnrollmentCount", "CourseRevenue"}
    assert set(results["Model"]) == {"Ridge", "Random Forest", "HistGradientBoosting"}
    assert report["test_months"] == 3
    assert report["test_period_start"] <= report["test_period_end"]
    assert report["source_sha256"]["Transactions"]
    assert (tmp_path / "chronological_backtest.csv").is_file()
    assert (tmp_path / "chronological_backtest.json").is_file()
    assert results[["MAE", "RMSE", "NaiveLag1_MAE", "NaiveLag1_RMSE"]].notna().all().all()

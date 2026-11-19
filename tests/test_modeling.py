from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from modeling import build_monthly_panel, fit_all


def sample_data():
    dates = pd.date_range("2025-01-01", periods=12, freq="MS")
    rows = []
    number = 1
    for course in ("C1", "C2", "C3"):
        for month_index, date in enumerate(dates):
            for _ in range((month_index + 1) * (1 if course == "C1" else 2)):
                rows.append({
                    "TransactionID": f"T{number}",
                    "CourseID": course,
                    "TransactionDate": date + pd.Timedelta(days=2),
                    "Amount": float(month_index * 10 + (0 if course == "C1" else 5)),
                })
                number += 1
    return pd.DataFrame(rows), pd.DataFrame({"CourseID": ["C1", "C2", "C3"]})


def test_monthly_panel_builds_complete_course_months_and_prior_lags():
    transactions, courses = sample_data()
    panel = build_monthly_panel(transactions, courses)
    assert len(panel) == 36
    first = panel[panel.CourseID == "C1"].sort_values("Month").reset_index(drop=True)
    assert pd.isna(first.loc[0, "EnrollmentCount_lag_1"])
    assert first.loc[1, "EnrollmentCount_lag_1"] == first.loc[0, "EnrollmentCount"]
    assert first.loc[3, "EnrollmentCount_rolling_mean_3"] == pytest.approx(
        first.loc[:2, "EnrollmentCount"].mean()
    )


def test_backtest_holds_out_latest_months_and_reports_naive_baseline():
    transactions, courses = sample_data()
    result = fit_all(transactions, courses, test_months=3)
    assert set(result.Target) == {"EnrollmentCount", "CourseRevenue"}
    assert set(result.Model) == {"Ridge", "Random Forest", "HistGradientBoosting"}
    assert result.TestFrom.eq("2025-10").all()
    assert result.TestThrough.eq("2025-12").all()
    assert result.TrainThrough.eq("2025-09").all()
    assert result[["MAE", "RMSE", "NaiveLag1_MAE", "NaiveLag1_RMSE"]].notna().all().all()


def test_backtest_rejects_insufficient_history():
    transactions, courses = sample_data()
    transactions = transactions[transactions.TransactionDate < "2025-06-01"]
    with pytest.raises(ValueError, match="at least four history months"):
        fit_all(transactions, courses, test_months=3)


def test_backtest_rejects_missing_required_columns():
    transactions, courses = sample_data()
    with pytest.raises(ValueError, match="Transactions missing columns"):
        build_monthly_panel(transactions.drop(columns=["Amount"]), courses)


def test_monthly_panel_rejects_duplicate_transaction_ids():
    transactions, courses = sample_data()
    transactions.loc[1, "TransactionID"] = transactions.loc[0, "TransactionID"]
    with pytest.raises(ValueError, match="duplicate transaction IDs"):
        build_monthly_panel(transactions, courses)


def test_monthly_panel_rejects_unknown_course_ids():
    transactions, courses = sample_data()
    transactions.loc[0, "CourseID"] = "NOT_IN_COURSE_TABLE"
    with pytest.raises(ValueError, match="absent from Courses"):
        build_monthly_panel(transactions, courses)


def test_monthly_panel_rejects_missing_amounts():
    transactions, courses = sample_data()
    transactions.loc[0, "Amount"] = float("nan")
    with pytest.raises(ValueError, match="missing, non-numeric"):
        build_monthly_panel(transactions, courses)


def test_monthly_panel_rejects_invalid_dates():
    transactions, courses = sample_data()
    transactions["TransactionDate"] = transactions["TransactionDate"].astype(object)
    transactions.loc[0, "TransactionDate"] = "not-a-date"
    with pytest.raises(ValueError, match="invalid or missing dates"):
        build_monthly_panel(transactions, courses)

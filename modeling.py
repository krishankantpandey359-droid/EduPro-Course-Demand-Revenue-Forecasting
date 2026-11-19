"""Leakage-aware, walk-forward monthly forecasting for EduPro.

The historical course-level totals are descriptive, not forecast targets.
This module forecasts monthly course activity from prior-month transaction
history and calendar features only. It holds out the latest months in time.
"""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


TARGETS = {
    "EnrollmentCount": "monthly unique transaction count",
    "CourseRevenue": "monthly transaction amount sum",
}
FEATURES = [
    "CourseID", "month_sin", "month_cos",
    "lag_1", "lag_2", "lag_3", "rolling_mean_3",
]


def build_monthly_panel(transactions, courses):
    """Build a complete course-month panel with strictly historical features."""
    required_tx = {"TransactionID", "CourseID", "TransactionDate", "Amount"}
    required_courses = {"CourseID"}
    if not required_tx.issubset(transactions.columns):
        raise ValueError(f"Transactions missing columns: {sorted(required_tx - set(transactions.columns))}")
    if not required_courses.issubset(courses.columns):
        raise ValueError(f"Courses missing columns: {sorted(required_courses - set(courses.columns))}")

    tx = transactions[list(required_tx)].copy()
    tx["TransactionDate"] = pd.to_datetime(tx["TransactionDate"], errors="coerce", dayfirst=True)
    tx["Amount"] = pd.to_numeric(tx["Amount"], errors="coerce")
    tx = tx.dropna(subset=["TransactionDate", "CourseID"])
    if tx.empty:
        raise ValueError("No valid dated transactions are available for forecasting.")

    tx["Month"] = tx["TransactionDate"].dt.to_period("M")
    observed = tx.groupby(["CourseID", "Month"], as_index=False).agg(
        EnrollmentCount=("TransactionID", "nunique"),
        CourseRevenue=("Amount", lambda values: values.sum(min_count=1)),
    )
    course_ids = courses["CourseID"].dropna().astype(str).drop_duplicates()
    months = pd.period_range(observed["Month"].min(), observed["Month"].max(), freq="M")
    panel = pd.MultiIndex.from_product(
        [course_ids, months], names=["CourseID", "Month"]
    ).to_frame(index=False)
    panel["CourseID"] = panel["CourseID"].astype(str)
    observed["CourseID"] = observed["CourseID"].astype(str)
    panel = panel.merge(observed, on=["CourseID", "Month"], how="left", validate="one_to_one")
    panel[["EnrollmentCount", "CourseRevenue"]] = panel[
        ["EnrollmentCount", "CourseRevenue"]
    ].fillna(0.0)
    panel = panel.sort_values(["CourseID", "Month"]).reset_index(drop=True)

    month_number = panel["Month"].dt.month
    panel["month_sin"] = np.sin(2 * np.pi * month_number / 12)
    panel["month_cos"] = np.cos(2 * np.pi * month_number / 12)
    for target in TARGETS:
        grouped = panel.groupby("CourseID", sort=False)[target]
        panel[f"{target}_lag_1"] = grouped.shift(1)
        panel[f"{target}_lag_2"] = grouped.shift(2)
        panel[f"{target}_lag_3"] = grouped.shift(3)
        panel[f"{target}_rolling_mean_3"] = grouped.transform(
            lambda values: values.shift(1).rolling(3, min_periods=3).mean()
        )
    return panel


def _make_pipeline(model):
    numeric = ["month_sin", "month_cos", "lag_1", "lag_2", "lag_3", "rolling_mean_3"]
    categorical = ["CourseID"]
    prep = ColumnTransformer([
        ("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]), numeric),
        ("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            # Dense output is required by HistGradientBoostingRegressor.
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), categorical),
    ])
    return Pipeline([("preprocess", prep), ("model", model)])


def _metrics(actual, predicted):
    error = np.asarray(actual, dtype=float) - np.asarray(predicted, dtype=float)
    denominator = float(np.abs(actual).sum())
    return {
        "MAE": float(np.mean(np.abs(error))),
        "RMSE": float(np.sqrt(np.mean(error ** 2))),
        "WAPE": float(np.abs(error).sum() / denominator) if denominator else np.nan,
    }


def fit_all(transactions, courses, test_months=3):
    """Run a rolling one-step-ahead backtest on the latest chronological months."""
    panel = build_monthly_panel(transactions, courses)
    all_months = sorted(panel["Month"].unique())
    if test_months < 1 or len(all_months) <= test_months + 3:
        raise ValueError("Need at least four history months plus the requested holdout months.")

    first_test_month = all_months[-test_months]
    results = []
    model_specs = {
        "Ridge": Ridge(alpha=1.0),
        "Random Forest": RandomForestRegressor(
            n_estimators=300, min_samples_leaf=3, random_state=42, n_jobs=-1
        ),
        "HistGradientBoosting": HistGradientBoostingRegressor(
            max_iter=150, learning_rate=0.05, l2_regularization=1.0, random_state=42
        ),
    }

    for target in TARGETS:
        lag_columns = [f"{target}_lag_{n}" for n in (1, 2, 3)]
        rolling_column = f"{target}_rolling_mean_3"
        frame = panel.dropna(subset=lag_columns + [rolling_column]).copy()
        train = frame[frame["Month"] < first_test_month]
        test = frame[frame["Month"] >= first_test_month]
        if train.empty or test.empty:
            raise ValueError(f"Insufficient chronological rows for {target}.")

        X_train = train[["CourseID", "month_sin", "month_cos"]].copy()
        X_test = test[["CourseID", "month_sin", "month_cos"]].copy()
        for name, column in zip(("lag_1", "lag_2", "lag_3"), lag_columns):
            X_train[name] = train[column].to_numpy()
            X_test[name] = test[column].to_numpy()
        X_train["rolling_mean_3"] = train[rolling_column].to_numpy()
        X_test["rolling_mean_3"] = test[rolling_column].to_numpy()
        y_train = train[target].astype(float)
        y_test = test[target].astype(float)

        baseline = _metrics(y_test, X_test["lag_1"])
        for model_name, estimator in model_specs.items():
            pipeline = _make_pipeline(estimator)
            pipeline.fit(X_train[FEATURES], y_train)
            predictions = np.maximum(0, pipeline.predict(X_test[FEATURES]))
            scores = _metrics(y_test, predictions)
            results.append({
                "Target": target,
                "Model": model_name,
                "TrainThrough": str(train["Month"].max()),
                "TestFrom": str(test["Month"].min()),
                "TestThrough": str(test["Month"].max()),
                "TrainRows": len(train),
                "TestRows": len(test),
                "MAE": scores["MAE"],
                "RMSE": scores["RMSE"],
                "WAPE": scores["WAPE"],
                "NaiveLag1_MAE": baseline["MAE"],
                "NaiveLag1_RMSE": baseline["RMSE"],
                "NaiveLag1_WAPE": baseline["WAPE"],
            })
    return pd.DataFrame(results).sort_values(["Target", "MAE"]).reset_index(drop=True)

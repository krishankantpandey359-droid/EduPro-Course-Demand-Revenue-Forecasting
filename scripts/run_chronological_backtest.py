"""Run the reproducible three-month chronological EduPro backtest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from pipeline import prepare, read_bundled
from modeling import fit_all


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_backtest(data_dir: Path, output_dir: Path, test_months: int = 3):
    sheets = read_bundled(data_dir)
    prepared = prepare(sheets)
    transactions = prepared["transactions"]
    courses = prepared["courses"]
    results = fit_all(transactions, courses, test_months=test_months)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "chronological_backtest.csv"
    results.to_csv(csv_path, index=False)

    first_date = transactions["TransactionDate"].min()
    last_date = transactions["TransactionDate"].max()
    report = {
        "title": "EduPro chronological monthly backtest",
        "method": "rolling one-step-ahead holdout using only lag and rolling features from prior months",
        "test_months": int(test_months),
        "transaction_rows": int(len(transactions)),
        "course_rows": int(len(courses)),
        "source_date_start": first_date.date().isoformat(),
        "source_date_end": last_date.date().isoformat(),
        "test_period_start": str(results["TestFrom"].min()),
        "test_period_end": str(results["TestThrough"].max()),
        "training_period_end": str(results["TrainThrough"].max()),
        "metrics_note": "MAE, RMSE and WAPE are calculated on the latest chronological test months. NaiveLag1 columns are previous-month baselines. These are backtest metrics, not guarantees of future performance.",
        "source_sha256": {
            name: sha256(data_dir / f"{name}.csv")
            for name in ("Courses", "Transactions")
        },
        "results": results.replace({float("nan"): None}).to_dict(orient="records"),
    }
    json_path = output_dir / "chronological_backtest.json"
    json_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return results, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    parser.add_argument("--test-months", type=int, default=3)
    args = parser.parse_args()
    results, report = run_backtest(args.data_dir, args.output_dir, args.test_months)
    print(results.to_string(index=False))
    print(f"Saved {args.output_dir / 'chronological_backtest.csv'}")
    print(f"Saved {args.output_dir / 'chronological_backtest.json'}")
    print(f"Backtest period: {report['test_period_start']} to {report['test_period_end']}")


if __name__ == "__main__":
    main()

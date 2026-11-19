from pathlib import Path
import hashlib
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pipeline import REQUIRED, audit, prepare, read_bundled


def test_bundled_source_tables_have_expected_schema_and_rows():
    sheets = read_bundled(ROOT / "data")
    assert set(sheets) == set(REQUIRED)
    expected_rows = {"Users": 3000, "Teachers": 60, "Courses": 60, "Transactions": 10000}
    for name, frame in sheets.items():
        assert len(frame) == expected_rows[name]
        assert set(REQUIRED[name]).issubset(frame.columns)
    report = audit(sheets)
    assert report["Status"].eq("OK").all()


def test_pipeline_builds_analysis_without_mutating_source_files():
    files = [ROOT / "data" / f"{name}.csv" for name in REQUIRED]
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

    result = prepare(read_bundled(ROOT / "data"))

    assert len(result["users"]) == 3000
    assert len(result["teachers"]) == 60
    assert len(result["courses"]) == 60
    assert len(result["transactions"]) == 10000
    assert len(result["course_features"]) == 60
    assert {"EnrollmentCount", "CourseRevenue", "UniqueUsers"}.issubset(result["course_features"].columns)
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    assert after == before


def test_prepare_rejects_missing_source_table_without_fabricating_rows():
    sheets = read_bundled(ROOT / "data")
    sheets.pop("Teachers")
    try:
        prepare(sheets)
    except ValueError as exc:
        assert "Teachers" in str(exc)
        assert "no missing rows will be fabricated" in str(exc)
    else:
        raise AssertionError("prepare() should reject an incomplete workbook")


def test_prepare_rejects_missing_transaction_amount():
    sheets = read_bundled(ROOT / "data")
    sheets["Transactions"].loc[0, "Amount"] = None
    try:
        prepare(sheets)
    except ValueError as exc:
        assert "missing, non-numeric, or non-finite Amount" in str(exc)
    else:
        raise AssertionError("prepare() should reject a missing transaction amount")


def test_prepare_rejects_duplicate_transaction_id():
    sheets = read_bundled(ROOT / "data")
    sheets["Transactions"].loc[1, "TransactionID"] = sheets["Transactions"].loc[0, "TransactionID"]
    try:
        prepare(sheets)
    except ValueError as exc:
        assert "duplicate TransactionID" in str(exc)
    else:
        raise AssertionError("prepare() should reject duplicate transaction IDs")


def test_prepare_rejects_unknown_course_reference():
    sheets = read_bundled(ROOT / "data")
    sheets["Transactions"].loc[0, "CourseID"] = "UNKNOWN"
    try:
        prepare(sheets)
    except ValueError as exc:
        assert "references absent" in str(exc)
    else:
        raise AssertionError("prepare() should reject unmatched course references")

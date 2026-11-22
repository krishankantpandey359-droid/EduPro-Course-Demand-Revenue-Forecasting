"""Read, audit and prepare the EduPro source workbook without fabricating rows."""
from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED = {
    "Users": ["UserID", "UserName", "Age", "Gender", "Email"],
    "Teachers": [
        "TeacherID", "TeacherName", "Age", "Gender", "Expertise",
        "YearsOfExperience", "TeacherRating",
    ],
    "Courses": [
        "CourseID", "CourseName", "CourseCategory", "CourseType",
        "CourseLevel", "CoursePrice", "CourseDuration", "CourseRating",
    ],
    "Transactions": [
        "TransactionID", "UserID", "CourseID", "TransactionDate",
        "Amount", "PaymentMethod", "TeacherID",
    ],
}
KEY_COLUMNS = {
    "Users": ["UserID"],
    "Teachers": ["TeacherID"],
    "Courses": ["CourseID"],
    "Transactions": ["TransactionID", "UserID", "CourseID", "TeacherID"],
}
NUMERIC_COLUMNS = {
    "Users": ["Age"],
    "Teachers": ["Age", "YearsOfExperience", "TeacherRating"],
    "Courses": ["CoursePrice", "CourseDuration", "CourseRating"],
}


def read_workbook(file):
    xls = pd.ExcelFile(file)
    out = {}
    aliases = {
        "Tranactions": "Transactions",
        "Transaction": "Transactions",
        "transactions": "Transactions",
        "users": "Users",
        "teachers": "Teachers",
        "courses": "Courses",
    }
    for raw in xls.sheet_names:
        name = aliases.get(raw, raw)
        if name in out:
            raise ValueError(f"Workbook contains more than one sheet mapping to {name}.")
        out[name] = pd.read_excel(xls, sheet_name=raw)
    return out


def read_bundled(data_dir):
    out = {}
    for name in REQUIRED:
        path = Path(data_dir) / f"{name}.csv"
        if path.exists():
            out[name] = pd.read_csv(path)
    return out


def _normalized_frame(name, frame):
    if not isinstance(frame, pd.DataFrame):
        raise TypeError(f"{name} must be a pandas DataFrame.")
    result = frame.copy()
    result.columns = [str(column).strip() for column in result.columns]
    if any(not column for column in result.columns):
        raise ValueError(f"{name} contains blank column names.")
    if result.columns.duplicated().any():
        duplicates = result.columns[result.columns.duplicated()].unique().tolist()
        raise ValueError(f"{name} contains duplicate column names after trimming: {duplicates}")
    missing = [column for column in REQUIRED[name] if column not in result.columns]
    if missing:
        raise ValueError(f"{name} is missing columns: {missing}")
    return result


def audit(sheets):
    """Return a per-sheet schema and duplicate summary without mutating sources."""
    rows = []
    for name, required_columns in REQUIRED.items():
        if name not in sheets:
            rows.append({
                "Sheet": name,
                "Status": "MISSING",
                "Rows": 0,
                "Missing columns": ", ".join(required_columns),
                "Duplicate rows": None,
            })
            continue

        frame = sheets[name]
        normalized = [str(column).strip() for column in frame.columns]
        duplicate_columns = sorted({
            column for column in normalized if normalized.count(column) > 1
        })
        blank_columns = any(not column for column in normalized)
        missing = [column for column in required_columns if column not in normalized]
        try:
            duplicate_rows = int(frame.duplicated().sum()) if not duplicate_columns else None
        except TypeError:
            duplicate_rows = None

        if duplicate_columns:
            status = "DUPLICATE COLUMNS"
        elif blank_columns:
            status = "BLANK COLUMNS"
        elif missing:
            status = "COLUMN CHECK NEEDED"
        else:
            status = "OK"
        rows.append({
            "Sheet": name,
            "Status": status,
            "Rows": len(frame),
            "Missing columns": ", ".join(missing) or "None",
            "Duplicate rows": duplicate_rows,
        })
    return pd.DataFrame(rows)


def prepare(sheets):
    """Validate source tables and return analysis frames plus an audit summary."""
    missing_sheets = [name for name in REQUIRED if name not in sheets]
    if missing_sheets:
        raise ValueError(
            "Missing sheet(s): " + ", ".join(missing_sheets)
            + ". Upload the original workbook with all four sheets; "
            "no missing rows will be fabricated."
        )

    normalized = {
        name: _normalized_frame(name, sheets[name])
        for name in REQUIRED
    }
    users = normalized["Users"]
    teachers = normalized["Teachers"]
    courses = normalized["Courses"]
    tx = normalized["Transactions"]

    for name, frame in (
        ("Users", users), ("Teachers", teachers), ("Courses", courses),
        ("Transactions", tx),
    ):
        for column in KEY_COLUMNS[name]:
            frame[column] = frame[column].astype("string").str.strip()
            if frame[column].isna().any() or frame[column].eq("").any():
                raise ValueError(f"{name} contains missing or blank {column} values.")
        for column in KEY_COLUMNS[name]:
            if frame[column].duplicated().any():
                raise ValueError(
                    f"{name} contains duplicate {column} values after whitespace normalization."
                )

    audit_info = {
        "unmatched_user_rows": 0,
        "unmatched_course_rows": 0,
        "unmatched_teacher_rows": 0,
        "invalid_dates": 0,
        "missing_amounts": 0,
        "non_finite_amounts": 0,
        "duplicate_transaction_ids": 0,
    }

    for name, frame in NUMERIC_COLUMNS.items():
        for column in frame:
            raw_values = normalized[name][column]
            converted = pd.to_numeric(raw_values, errors="coerce")
            invalid_text = raw_values.notna() & converted.isna()
            if invalid_text.any():
                raise ValueError(f"{name}.{column} contains non-numeric values.")
            finite = np.isfinite(converted.dropna().to_numpy(dtype=float))
            if not finite.all():
                raise ValueError(f"{name}.{column} contains non-finite values.")
            normalized[name][column] = converted

    tx["Amount"] = pd.to_numeric(tx["Amount"], errors="coerce")
    audit_info["missing_amounts"] = int(tx["Amount"].isna().sum())
    if audit_info["missing_amounts"]:
        raise ValueError(
            f"Transactions contain {audit_info['missing_amounts']} "
            "missing or non-numeric Amount values."
        )
    finite_amounts = np.isfinite(tx["Amount"].to_numpy(dtype=float))
    audit_info["non_finite_amounts"] = int((~finite_amounts).sum())
    if audit_info["non_finite_amounts"]:
        raise ValueError(
            f"Transactions contain {audit_info['non_finite_amounts']} non-finite Amount values."
        )

    tx["TransactionDate"] = pd.to_datetime(
        tx["TransactionDate"], errors="coerce", dayfirst=True
    )
    audit_info["invalid_dates"] = int(tx["TransactionDate"].isna().sum())
    if audit_info["invalid_dates"]:
        raise ValueError(
            f"Transactions contain {audit_info['invalid_dates']} invalid or missing TransactionDate values."
        )

    audit_info["unmatched_user_rows"] = int((~tx["UserID"].isin(users["UserID"])).sum())
    audit_info["unmatched_course_rows"] = int((~tx["CourseID"].isin(courses["CourseID"])).sum())
    audit_info["unmatched_teacher_rows"] = int((~tx["TeacherID"].isin(teachers["TeacherID"])).sum())
    if any(audit_info[key] for key in (
        "unmatched_user_rows", "unmatched_course_rows", "unmatched_teacher_rows"
    )):
        raise ValueError(
            "Transactions contain UserID, CourseID, or TeacherID references "
            "absent from their source tables."
        )

    agg = tx.groupby("CourseID").agg(
        EnrollmentCount=("TransactionID", "nunique"),
        CourseRevenue=("Amount", lambda values: values.sum(min_count=1)),
        UniqueUsers=("UserID", "nunique"),
        PaidTransactions=("Amount", lambda values: int((values > 0).sum())),
        FreeTransactions=("Amount", lambda values: int((values == 0).sum())),
    ).reset_index()

    course_features = courses.merge(
        agg, on="CourseID", how="left", validate="one_to_one"
    )
    for column in (
        "EnrollmentCount", "CourseRevenue", "UniqueUsers",
        "PaidTransactions", "FreeTransactions",
    ):
        course_features[column] = course_features[column].fillna(0)

    course_features["RevenuePerEnrollment"] = np.where(
        course_features["EnrollmentCount"] > 0,
        course_features["CourseRevenue"] / course_features["EnrollmentCount"],
        0,
    )
    course_features["PriceBand"] = pd.cut(
        course_features["CoursePrice"],
        bins=[-np.inf, 0, 100, 250, 400, np.inf],
        labels=["Free/Zero", "Low", "Medium", "High", "Premium"],
    ).astype("string")
    course_features["DurationBucket"] = pd.cut(
        course_features["CourseDuration"],
        bins=[-np.inf, 5, 15, 30, np.inf],
        labels=["Very Short (<=5)", "Short (5-15)", "Medium (15-30)", "Long (>30)"],
    ).astype("string")
    course_features["RatingTier"] = pd.cut(
        course_features["CourseRating"],
        bins=[-np.inf, 2, 3.5, 4.25, np.inf],
        labels=["Low", "Moderate", "Good", "High"],
    ).astype("string")

    teacher_course = tx[["CourseID", "TeacherID"]].drop_duplicates().merge(
        teachers, on="TeacherID", how="left", validate="many_to_one"
    )
    teacher_aggregates = teacher_course.groupby("CourseID").agg(
        TeacherCount=("TeacherID", "nunique"),
        AvgTeacherExperience=("YearsOfExperience", "mean"),
        AvgTeacherRating=("TeacherRating", "mean"),
        TeacherExpertise=(
            "Expertise",
            lambda values: " | ".join(sorted(set(values.dropna().astype(str)))),
        ),
    ).reset_index()
    course_features = course_features.merge(
        teacher_aggregates, on="CourseID", how="left", validate="one_to_one"
    )
    course_features["TeacherCount"] = course_features["TeacherCount"].fillna(0)
    course_features["AvgTeacherExperience"] = course_features[
        "AvgTeacherExperience"
    ].fillna(teachers["YearsOfExperience"].median())
    course_features["AvgTeacherRating"] = course_features[
        "AvgTeacherRating"
    ].fillna(teachers["TeacherRating"].median())
    course_features["TeacherExpertise"] = course_features["TeacherExpertise"].fillna("Unknown")

    monthly = tx.assign(
        Month=tx["TransactionDate"].dt.to_period("M").astype(str)
    ).groupby("Month").agg(
        Enrollments=("TransactionID", "nunique"),
        Revenue=("Amount", lambda values: values.sum(min_count=1)),
        UniqueUsers=("UserID", "nunique"),
    ).reset_index()
    category = course_features.groupby("CourseCategory", dropna=False).agg(
        CourseCount=("CourseID", "nunique"),
        EnrollmentCount=("EnrollmentCount", "sum"),
        CourseRevenue=("CourseRevenue", "sum"),
        AverageCourseRating=("CourseRating", "mean"),
        AveragePrice=("CoursePrice", "mean"),
    ).reset_index().sort_values("CourseRevenue", ascending=False)

    return {
        "users": users,
        "teachers": teachers,
        "courses": courses,
        "transactions": tx,
        "course_features": course_features,
        "monthly": monthly,
        "category": category,
        "audit_info": audit_info,
    }

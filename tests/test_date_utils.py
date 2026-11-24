import pandas as pd

from date_utils import parse_dmy_dates


def test_parse_dmy_dates_handles_ambiguous_day_month_values_explicitly():
    values = pd.Series(["5/10/2025", "13/1/2025", "25/10/2025"])
    parsed = parse_dmy_dates(values)

    assert parsed.tolist() == [
        pd.Timestamp("2025-10-05"),
        pd.Timestamp("2025-01-13"),
        pd.Timestamp("2025-10-25"),
    ]


def test_parse_dmy_dates_accepts_excel_datetime_values_and_rejects_invalid_text():
    values = pd.Series([pd.Timestamp("2025-03-04"), "not-a-date", None], dtype=object)
    parsed = parse_dmy_dates(values)

    assert parsed.iloc[0] == pd.Timestamp("2025-03-04")
    assert pd.isna(parsed.iloc[1])
    assert pd.isna(parsed.iloc[2])

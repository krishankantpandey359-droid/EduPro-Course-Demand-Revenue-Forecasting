"""Explicit parsing for the project's day/month/year transaction dates."""
from datetime import date, datetime

import numpy as np
import pandas as pd


def parse_dmy_dates(values):
    """Parse D/M/YYYY text or already-parsed Excel dates without format inference."""
    if not isinstance(values, pd.Series):
        values = pd.Series(values)

    def parse_value(value):
        if pd.isna(value):
            return pd.NaT
        if isinstance(value, (pd.Timestamp, datetime, date, np.datetime64)):
            return pd.Timestamp(value)
        return pd.to_datetime(
            str(value).strip(),
            format="%d/%m/%Y",
            errors="coerce",
        )

    return pd.Series(
        [parse_value(value) for value in values],
        index=values.index,
        name=values.name,
        dtype="datetime64[ns]",
    )

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd


def mask_contact_fields(frame):
    """Return a copy with email/phone-like fields redacted for display/export."""
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas DataFrame.")

    result = frame.copy()
    for column in result.columns:
        normalized = str(column).strip().lower()
        if any(token in normalized for token in ("email", "phone", "mobile", "telephone")):
            result[column] = result[column].map(
                lambda value: "[redacted]"
                if pd.notna(value) and str(value).strip()
                else value
            )
    return result

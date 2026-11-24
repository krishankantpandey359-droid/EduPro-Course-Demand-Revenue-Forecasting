import pandas as pd


def mask_contact_fields(frame):
    """Return a copy with person-name and contact fields redacted for display/export."""
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas DataFrame.")

    result = frame.copy()
    person_name_columns = {"username", "teachername", "fullname", "firstname", "lastname", "name"}
    contact_tokens = ("email", "phone", "mobile", "telephone")
    for column in result.columns:
        normalized = str(column).strip().lower()
        if normalized in person_name_columns or any(token in normalized for token in contact_tokens):
            result[column] = result[column].map(
                lambda value: "[redacted]"
                if pd.notna(value) and str(value).strip()
                else value
            )
    return result


def mask_user_identifiers(frame):
    """Return a copy with user foreign keys redacted before transaction export."""
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas DataFrame.")

    result = frame.copy()
    for column in result.columns:
        if str(column).strip().lower() in {"userid", "user_id"}:
            result[column] = result[column].map(
                lambda value: "[redacted]"
                if pd.notna(value) and str(value).strip()
                else value
            )
    return result

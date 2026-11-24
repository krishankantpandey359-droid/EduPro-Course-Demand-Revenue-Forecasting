import pandas as pd

from privacy import mask_contact_fields


def test_mask_contact_fields_redacts_email_and_phone_without_mutating_source():
    source = pd.DataFrame({
        "UserID": ["U1", "U2"],
        "Email": ["demo@example.invalid", ""],
        "PhoneNumber": ["0000000000", None],
        "Age": [21, 22],
    })

    safe = mask_contact_fields(source)

    assert safe["Email"].tolist() == ["[redacted]", ""]
    assert safe["PhoneNumber"].tolist() == ["[redacted]", None]
    assert source.loc[0, "Email"] == "demo@example.invalid"
    assert source.loc[0, "PhoneNumber"] == "0000000000"


def test_mask_contact_fields_leaves_non_contact_fields_unchanged():
    source = pd.DataFrame({"UserID": ["U1"], "UserName": ["demo_user"], "Age": [21]})

    safe = mask_contact_fields(source)

    pd.testing.assert_frame_equal(safe, source)

import pandas as pd

from privacy import mask_contact_fields, mask_user_identifiers


def test_mask_contact_fields_redacts_email_and_phone_without_mutating_source():
    source = pd.DataFrame({
        "UserID": ["U1", "U2"],
        "Email": ["demo@example.invalid", ""],
        "PhoneNumber": ["0000000000", None],
        "Age": [21, 22],
    })

    safe = mask_contact_fields(source)

    assert safe["Email"].tolist() == ["[redacted]", ""]
    assert safe["PhoneNumber"].iloc[0] == "[redacted]"
    assert pd.isna(safe["PhoneNumber"].iloc[1])
    assert source.loc[0, "Email"] == "demo@example.invalid"
    assert source.loc[0, "PhoneNumber"] == "0000000000"


def test_mask_contact_fields_redacts_person_names_but_preserves_non_personal_fields():
    source = pd.DataFrame({
        "UserID": ["U1"],
        "UserName": ["demo_user"],
        "TeacherName": ["Demo Teacher"],
        "CourseName": ["Python"],
        "Age": [21],
    })

    safe = mask_contact_fields(source)

    assert safe.loc[0, "UserName"] == "[redacted]"
    assert safe.loc[0, "TeacherName"] == "[redacted]"
    assert safe.loc[0, "CourseName"] == "Python"
    assert safe.loc[0, "Age"] == 21
    assert source.loc[0, "UserName"] == "demo_user"


def test_mask_user_identifiers_redacts_transaction_user_keys():
    source = pd.DataFrame({"UserID": ["U00001", "U00002"], "CourseID": ["C1", "C2"]})

    safe = mask_user_identifiers(source)

    assert safe["UserID"].tolist() == ["[redacted]", "[redacted]"]
    assert safe["CourseID"].tolist() == ["C1", "C2"]
    assert source["UserID"].tolist() == ["U00001", "U00002"]

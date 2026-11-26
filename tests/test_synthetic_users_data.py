from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_bundled_users_table_contains_only_generated_placeholders():
    users = pd.read_csv(ROOT / "data" / "Users.csv", dtype={"UserID": str})

    assert len(users) == 3000
    assert users["UserID"].is_unique
    assert users["UserID"].iloc[0] == "U00001"
    assert users["UserID"].iloc[-1] == "U03000"
    assert users["UserName"].str.fullmatch(r"learner_\d{5}").all()
    assert users["Email"].str.fullmatch(r"learner\d{5}@example\.invalid").all()
    assert users["Email"].str.endswith(".invalid").all()
    assert users["Age"].between(18, 65).all()
    assert set(users["Gender"].dropna().unique()).issubset({"Female", "Male"})


def test_bundled_transactions_still_reference_existing_synthetic_user_keys():
    users = pd.read_csv(ROOT / "data" / "Users.csv", dtype={"UserID": str})
    transactions = pd.read_csv(ROOT / "data" / "Transactions.csv", dtype={"UserID": str})

    assert transactions["UserID"].notna().all()
    assert transactions["UserID"].isin(users["UserID"]).all()

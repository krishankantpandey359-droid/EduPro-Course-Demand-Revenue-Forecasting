# Data source integrity

The four CSV files bundled in this repository are the original EduPro tables supplied for this project. The data provider confirmed to the project owner that the supplied names, email-like fields, and other example details are fictional and that the dataset is approved for public portfolio use. This confirmation is reported by the project owner; it is not an independent identity verification.

- Users.csv: supplied Users sheet export
- Teachers.csv: supplied Teachers table
- Courses.csv: supplied Courses table
- Transactions.csv: supplied Transactions sheet export

The original CSV contents are intentionally preserved. No names, email fields, identifiers, phone numbers, rows, or other source values are masked, rewritten, or fabricated by this project. Derived features and test fixtures are kept separate from the original source files.

The app validates sheet schemas, identifiers, dates, duplicates and missing values before analysis. Derived features are generated separately by the pipeline.

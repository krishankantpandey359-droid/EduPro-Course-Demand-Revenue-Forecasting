# Data source and privacy note

## Users table

`Users.csv` is an independently generated synthetic placeholder table created for this public portfolio repository. It contains 3,000 records. The stable `UserID` keys are retained in the `U00001`–`U03000` sequence so the bundled Transactions table continues to pass referential-integrity checks.

- User names are non-personal placeholders (`learner_00001`, etc.).
- Email addresses use the reserved `.invalid` domain and cannot identify or contact real people.
- Ages and gender categories are generated demo values, not observations about real users.
- No provider confirmation or licence claim is made for the previous person-like values.

## Other bundled tables

`Teachers.csv`, `Courses.csv`, and `Transactions.csv` remain the supplied project tables. Their provenance and publication rights have not been independently verified by this repository. Teacher names are masked in the dashboard's data explorer and CSV exports. User IDs are omitted from transaction exports.

## Privacy controls

- The Users table is used internally for schema and foreign-key validation.
- User-level rows are not displayed or downloadable from the Streamlit Data Explorer.
- Transaction exports omit `UserID`.
- Teacher-name and contact-like columns are redacted in Data Explorer previews and downloads.
- These controls apply to the Data Explorer, not to arbitrary copies of the source files.

Do not describe the whole dataset as independently verified or licensed. The synthetic Users table is a privacy-safe demonstration replacement, not evidence that the remaining supplied tables have verified provenance.

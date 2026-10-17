# Data source integrity

All bundled rows come only from data the user supplied in this conversation. No external datasets or fabricated records are included.

- Users.csv: supplied Users sheet export
- Teachers.csv: 60 teacher rows pasted directly by the user
- Courses.csv: supplied Courses table
- Transactions.csv: supplied Transactions sheet export

The app validates sheet schemas, identifiers, dates, duplicates and missing values before analysis. Original source values are preserved in these CSVs; derived features are generated separately by the pipeline.

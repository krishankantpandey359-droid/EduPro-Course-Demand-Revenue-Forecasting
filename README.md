# EduPro — Course Demand & Revenue Intelligence

A Python and Streamlit project built using only the four EduPro tables supplied by the user. No external datasets or synthetic records are used.

## Included Source Data

- `data/Users.csv` — 3,000 rows
- `data/Teachers.csv` — 60 rows from the supplied EduPro dataset
- `data/Courses.csv` — 60 rows
- `data/Transactions.csv` — 10,000 rows

These files contain the source data used by the project. The row counts refer to the records included in the current project.

## Source-data handling

The data provider confirmed to the project owner that the supplied dataset details are fictional and approved for public portfolio use. This is a provider confirmation reported by the project owner, not an independent verification. The four original CSV files are preserved exactly as supplied. The project does not mask or rewrite names, email-like fields, identifiers, or other source values, and it does not add fabricated records. Automated tests use the supplied files or separate in-memory fixtures only.

## Project Objective

The objective of this project is to analyse EduPro's recorded course demand and revenue. It includes data-quality checks, course-level and category-level analysis, historical revenue analysis, and a comparison of regression models for enrollment count and course revenue.

The results are exploratory and should not be treated as a guarantee of future performance.

## Requirements

- Python 3.10 or a compatible Python version
- Visual Studio Code
- Internet access for installing the required Python packages
- The packages listed in `requirements.txt`

## Run the Project in VS Code (Windows)

### 1. Open the Project

Open the cloned or downloaded `EduPro-Course-Demand-Revenue-Forecasting` project folder in Visual Studio Code.

### 2. Open the Terminal

In VS Code, select **Terminal → New Terminal**.

### 3. Create a Virtual Environment

```powershell
python -m venv .venv
```

### 4. Activate the Virtual Environment

```powershell
.venv\Scripts\activate
```

### 5. Install the Required Packages

```powershell
pip install -r requirements.txt
```

### 6. Run the Streamlit Dashboard

```powershell
streamlit run app.py
```

The dashboard should open in your default web browser. If it does not open automatically, follow the local URL displayed in the terminal.

## Using the Source Workbook

The application uses the bundled CSV files by default. If workbook upload is supported by the running application, you can upload the original EduPro Excel workbook through the sidebar.

The expected sheet names are:

- `Users`
- `Teachers`
- `Courses`
- `Transactions`

The common misspelling `Tranactions` is also recognized by the project, according to its current implementation.

## Project Features

- Dataset overview and record counts
- Required-column and schema checks
- Duplicate and key-integrity checks
- Checks for unmatched identifiers, invalid dates, missing amounts, and duplicate transaction IDs
- Course-level enrollment-event and revenue aggregation
- Teacher-course analysis using transaction `TeacherID` values
- Price, duration, and rating buckets
- Course-category comparisons
- Historical monthly revenue analysis
- Chronological monthly forecasting using Ridge, Random Forest, and HistGradientBoosting
- Comparison against a naive previous-month baseline using MAE, RMSE, and WAPE
- Data Explorer with downloadable CSV results
- Executive summary and research paper
- Data dictionary and supporting project outputs

The availability of individual features depends on the current project implementation and the data loaded into the application.

## Data Integrity and Interpretation

The analysis is based on the supplied EduPro data. No external dataset or fabricated records are intentionally introduced.

Derived values are calculated from the source tables:

- **EnrollmentCount:** The number of distinct `TransactionID` events associated with a course. This is not necessarily the number of distinct students enrolled.
- **CourseRevenue:** The sum of `Transactions.Amount` associated with a course.
- **Category revenue:** Revenue aggregated across courses in each category.
- **Historical monthly revenue:** Revenue grouped by transaction month.

Free-course transactions may contribute to recorded demand without contributing revenue.

Data-quality checks can identify technical issues, but they do not independently prove that every source value or business definition is correct. Repeated transactions should be reviewed to determine whether they represent separate enrollments, retries, refunds, or other events.

## Chronological Forecast Backtest

The repository now runs a reproducible chronological backtest on the bundled source tables in both GitHub Actions and the dashboard. It uses a rolling one-step-ahead design: the models are trained through September 2025, then evaluated on October–December 2025. Each test month uses only transaction history available before that month.

- Source data: 10,000 transaction rows and 60 courses.
- Full transaction date range: 1 January 2025 to 30 December 2025.
- Training period: January–September 2025 (after the required lag history, 360 course-month training rows per target).
- Holdout period: October–December 2025 (180 course-month test rows per target).
- Models: Ridge, Random Forest, and HistGradientBoosting.
- Baseline: previous month's value (naive lag-1).
- Metrics: MAE, RMSE, and WAPE. Revenue amounts use the source `Amount` units; the project does not infer a currency.

### Best chronological results

| Target | Best model | MAE | RMSE | WAPE | Naive lag-1 MAE | Naive lag-1 RMSE | Naive lag-1 WAPE |
|---|---|---:|---:|---:|---:|---:|---:|
| EnrollmentCount | Random Forest | 2.93 | 3.84 | 21.56% | 3.99 | 5.08 | 29.32% |
| CourseRevenue | Random Forest | 282.92 | 684.26 | 22.41% | 395.11 | 991.33 | 31.30% |

Random Forest had the lowest MAE for both targets in this held-out period. It improved on the naive lag-1 baseline for all three reported metrics. This is evidence of better performance on this specific three-month backtest, not proof of reliable future performance. The source contains only one calendar year, so seasonality and performance across other years cannot be established.

The older values in `outputs/model_comparison.csv` and earlier five-model cross-validation tables belong to a separate historical course-level experiment. They are not comparable with this transaction-level chronological forecast and must not be quoted as current chronological results.

### Reproduce the backtest

```bash
python scripts/run_chronological_backtest.py --test-months 3
pytest -q
```

The script writes `outputs/chronological_backtest.csv` and `outputs/chronological_backtest.json`. GitHub Actions uploads both files as the `edupro-chronological-backtest` artifact. The JSON records the source-file SHA-256 hashes, date window, sample sizes, model scores, and baseline metrics.

### Limitations

- The test covers only October–December 2025. A single 3-month window is not enough to establish stable performance.
- The rolling one-step-ahead test assumes actual prior-month activity is available before each subsequent month's forecast.
- EnrollmentCount means distinct transaction IDs, not verified unique students or completed enrolments.
- CourseRevenue is the sum of transaction Amount values. The source currency and business treatment of refunds or retries have not been independently verified.
- More historical years and an additional untouched period are needed before operational use.


## Recommendations

1. Review data-quality findings against the original workbook.
2. Confirm the meaning of repeated transactions before treating each event as an enrollment.
3. Analyse free-course demand separately from revenue.
4. Investigate the weak enrollment model results.
5. Check predictors for potential target leakage.
6. Evaluate future-period predictions using chronological train/test validation.
7. Collect additional course-level observations and historical periods before relying on forecasts for operational decisions.
8. Treat model metrics as exploratory evidence, not proof of causation or guaranteed future accuracy.

## Project Structure

```text
EduPro/
├── app.py
├── README.md
├── requirements.txt
├── data/
│   ├── Users.csv
│   ├── Teachers.csv
│   ├── Courses.csv
│   └── Transactions.csv
├── outputs/
├── reports/
│   ├── Executive_Summary.md
│   └── Research_Paper.md
└── src/
```

The structure above summarizes the main project files. The repository also includes supporting data-source notes, audit outputs, model comparison outputs, and reports.

## Conclusion

EduPro provides an exploratory workflow for analysing recorded course demand and revenue. It combines data-quality checks, course and category summaries, dashboard exploration, and regression baseline comparisons.

The current results indicate that enrollment prediction needs further improvement. Revenue models show stronger reported R² values, but their reliability for future periods remains to be established. The project should therefore be treated as an analytical starting point until data quality, feature construction, and chronological forecasting performance have been verified.

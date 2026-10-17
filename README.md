<<<<<<< HEAD
# EduPro — Course Demand & Revenue Intelligence

A Python and Streamlit project built using only the four EduPro tables supplied by the user. No external datasets or synthetic records are used.

## Included Source Data

- `data/Users.csv` — 3,000 rows
- `data/Teachers.csv` — 60 rows from the supplied EduPro dataset
- `data/Courses.csv` — 60 rows
- `data/Transactions.csv` — 10,000 rows

These files contain the source data used by the project. The row counts refer to the records included in the current project.

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

Extract `EduPro_Project_Submission.zip` and open the extracted project folder in Visual Studio Code.

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
- Comparison of Linear Regression, Ridge, Lasso, Random Forest, and Gradient Boosting
- Model evaluation using MAE, RMSE, and R²
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

## Model Results and Limitations

The project compares five regression models for two targets: `EnrollmentCount` and `CourseRevenue`.

In the current reported model comparison:

### EnrollmentCount

Ridge has the lowest cross-validated MAE among the tested models:

- **CV MAE:** 9.5694
- **CV RMSE:** 11.7840
- **CV R²:** -0.0707

All five tested models have negative cross-validated R² values for enrollment count. This indicates weak predictive performance under the current evaluation procedure.

### CourseRevenue

Gradient Boosting has the lowest cross-validated MAE among the tested models:

- **CV MAE:** 1540.0679
- **CV RMSE:** 3024.5781
- **CV R²:** 0.9847

Ridge has a slightly lower RMSE than Gradient Boosting in the reported comparison.

These scores are exploratory. The course-level dataset contains only 60 records, and the feature-generation process must be reviewed for potential target leakage. A high R² score alone does not establish reliable future forecasting performance.

Model scores may change when the data, features, or validation procedure changes. The values above should be checked against the latest `outputs/model_comparison.csv` before being quoted in a final submission.

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

This is the expected project structure. The actual folders and files in your project should be checked before submission.

## Conclusion

EduPro provides an exploratory workflow for analysing recorded course demand and revenue. It combines data-quality checks, course and category summaries, dashboard exploration, and regression baseline comparisons.

The current results indicate that enrollment prediction needs further improvement. Revenue models show stronger reported R² values, but their reliability for future periods remains to be established. The project should therefore be treated as an analytical starting point until data quality, feature construction, and chronological forecasting performance have been verified.
=======
# EduPro-Course-Demand-Revenue-Forecasting
Python and Streamlit project for course demand analysis, revenue forecasting, data quality checks, and machine learning model comparison using EduPro data.
>>>>>>> cebf19278a281d0e367f474955ca99d83964db3a

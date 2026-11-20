# Predictive Modeling for Course Demand and Revenue Forecasting on EduPro

## Abstract

This project analyses course activity and revenue using the supplied EduPro Users, Teachers, Courses, and Transactions tables. The current forecast evaluation uses a rolling one-step-ahead chronological backtest, comparing Ridge, Random Forest, and HistGradientBoosting with a naive previous-month baseline. On the October–December 2025 holdout, Random Forest outperforms the baseline for both transaction-event count and revenue. The evaluation covers one source year and one three-month window, so it does not establish stable future performance. No external dataset or fabricated source record is introduced.

## 1. Business Problem

Online learning platforms need to understand which courses attract learners and which courses contribute most to revenue. This information can support course planning, pricing reviews, category-level business decisions, and instructor onboarding.

The objective of this project is to analyse historical EduPro transaction data, calculate course-level enrollment counts and revenue, compare course categories, and evaluate baseline predictive models. The project provides evidence for further investigation and planning. It does not establish causal relationships or guarantee future business performance.

## 2. Dataset Description

The analysis uses the original EduPro workbook supplied by the user. It contains four sheets.

### 2.1 Users

The Users sheet contains the following fields:

- UserID
- UserName
- Age
- Gender
- Email

The sheet provides user-related information that can support data validation and analysis of the platform's user records.

### 2.2 Teachers

The Teachers sheet contains:

- TeacherID
- TeacherName
- Age
- Gender
- Expertise
- YearsOfExperience
- TeacherRating

These fields describe teacher characteristics, areas of expertise, experience, and ratings. Teacher information can be linked with courses and transactions through the relevant identifiers.

### 2.3 Courses

The Courses sheet contains:

- CourseID
- CourseName
- CourseCategory
- CourseType
- CourseLevel
- CoursePrice
- CourseDuration
- CourseRating

These attributes describe the available courses, their categories, course types, levels, prices, durations, and ratings.

### 2.4 Transactions

The Transactions sheet contains:

- TransactionID
- UserID
- CourseID
- TransactionDate
- Amount
- PaymentMethod
- TeacherID

Transaction records provide the historical activity used to calculate recorded enrollment counts and revenue. The meaning of repeated transactions must be confirmed before every transaction is treated as a separate enrollment.

The dashboard reports 3,000 user records, 60 teacher records, 60 course records, and 10,000 transaction records. These counts describe the records loaded into the current analysis. Data-quality checks are used to examine identifiers, duplicate transaction IDs, date validity, missing amounts, and required columns.

## 3. Data Preparation and Audit

Data preparation is necessary to make the analysis consistent and reproducible. The workflow checks that the expected sheets and columns are available, parses transaction dates using day-first interpretation based on the supplied date examples, and checks relationships between the transaction table and the user, course, and teacher tables.

The data audit examines:

- Missing required columns.
- Duplicate transaction identifiers.
- Invalid or unparseable transaction dates.
- Missing transaction amounts.
- Transaction records with unmatched UserID, CourseID, or TeacherID values.

Course-level aggregates are joined with the course catalogue so that courses without recorded transactions can remain in the course-level analysis. The audit results should be interpreted as the output of the current data-processing run; they do not establish that every business rule or source-data value is correct.

No source value should be silently changed merely because it appears unusual. Potential issues should be documented and confirmed against the original workbook.

## 4. Feature Engineering

Feature engineering converts the source data into variables suitable for analysis and predictive modelling.

The workflow derives course-level EnrollmentCount from transaction records and CourseRevenue from the sum of transaction amounts associated with each course. Category-level revenue is calculated by aggregating course revenue within each course category.

Additional derived features may include:

- Price bands based on course prices.
- Duration buckets based on course duration.
- Rating tiers based on course ratings.
- Course category, type, and level as categorical features.
- Teacher experience and rating summaries linked to the relevant courses, where the available data and implementation support these features.

The target variables are EnrollmentCount and CourseRevenue. EnrollmentCount is defined in the current workflow as the number of distinct TransactionID values associated with a course. CourseRevenue is defined as the sum of Amount values associated with that course.

These definitions measure recorded transaction activity. If the platform contains retries, refunds, repeated purchases, or other transaction types, the business definition of a true enrollment may differ from the current calculation.

## 5. Modelling and Metrics

The current forecasting unit is the course-month. For each course and calendar month, the pipeline calculates EnrollmentCount as the number of distinct TransactionID values and CourseRevenue as the sum of transaction Amount values. Predictors use CourseID, month-of-year sine/cosine features, lagged target values for the previous one, two and three months, and a three-month rolling mean shifted so it contains prior months only.

The evaluated models are Ridge Regression, Random Forest Regressor, and HistGradientBoosting Regressor. The baseline predicts the next month's value using the previous month's observed value. The rolling one-step-ahead design permits an observed holdout month to become historical input for the following month. It does not use the same month's target as a predictor.

The evaluation metrics are:

- MAE: mean absolute prediction error.
- RMSE: square root of the mean squared prediction error, which gives larger errors more weight.
- WAPE: sum of absolute errors divided by the sum of absolute actual values.

### 5.1 Chronological Holdout Design

The bundled transaction table contains 10,000 records dated from 1 January 2025 to 30 December 2025, with 60 courses in the course catalogue. The training period ends in September 2025. The test period is October–December 2025. After lag-history rows are removed, there are 360 course-month training rows and 180 course-month test rows per target.

### 5.2 Chronological Results

| Target | Model | MAE | RMSE | WAPE |
|---|---|---:|---:|---:|
| CourseRevenue | Random Forest | 282.92 | 684.26 | 22.41% |
| CourseRevenue | HistGradientBoosting | 286.06 | 708.83 | 22.66% |
| CourseRevenue | Ridge | 437.87 | 779.58 | 34.68% |
| EnrollmentCount | Random Forest | 2.93 | 3.84 | 21.56% |
| EnrollmentCount | Ridge | 2.99 | 3.86 | 21.98% |
| EnrollmentCount | HistGradientBoosting | 3.18 | 4.13 | 23.40% |

The naive previous-month baseline produced the following results:

| Target | Naive lag-1 MAE | Naive lag-1 RMSE | Naive lag-1 WAPE |
|---|---:|---:|---:|
| CourseRevenue | 395.11 | 991.33 | 31.30% |
| EnrollmentCount | 3.99 | 5.08 | 29.32% |

Random Forest had the lowest MAE for both targets and outperformed the naive baseline on MAE, RMSE and WAPE in this specific holdout. This does not prove that the same improvement will persist in other periods, other markets or future operating conditions.

### 5.3 Interpretation and Scope

EnrollmentCount measures transaction events identified by distinct TransactionID values. It is not necessarily a count of unique learners, paid enrollments or completed enrollments. CourseRevenue is the sum of transaction Amount values. The source currency and accounting treatment of refunds, retries or repeated purchases have not been independently verified.

The older five-model course-level cross-validation results in `outputs/model_comparison.csv` belong to a separate experiment with a different unit of analysis. They are not directly comparable with the transaction-level monthly chronological results in this section and should not be presented as the current forecast validation.

## 6. Dashboard

The Streamlit dashboard provides an interactive interface for exploring the EduPro data and model results. Its intended analytical areas include:

- Dataset overview and record counts.
- Course and category analysis.
- Historical revenue analysis.
- Course-level demand and revenue comparison.
- Data-quality audit.
- Table exploration and data export.
- Regression model comparison.

The dashboard allows the user to inspect different aspects of the supplied data without manually calculating every aggregate. The displayed results depend on the workbook loaded and the analysis executed at runtime.

## 7. Limitations

The project has several limitations that should be considered before using the results for business decisions.

### 7.1 Small Course-Level Sample

The course catalogue contains 60 course records. This is a limited sample for comparing multiple predictive models and may result in unstable performance estimates.

### 7.2 Enrollment Definition

The current workflow defines EnrollmentCount as the number of distinct transaction IDs associated with a course. Repeated user-course transactions may represent new enrollments, retries, refunds, or other events. These possibilities should be checked before using the count as a business measure of enrollment demand.

### 7.3 Free and Paid Courses

Free courses may generate recorded transaction activity while contributing zero revenue. Enrollment demand and revenue should therefore be analysed separately, and free and paid courses may require different evaluation approaches.

### 7.4 Revenue and Price Relationship

Course revenue is calculated from transaction amounts. If transaction amounts are strongly related to listed course prices, a revenue model may learn this relationship rather than broader patterns of future demand. This association should not be interpreted as evidence of a causal effect.

### 7.5 Validation and Potential Leakage

The current workflow uses historical lag and rolling features shifted to exclude the target month. The three-month test window is still limited, and rolling one-step-ahead evaluation assumes actual values become available each month. The currency and business meaning of Amount and repeated transactions require confirmation.

### 7.6 Historical Coverage

The bundled transaction dates span 1 January 2025 to 30 December 2025. One calendar year is insufficient to establish recurring annual seasonality. A longer history and another untouched evaluation period are required.

### 7.7 Data Quality and Business Meaning

Automated checks can identify technical issues such as invalid dates, missing amounts, and unmatched identifiers. They cannot independently establish that every source value is correct or that the business meaning of each transaction has been interpreted correctly.

## 8. Recommendations

1. Verify the source workbook and retain the original records for reproducibility.
2. Review data-audit findings and resolve confirmed data-quality problems with reference to the original source.
3. Confirm whether repeated user-course transactions represent distinct enrollments.
4. Analyse free and paid course demand separately from revenue.
5. Extend the chronological backtest to more years and a later untouched holdout.
6. Monitor future monthly performance and preserve each evaluation dataset and model report.
7. Check all predictors for target leakage and ensure that future information is not used during training.
8. Collect more historical periods and additional course-level observations before relying on the models for business planning.
9. Treat feature importance and model relationships as associations, not proof of causation.
10. Re-run the complete workflow and preserve the dataset version, model metrics, and audit output used for the final report.

## Conclusion

This project provides an initial, reproducible workflow for analysing course demand and revenue on EduPro using the user-supplied workbook. It combines source-data auditing, course and category aggregation, feature engineering, interactive exploration, and regression baseline comparison.

The October–December 2025 chronological holdout shows that Random Forest outperforms the naive previous-month baseline for both transaction-event count and revenue. One year of history and one test window are not enough to establish stable performance. More data and business-definition checks are needed before operational use.

The project is best regarded as an exploratory analytical foundation. More historical data, clear transaction definitions, leakage checks, and chronological validation are required before using the models to guide operational decisions.
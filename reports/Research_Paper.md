# Predictive Modeling for Course Demand and Revenue Forecasting on EduPro

## Abstract

This project presents a data analysis and predictive modelling workflow for studying course demand and revenue on EduPro. It uses the user-supplied workbook containing Users, Teachers, Courses, and Transactions sheets. The analysis examines recorded enrollment activity, course revenue, category-level revenue, data quality, and baseline regression models. Five models are compared using cross-validated Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and R². Ridge gives the lowest MAE among the tested models for EnrollmentCount, while Gradient Boosting gives the lowest MAE for CourseRevenue. However, the enrollment model results are weak, and the high revenue-model R² requires further validation before operational use. No external dataset or fabricated record is introduced.

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

The dashboard compares five regression models:

1. Linear Regression
2. Ridge Regression
3. Lasso Regression
4. Random Forest Regressor
5. Gradient Boosting Regressor

Model performance is evaluated using cross-validated MAE, RMSE, and R². MAE measures the average absolute prediction error, while RMSE gives greater weight to larger errors. R² measures performance relative to a mean-based reference under the evaluation procedure; a negative R² indicates performance worse than that reference.

### 5.1 EnrollmentCount Results

| Model | CV MAE | CV RMSE | CV R² |
|---|---:|---:|---:|
| Ridge | 9.5694 | 11.7840 | -0.0707 |
| Random Forest | 9.8971 | 12.4756 | -0.1875 |
| Gradient Boosting | 11.2342 | 13.4844 | -0.5656 |
| Lasso | 11.6820 | 14.5118 | -0.5472 |
| Linear Regression | 13.2697 | 16.7683 | -1.0048 |

Ridge produces the lowest MAE among the five tested models for EnrollmentCount. However, all five models have negative cross-validated R² values. This indicates that enrollment prediction is weak under the current evaluation procedure. The results do not support claiming that the current models provide reliable course-demand forecasts.

Further work should examine the features used, the distribution of enrollment counts, the cross-validation setup, and whether the small course-level sample is sufficient for modelling.

### 5.2 CourseRevenue Results

| Model | CV MAE | CV RMSE | CV R² |
|---|---:|---:|---:|
| Gradient Boosting | 1540.0679 | 3024.5781 | 0.9847 |
| Ridge | 1977.2276 | 2834.8483 | 0.9809 |
| Random Forest | 2214.2506 | 4581.5693 | 0.9705 |
| Lasso | 2827.8159 | 3802.1004 | 0.9590 |
| Linear Regression | 2830.1759 | 3804.5594 | 0.9590 |

Gradient Boosting produces the lowest MAE among the tested models for CourseRevenue. Its cross-validated R² is 0.9847. Ridge has a slightly lower RMSE, so the best model depends on the metric used to evaluate errors.

The high R² should not be treated as proof of reliable future revenue forecasting. Only 60 course-level records are available, and the feature construction and validation procedure must be examined for possible target leakage. Revenue is also closely related to transaction amounts and course prices, which can make some relationships mechanically strong.

### 5.3 Interpretation of Model Comparison

The current model comparison provides different conclusions for the two targets. EnrollmentCount is difficult to predict using the tested features and current evaluation setup. CourseRevenue has much higher R² values, but further validation is needed to determine how well these results generalise to unseen courses or future periods.

A chronological train/test split is recommended for future forecasting. Feature engineering should use only information that would have been available at the forecast date. Any feature that directly contains or indirectly reveals the target must be excluded from the predictors.

The model results should therefore be described as exploratory baseline comparisons rather than production-ready forecasts.

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

Cross-validation results depend on how data and features are prepared. Any feature that uses the target or information unavailable at prediction time can lead to overly optimistic scores. The complete feature-generation and validation process should be checked before the model is used for forecasting.

### 7.6 Historical Coverage

The supplied transaction examples include dates from 2025. The complete date range should be verified directly from the loaded workbook. Robust seasonal forecasting requires sufficient historical coverage and chronological evaluation.

### 7.7 Data Quality and Business Meaning

Automated checks can identify technical issues such as invalid dates, missing amounts, and unmatched identifiers. They cannot independently establish that every source value is correct or that the business meaning of each transaction has been interpreted correctly.

## 8. Recommendations

1. Verify the source workbook and retain the original records for reproducibility.
2. Review data-audit findings and resolve confirmed data-quality problems with reference to the original source.
3. Confirm whether repeated user-course transactions represent distinct enrollments.
4. Analyse free and paid course demand separately from revenue.
5. Evaluate enrollment prediction further because all tested models currently have negative cross-validated R².
6. Use chronological train/test evaluation for future-period forecasting.
7. Check all predictors for target leakage and ensure that future information is not used during training.
8. Collect more historical periods and additional course-level observations before relying on the models for business planning.
9. Treat feature importance and model relationships as associations, not proof of causation.
10. Re-run the complete workflow and preserve the dataset version, model metrics, and audit output used for the final report.

## Conclusion

This project provides an initial, reproducible workflow for analysing course demand and revenue on EduPro using the user-supplied workbook. It combines source-data auditing, course and category aggregation, feature engineering, interactive exploration, and regression baseline comparison.

The current results show that enrollment prediction remains weak under the tested evaluation procedure, while the revenue models achieve much higher R² values. However, the small course-level sample and the need to verify feature construction and validation prevent these scores from being treated as proof of reliable future forecasting.

The project is best regarded as an exploratory analytical foundation. More historical data, clear transaction definitions, leakage checks, and chronological validation are required before using the models to guide operational decisions.
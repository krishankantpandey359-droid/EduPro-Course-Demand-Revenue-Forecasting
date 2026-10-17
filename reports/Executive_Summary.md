# EduPro — Executive Summary

## Objective

The objective of this project is to analyse EduPro's supplied platform data to understand recorded course demand, revenue, and category-level performance. The project also compares baseline regression models for course-level enrollment count and revenue. The findings are intended to support business analysis and further investigation, not to guarantee future performance.

## Dataset

The analysis uses the original EduPro workbook supplied by the user, containing four sheets:

- **Users:** UserID, UserName, Age, Gender, Email.
- **Teachers:** TeacherID, TeacherName, Age, Gender, Expertise, YearsOfExperience, TeacherRating.
- **Courses:** CourseID, CourseName, CourseCategory, CourseType, CourseLevel, CoursePrice, CourseDuration, CourseRating.
- **Transactions:** TransactionID, UserID, CourseID, TransactionDate, Amount, PaymentMethod, TeacherID.

The current dashboard reports 3,000 user records, 60 teacher records, 60 course records, and 10,000 transaction records. These counts refer to the records loaded in the current analysis.

## Main Outputs

- Dataset overview and record counts.
- Course-level recorded enrollment counts and revenue.
- Category-level demand and revenue comparisons.
- Historical monthly revenue analysis.
- Data-quality checks for required columns, unmatched identifiers, invalid dates, missing amounts, and duplicate transaction IDs.
- Comparison of Linear Regression, Ridge, Lasso, Random Forest, and Gradient Boosting using MAE, RMSE, and R².
- Data exploration and downloadable model-comparison results.

## Model Results

### EnrollmentCount

Ridge produced the lowest cross-validated MAE among the tested models.

- **Best model by MAE:** Ridge
- **CV MAE:** 9.5694
- **CV RMSE:** 11.7840
- **CV R²:** -0.0707

All five tested models produced negative cross-validated R² values for EnrollmentCount. This indicates weak performance under the current evaluation procedure, so the results do not support claiming reliable enrollment forecasting.

### CourseRevenue

Gradient Boosting produced the lowest cross-validated MAE among the tested models.

- **Best model by MAE:** Gradient Boosting
- **CV MAE:** 1540.0679
- **CV RMSE:** 3024.5781
- **CV R²:** 0.9847

Ridge produced a slightly lower RMSE than Gradient Boosting. The high revenue-model R² should be interpreted cautiously because the course-level sample contains only 60 records, and potential data leakage and validation limitations still need to be checked.

## Data Integrity and Interpretation

Only the user's supplied EduPro data is used; no external dataset or fabricated records are introduced.

- EnrollmentCount is calculated from distinct transaction IDs associated with each course.
- CourseRevenue is calculated as the sum of transaction amounts associated with each course.
- Category revenue is aggregated from course-level revenue.
- Free-course transactions may contribute to recorded demand while contributing zero revenue.
- Data-quality checks identify technical issues but do not independently establish that every source value or business definition is correct.
- Repeated transactions should be reviewed to determine whether they represent distinct enrollments, retries, refunds, or other events.
- Historical totals describe recorded activity and should not be confused with future forecasts.

## Limitations

The course-level dataset contains only 60 records, which limits the strength and stability of the model comparison. The negative R² results for EnrollmentCount indicate that further work is needed before relying on the tested models for demand prediction.

The high R² for CourseRevenue is not proof of reliable future forecasting. The feature-generation process should be reviewed for target leakage, and future predictions should be evaluated using chronological train/test validation. The full transaction date range should also be verified before making claims about historical coverage or seasonality.

## Recommendations

1. Review the data-quality audit and resolve confirmed issues against the original workbook.
2. Confirm the business meaning of repeated transactions before treating every transaction as a separate enrollment.
3. Analyse free-course demand separately from revenue.
4. Investigate the weak EnrollmentCount model results and improve the feature set where justified.
5. Check all model predictors for target leakage.
6. Use chronological validation to evaluate future-period forecasts.
7. Collect more course-level observations and historical periods before using the models for operational decisions.
8. Treat model metrics and feature relationships as exploratory evidence, not proof of causation.

## Conclusion

The EduPro project provides a starting point for analysing recorded course demand and revenue through data auditing, course and category summaries, dashboard exploration, and regression baseline comparisons.

The current results show that enrollment prediction remains weak under the tested evaluation procedure, while revenue models achieve higher R² values that require further validation. The project should be treated as an exploratory analytical workflow until the feature construction, data-quality findings, and chronological forecasting performance have been verified.
# Data Dictionary

## Source tables
- Users: UserID, UserName, Age, Gender, Email
- Teachers: TeacherID, TeacherName, Age, Gender, Expertise, YearsOfExperience, TeacherRating
- Courses: CourseID, CourseName, CourseCategory, CourseType, CourseLevel, CoursePrice, CourseDuration, CourseRating
- Transactions: TransactionID, UserID, CourseID, TransactionDate, Amount, PaymentMethod, TeacherID

## Derived course-level fields
- EnrollmentCount: distinct TransactionID count per CourseID (proxy based on transaction events)
- CourseRevenue: sum of Transactions.Amount per CourseID
- UniqueUsers: distinct UserID count per course
- RevenuePerEnrollment: CourseRevenue / EnrollmentCount where count > 0
- AvgTeacherExperience / AvgTeacherRating: average over distinct course-teacher pairs found in transaction records
- PriceBand, DurationBucket, RatingTier: categories derived from supplied numeric columns

Source CSVs are preserved; derived fields are produced at runtime and do not overwrite source values.

## Demonstration data and safe display

The project owner confirms that names, email-like values, phone-like values, and identifiers are dummy values created for this portfolio project. This statement does not establish the source or redistribution licence of every other dataset field. The Streamlit Data Explorer redacts columns whose names identify email, phone, mobile, or telephone contact information from both on-screen previews and CSV downloads. Original source CSVs are preserved unchanged in the repository.

## Transaction date format

Text dates in `Transactions.TransactionDate` are parsed explicitly as day/month/year (`D/M/YYYY`). Excel cells already stored as dates are accepted as dates. Invalid or missing values are rejected by the pipeline rather than silently guessed.

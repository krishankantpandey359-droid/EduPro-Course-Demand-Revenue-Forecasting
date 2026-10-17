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

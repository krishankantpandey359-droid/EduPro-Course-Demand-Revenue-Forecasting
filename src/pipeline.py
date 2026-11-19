from pathlib import Path
import pandas as pd
import numpy as np
REQUIRED={
 'Users':['UserID','UserName','Age','Gender','Email'],
 'Teachers':['TeacherID','TeacherName','Age','Gender','Expertise','YearsOfExperience','TeacherRating'],
 'Courses':['CourseID','CourseName','CourseCategory','CourseType','CourseLevel','CoursePrice','CourseDuration','CourseRating'],
 'Transactions':['TransactionID','UserID','CourseID','TransactionDate','Amount','PaymentMethod','TeacherID']}
def read_workbook(file):
 xls=pd.ExcelFile(file); out={}
 for raw in xls.sheet_names:
  name={'Tranactions':'Transactions','Transaction':'Transactions','transactions':'Transactions','users':'Users','teachers':'Teachers','courses':'Courses'}.get(raw,raw)
  out[name]=pd.read_excel(xls,sheet_name=raw)
 return out
def read_bundled(data_dir):
 out={}
 for n in ('Users','Teachers','Courses','Transactions'):
  f=Path(data_dir)/f'{n}.csv'
  if f.exists(): out[n]=pd.read_csv(f)
 return out
def audit(sheets):
 rows=[]
 for name,cols in REQUIRED.items():
  if name not in sheets: rows.append({'Sheet':name,'Status':'MISSING','Rows':0,'Missing columns':', '.join(cols),'Duplicate rows':None}); continue
  d=sheets[name]; miss=[c for c in cols if c not in d.columns]
  rows.append({'Sheet':name,'Status':'OK' if not miss else 'COLUMN CHECK NEEDED','Rows':len(d),'Missing columns':', '.join(miss) or 'None','Duplicate rows':int(d.duplicated().sum())})
 return pd.DataFrame(rows)
def prepare(sheets):
 missing=[n for n in REQUIRED if n not in sheets]
 if missing: raise ValueError('Missing sheet(s): '+', '.join(missing)+'. Upload the original workbook with all four sheets; no missing rows will be fabricated.')
 for n,cols in REQUIRED.items():
  miss=[c for c in cols if c not in sheets[n].columns]
  if miss: raise ValueError(f'{n} is missing columns: {miss}')
 users,teachers,courses,tx=[sheets[n].copy() for n in ('Users','Teachers','Courses','Transactions')]
 for d,cols in [(users,['UserID']),(teachers,['TeacherID']),(courses,['CourseID']),(tx,['TransactionID','UserID','CourseID','TeacherID'])]:
  for c in cols: d[c]=d[c].astype('string').str.strip()
 for c in ['Age']: users[c]=pd.to_numeric(users[c],errors='coerce')
 for c in ['CoursePrice','CourseDuration','CourseRating']: courses[c]=pd.to_numeric(courses[c],errors='coerce')
 for c in ['YearsOfExperience','TeacherRating','Age']: teachers[c]=pd.to_numeric(teachers[c],errors='coerce')
 tx['Amount']=pd.to_numeric(tx['Amount'],errors='coerce')
 tx['TransactionDate']=pd.to_datetime(tx['TransactionDate'],errors='coerce',dayfirst=True)
 audit_info={'unmatched_user_rows':int((~tx.UserID.isin(users.UserID)).sum()),'unmatched_course_rows':int((~tx.CourseID.isin(courses.CourseID)).sum()),'unmatched_teacher_rows':int((~tx.TeacherID.isin(teachers.TeacherID)).sum()),'invalid_dates':int(tx.TransactionDate.isna().sum()),'missing_amounts':int(tx.Amount.isna().sum()),'duplicate_transaction_ids':int(tx.TransactionID.duplicated().sum())}
 # Fail fast on invalid transaction keys and measures. The audit report remains
 # available for inspection, but invalid rows must not silently enter forecasts.
 for name, frame, key in [('Users', users, 'UserID'), ('Teachers', teachers, 'TeacherID'), ('Courses', courses, 'CourseID')]:
  if frame[key].isna().any() or frame[key].eq('').any():
   raise ValueError(f"{name} contains missing or blank {key} values.")
  if frame[key].duplicated().any():
   raise ValueError(f"{name} contains duplicate {key} values.")
 for key in ['TransactionID','UserID','CourseID','TeacherID']:
  if tx[key].isna().any() or tx[key].eq('').any():
   raise ValueError(f"Transactions contain missing or blank {key} values.")
 if audit_info['duplicate_transaction_ids']:
  raise ValueError("Transactions contain duplicate TransactionID values.")
 if audit_info['invalid_dates']:
  raise ValueError(f"Transactions contain {audit_info['invalid_dates']} invalid or missing TransactionDate values.")
 if audit_info['missing_amounts'] or not np.isfinite(tx['Amount'].to_numpy(dtype=float)).all():
  raise ValueError("Transactions contain missing, non-numeric, or non-finite Amount values.")
 if audit_info['unmatched_user_rows'] or audit_info['unmatched_course_rows'] or audit_info['unmatched_teacher_rows']:
  raise ValueError("Transactions contain UserID, CourseID, or TeacherID references absent from their source tables.")
 agg=tx.groupby('CourseID').agg(EnrollmentCount=('TransactionID','nunique'),CourseRevenue=('Amount',lambda s:s.sum(min_count=1)),UniqueUsers=('UserID','nunique'),PaidTransactions=('Amount',lambda s:int((s.fillna(0)>0).sum())),FreeTransactions=('Amount',lambda s:int((s.fillna(0)==0).sum()))).reset_index()
 cf=courses.merge(agg,on='CourseID',how='left',validate='one_to_one')
 for c in ['EnrollmentCount','CourseRevenue','UniqueUsers','PaidTransactions','FreeTransactions']: cf[c]=cf[c].fillna(0)
 cf['RevenuePerEnrollment']=np.where(cf.EnrollmentCount>0,cf.CourseRevenue/cf.EnrollmentCount,0)
 cf['PriceBand']=pd.cut(cf.CoursePrice,bins=[-np.inf,0,100,250,400,np.inf],labels=['Free/Zero','Low','Medium','High','Premium']).astype('string')
 cf['DurationBucket']=pd.cut(cf.CourseDuration,bins=[-np.inf,5,15,30,np.inf],labels=['Very Short (<=5)','Short (5-15)','Medium (15-30)','Long (>30)']).astype('string')
 cf['RatingTier']=pd.cut(cf.CourseRating,bins=[-np.inf,2,3.5,4.25,np.inf],labels=['Low','Moderate','Good','High']).astype('string')
 tt=tx[['CourseID','TeacherID']].drop_duplicates().merge(teachers,on='TeacherID',how='left')
 ta=tt.groupby('CourseID').agg(TeacherCount=('TeacherID','nunique'),AvgTeacherExperience=('YearsOfExperience','mean'),AvgTeacherRating=('TeacherRating','mean'),TeacherExpertise=('Expertise',lambda s:' | '.join(sorted(set(s.dropna().astype(str)))))).reset_index()
 cf=cf.merge(ta,on='CourseID',how='left')
 cf['TeacherCount']=cf.TeacherCount.fillna(0); cf['AvgTeacherExperience']=cf.AvgTeacherExperience.fillna(teachers.YearsOfExperience.median()); cf['AvgTeacherRating']=cf.AvgTeacherRating.fillna(teachers.TeacherRating.median()); cf['TeacherExpertise']=cf.TeacherExpertise.fillna('Unknown')
 monthly=tx.dropna(subset=['TransactionDate']).assign(Month=lambda d:d.TransactionDate.dt.to_period('M').astype(str)).groupby('Month').agg(Enrollments=('TransactionID','nunique'),Revenue=('Amount',lambda s:s.sum(min_count=1)),UniqueUsers=('UserID','nunique')).reset_index()
 category=cf.groupby('CourseCategory',dropna=False).agg(CourseCount=('CourseID','nunique'),EnrollmentCount=('EnrollmentCount','sum'),CourseRevenue=('CourseRevenue','sum'),AverageCourseRating=('CourseRating','mean'),AveragePrice=('CoursePrice','mean')).reset_index().sort_values('CourseRevenue',ascending=False)
 return {'users':users,'teachers':teachers,'courses':courses,'transactions':tx,'course_features':cf,'monthly':monthly,'category':category,'audit_info':audit_info}

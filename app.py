from pathlib import Path
import sys,streamlit as st,plotly.express as px
ROOT=Path(__file__).parent; sys.path.insert(0,str(ROOT/'src'))
from pipeline import read_workbook,read_bundled,audit,prepare
from modeling import fit_all
from privacy import mask_contact_fields
st.set_page_config(page_title='EduPro Demand & Revenue',page_icon='📚',layout='wide')
st.title('📚 EduPro | Course Demand & Revenue Intelligence')
st.caption('Portfolio demonstration using project data. Person-like fields are dummy values. Email and phone fields are masked in data previews and CSV exports.')
upload=st.sidebar.file_uploader('Upload original EduPro workbook (.xlsx)',type=['xlsx'])
try: sheets=read_workbook(upload) if upload else read_bundled(ROOT/'data')
except Exception as e: st.error(f'Workbook could not be read: {e}'); st.stop()
st.subheader('Data integrity check'); st.dataframe(audit(sheets),use_container_width=True,hide_index=True)
missing=[n for n in ['Users','Teachers','Courses','Transactions'] if n not in sheets]
if missing:
 st.warning('Full analysis needs these source sheets: '+', '.join(missing)+'. No records were fabricated. Upload the original workbook containing all four sheets.'); st.stop()
try: r=prepare(sheets)
except Exception as e: st.error(str(e)); st.stop()
users,teachers,courses,tx,cf,monthly,cat=[r[k] for k in ['users','teachers','courses','transactions','course_features','monthly','category']]
a,b,c,d=st.columns(4); a.metric('Users',f'{len(users):,}'); b.metric('Teachers',f'{len(teachers):,}'); c.metric('Courses',f'{len(courses):,}'); d.metric('Transactions',f'{len(tx):,}')
a,b,c,d=st.columns(4); a.metric('Recorded enrollments',f'{tx.TransactionID.nunique():,}'); b.metric('Recorded revenue',f'{tx.Amount.sum(min_count=1):,.2f}'); c.metric('Categories',f'{courses.CourseCategory.nunique():,}'); d.metric('Unmatched course rows',f"{r['audit_info']['unmatched_course_rows']:,}")
tabs=st.tabs(['Overview','Course analysis','Categories','Model comparison','Data audit','Explore data'])
with tabs[0]:
 x,y=st.columns(2)
 with x: st.plotly_chart(px.bar(cat.sort_values('EnrollmentCount',ascending=False),x='CourseCategory',y='EnrollmentCount',title='Recorded enrollments by category'),use_container_width=True)
 with y: st.plotly_chart(px.bar(cat.sort_values('CourseRevenue',ascending=False),x='CourseCategory',y='CourseRevenue',title='Recorded revenue by category'),use_container_width=True)
 if not monthly.empty: st.plotly_chart(px.line(monthly,x='Month',y='Revenue',markers=True,title='Historical monthly revenue'),use_container_width=True)
with tabs[1]:
 st.info('These are historical totals, not future predictions.')
 st.plotly_chart(px.scatter(cf,x='EnrollmentCount',y='CourseRevenue',color='CourseCategory',hover_name='CourseName',title='Course demand vs revenue'),use_container_width=True)
 st.dataframe(cf[['CourseID','CourseName','CourseCategory','CourseType','CourseLevel','CoursePrice','EnrollmentCount','CourseRevenue','RevenuePerEnrollment']].sort_values('CourseRevenue',ascending=False),use_container_width=True,hide_index=True)
with tabs[2]:
 st.dataframe(cat,use_container_width=True,hide_index=True); st.plotly_chart(px.bar(cat,x='CourseCategory',y='AverageCourseRating',title='Average course rating by category'),use_container_width=True)
with tabs[3]:
 st.warning('This is a chronological historical backtest, not a guarantee of future performance. The latest 3 months are held out; prior-month transaction history is used as the baseline.')
 if st.button('Run chronological forecast backtest'):
  try:
   with st.spinner('Building monthly course history and evaluating holdout months...'): scores=fit_all(tx, courses, test_months=3)
   st.dataframe(scores,use_container_width=True,hide_index=True); st.download_button('Download chronological backtest CSV',scores.to_csv(index=False).encode(),'chronological_backtest.csv','text/csv')
  except Exception as e: st.error(f'Forecast backtest failed: {e}')
 st.markdown('Models: Ridge, Random Forest and HistGradientBoosting. Metrics: MAE, RMSE and WAPE. Each is compared with a naive previous-month baseline. Historical totals elsewhere in the app remain descriptive, not forecasts.')
with tabs[4]: st.json(r['audit_info']); st.markdown('Unmatched IDs and invalid records are reported; source records are not silently discarded.')
with tabs[5]:
 name=st.selectbox('Choose a table',['Users','Teachers','Courses','Transactions','Course-level features']); obj={'Users':users,'Teachers':teachers,'Courses':courses,'Transactions':tx,'Course-level features':cf}[name]
 safe_obj = mask_contact_fields(obj)
 st.dataframe(safe_obj,use_container_width=True,hide_index=True)
 st.download_button('Download selected table CSV (contact fields masked)',safe_obj.to_csv(index=False).encode(),name.lower().replace(' ','_')+'.csv','text/csv')

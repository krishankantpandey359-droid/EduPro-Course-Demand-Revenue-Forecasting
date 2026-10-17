import numpy as np, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import KFold,cross_validate
from sklearn.linear_model import LinearRegression,Ridge,Lasso
from sklearn.ensemble import RandomForestRegressor,GradientBoostingRegressor

def make_pipe(X,model):
 cats=X.select_dtypes(include=['object','string','category']).columns.tolist(); nums=[c for c in X.columns if c not in cats]
 prep=ColumnTransformer([('num',Pipeline([('imputer',SimpleImputer(strategy='median')),('scale',StandardScaler())]),nums),('cat',Pipeline([('imputer',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore'))]),cats)])
 return Pipeline([('prep',prep),('model',model)])
def compare(df,target):
 exclude={'CourseID','CourseName','EnrollmentCount','CourseRevenue','UniqueUsers','PaidTransactions','FreeTransactions','RevenuePerEnrollment','TeacherExpertise'}
 feats=[c for c in df.columns if c not in exclude and not c.lower().endswith('id') and df[c].notna().any()]
 d=df.dropna(subset=[target]); X=d[feats].copy(); y=pd.to_numeric(d[target],errors='coerce'); ok=y.notna(); X,y=X.loc[ok],y.loc[ok]
 if len(X)<8: raise ValueError('Too few course rows for a stable model comparison.')
 models={'Linear Regression':LinearRegression(),'Ridge':Ridge(alpha=1),'Lasso':Lasso(alpha=.01,max_iter=10000),'Random Forest':RandomForestRegressor(n_estimators=250,min_samples_leaf=2,random_state=42),'Gradient Boosting':GradientBoostingRegressor(random_state=42)}
 cv=KFold(n_splits=min(5,len(X)),shuffle=True,random_state=42); rows=[]
 for name,m in models.items():
  s=cross_validate(make_pipe(X,m),X,y,cv=cv,scoring={'mae':'neg_mean_absolute_error','mse':'neg_mean_squared_error','r2':'r2'})
  rows.append({'Target':target,'Model':name,'CV_MAE':-s['test_mae'].mean(),'CV_RMSE':np.sqrt(-s['test_mse'].mean()),'CV_R2':s['test_r2'].mean()})
 return pd.DataFrame(rows).sort_values('CV_MAE')
def fit_all(df): return pd.concat([compare(df,t) for t in ['EnrollmentCount','CourseRevenue']],ignore_index=True)

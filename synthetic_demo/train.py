"""Reproduce synthetic artifacts only. Run with the existing Anaconda Python."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge
ROOT=Path(__file__).resolve().parent

def train():
 d=pd.read_csv(ROOT/'exposures.csv'); traits=['privacy_concern_pre','relevance_preference_pre','tracking_awareness_pre','personalization_preference_pre']; x=d[traits].copy(); x['intensity']=d.personalization_level.map(dict(zip(['L0','L1','L2','L3','L4'],[0,.75,1.75,2.45,3.3]))); x['disclosure']=d.disclosure_present
 poly=PolynomialFeatures(2); X=poly.fit_transform(x); fit=d.split.eq('train');test=~fit
 assert not set(d.loc[fit,'synthetic_consumer_id'])&set(d.loc[test,'synthetic_consumer_id'])
 assert d.dataset_type.eq('SYNTHETIC_SIMULATION_NOT_REAL_RESPONDENTS').all()
 assert d.groupby('synthetic_consumer_id').personalization_level.nunique().eq(5).all()
 models={};metrics={}
 for target in ['discomfort','relevance']:
  y=d[target+'_1_7_simulated'];m=Ridge(alpha=10,fit_intercept=False).fit(X[fit],y[fit]);p=np.clip(m.predict(X[test]),1,7);yt=y[test].to_numpy();base=d.loc[fit].groupby('personalization_level')[target+'_1_7_simulated'].mean();bp=d.loc[test,'personalization_level'].map(base).to_numpy();models[target]=m.coef_.tolist()
  metrics[target]={'mae':float(abs(p-yt).mean()),'rmse':float(np.sqrt(((p-yt)**2).mean())),'baseline_mae':float(abs(bp-yt).mean()),'baseline_rmse':float(np.sqrt(((bp-yt)**2).mean())),'by_level':{l:float(abs(p[d.loc[test,'personalization_level'].to_numpy()==l]-yt[d.loc[test,'personalization_level'].to_numpy()==l]).mean()) for l in ['L0','L1','L2','L3','L4']},'high_n':int((yt>=5).sum()),'high_predicted_below_5':int(((yt>=5)&(p<5)).sum())}
 segments=[]
 for name,g in d.groupby('simulated_segment'):
  segments.append({'name':name,'consumers':g.synthetic_consumer_id.nunique(),'profile':g[traits].mean().tolist(),'levels':[{'level':l,'discomfort':float(h.discomfort_1_7_simulated.mean()),'relevance':float(h.relevance_1_7_simulated.mean())} for l,h in g.groupby('personalization_level')]})
 return {'powers':poly.powers_.tolist(),'coefficients':models,'metrics':metrics,'segments':segments,'train_consumers':240,'test_consumers':60,'source':'Synthetic data'}
if __name__=='__main__':(ROOT/'model.json').write_text(json.dumps(train(),indent=2))

"""Local research-only perceived-surveillance evaluation; no respondent exports."""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split

def run(archive):
    with zipfile.ZipFile(archive) as z:
        d=pd.read_csv(io.BytesIO(z.read("Supplementary materials/data.csv")))
    missing={k:int(v) for k,v in d.isna().sum().items() if v}
    conditions=d.cond_sensitivity+"_"+d.cond_amount
    y=d[["ps_1","ps_2","ps_3","ps_4"]].mean(axis=1)
    numeric=[c for c in d if c.startswith("smu_")]
    categories=["cond_sensitivity","cond_amount"]
    features=numeric+categories
    if d[features].isna().any().any() or not d[["ps_1","ps_2","ps_3","ps_4"]].isin(range(1,8)).all().all():
        raise ValueError("Invalid or missing model values")
    idx=np.arange(len(d))
    train,rest=train_test_split(idx,test_size=.4,stratify=conditions,random_state=612)
    cal,test=train_test_split(rest,test_size=.5,stratify=conditions.iloc[rest],random_state=613)
    pre=ColumnTransformer([("numeric",StandardScaler(),numeric),("condition",OneHotEncoder(handle_unknown="error"),categories)])
    model=make_pipeline(pre,Ridge(alpha=10))
    model.fit(d.iloc[train][features],y.iloc[train])
    pred=np.clip(model.predict(d.iloc[test][features]),1,7)
    means=y.iloc[train].groupby(conditions.iloc[train]).mean()
    base=conditions.iloc[test].map(means).to_numpy()
    residual=np.abs(y.iloc[cal].to_numpy()-np.clip(model.predict(d.iloc[cal][features]),1,7))
    q=float(np.sort(residual)[min(len(residual)-1,int(np.ceil((len(residual)+1)*.9))-1)])
    observed=y.iloc[test].to_numpy()
    def metrics(p):
        high=observed>=5
        return {"mae":float(np.abs(p-observed).mean()),"rmse":float(np.sqrt(((p-observed)**2).mean())),"high_n":int(high.sum()),"high_predicted_below_5":int((high&(p<5)).sum())}
    gains=np.abs(base-observed)-np.abs(pred-observed)
    rng=np.random.default_rng(614)
    ci=np.quantile(gains[rng.integers(0,len(gains),(2000,len(gains)))].mean(axis=1),[.025,.975]).tolist()
    groups=[]
    for condition,g in d.assign(PS=y).groupby(conditions):
        groups.append({"condition":condition,"n":len(g),"observed_PS_mean":float(g.PS.mean())})
    return {"archive_sha256":hashlib.sha256(Path(archive).read_bytes()).hexdigest(),"n":len(d),"missing_cells":missing,"missingness":"Both manipulation checks missing only in all 253 control records; no imputation", "target":"Perceived surveillance: mean ps_1..ps_4, original 1-7 scale", "predictors":features,"excluded":"Post-exposure privacy history/literacy, relevance, personalization, attitudes, manipulation checks, demographics and timings", "train_n":len(train),"calibration_n":len(cal),"test_n":len(test),"model":"Ridge alpha=10, fixed before test; training-only preprocessing", "baseline_condition_mean":metrics(base),"candidate":metrics(pred),"mae_gain_95pct_bootstrap_ci":ci,"split_conformal_90pct":{"radius":q,"test_coverage":float(((observed>=np.maximum(1,pred-q))&(observed<=np.minimum(7,pred+q))).mean()),"mean_width":float((np.minimum(7,pred+q)-np.maximum(1,pred-q)).mean())},"observed_conditions":groups,"status":"research_only; no recommendation or L0-L4 mapping", "rights":"User-authorized local analysis; source license not independently verified"}

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--archive",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    out=Path(a.output)
    if out.exists():raise ValueError("Output already exists")
    result=run(a.archive); out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8"); print(json.dumps(result,indent=2))

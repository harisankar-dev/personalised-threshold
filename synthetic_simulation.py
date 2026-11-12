"""Synthetic-only demonstration. Never supplies empirical threshold estimates."""
import json, math
from pathlib import Path
from threshold_engine import LEVELS
ROOT=Path(__file__).resolve().parent
MODEL=json.loads((ROOT/'synthetic_demo/model.json').read_text())
INTENSITY=[0,.75,1.75,2.45,3.3]
SOURCES=['None','Context / broad demographics','Browsing / search behavior','Purchase / relationship history','Context + behavior + history']
def number(value,name,lo=0,hi=1e12):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not lo<=value<=hi:raise ValueError(f'{name} must be between {lo} and {hi}')
    return float(value)
def predict(profile,level):
    x=profile+[INTENSITY[level],1.0] # disclosure present in all demo comparisons
    terms=[math.prod(v**p for v,p in zip(x,powers)) for powers in MODEL['powers']]
    return {k:round(max(1,min(7,sum(a*b for a,b in zip(coef,terms)))),3) for k,coef in MODEL['coefficients'].items()}
def evaluate(payload):
    if not isinstance(payload,dict):raise ValueError('Send an object')
    profile=payload.get('profile')
    if not isinstance(profile,list) or len(profile)!=4:raise ValueError('Four profile ratings are required')
    profile=[number(v,'Profile rating',1,7) for v in profile]
    threshold=number(payload.get('threshold',4),'Discomfort ceiling',1,7);minimum=number(payload.get('minimum_relevance',3),'Minimum relevance',1,7)
    perms=payload.get('permissions',{});costs=payload.get('costs',[None]*5)
    if not isinstance(perms,dict) or any(v not in ['yes','no','unknown'] for v in perms.values()):raise ValueError('Invalid permission')
    if not isinstance(costs,list) or len(costs)!=5:raise ValueError('Five cost estimates required')
    headroom=payload.get('headroom');headroom=None if headroom is None else number(headroom,'Headroom')
    segment=payload.get('segment');groups={s['name']:s for s in MODEL['segments']}
    if segment is not None and segment not in groups:raise ValueError('Unknown segment')
    rows=[]
    for level in range(5):
        response=predict(profile,level) if segment is None else {k:next(v for v in groups[segment]['levels'] if v['level']==f'L{level}')[k] for k in ['discomfort','relevance']}
        required=[[],['context'],['behavior'],['history'],['context','behavior','history']][level]
        reasons=[]
        for source in required:
            if perms.get(source,'unknown')!='yes':reasons.append(f'{source}: data possession and permitted use '+('not confirmed' if perms.get(source,'unknown')=='unknown' else 'not available'))
        cost=costs[level]
        if cost is None:reasons.append('Cost estimate missing')
        else:
            cost=number(cost,'Incremental cost')
            if headroom is None:reasons.append('Budget headroom missing')
            elif cost>headroom:reasons.append('Cost exceeds headroom')
        rows.append({'level':f'L{level}','name':LEVELS[level],'source':SOURCES[level],**response,'eligible':not reasons,'reasons':reasons,'cost':cost})
    feasible=[r for r in rows if r['eligible'] and r['discomfort']<=threshold and r['relevance']>=minimum]
    chosen=feasible[0]['level'] if feasible else None
    return {'source':'Synthetic data','detail':'Simulated using generated consumer data; not validated on real consumer responses.','levels':rows,'recommended_level':chosen,'reason':('Lowest-complexity eligible level meeting your stated simulated response criteria.' if chosen else 'No level meets the permission, budget and simulated response criteria.'),'real_threshold_status':'insufficient_evidence','segment':segment}

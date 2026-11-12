"""Streamlit deployment entry point for the existing 49-C application."""
from pathlib import Path
import hashlib,json,subprocess,tempfile,shutil
import pandas as pd
import streamlit as st
from intrusive_ad_model import predict
from marketer_app import image_matches_type
from synthetic_simulation import evaluate as simulate,MODEL
from stp_advisory import evaluate as strategy,survey_personas
from research_dashboard import dashboard_data

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title="49-C · Personalization Threshold",page_icon="◉",layout="wide")
st.title("49-C · The Personalization Threshold")
st.caption("Creative review, consumer simulation and permission-aware campaign planning")

@st.cache_resource
def prepare_ocr():
    if not shutil.which('node'):raise RuntimeError('Node.js is missing. Install the system packages listed in packages.txt.')
    if not (ROOT/'node_modules/tesseract.js/package.json').exists():
        proc=subprocess.run(['npm','install','--omit=dev','--ignore-scripts'],cwd=ROOT,capture_output=True,text=True,timeout=180,shell=False)
        if proc.returncode:raise RuntimeError('OCR dependency setup failed. Run npm install in the project directory.')
    return True

def optional(label,key):
    value=st.text_input(label,key=key,placeholder="Unknown")
    return value.strip() or None

creative,consumer,research=st.tabs(["Advertisement & STP","Consumer & levels","Research evidence"])
with creative:
    left,right=st.columns(2)
    with left:
        st.subheader("Advertisement")
        copy=st.text_area("Ad copy",key="ad_copy",max_chars=20000,help="Analyze one advertisement at a time.")
        uploaded=st.file_uploader("English advertisement image",type=['png','jpg','jpeg','webp','bmp','tif','tiff'])
        if uploaded:
            raw=uploaded.getvalue();digest=hashlib.sha256(raw).hexdigest()
            if len(raw)>10*1024*1024:st.error('Choose an image under 10 MB.')
            else:
                st.image(raw,width=320)
                if st.button('Extract English text'):
                    try:
                        mime=uploaded.type
                        if mime not in ('image/png','image/jpeg','image/webp','image/bmp','image/tiff') or not image_matches_type(raw,mime):raise ValueError('Image content does not match its supported type.')
                        with st.spinner('Reading English text locally…'):
                            prepare_ocr()
                            with tempfile.TemporaryDirectory() as tmp:
                                path=Path(tmp)/('ad'+Path(uploaded.name).suffix.lower());path.write_bytes(raw);result=predict(image=path)
                        st.session_state['ocr_original']=result['ocr_text'];st.session_state['ocr_edited']=result['ocr_text'];st.session_state['ocr_warning']=result.get('ocr_warning');st.session_state['ocr_digest']=digest
                    except (ValueError,RuntimeError,OSError,subprocess.SubprocessError) as exc:st.error(str(exc))
                if st.session_state.get('ocr_digest')==digest:
                    with st.expander('Original OCR transcript'):st.text(st.session_state.get('ocr_original',''))
                    st.text_area('Review and correct extracted text',key='ocr_edited',max_chars=20000)
                    if st.session_state.get('ocr_warning'):st.warning(st.session_state['ocr_warning'])
        targeting=st.text_input('Known targeting details',max_chars=5000)
        visual=st.text_area('Other visual details (optional)',max_chars=5000)
        st.subheader('Campaign context')
        campaign={}
        for key,options in [('objective',['unknown','awareness','traffic','conversions']),('targeting_method',['unknown','generic','contextual','demographic','behavioral','historical','combined','sensitive']),('data_source',['unknown','none','page_context','broad_demographic','first_party_behavior','first_party_purchase','third_party','combined','other']),('consent_status',['unknown','yes','no']),('audience_eligibility',['unknown','yes','no'])]:
            campaign[key]=st.selectbox(key.replace('_',' ').title(),options,key='campaign_'+key)
        campaign['currency']=st.text_input('Currency code',value='INR',max_chars=3)
        for key in ['total_budget','committed_spend','revision_cost','targeting_cost','variant_cost','management_cost','segmentation_cost','variant_count','contribution_margin','audience_reach','cpc','cpm','conversion_rate_pct']:
            campaign[key]=optional(key.replace('_',' ').title(),'campaign_'+key)
        with st.expander('Hypothetical economic scenarios'):
            campaign['scenario_option']=st.selectbox('Scenario option',['one_variant','revise_one_creative','adjust_targeting','multiple_variants'])
            for key in ['worst_incremental_conversions','central_incremental_conversions','best_incremental_conversions']:campaign[key]=optional(key.replace('_',' ').title(),'campaign_'+key)
        if st.button('Analyze creative and campaign',type='primary'):
            try:
                corrected=st.session_state.get('ocr_edited','') if uploaded and st.session_state.get('ocr_digest')==digest else ''
                text=' '.join(x for x in [copy,corrected] if x.strip())
                if not text.strip() and not visual.strip():raise ValueError('Add copy or extract and review image text first.')
                result=predict(text=text,targeting=targeting,visual_description=visual)
                st.session_state['creative_result']=result;st.session_state['strategy_result']=strategy(campaign,result)
            except ValueError as exc:st.error(str(exc))
    with right:
        result=st.session_state.get('creative_result');plan=st.session_state.get('strategy_result')
        if result:
            st.subheader('Creative analysis');st.metric('Editorial screening score / 10',result['score_out_of_10']);st.write(result['tier']);st.caption(result['reason'])
            st.dataframe(pd.DataFrame(result['evidence']+result.get('pressure_evidence',[])),hide_index=True)
            for item in result.get('recommendations',[]):st.write(item)
            st.subheader('STP recommendation');st.write(plan['action']);st.write(plan['reason']);st.metric('Available budget headroom',plan['available_budget_headroom'] or 'Unknown')
            st.dataframe(pd.DataFrame(plan['options']),hide_index=True)
            if plan['warnings']:
                with st.expander('Permission and budget findings'):
                    for warning in plan['warnings']:st.write(warning)
            with st.expander('Hypothetical scenario calculation'):st.json(plan['scenario'])
            st.caption('Empirical personalization threshold: '+result['threshold_decision']['status'])
with consumer:
    st.subheader('Individual and segment analysis');st.caption('Synthetic data · Simulated using generated consumer data; not validated on real consumer responses.')
    names=['Individual','Privacy-sensitive example','Relevance-seeking example']+[s['name'] for s in MODEL['segments']]
    selected=st.selectbox('Profile or synthetic segment',names)
    preset=[7,4,6,2] if selected==names[1] else [2,7,3,6] if selected==names[2] else [4,4,4,4]
    profile=[st.slider(label,1,7,value,key='sim_'+str(i)+'_'+str(preset)) for i,(label,value) in enumerate(zip(['Privacy concern','Relevance preference','Tracking awareness','Personalization preference'],preset))]
    ceiling=st.slider('Maximum simulated discomfort',1.,7.,4.,.1);minimum=st.slider('Minimum simulated relevance',1.,7.,3.,.1)
    perms={key:st.selectbox(key.title()+' data possessed and permitted',['unknown','yes','no'],key='sim_perm_'+key) for key in ['context','behavior','history']}
    default_headroom=st.session_state.get('strategy_result',{}).get('available_budget_headroom')
    headroom=st.text_input('Incremental budget headroom',value=str(default_headroom) if default_headroom is not None else '')
    costs=[st.text_input('L'+str(i)+' incremental cost',value='0' if i==0 else '',key='sim_cost_'+str(i)) for i in range(5)]
    if st.button('Compare L0–L4',type='primary'):
        try:
            result=simulate(dict(profile=profile,segment=selected if selected in names[3:] else None,threshold=ceiling,minimum_relevance=minimum,permissions=perms,headroom=float(headroom) if headroom.strip() else None,costs=[float(v) if v.strip() else None for v in costs]));st.session_state['simulation_result']=result
        except ValueError as exc:st.error(str(exc))
    if 'simulation_result' in st.session_state:
        result=st.session_state['simulation_result'];st.write('Demonstration choice: '+(result['recommended_level'] or 'No eligible choice'));st.caption(result['reason']);frame=pd.DataFrame(result['levels']);st.dataframe(frame,hide_index=True);st.bar_chart(frame.set_index('level')[['discomfort','relevance']]);st.caption('Synthetic data · Disclosures remain present. Real-evidence threshold: insufficient_evidence')
    st.subheader('Real research profiles')
    profiles=json.loads((ROOT/'results/phase7_segmentation_v1.json').read_text(encoding='utf-8'))
    for key,title in [('genz','Gen Z: relevance × privacy concern'),('romano_han','Romano–Han: ad benefits × privacy concern')]:
        st.write(title);st.caption(str(profiles[key]['respondents'])+' actual survey respondents; unrelated to synthetic consumers');st.dataframe(pd.DataFrame([{'profile':name,'respondents':n,'share_95pct_interval':profiles[key]['respondent_bootstrap_95pct_share_intervals'][name]} for name,n in profiles[key]['counts'].items()]),hide_index=True)
with research:
    st.subheader('Research evidence');st.caption('Saved aggregate results from separate secondary datasets. Original measurement scales and limitations apply.')
    for name,value in dashboard_data().items():
        with st.expander(name.replace('_',' ').title()):st.json(value)

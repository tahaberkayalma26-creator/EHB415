"""Tamamlanan tekrar günlüklerinde genişlik, RE, TBS ve HARQ izini denetler."""
from pathlib import Path
from collections import Counter
import gzip,json,re,sys
ROOT=Path(__file__).resolve().parents[1]

def inspect(tag):
    p=ROOT/'Ham_Kayitlar'/tag/'gnb.log.gz'
    ranges=Counter();tbs48=Counter();retx=Counter();prs=Counter();mapping=Counter();examples=[]
    with gzip.open(p,'rt',encoding='utf-8',errors='replace') as f:
        for i,line in enumerate(f,1):
            if 'PDSCH' in line and re.search(r'rnti=(?:0x)?44\b',line):
                m=re.search(r'nrtx=(\d+)',line)
                if m:
                    retx[m[1]]+=1
                    if m[1]!='0' and len(examples)<3:examples.append({'line':i,'text':line.rstrip()})
            if '- PDSCH rnti=0x44 ' in line:
                mp=re.search(r'vrb_to_prb_mapping=(\d+)',line)
                if mp:mapping[mp[1]]+=1
                m=re.search(r'vrbs=\[(\d+)\.\.(\d+)\)',line)
                if m:
                    key=f'[{m[1]}..{m[2]})';ranges[key]+=1
                    if int(m[2])-int(m[1])==48:
                        t=re.search(r'\btbs=(\d+)',line)
                        if t:tbs48[t[1]]+=1
            if 'Experimental PRS RE model:' in line and 'nof_prbs=48 ' in line:
                m=re.search(r'excluded_data_re=(\d+)',line)
                if m:prs[m[1]]+=1
    return {'tag':tag,'pdsch_phy_pdu_ranges':dict(ranges),'full48_tbs_bytes':dict(tbs48),
            'vrb_to_prb_mapping_counts':dict(mapping),'non_interleaved_only':bool(mapping) and set(mapping)=={'0'},
            'nrtx_counts':dict(retx),'no_retx_verified':bool(retx) and all(k=='0' for k in retx),
            'full48_prs_excluded_re_counts':dict(prs),'nonzero_retx_examples':examples}

def main():
    width=inspect('v2_veri_genisligi100')
    assert width['pdsch_phy_pdu_ranges'],'No PHY PDSCH width evidence'
    dominant=max(width['pdsch_phy_pdu_ranges'],key=width['pdsch_phy_pdu_ranges'].get)
    result={'method':'Read-only full archived debug logs, after gNB measurements finished; count actual PHY PDU ranges and scheduler trace fields.',
            'pdsch_width':{'dominant_range':dominant,'counts':width['pdsch_phy_pdu_ranges'],'baseline_tbs_3969_observed':width['full48_tbs_bytes'].get('3969',0)>0,'non_interleaved_only':width['non_interleaved_only']},'models':{}}
    for case,re_count,tbs in zip(['K1','K6','K7','K8','K11'],[432,1296,864,432,384],[3713,3072,3393,3713,3713]):
        for stage in ['oncesi','sonrasi']:
            tag='v2_'+stage+'_'+case
            d=inspect(tag)
            if stage=='sonrasi':
                d['expected_data_re']=re_count;d['expected_prs_slot_tbs_bytes']=tbs
                d['re_trace_matches']=d['full48_prs_excluded_re_counts'].get(str(re_count),0)>0 and set(d['full48_prs_excluded_re_counts'])=={str(re_count)}
                d['expected_tbs_observed']=d['full48_tbs_bytes'].get(str(tbs),0)>0
            result['models'][tag]=d
    result['all_expected_re_tbs_observed']=all(d['re_trace_matches'] and d['expected_tbs_observed'] for k,d in result['models'].items() if '_sonrasi_' in k)
    result['all_selected_repeats_no_retx']=all(d['no_retx_verified'] for d in result['models'].values())
    out=ROOT/'Dogrulama/pdsch_genislik_ve_model_kontrolu.json'
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(out),'dominant_width':dominant,'re_tbs_match':result['all_expected_re_tbs_observed'],'all_no_retx':result['all_selected_repeats_no_retx']},ensure_ascii=False))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()

#!/usr/bin/env bash
# OCUDU testmode: cok kullanicili ve/veya dilimli (slicing) deney.
# Kullanim (Ubuntu/WSL):  bash ocudu_cok_ue.sh <etiket> <nof_ues> <prs_periyot|0> <dilim_max_prb_%|0>
#   ornek: bash ocudu_cok_ue.sh u4 4 0 0        (4 UE, PRS yok, dilim siniri yok)
#          bash ocudu_cok_ue.sh u4p4 4 4 0      (4 UE, PRS her 4 slotta bir)
#          bash ocudu_cok_ue.sh s60 1 0 60      (1 UE, varsayilan dilime max %60 PRB siniri)
# Cikti: /tmp/cok_<etiket>.csv  (tek satir: etiket,nof_ues,prs,dilim,toplam_Mbps,UE basina Mbps...)
set -u
tag=$1; nue=$2; per=$3; sl=$4
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cfg=/tmp/cok_$tag.yml
cp "$here/../../kurulum/ocudu_testmode.yml" "$cfg"
python3 - "$cfg" "$nue" "$per" "$sl" <<'EOF'
import sys
cfg,nue,per,sl=sys.argv[1:5]
t=open(cfg).read()
t=t.replace("    nof_ues: 1","    nof_ues: "+nue)
extra=""
if per!="0":
    extra+=f"""  prs:
    resource_sets:
      - comb_size: 2
        periodicity_slots: {per}
        slot_offset: 1
        nof_symbols: 12
        bandwidth_prbs: 104
        resources:
          - sequence_id: 1
            re_offset: 0
            slot_offset: 0
            symbol_offset: 2
"""
if sl!="0":
    extra+=f"""  slicing:
    - sst: 1
      sched_cfg:
        max_prb_policy_ratio: {sl}
"""
t=t.replace("  pdsch:\n    mcs_table: qam64", extra+"  pdsch:\n    mcs_table: qam64",1)
open(cfg,"w").write(t)
EOF
cd ~/ehb415/ocudu/build/apps/gnb
rm -f /tmp/cok_$tag.txt
( sleep 9; printf 't\n'; sleep 20; printf 'q\n' ) | timeout 55 script -qc "./gnb -c $cfg" /tmp/cok_$tag.txt > /dev/null 2>&1
python3 - "$tag" "$nue" "$per" "$sl" <<'EOF' | tee /tmp/cok_$1.csv
import re,sys,statistics as st
tag,nue,per,sl=sys.argv[1:5]
t=open(f"/tmp/cok_{tag}.txt",errors="ignore").read()
t=re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]","",t).replace("\r","")
if "ERROR" in t or "rror" in t.split("gNB started")[0] if "gNB started" in t else True:
    err=[l for l in t.split("\n") if "ERROR" in l or ">" in l[:3] or "Invalid" in l][:2]
    if "gNB started" not in t: print(f"{tag},{nue},{per},{sl},HATA,{' '.join(err)[:160]}"); sys.exit()
def num(s):
    m=re.match(r"([\d.]+)([kMG]?)",s.strip()); return float(m.group(1))*{"":1e-6,"k":1e-3,"M":1,"G":1e3}[m.group(2)]
satir={}
for l in t.split("\n"):
    m=re.match(r"^\s+1\s+([0-9a-f]+)\s*\|(.*?)\|",l)
    if m:
        d=m.group(2).split()
        try: satir.setdefault(m.group(1),[]).append(num(d[3]))
        except Exception: pass
ort={k:st.mean(v[-15:]) for k,v in satir.items() if len(v)>=3}
tot=sum(ort.values())
print(f"{tag},{nue},{per},{sl},{tot:.1f},"+";".join(f"{k}={v:.1f}" for k,v in sorted(ort.items())))
EOF

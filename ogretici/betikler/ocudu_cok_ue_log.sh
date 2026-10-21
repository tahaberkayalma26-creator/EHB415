#!/usr/bin/env bash
# 4 test UE + PRS (her 4 slotta bir) ile scheduler log'unu alip slot basina UE tahsislerini CSV'ye cevirir.
# Kullanim (Ubuntu/WSL): bash ocudu_cok_ue_log.sh     Cikti: ogretici/veri/ocudu_cok_ue_slot.csv
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cfg=/tmp/ehb_cokue_log.yml
cp "$here/../../kurulum/ocudu_testmode.yml" "$cfg"
python3 - "$cfg" <<'EOF'
import sys
cfg=sys.argv[1]; t=open(cfg).read()
t=t.replace("    nof_ues: 1","    nof_ues: 4")
t=t.replace("/tmp/gnb_testmode.log","/tmp/gnb_cokue.log").replace("all_level: warning","all_level: debug")
prs="""  prs:
    resource_sets:
      - comb_size: 2
        periodicity_slots: 4
        slot_offset: 1
        nof_symbols: 12
        bandwidth_prbs: 104
        resources:
          - sequence_id: 1
            re_offset: 0
            slot_offset: 0
            symbol_offset: 2
"""
t=t.replace("  pdsch:\n    mcs_table: qam64", prs+"  pdsch:\n    mcs_table: qam64",1)
open(cfg,"w").write(t)
EOF
rm -f /tmp/gnb_cokue.log
cd ~/ehb415/ocudu/build/apps/gnb && timeout 14 ./gnb -c "$cfg" > /dev/null 2>&1
python3 - "$here/../veri/ocudu_cok_ue_slot.csv" <<'EOF'
import re,sys
log=open('/tmp/gnb_cokue.log',errors='ignore').read().split('\n')
rows=[]
for l in log:
    m=re.search(r'\[\s*(\d+)\.(\d)\]\s+PDSCH: rnti=0x([0-9a-f]+).*prb=\[(\d+), (\d+)\) symb=\[(\d+), (\d+)\).*tbs=(\d+)',l)
    if m: rows.append(m.groups())
rows=rows[len(rows)//3:]            # baslangic dalgalanmasini at
with open(sys.argv[1],'w') as f:
    f.write("sfn,slot,rnti,prb_lo,prb_hi,sym_lo,sym_hi,tbs_bayt\n")
    for r in rows: f.write(",".join(r)+"\n")
print("PDSCH satiri:",len(rows),"| UE'ler:",sorted(set(r[2] for r in rows)))
EOF

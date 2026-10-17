#!/usr/bin/env bash
# PRS periyodu ve genisligi degisirken DL/UL throughput taramasi (yaklasik 6 dk).
# Kullanim (Ubuntu/WSL icinde):  bash ocudu_prs_sweep.sh      Cikti: /tmp/prs_sweep.csv
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
out=/tmp/prs_sweep.csv
echo "tag,periyot_slot,sembol,bw_prb,dl_brate_mbps,dl_ok_per_s,ul_brate_mbps,ul_ok_per_s" > $out
run() {
  tag=$1; per=$2; sym=$3; bw=$4
  bash "$here/ocudu_prs_kos.sh" $tag $per $sym $bw > /tmp/run_$tag.log 2>&1
  python3 - "$tag" "$per" "$sym" "$bw" >> $out <<'EOF'
import re,sys,statistics as st
tag,per,sym,bw=sys.argv[1:5]
t=open(f"/tmp/out_{tag}.txt",errors="ignore").read()
t=re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]","",t).replace("\r","")
rows=[l for l in t.split("\n") if re.match(r"^\s+1\s+44\s*\|",l)]
def num(s):
    m=re.match(r"([\d.]+)([kMG]?)",s.strip()); v=float(m.group(1)); return v*{"":1e-6,"k":1e-3,"M":1,"G":1e3}[m.group(2)]
dl=[];dok=[];ul=[];uok=[]
for l in rows[-15:]:
    parts=l.split("|"); d=parts[1].split(); u=parts[2].split()
    # DL: cqi ri mcs brate ok nok (%) dl_bs ; UL: pusch rsrp ri mcs brate ok nok (%) bsr ta phr
    dl.append(num(d[3])); dok.append(float(d[4])); ul.append(num(u[4])); uok.append(float(u[5]))
print(f"{tag},{per},{sym},{bw},{st.mean(dl):.1f},{st.mean(dok):.0f},{st.mean(ul):.1f},{st.mean(uok):.0f}")
EOF
}
run base 0 0 0
run p80 80 12 104
run p40 40 12 104
run p20 20 12 104
run p10 10 12 104
run p8 8 12 104
run p4 4 12 104
run p4w52 4 12 52
run p4s4 4 4 104
cat $out

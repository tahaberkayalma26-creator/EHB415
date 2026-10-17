#!/usr/bin/env bash
# ns-3 cttc-nr-demo: UE sayisina gore throughput ve gecikme (yaklasik 2 dk).
# Kullanim (Ubuntu/WSL icinde):  bash ns3_ue_sweep.sh      Cikti: /tmp/ns3_sweep.csv
cd ~/ehb415/ns-3-dev
out=/tmp/ns3_sweep.csv
echo "ue_per_gnb,flows,mean_flow_throughput_mbps,mean_flow_delay_ms,total_throughput_mbps" > $out
for n in 1 2 5 10 20; do
  ./ns3 run "cttc-nr-demo --ueNumPergNb=$n --simTime=1" > /tmp/ns3_run_$n.txt 2>&1
  python3 - "$n" >> $out <<'EOF'
import re,sys
n=sys.argv[1]
t=open(f"/tmp/ns3_run_{n}.txt",errors="ignore").read()
thr=[float(x) for x in re.findall(r"Throughput:\s+([\d.]+)\s+Mbps",t)]
mt=re.search(r"Mean flow throughput:\s+([\d.]+)",t); md=re.search(r"Mean flow delay:\s+([\d.]+)",t)
print(f"{n},{len(thr)},{float(mt.group(1)):.2f},{float(md.group(1)):.3f},{sum(thr):.1f}")
EOF
done
cat $out

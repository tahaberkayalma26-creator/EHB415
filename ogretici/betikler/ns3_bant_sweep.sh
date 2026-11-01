#!/usr/bin/env bash
# ns-3 cttc-nr-demo: bandi daraltarak sensing'e kaynak ayirmayi taklit eder (alfa = 1 - B/B0). BE akisi doygun tutulur (lambdaBe=40000),
# boylece olculen throughput bandin kapasitesidir. Dickerson modeli: kapasite (1-alfa)*C0 olmali; ns-3 ne veriyor?
# Kullanim (Ubuntu/WSL icinde):  bash ns3_bant_sweep.sh      Cikti: /tmp/ns3_bant.csv
cd ~/ehb415/ns-3-dev
out=/tmp/ns3_bant.csv
echo "bant_mhz,alfa,be_alinan_mbps,be_gecikme_ms,ulL_alinan_mbps,ull_gecikme_ms" > $out
for bw in 50000000 40000000 30000000 25000000 10000000; do
  ./ns3 run "cttc-nr-demo --ueNumPergNb=2 --simTime=1 --doubleOperationalBand=false --lambdaBe=40000 --bandwidthBand1=$bw" > /tmp/ns3_bant_$bw.txt 2>&1
  python3 - "$bw" >> $out <<'EOF'
import re, sys
bw = int(sys.argv[1]); t = open(f"/tmp/ns3_bant_{bw}.txt", errors="ignore").read()
f = {}
for blk in re.split(r"(?=Flow \d+ \()", t)[1:]:
    k = int(re.match(r"Flow (\d+)", blk).group(1))
    f[k] = (float(re.search(r"Throughput:\s+([\d.]+)", blk).group(1)), float(re.search(r"Mean delay:\s+([\d.]+)", blk).group(1)))
print(f"{bw/1e6:.0f},{1-bw/50e6:.2f},{f[2][0]:.2f},{f[2][1]:.3f},{f[1][0]:.2f},{f[1][1]:.3f}")
EOF
done
cat $out

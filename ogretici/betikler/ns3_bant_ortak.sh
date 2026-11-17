#!/usr/bin/env bash
# ns-3 cttc-nr-demo, ORTAK IZGARA: 3,5 GHz. Sensing payini bant daraltarak taklit eder (7 nokta, her seferinde 1 birim daha dar).
# alfa_gercek = 1 - PRB / PRB0 ; PRB = ns-3'un kendi hesabi (nr-phy.cc DoUpdateRbNum: bant*(1-0,04)/(12*SCS), asagi yuvarla).
# Kullanim (Ubuntu/WSL):  bash ns3_bant_ortak.sh <numeroloji> <bant0_MHz> <adim_MHz>
#   ana ayar (30 kHz, 106 PRB):  bash ns3_bant_ortak.sh 1 40 2      Karsilastirma (15 kHz, 106 PRB):  bash ns3_bant_ortak.sh 0 20 1
# Cikti: /tmp/ns3_bant_ortak_n<numeroloji>.csv
num=${1:?numeroloji}; bw0=${2:?bant0 MHz}; adim=${3:?adim MHz}
scs=$((15000 * (1 << num)))
cd ~/ehb415/ns-3-dev
out=/tmp/ns3_bant_ortak_n$num.csv
echo "bant_mhz,prb,alfa_gercek,be_alinan_mbps,be_gecikme_ms,ull_alinan_mbps,ull_gecikme_ms" > $out
for i in 0 1 2 3 4 5 6; do
  bw=$(( (bw0 - i * adim) * 1000000 ))
  ./ns3 run "cttc-nr-demo --ueNumPergNb=2 --simTime=1 --doubleOperationalBand=false --lambdaBe=40000 --numerologyBwp1=$num --centralFrequencyBand1=3.5e9 --bandwidthBand1=$bw" > /tmp/ns3_bant_ortak_${num}_$bw.txt 2>&1
  python3 - "$bw" "$scs" "$bw0" >> $out <<'PY'
import re, sys, math
bw, scs, bw0 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
num = {15000: 0, 30000: 1}[scs]
t = open(f"/tmp/ns3_bant_ortak_{num}_{bw}.txt", errors="ignore").read()
prb = lambda b: math.floor(b * (1 - 0.04) / (12 * scs))
f = {}
for blk in re.split(r"(?=Flow \d+ \()", t)[1:]:
    k = int(re.match(r"Flow (\d+)", blk).group(1))
    f[k] = (float(re.search(r"Throughput:\s+([\d.]+)", blk).group(1)), float(re.search(r"Mean delay:\s+([\d.]+)", blk).group(1)))
print(f"{bw/1e6:g},{prb(bw)},{1-prb(bw)/prb(bw0*1000000):.3f},{f[2][0]:.2f},{f[2][1]:.3f},{f[1][0]:.2f},{f[1][1]:.3f}")
PY
done
cat $out

#!/usr/bin/env bash
# ns-3 cttc-nr-demo: en-iyi-caba (BE) akisinin paket hizini (lambdaBe) degistirir; her akisin throughput, gecikme ve kaybini yazar.
# Fikir: BE akisini "ek yuk" (sensing'i ayri trafik akisi olarak ekleme yolu) gibi okuyup oteki akisa etkisine bakmak.
# --doubleOperationalBand=false: iki akis AYNI bandi paylasir (varsayilanda iki ayri band kullanir ve akislar birbirini etkilemez).
# Kullanim (Ubuntu/WSL icinde):  bash ns3_yuk_sweep.sh      Cikti: /tmp/ns3_yuk.csv
cd ~/ehb415/ns-3-dev
out=/tmp/ns3_yuk.csv
echo "lambdaBe,akis,gonderilen_mbps,alinan_mbps,gecikme_ms,kayip_yuzde" > $out
for lam in 1000 5000 10000 20000 40000; do
  ./ns3 run "cttc-nr-demo --ueNumPergNb=2 --simTime=1 --doubleOperationalBand=false --lambdaBe=$lam" > /tmp/ns3_yuk_$lam.txt 2>&1
  python3 - "$lam" >> $out <<'EOF'
import re, sys
lam = sys.argv[1]
t = open(f"/tmp/ns3_yuk_{lam}.txt", errors="ignore").read()
for blk in re.split(r"(?=Flow \d+ \()", t)[1:]:
    k   = re.match(r"Flow (\d+)", blk).group(1)
    tx  = float(re.search(r"TxOffered:\s+([\d.]+)", blk).group(1))
    rx  = float(re.search(r"Throughput:\s+([\d.]+)", blk).group(1))
    dl  = float(re.search(r"Mean delay:\s+([\d.]+)", blk).group(1))
    txp = int(re.search(r"Tx Packets:\s+(\d+)", blk).group(1)); rxp = int(re.search(r"Rx Packets:\s+(\d+)", blk).group(1))
    print(f"{lam},{k},{tx:.2f},{rx:.2f},{dl:.3f},{100*(txp-rxp)/txp:.2f}")
EOF
done
cat $out

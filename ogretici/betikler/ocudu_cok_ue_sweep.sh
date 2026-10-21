#!/usr/bin/env bash
# UE sayisi x PRS taramasi (yaklasik 5 dk). Cikti: /tmp/ocudu_cok_ue.csv
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
out=/tmp/ocudu_cok_ue.csv
echo "etiket,nof_ues,prs_periyot,dilim_max,toplam_Mbps,ue_basina" > $out
for n in 1 2 4 8; do
  bash "$here/ocudu_cok_ue.sh" u${n} $n 0 0 >> $out
  bash "$here/ocudu_cok_ue.sh" u${n}p4 $n 4 0 >> $out
done
# dilim sinirinin testmode'da etkisiz oldugunu belgelemek icin
bash "$here/ocudu_cok_ue.sh" s60 1 0 60 >> $out
bash "$here/ocudu_cok_ue.sh" s30 1 0 30 >> $out
cat $out

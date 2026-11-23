#!/usr/bin/env bash
# PRS'siz kosuda PDSCH'nin kullandigi PRB araliklarini sayar (veri alani genisligi).
# Kullanim (Ubuntu/WSL, repo kokunde):  bash ogretici/betikler/ocudu_veri_genislik.sh [yml]     varsayilan yml: kurulum/ocudu_testmode_n78.yml
cfg=${1:-kurulum/ocudu_testmode_n78.yml}
cp "$cfg" /tmp/ehb_genislik.yml
sed -i 's#/tmp/gnb_testmode.log#/tmp/gnb_genislik.log#; s#all_level: warning#all_level: debug#' /tmp/ehb_genislik.yml
rm -f /tmp/gnb_genislik.log
( cd ~/ehb415/ocudu/build/apps/gnb && timeout 12 "${GNB_BIN:-./gnb}" -c /tmp/ehb_genislik.yml > /dev/null 2>&1 )
echo "PDSCH rb araligi (sayi, aralik) - en sik 5:"
grep -a "UE PDSCH" /tmp/gnb_genislik.log | grep -a -o "rb=\[[0-9]*\.\.[0-9]*)" | sort | uniq -c | sort -rn | head -5

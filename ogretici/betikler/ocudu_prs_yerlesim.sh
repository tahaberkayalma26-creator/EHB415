#!/usr/bin/env bash
# PRS'i farkli yerlere koymayi dener; OCUDU hangi yerlesimi kabul ediyor, hangisini reddediyor?
# Kullanim (Ubuntu/WSL): bash ocudu_prs_yerlesim.sh
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
base="$here/../../kurulum/ocudu_testmode.yml"
try() {  # etiket periyot slot_ofs sembol sembol_ofs bw start_prb
  tag=$1; per=$2; so=$3; sym=$4; sof=$5; bw=$6; st=$7
  cfg=/tmp/yer_$tag.yml; cp "$base" "$cfg"
  python3 - "$cfg" "$per" "$so" "$sym" "$sof" "$bw" "$st" <<'EOF'
import sys
cfg,per,so,sym,sof,bw,st=sys.argv[1:8]
t=open(cfg).read()
add=f"""  prs:
    resource_sets:
      - comb_size: 2
        periodicity_slots: {per}
        slot_offset: {so}
        nof_symbols: {sym}
        bandwidth_prbs: {bw}
        start_prb: {st}
        resources:
          - sequence_id: 1
            re_offset: 0
            slot_offset: 0
            symbol_offset: {sof}
"""
open(cfg,"w").write(t.replace("  pdsch:\n    mcs_table: qam64", add+"  pdsch:\n    mcs_table: qam64",1))
EOF
  cd ~/ehb415/ocudu/build/apps/gnb
  out=$(timeout 8 ./gnb -c "$cfg" 2>&1 | sed 's/\x1b\[[0-9;?]*[a-zA-Z]//g' | tr -d '\r' | grep -vi "Scheduling priority")
  if echo "$out" | grep -q "gNB started"; then r="KABUL (gNB basladi)"
  else r="RED: $(echo "$out" | grep -iE "ERROR|>|Invalid|error" | head -2 | tr '\n' ' ' | cut -c1-210)"; fi
  printf "%-22s per=%-3s so=%-2s sym=%-2s sof=%-2s bw=%-3s st=%-3s -> %s\n" "$tag" "$per" "$so" "$sym" "$sof" "$bw" "$st" "$r"
}
echo "Hucre: 20 MHz, 15 kHz SCS, 106 PRB"
try referans          4 1 12 2 104 0
try yarim_alt_bant    4 1 12 2  52 0
try yarim_ust_bant    4 1 12 2  52 54
try bant_disina_tasar 4 1 12 2  52 60
try bw_4un_kati_degil 4 1 12 2  50 0
try baska_slot        4 3 12 2 104 0
try slot0_cakisma     10 0 12 2 104 0
try sembol0_PDCCH     4 1 12 0 104 0
try sembol_tasar      4 1  4 12 104 0
try seyrek_az_sembol  8 2  4 6  52 0

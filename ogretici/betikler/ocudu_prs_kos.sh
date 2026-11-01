#!/usr/bin/env bash
# Tek bir OCUDU testmode kosusu: PRS yapilandirmasi ile DL throughput olcer.
# Kullanim (Ubuntu/WSL icinde):  bash ocudu_prs_kos.sh <etiket> <periyot_slot|0> <sembol> <bw_prb>
#   ornek: bash ocudu_prs_kos.sh p4 4 12 104     (PRS her 4 slotta bir, 12 sembol, 104 PRB)
#          bash ocudu_prs_kos.sh o5 4 4 52 5     (5. arguman: PRS ilk sembol ofseti, varsayilan 2)
#          bash ocudu_prs_kos.sh r16 40 4 32 2 16 1 4   (6.-8. arguman: tekrar sayisi, tekrar arasi bosluk (slot), tarak boyutu; varsayilan 1 1 2)
#          bash ocudu_prs_kos.sh base 0 0 0      (PRS yok)
# Not: PRS penceresi periyoda sigmali: slot_offset(1) + (tekrar-1)*bosluk + 1 <= periyot  (OCUDU prs_scheduler.cpp satir 80). nof_symbols >= tarak ve tarak'in kati olmali.
# Cikti:  /tmp/out_<etiket>.txt (terminal kaydi), /tmp/ehb_<etiket>.yml (kullanilan yapilandirma)
set -u
tag=$1; per=$2; sym=$3; bw=$4; off=${5:-2}   # 5. arguman (istege bagli): PRS sembol ofseti, varsayilan 2
rep=${6:-1}; gap=${7:-1}; comb=${8:-2}         # 6-8. arguman (istege bagli): repetition_factor, time_gap, comb_size
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
base="$here/../../kurulum/ocudu_testmode.yml"
cfg=/tmp/ehb_$tag.yml
cp "$base" "$cfg"
if [ "${CSI_OFF:-0}" = "1" ]; then     # CSI_OFF=1: CSI-RS kapali (testmode'da CQI sabit; uzun PRS penceresi CSI-RS ile cakisip yapilandirma reddedilmesin)
python3 - "$cfg" <<'EOF2'
import sys
t=open(sys.argv[1]).read()
t=t.replace("  pdcch:\n","  csi:\n    csi_rs_enabled: false\n  pucch:\n    nof_cell_csi_res: 0\n  pdcch:\n",1)   # CSI kapaliyken CSI icin PUCCH kaynagi da 0 olmali (du_high_config_validator.cpp satir 838-841)
open(sys.argv[1],"w").write(t)
EOF2
fi
if [ "$per" != "0" ]; then
python3 - "$cfg" "$per" "$sym" "$bw" "$off" "$rep" "$gap" "$comb" <<'EOF'
import sys
cfg,per,sym,bw,off,rep,gap,comb=sys.argv[1:9]
t=open(cfg).read()
add=f"""  prs:
    resource_sets:
      - comb_size: {comb}
        repetition_factor: {rep}
        time_gap: {gap}
        periodicity_slots: {per}
        slot_offset: 1
        nof_symbols: {sym}
        bandwidth_prbs: {bw}
        resources:
          - sequence_id: 1
            re_offset: 0
            slot_offset: 0
            symbol_offset: {off}
"""
t=t.replace("  pdsch:\n    mcs_table: qam64", add+"  pdsch:\n    mcs_table: qam64",1)
open(cfg,"w").write(t)
EOF
fi
cd ~/ehb415/ocudu/build/apps/gnb
rm -f /tmp/out_$tag.txt
# 8 sn bekle, 't' gonder (metrik tablosu), 22 sn olc, 'q' ile cik
( sleep 8; printf 't\n'; sleep 22; printf 'q\n' ) | timeout 50 script -qc "./gnb -c $cfg" /tmp/out_$tag.txt > /dev/null 2>&1
echo "== $tag per=$per sym=$sym bw=$bw off=$off rep=$rep gap=$gap comb=$comb exit=$?"
sed 's/\x1b\[[0-9;?]*[a-zA-Z]//g' /tmp/out_$tag.txt | tr -d '\r' | grep -E "pci rnti|^ +1 +44 *\||ERROR" | head -14 | cut -c1-150

#!/usr/bin/env bash
# Tek bir OCUDU testmode kosusu: PRS yapilandirmasi ile DL throughput olcer.
# Kullanim (Ubuntu/WSL icinde):  bash ocudu_prs_kos.sh <etiket> <periyot_slot|0> <sembol> <bw_prb> [sembol_ofseti=2]
#   ornek: bash ocudu_prs_kos.sh p4 4 12 104     (PRS her 4 slotta bir, 12 sembol, 104 PRB)
#          bash ocudu_prs_kos.sh base 0 0 0      (PRS yok)
#          bash ocudu_prs_kos.sh e3 4 4 52 0    (PRS ilk sembolden baslar)
# Cikti:  /tmp/out_<etiket>.txt (terminal kaydi), /tmp/ehb_<etiket>.yml (kullanilan yapilandirma)
set -u
if [ "$#" -lt 4 ] || [ "$#" -gt 5 ]; then
  echo "Kullanim: bash $0 <etiket> <periyot_slot|0> <sembol> <bw_prb> [sembol_ofseti=2]" >&2
  exit 2
fi
tag=$1; per=$2; sym=$3; bw=$4
ofs=${5:-2}
if ! [[ "$ofs" =~ ^([0-9]|1[0-3])$ ]]; then
  echo "Hata: sembol ofseti 0 ile 13 arasinda bir tam sayi olmali." >&2
  exit 2
fi
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
base="$here/../../kurulum/ocudu_testmode.yml"
cfg=/tmp/ehb_$tag.yml
cp "$base" "$cfg" || exit $?
if [ "$per" != "0" ]; then
python3 - "$cfg" "$per" "$sym" "$bw" "$ofs" <<'EOF' || exit $?
import sys
cfg,per,sym,bw,ofs=sys.argv[1:6]
t=open(cfg).read()
add=f"""  prs:
    resource_sets:
      - comb_size: 2
        periodicity_slots: {per}
        slot_offset: 1
        nof_symbols: {sym}
        bandwidth_prbs: {bw}
        resources:
          - sequence_id: 1
            re_offset: 0
            slot_offset: 0
            symbol_offset: {ofs}
"""
anchor="  pdsch:\n    mcs_table: qam64"
if t.count(anchor) != 1:
    raise SystemExit("Hata: taban yapilandirmada beklenen pdsch bolumu bulunamadi veya birden fazla bulundu.")
t=t.replace(anchor, add+anchor,1)
open(cfg,"w").write(t)
EOF
fi
cd ~/ehb415/ocudu/build/apps/gnb || exit $?
rm -f /tmp/out_$tag.txt
# 8 sn bekle, 't' gonder (metrik tablosu), 22 sn olc, 'q' ile cik
( sleep 8; printf 't\n'; sleep 22; printf 'q\n' ) | timeout 50 script -eqc "./gnb -c $cfg" /tmp/out_$tag.txt > /dev/null 2>&1
echo "== $tag per=$per sym=$sym bw=$bw ofs=$ofs exit=$?"
sed 's/\x1b\[[0-9;?]*[a-zA-Z]//g' /tmp/out_$tag.txt | tr -d '\r' | grep -E "pci rnti|^ +1 +44 *\||ERROR|collision" | head -14 | cut -c1-150

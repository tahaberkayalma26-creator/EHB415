#!/usr/bin/env bash
# OCUDU: PRS tekrar sayisi / tarak boyutu / bant / periyot degisince iletisim hizi (DL/UL) ne oluyor?
# Hucre: 20 MHz, 15 kHz, 106 PRB (kurulum/ocudu_testmode.yml). Her kosu ~50 sn. Toplam ~7 dk.
# Kullanim (Ubuntu/WSL icinde):  bash ocudu_rep_sweep.sh      Cikti: /tmp/ocudu_rep.csv
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
out=/tmp/ocudu_rep.csv
# etiket periyot sembol bw ofset tekrar bosluk tarak
export CSI_OFF=1      # tum kosularda (taban dahil) CSI-RS kapali; ilk denemede 16 ardisik PRS slotu CSI-RS/CSI-IM/SSB ile cakisip reddedilmisti
CONFIGS=(
  "base 0 0 0 2 1 1 2"
  "b1 40 4 32 2 1 1 4"
  "r8 40 4 32 2 8 1 4"
  "r16c4 40 4 32 2 16 1 4"
  "r16c2 40 4 32 2 16 1 2"
  "r16c12 40 12 32 2 16 1 12"
  "r16p20 20 4 32 2 16 1 4"
  "r16w24 40 4 24 2 16 1 4"
  "r16w40 40 4 40 2 16 1 4"
)
if [ -n "${1:-}" ]; then mapfile -t CONFIGS < "$1"; out="${2:-$out}"; fi   # istege bagli: 1. arguman = yapilandirma listesi dosyasi (satir basina "etiket periyot sembol bw ofset tekrar bosluk tarak"), 2. arguman = cikti csv
for c in "${CONFIGS[@]}"; do
  bash "$here/ocudu_prs_kos.sh" $c > /dev/null 2>&1
done
python3 - "$out" "${CONFIGS[@]}" <<'EOF'
import re, sys, statistics as st
out = sys.argv[1]; rows = []
def deger(s):
    s = s.strip(); k = {"k": 1e-3, "M": 1.0, "G": 1e3}.get(s[-1], None)
    return float(s[:-1]) * k if k else float(s)
for c in sys.argv[2:]:
    tag, per, sym, bw, off, rep, gap, comb = c.split()
    t = open(f"/tmp/out_{tag}.txt", errors="ignore").read()
    t = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", t).replace("\r", "")
    hata = [l.strip() for l in t.splitlines() if "ERROR" in l or "does not fit" in l or "reject" in l.lower()]
    sat = [l.split() for l in t.splitlines() if re.match(r"^ +1 +44 *\|", l)][:14]
    if not sat:
        rows.append((tag, per, sym, bw, rep, gap, comb, "", "", "", "", "olcum yok/reddedildi: " + (hata[0][:90] if hata else "satir bulunamadi"))); continue
    dl = [deger(s[6]) for s in sat]; dok = [int(s[7]) for s in sat]; ul = [deger(s[16]) for s in sat]; uok = [int(s[17]) for s in sat]
    rows.append((tag, per, sym, bw, rep, gap, comb, round(st.median(dl), 1), round(st.median(dok)), round(st.median(ul), 1), round(st.median(uok)), ""))
open(out, "w").write("etiket,periyot_slot,sembol,bw_prb,tekrar,bosluk,tarak,dl_mbps,dl_ok_per_s,ul_mbps,ul_ok_per_s,not\n" + "\n".join(",".join(str(x) for x in r) for r in rows) + "\n")
print(open(out).read())
EOF

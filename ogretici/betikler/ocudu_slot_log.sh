#!/usr/bin/env bash
# OCUDU scheduler'in her slotta ne yaptigini log'dan gosterir (PRS her 4 slotta bir).
# Kullanim (Ubuntu/WSL): bash ocudu_slot_log.sh        Cikti: /tmp/slot_log_excerpt.txt
set -u
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cfg=/tmp/ehb_slotlog.yml
cp "$here/../veri/ocudu_p4_config.yml" "$cfg"
sed -i 's#/tmp/gnb_testmode.log#/tmp/gnb_slotlog.log#; s#all_level: warning#all_level: debug#' "$cfg"
rm -f /tmp/gnb_slotlog.log
cd ~/ehb415/ocudu/build/apps/gnb
timeout 12 ./gnb -c "$cfg" > /dev/null 2>&1
grep -a "Slot decisions" /tmp/gnb_slotlog.log | head -2000 > /tmp/slot_log_all.txt
wc -l /tmp/slot_log_all.txt

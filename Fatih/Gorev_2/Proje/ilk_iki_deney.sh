#!/usr/bin/env bash
# Run only the first two experiments from Fatih's task card, keeping raw evidence.
set -euo pipefail
if [ "$(id -u)" -eq 0 ]; then
  printf '%s\n' 'Run this script as the normal Ubuntu user.' >&2
  exit 1
fi
if pgrep -x gnb >/dev/null; then
  printf '%s\n' 'An existing gNB process is running; leave it intact and stop here.' >&2
  exit 1
fi
repo='/mnt/c/Users/fatih/OneDrive/Desktop/Data Com/EHB415'
run_id="ilk_iki_$(date -u +%Y%m%dT%H%M%SZ)_$$"
run_dir="$HOME/ehb415/fatih_ocudu/$run_id"
export_dir="/mnt/c/Users/fatih/OneDrive/Desktop/Data Com/fatih_ocudu/$run_id"
mkdir -p "$run_dir" "$export_dir"
for condition in base p4; do
  tag="fatih_${run_id}_${condition}"
  if [ "$condition" = base ]; then
    parameters=(0 0 0)
  else
    parameters=(4 12 104)
  fi
  printf 'Running %s: PRS parameters %s\n' "$condition" "${parameters[*]}"
  bash "$repo/ogretici/betikler/ocudu_prs_kos.sh" "$tag" "${parameters[@]}" > "$run_dir/${condition}-invocation.log" 2>&1
  cp "/tmp/out_${tag}.txt" "$run_dir/${condition}-console.txt"
  cp "/tmp/ehb_${tag}.yml" "$run_dir/${condition}.yml"
  if pgrep -x gnb >/dev/null; then
    printf '%s\n' 'A gNB process remains after this run. Stop here before another experiment.' >&2
    exit 1
  fi
done
python3 - "$run_dir" "$export_dir" <<'PY'
import csv, datetime, json, re, shutil, statistics, subprocess, sys
from pathlib import Path

run_dir, export_dir = map(Path, sys.argv[1:])
summary = []
def mbps(value):
    match = re.fullmatch(r'([0-9.]+)([kMG]?)', value)
    if not match:
        raise ValueError('Unrecognized bitrate: ' + value)
    return float(match[1]) * {'': 1e-6, 'k': 1e-3, 'M': 1, 'G': 1e3}[match[2]]

for condition, period, symbols, prbs in [('base',0,0,0), ('p4',4,12,104)]:
    config = (run_dir / f'{condition}.yml').read_text()
    if condition == 'base' and '\n  prs:\n' in config:
        raise RuntimeError('Baseline unexpectedly contains a PRS configuration')
    if condition == 'p4':
        for setting in ['\n  prs:\n', 'periodicity_slots: 4', 'nof_symbols: 12', 'bandwidth_prbs: 104']:
            if setting not in config:
                raise RuntimeError('PRS configuration was not applied: ' + setting)
    raw = (run_dir / f'{condition}-console.txt').read_text(errors='replace')
    clean = re.sub(r'\x1b\[[0-9;?]*[a-zA-Z]', '', raw).replace('\r', '')
    if '==== gNB started ===' not in clean:
        raise RuntimeError(f'{condition}: gNB startup was not confirmed')
    if 'COMMAND_EXIT_CODE="0"' not in clean:
        raise RuntimeError(f'{condition}: clean gNB termination was not confirmed')
    rows = [line for line in clean.splitlines() if re.match(r'^\s+1\s+44\s*\|', line)]
    if len(rows) < 3:
        raise RuntimeError(f'{condition}: insufficient metric samples ({len(rows)})')
    samples = []
    for row in rows[-15:]:
        fields = row.split('|')[1].split()
        samples.append((mbps(fields[3]), float(fields[4])))
    summary.append({'condition':condition, 'prs_period_slots':period, 'prs_symbols':symbols,
                    'prs_prbs':prbs, 'dl_mbps':statistics.mean(x[0] for x in samples),
                    'dl_ok_per_second':statistics.mean(x[1] for x in samples),
                    'averaged_samples':len(samples), 'total_metric_rows':len(rows)})
    (run_dir / f'{condition}-readable.txt').write_text(clean)

loss = 100 * (1 - summary[1]['dl_mbps'] / summary[0]['dl_mbps'])
metadata = {'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'ocudu_commit':subprocess.check_output(['git','-C',str(Path.home()/'ehb415/ocudu'),'rev-parse','HEAD'],text=True).strip(),
            'source_script':str(Path('/mnt/c/Users/fatih/OneDrive/Desktop/Data Com/EHB415/ogretici/betikler/ocudu_prs_kos.sh')),
            'linux_run_directory':str(run_dir), 'conditions':summary, 'dl_loss_percent':loss,
            'limitations':'One run per condition on WSL2, ru_dummy/testmode; measures PRS resource cost, not sensing accuracy or field-network throughput.'}
(run_dir / 'sonuclar.json').write_text(json.dumps(metadata,indent=2)+'\n')
with (run_dir / 'ilk_karsilastirma.csv').open('w',newline='') as stream:
    writer=csv.DictWriter(stream,fieldnames=list(summary[0]))
    writer.writeheader()
    writer.writerows(summary)
for path in run_dir.iterdir():
    if path.is_file():
        shutil.copyfile(path, export_dir / path.name)
print(json.dumps(metadata,indent=2))
print('Results saved:',export_dir)
PY

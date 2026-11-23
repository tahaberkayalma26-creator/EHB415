from pathlib import Path
import subprocess,sys,json,argparse
ROOT=Path('/mnt/c/Users/fatih/OneDrive/Desktop/Data Com/4. Görev Kartı Belgeleri')
p=argparse.ArgumentParser();p.add_argument('--model',action='store_true');args=p.parse_args()
cases=json.loads((ROOT/'Araclar/prs_kosullari.json').read_text())['konfigurasyonlar']
runner=ROOT/'Araclar/olcum_kos.py'
binary='/home/fatih/ehb415/gorev4_runs/bin/'+('gnb_prs_model' if args.model else 'gnb_compat')
selected={'K1','K6','K7','K8','K11'}
for c in cases:
    label=c['etiket']
    if label=='K0' or (args.model and label not in selected):continue
    tag=('sonrasi_' if args.model else 'oncesi_')+label
    vals=[c['periyot_slot'],c['sembol'],c['bw_prb'],c['sembol_ofset'],c['rep'],c['gap'],c['comb']]
    level='debug' if label in selected else ('info' if label in ('K9','K10') else 'warning')
    cmd=[sys.executable,str(runner),tag,'/home/fatih/ehb415/gorev4_runs/band_100.yml',
         '--prs',*map(str,vals),'--binary',binary,'--level',level]
    result=subprocess.run(cmd)
    if result.returncode:raise SystemExit(result.returncode)

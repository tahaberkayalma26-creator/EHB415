from pathlib import Path
import subprocess,sys,json
ROOT=Path('/mnt/c/Users/fatih/OneDrive/Desktop/Data Com/4. Görev Kartı Belgeleri')
RUNNER=ROOT/'Araclar/olcum_kos.py'
BIN='/home/fatih/ehb415/gorev4_runs/bin/gnb_compat'
jobs=[('ref100_1',100,'info'),('ref100_2',100,'warning'),('ref100_3',100,'warning'),
      ('duzeltilmis40',40,'warning'),('duzeltilmis60',60,'warning'),
      ('duzeltilmis80',80,'warning'),('duzeltilmis100',100,'warning')]
for tag,bw,level in jobs:
    cfg='/home/fatih/ehb415/gorev4_runs/band_'+str(bw)+'.yml'
    r=subprocess.run([sys.executable,str(RUNNER),tag,cfg,'--binary',BIN,'--level',level])
    if r.returncode:raise SystemExit(r.returncode)
    d=json.loads((ROOT/'Ham_Kayitlar'/tag/'summary.json').read_text())
    if not d.get('measurement_valid') or d.get('dl_mbps_mean',0)<=0:
        print('REVIEW_REQUIRED',tag,flush=True)
        break

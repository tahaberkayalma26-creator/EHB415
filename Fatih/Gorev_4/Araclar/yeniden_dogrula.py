"""Aynı ikili ve ayarlarla arşivi ezmeden Görev 4 ölçümlerini tekrarlar."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, re, subprocess, sys

ROOT = Path('/mnt/c/Users/fatih/OneDrive/Desktop/Data Com/4. Görev Kartı Belgeleri')
LOCAL = Path('/home/fatih/ehb415/gorev4_runs')
OUT = ROOT / 'Dogrulama'
RUNNER = ROOT / 'Araclar/olcum_kos.py'
KEYS = ['dl_mbps_mean','ul_mbps_mean','dl_ok_mean','ul_ok_mean','dl_nok_mean','ul_nok_mean']

def write(name, value):
    OUT.mkdir(exist_ok=True)
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    if os.environ.get('LD_PRELOAD'):
        raise SystemExit('Unexpected LD_PRELOAD; validation not started')
    if subprocess.run(['pgrep','-f',r'(^|/)(gnb|gnb_compat|gnb_prs_model|gnb_clockguard)( |$)'],capture_output=True).returncode == 0:
        raise SystemExit('Another gNB is running')
    tags = ['ref100_1','ref100_2','ref100_3'] + ['duzeltilmis'+str(b) for b in [40,60,80,100]]
    tags += ['oncesi_K'+str(i) for i in range(1,12)]
    tags += ['sonrasi_'+k for k in ['K1','K6','K7','K8','K11']]
    jobs=[]
    binary_hashes={}
    version=json.loads((ROOT/'Kod_Degisiklikleri/surum_kaydi.json').read_text())
    known={r['path']:r['sha256'] for r in version['binary_records']}
    for old in tags:
        d=json.loads((ROOT/'Ham_Kayitlar'/old/'summary.json').read_text())
        binary=d['binary']
        if binary not in binary_hashes:
            binary_hashes[binary]=hashlib.sha256(Path(binary).read_bytes()).hexdigest()
            if binary_hashes[binary] != known[binary]:
                raise SystemExit('Binary differs from original: '+binary)
        tag='v2_'+old
        if (ROOT/'Ham_Kayitlar'/tag).exists() or (LOCAL/tag).exists():
            raise SystemExit('Will not overwrite existing run '+tag)
        bw=100 if old.startswith(('ref','oncesi','sonrasi')) else int(old.replace('duzeltilmis',''))
        cmd=[sys.executable,str(RUNNER),tag,str(LOCAL/('band_'+str(bw)+'.yml')),
             '--binary',binary,'--level',d['log_level']]
        if old.startswith(('oncesi','sonrasi')):
            cmd+=['--prs',*map(str,d['prs'])]
        jobs.append({'old_tag':old,'new_tag':tag,'command':cmd,'expected':{k:d.get(k) for k in KEYS}})
    plan={'started_utc':datetime.now(timezone.utc).isoformat(),'binary_sha256':binary_hashes,
          'method':'Same frozen binary/configuration/log level; all interior metric rows retained; no LD_PRELOAD.',
          'comparison':'Exact console-value comparison, plus validity/exit/NOK checks; differing rows are investigated, not filtered.',
          'jobs':jobs}
    write('yeniden_kosu_plani.json',plan)
    results=[]
    for i,j in enumerate(jobs,1):
        print(f'VALIDATION {i}/{len(jobs)} {j["new_tag"]}',flush=True)
        subprocess.run(j['command'],check=True)
        d=json.loads((ROOT/'Ham_Kayitlar'/j['new_tag']/'summary.json').read_text())
        delta={k:round(d[k]-j['expected'][k],6) if d.get(k) is not None and j['expected'].get(k) is not None else None for k in KEYS}
        r={'old_tag':j['old_tag'],'new_tag':j['new_tag'],'measurement_valid':d['measurement_valid'],
           'exit':d.get('gnb_returncode'),'metric_rows':d.get('metric_rows'),'used_rows':d.get('used_rows'),
           'old_values':j['expected'],'new_values':{k:d.get(k) for k in KEYS},'delta':delta,
           'console_values_identical':all(v==0 for v in delta.values()),'log_counts':d.get('log_counts',{}),
           'accepted':d['accepted']}
        results.append(r)
        write('yeniden_kosu_sonuclari.json',{'completed':len(results),'total':len(jobs),'results':results})
        print(json.dumps(r,ensure_ascii=False),flush=True)
    print('VALIDATION_FINISHED',flush=True)

if __name__=='__main__':main()

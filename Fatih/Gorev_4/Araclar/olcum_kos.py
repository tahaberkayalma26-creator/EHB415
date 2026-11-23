"""Görev 4 ölçümleri: gerçek gNB çalıştırması, tam kayıt ve tek tip özet."""
from pathlib import Path
import argparse, collections, csv, gzip, json, os, re, shlex, shutil
import statistics, subprocess, threading, time
from datetime import datetime, timezone

ROOT = Path('/mnt/c/Users/fatih/OneDrive/Desktop/Data Com/4. Görev Kartı Belgeleri')
PROJECT = Path('/home/fatih/ehb415/gorev4_project')
LOCAL = Path('/home/fatih/ehb415/gorev4_runs')
SCRIPT = PROJECT / 'ogretici/betikler/ocudu_prs_kos.sh'
ANSI = re.compile(r'\x1b\[[0-9;?]*[a-zA-Z]')

def bitrate(s):
    m = re.fullmatch(r'([\d.]+)([kMG]?)', s.strip())
    if not m:
        raise ValueError(s)
    return float(m[1]) * {'': 1e-6, 'k': 1e-3, 'M': 1, 'G': 1e3}[m[2]]

def main():
    a = argparse.ArgumentParser()
    a.add_argument('tag')
    a.add_argument('base')
    a.add_argument('--prs', nargs=7, type=int, default=[0,0,0,2,1,1,4],
                   metavar=('PER','SYM','BW','OFS','REP','GAP','COMB'))
    a.add_argument('--binary')
    a.add_argument('--level', default='warning')
    a.add_argument('--preload', help='Process-local controlled test helper; never set globally')
    args = a.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_]+', args.tag):
        raise SystemExit('Invalid tag')
    run = LOCAL / args.tag
    dest = ROOT / 'Ham_Kayitlar' / args.tag
    if run.exists() or dest.exists():
        raise SystemExit('Existing run will not be overwritten: '+args.tag)
    if subprocess.run(['pgrep','-x','gnb'],capture_output=True).returncode == 0:
        raise SystemExit('Another gNB is running; no concurrent measurement allowed')
    run.mkdir(parents=True)
    dest.mkdir(parents=True)
    source = Path(args.base)
    text = source.read_text()
    text, n_log_path = re.subn(r'(?m)^(\s*filename:)\s*.*$', lambda m: m[1]+' '+str(run/'gnb.log'), text, count=1)
    if n_log_path != 1:
        raise SystemExit('Exactly one log filename must be set before running')
    text = re.sub(r'all_level:\s*\S+', 'all_level: '+args.level, text, count=1)
    base = run/'base.yml'
    base.write_text(text)
    env = os.environ.copy()
    env['CFG_BASE'] = str(base)
    env['LC_ALL'] = 'C'
    env.pop('CSI_OFF', None)
    if args.binary:
        env['GNB_BIN'] = str(Path(args.binary).resolve())
    if args.preload:
        env['LD_PRELOAD'] = str(Path(args.preload).resolve())
    cmd = ['bash', str(SCRIPT), args.tag] + list(map(str,args.prs))
    command = 'CFG_BASE='+shlex.quote(str(base))+' '
    if args.binary:
        command += 'GNB_BIN='+shlex.quote(env['GNB_BIN'])+' '
    if args.preload:
        command += 'LD_PRELOAD='+shlex.quote(env['LD_PRELOAD'])+' '
    command += shlex.join(cmd)
    (run/'command.txt').write_text(command+'\n',encoding='utf-8')
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.monotonic()
    print('START',args.tag,started,flush=True)
    with (run/'wrapper_output.txt').open('w') as wrapper:
        proc = subprocess.Popen(cmd,cwd=PROJECT,env=env,stdout=wrapper,stderr=subprocess.STDOUT)
        top_proc = None
        gnb_pid = None
        top_file = (run/'top.txt').open('w')
        try:
            while proc.poll() is None:
                if top_proc is None:
                    pattern = '^'+re.escape(str(Path(args.binary).resolve()) if args.binary else './gnb')+' -c '+re.escape('/tmp/ehb_'+args.tag+'.yml')+'$'
                    found = subprocess.run(['pgrep','-n','-f',pattern],capture_output=True,text=True)
                    if found.returncode == 0:
                        pid = found.stdout.strip()
                        gnb_pid = pid
                        top_proc = subprocess.Popen(['top','-b','-d','1','-n','50','-p',pid],
                                                    env=env,stdout=top_file,stderr=subprocess.STDOUT)
                if time.monotonic()-t0 > 65:
                    proc.terminate()
                    raise RuntimeError('Measurement wrapper exceeded 65 seconds')
                time.sleep(0.25)
        finally:
            if top_proc is not None and top_proc.poll() is None:
                top_proc.terminate()
                top_proc.wait(timeout=5)
            top_file.close()
    raw_path = Path('/tmp/out_'+args.tag+'.txt')
    raw = raw_path.read_text(errors='replace') if raw_path.exists() else ''
    clean = ANSI.sub('',raw).replace('\r','')
    (run/'terminal.txt').write_text(clean,encoding='utf-8')
    if raw_path.exists():
        shutil.copy2(raw_path,run/'typescript.txt')
    generated = Path('/tmp/ehb_'+args.tag+'.yml')
    if generated.exists():
        shutil.copy2(generated,run/'config.yml')
    rows=[]
    for line in clean.splitlines():
        if re.match(r'^\s*1\s+44\s*\|',line):
            parts=line.split('|');d=parts[1].split();u=parts[2].split()
            if len(d)>=7 and len(u)>=8:
                rows.append(dict(row=len(rows)+1,dl_mbps=bitrate(d[3]),dl_ok=int(d[4]),
                                 dl_nok=int(d[5]),ul_mbps=bitrate(u[4]),ul_ok=int(u[5]),ul_nok=int(u[6])))
    if rows:
        with (run/'metrics.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    used=rows[1:-1] if len(rows)>=5 else rows
    exit_match=re.search(r'COMMAND_EXIT_CODE="(\d+)"',clean)
    info={'tag':args.tag,'started_utc':started,'elapsed_s':round(time.monotonic()-t0,3),
          'source_config':str(source),'prs':args.prs,'binary':args.binary or 'original e0db566',
          'log_level':args.level,'wrapper_returncode':proc.returncode,
          'controlled_clockstep_helper':str(args.preload) if args.preload else None,
          'gnb_returncode':int(exit_match[1]) if exit_match else None,
          'accepted':'gNB started' in clean,'metric_rows':len(rows),'used_rows':len(used),
          'sample_rule':'first and last metric rows excluded when at least five rows; no loss rows filtered'}
    info['measurement_valid'] = info['accepted'] and 12 <= len(rows) <= 35
    info['measurement_note'] = ('normal metric row count for 22-second reporting window' if info['measurement_valid']
                                else 'rejected/no metrics or abnormal metric timing; row means are diagnostic only')
    for key in ('dl_mbps','ul_mbps','dl_ok','ul_ok','dl_nok','ul_nok'):
        values=[r[key] for r in used]
        info[key+'_mean']=round(statistics.mean(values),6) if values else None
        if key.endswith('mbps'):
            info[key+'_min']=min(values) if values else None
            info[key+'_max']=max(values) if values else None
    cpu=[]
    for line in (run/'top.txt').read_text(errors='replace').splitlines():
        vals=line.split()
        if len(vals)>=12 and vals[0] == gnb_pid:
            try:cpu.append(float(vals[8]))
            except ValueError:pass
    info['top_gnb_cpu_mean']=round(statistics.mean(cpu),2) if cpu else None
    info['top_gnb_cpu_max']=max(cpu) if cpu else None
    info['gnb_pid']=gnb_pid
    counts=collections.Counter();samples=[];pusch_slots=[]
    log=run/'gnb.log'
    if log.exists():
        with log.open(errors='replace') as f:
            for line in f:
                if 'Failed to allocate PUSCH. Cause: No space in PDCCH.' in line:
                    counts['pusch_no_pdcch']+=1
                    m=re.search(r'\[\s*(\d+)\.(\d+)\]',line)
                    if m:pusch_slots.append([int(m[1]),int(m[2])])
                if 'late' in line.lower():counts['late_lines']+=1
                if '[W]' in line:counts['warning_lines']+=1
                if '[E]' in line:counts['error_lines']+=1
                if 'SIB1' in line:counts['sib1_lines']+=1
                if 'Dummy RU backward clock slot detected' in line:counts['dummy_backward_clock_events']+=1
                if len(samples)<120 and any(k in line for k in ('[W]','[E]','No space in PDCCH')):
                    samples.append(line.rstrip())
        info['gnb_log_bytes']=log.stat().st_size
        info['log_counts']=dict(counts)
        if counts['warning_lines'] > 100000:
            info['measurement_valid'] = False
            info['measurement_note'] = 'warning storm / dummy timing instability; row means are diagnostic only'
    if info['gnb_returncode'] != 0:
        info['measurement_valid'] = False
        info['measurement_note'] = 'gNB exited with an error; run not used as a completed reference'
    if args.preload:
        info['measurement_valid'] = False
        info['measurement_note'] = 'synthetic process-local clock regression only; never a performance reference'
    if log.exists():
        (run/'warning_excerpt.txt').write_text('\n'.join(samples)+'\n',encoding='utf-8')
        if pusch_slots:(run/'pusch_failure_slots.json').write_text(json.dumps(pusch_slots),encoding='utf-8')
        with log.open('rb') as src,gzip.open(dest/'gnb.log.gz','wb') as dst:shutil.copyfileobj(src,dst)
    error_lines=[l for l in clean.splitlines() if any(k in l for k in ('ERROR','collision','Invalid'))]
    info['rejection_messages']=error_lines
    (run/'summary.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    for path in run.iterdir():
        if path.is_file() and path.name!='gnb.log':shutil.copy2(path,dest/path.name)
    summaries=[]
    for path in sorted((ROOT/'Ham_Kayitlar').glob('*/summary.json')):
        item=json.loads(path.read_text())
        if 'tag' in item and 'metric_rows' in item:
            summaries.append(item)
    (ROOT/'tum_olcumler.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:info[k] for k in ('tag','accepted','gnb_returncode','metric_rows',
                     'dl_mbps_mean','ul_mbps_mean','dl_ok_mean','ul_ok_mean','top_gnb_cpu_mean')},ensure_ascii=False),flush=True)

if __name__=='__main__':main()

from pathlib import Path
import subprocess,json,sys
ROOT=Path('/mnt/c/Users/fatih/OneDrive/Desktop/Data Com/4. Görev Kartı Belgeleri')
PROJ=Path('/home/fatih/ehb415/gorev4_project')
runner=ROOT/'Araclar/olcum_kos.py'
for tag,bw in [('b100_r2',100),('b100_r3',100),('band40',40),('band60',60),('band80',80),('band100',100)]:
    cfg=Path('/home/fatih/ehb415/gorev4_runs')/('band_'+str(bw)+'.yml')
    cfg.parent.mkdir(parents=True,exist_ok=True)
    txt=(PROJ/'kurulum/ocudu_testmode_n78_100MHz.yml').read_text()
    txt=txt.replace('channel_bandwidth_MHz: 100','channel_bandwidth_MHz: '+str(bw))
    cfg.write_text(txt)
    result=subprocess.run([sys.executable,str(runner),tag,str(cfg)])
    if result.returncode:raise SystemExit(result.returncode)

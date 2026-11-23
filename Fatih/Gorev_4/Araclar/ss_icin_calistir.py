"""Kullanıcı tarafından açılan terminalde yeni OCUDU koşusu ve gerçek çıktı gösterimi."""
from pathlib import Path
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCAL = Path('/home/fatih/ehb415/gorev4_runs')
PROJECT = Path('/home/fatih/ehb415/gorev4_project')
RUNNER = ROOT / 'Araclar/olcum_kos.py'
CHOICES = {
    '1': ('REF', 'referans', 'SS 1 - PRS yok / 100 MHz referans'),
    '2': ('K1', 'oncesi', 'SS 2 - K1 / PRS RB rezervasyonu'),
    '3': ('K1', 'sonrasi', 'SS 3 - K1 / deneysel RE-TBS modeli'),
    '4': ('K6', 'oncesi', 'SS 4 - K6 / PRS RB rezervasyonu'),
    '5': ('K6', 'sonrasi', 'SS 5 - K6 / deneysel RE-TBS modeli'),
    '6': ('K7', 'oncesi', 'EK SS - K7 / PRS RB rezervasyonu'),
    '7': ('K7', 'sonrasi', 'EK SS - K7 / deneysel RE-TBS modeli'),
    '8': ('K8', 'oncesi', 'EK SS - K8 / PRS RB rezervasyonu'),
    '9': ('K8', 'sonrasi', 'EK SS - K8 / deneysel RE-TBS modeli'),
    '10': ('K11', 'oncesi', 'EK SS - K11 / PRS RB rezervasyonu'),
    '11': ('K11', 'sonrasi', 'EK SS - K11 / deneysel RE-TBS modeli'),
}


def block_reason():
    plan = ROOT / 'Dogrulama/yeniden_kosu_plani.json'
    status = ROOT / 'Dogrulama/yeniden_kosu_sonuclari.json'
    if plan.exists():
        if not status.exists():
            return '23 kosuluk dogrulama devam ediyor. Bittigi bildirildikten sonra tekrar acin.'
        d = json.loads(status.read_text(encoding='utf-8'))
        if d.get('completed', 0) < d.get('total', 23):
            return f"Dogrulama devam ediyor: {d.get('completed', 0)}/{d.get('total', 23)}. Simdi yeni kosu baslatilmadi."
    if os.environ.get('LD_PRELOAD'):
        return 'Bu terminalde LD_PRELOAD ayarli. Sentetik saat yardimcisi olmadan yeni bir Ubuntu terminali acin.'
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            first = (p / 'cmdline').read_bytes().split(b'\0', 1)[0].decode(errors='replace')
            name = Path(first).name
            if name == 'gnb' or name.startswith('gnb_'):
                return 'Baska bir gNB calisiyor. Olcumler cakismasin diye yeni kosu baslatilmadi.'
        except (OSError, ProcessLookupError):
            pass
    return None


def run_case(key):
    case, stage, caption = CHOICES[key]
    reason = block_reason()
    if reason:
        print('\n' + reason)
        return
    config_file = LOCAL / 'band_100.yml'
    binary = LOCAL / 'bin' / ('gnb_prs_model' if stage == 'sonrasi' else 'gnb_compat')
    versions = json.loads((ROOT / 'Kod_Degisiklikleri/surum_kaydi.json').read_text(encoding='utf-8'))
    expected = next(r['sha256'] for r in versions['binary_records'] if r['path'] == str(binary))
    if hashlib.sha256(binary.read_bytes()).hexdigest() != expected:
        raise RuntimeError('Kaydedilmis olcum ikilisi degismis; kosu baslatilmadi.')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%f')
    tag = f'ss_{case.lower()}_{stage}_{stamp}'
    command = [sys.executable, str(RUNNER), tag, str(config_file), '--binary', str(binary), '--level', 'warning' if case == 'REF' else 'debug']
    if case != 'REF':
        configs = json.loads((ROOT / 'Araclar/prs_kosullari.json').read_text(encoding='utf-8'))['konfigurasyonlar']
        c = next(c for c in configs if c['etiket'] == case)
        command += ['--prs', *map(str, [c['periyot_slot'], c['sembol'], c['bw_prb'], c['sembol_ofset'], c['rep'], c['gap'], c['comb']])]
    lock_path = ROOT / 'Dogrulama/ss_kosu.lock'
    lock_path.parent.mkdir(exist_ok=True)
    with lock_path.open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('Baska bir ekran goruntusu kosusu devam ediyor. Yeni kosu baslatilmadi.')
            return
        print('\nYeni ve gercek OCUDU kosusu baslatiliyor. Yaklasik 30-60 saniye bekleyin.', flush=True)
        result = subprocess.run(command, cwd=PROJECT)
        if result.returncode:
            print('Calistirma araci hata verdi. Bu cikti basarili olcum olarak kullanilmamali.')
            return
    folder = ROOT / 'Ham_Kayitlar' / tag
    summary = json.loads((folder / 'summary.json').read_text(encoding='utf-8'))
    terminal = (folder / 'terminal.txt').read_text(encoding='utf-8', errors='replace')
    lines = terminal.splitlines()
    metrics = [line for line in lines if re.match(r'^\s*1\s+44\s*\|', line)]
    header = next((line for line in lines if 'pci' in line and 'rnti' in line and 'brate' in line), None)
    print('\n' + '=' * 88)
    print(caption)
    print('Bu kosu simdi calistirildi. Asagisi bu kosunun gercek terminal kaydindan alintidir.')
    print('Kosu: ' + tag)
    print('Ortam: n78 / 30 kHz / 100 MHz / dummy RU ve test UE')
    print('Ikili: ' + binary.name)
    print('-' * 88)
    if header and metrics:
        print('DL ve UL basliklari ile son 8 metrik satiri (satirlar degistirilmedi):')
        print(header)
        for line in metrics[-8:]:
            print(line)
    else:
        print('Metrik satiri bulunamadi. Terminalin son kismi:')
        for line in lines[-18:]:
            print(line)
    print('-' * 88)
    print('gNB cikis kodu:', summary.get('gnb_returncode'), '/ Kabul:', summary.get('accepted'), '/ Olcum gecerli:', summary.get('measurement_valid'))
    print('Ortalamalar: DL', summary.get('dl_mbps_mean'), 'Mbps | UL', summary.get('ul_mbps_mean'), 'Mbps')
    print('DL ok', summary.get('dl_ok_mean'), '| UL ok', summary.get('ul_ok_mean'))
    print('Tam terminal, ayarlar, komut ve gunluk: 4. Gorev Karti Belgeleri/Ham_Kayitlar/' + tag)
    if not summary.get('measurement_valid'):
        print('DIKKAT: Bu kosu gecerli referans degil; bu sonucu inceleme icin de gonderin.')
    print('Bu terminali ekran goruntusu olarak alin. Tarih/etiket ve DL-UL basliklari gorunsun.')
    input('SS alindiktan sonra menuye donmek icin Enter: ')


def show_archive():
    """Yalnız tamamlanmış tekrar koşularını okur; yeni ölçüm başlatmaz."""
    source = ROOT / 'Dogrulama/yeniden_kosu_sonuclari.json'
    if not source.exists():
        print('\nDogrulama bitmedi; tamamlanmis 23 kosunun arsiv ozeti henuz yok.')
        return
    data = json.loads(source.read_text(encoding='utf-8'))
    rows = data.get('results', [])
    if data.get('completed') != 23 or data.get('total') != 23 or len(rows) != 23:
        print('\nDogrulama bitmedi. Arsiv tablosu ancak 23/23 kosu tamamlaninca gosterilir.')
        return
    def number(value):
        if value is None:
            return '-'
        return f'{value:.3f}'.rstrip('0').rstrip('.')
    print('\n' + '=' * 103)
    print('SS 6 - ARSIV OZETI: 23 gercek tekrar kosusundan; canli yeni test degil.')
    print('Kaynak: Dogrulama/yeniden_kosu_sonuclari.json | Hiz: Mbps | ok: yeni kosu ortalamasi')
    print('Degerler en fazla 3 ondalikla gosterilir; tam hassasiyet kaynak JSON dosyasindadir.')
    print(f'{"Kosul":<16} {"Ilk DL":>8} {"Yeni DL":>8} {"Ilk UL":>8} {"Yeni UL":>8} {"DL ok":>9} {"UL ok":>9} {"dDL":>8} {"dUL":>8}')
    print('-' * 103)
    for row in rows:
        old = row['old_values']
        new = row['new_values']
        delta = row['delta']
        flag = '' if row.get('measurement_valid') and row.get('accepted') and row.get('exit') == 0 else ' !'
        print(f'{row["old_tag"]:<16} '
              f'{number(old.get("dl_mbps_mean")):>8} {number(new.get("dl_mbps_mean")):>8} '
              f'{number(old.get("ul_mbps_mean")):>8} {number(new.get("ul_mbps_mean")):>8} '
              f'{number(new.get("dl_ok_mean")):>9} {number(new.get("ul_ok_mean")):>9} '
              f'{number(delta.get("dl_mbps_mean")):>8} {number(delta.get("ul_mbps_mean")):>8}{flag}')
    print('-' * 103)
    print('dDL/dUL = yeni - ilk. ! varsa kosu gecersiz/ret/hata ile bitmistir; gizlenmemistir.')
    print('Bu secenek hicbir gNB programi calistirmadi. Tamamlanmis olcumlerin ozeti okundu.')
    input('Bu ozetin SS goruntusunu aldiktan sonra menuye donmek icin Enter: ')


def main():
    if os.name == 'nt':
        raise SystemExit('Bu arac Windows Python ile degil, Ubuntu/WSL icinde calistirilir.')
    while True:
        print('\nOCUDU GERCEK KOSU VE EKRAN GORUNTUSU')
        print('Ilk rapor icin 1, 2, 3, 4, 5 seceneklerini sirayla kullanin.')
        for key, (_, _, caption) in CHOICES.items():
            print(f'{key:>2}. {caption}')
        print('12. SS 6 - Tamamlanan 23 dogrulama kosusunun ARSIV ozetini goster (yeni test yok)')
        key = input('Secim (cikis: 0): ').strip()
        if key == '0':
            return
        if key == '12':
            show_archive()
            continue
        if key not in CHOICES:
            print('Lutfen listedeki bir sayiyi secin.')
            continue
        run_case(key)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nKullanici tarafindan durduruldu.')
    except Exception as exc:
        print('\nHata:', str(exc))
        sys.exit(1)

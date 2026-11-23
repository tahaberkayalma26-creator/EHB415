"""Görev 4 nihai Word raporu.

Bu dosya hazırlık sırasında yalnız yazılır. Ölçümler bitmeden çalıştırılmaz.
Çalıştırma için açık --final-data-ready bayrağı gerekir. Ham kayıtları değiştirmez.
Yetkili Python, load_workspace_dependencies ile çözülen paket Python yoludur.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from statistics import mean

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT.parent / '2. Görev Kartı Belgeleri' / 'Fatih_Görev_Kartı_2_Çıktıları.docx'
REFERENCE_SHA = 'd1585e9f56a7461e709f2285b8913f2bbf638aa310f1efa234a81e44252ba12c'
FINAL = ROOT / 'Fatih_Gorev_Karti_4_Rapor.docx'
RAW = ROOT / 'Ham_Kayitlar'
SELECTED = ('K1', 'K6', 'K7', 'K8', 'K11')
URLS = [
    ('TS 38.211 V18.2.0', 'https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/18.02.00_60/ts_138211v180200p.pdf'),
    ('TS 38.214 V18.2.0', 'https://www.etsi.org/deliver/etsi_ts/138200_138299/138214/18.02.00_60/ts_138214v180200p.pdf'),
    ('TS 38.212 V18.2.0', 'https://www.etsi.org/deliver/etsi_ts/138200_138299/138212/18.02.00_60/ts_138212v180200p.pdf'),
    ('TS 38.331 V18.6.0', 'https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/18.06.00_60/ts_138331v180600p.pdf'),
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def load_runs():
    # Her koşunun kendi özeti esas alınır; büyüyen toplu JSON kullanılmaz.
    return {p.parent.name: read_json(p) for p in sorted(RAW.glob('*/summary.json'))}


def num(v, digits=1):
    if v is None:
        return '-'
    if isinstance(v, str):
        return v
    if abs(v - round(v)) < 0.0000001:
        return str(int(round(v)))
    return f'{v:.{digits}f}'.replace('.', ',')


def count(run, name):
    return run.get('log_counts', {}).get(name, 0)


def loss(dl, reference=36.0):
    return (1 - dl / reference) * 100 if dl is not None and reference else None


def set_font(font, name='Times New Roman', size=12, bold=None):
    font.name = name
    font.size = Pt(size)
    font.color.rgb = RGBColor(0, 0, 0)
    if bold is not None:
        font.bold = bold


def explicit_font(run, name='Times New Roman', size=12, bold=None):
    set_font(run.font, name, size, bold)
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rpr.insert(0, rf)
    for field in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
        rf.set(qn('w:' + field), name)
    for field in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
        rf.attrib.pop(qn('w:' + field), None)


def configure(doc):
    for name in ('Normal', 'Title', 'Heading 1', 'Heading 2'):
        st = doc.styles[name]
        set_font(st.font, size=12, bold=name != 'Normal')
        st.paragraph_format.line_spacing = 1.0
        st.paragraph_format.space_after = Pt(5)
        st.paragraph_format.space_before = Pt(0 if name in ('Normal', 'Title') else 10)
        if name != 'Normal':
            st.paragraph_format.keep_with_next = True
        for border in list(st.element.findall('.//' + qn('w:pBdr'))):
            border.getparent().remove(border)
    for name in ('Kayıt Alıntısı', 'Kaynak Satırı'):
        if name not in doc.styles:
            doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        st = doc.styles[name]
        st.base_style = doc.styles['Normal']
        st.paragraph_format.space_after = Pt(4)
        st.paragraph_format.line_spacing = 1.0
    set_font(doc.styles['Kayıt Alıntısı'].font, 'Consolas', 9)
    set_font(doc.styles['Kaynak Satırı'].font, size=12)


def new_document():
    if hashlib.sha256(REFERENCE.read_bytes()).hexdigest() != REFERENCE_SHA:
        raise RuntimeError('Referans Word değişmiş; stil kanıtı yeniden incelenmeli.')
    doc = Document(REFERENCE)
    body = doc._element.body
    for child in list(body):
        if child.tag != qn('w:sectPr'):
            body.remove(child)
    configure(doc)
    doc.core_properties.title = 'Fatih Görev Kartı 4 Uygulama ve Sonuç Raporu'
    doc.core_properties.subject = 'OCUDU n78 PRS ölçümleri ve RE TBS kod denemesi'
    doc.core_properties.author = 'Fatih'
    doc.core_properties.keywords = 'Görev 4, OCUDU, PRS, PDSCH, TBS'
    return doc


def para(doc, text='', bold=False, style=None, after=6, keep=False):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.keep_with_next = keep
    p.paragraph_format.widow_control = True
    r = p.add_run(text)
    if style == 'Kayıt Alıntısı':
        explicit_font(r, 'Consolas', 9, bold)
    else:
        explicit_font(r, size=12, bold=bold)
    return p


def heading(doc, text, page=False):
    p = para(doc, text, bold=True, style='Heading 1', after=7, keep=True)
    if page:
        p.paragraph_format.page_break_before = True
    return p


def caption(doc, text):
    p = para(doc, text, after=5, keep=True)
    p.runs[0].italic = True
    return p


def table(doc, headers, rows, widths, left_cols=()):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tpr = t._tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for tag in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        x = OxmlElement('w:' + tag)
        for a, v in {'val': 'single', 'sz': '4', 'color': 'D9D9D9'}.items():
            x.set(qn('w:' + a), v)
        borders.append(x)
    tpr.append(borders)
    margins = OxmlElement('w:tblCellMar')
    for tag, value in [('top', '65'), ('left', '75'), ('bottom', '65'), ('right', '75')]:
        x = OxmlElement('w:' + tag)
        x.set(qn('w:w'), value)
        x.set(qn('w:type'), 'dxa')
        margins.append(x)
    tpr.append(margins)
    for col, w in zip(t.columns, widths):
        col.width = Inches(w)
    allrows = [headers] + list(rows)
    for ri, values in enumerate(allrows):
        cells = t.rows[0].cells if ri == 0 else t.add_row().cells
        trpr = cells[0]._tc.getparent().get_or_add_trPr()
        no_split = OxmlElement('w:cantSplit')
        trpr.append(no_split)
        if ri == 0:
            repeat = OxmlElement('w:tblHeader')
            trpr.append(repeat)
        for ci, (cell, value) in enumerate(zip(cells, values)):
            cell.width = Inches(widths[ci])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if ri == 0:
                shade = OxmlElement('w:shd')
                shade.set(qn('w:fill'), 'E7E6E6')
                cell._tc.get_or_add_tcPr().append(shade)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.keep_with_next = False
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci in left_cols else WD_ALIGN_PARAGRAPH.CENTER
            explicit_font(p.add_run(str(value)), size=12, bold=ri == 0)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return t


def source(doc, text):
    return para(doc, 'Kayıt: ' + text, after=6)


def raw_text(path):
    if not path.exists():
        return ''
    return path.read_text(encoding='utf-8', errors='replace').replace('\r', '')


def command(doc, tag, label=None):
    path = RAW / tag / 'command.txt'
    actual = raw_text(path).strip()
    if not actual:
        return
    para(doc, label or (tag + ' için kaydedilen komut'), bold=True, after=3, keep=True)
    # Satır, yalnız Word akışına göre kaydırılır; komut içeriği değiştirilmez.
    para(doc, actual, style='Kayıt Alıntısı', after=5)


def quote_metrics(doc, tag):
    path = RAW / tag / 'terminal.txt'
    lines = raw_text(path).splitlines()
    sample = next(((i + 1, x) for i, x in enumerate(lines) if re.match(r'^\s*1\s+44\s*\|', x)), None)
    if not sample:
        return
    line_no, text = sample
    parts = text.split('|')
    caption(doc, f'{tag} kaydından alıntı terminal satırı {line_no}')
    if len(parts) >= 3:
        para(doc, 'DL başlıkları cqi ri mcs brate ok nok (%) dl_bs', style='Kayıt Alıntısı', after=0)
        para(doc, parts[1], style='Kayıt Alıntısı', after=3)
        para(doc, 'UL başlıkları pusch rsrp ri mcs brate ok nok (%) bsr ta phr', style='Kayıt Alıntısı', after=0)
        para(doc, parts[2], style='Kayıt Alıntısı', after=3)
    else:
        para(doc, text, style='Kayıt Alıntısı', after=3)
    source(doc, f'Ham_Kayitlar/{tag}/terminal.txt; aynı koşunun metrics.csv ve summary.json dosyaları.')


def warning_quote(doc, tag, keys, limit=2):
    lines = raw_text(RAW / tag / 'warning_excerpt.txt').splitlines()
    picked = [x for x in lines if any(k in x for k in keys)][:limit]
    if not picked:
        return
    caption(doc, tag + ' uyarı kaydından alıntı')
    for x in picked:
        para(doc, x, style='Kayıt Alıntısı', after=3)


def add_hyperlink(paragraph, label, url):
    rel = paragraph.part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    h = OxmlElement('w:hyperlink')
    h.set(qn('r:id'), rel)
    r = OxmlElement('w:r')
    props = OxmlElement('w:rPr')
    rf = OxmlElement('w:rFonts')
    rf.set(qn('w:ascii'), 'Times New Roman')
    rf.set(qn('w:hAnsi'), 'Times New Roman')
    props.append(rf)
    sz = OxmlElement('w:sz'); sz.set(qn('w:val'), '24'); props.append(sz)
    color = OxmlElement('w:color'); color.set(qn('w:val'), '000000'); props.append(color)
    r.append(props)
    txt = OxmlElement('w:t'); txt.text = label; r.append(txt)
    h.append(r); paragraph._p.append(h)


def insert_real_screenshots(doc, root):
    """Yalnız gerçekten var olan görüntü dosyalarını belgeye yerleştirir.

    Hiçbir terminal arayüzü, ekran görüntüsü veya kayıt görselleştirmesi üretilmez.
    İsteğe bağlı rapor_veri.json, ekran görüntülerine ad/açıklama eşleyebilir.
    """
    manifest = root / 'Araclar' / 'rapor_veri.json'
    data = read_json(manifest) if manifest.exists() else {}
    items = data.get('screenshots', [])
    if not items:
        dirs = [root / x for x in ('Ekran_Goruntuleri', 'Ekran Görüntüleri', 'EkranGoruntuleri', 'Ekran_Goruntusu')]
        items = [{'path': str(p), 'caption': p.stem.replace('_', ' ')} for d in dirs if d.exists() for p in sorted(d.glob('*')) if p.suffix.lower() in ('.png', '.jpg', '.jpeg')]
    count_images = 0
    for item in items:
        p = Path(item['path'])
        if not p.is_absolute():
            p = root / p
        if not p.exists() or p.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
            continue
        if count_images == 0:
            heading(doc, 'Gerçek ekran kayıtları', page=True)
        if count_images and count_images % 2 == 0:
            doc.add_page_break()
        caption(doc, item.get('caption', p.stem))
        doc.add_picture(str(p), width=Inches(6.5))
        source(doc, str(p.relative_to(root)) if p.is_relative_to(root) else str(p))
        count_images += 1
    return count_images


def required_checks(runs):
    required = ['b100_r1', 'b100_r2', 'b100_r3', 'band40', 'band60', 'band80', 'band100',
                'ref100_1', 'ref100_2', 'ref100_3', 'duzeltilmis40', 'duzeltilmis60',
                'duzeltilmis80', 'duzeltilmis100', 'veri_genisligi100']
    required += ['oncesi_K' + str(i) for i in range(1, 12)]
    required += ['sonrasi_' + k for k in SELECTED]
    missing = [x for x in required if x not in runs]
    if missing:
        raise RuntimeError('Nihai rapor için eksik koşular: ' + ', '.join(missing))
    if not (ROOT / 'Standart_Incelemesi.md').exists():
        raise RuntimeError('Standart_Incelemesi.md nihai kaynak metni bulunamadı.')
    for tag in ['ref100_1', 'ref100_2', 'ref100_3'] + ['oncesi_K' + str(i) for i in range(1, 12)] + ['sonrasi_' + k for k in SELECTED]:
        r = runs[tag]
        # Ret koşulu meşru sonuçtur; kabul edilmiş ama bozuk koşu geçerli sayılmaz.
        if r.get('accepted') and not r.get('measurement_valid'):
            raise RuntimeError(f'{tag}: kabul edilmiş fakat geçersiz ölçüm; rapor kararı gerektiriyor.')


def build():
    runs = load_runs()
    configs = read_json(ROOT / 'Araclar' / 'prs_kosullari.json')['konfigurasyonlar']
    config_map = {x['etiket']: x for x in configs}
    required_checks(runs)
    doc = new_document()

    # 1 — Çalışmanın kapsamı ve yöntem.
    para(doc, 'Fatih Görev Kartı 4 Uygulama ve Sonuç Raporu', bold=True, style='Title', after=9)
    para(doc, '20 Kasım 2026', after=9)
    para(doc, 'OCUDU üzerinde 100 MHz başlangıç sorunu incelendi, n78 bant taraması ve PRS koşulları ölçüldü. İki yerel uyumluluk düzeltmesinden sonra üç PRS’siz 100 MHz referansında DL 36 Mbps ve UL 119 Mbps elde edildi; veri PDSCH genişliği 48 PRB olarak doğrulandı.')
    para(doc, 'PRS için K0–K11 karşılaştırması ve seçilen beş koşulda RE/TBS kod denemesi yapıldı. Sonuçlar radyosuz ru_dummy ve no_core test ortamında tek sanal UE’nin MAC metrikleridir; gerçek radyo, çekirdek şebeke veya standart UE üzerinde uçtan uca hız ölçümü değildir.')
    heading(doc, 'Kullanılan ortam ve kaynaklar')
    table(doc, ['Öğe', 'Kaydedilen değer'], [
        ('Sistem', 'Ubuntu 24.04 WSL'),
        ('OCUDU', '26.10.0  e0db566aac6e6376ddd60e83c84f58698fcc4d70'),
        ('Görev projesi', '4c31d938648abb355e0befdd8221ae0d5cdfbbbb'),
        ('Hücre', 'n78 TDD  3500,01 MHz  30 kHz SCS  1T1R'),
        ('Ana ızgara', '100 MHz  273 PRB  slot süresi 0,5 ms'),
        ('TDD', '10 slotta 6 DL slot  8 DL sembollü karışık slot  3 UL slot'),
        ('Trafik', 'Tek test UE  doygun DL ve UL  CQI 15  dummy CQI açık'),
    ], [1.4, 5.1], left_cols=(0, 1))
    para(doc, 'K0–K10 parametreleri kullanıcının 22 505 baytlık ortak_degerler.xlsx dosyasından alındı. Eksik K11, güncel proje deposunun 4c31d938 sürümündeki Excel’in A13:H13 aralığından ayrıca eklendi. rep=1 ve gap=1, kart örneği ve güncel betik varsayılanı olarak uygulandı; bu iki değer Excel’de açıkça tanımlı değildi.')
    para(doc, 'Koşular tek tek çalıştırıldı. En az beş metrik satırı varsa ilk ve son satır dışarıda bırakıldı; NOK veya düşük hız satırları filtrelenmedi. CPU değerleri top örnekleridir ve birden çok çekirdekte yüzde 100’ü aşabilir. Uyarı fırtınası ve anormal slot ilerlemesi olan ilk koşular hız ortalamasına alınmadı.')
    source(doc, 'Yapilan_Islemler.md; Araclar/prs_kosullari.json; koşuların config.yml ve summary.json dosyaları.')

    # 2 — Özgün sürümde başlangıç ve bant taraması.
    heading(doc, 'Özgün sürümde 100 MHz ve bant taraması', page=True)
    para(doc, 'Özgün e0db566 sürümüyle 100 MHz üç kez ve 40 60 80 100 MHz birer kez çalıştırıldı. Yapılandırmalar kabul edildi; ancak zamanlama bozulması ve yoğun uyarı kayıtları nedeniyle bu koşular tamamlanmış hız referansı sayılmadı. Bazen görülen 36 ve 119 Mbps satırları, tüm koşunun kararlı çalıştığını göstermedi.')
    rows = []
    for tag in ['b100_r1', 'b100_r2', 'b100_r3', 'band40', 'band60', 'band80', 'band100']:
        r = runs[tag]
        rows.append((tag, r.get('metric_rows', 0), f"{num(r.get('top_gnb_cpu_mean'))} / {num(r.get('top_gnb_cpu_max'))}",
                     f"{num(r.get('gnb_log_bytes', 0) / 1000000)}", count(r, 'warning_lines'), r.get('gnb_returncode')))
    caption(doc, 'İlk koşuların tanısal kayıtları hız ortalaması olarak kullanılmadı')
    table(doc, ['Koşu', 'Metrik satırı', 'CPU % ort en çok', 'Günlük MB', 'Uyarı', 'Çıkış'], rows,
          [1.1, .75, 1.35, .9, 1.5, .9], left_cols=(0,))
    para(doc, 'b100_r1 ve b100_r3 günlüklerinde yaklaşık 2,46 ve 2,20 saniyelik UTC geri sıçramaları ile 20 971 520 slotluk sayaç çevrimine yakın yapay ilerleme birlikte görüldü. b100_r3’te normal sayıda metrik satırı bulunsa da yoğun uyarı fırtınası bu koşunun geçerli sayılmasını engelledi. 40 MHz denemesi bir süre 36 ve 44,9 Mbps verdi, ardından dosyaya yazma hatasıyla 134 çıkış kodunda durdu.')
    para(doc, 'CPU artışı tek başına neden olarak atanmadı. Saat geri okuması, MAC kuyruk taşması ve yoğun günlük üretimi birlikte değerlendirildi; kısa bağımsız saat testlerinde sıçrama görülmemesi de olumsuz bulgu olarak saklandı.')
    command(doc, 'b100_r1')
    source(doc, 'Ham_Kayitlar/b100_r1–r3 ve band40 band60 band80 band100; 100MHz_Sorun_Analizi.md. MB ondalık birimdir.')

    # 3 — Birbirinden ayrı iki düzeltme.
    heading(doc, 'İki bağımsız sorun ve yerel düzeltmeler', page=True)
    para(doc, 'Saat geri okuması', bold=True, keep=True)
    para(doc, 'RU dummy slot üretimi system_clock üzerinden yapılıyordu. Hedef slota yalnız ileri sayarak gidildiğinden küçük bir geri saat farkı neredeyse tam sayaç turu kadar işlemeye dönüşebiliyordu. İzole fatih/gorev4-clockguard dalında çevrimin yarısından büyük modüler farkın geri okuma olarak kaydedilip o turda slot üretiminin bekletilmesi eklendi. İşletim sistemi saatinin altta yatan geri sıçrama nedeni belirlenmedi.')
    para(doc, 'ConRes sonrası eksik planlayıcı bildirimi', bold=True, keep=True)
    para(doc, 'Saat koruması bulunan ilk denemelerde trafik yine sıfır kaldı. Test adaptörünün Msg4 planlanınca RRCSetupComplete üretmesi, ConRes tamamlanmadan yapılandırma bildirimini öne çekiyordu. UE fallback durumundan çıktığında eksik kalan slice_sched.config_applied(ue_index) çağrısı tamamlandı. BUILD_TESTING seçeneğinin kapalı olması neden değildi; test modu adaptörleri bu seçenekten bağımsız derleniyordu.')
    table(doc, ['Yama', 'Değiştirilen yol ve amaç'], [
        ('01_dummy_saat_korumasi.patch', 'lib/ru/dummy/ru_dummy_impl.cpp  geri slot okumasında tam turu önleme'),
        ('02_conres_slice_bildirimi.patch', 'lib/scheduler/ue_scheduling/cell_group_event_manager.cpp  ConRes ACK sonrasında dilim kaydını tamamlama'),
        ('00_referans_uyumluluk_toplu.patch', 'İki uyumluluk değişikliğinin birleşik hali  gnb_compat referansı'),
    ], [2.5, 4.0], left_cols=(0, 1))
    para(doc, 'Özgün kurulumun yerine ayrı çalışma ağacı ve ayrı yürütülebilir dosyalar kullanıldı. Bu iki uyumluluk değişikliği PRS RE/TBS modelinden ayrı tutuldu. gnb_clockguard yalnız saat korumasını, gnb_compat saat korumasını ve ConRes bildirimini içerdi.')
    if 'clockstep2_korumali' in runs and 'clockstep2_korumasiz' in runs:
        para(doc, 'Kontrollü saat regresyonu', bold=True, keep=True)
        a = runs['clockstep2_korumasiz']; b = runs['clockstep2_korumali']
        para(doc, 'Yalnız gNB sürecinin CLOCK_REALTIME okuması beş saniye sonra iki saniye geri kaydırıldı; işletim sistemi saati değiştirilmedi. ' +
             f"Korumasız koşuda {count(a, 'warning_lines')} uyarı ve {num(a.get('gnb_log_bytes', 0) / 1000000)} MB günlük; " +
             f"korumalı koşuda {count(b, 'warning_lines')} uyarı ve {num(b.get('gnb_log_bytes', 0) / 1000000)} MB günlük oluştu. " +
             f"Korumadaki {count(b, 'dummy_backward_clock_events')} kayıt, tek kalıcı geri fark boyunca yinelenen koruma bildirimleridir; ayrı saat sıçramaları değildir. " +
             'Korumalı koşuda 36 ve 119 Mbps satırları korundu. Yapay tanı koşuları ana hız referanslarına katılmadı.')
    else:
        para(doc, 'Saat korumasının doğal sıçrama görülmeyen referanslarda çalışması, kontrollü geri sıçrama altında etkinlik kanıtı sayılmadı. İşletim sistemi saatinin altta yatan davranışına ilişkin belirsizlik korundu.')
    source(doc, '100MHz_Sorun_Analizi.md; Kod_Degisiklikleri/*.patch; Kod_Degisiklikleri/surum_kaydi.json; tanisal100_info kayıtları.')

    # 4 — Düzeltilmiş referans ve veri genişliği.
    heading(doc, 'Düzeltilmiş referanslar ve PDSCH veri genişliği', page=True)
    para(doc, 'gnb_compat ile yapılan üç 100 MHz referansında aynı DL ve UL hızları görüldü. 40–100 MHz düzeltilmiş taramada DL 36 Mbps kaldı; UL, kanal genişliği arttıkça yükseldi. DL’nin sabit kalması tek UE’nin bu yapılandırmadaki 48 PRB veri tahsisiyle birlikte yorumlandı.')
    rows = []
    for tag, label in [('ref100_1','100 MHz ref 1'),('ref100_2','100 MHz ref 2'),('ref100_3','100 MHz ref 3'),('duzeltilmis40','40 MHz'),('duzeltilmis60','60 MHz'),('duzeltilmis80','80 MHz'),('duzeltilmis100','100 MHz')]:
        r = runs[tag]
        rows.append((label, num(r.get('dl_mbps_mean')), num(r.get('ul_mbps_mean')), num(r.get('dl_ok_mean')), num(r.get('ul_ok_mean')), num(r.get('top_gnb_cpu_mean'))))
    table(doc, ['Koşu', 'DL Mbps', 'UL Mbps', 'DL ok', 'UL ok', 'CPU % ort'], rows,
          [1.55, .95, .95, .9, .9, 1.25], left_cols=(0,))
    quote_metrics(doc, 'ref100_1')
    width = runs['veri_genisligi100']
    ranges = width.get('prb_ranges', {})
    para(doc, 'Veri genişliği için veri akışı açıkken debug kaydındaki UE PDSCH satırları incelendi. ' +
         f"[0..48) aralığı {ranges.get('0..48', 0)} kez görüldü ve baskın veri genişliği 48 PRB olarak alındı. " +
         'Diğer tahsisler [0..17), [10..48), [0..42) ve [0..2) aralıklarındaydı; her tahsisin tam 48 PRB olduğu ileri sürülmedi. Hücrenin toplam 273 PRB olması ile tek PDSCH veri tahsisi ayrıldı.')
    command(doc, 'veri_genisligi100', 'Veri tahsis kaydının alınmasında kullanılan komut')
    warning_quote(doc, 'ref100_1', ['SIB1', '[E]'], 1)
    para(doc, 'Metrikler sıfır NOK gösterse de günlükler tümüyle temiz değildi. SIB1 hata satırları ve late kayıtları korunarak sayıldı; dummy CQI açık olması nedeniyle bunlar gerçek kanal kalitesi veya BLER kanıtı olarak yorumlanmadı.')
    source(doc, 'Ham_Kayitlar/ref100_1–3 duzeltilmis40–100 veri_genisligi100; config.yml ve sıkıştırılmış tam günlükler.')

    # 5 — Koşul tanımları.
    heading(doc, 'K0 ile K11 arasında PRS koşulları', page=True)
    para(doc, 'Aşağıdaki tabloda yalnız koşulu değiştiren PRS parametreleri gösterildi. K0 PRS’siz referanstır. Bütün etkin PRS koşullarında tekrar ve gap değeri 1 uygulandı. Sembol ve slot ofsetleri sıfırdan başlayan indislerdir.')
    rows = []
    for k in ['K' + str(i) for i in range(12)]:
        c = config_map[k]
        rows.append((k, c['periyot_slot'], c['sembol'], c['comb'], c['bw_prb'], c['sembol_ofset'], c['slot_ofset']))
    table(doc, ['Koşul', 'Periyot slot', 'Sembol', 'Comb', 'PRS PRB', 'Sembol ofseti', 'Slot ofseti'], rows,
          [.62, .96, .85, .78, .96, 1.23, 1.1])
    para(doc, 'K11 için 10 slot periyot, 6 sembol, comb 6, 48 PRB, sembol ofseti 2 ve slot ofseti 1 kullanıldı. Bu satır kullanıcının özgün dosyasında bulunmadığından güncel depo kaynağı raporda ve sonuç çalışma kitabında ayrıca işaretlendi.')
    para(doc, 'Çalıştırma parametre sırası etiket periyot sembol PRB sembol_ofseti rep gap comb biçimindedir. Slot ofseti ayar dosyasından gelir; bu koşullarda 1’dir. Koşu bazında gerçek üretilen config.yml dosyası saklandı.')
    command(doc, 'oncesi_K1', 'K1 koşulunun gerçek komutu')
    source(doc, 'Araclar/prs_kosullari.json; Ham_Kayitlar/oncesi_K1–K11/command.txt ve config.yml; Kaynaklar/Proje/ogretici/veri/ortak_degerler.xlsx.')

    # 6 — Ölçüm sonuçları ve beklenen kaybın ayrılması.
    heading(doc, 'PRS koşullarının ölçüm sonuçları', page=True)
    para(doc, 'K0 için üç 100 MHz referansının ortalaması alındı. Diğer koşullar gnb_compat ile ölçüldü. Model sütunu kaynak Excel’in öngörüsüdür; ölçülen DL kaybı 36 Mbps referansa göre ayrıca hesaplandı. Model ve ölçüm aynı değer olarak sunulmadı.')
    rows = []
    ref = mean(runs['ref100_' + str(i)]['dl_mbps_mean'] for i in range(1, 4))
    rows.append(('K0', num(ref), '119', '1200 / 600', 'Kabul', '0', '0'))
    for i in range(1, 12):
        k = 'K' + str(i); r = runs['oncesi_' + k]; c = config_map[k]
        model = c.get('model_kaybi_oran')
        if model is None:
            # K11 için kaynak önbelleği boş; formül sonucu ölçüm olarak icat edilmez.
            model_label = '-'
        else:
            model_label = num(model * 100)
        rows.append((k, num(r.get('dl_mbps_mean')), num(r.get('ul_mbps_mean')),
                     f"{num(r.get('dl_ok_mean'))} / {num(r.get('ul_ok_mean'))}",
                     'Kabul' if r.get('accepted') else 'Ret', model_label,
                     num(loss(r.get('dl_mbps_mean'), ref)) if r.get('accepted') else '-'))
    table(doc, ['Koşul', 'DL Mbps', 'UL Mbps', 'DL UL ok', 'Sonuç', 'Model kayıp %', 'Ölçülen DL kayıp %'], rows,
          [.6, .8, .8, 1.2, .82, 1.14, 1.14])
    rejections = [(k, runs['oncesi_' + k]) for k in ['K' + str(i) for i in range(1, 12)] if not runs['oncesi_' + k].get('accepted')]
    if rejections:
        for k, r in rejections:
            para(doc, k + ' reddi: ' + '; '.join(r.get('rejection_messages', [])))
    else:
        para(doc, 'K1–K11 yapılandırmalarının tamamı bu n78 TDD ayarlarıyla kabul edildi. K9 ve K10’da UL 119 Mbps kaldı; önceki band 3 FDD çalışmasındaki yüzde 25 UL düşüşü bu yeni ortama aktarılmadı.')
    para(doc, 'K1 için kaynak model yüzde 16,7 kayıp öngördü; ölçülen 29 Mbps, 36 Mbps referansa göre yüzde 19,4 kayıp verdi. Fark, kaynak modelin TDD takvimi ve gerçek scheduler tahsisleriyle aynı hesap olmamasını gösterir. K11’in kaynak formül önbelleği boş olduğundan model değeri çizgiyle bırakıldı.')
    pdcch = [(k, count(runs['oncesi_' + k], 'pusch_no_pdcch')) for k in ['K' + str(i) for i in range(1, 12)]]
    para(doc, 'PUSCH için No space in PDCCH mesajı sayıları: ' + '; '.join(k + ' ' + str(v) for k, v in pdcch) + '. Başarılı işlem sayısı ile NOK ve günlük hata sayısı ayrı alanlardır.')
    para(doc, 'Bütün K1–K11 metriklerinde DL ve UL NOK ortalaması sıfırdı. Buna rağmen K1 günlüğünde 1584 hata ve 1586 SIB1 içeren satır, K9’da 1593 hata ve K10’da 531 hata kaydedildi. SIB1 ve diğer günlük hataları başarılı trafik ölçümünden ayrı tutuldu; hata satırları silinmedi.')
    source(doc, 'Ham_Kayitlar/oncesi_K1–K11/summary.json metrics.csv gnb.log.gz; kaynak model için Araclar/prs_kosullari.json.')

    # 7 — Model denemesi ve kapsam sınırı.
    heading(doc, 'PRS RE ve TBS kod denemesi', page=True)
    para(doc, 'Özgün scheduler PRS’nin comb alt taşıyıcıları yerine PRS genişliğindeki bütün RB ve sembol dikdörtgenini kapatıyordu. Deneysel yamada bu genel rezervasyon kaldırıldı; yeni UE PDSCH tahsisinin fiziksel CRB aralığı ile örtüşen PRS veri RE’leri TBS bütçesinden düşüldü. PRS kaynak maskeleri birleştirildi ve DMRS nedeniyle zaten veri taşımayan RE’ler ikinci kez sayılmadı.')
    para(doc, 'Özgün TBS hesabı lib/ran/sch/tbs_calculator.cpp:109-110’da nPRB × min(12 × sembol − DMRS − overhead, 156) şeklindedir. mcs_tbs_calculator.cpp:216-223 hesabın girdilerini iletir. Değiştirilen hesapta 111. satır PRS veri RE giderini çıkarır; TBS ve etkin kod oranı aynı giderle güncellenir. Bu hesap deneysel scheduler/TBS muhasebesidir.')
    rows = []
    for k in SELECTED:
        a = runs['oncesi_' + k]; b = runs['sonrasi_' + k]
        rows.append((k, num(a.get('dl_mbps_mean')), num(b.get('dl_mbps_mean')),
                     num(b.get('dl_mbps_mean') - a.get('dl_mbps_mean')) if a.get('dl_mbps_mean') is not None and b.get('dl_mbps_mean') is not None else '-',
                     num(a.get('ul_mbps_mean')) + ' / ' + num(b.get('ul_mbps_mean')),
                     num(a.get('dl_ok_mean')) + ' / ' + num(b.get('dl_ok_mean'))))
    caption(doc, 'Aynı 100 MHz ortamında seçilen beş koşulun önce ve sonra değerleri')
    table(doc, ['Koşul', 'DL önce Mbps', 'DL sonra Mbps', 'DL fark Mbps', 'UL önce sonra', 'DL ok önce sonra'], rows,
          [.6, 1.0, 1.0, 1.0, 1.4, 1.5])
    validation = read_json(ROOT / 'model_dogrulama.json')
    observed = []
    for k in SELECTED:
        v = validation['sonrasi_' + k]
        counter = v.get('prs_excluded_data_re_counts', {})
        common = max(counter, key=lambda x: counter[x]) if counter else '-'
        observed.append(k + ' ' + common)
    if not all(validation[stage + '_' + k].get('no_retx_verified') for stage in ('oncesi', 'sonrasi') for k in SELECTED):
        raise RuntimeError('Seçilen RE denemelerinde nrtx=0 doğrulaması eksik.')
    para(doc, 'Debug kaydındaki baskın çıkarılan veri RE sayıları: ' + '; '.join(observed) +
         '. Daha dar tahsislerde daha küçük giderler de görüldü. Bu değerler ham PRS RE hesabından farklıdır; PDSCH sembol aralığı ve DMRS veri dışı maskesi hesaba katıldı. Seçilen on koşunun tamamında nrtx=0 doğrulandı.')
    para(doc, 'Yama PRS için PHY reserved RE maskesi, FAPI aktarımı veya UE tarafında kaynak eşleme bildirimi eklemedi. Fiziksel PRS/DMRS yazım çakışması çözülmedi. Artan MAC/TBS sayacı, gerçek PRS ve PDSCH’nin standart UE üzerinde birlikte çalıştığının veya radyo hızının arttığının kanıtı değildir.')
    para(doc, 'Deneme yalnız yeni PDSCH iletim yolunu kapsadı. HARQ yeniden iletiminde eski TBS korunur; PDSCH repetition, SIB1, paging, RAR ve fallback yolları için ortak güvenli eşleme geliştirilmedi. Beş sonraki koşunun her birinde hata satırı 0, SIB1 içeren satır 2 ve late satırı 5’ti; DL ve UL NOK 0’dı. SIB1 içeren satır sayısı hata sayısıyla eş tutulmadı.')
    command(doc, 'sonrasi_K1', 'RE modeli sonrasında K1 için kullanılan komut')
    source(doc, 'Kod_Degisiklikleri/03_tum_deney_degisiklikleri.patch uygulanmış son haldir; 02_prs_re_tbs_modeli.patch model tasarımıdır. Son_Kaynaklar ve model_dogrulama.json ile oncesi ve sonrasi koşuları saklandı.')

    # 8 — Standart sorusuna açık cevap ve izlenebilir kayıtlar.
    heading(doc, 'Standart sorusunun cevabı ve kanıt kayıtları', page=True)
    para(doc, 'Gerçek UE PDSCH kaynak boşluklarını nasıl öğrenir', bold=True, keep=True)
    para(doc, 'Gerçek UE, gNB içindeki PRS RE maskesini kendiliğinden öğrenmez; TS 38.214 V18.2.0 madde 5.1.4–5.1.4.1 uyarınca RRC ile yapılandırılan rezervasyonları ve gerektiğinde DCI 1_1’in Rate matching indicator seçimini kullanarak PDSCH eşlemesini belirler. RateMatchPattern, PRS taşıyan RB ve sembolleri korumaya elverişli olsa da PRS comb RE’lerini tek tek bildiren bir alan değildir; dolayısıyla PRS alım yapılandırması veya yalnız vericide RE çıkarılması, gerçek UE’nin aynı PDSCH boşluklarını uygulayacağını kanıtlamaz.')
    para(doc, 'TS 38.211 madde 7.3.1.5 ve 7.4.1.7.3, PDSCH ve PRS kaynak eşlemesini ayrı kurallarla tanımlar. TS 38.214 madde 5.1.3.2 TBS hesabını; 5.1.4–5.1.4.1 kaynak rezervasyonlarını açıklar. TS 38.331 madde 6.3.2 içindeki RateMatchPattern RB ve OFDM sembolü bitmap’lerini, TS 38.212 madde 7.3.1.2.2 DCI rate matching indicator seçimini tanımlar. PRS alım ayarı tek başına PDSCH comb maskesi bildirimi değildir.')
    for name, url in URLS:
        p = para(doc, '', after=3)
        add_hyperlink(p, name + ' resmi ETSI metni', url)
        para(doc, url, style='Kayıt Alıntısı', after=5)
    para(doc, 'Ham kayıtların okunması', bold=True, keep=True)
    para(doc, 'Her koşunun command.txt dosyası çalıştırılan komutu, config.yml dosyası etkin ayarları, terminal.txt dosyası tam konsol çıktısını, metrics.csv dosyası bütün metrik satırlarını ve summary.json dosyası türetilen özeti içerir. top.txt CPU örneklerini, gnb.log.gz sıkıştırılmış tam günlüğü içerir. Uyarı ve hata satırları temizlenmedi.')
    para(doc, 'Derleme ve kod kontrolü', bold=True, keep=True)
    build_log = raw_text(ROOT / 'Kod_Degisiklikleri' / 'Derleme_Kayitlari' / 'final_build_check.log')
    build_command = next((x for x in build_log.splitlines() if x.startswith('$ ')), '')
    if build_command:
        para(doc, build_command, style='Kayıt Alıntısı', after=4)
    para(doc, 'Son derleme kontrolü 0 çıkış koduyla tamamlandı. git diff --check ve birleşik yamanın git apply --reverse --check kontrolleri başarılıydı; ters uygulama yapılmadı. Ayrı saat koruması, uyumluluk ve PRS modeli derleme günlükleri Derleme_Kayitlari altında korundu.')
    para(doc, 'Sonuçların kullanım sınırı', bold=True, keep=True)
    para(doc, 'Bu rapor, OCUDU test modunda yapılandırma kabulünü, MAC trafik metriklerini ve scheduler/TBS denemesini belgeledi. Saha kapsaması, gerçek UE alımı, gerçek PRS doğruluğu, RF performansı veya standartlarla tam birlikte çalışma sonucu çıkarılmadı. Koşu bazındaki tam değerler ve hata sayıları sonuç çalışma kitabıyla birlikte değerlendirilmelidir.')
    source(doc, 'Standart_Incelemesi.md; Kaynaklar/Standart resmi PDF kopyaları; Ham_Kayitlar; Kod_Degisiklikleri; Yapilan_Islemler.md.')

    added_images = insert_real_screenshots(doc, ROOT)
    doc.save(FINAL)
    # Nihai içerik denetimi: eski rapor metni ve birinci şahıs kalmamalı.
    visible = '\n'.join(p.text for p in doc.paragraphs)
    for t in doc.tables:
        visible += '\n' + '\n'.join(c.text for r in t.rows for c in r.cells)
    for bad in ('Görev Kartı 2 Görev Uygulaması', 'hazırladığım', 'çalıştırdım', 'çalıştırıyoruz', ' [[', 'TODO', 'TBD'):
        if bad in visible:
            raise RuntimeError('Rapor içeriği denetimi başarısız: ' + bad)
    print(json.dumps({'docx': str(FINAL), 'runs': len(runs), 'images': added_images,
                      'tables': len(doc.tables), 'paragraphs': len(doc.paragraphs),
                      'reference_sha_unchanged': hashlib.sha256(REFERENCE.read_bytes()).hexdigest() == REFERENCE_SHA}, ensure_ascii=False))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--final-data-ready', action='store_true', help='Bütün deneyler tamamlandıktan sonra kullanılır.')
    args = parser.parse_args()
    if not args.final_data_ready:
        parser.error('Nihai veri onayı olmadan rapor üretilmez. --final-data-ready bayrağı gerekir.')
    build()

"""Beğenilen tablo raporunun metnini korur; sonuç görsellerini ve veri sunumunu değiştirir."""
from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile
import hashlib,json,shutil,sys
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'Araclar/SS_Rapor_QA/aligned'
QA.mkdir(parents=True,exist_ok=True)
REF=ROOT/'Fatih_Gorev_Karti_4_Rapor.docx'
REF_SHA='e4d06a0b5a3d5e1e7b4015801a7baed3b2e37a568305bd4ee56f6b043a6a0ca3'
assert hashlib.sha256(REF.read_bytes()).hexdigest()==REF_SHA
OUT=ROOT/'Fatih_Gorev_Karti_4_Ekran_Goruntulu_Rapor.docx'
BACK=ROOT/'Araclar/SS_Rapor_QA/onceki_duzen'
BACK.mkdir(exist_ok=True)
for name in ['Fatih_Gorev_Karti_4_Ekran_Goruntulu_Rapor.docx','Fatih_Gorev_Karti_4_Ekran_Goruntulu_Rapor.pdf']:
    p=ROOT/name
    if p.exists() and not (BACK/name).exists():shutil.copy2(p,BACK/name)
old_crop=ROOT/'Araclar/SS_Rapor_QA/crop_and_package_check.json'
if old_crop.exists() and not (BACK/old_crop.name).exists():shutil.copy2(old_crop,BACK/old_crop.name)
records=json.loads((BACK/old_crop.name).read_text(encoding='utf-8'))['images']
records=[r for r in records if r['key']!='archive']
assert len(records)==5
source=Document(REF);blocks=list(source.element.body)
doc=Document(REF)
for e in list(doc.element.body):
    if e.tag!=qn('w:sectPr'):doc.element.body.remove(e)
doc.core_properties.title='Fatih Görev Kartı 4 Ekran Görüntülü Rapor'
tracking={'kept_exact':[],'adapted':[],'removed':[],'replaced_tables':[],'added_log_evidence':[]}

def add_el(el):
    doc.element.body.insert(len(doc.element.body)-1,el)
    return el

def clone_p(i,text=None):
    el=deepcopy(blocks[i]);p=Paragraph(el,doc)
    old=p.text
    if text is not None and text!=old:
        rpr=deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
        p.text=text
        if rpr is not None:
            run=p.runs[0]._r
            if run.rPr is not None:run.remove(run.rPr)
            run.insert(0,rpr)
        tracking['adapted'].append({'block':i,'before':old,'after':text})
    elif old:tracking['kept_exact'].append({'block':i,'text':old})
    if p.style.name=='Kayıt Alıntısı':p.paragraph_format.keep_together=True
    return Paragraph(add_el(el),doc)

def para(text,bold=False,after=6,keep=False,style='Normal'):
    p=doc.add_paragraph(style=style)
    p.paragraph_format.space_before=Pt(0);p.paragraph_format.space_after=Pt(after)
    p.paragraph_format.line_spacing=1.0;p.paragraph_format.first_line_indent=Inches(0)
    p.paragraph_format.keep_with_next=keep
    run=p.add_run(text);run.font.name='Times New Roman';run.font.size=Pt(12)
    run.font.bold=bold;run.font.color.rgb=RGBColor(0,0,0)
    return p

def code(text):
    p=doc.add_paragraph(style='Kayıt Alıntısı')
    p.paragraph_format.space_after=Pt(5);p.paragraph_format.space_before=Pt(0)
    p.add_run(text)
    return p

def photo(key,keep=False):
    r=next(x for x in records if x['key']==key)
    file=Path(r['stored_original'])
    assert hashlib.sha256(file.read_bytes()).hexdigest()==r['sha256']
    w,h=r['size_px'];x0,y0,x1,y1=r['crop_px']
    width=Inches(6.5);height=round(width*(y1-y0)/(x1-x0))
    p=doc.add_paragraph()
    p.alignment=WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before=Pt(0);p.paragraph_format.space_after=Pt(7)
    p.paragraph_format.first_line_indent=Inches(0);p.paragraph_format.line_spacing=1
    p.paragraph_format.keep_with_next=keep
    shape=p.add_run().add_picture(str(file),width=width,height=height)
    rect=OxmlElement('a:srcRect')
    values={'l':round(x0/w*100000),'t':round(y0/h*100000),'r':round((w-x1)/w*100000),'b':round((h-y1)/h*100000)}
    for k,v in values.items():rect.set(k,str(v))
    shape._inline.graphic.graphicData.pic.blipFill.insert(1,rect)
    shape._inline.docPr.set('descr',key+' gerçek terminal sonucu; kaynak pikseller değiştirilmedi')
    r['crop_ooxml']=values;r['display_emu']=[int(width),int(height)]

def rows(i):return [[c.text for c in row.cells] for row in Table(blocks[i],source).rows]

removed={28,29,35,36,37,38,39,40}
edits={
47:'Aşağıda yalnız koşulu değiştiren PRS parametreleri gösterildi. K0 PRS’siz referanstır. Bütün etkin PRS koşullarında tekrar ve gap değeri 1 uygulandı. Sembol ve slot ofsetleri sıfırdan başlayan indislerdir.',
56:'K0 için üç 100 MHz referansının ortalaması alındı. Diğer koşullar gnb_compat ile ölçüldü. Kaynak model, Excel’in öngörüsüdür; ölçülen DL kaybı 36 Mbps referansa göre ayrıca hesaplandı. Model ve ölçüm aynı değer olarak sunulmadı.',
60:'K1 için kaynak model yüzde 16,7 kayıp öngördü; ölçülen 29 Mbps, 36 Mbps referansa göre yüzde 19,4 kayıp verdi. Fark, kaynak modelin TDD takvimi ve gerçek scheduler tahsisleriyle aynı hesap olmamasını gösterir. K11’in kaynak formül önbelleği boş olduğundan bu koşul için model değeri verilmedi.',
70:'Debug kaydındaki baskın çıkarılan veri RE sayıları: K1 432; K6 1296; K7 864; K8 432; K11 384. Daha dar tahsislerde daha küçük giderler de görüldü. Bu değerler ham PRS RE hesabından farklıdır; PDSCH sembol aralığı ve DMRS veri dışı maskesi hesaba katıldı. İlk seçilen on koşunun tamamında nrtx=0 doğrulandı.',
72:'Deneme yalnız yeni PDSCH iletim yolunu kapsadı. HARQ yeniden iletiminde eski TBS korunur; PDSCH repetition, SIB1, paging, RAR ve fallback yolları için ortak güvenli eşleme geliştirilmedi. İlk beş model koşusunun her birinde hata satırı 0, SIB1 içeren satır 2 ve late satırı 5’ti; DL ve UL NOK 0’dı. SIB1 içeren satır sayısı hata sayısıyla eş tutulmadı.',
75:'Kayıt: Kod_Degisiklikleri/03_tum_deney_degisiklikleri.patch uygulanmış son haldir; 02_prs_re_tbs_modeli.patch model tasarımıdır. Son_Kaynaklar ile ilk oncesi ve sonrasi koşuları saklandı.',
90:'Derleme',
92:'Derleme 0 çıkış koduyla tamamlandı. Ayrı saat koruması, uyumluluk ve PRS modeli derleme günlükleri Derleme_Kayitlari altında korundu.',
}

for i,el in enumerate(blocks):
    if el.tag==qn('w:sectPr'):continue
    if i in removed:
        tracking['removed'].append({'block':i,'text':Paragraph(el,source).text})
        continue
    if el.tag==qn('w:p'):
        clone_p(i,edits.get(i))
        if i==15:
            para('100 MHz koşusunda kaydedilen uyarı satırı',bold=True,after=4,keep=True)
            warning=next(line for line in (ROOT/'Ham_Kayitlar/b100_r2/warning_excerpt.txt').read_text(encoding='utf-8').splitlines() if 'Received late DL_TTI.request' in line)
            code(warning);tracking['added_log_evidence'].append({'source':'Ham_Kayitlar/b100_r2/warning_excerpt.txt','text':warning})
            para('40 MHz koşusunda kaydedilen hata satırları',bold=True,after=4,keep=True)
            log=(ROOT/'Ham_Kayitlar/band40/terminal.txt').read_text(encoding='utf-8')
            literals=[x for x in log.splitlines() if 'std::system_error' in x or 'what():  cannot write to file:' in x]
            assert len(literals)==2
            for line in literals:code(line)
        if i==75:
            para('K6 için önce ve sonra terminal çıktıları',bold=True,after=5,keep=True)
            photo('k6_before',keep=True)
            para('K6 RE/TBS modeli sonrası',bold=True,after=5,keep=True)
            photo('k6_after')
            para('K6’da DL 29 Mbps’den 34 Mbps’ye çıktı; UL 119 Mbps kaldı. DL ok 1000’den 1200’e yükseldi. Görüntüler aynı ayarlarla yapılan ayrı K6 koşularına aittir.')
        continue
    if el.tag!=qn('w:tbl'):continue
    data=rows(i);tracking['replaced_tables'].append({'block':i,'header':data[0],'rows':len(data)-1})
    if i==5:
        for row in data[1:]:para(row[0]+': '+row[1]+'.',after=4)
    elif i==13:
        for r in data[1:]:
            para(f'{r[0]}: metrik satırı {r[1]}; CPU ortalama / en çok %{r[2]}; günlük {r[3]} MB; uyarı {r[4]}; çıkış kodu {r[5]}.',after=4)
    elif i==25:
        for row in data[1:]:para(row[0]+': '+row[1]+'.',after=5)
    elif i==33:
        para('PRS’siz referansın terminal çıktısı',bold=True,after=4,keep=True)
        photo('ref')
        para('Üç 100 MHz referansında DL 36 / UL 119 Mbps ve DL/UL ok 1200/600 bulundu. CPU ortalamaları sırasıyla %60,8, %63,2 ve %65,3 oldu.')
        para('40/60/80/100 MHz için DL 36 Mbps; UL sırasıyla 44,9/69,5/94,6/119 Mbps bulundu. Her bantta DL/UL ok 1200/600 oldu; CPU ortalamaları sırasıyla %52,0/%52,6/%53,7/%56,9 kaydedildi.')
        para('Kayıt: Ham_Kayitlar/ss_ref_referans_20261120T142925_245969; ilk referanslar ref100_1–3 ve bant koşuları duzeltilmis40–100.')
    elif i==48:
        for r in data[1:]:
            if r[0]=='K0':para('K0: PRS yok.',after=4);continue
            para(f'{r[0]}: periyot {r[1]} slot, {r[2]} sembol, comb {r[3]}, {r[4]} PRB, sembol ofseti {r[5]}, slot ofseti {r[6]}.',after=4)
    elif i==57:
        para('K0: DL 36 / UL 119 Mbps; DL/UL ok 1200/600. K2: DL 32 / UL 119 Mbps; ok 1100/600. K3: DL 34 / UL 119 Mbps; ok 1150/600. K5: DL 32 / UL 119 Mbps; ok 1200/600.')
        para('K1, K4, K6, K7, K8, K9, K10 ve K11: DL 29 / UL 119 Mbps; DL/UL ok 1000/600.')
        para('Kaynak model kaybı K1/K4/K6–K10’da %16,7; K2/K5’te %8,3; K3’te %4,2’dir. Ölçülen DL kaybı K1/K4/K6–K11’de %19,4; K2/K5’te %11,1; K3’te %5,6 bulundu. K0’da iki kayıp da %0’dır.')
        para('K1 koşulunun terminal çıktısı',bold=True,after=4,keep=True)
        photo('k1_before')
    elif i==68:
        para('DL önce / sonra değerleri K1: 29 / 35; K6: 29 / 34; K7: 29 / 35; K8: 29 / 35; K11: 29 / 35 Mbps bulundu. DL farkı sırasıyla 6/5/6/6/6 Mbps oldu. Bütün seçili koşullarda UL önce ve sonra 119 Mbps, DL ok önce / sonra 1000/1200 bulundu.')
        para('K1 RE/TBS modeli sonrası terminal çıktısı',bold=True,after=4,keep=True)
        photo('k1_after')
    else:raise RuntimeError('Unmapped table '+str(i))

doc.save(OUT)
visible='\n'.join(p.text for p in doc.paragraphs)
for term in ['Kontrollü saat regresyonu','23 koşu','35,983','113 metrik','ARSIV OZETI','Doğrulama özeti','yeniden doğrulama']:
    assert term not in visible,term
assert len(doc.inline_shapes)==5 and len(doc.tables)==0
with ZipFile(REF) as a,ZipFile(OUT) as b:
    preserve=[n for n in a.namelist() if n.startswith(('word/styles','word/numbering','word/theme','customXml/','word/header','word/footer','docProps/custom'))]
    assert all(a.read(n)==b.read(n) for n in preserve)
for sh,r in zip(doc.inline_shapes,[next(x for x in records if x['key']==k) for k in ['ref','k1_before','k1_after','k6_before','k6_after']]):
    embed=sh._inline.graphic.graphicData.pic.blipFill.blip.embed
    assert hashlib.sha256(doc.part.related_parts[embed].blob).hexdigest()==r['sha256']
assert hashlib.sha256(REF.read_bytes()).hexdigest()==REF_SHA
tracking.update({'source':str(REF),'source_sha256':REF_SHA,'output':str(OUT),'screenshots':5,'archive_screenshot_removed':True,'source_report_unchanged':True,'tables_converted_without_losing_values':True})
(QA/'prose_preservation.json').write_text(json.dumps(tracking,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'Araclar/SS_Rapor_QA/crop_and_package_check.json').write_text(json.dumps({'reference':str(REF),'reference_sha256':REF_SHA,'output':str(OUT),'images':records,'pixel_data_changed':False,'source_geometry_and_preserve_only_parts_match':True,'inline_images':5,'tables':0},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'docx':str(OUT),'original_paragraphs_exact':len(tracking['kept_exact']),'paragraphs_adapted':len(tracking['adapted']),'verification_and_plain_quotes_removed':len(tracking['removed']),'images':5,'source_unchanged':True},ensure_ascii=False))

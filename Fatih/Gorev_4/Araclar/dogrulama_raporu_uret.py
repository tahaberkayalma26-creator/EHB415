"""İlk kayıtların bağımsız denetimini ve yeni koşuları birlikte belgeler."""
from pathlib import Path
from xml.sax.saxutils import escape
from statistics import mean
import json, sys, csv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'Dogrulama/yeniden_kosu_sonuclari.json').read_text(encoding='utf-8'))
assert DATA['completed']==DATA['total']==23
rows=DATA['results'];by={r['old_tag']:r for r in rows}
assert all(r['measurement_valid'] and r['accepted'] and r['exit']==0 for r in rows)
raw=json.loads((ROOT/'Araclar/Dogrulama_QA/raw_audit_original.json').read_text(encoding='utf-8'))
newraw=json.loads((ROOT/'Araclar/Dogrulama_QA/raw_audit_v2.json').read_text(encoding='utf-8'))
assert not raw['integrity_issues'] and not newraw['integrity_issues']
width=json.loads((ROOT/'Dogrulama/pdsch_genislik_ve_model_kontrolu.json').read_text(encoding='utf-8'))
assert width['all_expected_re_tbs_observed']
assert width['pdsch_width']['dominant_range']=='[0..48)'
assert width['pdsch_width']['baseline_tbs_3969_observed'] and width['pdsch_width']['non_interleaved_only']
pdfmetrics.registerFont(TTFont('TimesTR','C:/Windows/Fonts/times.ttf'))
pdfmetrics.registerFont(TTFont('TimesTR-Bold','C:/Windows/Fonts/timesbd.ttf'))
pdfmetrics.registerFontFamily('TimesTR',normal='TimesTR',bold='TimesTR-Bold')
body=ParagraphStyle('body',fontName='TimesTR',fontSize=11,leading=14,spaceAfter=8)
head=ParagraphStyle('head',parent=body,fontName='TimesTR-Bold',fontSize=12,leading=15,spaceAfter=10)
small=ParagraphStyle('small',parent=body,fontSize=9.5,leading=12,spaceAfter=7)
cell=ParagraphStyle('cell',parent=body,fontSize=9.5,leading=11.5,spaceAfter=0)
story=[]
def p(t,style=body):story.append(Paragraph(t,style))
def h(t):p(t,head)
def n(v):return f'{v:.3f}'.rstrip('0').rstrip('.').replace('.',',')
def pair(r,stage):
 d=r[stage+'_values'];return n(d['dl_mbps_mean'])+' / '+n(d['ul_mbps_mean'])
def table(data,widths):
 t=Table([[Paragraph(escape(str(c)),cell) for c in row] for row in data],colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.black),('LINEBELOW',(0,-1),(-1,-1),.4,colors.black),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3)]))
 story.extend([t,Spacer(1,9)])
dl_delta=max(abs(r['delta']['dl_mbps_mean']) for r in rows)
ul_delta=max(abs(r['delta']['ul_mbps_mean']) for r in rows)
max_relative=max(abs(r['delta'][k])/r['old_values'][k]*100 for r in rows for k in ['dl_mbps_mean','ul_mbps_mean'])
same_rates=sum(all(r['delta'][k]==0 for k in ['dl_mbps_mean','ul_mbps_mean']) for r in rows)
same_all=sum(r['console_values_identical'] for r in rows)

h('1. Kayıtların doğruluğu ve yeniden ölçüm')
p('İlk raporda kullanılan 23 koşu, terminal satırlarından bağımsız bir okuyucuyla yeniden hesaplandı. '
  'İlk koşulardaki 509 ve yeni koşulardaki 506 metrik satırı kontrol edildi. DL/UL başlıkları esas alınarak CSV değerleri ve ilk/son satır dışlama kuralı doğrulandı. '
  'Excel, Word ve PDF’deki ölçülmüş hızlar ile başarılı taşıma bloğu değerlerinde hesap veya aktarım hatası bulunmadı. '
  'CPU örnekleri ve gerçek PRS ayarları da kayıtlarla eşleşti.')
p('Ardından aynı dondurulmuş OCUDU ikilileriyle 23 yeni koşu yapıldı: üç referans, dört bant genişliği, '
  'K1-K11 ve beş RE/TBS karşılaştırması. İkili SHA-256 değerleri kontrol edildi; sentetik saat yardımcısı kullanılmadı. '
  'Kayıtlar v2_ etiketleriyle saklandı, önceki ölçümler silinmedi.')
p(f'Yeni 23 koşunun tamamı kabul edildi ve sıfır çıkış koduyla sonlandı. Hız çiftleri {same_rates}/23 koşuda, '
  f'hız/ok/nok alanlarının tamamı {same_all}/23 koşuda aynı çıktı. En büyük DL farkı {n(dl_delta)} Mbps, '
  f'UL farkı {n(ul_delta)} Mbps; en büyük göreli hız farkı %{n(max_relative)} oldu. '
  'Fark görülen satırlar ortalamadan seçilerek çıkarılmadı.')
table([['PRS’siz 100 MHz','İlk DL / UL','Tekrar DL / UL'],
       *[[f'Referans {i}',pair(by['ref100_'+str(i)],'old'),pair(by['ref100_'+str(i)],'new')] for i in (1,2,3)],
       ['Üç koşu ortalaması','36 / 119',n(mean(by['ref100_'+str(i)]['new_values']['dl_mbps_mean'] for i in (1,2,3)))+' / '+n(mean(by['ref100_'+str(i)]['new_values']['ul_mbps_mean'] for i in (1,2,3)))]],[162,153,153])
table([['Bant','İlk DL / UL','Tekrar DL / UL'],
       *[[f'{b} MHz',pair(by['duzeltilmis'+str(b)],'old'),pair(by['duzeltilmis'+str(b)],'new')] for b in (40,60,80,100)]],[162,153,153])
p('Tablolarda hız birimi Mbps’dir. Ondalıklı tekrar değerleri, konsolda yuvarlatılmış dönem satırlarının aritmetik ortalamasıdır; '
  'bu basamaklar fiziksel ölçüm hassasiyeti anlamına gelmez. İlk 36 Mbps gibi değerler kaydedildikleri koşular için doğrudur; '
  'her yeni çalıştırmada noktasına kadar sabit kalacak donanım özellikleri değildir.',small)
p('Küçük değişim görülen koşularda FAPI “Real-time failure”/“late” ve bazı koşularda geri saat koruması kayıtları vardı. '
  'Bu, WSL test ortamındaki zamanlama değişkenliğiyle uyumludur; her tek hız farkının yalnız bir uyarıdan kaynaklandığı kanıtlanmadı. '
  'Saat koruma uyarısının tekrarı ayrı saat sıçramaları sayılmadı.',small)

story.append(PageBreak())
h('2. K1 ile K11 sonuçlarının yeniden kontrolü')
p('Aşağıdaki ilk değerler ana rapordan, tekrar değerleri yeni koşulardan alındı. '
  'DL ok, HARQ ACK sayısı; UL ok, başarılı CRC sayısıdır. Bunlar uygulama paket sayısı değildir. '
  'Bütün değerler aynı satır ortalama kuralıyla hesaplandı.')
table([['Koşul','İlk DL / UL','Tekrar DL / UL','Tekrar DL ok','Tekrar UL ok'],
       *[[f'K{i}',pair(by[f'oncesi_K{i}'],'old'),pair(by[f'oncesi_K{i}'],'new'),n(by[f'oncesi_K{i}']['new_values']['dl_ok_mean']),n(by[f'oncesi_K{i}']['new_values']['ul_ok_mean'])] for i in range(1,12)]],[42,116,126,92,92])
for k in ['K1','K9','K10']:
 r=by['oncesi_'+k]
 p(f'{k}: tekrar UL {n(r["new_values"]["ul_mbps_mean"])} Mbps; “No space in PDCCH” sayısı '
   f'{r["log_counts"].get("pusch_no_pdcch",0)}.',small)
p('Kabul edilen bazı koşularda SIB1 kaynak ayırma hataları görüldü. Yapılandırmanın kabul edilmesi, '
  'günlüklerin hatasız olduğu anlamına gelmez. İlk rapordaki SIB1 sayıları ilk koşulara aittir; '
  'yeni günlüklerdeki hata/uyarı sayıları ayrıca saklandı.')
p('K11’deki teorik hücre farkı ölçüm hatası değildir: kaynak Excel formülünün önbelleği boş olduğu için Word’de '
  'teorik model “-” gösterilmişti; üretilen sonuç Excel’i aynı formülü yeniden hesaplayıp %16,67 gösterir. '
  'K11’in ilk ölçülmüş 29 / 119 Mbps değeri bütün teslim dosyalarında aynıdır. '
  'Teorik kayıp ile ölçülmüş hız kaybı ayrı değerlendirilmelidir.')
p('Kaynaklar: Araclar/Dogrulama_QA/raw_audit_original.json ve raw_audit_v2.json; '
  'Dogrulama/yeniden_kosu_sonuclari.json; Ham_Kayitlar/v2_oncesi_K1-K11 klasörleri.',small)

story.append(PageBreak())
h('3. Kod deneyi ve bağımsız hesap kontrolü')
selected=['K1','K6','K7','K8','K11']
table([['Koşul','Tekrar önce DL','Tekrar sonra DL','Sonra UL','Çıkarılan veri RE','PRS slotu TBS byte'],
       *[[k,n(by['oncesi_'+k]['new_values']['dl_mbps_mean']),n(by['sonrasi_'+k]['new_values']['dl_mbps_mean']),n(by['sonrasi_'+k]['new_values']['ul_mbps_mean']),re,tbs] for k,re,tbs in zip(selected,[432,1296,864,432,384],[3713,3072,3393,3713,3713])]],
      [38,80,80,65,99,106])
p('Günlükte tam 48 PRB PDSCH tahsisi [1..14) sembollerini, DMRS ise 2, 7 ve 11. sembolleri kullanıyor. '
  'DMRS type 1 ve iki veri dışı CDM grubu nedeniyle her DMRS sembolünde 12 RE veri dışıdır. '
  'PRS’siz veri RE bütçesi 48 × (13 - 3) × 12 = 5760 olarak bağımsız hesaplandı.')
p('DMRS dışındaki PRS sembolleri K1/K6/K7/K8/K11 için 3/9/3/9/4; her PRB ve semboldeki PRS RE sayısı '
  '12/comb’dur. Böylece sırasıyla 432/1296/864/432/384 veri RE çıkarılır. '
  'MCS 28, 64QAM, tek katman ve TS 38.214 TBS formülü kullanılarak OCUDU hesaplayıcısı çağrılmadan '
  '3969 byte referans ve tabloda verilen PRS slotu TBS değerleri yeniden üretildi; ilk gerçek günlüklerle eşleşti.')
p('Yeni PDSCH genişliği kontrolünde baskın aralık '+escape(str(width['pdsch_width']['dominant_range']))+
  ' bulundu. Böylece 48 PRB veri genişliği de tekrar kontrol edildi. '
  'Model tahsislerinin yeni RE/TBS/nrtx kontrolü Dogrulama/pdsch_genislik_ve_model_kontrolu.json içinde saklandı.',small)
if width['all_selected_repeats_no_retx']:
 p('Seçili on tekrar günlüğünde nrtx=0 doğrulandı. RE izi ile beklenen TBS değerinin günlükte bulunması ayrı ayrı kontrol edildi; bütün tahsisler slot bazında eşleştirilmedi.',small)
else:
 p('Seçili on tekrar günlüğünün altısında bazı tahsisler için nrtx &gt; 0 (yeniden iletim) bulundu. Bu koşuların hızları metrik tekrarıdır; yeniden iletimsiz ideal RE kazancının doğrudan ölçümü sayılmadı. İlk raporun yeniden iletimsiz koşularına ait kanıtlar ayrıca korunmuştur.',small)
p('Bu doğrulama, kayıtlardaki MAC test modu değerlerini ve deneysel RE/TBS aritmetiğini doğrular. '
  'Test UE, ACK/CRC geri bildirimlerini büyük ölçüde başarılıya zorlar; sıfır NOK gerçek RF başarısının kanıtı değildir. '
  'PRS için PHY rate matching ve gerçek UE bildirimi eklenmediği için gerçek telefonla hız kazanımı veya standart uyumu sonucu çıkarılamaz.')
p('Ekran görüntülü ikinci rapor için Araclar/OCUDU_SS_icin_Ac.cmd hazırlandı. Menü 1-5 gerçek yeni koşular başlatır '
  've o koşunun terminal satırlarını ekranda bekletir. Menü 12, bu 23 doğrulamanın kaydedilmiş özetini terminalde gösterir; '
  'yeni gNB çalıştırmaz. Ekran görüntüleri geldikten sonra ayrı rapora eklenebilir; tablolu rapor korunmuştur.',small)
p('Kanıtlar: Araclar/Dogrulama_QA/source_audit.md ve independent_re_tbs.json; '
  'Ham_Kayitlar/v2_sonrasi_*; Ekran_Goruntusu_Alma.txt.',small)

OUT=ROOT/'Fatih_Gorev_Karti_4_Dogrulama_Raporu.pdf'
SimpleDocTemplate(str(OUT),pagesize=(612,792),leftMargin=72,rightMargin=72,topMargin=54,bottomMargin=54,
                  title='Görev Kartı 4 Sonuç Doğrulama',author='Fatih').build(story)
print(OUT)

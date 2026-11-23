"""Görev kartı 4 için kayıtlı ölçümlerden kısa teslim PDF'si."""
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding="utf-8")
import json
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Fatih_Gorev_Karti_4_Teslim_Ozeti.pdf'
pdfmetrics.registerFont(TTFont('TimesTR', 'C:/Windows/Fonts/times.ttf'))
pdfmetrics.registerFont(TTFont('TimesTR-Bold', 'C:/Windows/Fonts/timesbd.ttf'))
pdfmetrics.registerFont(TTFont('ConsolaTR', 'C:/Windows/Fonts/consola.ttf'))
pdfmetrics.registerFontFamily('TimesTR', normal='TimesTR', bold='TimesTR-Bold')
normal = ParagraphStyle('normal', fontName='TimesTR', fontSize=11, leading=14, spaceAfter=7)
head = ParagraphStyle('head', parent=normal, fontName='TimesTR-Bold', fontSize=12, leading=15, spaceBefore=0, spaceAfter=10)
small = ParagraphStyle('small', parent=normal, fontSize=9.5, leading=12, spaceAfter=6)
cell = ParagraphStyle('cell', parent=normal, fontSize=9.2, leading=11, spaceAfter=0)
code = ParagraphStyle('code', fontName='ConsolaTR', fontSize=8.1, leading=10.3, spaceAfter=7, wordWrap='CJK')
story = []
def P(t, style=normal):
    story.append(Paragraph(t, style))
def H(t):
    P(t, head)
def T(rows, widths, fs=9.2):
    data = [[Paragraph(escape(str(x)), cell) for x in row] for row in rows]
    tab = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    tab.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LINEBELOW',(0,0),(-1,0),0.6,colors.black),
        ('LINEBELOW',(0,-1),(-1,-1),0.4,colors.black),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3)
    ]))
    story.extend([tab, Spacer(1,9)])
def get(tag):
    return json.loads((ROOT/'Ham_Kayitlar'/tag/'summary.json').read_text(encoding='utf-8'))
def num(x, places=1):
    return f'{x:.{places}f}'.rstrip('0').rstrip('.').replace('.',',')
def metric(d,k):
    return num(d[k+'_mean'])
configs = json.loads((ROOT/'Araclar/prs_kosullari.json').read_text(encoding='utf-8'))['konfigurasyonlar']
cfgs = {d['etiket']:d for d in configs}
refs = [get('ref100_'+str(i)) for i in (1,2,3)]
assert all(d['measurement_valid'] and d['dl_mbps_mean']==36 and d['ul_mbps_mean']==119 for d in refs)
before = {f'K{i}':get(f'oncesi_K{i}') for i in range(1,12)}
selected = ['K1','K6','K7','K8','K11']
after = {k:get('sonrasi_'+k) for k in selected}
assert all(d['measurement_valid'] for d in list(before.values())+list(after.values()))

H('1. Ortak ızgara ve 100 MHz kontrolü')
P('OCUDU 26.10.0 (e0db566), Ubuntu 24.04/WSL üzerinde dummy RU ve test UE ile çalıştırıldı. '
  'Ortak ayarlar n78, yaklaşık 3,5 GHz, 30 kHz SCS ve TDD olarak kullanıldı. '
  '100 MHz için 273 PRB içeren ızgara seçildi. Gerçek anten, telefon veya çekirdek şebeke ile uçtan uca test yapılmadı.')
P('İlk yazılımda bazı koşularda sıfır hız ve yoğun zamanlama uyarıları görüldü. '
  'Günlüklerde yaklaşık 2,2-2,46 saniyelik saat geri sıçraması ve dummy slot sayacının çok büyük bir ileri tur yaptığı bulundu. '
  'Ayrı kod dalında geri slot okumasını engelleyen koruma eklendi. '
  'Saat kararsızlığının WSL altındaki kesin kaynağı belirlenemedi.')
P('Saat koruması tek başına 100 MHz sıfır hızını çözmedi. Kaynak incelemesinde ConRes onayı sonrasında fallback durumundan çıkan UE için '
  'slice scheduler bildiriminin eksik kalabildiği görüldü. Geçişe bağlı config_applied bildirimi eklendikten sonra aynı 100 MHz ayarıyla '
  'üç referans koşusunda düzenli veri akışı elde edildi. Aşağıdaki ana ölçümlerde bu iki düzeltmeyi içeren gnb_compat kullanıldı.')
T([['Bant (MHz)','DL (Mbps)','UL (Mbps)','Sonuç'],
   *[[b,metric(get('duzeltilmis'+str(b)),'dl_mbps'),metric(get('duzeltilmis'+str(b)),'ul_mbps'),'Veri akışı var'] for b in (40,60,80,100)]], [75,100,100,193])
P('Düzeltilmiş sürümle 40-100 MHz aralığında veri akışının durduğu bir bant görülmedi. '
  'İlk kararsız koşuların satır ortalamaları referans hız olarak kullanılmadı. İşlemci kullanımı top ile kaydedildi; '
  'üç 100 MHz referansında ortalamalar %60,78, %63,25 ve %65,29 oldu. Bu gösterimde %100 bir sanal işlemci çekirdeğine karşılık gelir.', small)
T([['PRS’siz 100 MHz','DL (Mbps)','UL (Mbps)','DL ok / UL ok'],
   *[[f'Koşu {i}',metric(d,'dl_mbps'),metric(d,'ul_mbps'),f"{metric(d,'dl_ok')} / {metric(d,'ul_ok')}"] for i,d in enumerate(refs,1)],
   ['Üç koşunun ortalaması','36','119','1200 / 600']], [168,85,85,130])
P('PDSCH günlüğünde en sık rb=[0..48) aralığı 10.637 kez görüldü. Bu aralık 0-47 numaralı 48 PRB anlamına gelir; '
  'bazı tahsisler daha dardır. Bu nedenle 273 PRB’lik taşıyıcının tamamı kullanıcı DL verisine ayrılmış kabul edilmedi. '
  'PDSCH için baskın veri genişliği 48 PRB olarak Excel’e işlendi.')
P('Kanıtlar: Ham_Kayitlar/ref100_1, ref100_2, ref100_3; duzeltilmis40/60/80/100; veri_genisligi100. '
  'İlk tanı, hata satırları ve kod gerekçeleri 100MHz_Sorun_Analizi.md ile ayrıntılı Word raporunda verildi.', small)

story.append(PageBreak())
H('2. PRS koşulları ve ölçülen sonuçlar')
P('K0 PRS’siz referanstır. K1-K11, aynı 100 MHz ızgarada gnb_compat ile ölçüldü. '
  'Tablodaki değerler terminalde raporlanan hız ve başarılı taşıma bloğu sayaçlarının kullanılan aralık içindeki ortalamalarıdır. '
  'Tüm koşullarda yapılandırma kabul edildi ve gNB sıfır çıkış koduyla sonlandı.')
rows=[['Koşul','Per.','Semb.','Comb','BW','Ofs.','DL','UL','DL ok','UL ok','Karar'],
      ['K0','-','-','-','-','-','36','119','1200','600','Kabul']]
for k,d in before.items():
    c=cfgs[k]
    rows.append([k,c['periyot_slot'],c['sembol'],c['comb'],c['bw_prb'],c['sembol_ofset'],metric(d,'dl_mbps'),metric(d,'ul_mbps'),metric(d,'dl_ok'),metric(d,'ul_ok'),'Kabul'])
T(rows,[32,30,34,33,34,32,42,42,46,46,47])
P('Per.: PRS periyodu (slot); Semb.: PRS sembol sayısı; BW: PRS genişliği (PRB); Ofs.: sembol başlangıç ofseti. '
  'DL ve UL birimi Mbps’dir. PRS slot ofseti 1, tekrar ve boşluk parametreleri 1/1 kullanıldı. '
  'K0 satırı üç referansın ortalamasıdır.',small)
P('K1, K9 ve K10 için “Failed to allocate PUSCH. Cause: No space in PDCCH.” satır sayısı ayrı ayrı 0 bulundu. '
  'Bu koşullarda UL, PRS’siz referanstaki 119 Mbps değerinde kaldı. Önceki görevdeki farklı FDD ayarlarında görülen UL düşüşü bu TDD ölçümünde tekrarlanmadı.')
P('K1 ile K4 aynı DL hızını verdi: PRS genişliği 48’den 272 PRB’ye çıkarılsa da kullanıcı PDSCH’si çoğunlukla ilk 48 PRB içindedir. '
  'K5’te PRS genişliği 24 PRB’ye düşürüldüğünde DL 32 Mbps oldu. K2 ve K3’te daha seyrek PRS kullanımıyla DL sırasıyla 32 ve 34 Mbps’ye çıktı.')
P('36 Mbps referansa göre terminaldeki yuvarlatılmış değerlerden hesaplanan DL kaybı; 29 Mbps için %19,4, '
  '32 Mbps için %11,1, 34 Mbps için %5,6’dır. Excel’deki önceden verilmiş teorik kayıp sütunu ölçüm olarak kullanılmadı.')
P('Kabul sonucu, günlüğün hatasız olduğu anlamına gelmez. Örneğin K1/K9/K10 günlüklerinde sırasıyla 1.584/1.593/531 hata satırı bulundu; '
  'bunlar SIB1 kaynak ayırma hatalarıyla ilişkilidir. Ölçülen nok/ok değerleri ile günlük hataları ayrı kaydedildi. '
  'Tam günlükler ve tüm metrik satırları korunmuştur.')
P('K11 kullanıcının ilk Excel dosyasında bulunmadığından güncel proje deposundaki PRS konfigürasyonları!A13:H13 satırından alındı '
  '(commit 4c31d938648abb355e0befdd8221ae0d5cdfbbbb). Diğer koşullar özgün dosyadan alındı; kaynak farkı sonuç Excel’inde belirtildi.',small)

story.append(PageBreak())
H('3. PRS boşluklarını kullanma deneyi ve standart cevabı')
P('Asıl kurulum korunarak fatih/gorev4-clockguard dalında çalışıldı. Özgün prs_scheduler.cpp:189-193 içindeki '
  'dl_res_grid.fill çağrısı kaldırıldı. PRS PDU listesi korundu; PDSCH ile örtüşen gerçek PRS veri RE’leri sayılarak '
  'TBS hesabından düşüldü. DMRS nedeniyle zaten veri taşımayan RE’ler ikinci kez düşülmedi.')
P('Özgün mcs_tbs_calculator.cpp:216-223 TBS hesaplayıcısına sembol sayısı, DMRS gideri, overhead ve PRB sayısını iletir. '
  'Asıl RE hesabı lib/ran/sch/tbs_calculator.cpp:109-110’dadır. Değiştirilmiş sürümde 111. satır PRS veri RE giderini çıkarır; '
  'MCS/TBS dosyasında 219-226 ve 266-273 aralıkları bu gideri iki TBS yoluna da iletir.',small)
P('N_RE,başlangıç = min(12 × N_sembol - N_DMRS/PRB - N_overhead/PRB, 156) × N_PRB<br/>'
  'N_RE,deney = max(N_RE,başlangıç - N_PRS,veri, 0)',code)
P('RE, bir alt taşıyıcı ile bir OFDM sembolünün kesişimindeki kaynak elemanıdır. TBS, gönderilecek taşıma bloğunun boyutudur. '
  'PRS maskeleri birleştirilip DMRS maskesi çıkarıldığı için aynı RE iki kez sayılmaz.',small)
T([['Koşul','Önce DL','Sonra DL','Sonra UL','48 PRB’de düşülen veri RE'],
   *[[k,metric(before[k],'dl_mbps'),metric(after[k],'dl_mbps'),metric(after[k],'ul_mbps'),v] for k,v in zip(selected,[432,1296,864,432,384])]],
  [46,74,74,74,200])
P('Hızların birimi Mbps’dir. Değişiklik sonrası beş koşulda DL ok 1200, UL ok 600 bulundu. '
  'Seçili önce/sonra günlüklerindeki PDSCH tahsislerinde nrtx=0 doğrulandı. '
  'Tablodaki RE sayıları yalnız tam 48 PRB tahsisleri içindir; daha dar tahsislerde değerler azalır.',small)
P('Bu sonuç dummy/test UE üzerindeki scheduler ve TBS deneyidir. PRS için PHY düzeyinde PDSCH rate matching, '
  'FAPI reserved-RE aktarımı ve gerçek UE bildirimi eklenmedi. PRS ile DMRS veya diğer sinyallerin fiziksel çakışmalarının çözüldüğü '
  'ya da gerçek telefonda aynı hızın elde edildiği gösterilmedi. TBS’nin küçültülmesi tek başına böyle bir kanıt oluşturmaz.')
P('Standart sorusunun cevabı',head)
P('Gerçek UE, gNB içindeki PRS RE maskesini kendiliğinden öğrenmez; TS 38.214 V18.2.0 §5.1.4-5.1.4.1 uyarınca '
  'RRC ile yapılandırılan rezervasyonları ve gerektiğinde DCI 1_1’in “Rate matching indicator” seçimini kullanarak PDSCH eşlemesini belirler. '
  'RateMatchPattern, PRS taşıyan RB/sembolleri korumaya elverişli olsa da PRS comb RE’lerini tek tek bildiren bir alan değildir; '
  'dolayısıyla PRS alım yapılandırması (§5.1.6.5) veya yalnız vericide RE çıkarılması, gerçek UE’nin aynı PDSCH boşluklarını uygulayacağını kanıtlamaz.')
P('Resmî kaynaklar: '
  '<link href="https://www.etsi.org/deliver/etsi_ts/138200_138299/138214/18.02.00_60/ts_138214v180200p.pdf">TS 38.214 V18.2.0</link>, '
  '<link href="https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/18.06.00_60/ts_138331v180600p.pdf">TS 38.331 V18.6.0 §6.3.2 (RateMatchPattern)</link>, '
  '<link href="https://www.etsi.org/deliver/etsi_ts/138200_138299/138212/18.02.00_60/ts_138212v180200p.pdf">TS 38.212 V18.2.0 §7.3.1.2.2</link>. '
  'İlgili standart PDF’leri, sayfa/bölüm kanıtları, kod yamaları ve derleme kayıtları klasörde saklandı.',small)

SimpleDocTemplate(str(OUT),pagesize=(612,792),leftMargin=72,rightMargin=72,topMargin=54,bottomMargin=54,
                  title='Fatih - Görev Kartı 4 Teslim Özeti',author='Fatih').build(story)
print(OUT)

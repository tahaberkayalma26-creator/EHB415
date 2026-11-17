"""PRS yerlesimini gorsel gosteren Excel: ogretici/veri/prs_gorsel.xlsx
Sayfalar: Nasil okunur | OCUDU varsayilani | Secici (acilir listeden konfig sec, izgaralar degisir) | Konfig listesi
Izgaralar kosullu bicimlendirme ile boyanir; sayilar hucrelerde yazmaz. Kosullu bicimlendirme Excel'de goruntulenerek dogrulanmadi (Excel bu ortamda acilamiyor).
Calistirma: python prs_gorsel_excel.py
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter as L

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "veri", "prs_gorsel.xlsx")
F = lambda c: PatternFill("solid", bgColor=c, fgColor=c)
RED, PINK, BLUE, GRAY, YEL, WHITE = "DC2626", "FECACA", "93C5FD", "E5E7EB", "FDE68A", "FFFFFF"
thin = Side(style="thin", color="D1D5DB"); BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
HDR = PatternFill("solid", fgColor="DBEAFE")

wb = Workbook(); wb.remove(wb.active)

# ------------------------------------------------------------ Konfig listesi
kl = wb.create_sheet("Konfig listesi")
kl.append(["id", "periyot (slot)", "sembol", "comb", "bw (PRB)", "sembol ofseti", "slot ofseti", "başlangıç PRB", "RE ofseti", "açıklama"])
KONF = [
    ["OCUDU varsayılan", 160, 2, 2, 272, 0, 0, 0, 0, "OCUDU'nun kendi varsayılanı (du_high_config.h). bw: hücre bandından türer, 4'ün katına aşağı yuvarlanır: 273 PRB → 272."],
    ["K0", 0, 0, 0, 0, 0, 0, 0, 0, "PRS yok"],
    ["K1", 10, 4, 4, 48, 2, 1, 0, 0, "Referans PRS (5 ms'de bir)"],
    ["K2", 20, 4, 4, 48, 2, 1, 0, 0, "Yalnız periyot: 10 ms"],
    ["K3", 40, 4, 4, 48, 2, 1, 0, 0, "Yalnız periyot: 20 ms"],
    ["K4", 10, 4, 4, 272, 2, 1, 0, 0, "Yalnız genişlik: tüm hücre"],
    ["K5", 10, 4, 4, 24, 2, 1, 0, 0, "Yalnız genişlik: yarım"],
    ["K6", 10, 12, 4, 48, 2, 1, 0, 0, "Yalnız sembol sayısı: 12"],
    ["K7", 10, 4, 2, 48, 2, 1, 0, 0, "Yalnız comb: 2"],
    ["K8", 10, 12, 12, 48, 2, 1, 0, 0, "Comb 12, 12 sembol"],
    ["K9", 10, 4, 4, 48, 0, 1, 0, 0, "Yalnız sembol ofseti: 0 (PDCCH ile çakışır)"],
    ["K10", 10, 4, 4, 48, 10, 1, 0, 0, "Yalnız sembol ofseti: 10"],
    ["K11", 10, 6, 6, 48, 2, 1, 0, 0, "Comb 6, 6 sembol"],
]
for r in KONF: kl.append(r)
for c in kl[1]: c.font = Font(bold=True); c.fill = HDR
for i, w in enumerate([18, 12, 9, 7, 9, 13, 11, 14, 10, 90], 1): kl.column_dimensions[L(i)].width = w
n_konf = len(KONF)

# ------------------------------------------------------------ Secici
s = wb.create_sheet("Seçici", 0)
s["A1"] = "PRS seçici: B2'deki listeden bir konfigürasyon seç, aşağıdaki ızgaralar değişir"; s["A1"].font = Font(bold=True, size=13)
s["A2"] = "Konfigürasyon"; s["B2"] = "K1"; s["B2"].fill = PatternFill("solid", fgColor="FEF9C3"); s["B2"].font = Font(bold=True)
dv = DataValidation(type="list", formula1=f"='Konfig listesi'!$A$2:$A${n_konf + 1}", allow_blank=False); s.add_data_validation(dv); dv.add("B2")
isimler = ["periyot (slot)", "sembol", "comb", "bw (PRB)", "sembol ofseti", "slot ofseti", "başlangıç PRB", "RE ofseti"]
for i, ad in enumerate(isimler):
    r = 4 + i
    s.cell(r, 1, ad)
    s.cell(r, 2, f"=INDEX('Konfig listesi'!${L(i + 2)}$2:${L(i + 2)}${n_konf + 1},MATCH($B$2,'Konfig listesi'!$A$2:$A${n_konf + 1},0))")
s["A12"] = "veri alanı genişliği (PRB)"; s["B12"] = 48; s["B12"].fill = PatternFill("solid", fgColor="FEF9C3")
s["C12"] = "ön değer (ölçüm); Fatih doğrulayınca değiştir"
s["A13"] = "DL slotu / 10 slot (TDD)"; s["B13"] = 6
bilgi = [
    ("PRS gönderim aralığı (ms)", '=IF(B4=0,"PRS yok",B4*0.5)', None),
    ("Veriden kapanan pay: şimdi (model)", "=IF(B4=0,0,(20/B4)/(B13*2)*MIN(B7,B12)/B12)", "0.0%"),
    ("PDCCH (sembol 0) ile çakışma", '=IF(AND(B4>0,B8=0),"VAR","yok")', None),
    ("Geçerli mi (sembol>=comb, katı)", '=IF(B4=0,"-",IF(AND(B5>=B6,MOD(B5,B6)=0),"evet","HAYIR: OCUDU reddeder"))', None),
    ("PRS slotunda kapanan: şimdi", "=IF(B4=0,0,1)", "0%"),
    ("PRS slotunda kapanan: RE düzeyi", "=IF(B4=0,0,B5/(13*B6))", "0.0%"),
    ("Toplam kapanan pay: RE düzeyi", "=IF(B4=0,0,P5*P9)", "0.0%"),
]
for i, (ad, fm, nf) in enumerate(bilgi):
    s.cell(4 + i, 4, ad).font = Font(bold=True)
    c = s.cell(4 + i, 16, fm)
    if nf: c.number_format = nf
    c.font = Font(bold=True)
s["D11"] = "RE düzeyi = PRS'in doldurmadığı kutular da veri için kullanılırsa (üst sınır; DMRS vb. sayılmadı)"; s["D11"].font = Font(italic=True, color="6B7280")

# yardimci: comb desenleri (R:AC)
s["R3"] = "yardımcı: comb deseni (OCUDU prs.cpp get_prs_freq_offset)"; s["R3"].font = Font(italic=True, color="6B7280")
pat = {2: [0, 1], 4: [0, 2, 1, 3], 6: [0, 3, 1, 4, 2, 5], 12: [0, 6, 3, 9, 1, 7, 4, 10, 2, 8, 5, 11]}
for i, (cb, p) in enumerate(pat.items()):
    r = 5 + i
    s.cell(r, 17, cb)
    for j, v in enumerate(p): s.cell(r, 18 + j, v)
for c in range(17, 30): s.cell(5, c).font = Font(color="6B7280"); s.cell(6, c).font = Font(color="6B7280"); s.cell(7, c).font = Font(color="6B7280"); s.cell(8, c).font = Font(color="6B7280")

# --- RE izgarasi: bir PRB (12 alt tasiyici) x 14 sembol
s["A15"] = "1) Bir PRB'nin içi (12 alt taşıyıcı × 14 sembol). Kırmızı = PRS'in gerçekten doldurduğu kutu, mavi = PDCCH sembolü"; s["A15"].font = Font(bold=True)
s["A16"] = "alt taşıyıcı ↓ / sembol →"
for sy in range(14):
    c = s.cell(16, 3 + sy, sy); c.alignment = Alignment(horizontal="center"); c.font = Font(color="6B7280")
for k in range(12):
    r = 17 + k
    s.cell(r, 2, 11 - k).font = Font(color="6B7280"); s.cell(r, 2).alignment = Alignment(horizontal="center")
    for sy in range(14):
        s.cell(r, 3 + sy).border = BORDER
rng = "C17:P28"
# PRS RE
f_re = ("AND($B$4>0,C$16>=$B$8,C$16<$B$8+$B$5,"
        "MOD($B17-$B$11-INDEX($R$5:$AC$8,MATCH($B$6,$Q$5:$Q$8,0),MOD(C$16-$B$8,$B$6)+1),$B$6)=0)")
s.conditional_formatting.add(rng, FormulaRule(formula=[f_re], fill=F(RED), stopIfTrue=True))
s.conditional_formatting.add(rng, FormulaRule(formula=["C$16=0"], fill=F(BLUE)))

# --- slot izgarasi: 40 slot x 23 PRB bandi (12 PRB)
s["A31"] = "2) Zamanda ve frekansta (40 slot = 20 ms, her satır 12 PRB). Kırmızı = PRS yüzünden veriye kapanan PRB'ler, yeşilimsi gri = veri alanı (kapanmamış)"
s["A31"].font = Font(bold=True)
s["A32"] = "PRB bandı ↓ / slot →"
NS, NB = 40, 23
for sl in range(NS):
    c = s.cell(32, 3 + sl, sl); c.alignment = Alignment(horizontal="center"); c.font = Font(size=8, color="6B7280")
    t = s.cell(33, 3 + sl, f'=IF(MOD({L(3 + sl)}$32,10)<6,"D",IF(MOD({L(3 + sl)}$32,10)=6,"S","U"))')
    t.alignment = Alignment(horizontal="center"); t.font = Font(size=8, color="6B7280"); t.border = BORDER
s["A33"] = "TDD (D indirme, S karışık, U yükleme)"
for b in range(NB):
    r = 34 + b
    s.cell(r, 1, f"PRB {12 * b}–{12 * b + 11}").font = Font(size=8, color="6B7280")
    s.cell(r, 2, 12 * b).font = Font(size=8, color="9CA3AF")
    for sl in range(NS):
        s.cell(r, 3 + sl).border = BORDER
        if 12 * b < 48: s.cell(r, 3 + sl).fill = F("D1FAE5")                      # veri alani (PRB < 48)
last = 34 + NB - 1
rng2 = f"C34:{L(2 + NS)}{last}"
f_sl = "AND($B$4>0,MOD(C$32-$B$9,$B$4)=0,$B34<$B$10+$B$7,$B34+12>$B$10)"
s.conditional_formatting.add(rng2, FormulaRule(formula=[f_sl], fill=F(RED)))
s.column_dimensions["A"].width = 34; s.column_dimensions["B"].width = 12
for sl in range(NS): s.column_dimensions[L(3 + sl)].width = 3.4
s.column_dimensions["D"].width = 3.4
s.freeze_panes = "C3"

# ------------------------------------------------------------ OCUDU varsayilani
v = wb.create_sheet("OCUDU varsayılanı", 0)
v["A1"] = "OCUDU'nun varsayılan PRS ayarı (du_high_config.h, du_high_unit_prs_resource_set_config)"; v["A1"].font = Font(bold=True, size=13)
v.append([]); v.append(["Ayar", "Varsayılan", "Anlamı", "Kaynak"])
for c in v[3]: c.font = Font(bold=True); c.fill = HDR
VAR = [
    ["PRS bloğu", "yok (kapalı)", "yapılandırma dosyasına 'prs:' yazılmazsa PRS gönderilmez. Bizim koşularda betik ekliyor.", "ocudu_prs_kos.sh"],
    ["periodicity_slots", 160, "PRS her 160 slotta bir. 30 kHz'te 160 slot = 80 ms.", "du_high_config.h"],
    ["slot_offset", 0, "Periyodun ilk slotu.", "du_high_config.h"],
    ["nof_symbols", 2, "Her gönderim 2 sembol.", "du_high_config.h"],
    ["comb_size", 2, "Her 2 alt taşıyıcıdan biri.", "du_high_config.h"],
    ["bandwidth_prbs", "ayarlanmazsa türetilir", "'hücre bandından türetilir, 4'ün katına aşağı yuvarlanır': 273 PRB → 272 PRB.", "du_high_config.h (kod yorumu)"],
    ["start_prb", 0, "PRB 0'dan başlar.", "du_high_config.h"],
    ["repetition_factor / time_gap", "1 / 1", "Tekrar yok.", "du_high_config.h"],
    ["sembol ofseti, RE ofseti (kaynak düzeyi)", "0 / 0", "Slotun ilk sembolünden başlar. (Bu kaynak ayarları örnek kodda 0.)", "du_high_config.h"],
    ["power_offset_db", 0, "", "du_high_config.h"],
]
for r in VAR: v.append(r)
for i, w in enumerate([38, 26, 80, 30], 1): v.column_dimensions[L(i)].width = w
v.append([]); v.append(["Ne anlama geliyor?"]); v.cell(v.max_row, 1).font = Font(bold=True)
v.append(["Varsayılan, PRS'i çok seyrek ve çok geniş yollar: 80 ms'de bir, 272 PRB. Veri alanı yalnız 48 PRB olduğu için o slotta veri tamamen kapanır; ama 160 slotta yalnız 1 slot, yani kayıp küçüktür."])
v.append(["Radar açısından 80 ms çok seyrek: hız ölçümü için kullanılmaz. Bunu K1–K3 ile karşılaştırmak için 'Seçici' sayfasında 'OCUDU varsayılan' ve K1'i sırayla seç."])
v.append(["Slot ofseti 0 olduğundan varsayılan PRS, slot 0'a (TDD'de DL slotu) düşer; sembol ofseti 0 olduğu için PDCCH'nin bulunduğu sembol 0 ile çakışır. Bu çakışmanın OCUDU'da UL'yi düşürdüğünü Fatih ölçtü (eski testte, ofset 0)."])

# ------------------------------------------------------------ Nasil okunur
n = wb.create_sheet("Nasıl okunur", 0)
for t in [["PRS görsel dosyası"],
          ["1. 'OCUDU varsayılanı': OCUDU'nun kendi PRS ayarı ve ne anlama geldiği."],
          ["2. 'Seçici': B2 hücresindeki listeden bir konfigürasyon seç (OCUDU varsayılan, K0–K10). Üç şey değişir:"],
          ["   a) Bir PRB'nin içi: PRS'in hangi kutulara yazdığı (comb deseni)."],
          ["   b) 40 slotluk zaman çizelgesi: PRS hangi slotlarda, hangi PRB bantlarında veriyi kapatıyor."],
          ["   c) Üstte: PRS aralığı (ms), veriden kapanan pay (şimdi ve RE düzeyinde), PDCCH çakışması, geçerlilik."],
          ["3. 'Konfig listesi': bütün ayarların tablosu. Yeni bir satır ekleyip listeye ekleyebilirsin (A sütunu isim)."],
          ["Renkler: kırmızı = PRS; mavi = PDCCH sembolü; yeşilimsi gri = veri alanı (48 PRB); sarı = yükleme slotu."],
          ["Durumlar: veri alanı genişliği (48) ön değerdir, Fatih'in ölçümüyle doğrulanacak. 'Veriden kapanan pay' formülü TDD için ölçümle doğrulanmadı."],
          ["Not: Kosullu bicimlendirme Excel'de goruntulenerek dogrulanmadi (bu ortamda Excel acilamiyor). Renkler gelmezse haber ver."]]:
    n.append(t)
n["A1"].font = Font(bold=True, size=14); n.column_dimensions["A"].width = 140

wb.save(OUT); print("tamam")

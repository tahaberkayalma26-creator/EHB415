"""Ortak degerler sayfasini uretir: ogretici/veri/ortak_degerler.xlsx ve ortak_prs_konfig.csv (ayni kaynaktan).
Calistirma: python ortak_sheet_uret.py
'Durum' sutunu: KAYNAK (standart/kod), TURETME (hesap), ONERI (takim onaylayacak), OLCULECEK (kimin olcecegi yazili), DENENDI (Taha oturumunda calistirildi).
"""
import csv, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
VERI = os.path.join(HERE, "..", "veri")
HDR = PatternFill("solid", fgColor="DBEAFE")
wb = Workbook(); wb.remove(wb.active)

def sayfa(ad, baslik, satirlar, genislik):
    ws = wb.create_sheet(ad)
    ws.append(baslik)
    for h in ws[1]:
        h.font = Font(bold=True); h.fill = HDR
    for s in satirlar: ws.append(s)
    for i, g in enumerate(genislik, 1): ws.column_dimensions[get_column_letter(i)].width = g
    for r in ws.iter_rows():
        for c in r: c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"
    return ws

# ---------------------------------------------------------------- 1. ortak degerler (satir numaralari formullerde kullaniliyor: B8 PRB, B11 slot/cerceve, B12 TDD periyot, B13 DL slot, B16 veri genisligi)
sayfa("Ortak değerler", ["Değer", "Sayı", "Birim", "Durum", "Kaynak / not"], [
    ["Merkez frekans", 3.5, "GHz", "KARAR (Taha)", "Türkiye'de 5G baz istasyonları bu frekans civarında (Taha)."],
    ["Band", "n78", "", "KAYNAK", "TS 38.101-1: n78 = 3300-3800 MHz, TDD. OCUDU band_helper.cpp: n78 = TDD."],
    ["NR-ARFCN (DL)", 633334, "", "DENENDİ", "600000 + (3500-3000) MHz / 15 kHz = 633333,3; n78'de 30 kHz rasterinde adım 2 olduğundan çift sayı: 633334 (3500,01 MHz). OCUDU kabul etti."],
    ["Çift yönlü mod", "TDD", "", "KAYNAK", "Eski OCUDU testi band 3 (FDD) idi. Sayılar yeniden ölçülecek."],
    ["Ana alt taşıyıcı aralığı (SCS)", 30, "kHz", "DENENDİ", "OCUDU n78'de 15 kHz'i REDDETTİ: 'Common SCS 15kHz is not equal to SSB SCS 30kHz'. n78'de SSB yalnız 30 kHz (OCUDU band_helper.cpp satır 308). Ana ızgara 30 kHz."],
    ["Kanal bant genişliği", 100, "MHz", "KARAR (Taha)", "Türkiye'de 5G yayını 100 MHz ile yapılıyor (Taha). Yedek ızgara: 40 MHz (106 PRB), OCUDU'da çalıştığı doğrulandı: 'Yedek ızgara' sayfası."],
    ["PRB sayısı (ana ızgara)", 273, "PRB", "KAYNAK", "TS 38.101-1 Tablo 5.3.2-1, SCS 30 kHz, 100 MHz."],
    ["Alt taşıyıcı sayısı", "=B8*12", "", "TÜRETME", "1 PRB = 12 alt taşıyıcı."],
    ["Slot süresi", 0.5, "ms", "GENEL BİLGİ", "30 kHz: 1 slot = 0,5 ms, 14 sembol. TS 38.211 §4.3'ten teyit edilmedi (dosya bizde yok). OCUDU testinde 30 kHz'te DL ok 1200/s, 2000 slot/s ile uyumlu göründü. Eski testte 15 kHz idi (1 ms)."],
    ["Slot sayısı / 10 ms çerçeve", 20, "slot", "GENEL BİLGİ", "30 kHz: 10 ms / 0,5 ms. Çerçeve süresi 10 ms (TS 38.211 teyit edilmedi)."],
    ["TDD deseni: periyot", 10, "slot", "DENENDİ", "OCUDU varsayılanı (du_high_config.h: dl_ul_period_slots = 10 → 5 ms). Testte kabul edildi."],
    ["TDD deseni: DL slot", 6, "slot", "DENENDİ", "OCUDU varsayılanı (nof_dl_slots = 6). Testte DL ok 1200/s, UL ok 600/s göründü (2000 slot/s içinde)."],
    ["TDD deseni: karışık slottaki DL sembol", 8, "sembol", "KAYNAK", "OCUDU varsayılanı (nof_dl_symbols = 8). Model kaybı karışık slotu saymaz."],
    ["TDD deseni: UL slot", 3, "slot", "KAYNAK", "OCUDU varsayılanı (nof_ul_slots = 3)."],
    ["Veri (PDSCH) genişliği", 48, "PRB", "ÖN DEĞER (Fatih doğrulayacak)", "40 MHz koşusunda 9566 kez [0..48); 100 MHz koşusunda 8185 kez [0..48) (ocudu_veri_genislik.sh, tek koşu). Ama 100 MHz koşusunda veri akışı yoktu (DL/UL = 0), bu yüzden kesin değil. Eski testteki 96 geçerli değil."],
    ["PRS yokken DL hızı", "ÖLÇÜLECEK", "Mbps", "ÖLÇÜLECEK (Fatih)", "100 MHz: tek koşuda DL ve UL = 0 (veri akışı yok, nedeni bilinmiyor; Fatih araştıracak). Yedek 40 MHz: DL 36 Mbps (ok 1200/s), UL 44,9 Mbps (ok 600/s). Eski 59,0 / 77,3 band 3 FDD içindi; geçerli değil."],
    ["PRS yokken UL hızı", "ÖLÇÜLECEK", "Mbps", "ÖLÇÜLECEK (Fatih)", "Aynı not."],
    ["gNB konumu", "EEF çatısı", "", "KARAR", "Proje kararı (ITU kampüs haritası)."],
    ["Menzil", 300, "m", "KARAR", "Proje kararı."],
    ["Verici gücü", 37, "dBm", "KAYNAK", "TR 38.765 v20.0.0 Tablo A-1 (okundu): 'Max BS Tx power 37 dBm, 52 dBm'; not 1: 37 dBm = Baseline 2 (anten izolasyonu 65 dB), 52 dBm = Baseline 1 (80 dB)."],
    ["Hedef RCS (ortalama)", -12.81, "dBsm", "KAYNAK", "TR 38.901 Tablo 7.9.2.1-1 'UAV with small size': 10lg(σ_M) = -12,81 dBsm (Taha'nın gönderdiği ekran görüntüsü; belge sürümü görünmüyor). radar_takip.py şimdi -20 kullanıyor, güncellenecek."],
    ["Hedef RCS sapması (σ_S)", 3.74, "dB", "KAYNAK; KULLANILMIYOR", "Aynı tablo: σ_S sapması 3,74 dB. KARAR (Taha): şimdilik modellenmeyecek, RCS sabit -12,81 dBsm. Raporda 'standarttaki 3,74 dB sapma modellenmedi' yazılacak."],
    ["Gürültü figürü", 5, "dB", "KAYNAK", "TR 38.765 Tablo A-1: 'BS receiver noise figure 5 dB' (FR1); FR2-1 için 7 dB."],
    ["Hedef boyutu", "0,3 × 0,4 × 0,2 m", "", "KAYNAK", "TR 38.765 Tablo A-1: 'UAV with small size (0.3m x 0.4m x 0.2m)'."],
    ["TR'nin FR1 değerlendirme ayarı", "4 veya 4,9 GHz, 100 MHz, 30 kHz", "", "KAYNAK", "TR 38.765 Tablo A-1. Bizim 3,5 GHz bunların dışında (TR'nin listesinde yok). 100 MHz ve 30 kHz ile uyuşuyor."],
    ["Sensing payı α (tanım)", "PRS'in kapattığı PRB×slot / toplam PRB×slot", "", "TANIM", "Sözlük: kartlar 4."],
], [34, 22, 9, 22, 90])

# ---------------------------------------------------------------- 2. SCS karsilastirma (40 MHz)
tablo = [(15, "N/A (15 kHz için en çok 50 MHz = 270 PRB)", "HAYIR: denendi, ret", "Sionna ve ns-3'te 50 MHz ile çalışır"), (30, 273, "EVET: denendi (40 MHz'de veri aktı, 100 MHz'de akmadı)", "ana ızgara"), (60, 135, "DENENMEDİ (n78'de SSB 60 kHz yok, büyük olasılıkla ret)", "Sionna ve ns-3'te çalışır")]
sayfa("SCS karşılaştırma (100 MHz)", ["SCS (kHz)", "PRB (100 MHz)", "Slot (ms)", "Slot / 10 ms", "OCUDU n78'de çalışır mı", "Not", "Kaynak"],
      [[s, n, 1 / (s / 15), int(10 / (1 / (s / 15))), o, nt, "TS 38.101-1 Tablo 5.3.2-1 (100 MHz sütunu)"] for s, n, o, nt in tablo], [10, 12, 10, 12, 40, 28, 40])

# ---------------------------------------------------------------- 3. PRS konfigurasyonlari (30 kHz: periyot 10 slot = 5 ms)
cols = ["id", "periyot_slot", "sembol", "comb", "bw_prb", "sembol_ofset", "slot_ofset", "aciklama"]
prs = [
    ["K0", 0, 0, 0, 0, 0, 0, "PRS yok (referans)"],
    ["K1", 10, 4, 4, 48, 2, 1, "Referans PRS (5 ms'de bir)"],
    ["K2", 20, 4, 4, 48, 2, 1, "Yalnız periyot: 10 ms"],
    ["K3", 40, 4, 4, 48, 2, 1, "Yalnız periyot: 20 ms"],
    ["K4", 10, 4, 4, 272, 2, 1, "Yalnız genişlik: tüm hücre (272 PRB). Veri kaybı K1 ile aynı olmalı (veri alanı 48 PRB ise), menzil çözünürlüğü çok daha iyi"],
    ["K5", 10, 4, 4, 24, 2, 1, "Yalnız genişlik: yarım"],
    ["K6", 10, 12, 4, 48, 2, 1, "Yalnız sembol sayısı: 12"],
    ["K7", 10, 4, 2, 48, 2, 1, "Yalnız comb: 2"],
    ["K8", 10, 12, 12, 48, 2, 1, "Comb 12, 12 sembol"],
    ["K9", 10, 4, 4, 48, 0, 1, "Yalnız sembol ofseti: 0"],
    ["K10", 10, 4, 4, 48, 10, 1, "Yalnız sembol ofseti: 10"],
    ["K11", 10, 6, 6, 48, 2, 1, "Comb 6, 6 sembol"],
]
with open(os.path.join(VERI, "ortak_prs_konfig.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(cols); w.writerows(prs)
ws = sayfa("PRS konfigürasyonları", cols + ["PRS aralığı (ms)", "Model kaybı (DL slotları içinde)", "Durum"],
           [r + [f"=IF(B{i+2}=0,0,B{i+2}*'Ortak değerler'!B10)",
                 f"=IF(B{i+2}=0,0,('Ortak değerler'!B11/B{i+2})/('Ortak değerler'!B13*'Ortak değerler'!B11/'Ortak değerler'!B12)*MIN(E{i+2},'Ortak değerler'!B16)/'Ortak değerler'!B16)",
                 "ÖNERİ: her satır bir parametreyi değiştirir. Kayıp modeli TDD için ölçümle doğrulanmadı."] for i, r in enumerate(prs)],
           [6, 12, 9, 7, 8, 13, 11, 40, 14, 20, 60])
ws.append([])
ws.append(["Kural (TS 38.211 §7.4.1.7, OCUDU prs.cpp / prs_constants.h): comb {2,4,6,12}; sembol {2,4,6,12}; sembol >= comb ve comb'un katı olmalı. "
           "Periyot (30 kHz, slot) = 2 × {4,5,8,10,16,20,32,40,64,80,...}. PRS genişliği 24..272 PRB, 4'ün katı. Hücre 273 PRB, PRS en çok 272."])
ws.append(["PRS aralığı sütunu 'Slot süresi' hücresini (B10) kullanır. Model kaybı hücresi 'Veri genişliği' (B16) ve TDD hücrelerini kullanır; hücreler 'ÖLÇÜLECEK' yazarsa #DEĞER! görünür."])
ws.append(["Ofset kabulü: eski testte (FDD, band 3, 15 kHz) ofset 0, 2, 10 kabul; 1, 5, 7 NZP-CSI-RS ile çakışıp ret. n78 TDD 30 kHz'te yeniden denenecek."])
ws.append(["PRS slotu TDD'de DL slotuna düşmeli (slot_ofset 1 = periyodun 1. slotu; DL slotlar 0-5). Aksi halde OCUDU reddedebilir; sonucu yazın."])

# ---------------------------------------------------------------- 4. ns-3 bant (30 kHz ana, 15 kHz karsilastirma)
rows = [[100 - 5 * i, f"=ROUNDDOWN(A{i+2}*1000000*(1-0.04)/(12*30000),0)", f"=1-B{i+2}/B2", ""] for i in range(7)]
rows[0][3] = "KAYNAK: formül nr-phy.cc:571-584 (okundu). %4 ek yük oranı Aziz raporundan, kodda doğrulanmadı. 30 kHz = numeroloji 1."
sayfa("ns-3 bant (30 kHz)", ["Bant (MHz)", "PRB", "Gerçek α = 1 - PRB/ilk satır", "Not"], rows, [12, 12, 22, 80])
rows = [[50 - 3 * i, f"=ROUNDDOWN(A{i+2}*1000000*(1-0.04)/(12*15000),0)", f"=1-B{i+2}/B2", ""] for i in range(7)]
rows[0][3] = "15 kHz = numeroloji 0. 15 kHz'te en geniş bant 50 MHz (270 PRB, TS 38.101-1); ns-3 hesabı 266 PRB verir, 30 kHz / 100 MHz ile aynı. Karşılaştırma içindir."
sayfa("ns-3 bant (15 kHz)", ["Bant (MHz)", "PRB", "Gerçek α = 1 - PRB/ilk satır", "Not"], rows, [12, 12, 22, 80])

# ---------------------------------------------------------------- 5. Sionna
sayfa("Sionna", ["Değer", "Sayı", "Not"], [
    ["Merkez frekans (Hz)", 3.5e9, "rt_sehir.py: FC = 4.9e9 idi → 3.5e9"],
    ["SCS (Hz)", 30000, "radar_takip.py: 30e3 (zaten 30 kHz). Karşılaştırma: 15e3 ve 60e3."],
    ["Kullanılan alt taşıyıcı", "=273*12", "Ortak ızgara: 273 PRB (radar_takip.py'de N = 1024 idi → 3276)"],
    ["Dalga boyu λ (m)", "=3E8/B2", "8,57 cm"],
    ["Sembol süresi Ts (µs)", "=(1/B3)*(1+7/64)*1E6", "radar_takip.py'deki CP oranı korunur; normal CP'nin gerçek oranı kontrol edilecek (ÇIKARIM)"],
    ["PRS periyodu, sembol sayısı, comb", "ortak_prs_konfig.csv", "K1..K11"],
], [30, 24, 80])

sayfa("Yedek ızgara (40 MHz)", ["Değer", "Sayı", "Durum", "Not"], [
    ["Bant", "40 MHz", "DENENDİ", "n78, 30 kHz, ARFCN 633334; OCUDU'da veri aktı: kurulum/ocudu_testmode_n78.yml"],
    ["PRB", 106, "KAYNAK", "TS 38.101-1 Tablo 5.3.2-1 (30 kHz, 40 MHz)"],
    ["PRS'siz DL / UL", "36 / 44,9 Mbps", "DENENDİ (tek koşu)", "ok 1200 / 600"],
    ["K1 (periyot 10, 4 sembol, comb 4, bw 48, ofset 2)", "DL 29 / UL 44,9 Mbps", "DENENDİ (tek koşu)", "ok 1000 / 600"],
    ["PDSCH aralığı", "[0..48)", "DENENDİ", "9566 kez"],
], [44, 24, 24, 70])

# ---------------------------------------------------------------- 6. sonuc sablonu
sayfa("Sonuç şablonu", ["Konfig", "DL (Mbps)", "UL (Mbps)", "DL kayıp %", "UL kayıp %", "Model kayıp %", "Pd (300 m)", "Hız çözünürlüğü (m/s)", "En büyük hız (m/s)", "Kim ölçtü", "Tarih"],
      [[r[0]] + [""] * 10 for r in prs], [8, 10, 10, 12, 12, 14, 12, 18, 16, 12, 12])

wb.save(os.path.join(VERI, "ortak_degerler.xlsx"))
print("tamam")

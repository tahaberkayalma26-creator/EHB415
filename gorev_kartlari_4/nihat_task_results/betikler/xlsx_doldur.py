"""[Nihat, gorev kartlari 4] Sonuclarin ortak dosya bicimine aktarilmasi.
Kaynak: ogretici/veri/ortak_degerler.xlsx (kartin isaret ettigi, K11'i iceren depo surumu). Kaynak dosya DEGISTIRILMEZ; kopya yazilir:
    gorev_kartlari_4/nihat_task_results/Nihat_Ortak_Degerler_Tablosu.xlsx
Yapilanlar:
  - 'Sonuc sablonu' sayfasinda yalnizca Nihat'a ait sutunlar doldurulur: G (Pd, 300 m), H (hiz cozunurlugu), I (en buyuk hiz),
    J (kim olctu), K (tarih). DL/UL olcum sutunlari (B-F) bu gorevin kapsami disinda oldugundan bos birakilir.
  - Diger ortak sayfalara dokunulmaz; ayrintili sonuclar 'Nihat ...' adli yeni sayfalara yazilir.
Calistirma (tum betikler calistiktan sonra):  python xlsx_doldur.py
"""
import os
import numpy as np
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__)); KOK = os.path.join(HERE, "..")
CIK = os.path.join(KOK, "cikti")
KAYNAK = os.path.join(KOK, "..", "..", "ogretici", "veri", "ortak_degerler.xlsx")
HEDEF = os.path.join(KOK, "Nihat_Ortak_Degerler_Tablosu.xlsx")
TARIH = "2026-11-21"
LAM = 3e8 / 3.5e9
RCS_CUMLE = ("RCS sabit −12,81 dBsm alındı (TR 38.901 Tablo 7.9.2.1-1, küçük drone ortalaması); standarttaki 3,74 dB sapma "
             "modellenmedi, bu yüzden sonuçlar iyimser olabilir.")

wb = openpyxl.load_workbook(KAYNAK)
ws = wb["Sonuç şablonu"]
ozet = pd.read_csv(os.path.join(CIK, "prs_n78", "prs_n78_ozet.csv")).set_index("id")
for r in range(2, ws.max_row + 1):
    kid = ws.cell(r, 1).value
    if kid is None: continue
    if kid == "K0":
        ws.cell(r, 7).value = "PRS yok: sensing yok"; ws.cell(r, 8).value = "-"; ws.cell(r, 9).value = "-"
    elif kid in ozet.index:
        s = ozet.loc[kid]
        ws.cell(r, 7).value = round(float(s.pd_300m_xsi40), 2)
        ws.cell(r, 8).value = round(float(s.hiz_cozunurlugu_ms), 3)
        ws.cell(r, 9).value = round(float(s.en_buyuk_hiz_ms), 3)
    ws.cell(r, 10).value = "Nihat (Sionna simülasyonu; yalnız G-I)"
    ws.cell(r, 11).value = TARIH
son = ws.max_row
notlar = ["Notlar (Nihat, G-I sütunları): simülasyon sonucudur, ölçüm değildir. Pd: 300 m, X_SI = 40 dB, P_FA = 1e-3, 160 deneme, "
          "160 ms gözlem, 3,5 GHz, hücre 273 PRB, PRS EPRE = veri EPRE (betikler/prs_takip_n78.py). X_SI = 30 dB'de K1-K11 Pd ≥ 0,99.",
          "H = λ/(2 × 0,16 s), I = λ/(4 × T_PRS), λ = 8,57 cm. I'dan büyük radyal hız katlanır (TR'de İHA hızı 0-50 m/s).",
          RCS_CUMLE,
          "Frekans: TR 38.765 değerlendirmesi 4 ve 4,9 GHz; projenin ortak ızgarası 3,5 GHz (TR listesinde yok)."]
for j, t in enumerate(notlar):
    ws.cell(son + 2 + j, 1).value = t
    ws.cell(son + 2 + j, 1).font = Font(italic=True)

def sayfa(ad, bloklar):
    """bloklar: [(baslik, DataFrame | list[str])]"""
    w = wb.create_sheet(ad); r = 1
    for baslik, icerik in bloklar:
        w.cell(r, 1).value = baslik; w.cell(r, 1).font = Font(bold=True); r += 1
        if isinstance(icerik, pd.DataFrame):
            for c, col in enumerate(icerik.columns, 1):
                w.cell(r, c).value = str(col); w.cell(r, c).font = Font(bold=True)
                w.cell(r, c).fill = PatternFill("solid", fgColor="E5E7EB")
            for row in icerik.itertuples(index=False):
                r += 1
                for c, v in enumerate(row, 1):
                    if isinstance(v, (float, np.floating)):
                        v = None if np.isnan(v) else round(float(v), 3)
                    elif isinstance(v, (np.integer, np.bool_)):
                        v = v.item()
                    w.cell(r, c).value = v
            r += 2
        else:
            for t in icerik:
                w.cell(r, 1).value = t; r += 1
            r += 1
    for c in range(1, 20): w.column_dimensions[get_column_letter(c)].width = 16
    w.column_dimensions["A"].width = 34
    return w

# 1) yol kazanci
mu = pd.read_csv(os.path.join(CIK, "yol_kazanci_5_konum.csv"))
mu = mu[["nokta", "x_m", "y_m", "z_m", "uzaklik_3b_m", "los_35", "kazanc_49_db", "kazanc_35_db", "fark_35_eksi_49_db", "serbest_uzay_49_db", "serbest_uzay_35_db"]]
it = pd.read_csv(os.path.join(CIK, "itu_35", "yol_kazanci_5_konum_itu.csv"))
sayfa("Nihat yol kazancı", [("Münih sahnesi (rt_sehir_35.py), İHA rotasının 5 noktası, max_depth = 3, izotropik antenler", mu),
                            ("ITU EEF kampüsü (itu_35ghz.py), 5 konum, max_depth = 3, izotropik antenler", it),
                            ("Serbest uzayda beklenen fark", [f"20·log10(4,9/3,5) = {20 * np.log10(4.9 / 3.5):.2f} dB"])])

# 2) Pd eski / yeni
ay = pd.read_csv(os.path.join(CIK, "radar_35", "ayristirma_pd_300m.csv"))
piv = ay.pivot_table(index=["X_SI_dB", "ayar"], columns="alpha", values="pd_300m").reset_index()
piv.columns = ["X_SI_dB", "ayar"] + [f"alfa {100 * a:.1f} %" for a in piv.columns[2:]]
kart = pd.DataFrame([dict(kaynak="kartlar 2 (radar_takip.py, 4,9 GHz, 1024 alt taş., -20 dBsm)", X_SI_dB=40, a20=0.18, a40=0.56, a50=0.73, a100=0.96),
                     dict(kaynak="kartlar 2 (radar_takip.py, 4,9 GHz, 1024 alt taş., -20 dBsm)", X_SI_dB=30, a20=1.00, a40=1.00, a50=1.00, a100=1.00),
                     dict(kaynak="yeni (radar_takip_35.py + tr_metrik_olc_35.py bölüm 3)", X_SI_dB=40, a20=1.00, a40=1.00, a50=1.00, a100=1.00),
                     dict(kaynak="yeni (radar_takip_35.py + tr_metrik_olc_35.py bölüm 3)", X_SI_dB=30, a20=1.00, a40=1.00, a50=1.00, a100=1.00)])
kart.columns = ["kaynak", "X_SI_dB", "alfa 20 %", "alfa 40 %", "alfa 50 %", "alfa 100 %"]
kb = pd.read_csv(os.path.join(CIK, "radar_35", "kaynak_basari.csv"))
sayfa("Nihat Pd (300 m)", [("Kartın istediği tablo: 300 m'de Pd, eski / yeni (160 deneme)", kart),
                           ("Ayrıştırma: tek tek değiştirilen parametreler (aynı rastgele sayılar, tohum 11)", piv),
                           ("Yeni radar, menzil ve α'ya göre Pd ve RMSE (kaynak_basari, X_SI = 40 dB)", kb)])

# 3) hiz tablosu ve PRS ozeti
hz = pd.DataFrame([dict(konfig=k, periyot_ms=p * 0.5, prs_firsati_160ms=int(160 / (p * 0.5)), en_buyuk_hiz_ms=LAM / (4 * p * 0.5e-3),
                        hiz_cozunurlugu_ms=LAM / (2 * 0.16)) for k, p in (("K1", 10), ("K2", 20), ("K3", 40))])
oz = ozet.reset_index()
sayfa("Nihat PRS ve hız", [("K1-K3 hız tablosu (λ = 8,57 cm)", hz),
                           ("PRS K1-K11, n78 / 3,5 GHz / 273 PRB hücre, 160 ms (prs_takip_n78.py)", oz)])

# 4) throughput
tb = pd.read_csv(os.path.join(CIK, "veri_tbs", "tbs_sonuclar.csv"))
sayfa("Nihat throughput (TBS)", [("PRS'in boş kutularının veriye açılması: TS 38.214 §5.1.3.2 TBS hesabı (prs_veri_tbs.py). "
                                  "M1 PRB kapatma (OCUDU), M2 PRB×sembol rate matching, M3 RE (comb) rate matching", tb)])

# 5) menzil cozunurlugu
mc = pd.read_csv(os.path.join(CIK, "menzil_cozunurlugu", "menzil_cozunurlugu_hesap.csv"))
ih = pd.read_csv(os.path.join(CIK, "menzil_cozunurlugu", "iki_hedef_ayirma.csv"))
sayfa("Nihat menzil çözünürlüğü", [("Hesap: ΔR = c/(2B)", mc), ("Simülasyon: iki hedefin ayırt edilme olasılığı", ih)])

wb.save(HEDEF)
print("yazildi:", os.path.relpath(HEDEF), "| sayfalar:", wb.sheetnames)

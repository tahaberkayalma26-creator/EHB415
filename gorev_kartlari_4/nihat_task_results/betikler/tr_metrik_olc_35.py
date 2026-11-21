"""[Nihat, gorev kartlari 4, adim 2] ogretici/sionna_sehir/tr_metrik_olc.py'nin KOPYASI; radar_takip.py yerine radar_takip_35.py'yi yukler.
Calistirma (once rt_sehir_35.py ve radar_takip_35.py bir kez calismis olmali):
    python tr_metrik_olc_35.py
Bolum 1-3 asil dosyayla ayni yontem (ayni tohum 11, ayni sira), yalnizca radar yeni ortak izgarada:
1) Pf1: hedefsiz CPI'larda yanlis alarm orani.
2) Pmd <= %5 (Pd >= 0,95) saglayan en kucuk alfa: yeni kaynak_basari.csv (cikti/radar_35) ve eski (ogretici/sionna_sehir/cikti) yan yana.
3) X_SI_DB 40 ve 30 iken 300 m'de Pd (alfa = %20 / 40 / 50 / 100)  -> kartin istedigi tablo.
Eklenen bolumler (kart: "farkin RCS'ten mi, frekanstan mi geldigini ayirmak icin RCS'i tek basina degistirdigin bir kosu"):
4) Ayristirma: eski ayardan baslayip frekans, N (bant) ve RCS tek tek / birlikte degistirilir. Her ayar ayni rastgele sayilarla
   (tohum 11, ortak rastgele sayilar) kosulur; boylece farklar Monte Carlo gurultusunden degil parametreden gelir.
5) SNR butcesi (hesap, Monte Carlo degil): ornek basina SNR, islem kazanci, RD haritasindaki tepe SNR'i ve esige gore pay.
"""
import os, time
import numpy as np
import pandas as pd
import radar_takip_35 as rt       # kopya radar (3,5 GHz npz, N = 3276, RCS = -12,81); film/analiz calismaz

t0 = time.time()
rng = np.random.default_rng(11)
YENI = dict(fc_hz=rt.fc, n_alt=rt.N, rcs_dbsm=rt.RCS_DBSM)          # 3,5 GHz, 3276, -12,81 (yuklenen varsayilan)
print("radar ayari:", rt.ayarla(), f"| menzil kutusu {rt.C / (2 * rt.W):.2f} m | X_SI = {rt.X_SI_DB} dB\n")

# ---------------- 1) Pf1
print("1) Pf1 (hedef yok; radar_takip.PFA = %g, CPI basina)" % rt.PFA)
for M in (14, 70):                                   # alpha = %10 ve %50
    n = 3000; k = 0
    for _ in range(n):
        rax, vax, P = rt.radar(300.0, 0.0, M, -np.inf, rng)   # snr = -inf dB -> yanki genligi 0 -> yalnizca gurultu
        k += bool(rt.tespit(rax, vax, P)[0])
    print(f"   M={M:3d} (alpha={M/rt.FRAME_SYM:.0%}): {k}/{n} hedefsiz CPI'da alarm -> Pf1 = {100*k/n:.2f} %")

# ---------------- 2) Pmd <= %5 icin gereken alfa
print("\n2) Pmd <= %5 (Pd >= 0,95) icin en kucuk alfa")
ESKI_CSV = os.path.join(rt.HERE, "..", "..", "..", "ogretici", "sionna_sehir", "cikti", "kaynak_basari.csv")
for ad, yol in (("yeni (3,5 GHz, 3276 alt tas., -12,81 dBsm)", os.path.join(rt.OUT, "kaynak_basari.csv")),
                ("eski (4,9 GHz, 1024 alt tas., -20 dBsm)  ", ESKI_CSV)):
    df = pd.read_csv(yol)
    for r, g in df.groupby("menzil_m"):
        ok = g[g.pd >= 0.95].sort_values("alpha")
        print(f"   {ad} {int(r)} m: " + (f"alfa = {ok.alpha.iloc[0]:.1%} (Pd = {ok.pd.iloc[0]:.2f})" if len(ok) else f"taranan alfa degerlerinin hicbirinde yok (en yuksek Pd = {g.pd.max():.2f})"))

# ---------------- 3) X_SI deneyi (kartin istedigi tablo)
print("\n3) 300 m'de Pd, X_SI_DB'ye gore (160 deneme)")
def pd_olc(r, M, n=160, g=None):
    g = rng if g is None else g
    ok = 0
    for _ in range(n):
        v0 = g.uniform(-30, 30); r_g = r + g.uniform(-6, 6)
        rax, vax, P = rt.radar(r_g, v0, M, rt.snr_ornek_db(r), g)
        tp, re_, ve = rt.tespit(rax, vax, P)
        ok += bool(tp and abs(re_ - r_g) < 3 * rt.C / (2 * rt.W))
    return ok / n
Ms = [28, 56, 70, 140]
print("   alpha:        " + "  ".join(f"{M/rt.FRAME_SYM:5.0%}" for M in Ms))
for x in (40.0, 30.0):
    rt.X_SI_DB = x                                    # snr_ornek_db() bu global degeri okur
    print(f"   X_SI={x:4.0f} dB: " + "  ".join(f"{pd_olc(300, M):5.2f}" for M in Ms))
rt.X_SI_DB = 40.0
print(f"   ({time.time() - t0:.0f} s)")

# ---------------- 4) Ayristirma: hangi degisiklik ne kadar etkiliyor?
AYARLAR = [  # (etiket, fc, N, RCS)
    ("A eski (kartlar 2)",          4.9e9, 1024, -20.0),
    ("B yalniz RCS",                4.9e9, 1024, -12.81),
    ("C yalniz frekans",            3.5e9, 1024, -20.0),
    ("D yalniz bant (N=3276)",      4.9e9, 3276, -20.0),
    ("F frekans + RCS (N=1024)",    3.5e9, 1024, -12.81),
    ("E yeni (hepsi)",              3.5e9, 3276, -12.81),
]
Ms4 = [4, 8, 14, 28, 56, 70, 140]
print("\n4) Ayristirma: 300 m'de Pd (160 deneme; her satir tohum 11 ile ayni rastgele sayilar)")
print("   alpha:                          " + "  ".join(f"{M/rt.FRAME_SYM:5.1%}" for M in Ms4))
sat = []
for x in (40.0, 30.0):
    rt.X_SI_DB = x
    for ad, f, n_, rc in AYARLAR:
        rt.ayarla(f, n_, rc)
        pds = []
        for M in Ms4:
            pds.append(pd_olc(300, M, g=np.random.default_rng(11)))
            sat.append(dict(X_SI_dB=x, ayar=ad, fc_GHz=f / 1e9, N=n_, RCS_dBsm=rc, M=M, alpha=M / rt.FRAME_SYM, pd_300m=pds[-1]))
        print(f"   X_SI={x:2.0f} {ad:28s} " + "  ".join(f"{p:5.2f}" for p in pds), flush=True)
pd.DataFrame(sat).to_csv(os.path.join(rt.OUT, "ayristirma_pd_300m.csv"), index=False)
rt.X_SI_DB = 40.0; rt.ayarla(**YENI)
print(f"   ({time.time() - t0:.0f} s)")

# ---------------- 5) SNR butcesi (hesap)
print("\n5) SNR butcesi, 300 m, X_SI = 40 dB (hedef kutu merkezinde; esik, ortalama gurultuye gore)")
print("   ayar                          ornek SNR   M=28: kazanc / tepe / esik / pay    M=140: kazanc / tepe / esik / pay")
for ad, f, n_, rc in AYARLAR:
    rt.ayarla(f, n_, rc)
    s0 = rt.snr_ornek_db(300.0)
    parca = []
    for M in (28, 140):
        g = 10 * np.log10(rt.N * M)
        nhucre = int(np.sum(np.arange(rt.N) * rt.C / (2 * rt.W) < 450.0)) * M
        esik = 10 * np.log10((np.log(nhucre) + np.log(1 / rt.PFA)) / np.log(2)) + 10 * np.log10(np.log(2))   # medyan esigi -> ortalamaya gore
        parca.append(f"{g:5.1f} / {s0 + g:5.1f} / {esik:4.1f} / {s0 + g - esik:+5.1f} dB")
    print(f"   {ad:28s} {s0:7.2f} dB   " + "    ".join(parca))
rt.ayarla(**YENI)
print(f"\nbitti ({time.time() - t0:.0f} s)")

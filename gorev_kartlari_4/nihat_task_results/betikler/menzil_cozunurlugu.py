"""[Nihat, CLAUDE.md 'Radar Configuration': bant genisligi 30 -> 100 MHz, menzil cozunurlugu karsilastirmasi]
1) Hesap: menzil cozunurlugu dR = c / (2 B), B = (dolu alt tasiyici sayisi) x SCS.
2) Simulasyon (iki hedef ayirt etme): ayni hizda, esit guclu iki IHA, aralarinda dr metre. radar_takip_35.radar ile ayni sinyal modeli
   (her RE'de rastgele fazli bilinen sembol, H = Y / X); M = 14 sembol, hedef basina toplam SNR 30 dB (sabit, VARSAYIM), hedefler
   arasi faz rastgele. Menzil profili 16 kat sifir dolgulu IFFT ile cikarilir. 'Ayrildi' olcutu: profilde iki yerel tepe, ikisinin
   arasindaki cukur kucuk tepeden en az 3 dB asagida ve tepeler arasi uzaklik 0,5 dr .. 1,5 dr icinde.
3) Tek hedef menzil hatasi (kestirim dogrulugu, cozunurlukten farkli): radar_takip (eski) ve radar_takip_35 (yeni) kaynak_basari ciktilari.
Calistirma:  python menzil_cozunurlugu.py        Cikti: cikti/menzil_cozunurlugu/
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "cikti", "menzil_cozunurlugu"); os.makedirs(OUT, exist_ok=True)
C, SCS = 3e8, 30e3
TS = (1 / SCS) * (1 + 7 / 64)
M, SNR_TOPLAM_DB, PAD, NDEN = 14, 30.0, 16, 200

# 1) hesap tablosu
TAB = [("radar_takip.py (eski, kartlar 2)",        1024 * 12 // 12,  "1024 alt tasiyici, dolu"),
       ("radar_takip_35.py (yeni, ortak izgara)", 273 * 12,         "273 PRB = 3276 alt tasiyici, dolu"),
       ("prs_takip.py (eski PRS)",                84 * 12,          "84 PRB, comb 4 (L = 4 sembolde tum alt tasiyicilar)"),
       ("PRS K1-K3, K6-K11 (48 PRB)",             48 * 12,          "48 PRB, comb birlestirilmis"),
       ("PRS K4 (272 PRB)",                       272 * 12,         "272 PRB, comb birlestirilmis"),
       ("PRS K5 (24 PRB)",                        24 * 12,          "24 PRB, comb birlestirilmis")]
sat = [dict(ayar=a, alt_tasiyici=n, bant_MHz=n * SCS / 1e6, menzil_cozunurlugu_m=C / (2 * n * SCS), not_=nt) for a, n, nt in TAB]
sat.append(dict(ayar="TR 38.765 Tablo A-1 FR1 (100 MHz, 30 kHz)", alt_tasiyici=273 * 12, bant_MHz=100.0, menzil_cozunurlugu_m=C / (2 * 100e6),
                not_="nominal bant; TR'nin degerlendirme ayari"))
tab = pd.DataFrame(sat); tab.to_csv(os.path.join(OUT, "menzil_cozunurlugu_hesap.csv"), index=False, float_format="%.3f")
pd.set_option("display.width", 200)
print("1) Hesap: dR = c / (2 B)\n" + tab.round(3).to_string(index=False))
print(f"   iyilesme (yeni / eski radar): {tab.menzil_cozunurlugu_m[0] / tab.menzil_cozunurlugu_m[1]:.2f} kat")

# 2) iki hedef simulasyonu
def profil(N, r1, r2, rng):
    n = np.arange(N)[:, None]
    X = np.exp(1j * 2 * np.pi * rng.random((N, M)))
    a = 10 ** ((SNR_TOPLAM_DB - 10 * np.log10(N * M)) / 20)          # RE basina genlik: toplam SNR 30 dB
    Y = np.zeros((N, M), complex)
    for r in (r1, r2):
        Y += a * np.exp(1j * 2 * np.pi * rng.random()) * X * np.exp(-1j * 2 * np.pi * n * SCS * 2 * r / C)
    Y += (rng.normal(size=Y.shape) + 1j * rng.normal(size=Y.shape)) / np.sqrt(2)
    h = (Y / X).mean(axis=1)                                         # ayni hiz (0 m/s): Doppler kutusu 0 = sembol ortalamasi
    p = np.abs(np.fft.ifft(h, PAD * N)) ** 2
    rax = np.arange(PAD * N) * C / (2 * PAD * N * SCS)
    return rax, p

def ayrildi(rax, p, r1, r2, dr):
    s = (rax > r1 - 3 * dr - 5) & (rax < r2 + 3 * dr + 5)
    x, y = rax[s], 10 * np.log10(p[s] + 1e-30)
    tep = np.where((y[1:-1] > y[:-2]) & (y[1:-1] >= y[2:]))[0] + 1
    if len(tep) < 2: return False
    iki = tep[np.argsort(y[tep])[-2:]]; i1, i2 = sorted(iki)
    if y[min(i1, i2)] < y.max() - 6 and y[max(i1, i2)] < y.max() - 6: return False
    cukur = y[i1:i2 + 1].min()
    ayr = abs(x[i2] - x[i1])
    return bool(min(y[i1], y[i2]) - cukur >= 3.0 and 0.5 * (r2 - r1) <= ayr <= 1.5 * (r2 - r1))

rng = np.random.default_rng(5)
DR = np.arange(0.5, 20.01, 0.5)
NLER = [(576, "48 PRB (17,28 MHz; PRS K1 esdegeri)"), (1024, "1024 alt tas. (30,72 MHz; eski radar)"), (3276, "273 PRB (98,28 MHz; yeni radar)")]
sonuc = {}
for N, ad in NLER:
    oran = []
    for d in DR:
        k = 0
        for _ in range(NDEN):
            r1 = 200.0 + rng.uniform(0, 5); r2 = r1 + d
            rax, p = profil(N, r1, r2, rng)
            k += ayrildi(rax, p, r1, r2, C / (2 * N * SCS))
        oran.append(k / NDEN)
    sonuc[ad] = oran
    i50 = next((d for d, o in zip(DR, oran) if o >= 0.5), np.nan); i90 = next((d for d, o in zip(DR, oran) if o >= 0.9), np.nan)
    print(f"2) {ad:40s}: c/2B = {C / (2 * N * SCS):5.2f} m | ayirma olasiligi >= 0,5 icin dr = {i50:.1f} m, >= 0,9 icin dr = {i90:.1f} m")
df = pd.DataFrame(sonuc, index=DR); df.index.name = "hedefler_arasi_m"; df.to_csv(os.path.join(OUT, "iki_hedef_ayirma.csv"), float_format="%.3f")
print("   secili satirlar (ayirma olasiligi):\n" + df.loc[[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0]].round(2).to_string())

# 3) tek hedef menzil hatasi (kaynak_basari)
eski = pd.read_csv(os.path.join(HERE, "..", "..", "..", "ogretici", "sionna_sehir", "cikti", "kaynak_basari.csv"))
yeni = pd.read_csv(os.path.join(HERE, "..", "cikti", "radar_35", "kaynak_basari.csv"))
k = eski.merge(yeni, on=["menzil_m", "M"], suffixes=("_eski", "_yeni"))
k = k[["menzil_m", "M", "alpha_eski", "pd_eski", "pd_yeni", "rmse_menzil_m_eski", "rmse_menzil_m_yeni", "rmse_hiz_ms_eski", "rmse_hiz_ms_yeni"]]
k.to_csv(os.path.join(OUT, "tek_hedef_rmse_eski_yeni.csv"), index=False, float_format="%.3f")
print("\n3) Tek hedef: menzil/hiz RMSE (yalnizca Pd >= 0,5 iken; eski 4,9 GHz/30,72 MHz/-20 dBsm, yeni 3,5 GHz/98,28 MHz/-12,81 dBsm)\n"
      + k.round(3).to_string(index=False))

# sekil
fig, ax = plt.subplots(1, 2, figsize=(12.5, 4))
for (N, ad), c in zip(NLER, ["#9ca3af", "#ea580c", "#2563eb"]):
    ax[0].plot(DR, sonuc[ad], "o-", ms=3, color=c, label=ad)
    ax[0].axvline(C / (2 * N * SCS), color=c, ls=":", lw=1)
ax[0].set_xlabel("iki İHA arasındaki menzil farkı (m)"); ax[0].set_ylabel("ayırt edilme olasılığı"); ax[0].grid(alpha=0.3)
ax[0].set_title(f"İki hedef ayırma (simülasyon, {NDEN} deneme/nokta, hedef başına SNR {SNR_TOPLAM_DB:.0f} dB)\nnoktalı çizgi: c/(2B)", fontsize=9)
ax[0].legend(fontsize=8, loc="lower right")
rr = np.random.default_rng(2)
for (N, ad), c in zip(NLER[1:], ["#ea580c", "#2563eb"]):
    rax, p = profil(N, 200.0, 203.0, rr)
    s = (rax > 185) & (rax < 220)
    ax[1].plot(rax[s], 10 * np.log10(p[s] / p[s].max()), color=c, label=ad)
for r in (200.0, 203.0): ax[1].axvline(r, color="black", ls="--", lw=0.8)
ax[1].set_ylim(-30, 2); ax[1].set_xlabel("menzil (m)"); ax[1].set_ylabel("normalize güç (dB)"); ax[1].grid(alpha=0.3)
ax[1].set_title("Örnek menzil profili: hedefler 200 m ve 203 m (kesikli)", fontsize=9); ax[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "menzil_cozunurlugu.png"), dpi=140); plt.close(fig)
print(f"\ncikti: {os.path.relpath(OUT)}")

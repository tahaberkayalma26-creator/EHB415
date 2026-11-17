"""OFDM'nin tek sembolde bastan sona zinciri (6 serit, CP yok). Her adim bir oncekinden HESAPLANIR, cizilmis degildir:
  1) vericinin 6 sayisi (her seridin fazi)  ->  2) 6 dalga  ->  3) toplam sinyal  ->  4) toplamin FFT'si  ->  5) alicinin 6 frekanstan okudugu sayilar.
Renk = serit kimligi (faz renk degil, derece olarak yazili). Alicinin okudugu faz ile vericinin koydugu fazin esit oldugu kontrol edilip basilir.
Calistirma: python ofdm_baglanti.py -> ofdm_baglanti.png
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTED, GRID = "#1F2937", "#6B7280", "#D1D5DB"
plt.rcParams.update({"font.size": 10, "text.color": INK, "axes.edgecolor": GRID})

SCS = 15e3
T = 1 / SCS
K = np.arange(1, 7)
KIMLIK = ["#2563EB", "#16A34A", "#D97706", "#DC2626", "#7C3AED", "#0891B2"]
FAZ_DEG = np.array([225, 315, 225, 45, 225, 45])          # vericinin sembol 1'e koydugu fazlar (ofdm_sinyal.py ile ayni)

N = 600
t = np.arange(N) * T / N
dalga = np.array([np.cos(2 * np.pi * k * SCS * t + np.deg2rad(d)) for k, d in zip(K, FAZ_DEG)])
toplam = dalga.sum(axis=0)

# alici: toplam sinyalin FFT'si; yalniz k x 15 kHz noktalari okunur (N ornek tam bir sembol -> bin k = k x 15 kHz)
X = np.fft.rfft(toplam) * 2 / N
okunan_gen = np.abs(X[K]); okunan_faz = np.rad2deg(np.angle(X[K])) % 360
assert np.allclose(okunan_faz, FAZ_DEG, atol=1e-6) and np.allclose(okunan_gen, 1.0, atol=1e-6)
print("alici okudu: faz", np.round(okunan_faz).astype(int), "genlik", np.round(okunan_gen, 3), "-> vericinin koyduguyla ayni")

# FFT egrisi (sifir doldurma ile ince cizim; ayni sinyal)
M = 1 << 15
Xi = np.fft.rfft(toplam, M) * 2 / N
fi = np.fft.rfftfreq(M, d=T / N) / 1e3

fig = plt.figure(figsize=(10, 13.4))
gs = fig.add_gridspec(5, 1, height_ratios=[0.8, 2.3, 1.2, 1.5, 0.8], hspace=0.95)
axs = [fig.add_subplot(gs[i]) for i in range(5)]

def kutular(ax, deg, baslik, ok=False):
    ax.set_xlim(0, 6); ax.set_ylim(0, 1); ax.axis("off")
    for i, (k, d) in enumerate(zip(K, deg)):
        ax.add_patch(FancyBboxPatch((i + 0.06, 0.08), 0.88, 0.84, boxstyle="round,pad=0,rounding_size=0.08", fc=KIMLIK[i], ec="none"))
        ax.text(i + 0.5, 0.64, f"{k * 15} kHz", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
        ax.text(i + 0.5, 0.30, f"faz {int(round(d))}°", ha="center", va="center", color="white", fontsize=11)
    ax.set_title(baslik, loc="left", fontsize=11, fontweight="bold")

kutular(axs[0], FAZ_DEG, "1) Verici: bu sembole 6 şeridin her birine bir faz değeri koyar (bitler bu açılarda saklı)")

# ---- 2: tek tek dalgalar
ax = axs[1]
for i in range(6):
    y0 = 6 - i
    ax.plot(t * 1e6, dalga[i] * 0.42 + y0, color=KIMLIK[i], lw=1.6)
    ax.axhline(y0, color=GRID, lw=0.5)
ax.set_yticks(6 - np.arange(6)); ax.set_yticklabels([f"{k * 15} kHz" for k in K])
ax.set_xlim(0, T * 1e6); ax.set_ylim(0.4, 6.6)
ax.set_title("2) Her şerit kendi frekansında ve kendi fazıyla bir sinüs üretir (yatay eksen: zaman, µs; toplam 66,7 µs)", loc="left", fontsize=11, fontweight="bold")

# ---- 3: toplam
ax = axs[2]
ax.plot(t * 1e6, toplam, color=INK, lw=1.4)
ax.set_xlim(0, T * 1e6); ax.set_ylabel("genlik")
ax.set_title("3) Altı dalga toplanıp tek sinyal olarak antenden gider (zamanda bu görünür)", loc="left", fontsize=11, fontweight="bold")

# ---- 4: FFT
ax = axs[3]
ax.plot(fi, np.abs(Xi), color=MUTED, lw=1.2)
for i, k in enumerate(K):
    ax.plot(k * 15, okunan_gen[i], "o", color=KIMLIK[i], ms=10, zorder=3)
ax.set_xlim(0, 120); ax.set_ylim(0, 1.5); ax.set_xticks(K * 15)
ax.set_xlabel("frekans (kHz)"); ax.set_ylabel("genlik")
ax.set_title("4) Alıcı toplamın FFT'sini alır; yalnız 15, 30 … 90 kHz noktalarına bakar", loc="left", fontsize=11, fontweight="bold")
ax.text(0.5, 0.06, "gri eğri karışık görünür; ama noktalarda komşular sıfır olduğundan nokta, tek şeridin değerini verir (genlik hepsinde 1)", transform=ax.transAxes, ha="center", va="bottom", fontsize=8.5, color=MUTED)

kutular(axs[4], okunan_faz, "5) Alıcının noktalardan okuduğu fazlar: vericinin 1. adımda koyduklarıyla aynı  ✔")

# ---- adimlar arasi oklar
def ok(ust, alt, yazi):
    p1, p2 = axs[ust].get_position(), axs[alt].get_position()
    y = p1.y0 - 0.5 * (p1.y0 - p2.y1) - 0.006
    fig.text(0.5, y, "▼  " + yazi, ha="center", va="center", fontsize=10, color=INK, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.3", fc="#EEF2FF", ec=GRID))
ok(0, 1, "her şerit kendi sinüsünü üretir")
ok(1, 2, "6 dalga toplanır")
ok(2, 3, "FFT: toplamı tekrar frekanslarına ayırır")
ok(3, 4, "6 noktadan faz okunur")

fig.savefig(os.path.join(HERE, "ofdm_baglanti.png"), dpi=140, bbox_inches="tight", facecolor="white")
print("tamam")

"""OFDM sinyali zamanda ve frekansta: 6 serit, 3 sembol (kucuk ornek; CP yok, ekranda gorulsun diye).
Her serit k, frekansi k x 15 kHz olan bir dalga. Her sembolde (66,7 us) o seridin genligi ve fazi sabit; sembol degisince yeni deger gelir.
Satir 1: tablo (zaman x serit), her kutuda o seridin o semboldeki fazi.
Satir 2: her seridin kendi dalgasi (alt alta).
Satir 3: hepsinin toplami = antenden cikan gercek sinyal.
Satir 4: ilk sembolun frekans gorunumu: her seridin tepesi, komsularin tepesinde sifir.
Calistirma: python ofdm_sinyal.py -> ofdm_sinyal.png
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTED, GRID, ACC = "#1F2937", "#6B7280", "#D1D5DB", "#2563EB"
plt.rcParams.update({"font.size": 9.5, "text.color": INK, "axes.edgecolor": GRID})

SCS = 15e3
T = 1 / SCS                                             # bir sembolun suresi (s)
K = np.arange(1, 7)                                     # serit numaralari
NS = 3                                                  # sembol sayisi
rng = np.random.default_rng(5)
FAZ = rng.integers(0, 4, size=(K.size, NS))             # 0..3 -> 45, 135, 225, 315 derece
DERECE = np.array([45, 135, 225, 315])
RENK = ["#2563EB", "#16A34A", "#F59E0B", "#DC2626"]

t = np.linspace(0, NS * T, 1500, endpoint=False)
sembol = np.minimum((t / T).astype(int), NS - 1)
tus = t * 1e6                                           # mikrosaniye

def serit_dalgasi(i):
    return np.cos(2 * np.pi * K[i] * SCS * t + np.deg2rad(DERECE[FAZ[i, sembol]]))

fig = plt.figure(figsize=(10.5, 12.2))
gs = fig.add_gridspec(4, 1, height_ratios=[1.15, 2.3, 1.2, 1.25], hspace=0.5)

# ---- satir 1: tablo
ax = fig.add_subplot(gs[0])
ax.imshow(FAZ[::-1], aspect="auto", cmap=ListedColormap(RENK), vmin=-0.5, vmax=3.5, extent=[0, NS * T * 1e6, 0.5, K.size + 0.5], alpha=0.85)
for i in range(K.size):
    for s in range(NS):
        ax.text((s + 0.5) * T * 1e6, K[i], f"{DERECE[FAZ[i, s]]}°", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
ax.set_yticks(K); ax.set_yticklabels([f"{k * 15} kHz" for k in K])
ax.set_xticks([(s + 0.5) * T * 1e6 for s in range(NS)]); ax.set_xticklabels([f"sembol {s + 1}" for s in range(NS)])
ax.set_ylabel("şerit"); ax.set_title("1) Tablo: her kutuda o şeridin o semboldeki fazı (genlik hepsinde aynı)", loc="left", fontsize=10.5, fontweight="bold")
for s in range(1, NS): ax.axvline(s * T * 1e6, color="white", lw=2)

# ---- satir 2: tek tek dalgalar
ax = fig.add_subplot(gs[1])
for i in range(K.size):
    y = serit_dalgasi(i) * 0.42 + (K.size - i)
    ax.plot(tus, y, color=INK, lw=1.0)
    ax.axhline(K.size - i, color=GRID, lw=0.5)
ax.set_yticks(K.size - np.arange(K.size)); ax.set_yticklabels([f"{k * 15} kHz" for k in K])
ax.set_ylim(0.4, K.size + 0.7); ax.set_xlim(0, NS * T * 1e6)
for s in range(1, NS): ax.axvline(s * T * 1e6, color=ACC, lw=1.2, ls="--")
ax.text(0.5 * T * 1e6, K.size + 0.55, "sembol 1", ha="center", color=ACC, fontsize=9)
ax.text(1.5 * T * 1e6, K.size + 0.55, "sembol 2", ha="center", color=ACC, fontsize=9)
ax.text(2.5 * T * 1e6, K.size + 0.55, "sembol 3", ha="center", color=ACC, fontsize=9)
ax.set_xlabel("zaman (µs)  —  her sembolde şerit tam sayıda tur atar: 15 kHz 1 tur, 30 kHz 2 tur, 45 kHz 3 tur …"); ax.set_ylabel("şerit")
ax.set_title("2) Her şeridin kendi dalgası: sembol boyunca aynı sinüs, sembol değişince faz yeni değere sıçrar", loc="left", fontsize=10.5, fontweight="bold")

# ---- satir 3: toplam
ax = fig.add_subplot(gs[2])
toplam = sum(serit_dalgasi(i) for i in range(K.size))
ax.plot(tus, toplam, color=ACC, lw=1.1)
ax.set_xlim(0, NS * T * 1e6)
for s in range(1, NS): ax.axvline(s * T * 1e6, color=ACC, lw=1.2, ls="--")
ax.set_xlabel("zaman (µs)"); ax.set_ylabel("genlik")
ax.set_title("3) Altı dalganın toplamı = antenden çıkan gerçek sinyal", loc="left", fontsize=10.5, fontweight="bold")

# ---- satir 4: frekans gorunumu (sembol 1)
ax = fig.add_subplot(gs[3])
f = np.linspace(0, 150, 3000)
for k in K:
    ax.plot(f, np.abs(np.sinc((f - k * 15) / 15)), color=MUTED, lw=1.0, alpha=0.7)
    ax.plot(k * 15, 1.0, "o", color=RENK[FAZ[k - 1, 0]], ms=9, zorder=3)
    ax.text(k * 15, 1.1, f"{k * 15} kHz\n{DERECE[FAZ[k - 1, 0]]}°", ha="center", fontsize=8.5, color=INK)
ax.set_xlim(0, 150); ax.set_ylim(0, 1.4); ax.set_xticks(K * 15)
ax.set_xlabel("frekans (kHz)"); ax.set_ylabel("her şeridin yayılımı")
ax.set_title("4) Sembol 1'in frekans görünümü (nokta rengi = tablodaki faz rengi)", loc="left", fontsize=10.5, fontweight="bold")
ax.text(0.99, 0.55, "etekler üst üste biner ama\nher noktada (●) yalnız o şerit sıfırdan farklı", transform=ax.transAxes, ha="right", fontsize=8.5, color=MUTED)

fig.savefig(os.path.join(HERE, "ofdm_sinyal.png"), dpi=140, bbox_inches="tight", facecolor="white")
print("tamam")

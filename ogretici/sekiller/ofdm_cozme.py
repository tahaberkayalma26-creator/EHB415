"""OFDM alicisinda cozme: gelen toplam sinyalden 15 kHz seridinin acisi adim adim nasil cikar (kanal yok, gurultu yok).
Sekil 1 (ofdm_cozme_1.png): gelen sinyal -> referans cos -> carpim -> ortalama (carpimin 6 parcasi ayri ayri) -> I
Sekil 2 (ofdm_cozme_2.png): referans -sin ile ayni isleme -> Q -> (I,Q) noktasinin acisi; sonra 6 seridin hepsi
Her sayi gelen sinyalden hesaplanir; vericinin koydugu fazlar yalniz kontrol icin kullanilir.
Calistirma: python ofdm_cozme.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTED, GRID = "#1F2937", "#6B7280", "#D1D5DB"
KIMLIK = ["#2563EB", "#16A34A", "#D97706", "#DC2626", "#7C3AED", "#0891B2"]
plt.rcParams.update({"font.size": 10, "text.color": INK, "axes.edgecolor": GRID})

SCS = 15e3
T = 1 / SCS
N = 1200
t = np.arange(N) * T / N
tus = t * 1e6
K = np.arange(1, 7)
FAZ = np.array([225, 315, 225, 45, 225, 45])                  # vericinin koydugu fazlar (yalniz kontrol icin)
parca = np.array([np.cos(2 * np.pi * k * SCS * t + np.deg2rad(f)) for k, f in zip(K, FAZ)])
x = parca.sum(axis=0)                                         # alicinin eline gecen tek sinyal

def referans(k):  return np.cos(2 * np.pi * k * SCS * t), -np.sin(2 * np.pi * k * SCS * t)
def oku(k):
    rc, rs = referans(k)
    return 2 * np.mean(x * rc), 2 * np.mean(x * rs)           # I, Q
IQ = np.array([oku(k) for k in K])
DERECE = np.rad2deg(np.arctan2(IQ[:, 1], IQ[:, 0])) % 360
assert np.allclose(DERECE, FAZ, atol=1e-6)
print("okunan I,Q:", np.round(IQ, 3).tolist(), " faz:", np.round(DERECE).astype(int).tolist())

# ================= SEKIL 1
k0 = 1
rc, rs = referans(k0)
carp = x * rc
fig = plt.figure(figsize=(10, 14.5))
gs = fig.add_gridspec(4, 1, height_ratios=[1.0, 1.0, 1.25, 3.3], hspace=0.7)

ax = fig.add_subplot(gs[0])
ax.plot(tus, x, color=INK, lw=1.3); ax.set_xlim(0, T * 1e6); ax.set_ylabel("genlik")
ax.set_title("A) Alıcıya gelen tek sinyal x(t): 6 şeridin toplamı (içinde ne olduğunu bilmiyor)", loc="left", fontweight="bold")

ax = fig.add_subplot(gs[1])
ax.plot(tus, rc, color=KIMLIK[0], lw=1.6)
ax.set_xlim(0, T * 1e6); ax.set_ylim(-1.3, 1.3); ax.set_ylabel("genlik")
ax.set_title("B) Alıcının kendi ürettiği referans: 15 kHz'lik cos (alıcı hangi şeride baktığını kendi seçer)", loc="left", fontweight="bold")

ax = fig.add_subplot(gs[2])
ax.plot(tus, carp, color=INK, lw=1.2)
ort = carp.mean()
ax.axhline(0, color=GRID, lw=0.8)
ax.axhline(ort, color="#DC2626", lw=1.6, ls="--")
ax.text(0.99, 0.93, f"ortalama = {ort:.3f}   (×2 = {2 * ort:.3f})", transform=ax.transAxes, ha="right", va="top", color="#DC2626", fontweight="bold")
ax.set_xlim(0, T * 1e6); ax.set_ylabel("genlik")
ax.set_title("C) Çarpım x(t)·cos(15 kHz): A'nın her anı B'nin o anıyla çarpıldı. Kırmızı = ortalaması", loc="left", fontweight="bold")

ax = fig.add_subplot(gs[3])
aralik = 2.6
for m in range(6):
    y0 = (5 - m) * aralik
    p = parca[m] * rc
    ax.axhline(y0, color=GRID, lw=0.8)
    ax.plot(tus, p + y0, color=KIMLIK[m], lw=1.5)
    ax.hlines(y0 + p.mean(), 0, T * 1e6, color="#DC2626", lw=1.5, ls="--")
    ax.text(T * 1e6 * 1.01, y0, f"ortalama\n{p.mean():+.3f}", va="center", fontsize=9, color="#DC2626" if abs(p.mean()) > 1e-6 else MUTED)
    ax.text(-T * 1e6 * 0.015, y0, f"{(m + 1) * 15} kHz şeridi", ha="right", va="center", fontsize=9, color=INK)
ax.set_xlim(0, T * 1e6); ax.set_ylim(-1.6, 5 * aralik + 1.6); ax.set_yticks([])
ax.set_xticks([])
ax.set_title("D) C'yi 6 parçaya ayıralım: her şeridin dalgası ayrı ayrı 15 kHz referansla çarpılmış hali\n    (6 parçanın toplamı = C eğrisi; ortalamalar da toplanır)", loc="left", fontweight="bold")
toplam_ort = sum((parca[m] * rc).mean() for m in range(6))
ax.text(0.5, -0.09, f"6 ortalamanın toplamı = {toplam_ort:.3f}  = C'nin ortalaması.   ×2 → I = {2 * toplam_ort:.3f}  (= cos 225°)",
        transform=ax.transAxes, ha="center", va="top", fontsize=10.5, fontweight="bold")
fig.savefig(os.path.join(HERE, "ofdm_cozme_1.png"), dpi=130, bbox_inches="tight", facecolor="white")
plt.close(fig)

# ================= SEKIL 2
fig = plt.figure(figsize=(10, 11.6))
gs = fig.add_gridspec(3, 2, height_ratios=[1.0, 1.15, 1.15], hspace=0.62, wspace=0.28)

ax = fig.add_subplot(gs[0, :])
carp2 = x * rs
ort2 = carp2.mean()
ax.plot(tus, carp2, color=INK, lw=1.2); ax.axhline(0, color=GRID, lw=0.8)
ax.axhline(ort2, color="#DC2626", lw=1.6, ls="--")
ax.text(0.99, 0.93, f"ortalama = {ort2:.3f}   (×2 = {2 * ort2:.3f})", transform=ax.transAxes, ha="right", va="top", color="#DC2626", fontweight="bold")
ax.set_xlim(0, T * 1e6); ax.set_xlabel("zaman (µs)"); ax.set_ylabel("genlik")
ax.set_title("E) Aynı işlem ikinci referansla: x(t) · (−sin 15 kHz). Ortalamanın ×2'si = Q", loc="left", fontweight="bold")

ax = fig.add_subplot(gs[1, 0])
th = np.linspace(0, 2 * np.pi, 400)
ax.plot(np.cos(th), np.sin(th), color=GRID, lw=1.2)
ax.axhline(0, color=GRID, lw=0.6); ax.axvline(0, color=GRID, lw=0.6)
I0, Q0 = IQ[0]
ax.annotate("", xy=(I0, Q0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=KIMLIK[0], lw=2.2))
ax.plot(I0, Q0, "o", color=KIMLIK[0], ms=10)
ax.add_patch(matplotlib.patches.Arc((0, 0), 0.7, 0.7, theta1=0, theta2=DERECE[0], color=MUTED, lw=1.3))
ax.text(0.3, -0.35, f"{DERECE[0]:.0f}°", color=MUTED, fontsize=11)
ax.text(0, -1.3, f"(I, Q) = ({I0:.2f}, {Q0:.2f})", ha="center", fontsize=9)
ax.set_xlim(-1.4, 1.4); ax.set_ylim(-1.4, 1.4); ax.set_aspect("equal")
ax.set_xlabel("I  (= cos açı)"); ax.set_ylabel("Q  (= sin açı)")
ax.set_title("F) 15 kHz şeridinden çıkan iki sayı\nbir nokta olur; ok açısı = faz", loc="left", fontweight="bold", fontsize=10)

ax = fig.add_subplot(gs[1, 1])
ax.plot(np.cos(th), np.sin(th), color=GRID, lw=1.2)
ax.axhline(0, color=GRID, lw=0.6); ax.axvline(0, color=GRID, lw=0.6)
sayac = {}
for i, k in enumerate(K):
    anahtar = (round(IQ[i, 0], 2), round(IQ[i, 1], 2)); j = sayac.get(anahtar, 0); sayac[anahtar] = j + 1
    ox = IQ[i, 0] + (j - 1) * 0.0 + 0.0; oy = IQ[i, 1]
    yon = np.array([-IQ[i, 1], IQ[i, 0]]) / np.hypot(*IQ[i])           # daireye teget yon
    nx, ny = IQ[i] + yon * 0.16 * (j - 0.5 * (sum(1 for q in IQ if np.allclose(q, IQ[i])) - 1))
    ax.plot(nx, ny, "o", color=KIMLIK[i], ms=11)
    ax.text(nx, ny, f"{k * 15}", ha="center", va="center", fontsize=6.5, color="white", fontweight="bold")
for deg in (45, 135, 225, 315):
    ax.text(1.18 * np.cos(np.deg2rad(deg)), 1.18 * np.sin(np.deg2rad(deg)), f"{deg}°", ha="center", va="center", fontsize=8, color=MUTED)
ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_aspect("equal")
ax.set_xlabel("I"); ax.set_ylabel("Q")
ax.set_title("G) Altı şeridin altı noktası (sayı = kHz)\naynı açıya düşenler yan yana çizildi", loc="left", fontweight="bold", fontsize=10)

ax = fig.add_subplot(gs[2, :]); ax.axis("off")
satir = [["şerit", "I = 2·ort(x·cos)", "Q = 2·ort(x·(−sin))", "açı = atan2(Q, I)", "vericinin koyduğu"]]
for i, k in enumerate(K):
    satir.append([f"{k * 15} kHz", f"{IQ[i, 0]:+.3f}", f"{IQ[i, 1]:+.3f}", f"{DERECE[i]:.0f}°", f"{FAZ[i]}°"])
tb = ax.table(cellText=satir[1:], colLabels=satir[0], loc="center", cellLoc="center")
tb.auto_set_font_size(False); tb.set_fontsize(10); tb.scale(1, 1.6)
for j in range(5): tb[0, j].set_facecolor("#EEF2FF")
for i in range(6): tb[i + 1, 0].set_text_props(color=KIMLIK[i], fontweight="bold")
ax.set_title("H) Altı şerit için aynı işlem tekrarlandı (hepsi gelen x(t)'den hesaplandı)", loc="left", fontweight="bold")
fig.savefig(os.path.join(HERE, "ofdm_cozme_2.png"), dpi=130, bbox_inches="tight", facecolor="white")
print("tamam")

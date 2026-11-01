"""Tarak (comb) boyutu 2, 4, 12: ayni 1 PRB (12 serit) x 14 sembol.
Desen: OCUDU lib/phy/upper/signal_processors/prs/prs_generator_impl.cpp get_freq_offset (row_2, row_4, row_12).
Gecerlilik kurali: OCUDU lib/ran/prs/prs.cpp satir 15 (sembol sayisi >= tarak ve tarak'in kati).
Calistirma: python ocudu_tarak_karsilastirma.py -> ocudu_tarak_karsilastirma.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTED, GRID = "#1F2937", "#6B7280", "#D1D5DB"
SATIR = {2: [0, 1], 4: [0, 2, 1, 3], 12: [0, 6, 3, 9, 1, 7, 4, 10, 2, 8, 5, 11]}
SOFF = 2
plt.rcParams.update({"font.size": 9, "text.color": INK})

def renk(j, L):                                   # tek renk (mavi), acik -> koyu: kacinci PRS sembolu
    t = j / max(L - 1, 1)
    return (0.75 - 0.55 * t, 0.86 - 0.52 * t, 0.99 - 0.28 * t)

fig, axs = plt.subplots(3, 1, figsize=(10.6, 9.2), gridspec_kw=dict(hspace=0.5))
for ax, K in zip(axs, (2, 4, 12)):
    L = K
    ax.set_xlim(-1.2, 19.8); ax.set_ylim(-2.2, 13.6); ax.axis("off")
    for s in range(14):
        for k in range(12):
            ax.add_patch(Rectangle((s + 0.04, k + 0.04), 0.92, 0.92, fc="#F3F4F6", ec=GRID, lw=0.4))
    for j in range(L):
        for i in range(12 // K):
            k = K * i + SATIR[K][j]
            ax.add_patch(Rectangle((SOFF + j + 0.04, k + 0.04), 0.92, 0.92, fc=renk(j, L), ec="none"))
    for s in range(14): ax.text(s + 0.5, -0.35, str(s), ha="center", va="top", fontsize=7.5, color=MUTED)
    ax.text(-0.3, 6, "12 şerit\n(1 PRB)", ha="right", va="center", fontsize=8, color=MUTED)
    ax.set_title(f"comb_size: {K}   (her {K} şeritten 1'i;  nof_symbols en az {K})", loc="left", fontsize=10.5, fontweight="bold")
    ax.text(14.6, 9.5, f"bir sembolde dolu şerit: {12 // K} / 12", fontsize=9, va="center")
    ax.text(14.6, 7.0, f"PRS {L} sembole yayılır\n(sembol {SOFF}–{SOFF + L - 1})", fontsize=9, va="center", color=MUTED)
    ax.text(14.6, 4.0, "slot boyunca 12 şeridin\nhepsi bir kez dolmuş olur", fontsize=9, va="center", color=MUTED)
    if K == 4:
        ax.annotate("", xy=(SOFF + 0.5, 0.5), xytext=(SOFF + 0.5, 4.5), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.0))
        ax.text(SOFF - 0.1, 2.5, "diş arası 4", ha="right", va="center", fontsize=8.5)
    if K == 12:
        ax.text(SOFF + 6, 12.9, "tek diş: 12 sembol boyunca 12 farklı şerit", ha="center", fontsize=8.5, color=MUTED)
fig.suptitle("Tarak boyutu = PRS'in şeritlere ne kadar aralıklı konduğu", x=0.01, ha="left", fontsize=12, fontweight="bold")
fig.savefig(os.path.join(HERE, "ocudu_tarak_karsilastirma.png"), dpi=150, bbox_inches="tight", facecolor="white")
print("tamam")

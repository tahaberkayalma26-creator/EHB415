"""PRB ve slot: kayip nasil sayilir. Kucuk ornek: 4 slot x 8 PRB (gercekte OCUDU'da 96 PRB), PRS her 4 slotta bir, 4 PRB kaplar.
Yatay = zaman (14 sembol = 1 slot). Dikey = frekans (12 serit alt alta = 1 PRB).
PRS yalniz birkac sembol kullanir ama OCUDU o PRB'leri slot boyunca iletisime kapatir (kart: intra_slice_scheduler tum PDSCH sembol araligini tariyor).
Calistirma: python prb_slot_say.py -> prb_slot_say.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTED, GRID, ACC, RED = "#1F2937", "#6B7280", "#D1D5DB", "#2563EB", "#DC2626"
plt.rcParams.update({"font.size": 10, "text.color": INK, "axes.edgecolor": GRID})

NS, NP, SYM = 4, 8, 14
PRS_PRB = range(4, 8)               # ust 4 PRB (PRB 5..8)
PRS_SYM = range(2, 6)               # PRS'in kullandigi 4 sembol (ofset 2)

fig, ax = plt.subplots(figsize=(10.5, 6.3))
for s in range(NS):
    for p in range(NP):
        for y in range(SYM):
            ax.add_patch(Rectangle((s * SYM + y, p), 1, 1, fc="white", ec="#EEF0F3", lw=0.5))
        if s == 0 and p in PRS_PRB:
            for y in range(SYM):
                ax.add_patch(Rectangle((y, p), 1, 1, fc="#FECACA", ec="#EEF0F3", lw=0.5))
            for y in PRS_SYM:
                ax.add_patch(Rectangle((y, p), 1, 1, fc=RED, ec="#EEF0F3", lw=0.5))
for s in range(NS + 1): ax.plot([s * SYM] * 2, [0, NP], color=INK, lw=1.8)
for p in range(NP + 1): ax.plot([0, NS * SYM], [p, p], color=INK, lw=1.0)
ax.set_xlim(-6.5, NS * SYM + 1); ax.set_ylim(-2.2, NP + 1.8); ax.axis("off")

for s in range(NS): ax.text(s * SYM + SYM / 2, NP + 0.35, f"slot {s + 1}\n(14 sembol yan yana)", ha="center", va="bottom", fontsize=9.5, fontweight="bold")
for p in range(NP): ax.text(-0.4, p + 0.5, f"PRB {p + 1}", ha="right", va="center", fontsize=9)
ax.annotate("", xy=(-5.4, 0.05), xytext=(-5.4, NP - 0.05), arrowprops=dict(arrowstyle="-|>", color=MUTED))
ax.text(-5.9, NP / 2, "frekans: her PRB = 12 şerit alt alta", rotation=90, ha="center", va="center", color=MUTED, fontsize=9)
ax.annotate("", xy=(NS * SYM, -0.5), xytext=(0, -0.5), arrowprops=dict(arrowstyle="-|>", color=MUTED))
ax.text(NS * SYM / 2, -0.95, "zaman", ha="center", color=MUTED, fontsize=9)

ax.add_patch(Rectangle((0.5, -1.9), 1, 0.5, fc=RED, ec="none")); ax.text(2, -1.65, "PRS'in gerçekten kullandığı semboller (burada 4)", va="center", fontsize=8.5)
ax.add_patch(Rectangle((22.5, -1.9), 1, 0.5, fc="#FECACA", ec="none")); ax.text(24, -1.65, "PRS yüzünden iletişime kapalı kalan (slot boyunca)", va="center", fontsize=8.5)
ax.set_title("Kayıp = kapanan kutu / toplam kutu.  Kutu = bir PRB × bir slot", loc="left", fontsize=11.5, fontweight="bold")
ax.text(NS * SYM, NP + 1.55, "toplam: 4 slot × 8 PRB = 32 kutu    kapanan: 1 slot × 4 PRB = 4 kutu    kayıp = 4/32 = %12,5", ha="right", fontsize=10, fontweight="bold", color=RED)
fig.savefig(os.path.join(HERE, "prb_slot_say.png"), dpi=140, bbox_inches="tight", facecolor="white")
print("tamam")

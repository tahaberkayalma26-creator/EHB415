"""CORESET0 (TS 38.213 Tablo 13-1, Index 12: 96 PRB, 1 sembol, offset 38) ve SS/PBCH blogu, yalniz FREKANS ekseninde.
Offset tanimi (TS 38.213 sec.13): "from the smallest RB index of the CORESET for Type0-PDCCH CSS set to the smallest RB index of the
common RB overlapping with the first RB of the corresponding SS/PBCH block".
SS/PBCH blogunun 20 PRB oldugu GENEL BILGI (TS 38.211'den dogrulanmadi). Iki blok zamanda ayri (pattern 1); sekil yalniz frekanstaki yerlerini gosterir.
Calistirma: python coreset0_offset.py -> coreset0_offset.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTED, GRID, ACC, RED = "#1F2937", "#6B7280", "#D1D5DB", "#2563EB", "#DC2626"
plt.rcParams.update({"font.size": 10, "text.color": INK, "axes.edgecolor": GRID})

NRB, OFF, SSB = 96, 38, 20
fig, ax = plt.subplots(figsize=(8.2, 7.4))
ax.add_patch(Rectangle((5.5, 0), 2.2, NRB, fc="#DBEAFE", ec=ACC, lw=2))
ax.text(6.6, NRB - 4, "CORESET0", ha="center", fontweight="bold", color=ACC)
ax.text(6.6, NRB - 9, "96 PRB yükseklik\n1 sembol genişlik", ha="center", fontsize=9, color=ACC, va="top")
ax.add_patch(Rectangle((1.0, OFF), 2.2, SSB, fc="#FEE2E2", ec=RED, lw=2))
ax.text(2.1, OFF + SSB / 2, "SS/PBCH\nbloğu\n(20 PRB)", ha="center", va="center", fontsize=9, color=RED, fontweight="bold")
ax.plot([5.5, 0.2], [0, 0], color=MUTED, ls="--", lw=1)
ax.plot([3.2, 5.5], [OFF, OFF], color=MUTED, ls="--", lw=1)
ax.annotate("", xy=(4.4, OFF), xytext=(4.4, 0), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.8))
ax.text(4.25, OFF / 2, "offset = 38 PRB", va="center", ha="right", fontweight="bold")
ax.text(0.2, -2.2, "CORESET0'ın en alt PRB'si", fontsize=8.5, color=MUTED, va="top")
ax.set_xlim(0, 9); ax.set_ylim(-8, 104); ax.set_xticks([])
ax.set_ylabel("frekans (PRB numarası, aşağıdan yukarı)")
ax.set_title("Offset: CORESET0'ın en alt PRB'sinden, SS/PBCH bloğunun en alt PRB'sine olan uzaklık", loc="left", fontsize=10.5, fontweight="bold")
ax.text(4.5, -6.2, "iki blok zamanda ayrı yerlerde; şekil yalnız frekanstaki yerlerini gösteriyor", ha="center", fontsize=8.5, color=MUTED)
fig.savefig(os.path.join(HERE, "coreset0_offset.png"), dpi=140, bbox_inches="tight", facecolor="white")
print("tamam")

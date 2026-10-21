"""OCUDU kaynak izgarasi filmi: gercek scheduler log'undan (veri/ocudu_slot_serit.csv) slot slot izgara cizer.
Uretilenler:  sekiller/ocudu_izgara_filmi.gif   (animasyon)
              sekiller/fig_izgara_kareler.pdf/png (8 slotluk kareler seridi, ogretici icin)
Cizilenler (gercek log'dan): PDSCH dikdortgeni (prb, sembol araligi, TBS).
Cizilenler (yapilandirmadan): PRS dikdortgeni (periyot 4, slot ofseti 1, 12 sembol, ofset 2, 104 PRB).
Calistirma: python betikler/izgara_filmi.py   (numpy, matplotlib, pandas, pillow)
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation, PillowWriter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "sekiller")
d = pd.read_csv(os.path.join(ROOT, "veri", "ocudu_slot_serit.csv"), dtype={"slot": str})

NPRB, NSYM = 106, 14
PRS_PER, PRS_OFS, PRS_SYM0, PRS_NSYM, PRS_BW = 4, 1, 2, 12, 104     # ocudu_p4_config.yml
INK = "#1f2937"; MUTED = "#6b7280"; BLUE = "#2563eb"; ORANGE = "#ea580c"; GRAYG = "#e5e7eb"

def abs_slot(s):
    fr, sl = s.split(".")
    return int(fr) * 10 + int(sl)

d["abs"] = d.slot.map(abs_slot)
d["prs"] = (d["abs"] % PRS_PER) == PRS_OFS
# dogrulama: yapilandirmadan beklenen PRS slotlari = log'da PDSCH'nin olmadigi slotlar
assert ((d.pdsch_sayisi == 0) == d.prs).all(), "PRS slotlari log ile uyusmuyor"

def draw_slot(ax, r, kucuk=False):
    ax.set_xlim(0, NSYM); ax.set_ylim(0, NPRB)
    ax.add_patch(Rectangle((0, 0), NSYM, NPRB, fc="white", ec=MUTED, lw=0.8))
    # sembol 0: PDSCH baslamiyor (kontrol alani)
    ax.add_patch(Rectangle((0, 0), 1, NPRB, fc="#dcfce7", ec="none"))
    if r.prs:
        ax.add_patch(Rectangle((PRS_SYM0, 0), PRS_NSYM, PRS_BW, fc=ORANGE, ec="#9a3412", lw=1.2, alpha=0.95))
        if not kucuk:
            ax.text(PRS_SYM0 + PRS_NSYM / 2, PRS_BW / 2, "PRS\n104 PRB x 12 sembol\nveriye yer yok", ha="center",
                    va="center", color="white", fontsize=12, fontweight="bold")
        else:
            ax.text(PRS_SYM0 + PRS_NSYM / 2, PRS_BW / 2, "PRS", ha="center", va="center", color="white",
                    fontsize=9, fontweight="bold", rotation=90)
    elif r.pdsch_prb > 0:
        ax.add_patch(Rectangle((r.sembol_bas, 0), r.sembol_bit - r.sembol_bas, r.pdsch_prb, fc=BLUE, ec="#1e3a8a", lw=1.0, alpha=0.9))
        if not kucuk:
            ax.text((r.sembol_bas + r.sembol_bit) / 2, r.pdsch_prb / 2,
                    f"PDSCH (kullanıcı verisi)\n{int(r.pdsch_prb)} PRB x {int(r.sembol_bit - r.sembol_bas)} sembol\nTBS = {int(r.tbs_bayt)} bayt",
                    ha="center", va="center", color="white", fontsize=12, fontweight="bold")
    ax.set_xticks(np.arange(NSYM) + 0.5)
    ax.set_xticklabels([str(i) for i in range(NSYM)], fontsize=7 if kucuk else 8)
    ax.set_yticks([0, 53, 106] if kucuk else [0, 20, 40, 60, 80, 100, 106])
    ax.tick_params(labelsize=7 if kucuk else 8)
    ax.grid(False)

# ------------------------------------------------ 8 slotluk kareler seridi (PDF/PNG)
def kareler():
    sec = d.iloc[0:8]
    fig, axs = plt.subplots(2, 4, figsize=(8.6, 5.4), sharey=True)
    for ax, (_, r) in zip(axs.ravel(), sec.iterrows()):
        draw_slot(ax, r, kucuk=True)
        durum = "PRS: veri yok" if r.prs else (f"{int(r.pdsch_prb)} PRB, {int(r.tbs_bayt)} B" if r.pdsch_prb else "-")
        ax.set_title(f"slot {r.slot}\n{durum}", fontsize=8.5, color=ORANGE if r.prs else INK)
    for ax in axs[:, 0]:
        ax.set_ylabel("PRB (frekans)", fontsize=8)
    for ax in axs[1, :]:
        ax.set_xlabel("OFDM sembolü (zaman)", fontsize=8)
    fig.suptitle("Gerçek OCUDU log'undan 8 ardışık slot: her kare bir 1 ms'lik ızgara", fontsize=10.5, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(OUT, "fig_izgara_kareler.pdf"), bbox_inches="tight", dpi=200)
    fig.savefig(os.path.join(OUT, "fig_izgara_kareler.png"), bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("ok fig_izgara_kareler")

# ------------------------------------------------ animasyonlu GIF
def film():
    fig = plt.figure(figsize=(8.0, 6.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[5, 1.1], hspace=0.38)
    ax = fig.add_subplot(gs[0]); ax2 = fig.add_subplot(gs[1])
    n = len(d)
    def kare(i):
        ax.clear(); ax2.clear()
        r = d.iloc[i]
        draw_slot(ax, r)
        ax.set_xlabel("OFDM sembolü (zaman, 1 slot = 14 sembol = 1 ms)", fontsize=9)
        ax.set_ylabel("PRB (frekans, toplam 106)", fontsize=9)
        ax.set_title(f"OCUDU gNB, slot {r.slot}   (şu an: {i + 1}/{n})", fontsize=12, color=ORANGE if r.prs else INK, loc="left")
        # alt serit: o ana kadar gecen slotlar
        sub = d.iloc[: i + 1]
        cols = [ORANGE if p else BLUE for p in sub.prs]
        ax2.bar(range(len(sub)), np.where(sub.prs, 106, sub.pdsch_prb), color=cols, width=0.85)
        ax2.set_xlim(-0.5, n - 0.5); ax2.set_ylim(0, 115)
        ax2.set_xticks([]); ax2.set_yticks([0, 106]); ax2.tick_params(labelsize=7)
        veri = int(sub.pdsch_sayisi.sum())
        kbit = sub.tbs_bayt.sum() * 8 / 1000
        ax2.set_title(f"geçen slotlar: veri giden {veri}/{len(sub)}   |   toplam gönderilen {kbit:,.0f} kbit".replace(",", "."),
                      fontsize=9, loc="left", color=INK)
        ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
    anim = FuncAnimation(fig, kare, frames=n, interval=500)
    yol = os.path.join(OUT, "ocudu_izgara_filmi.gif")
    anim.save(yol, writer=PillowWriter(fps=2))
    plt.close(fig)
    print("ok", yol, round(os.path.getsize(yol) / 1024), "KB")

if __name__ == "__main__":
    kareler(); film()

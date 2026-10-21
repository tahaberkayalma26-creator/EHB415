"""OCUDU cok kullanicili izgara filmi: 4 UE, PRS her 4 slotta bir (veri/ocudu_cok_ue_slot.csv, gercek log).
Uretilenler: sekiller/ocudu_cok_ue_filmi.gif, sekiller/fig_cok_ue_kareler.pdf/png
Calistirma: python betikler/ocudu_cok_ue_film.py  (numpy, matplotlib, pandas, pillow)
"""
import os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation, PillowWriter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
d = pd.read_csv(os.path.join(ROOT, "veri", "ocudu_cok_ue_slot.csv"))
d["abs"] = d.sfn * 10 + d.slot
rntis = sorted(d.rnti.unique())
RENK = {r: c for r, c in zip(rntis, ["#2563eb", "#16a34a", "#9333ea", "#0891b2", "#be185d", "#65a30d"])}
ORANGE = "#ea580c"; INK = "#1f2937"
ilk = int(d["abs"].min())
# ardisik 40 slot pencere: ilk tam pencere
slotlar = list(range(ilk, ilk + 40))
PRS_PER, PRS_OFS = 4, 1
def kare_veri(a):
    return d[d["abs"] == a]

def ciz(ax, a, kucuk=False):
    ax.set_xlim(0, 14); ax.set_ylim(0, 106)
    ax.add_patch(Rectangle((0, 0), 14, 106, fc="white", ec="#6b7280", lw=0.8))
    ax.add_patch(Rectangle((0, 0), 1, 106, fc="#dcfce7", ec="none"))
    prs = (a % PRS_PER) == PRS_OFS
    if prs:
        ax.add_patch(Rectangle((2, 0), 12, 104, fc=ORANGE, ec="#9a3412", lw=1.2, alpha=0.95))
        ax.text(8, 52, "PRS" if kucuk else "PRS\nhiçbir kullanıcıya yer yok", ha="center", va="center", color="white",
                fontsize=9 if kucuk else 13, fontweight="bold", rotation=90 if kucuk else 0)
    else:
        for _, r in kare_veri(a).iterrows():
            ax.add_patch(Rectangle((r.sym_lo, r.prb_lo), r.sym_hi - r.sym_lo, r.prb_hi - r.prb_lo,
                                   fc=RENK[r.rnti], ec="white", lw=1.2, alpha=0.92))
            if not kucuk or (r.prb_hi - r.prb_lo) > 20:
                ax.text((r.sym_lo + r.sym_hi) / 2, (r.prb_lo + r.prb_hi) / 2, f"UE {r.rnti}\n{int(r.prb_hi - r.prb_lo)} PRB",
                        ha="center", va="center", color="white", fontsize=7 if kucuk else 11, fontweight="bold")
    ax.set_xticks([0, 7, 13] if kucuk else range(14)); ax.set_yticks([0, 53, 106] if kucuk else [0, 20, 40, 60, 80, 100, 106])
    ax.tick_params(labelsize=7 if kucuk else 8); ax.grid(False)

def kareler():
    sec = slotlar[:8]
    fig, axs = plt.subplots(2, 4, figsize=(8.6, 5.4), sharey=True)
    for ax, a in zip(axs.ravel(), sec):
        ciz(ax, a, kucuk=True)
        ues = kare_veri(a)
        ax.set_title(f"slot {a // 10}.{a % 10}\n" + ("PRS: veri yok" if (a % PRS_PER) == PRS_OFS else f"{len(ues)} UE"),
                     fontsize=8.5, color=ORANGE if (a % PRS_PER) == PRS_OFS else INK)
    for ax in axs[:, 0]: ax.set_ylabel("PRB (frekans)", fontsize=8)
    for ax in axs[1, :]: ax.set_xlabel("OFDM sembolü (zaman)", fontsize=8)
    fig.suptitle("Gerçek OCUDU log'u: 4 kullanıcı bir ızgarayı slot slot paylaşıyor", fontsize=10.5, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    for e in ("pdf", "png"):
        fig.savefig(os.path.join(ROOT, "sekiller", f"fig_cok_ue_kareler.{e}"), bbox_inches="tight", dpi=200)
    plt.close(fig); print("ok kareler")

def film():
    fig = plt.figure(figsize=(8.2, 6.4)); gs = fig.add_gridspec(2, 1, height_ratios=[4.6, 1.5], hspace=0.42)
    ax = fig.add_subplot(gs[0]); ax2 = fig.add_subplot(gs[1])
    def kare(i):
        ax.clear(); ax2.clear()
        a = slotlar[i]
        ciz(ax, a)
        ax.set_title(f"OCUDU gNB, slot {a // 10}.{a % 10}   (4 test UE; {i + 1}/{len(slotlar)})", fontsize=11, loc="left",
                     color=ORANGE if (a % PRS_PER) == PRS_OFS else INK)
        ax.set_xlabel("OFDM sembolü (zaman)", fontsize=9); ax.set_ylabel("PRB (frekans)", fontsize=9)
        sub = d[(d["abs"] >= slotlar[0]) & (d["abs"] <= a)]
        top = sub.groupby("rnti").tbs_bayt.sum() * 8 / 1000
        x = np.arange(len(rntis))
        ax2.bar(x, [top.get(r, 0) for r in rntis], color=[RENK[r] for r in rntis], width=0.6)
        ax2.set_xticks(x); ax2.set_xticklabels([f"UE {r}" for r in rntis], fontsize=9)
        ax2.set_ylim(0, 40 * 64 * 0.9 * 0.25 + 100)
        ax2.set_ylabel("o ana kadar\ngönderilen (kbit)", fontsize=8)
        ax2.set_title("kullanıcı başına toplam: scheduler herkese yaklaşık eşit pay veriyor", fontsize=9, loc="left")
        for s in ("top", "right"): ax2.spines[s].set_visible(False)
    FuncAnimation(fig, kare, frames=len(slotlar), interval=500).save(
        os.path.join(ROOT, "sekiller", "ocudu_cok_ue_filmi.gif"), writer=PillowWriter(fps=2))
    plt.close(fig); print("ok film")

if __name__ == "__main__":
    kareler(); film()

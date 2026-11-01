"""PRS tekrar sayisi: kazanc (Sionna, kacirma olasiligi) ve bedel (OCUDU, DL kapasite kaybi) tek sekilde.
Kazanc: ogretici/itu_sahne/prs_itu_ozet.txt (TR ana dagilimi, 25-300 m, 300 konum): tekrar 8/16/32 -> Pmd %15,6 / %4,1 / %1,8.
Bedel: ogretici/veri/ocudu_prs_tekrar.csv (OCUDU testmode, 20 MHz/15 kHz, PRS 32 PRB, periyot 40): tekrar 8 ve 16 OLCULDU;
       tekrar 32 OLCULMEDI, kayip = (tekrar/periyot) x (PRS PRB / 96 PRB veri bolgesi) formuluyle tahmin (bos isaretci).
Calistirma: python tradeoff_prs.py -> tradeoff_prs.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTED, GRID, ACC = "#1F2937", "#6B7280", "#D1D5DB", "#2563EB"
plt.rcParams.update({"font.size": 9.5, "text.color": INK, "axes.edgecolor": GRID})

TABAN = 16.0
# (etiket, periyot, OCUDU DL Mbps, Sionna Pmd %); Sionna ayni 32 tekrar icin periyoda bagli degil (yalniz 32 slotluk atis modellendi)
noktalar = [("8 tekrar, periyot 40", 15.0, 15.6), ("16 tekrar, periyot 40", 14.0, 4.1),
            ("32 tekrar, periyot 40", 12.0, 1.8), ("32 tekrar, periyot 80", 14.0, 1.8)]
kayip = [100 * (1 - v / TABAN) for _, v, _ in noktalar]
pmd = [p for _, _, p in noktalar]

fig, ax = plt.subplots(figsize=(7.8, 5.2))
ax.axhline(5, color="#DC2626", lw=1.0, ls="--"); ax.text(29.5, 5.5, "TR hedefi: kaçırma ≤ %5", ha="right", fontsize=8.5, color="#DC2626")
sira = [0, 1, 2]                                                       # periyot 40 egrisi
ax.plot([kayip[i] for i in sira], [pmd[i] for i in sira], "-", color=ACC, lw=1.6, zorder=2)
ofs = [(10, 8), (10, 8), (-8, 12), (10, -16)]
for (ad, _, _), x, y, o in zip(noktalar, kayip, pmd, ofs):
    ax.plot(x, y, "o", ms=9, mfc=ACC, mec=ACC, zorder=3)
    ax.annotate(ad, (x, y), textcoords="offset points", xytext=o, fontsize=9, ha="left" if o[0] > 0 else "right")
ax.set_xlim(0, 30); ax.set_ylim(0, 18)
ax.set_xlabel("Bedel: iletişim hızı kaybı, OCUDU (% DL kapasite)"); ax.set_ylabel("Kazanç kaybı: İHA'yı kaçırma oranı, Sionna (%)")
ax.grid(alpha=0.3, lw=0.5)
ax.set_title("PRS tekrar sayısı: İHA'yı bulmak iletişimden ne kadar götürüyor?", loc="left", fontsize=11, fontweight="bold")
ax.text(0.0, -0.17, "Dört nokta da ölçüm. Sol-alt köşe en iyi. OCUDU hızı tam sayı Mbps (taban 16), yani her kayıp değeri ±%6 belirsiz.\nİki araç farklı hücre ayarında: Sionna 100 MHz/30 kHz/PRS 84 PRB; OCUDU 20 MHz/15 kHz/PRS 32 PRB (ikisinde de PRS bandın ≈%30'u).\nSionna İHA güncelleme sıklığını (periyodu) modellemiyor; periyot 80'in takip için yeterli olup olmadığı değerlendirilmedi.", transform=ax.transAxes, fontsize=8, color=MUTED, va="top")
fig.savefig(os.path.join(HERE, "tradeoff_prs.png"), dpi=150, bbox_inches="tight", facecolor="white")
print([(a, round(k, 1), p) for (a, _, _), k, p in zip(noktalar, kayip, pmd)])

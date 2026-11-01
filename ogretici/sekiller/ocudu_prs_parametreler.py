"""OCUDU PRS yapilandirma parametrelerini zaman-frekans izgarasi uzerinde gosterir.
Parametre adlari ve izinli degerler: OCUDU apps/units/flexible_o_du/o_du_high/du_high/du_high_config.h (satir 1128-1174).
PRS satir/sembol deseni: lib/phy/upper/signal_processors/prs/prs_generator_impl.cpp (row_4 = {0,2,1,3}).
'Veriye kapanan serit': bu oturumdaki OCUDU olcumumuz (52 PRB, 4 ve 12 sembol ayni hizi verdi), kaynak kodundan alinti degil.
Calistirma: python ocudu_prs_parametreler.py   -> ocudu_prs_parametreler.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.gridspec import GridSpec

HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTED, GRID = "#1F2937", "#6B7280", "#D1D5DB"
PRS = ["#BFDBFE", "#60A5FA", "#2563EB", "#1E3A8A"]        # tek renk, acik -> koyu: kacinci PRS sembolu
KAPALI = "#E5E7EB"                                           # veriye kapanan serit
plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "text.color": INK})

def ok(ax, a, b, txt=None, dy=0, ha="center", color=INK):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="<->", mutation_scale=9, lw=1.0, color=color, shrinkA=0, shrinkB=0))
    if txt: ax.text((a[0] + b[0]) / 2 if ha == "center" else b[0] + 0.3, (a[1] + b[1]) / 2 + dy, txt, ha=ha, va="center", fontsize=8.8, color=color)

fig = plt.figure(figsize=(13.2, 11.6))
gs = GridSpec(4, 1, height_ratios=[3.6, 0.95, 1.35, 1.2], hspace=0.42, figure=fig)

# ---------------------------------------------------------------- 1) tek slotun ici
ax = fig.add_subplot(gs[0]); ax.set_xlim(-3.4, 21.0); ax.set_ylim(-9.0, 30.0); ax.axis("off")
COMB, NSYM, SOFF, ROW, NSC = 4, 4, 2, [0, 2, 1, 3], 24     # 2 PRB gosterildi
ax.add_patch(Rectangle((1, 0), 13, NSC, fc=KAPALI, ec="none", zorder=0))
for s in range(14):
    for k in range(NSC):
        ax.add_patch(Rectangle((s + 0.04, k + 0.04), 0.92, 0.92, fc="white" if s == 0 else "none", ec=GRID, lw=0.4, zorder=1))
for j in range(NSYM):
    for i in range(NSC // COMB):
        ax.add_patch(Rectangle((SOFF + j + 0.04, COMB * i + ROW[j] + 0.04), 0.92, 0.92, fc=PRS[j], ec="none", zorder=2))
ax.text(0.5, NSC / 2, "kontrol\n(slot başı)", ha="center", va="center", fontsize=8, color=MUTED, zorder=5, bbox=dict(fc="white", ec="none", pad=1.5))
for s in range(14): ax.text(s + 0.5, -0.7, str(s), ha="center", va="top", fontsize=8, color=MUTED)
ax.text(7.5, -2.7, "OFDM sembolü (bir slotta 14 tane)", ha="center", va="top", fontsize=8.8, color=MUTED)
ok(ax, (0, -5.0), (SOFF, -5.0), "symbol_offset: 2", dy=-1.5)
ax.text(7.5, -7.8, "gri bölge = veri bölgesi (sembol 1–13). OCUDU zamanlayıcı, PRS'in dokunduğu şeritleri bu bölgenin TÜM sembollerinde veriye kapatıyor\n(bizim ölçümümüz: PRS 4 sembol de olsa 12 sembol de olsa aynı kayıp; kaynak kodundan alıntı değil)", ha="center", va="top", fontsize=8.2, color=MUTED)
ok(ax, (SOFF, NSC + 2.2), (SOFF + NSYM, NSC + 2.2), "nof_symbols: 4", dy=1.5)
for x in (SOFF, SOFF + NSYM): ax.plot([x, x], [NSC + 1.5, NSC + 2.9], color=INK, lw=0.8)
# comb_size: sembol 2'deki iki dis arasi
xc = SOFF + 6.3
for y in (4.5, 8.5): ax.plot([SOFF + 1, xc + 0.2], [y, y], color=GRID, lw=0.8, ls=":")
ok(ax, (xc, 4.5), (xc, 8.5)); kutu = dict(fc="white", ec="none", pad=2.5, alpha=0.92)
ax.text(xc + 0.5, 6.5, "comb_size: 4  (iki PRS dişi arası 4 şerit)", ha="left", va="center", fontsize=8.8, bbox=kutu, zorder=6)
ax.text(xc + 0.2, 16.5, "her sembolde tarak 1 kayar\n(0, 2, 1, 3): 4 sembol sonunda\ntüm şeritler bir kez kullanılmış\nolur (açık maviden koyuya:\n1., 2., 3., 4. PRS sembolü)", ha="left", va="center", fontsize=8.2, color=MUTED, bbox=kutu, zorder=6)
# sol: bandwidth_prbs, sag: PRB
ok(ax, (-0.9, 0), (-0.9, NSC))
ax.text(-1.9, NSC / 2, "bandwidth_prbs  (burada 2 PRB gösterildi;\ngerçekte 24–272 PRB, örn. 84)", rotation=90, ha="center", va="center", fontsize=8.8)
for a, b in ((0, 12), (12, 24)):
    ok(ax, (14.6, a + 0.15), (14.6, b - 0.15)); ax.text(14.95, (a + b) / 2, "1 PRB = 12 şerit", ha="left", va="center", fontsize=8.2, color=MUTED)
ax.set_title("1) Bir slotun içi: PRS hangi kutulara konuyor?", loc="left", fontsize=11, fontweight="bold", color=INK)

# ---------------------------------------------------------------- 2) carrier icinde bant
axc = fig.add_subplot(gs[1]); axc.set_xlim(0, 273); axc.set_ylim(-1.6, 2.4); axc.axis("off")
axc.add_patch(Rectangle((0, 0), 273, 1, fc=KAPALI, ec=GRID, lw=0.6))
axc.add_patch(Rectangle((0, 0), 84, 1, fc=PRS[2], ec="none"))
axc.text(42, 0.5, "PRS bandı", ha="center", va="center", color="white", fontsize=8.8, fontweight="bold")
axc.text(178, 0.5, "veri bu şeritlerde sürer (PRS'li slotta)", ha="center", va="center", color=MUTED, fontsize=8.8)
ok(axc, (0, -0.7), (84, -0.7), "bandwidth_prbs: 84", dy=-0.6)
axc.text(88, -0.7, "start_prb: 0 (varsayılan; PRS bandın başından başlar)", ha="left", va="center", fontsize=8.2, color=MUTED)
ok(axc, (0, 1.7), (273, 1.7)); axc.text(136, 2.0, "taşıyıcı: 100 MHz, 30 kHz aralıkta 273 PRB (TR 38.765 ana senaryosu: 100 MHz, 30 kHz)", ha="center", va="bottom", fontsize=8.2, color=MUTED)
axc.set_title("2) Frekans yönü: PRS bandın ne kadarını kaplıyor?", loc="left", fontsize=11, fontweight="bold", color=INK, pad=22)

# ---------------------------------------------------------------- 3) slotlar arasi zaman
def zaman(ax, n, prs, baslik, notlar, ylim):
    ax.set_xlim(-2.5, n + 1.0); ax.set_ylim(*ylim); ax.axis("off")
    for s in range(n):
        ax.add_patch(Rectangle((s + 0.05, 0), 0.9, 1, fc=PRS[2] if s in prs else "white", ec=GRID, lw=0.6))
    ax.text(-0.4, 0.5, "slot", ha="right", va="center", fontsize=8.2, color=MUTED)
    for s in range(0, n, 4): ax.text(s + 0.5, -0.25, str(s), ha="center", va="top", fontsize=7.5, color=MUTED)
    notlar(ax)
    ax.set_title(baslik, loc="left", fontsize=10.5, fontweight="bold", color=INK)

def not1(ax):                                              # sematik: periyot 16, offset 2, tekrar 4, bosluk 2
    ok(ax, (0, 1.7), (2, 1.7)); ax.text(2.4, 1.7, "slot_offset: 2  (periyodun başından PRS'e kadar)", ha="left", va="center", fontsize=8.8)
    ok(ax, (2, 3.4), (9, 3.4)); ax.text(9.4, 3.4, "repetition_factor: 4  (grupta 4 PRS slotu)", ha="left", va="center", fontsize=8.8)
    ok(ax, (2.5, -1.9), (4.5, -1.9)); ax.text(5.0, -1.9, "time_gap: 2  (iki PRS slotu arası)", ha="left", va="center", fontsize=8.8)
    ok(ax, (2, -3.4), (18, -3.4)); ax.text(10, -4.1, "periodicity_slots: 16  (bir grubun başından sonrakinin başına)", ha="center", va="center", fontsize=8.8)
zaman(fig.add_subplot(gs[2]), 34, {2, 4, 6, 8, 18, 20, 22, 24}, "3a) Slotlar arası zaman düzeni, şematik örnek (değerler öğretmek için seçildi)", not1, (-4.9, 4.3))

def not2(ax):                                              # bizim Sionna ayari: periyot 40, offset 0, tekrar 16, bosluk 1
    ok(ax, (0, 1.7), (16, 1.7)); ax.text(16.4, 1.7, "repetition_factor: 16  (art arda 16 PRS slotu; time_gap: 1)", ha="left", va="center", fontsize=8.8)
    ok(ax, (0, -1.3), (40, -1.3)); ax.text(20, -2.0, "periodicity_slots: 40  (bir grubun başından sonrakinin başına; 40 örnek bir değer)", ha="center", va="center", fontsize=8.8)
zaman(fig.add_subplot(gs[3]), 46, set(range(0, 16)) | set(range(40, 46)), "3b) Sionna'da kullandığımız PRS'in OCUDU karşılığı (tekrar 16, boşluk 1)", not2, (-2.8, 2.5))

fig.savefig(os.path.join(HERE, "ocudu_prs_parametreler.png"), dpi=150, bbox_inches="tight", facecolor="white")
print("tamam")

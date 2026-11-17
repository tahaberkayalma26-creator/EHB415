"""PRS yerlesimini gorsel anlatan 4 sekil (ortak izgara: 30 kHz, 100 MHz, 273 PRB, TDD).
prs_re_comb.png   : bir PRB icinde PRS'in alt tasiyici x sembol deseni (comb 2/4/6/12)   [KAYNAK: OCUDU lib/ran/prs/prs.cpp get_prs_freq_offset]
prs_zaman.png     : 40 slotluk zaman cizgisi: TDD deseni + OCUDU varsayilani + K1/K2/K3     [KAYNAK: du_high_config.h varsayilanlari, TDD varsayilani; K'lar ortak_degerler.xlsx]
prs_frekans.png   : PRB ekseninde kim nerede (hucre, veri, CORESET0, PRS genislikleri)       [OLCUM: PDSCH [0..48) ocudu_veri_genislik.sh; CORESET0 genisligi 48 = ON GOZLEM]
prs_re_acik.png    : PRS'in bos kutulari veriye acilirsa kapanan pay (hesap: sembol / (13 x comb), ust sinir)   [TURETME]
prs_slot_ici.png  : bir slotun icinde PRS ofseti 0/2/10 ve 'kapanan' bolge                      [OLCUM: ofset/sembol sayisi DL'i degistirmedi (kart 2, Fatih); KAYNAK: intra_slice_scheduler.cpp]
Calistirma: python prs_gorsel.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch

HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTED, GRID = "#1F2937", "#6B7280", "#D1D5DB"
PRS, CLOSED, CTRL, DATA, UL = "#DC2626", "#FECACA", "#93C5FD", "#E5E7EB", "#FDE68A"
plt.rcParams.update({"font.size": 10, "text.color": INK, "axes.edgecolor": GRID})

OFFS = {2: [0, 1], 4: [0, 2, 1, 3], 6: [0, 3, 1, 4, 2, 5], 12: [0, 6, 3, 9, 1, 7, 4, 10, 2, 8, 5, 11]}   # prs.cpp
NPRB, PDSCH_W = 273, 48

# ------------------------------------------------------------------ 1) RE deseni
fig, axs = plt.subplots(1, 4, figsize=(15, 4.6))
for ax, (comb, nsym) in zip(axs, [(2, 4), (4, 4), (6, 6), (12, 12)]):
    ofs = 2
    for s in range(14):
        for k in range(12):
            fc = "white"
            if s == 0: fc = CTRL
            if ofs <= s < ofs + nsym and (k - OFFS[comb][(s - ofs) % comb]) % comb == 0: fc = PRS
            ax.add_patch(Rectangle((s, k), 1, 1, fc=fc, ec=GRID, lw=0.6))
    ax.set_xlim(0, 14); ax.set_ylim(0, 12); ax.set_aspect("equal")
    ax.set_xticks([x + 0.5 for x in range(14)]); ax.set_xticklabels(range(14), fontsize=7)
    ax.set_yticks([y + 0.5 for y in range(12)]); ax.set_yticklabels(range(12), fontsize=7)
    ax.set_title(f"comb {comb}, {nsym} sembol", fontweight="bold", loc="left")
    ax.set_xlabel("sembol (zaman)")
axs[0].set_ylabel("alt taşıyıcı (1 PRB = 12)")
fig.legend(handles=[Patch(fc=PRS, label="PRS'in gerçekten doldurduğu kutu"), Patch(fc=CTRL, label="PDCCH sembolü (sembol 0)"), Patch(fc="white", ec=GRID, label="PRS'in boş bıraktığı kutu")],
           loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.04))
fig.suptitle("Bir PRB'nin içi: comb = PRS her kaç alt taşıyıcıdan birini dolduruyor (sembol ofseti 2)", x=0.01, ha="left", fontweight="bold")
fig.savefig(os.path.join(HERE, "prs_re_comb.png"), dpi=140, bbox_inches="tight", facecolor="white"); plt.close(fig)

# ------------------------------------------------------------------ 2) zaman cizgisi (40 slot)
N = 40
satirlar = [("TDD deseni", None, None), ("OCUDU varsayılanı\n(her 160 slot, ofset 0)", 160, 0),
            ("K1: her 10 slot (5 ms)", 10, 1), ("K2: her 20 slot (10 ms)", 20, 1), ("K3: her 40 slot (20 ms)", 40, 1)]
fig, ax = plt.subplots(figsize=(15, 3.9))
for r, (ad, per, so) in enumerate(satirlar):
    y = len(satirlar) - 1 - r
    for s in range(N):
        if per is None:
            m = s % 10; fc, tx = (DATA, "D") if m < 6 else ((CTRL, "S") if m == 6 else (UL, "U"))
        else:
            fc, tx = ("white", "")
            if (s - so) % per == 0: fc, tx = PRS, "P"
        ax.add_patch(Rectangle((s, y), 1, 0.8, fc=fc, ec=GRID, lw=0.6))
        if tx: ax.text(s + 0.5, y + 0.4, tx, ha="center", va="center", fontsize=8, color="white" if tx == "P" else INK)
    ax.text(-0.4, y + 0.4, ad, ha="right", va="center", fontsize=9)
ax.set_xlim(-12, N); ax.set_ylim(-0.3, len(satirlar)); ax.set_yticks([])
ax.set_xticks([s + 0.5 for s in range(0, N, 5)]); ax.set_xticklabels(range(0, N, 5)); ax.set_xlabel("slot numarası (1 slot = 0,5 ms, 40 slot = 20 ms)")
for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
ax.set_title("Zamanda PRS: P = PRS'in gönderildiği slot. D = indirme, S = karışık, U = yükleme slotu", loc="left", fontweight="bold")
fig.savefig(os.path.join(HERE, "prs_zaman.png"), dpi=140, bbox_inches="tight", facecolor="white"); plt.close(fig)

# ------------------------------------------------------------------ 3) frekans: kim nerede
kol = [("Hücre", 0, NPRB, "#F3F4F6"), ("Veri alanı\n(PDSCH)", 0, PDSCH_W, DATA), ("CORESET0\n(sembol 0)", 0, PDSCH_W, CTRL),
       ("K5\nbw 24", 0, 24, PRS), ("K1\nbw 48", 0, 48, PRS), ("K4\nbw 272", 0, 272, PRS), ("OCUDU\nvarsayılan\nbw 272", 0, 272, PRS)]
fig, ax = plt.subplots(figsize=(10, 6.2))
for i, (ad, lo, hi, fc) in enumerate(kol):
    ax.add_patch(Rectangle((i + 0.1, lo), 0.8, hi - lo, fc=fc, ec=INK, lw=1))
    ax.text(i + 0.5, hi + 4, f"{lo}–{hi}", ha="center", fontsize=9)
ax.axhline(PDSCH_W, color=MUTED, ls="--", lw=1)
ax.text(len(kol) + 0.05, PDSCH_W + 5, "veri alanının\nüst sınırı (48)", va="bottom", fontsize=9, color=MUTED)
ax.set_xlim(0, len(kol) + 1.8); ax.set_ylim(0, 295)
ax.set_xticks([i + 0.5 for i in range(len(kol))]); ax.set_xticklabels([k[0] for k in kol], fontsize=9)
ax.set_ylabel("PRB numarası (aşağıdan yukarı)")
ax.set_title("Frekansta kim nerede: PRS PRB 0'dan başlar, veri alanı yalnız ilk 48 PRB", loc="left", fontweight="bold")
fig.savefig(os.path.join(HERE, "prs_frekans.png"), dpi=140, bbox_inches="tight", facecolor="white"); plt.close(fig)

# ------------------------------------------------------------------ 4) slot ici: ofset 0 / 2 / 10 (K1: bw 48, 4 sembol)
fig, axs = plt.subplots(1, 3, figsize=(15, 5.4), sharey=True)
for ax, ofs in zip(axs, (0, 2, 10)):
    ax.add_patch(Rectangle((0, 0), 14, 120, fc="white", ec=GRID))
    ax.add_patch(Rectangle((0, 0), 14, PDSCH_W, fc=DATA, ec="none"))                       # veri alani
    ax.add_patch(Rectangle((1, 0), 13, PDSCH_W, fc=CLOSED, ec="none"))                     # kapanan: PDSCH sembolleri 1-13
    ax.add_patch(Rectangle((0, 0), 1, PDSCH_W, fc=CTRL, ec="none"))                        # CORESET0
    ax.add_patch(Rectangle((ofs, 0), 4, PDSCH_W, fc=PRS, ec="none", alpha=0.95))           # PRS
    for s in range(15): ax.plot([s, s], [0, 120], color=GRID, lw=0.5)
    ax.axhline(PDSCH_W, color=MUTED, ls="--", lw=1)
    ax.text(14.1, PDSCH_W + 3, "PRB 48", fontsize=8, color=MUTED)
    ax.set_xlim(0, 14); ax.set_ylim(0, 120)
    ax.set_xticks([s + 0.5 for s in range(14)]); ax.set_xticklabels(range(14), fontsize=8); ax.set_xlabel("sembol (1 slot)")
    ax.set_title(f"sembol ofseti {ofs}" + ("  (PDCCH ile çakışır)" if ofs == 0 else ""), fontweight="bold", loc="left", color=PRS if ofs == 0 else INK)
axs[0].set_ylabel("PRB (grafik 0–120 gösteriyor, hücre 273)")
fig.legend(handles=[Patch(fc=PRS, label="PRS sembolleri (4 sembol, 48 PRB; 48 PRB = veri alanının tamamı)"), Patch(fc=CLOSED, label="PRS yüzünden veriye kapanan: PRS'in PRB'leri slotun tüm veri sembollerinde (1–13), o slotta veri kalmaz"),
                    Patch(fc=CTRL, label="CORESET0 / PDCCH (sembol 0)")],
           loc="lower center", ncol=1, frameon=False, bbox_to_anchor=(0.5, -0.17))
fig.suptitle("Bir PRS slotunun içi: PRS yalnız 4 sembol kullanır ama OCUDU o PRB'leri veri için tüm slot boyunca kapatır", x=0.01, ha="left", fontweight="bold")
fig.savefig(os.path.join(HERE, "prs_slot_ici.png"), dpi=140, bbox_inches="tight", facecolor="white"); plt.close(fig)

# ------------------------------------------------------------------ 5) PRS'in bos kutulari: simdi (PRB kapali) / RE duzeyi (bos kutular veriye acik)
OPEN = "#86EFAC"
fig, axs = plt.subplots(1, 3, figsize=(18, 5.0), gridspec_kw={"width_ratios": [1, 1, 1.2], "wspace": 0.65})
comb, nsym, ofs = 4, 4, 2
for ax, mod in zip(axs[:2], ("simdi", "re")):
    for s_ in range(14):
        for k in range(12):
            prs_re = ofs <= s_ < ofs + nsym and (k - OFFS[comb][(s_ - ofs) % comb]) % comb == 0
            if s_ == 0: fc = CTRL
            elif prs_re: fc = PRS
            else: fc = CLOSED if mod == "simdi" else OPEN
            ax.add_patch(Rectangle((s_, k), 1, 1, fc=fc, ec="white", lw=0.8))
    ax.set_xlim(0, 14); ax.set_ylim(0, 12); ax.set_aspect("equal")
    ax.set_xticks([x + 0.5 for x in range(14)]); ax.set_xticklabels(range(14), fontsize=7); ax.set_yticks([])
    ax.set_xlabel("sembol (zaman)")
axs[0].set_title("Şimdi (OCUDU): PRS'in PRB'si tamamen kapalı", loc="left", fontweight="bold", fontsize=10)
axs[1].set_title("Hedef: yalnız PRS'in kutuları kapalı", loc="left", fontweight="bold", fontsize=10)
axs[0].set_ylabel("1 PRB (12 alt taşıyıcı), K1: comb 4, 4 sembol")
ax = axs[2]
ornek = [("K1  comb 4, 4 sembol", 4, 4), ("K7  comb 2, 4 sembol", 4, 2), ("K6  comb 4, 12 sembol", 12, 4), ("K11 comb 6, 6 sembol", 6, 6), ("K8  comb 12, 12 sembol", 12, 12)]
for i, (ad, ns, cb) in enumerate(ornek):
    y = len(ornek) - 1 - i; deger = 100 * ns / (13 * cb)
    ax.barh(y, 100, color=CLOSED, height=0.6); ax.barh(y, deger, color=PRS, height=0.6)
    ax.text(deger + 1.5, y, f"%{deger:.1f}".replace(".", ","), va="center", fontsize=9, fontweight="bold")
ax.set_xlim(0, 108); ax.set_ylim(-0.6, len(ornek) - 0.4); ax.set_yticks(range(len(ornek))); ax.set_yticklabels([o[0] for o in ornek][::-1], fontsize=9); ax.tick_params(axis="y", length=0); ax.set_xlabel("PRS slotunda veriden kapanan pay (%)")
for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
ax.set_title("Açık pembe: şimdi %100. Kırmızı: hedefte (üst sınır)", loc="left", fontweight="bold", fontsize=10)
fig.legend(handles=[Patch(fc=PRS, label="PRS'in doldurduğu kutu"), Patch(fc=CLOSED, label="PRS yüzünden veriye kapalı"), Patch(fc=OPEN, label="PRS'in boş bıraktığı, veriye açık kutu"), Patch(fc=CTRL, label="PDCCH sembolü")],
           loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.06))
fig.suptitle("PRS'in boş bıraktığı kutular haberleşme için kullanılabilirse: kapanan pay nasıl düşer", x=0.01, ha="left", fontweight="bold")
fig.savefig(os.path.join(HERE, "prs_re_acik.png"), dpi=140, bbox_inches="tight", facecolor="white"); plt.close(fig)
print("tamam")

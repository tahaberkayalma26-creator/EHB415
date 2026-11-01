"""Radar IHA'yi yankidan nasil buluyor? Gercek kodumuzla (prs_takip.py) iki ornek: biri bulunur, biri kacirilir.
Her sutun tek bir radar denemesi (PRS 16 tekrar, RCS -12,81 dBsm, 37 dBm; radar_takip.py'deki radar denklemi ve esik):
  satir 1: tek tek olculen fazlar (gurultuyle)
  satir 2: bunlari toplayinca cikan mesafe profili + karar esigi (radar_takip.tespit ile ayni formul)
  satir 3: mesafe-hiz haritasi
Ornek secimi: 250 m'de tespit olasiligi yuksek (~0,9), 400 m'de dusuk (~0,1) oldugu icin tipik sonuclar gosterilir; tohum, bu tipik sonuclari verenler secildi.
Calistirma: python radar_nasil_bulur.py -> radar_nasil_bulur.png
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "sionna_sehir"))
import prs_takip as pt
rt = pt.rt
INK, MUTED, GRID, ACC = "#1F2937", "#6B7280", "#D1D5DB", "#2563EB"
plt.rcParams.update({"font.size": 9, "text.color": INK, "axes.edgecolor": GRID})

TEKRAR, V = 16, 12.0                                    # 16 PRS tekrari, gercek radyal hiz 12 m/s
ORNEK = [(250.0, "bulundu"), (400.0, "kaçırıldı")]

def dene(r, tohum):
    rng = np.random.default_rng(tohum)
    snr = rt.snr_ornek_db(r)
    rax, vax, P = pt.radar_prs(r, V, TEKRAR, snr, rng)
    ok, re, ve = rt.tespit(rax, vax, P, rmax=600.0)
    return snr, rax, vax, P, bool(ok and abs(re - r) < 10.0), re, ve

kutu = []
for r, istenen in ORNEK:
    for tohum in range(1, 60):
        s = dene(r, tohum)
        if s[4] == (istenen == "bulundu"): kutu.append((r, istenen, tohum, s)); break

fig, axs = plt.subplots(3, 2, figsize=(11.6, 10.4), gridspec_kw=dict(hspace=0.5, wspace=0.22))
for j, (r, istenen, tohum, (snr, rax, vax, P, dogru, re, ve)) in enumerate(kutu):
    renk = "#16A34A" if dogru else "#DC2626"
    # ---- satir 1: tek tek fazlar
    ax = axs[0, j]; rng = np.random.default_rng(tohum + 100)
    k = np.arange(0, 60); a = 10 ** (snr / 20)
    gercek = np.angle(np.exp(-1j * 2 * np.pi * k * pt.SCS * 2 * r / 3e8))
    olc = np.angle(a * np.exp(-1j * 2 * np.pi * k * pt.SCS * 2 * r / 3e8) + (rng.normal(size=k.size) + 1j * rng.normal(size=k.size)) / np.sqrt(2))
    ax.plot(k, gercek, "-", color=ACC, lw=1.0, alpha=0.7, label="gürültüsüz (gerçek) faz")
    ax.plot(k, olc, "o", color=INK, ms=3.2, label="gürültülü ölçülen faz")
    ax.set_ylim(-3.6, 3.6); ax.set_xlabel("şerit numarası (ilk 60)"); ax.set_ylabel("faz (radyan)")
    ax.legend(fontsize=7.5, loc="upper right", ncol=1, frameon=False)
    ax.set_title(f"İHA {r:.0f} m uzakta  →  {istenen.upper()}", loc="left", fontsize=11, fontweight="bold", color=renk)
    ax.text(0.01, 0.03, f"tek bir kutuda SNR = {snr:.0f} dB (sinyal gürültünün çok altında)", transform=ax.transAxes, fontsize=8, color=MUTED)
    # ---- satir 2: mesafe profili + esik
    ax = axs[1, j]; sel = rax < 450
    Pm = P[sel]; taban = np.median(Pm); prof = 10 * np.log10(Pm.max(axis=1) / taban)
    esik = 10 * np.log10((np.log(Pm.size) + np.log(1 / rt.PFA)) / np.log(2))
    ax.plot(rax[sel], prof, "-", color=ACC, lw=1.1)
    ax.axhline(esik, color="#DC2626", ls="--", lw=1.0); ax.text(446, esik + 0.8, "karar eşiği", color="#DC2626", ha="right", fontsize=8)
    ax.axvline(r, color=MUTED, ls=":", lw=1.0); ax.text(r + 4, ax.get_ylim()[1] * 0.0 + 1, "gerçek mesafe", rotation=90, color=MUTED, fontsize=8, va="bottom")
    ax.set_xlim(0, 450); ax.set_xlabel("mesafe (m)"); ax.set_ylabel("gürültü tabanının kaç dB üstünde")
    zirve = prof.max()
    ax.set_title(f"en yüksek zirve gürültü tabanının {zirve:.1f} dB üstünde, eşik {esik:.1f} dB", loc="left", fontsize=9, color=renk)
    # ---- satir 3: mesafe-hiz haritasi
    ax = axs[2, j]
    db = 10 * np.log10(Pm / taban)
    ax.imshow(db.T, origin="lower", aspect="auto", cmap="magma", vmin=0, vmax=max(25, zirve), extent=[rax[sel][0], rax[sel][-1], vax[0], vax[-1]])
    ax.plot(r, V, "o", mfc="none", mec="#22D3EE", ms=15, mew=1.6)
    ax.set_xlabel("mesafe (m)"); ax.set_ylabel("radyal hız (m/s)"); ax.set_xlim(0, 450)
    ax.set_title("mesafe-hız haritası (mavi halka = gerçek İHA)", loc="left", fontsize=9, color=MUTED)
fig.suptitle("Radar İHA'yı nasıl buluyor? (gerçek kodumuzdan iki deneme, PRS 16 tekrar)", x=0.01, ha="left", fontsize=12.5, fontweight="bold")
fig.savefig(os.path.join(HERE, "radar_nasil_bulur.png"), dpi=140, bbox_inches="tight", facecolor="white")
for r, istenen, tohum, s in kutu: print(r, istenen, "tohum", tohum, "SNR/RE %.1f dB" % s[0], "olculen mesafe %.1f" % s[5])

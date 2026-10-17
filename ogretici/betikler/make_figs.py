"""EHB415 ogretici: tum sekilleri uretir.
Calistirma (Windows):  <python> betikler\\make_figs.py     (ogretici klasorunden)
Gereken paketler: numpy, matplotlib, pandas
Veri: veri/*.csv (OCUDU ve ns-3 gercek olcumleri). Sentetik olanlar (radar) dosyada aciklanmistir.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "sekiller")
DATA = os.path.join(ROOT, "veri")
os.makedirs(OUT, exist_ok=True)

INK = "#1f2937"; MUTED = "#6b7280"; BLUE = "#2563eb"; ORANGE = "#ea580c"
GREEN = "#16a34a"; RED = "#dc2626"; PURPLE = "#7c3aed"; GRID = "#e5e7eb"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.7,
    "savefig.dpi": 200, "savefig.bbox": "tight",
})

def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".pdf"))
    fig.savefig(os.path.join(OUT, name + ".png"))
    plt.close(fig)
    print("ok", name)

# ---------------------------------------------------------------- OFDM radar (sentetik)
C = 3e8
def ofdm_radar(targets, N=1024, M=128, scs=30e3, fc=4.9e9, snr_db=10, mask=None, seed=0):
    """Dolgu (mask) olmayan OFDM sembollerinden range-Doppler haritasi.
    targets: [(R, v, genlik)]. mask: M uzunlugunda 0/1 (1 = sembol gonderildi)."""
    rng = np.random.default_rng(seed)
    W = N * scs; Ts = (1 / scs) * (1 + 7 / 64); lam = C / fc
    n = np.arange(N)[:, None]; m = np.arange(M)[None, :]
    X = np.exp(1j * 2 * np.pi * rng.random((N, M)))
    Y = np.zeros((N, M), complex)
    for R, v, a in targets:
        Y += a * X * np.exp(-1j * 2 * np.pi * n * scs * (2 * R / C)) * np.exp(1j * 2 * np.pi * m * Ts * (2 * v / lam))
    sig_p = np.mean(np.abs(Y) ** 2)
    nz = np.sqrt(sig_p / (10 ** (snr_db / 10)) / 2)
    Y += nz * (rng.normal(size=Y.shape) + 1j * rng.normal(size=Y.shape))
    H = Y / X
    if mask is not None:
        H = H * mask[None, :]
    rd = np.fft.fftshift(np.fft.fft(np.fft.ifft(H, axis=0), axis=1), axes=1)
    rax = np.arange(N) * C / (2 * W)
    vax = (np.arange(M) - M // 2) / (M * Ts) * lam / 2
    return rax, vax, rd, dict(W=W, Ts=Ts, lam=lam)

def fig_rd_map():
    tg = [(120.0, 25.0, 1.0), (260.0, -18.0, 0.6)]
    rax, vax, rd, _ = ofdm_radar(tg, snr_db=0)
    P = 20 * np.log10(np.abs(rd) / np.abs(rd).max() + 1e-9)
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    sel = rax < 400
    im = ax.imshow(P[sel].T, aspect="auto", origin="lower", cmap="magma", vmin=-40, vmax=0,
                   extent=[rax[sel][0], rax[sel][-1], vax[0], vax[-1]])
    for R, v, _a in tg:
        ax.plot(R, v, "o", mfc="none", mec="#22d3ee", ms=14, mew=1.6)
    ax.set_ylim(-80, 80)
    ax.set_xlabel("Menzil (m)"); ax.set_ylabel("Radyal hız (m/s)")
    ax.set_title("Range-Doppler haritası (2 hedef, simülasyon)", fontsize=10.5, color=INK)
    ax.grid(False)
    cb = fig.colorbar(im, ax=ax, pad=0.02); cb.set_label("Güç (dB, tepeye göre)")
    ax.text(0.99, 0.04, "turkuaz halka = gerçek hedef konumu", transform=ax.transAxes, ha="right",
            color="white", fontsize=8.5)
    save(fig, "fig_rd_map")

def fig_resolution():
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.2))
    bw = np.linspace(5e6, 400e6, 200)
    ax[0].plot(bw / 1e6, C / (2 * bw), color=BLUE, lw=2)
    offs0 = {20: (10, 8), 50: (12, 18), 100: (14, 30)}
    for b in (20, 50, 100):
        ax[0].plot(b, C / (2 * b * 1e6), "o", color=ORANGE)
        ax[0].annotate(f"{b} MHz: {C/(2*b*1e6):.2f} m", (b, C / (2 * b * 1e6)), textcoords="offset points",
                       xytext=offs0[b], fontsize=8.5, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
    ax[0].set_xlabel("Bant genişliği W (MHz)"); ax[0].set_ylabel("Menzil çözünürlüğü (m)")
    ax[0].set_title(r"$\Delta R = c / (2W)$", fontsize=10.5); ax[0].set_ylim(0, 32)
    M = np.arange(14, 1100); lam = C / 4.9e9; Ts = (1 / 30e3) * (1 + 7 / 64)
    ax[1].semilogx(M, lam / (2 * M * Ts), color=GREEN, lw=2)
    offs1 = {14: (14, -4), 128: (10, 14), 1024: (-60, 18)}
    for mm in (14, 128, 1024):
        ax[1].plot(mm, lam / (2 * mm * Ts), "o", color=ORANGE)
        ax[1].annotate(f"M={mm}: {lam/(2*mm*Ts):.1f} m/s", (mm, lam / (2 * mm * Ts)), textcoords="offset points",
                       xytext=offs1[mm], fontsize=8.5, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
    ax[1].set_ylim(-3, 66)
    ax[1].set_xlabel("Gözlenen OFDM sembol sayısı M"); ax[1].set_ylabel("Hız çözünürlüğü (m/s)")
    ax[1].set_title(r"$\Delta v = \lambda / (2 M T_{sym})$ (4,9 GHz, 30 kHz)", fontsize=9.5)
    fig.tight_layout()
    save(fig, "fig_resolution")

def pslr_db(rd, rax, vax, R0, v0, guard_r=3, guard_v=3):
    P = np.abs(rd)
    k0 = int(np.argmin(np.abs(rax - R0))); l0 = int(np.argmin(np.abs(vax - v0)))
    peak = P[k0 - 2:k0 + 3, l0 - 2:l0 + 3].max()
    Q = P.copy()
    Q[max(0, k0 - guard_r - 2):k0 + guard_r + 3, max(0, l0 - guard_v - 2):l0 + guard_v + 3] = 0
    Q[:, :] = np.where(np.arange(Q.shape[0])[:, None] < 2 * 400 / (C / (2 * 30e3 * 1024)) , Q, 0)
    return 20 * np.log10(peak / Q.max())

def fig_gap():
    """Haberlesme zamanlamasi bazi OFDM sembollerini sensing icin birakmazsa Doppler isleme nasil bozulur?"""
    M = 128; R0, v0 = 120.0, 25.0
    rng = np.random.default_rng(1)
    fracs = np.linspace(0, 0.8, 9)
    res_rand, res_burst = [], []
    for f in fracs:
        pr, pb = [], []
        for s in range(12):
            mk = np.ones(M)
            idx = rng.choice(M, int(round(f * M)), replace=False); mk[idx] = 0
            rax, vax, rd, _ = ofdm_radar([(R0, v0, 1.0)], snr_db=10, mask=mk, seed=s)
            pr.append(pslr_db(rd, rax, vax, R0, v0))
            mb = np.ones(M); mb[:int(round(f * M))] = 0     # ardisik bosluk
            rax, vax, rd, _ = ofdm_radar([(R0, v0, 1.0)], snr_db=10, mask=mb, seed=s)
            pb.append(pslr_db(rd, rax, vax, R0, v0))
        res_rand.append(np.mean(pr)); res_burst.append(np.mean(pb))
    fig, ax = plt.subplots(figsize=(6.0, 3.3))
    ax.plot(fracs * 100, res_rand, "o-", color=ORANGE, lw=2, label="rastgele dağılmış boşluklar")
    ax.plot(fracs * 100, res_burst, "s-", color=BLUE, lw=2, label="ardışık (tek parça) boşluk")
    ax.set_xlabel("Sensing'e kullanılamayan OFDM sembolü oranı (%)")
    ax.set_ylabel("Tepe / en yüksek yan lob (dB)")
    ax.set_title("Boşluklar Doppler haritasını bozar (simülasyon)", fontsize=10.5)
    ax.legend(frameon=False, fontsize=9)
    save(fig, "fig_gap")
    # yan yana harita ornegi
    fig, axs = plt.subplots(1, 3, figsize=(8.4, 2.9), sharey=True)
    for a, (f, ttl) in zip(axs, [(0.0, "boşluk yok"), (0.3, "%30 rastgele boşluk"), (0.6, "%60 rastgele boşluk")]):
        mk = np.ones(M); mk[rng.choice(M, int(round(f * M)), replace=False)] = 0
        rax, vax, rd, _ = ofdm_radar([(R0, v0, 1.0)], snr_db=10, mask=mk, seed=3)
        P = 20 * np.log10(np.abs(rd) / np.abs(rd).max() + 1e-9); sel = (rax > 60) & (rax < 200)
        a.imshow(P[sel].T, aspect="auto", origin="lower", cmap="magma", vmin=-40, vmax=0,
                 extent=[rax[sel][0], rax[sel][-1], vax[0], vax[-1]])
        a.set_title(ttl, fontsize=9.5); a.set_xlabel("Menzil (m)"); a.grid(False); a.set_ylim(-120, 120)
    axs[0].set_ylabel("Radyal hız (m/s)")
    fig.tight_layout()
    save(fig, "fig_gap_maps")

# ---------------------------------------------------------------- D1 modeli (formul, makale parametreleri)
def fig_d1():
    NPRB_TOT, OH, NSYM_SEC = 270, 0.14, 14000          # Dickerson vd. (2606.21677) bolum IV
    nzc = {71: 6, 211: 18, 503: 42, 839: 70, 1291: 108}  # Tablo II: N_ZC -> PRB
    def alpha(nb, f, prb): return (nb / (1 - OH)) * (f / NSYM_SEC) * (prb / NPRB_TOT)
    # Dogrulama: makalenin verdigi iki sayi
    a1 = alpha(1, 500, 108) * 100; a8 = alpha(8, 500, 108) * 100
    print(f"D1 dogrulama: Nb=1 -> {a1:.2f}% (makale 1.66), Nb=8 -> {a8:.2f}% (makale 13.29)")
    fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.3))
    f = np.linspace(10, 500, 100)
    cols = [BLUE, GREEN, ORANGE, PURPLE, RED]
    for (n, prb), c in zip(nzc.items(), cols):
        ax[0].plot(f, alpha(1, f, prb) * 100, color=c, lw=2, label=f"$N_{{ZC}}$={n} ({prb} PRB)")
    ax[0].set_xlabel("Sensing hızı $f_{sense}$ (Hz)"); ax[0].set_ylabel(r"$\alpha_{sense}$ (% ortak kaynak)")
    ax[0].set_title("Tek ışın: sensing'in kaynak payı", fontsize=10); ax[0].legend(frameon=False, fontsize=8)
    eta = np.linspace(0, 1, 200)
    for nb, c in [(1, GREEN), (8, ORANGE)]:
        a = alpha(nb, 500, 108)
        ax[1].plot(eta, np.minimum(eta, 1 - a), color=c, lw=2, label=f"{nb} ışın (α={a*100:.1f}%)")
    ax[1].plot(eta, eta, "--", color=MUTED, lw=1, label="sensing yok")
    ax[1].set_xlabel(r"Sunulan yük $\eta$"); ax[1].set_ylabel(r"Sunulan throughput $T(\eta)$")
    ax[1].set_title(r"$T(\eta)=\min\{\eta,\,1-\alpha_{sense}\}$", fontsize=10)
    ax[1].legend(frameon=False, fontsize=8.5); ax[1].set_xlim(0.6, 1.0); ax[1].set_ylim(0.6, 1.0)
    fig.tight_layout(); save(fig, "fig_d1_model")

# ---------------------------------------------------------------- OCUDU gercek olcum
def fig_ocudu():
    d = pd.read_csv(os.path.join(DATA, "ocudu_prs_sweep.csv"))
    base = d[d.tag == "base"].dl_brate_mbps.iloc[0]
    s = d[(d.tag.isin(["base", "p80", "p40", "p20", "p10", "p8", "p4"]))].copy()
    s["pay"] = np.where(s.periyot_slot > 0, 1.0 / s.periyot_slot.replace(0, np.nan), 0.0)
    fig, ax = plt.subplots(figsize=(6.2, 3.5))
    x = np.linspace(0, 0.26, 50)
    ax.plot(x * 100, base * (1 - x), "--", color=MUTED, lw=1.5, label=r"kuram: $59\,(1-1/T_{PRS})$")
    ax.plot(s.pay * 100, s.dl_brate_mbps, "o-", color=BLUE, lw=2, ms=6, label="OCUDU ölçümü (tüm bant PRS)")
    offs = {80: (-14, 10), 40: (4, 9), 20: (5, 7), 10: (5, 7), 8: (5, 7), 4: (5, 7)}
    for _, r in s.iterrows():
        if r.periyot_slot > 0:
            ax.annotate(f"T={int(r.periyot_slot)}", (r.pay * 100, r.dl_brate_mbps), textcoords="offset points",
                        xytext=offs[int(r.periyot_slot)], fontsize=8)
    w = d[d.tag == "p4w52"].iloc[0]
    ax.plot(25, w.dl_brate_mbps, "D", color=ORANGE, ms=8, label="T=4, PRS bandın yarısında (52 PRB)")
    ax.set_xlabel("PRS'li slot oranı (%)  =  100 / T$_{PRS}$"); ax.set_ylabel("DL throughput (Mbps)")
    ax.set_title("OCUDU testmode: PRS yükü arttıkça DL throughput düşer", fontsize=10.5)
    ax.legend(frameon=False, fontsize=8.5, loc="lower left"); ax.set_ylim(38, 62)
    save(fig, "fig_ocudu_prs")

# ---------------------------------------------------------------- ns-3 gercek olcum
def fig_ns3():
    d = pd.read_csv(os.path.join(DATA, "ns3_ue_sweep.csv"))
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.2))
    ax[0].plot(d.ue_per_gnb, d.total_throughput_mbps, "o-", color=BLUE, lw=2)
    ax[0].set_xlabel("gNB başına UE sayısı"); ax[0].set_ylabel("Toplam throughput (Mbps)")
    ax[0].set_title("Kapasite doygunluğa varır", fontsize=10)
    ax[1].plot(d.ue_per_gnb, d.mean_flow_delay_ms, "s-", color=RED, lw=2)
    ax[1].set_xlabel("gNB başına UE sayısı"); ax[1].set_ylabel("Ortalama gecikme (ms)")
    ax[1].set_title("Yük arttıkça gecikme patlar", fontsize=10)
    fig.tight_layout(); save(fig, "fig_ns3_ues")

# ---------------------------------------------------------------- kaynak izgarasi semasi
def fig_grid():
    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    nslot, nsym, nprb = 8, 14, 106
    ax.set_xlim(0, nslot * nsym); ax.set_ylim(0, nprb)
    ax.add_patch(Rectangle((0, 0), nslot * nsym, nprb, fc="#dbeafe", ec="none"))     # PDSCH (mavi)
    for sl in range(nslot):
        ax.add_patch(Rectangle((sl * nsym, nprb - 12), 2, 12, fc="#bbf7d0", ec="none"))   # PDCCH
    ax.add_patch(Rectangle((0 * nsym + 2, 0), 4, 40, fc="#fde68a", ec="none"))               # SSB
    for sl in (1, 5):                                                                       # PRS / sensing
        ax.add_patch(Rectangle((sl * nsym + 2, 1), 12, 104, fc="#fb923c", ec="#9a3412", lw=1))
    for sl in range(nslot + 1):
        ax.axvline(sl * nsym, color="white", lw=1.2)
    ax.set_xticks([(s + 0.5) * nsym for s in range(nslot)]); ax.set_xticklabels([f"slot {s}" for s in range(nslot)])
    ax.set_yticks([]); ax.set_ylabel("Frekans (PRB)"); ax.set_xlabel("Zaman (slot = 14 OFDM sembolü)")
    ax.grid(False)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc="#dbeafe", label="PDSCH (kullanıcı verisi)"), Patch(fc="#bbf7d0", label="PDCCH (kontrol)"),
                       Patch(fc="#fde68a", label="SSB (senkronizasyon)"), Patch(fc="#fb923c", label="PRS / sensing sinyali")],
              ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.16), frameon=False, fontsize=8.5)
    save(fig, "fig_grid")

# ---------------------------------------------------------------- terminal ciktisi gorselleri
def term(name, lines, title, fs=8.2, w=8.4):
    h = 0.62 + 0.155 * len(lines)
    fig = plt.figure(figsize=(w, h)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, fc="#0f172a", ec="none", transform=ax.transAxes))
    ax.text(0.012, 1 - 0.18 / h, title, color="#94a3b8", fontsize=7.8, family="DejaVu Sans Mono", va="top", transform=ax.transAxes)
    for i, ln in enumerate(lines):
        ax.text(0.012, 1 - (0.42 + 0.155 * i) / h, ln, color="#e2e8f0", fontsize=fs, family="DejaVu Sans Mono",
                va="top", transform=ax.transAxes)
    save(fig, name)

def fig_terms():
    ns = open(os.path.join(DATA, "ns3_run_5ue.txt"), errors="ignore").read().splitlines()
    ns = [l for l in ns if l.strip()][-14:]
    term("term_ns3", ["$ ./ns3 run \"cttc-nr-demo --ueNumPergNb=5\""] + [l[:100] for l in ns], "Ubuntu (WSL2): ns-3 çıktısının son satırları")
    oc = open(os.path.join(DATA, "ocudu_p4_console.txt"), errors="ignore").read().splitlines()
    keep = [l[:118] for l in oc if l.strip() and ("OCUDU" in l or "Cell" in l or "gNB" in l or "pci" in l
                                                   or l.strip().startswith("1  ") or "|" in l)]
    keep = keep[:4] + keep[-6:]
    term("term_ocudu", ["$ ./gnb -c ehb_p4.yml      # PRS her 4 slotta bir"] + keep, "Ubuntu (WSL2): OCUDU gNB testmode (gerçek çıktı)", fs=7.4, w=9.0)

if __name__ == "__main__":
    fig_rd_map(); fig_resolution(); fig_gap(); fig_d1(); fig_ocudu(); fig_ns3(); fig_grid(); fig_terms()

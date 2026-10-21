"""Sionna sehir projesi, 2. parca: IHA takibi (OFDM radar) ve sensing kaynagi <-> basari analizi.
Girdi:  cikti/rt_sonuclar.npz  (rt_sehir.py uretir: IHA rotasi, gNB konumu, gorus hatti LOS, kapsama haritasi)
Cikti:  cikti/05_takip_filmi.gif, cikti/06_kaynak_basari.png, cikti/takip_sonuclar.csv

MODEL (oyuncak ama standart radar denklemi): gNB, 4,9 GHz'te OFDM sinyali (1024 alt tasiyici x 30 kHz = 30,72 MHz) gonderir,
IHA'dan donen yanki alinir (monostatic). Menzil/hiz 2B FFT ile bulunur. Varsayimlar BU DOSYADA, asagida PARAM bolumunde.
Gorus hatti (LOS) bilgisi Sionna RT'den gelir; LOS yoksa yanki NLOS_KAYIP_DB kadar zayiflar.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.gridspec import GridSpec

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "cikti")
D = np.load(os.path.join(OUT, "rt_sonuclar.npz"))
pos, los, gnb, fc = D["pos"], D["los"], D["gnb"], float(D["fc"])
pg, cc = D["pg"], D["cc"]

# ------------------------------------------------ PARAM (hepsi varsayim; TR 38.765 Ek A'dan esinlenildi)
C = 3e8; LAM = C / fc
N, SCS, NF = 1024, 30e3, 5.0                      # alt tasiyici, SCS, gurultu figuru (dB)
W = N * SCS; TS = (1 / SCS) * (1 + 7 / 64)
PT_DBM, G_DBI, RCS_DBSM = 37.0, 26.0, -20.0       # gNB gucu, anten kazanci (tx=rx), IHA RCS
X_SI_DB = 40.0                                    # artik oz-girisim: TR'de "-94+X dBm / 100 MHz", X sirket secimi
NLOS_KAYIP_DB = 30.0                              # gorus hatti yoksa yanki zayiflamasi (varsayim)
PFA = 1e-3                                        # CPI basina yanlis alarm olasiligi; esik, hucre sayisina gore uyarlanir (CFAR benzeri)
DT = 14.3 / (len(pos) - 1)                        # IHA ~25 m/s
FRAME_SYM = 140                                   # 10 ms = 10 slot = 140 sembol; alpha = M / 140

R = np.linalg.norm(pos - gnb, axis=1)
Vr = np.gradient(R, DT)                           # radyal hiz (gNB'ye gore)

def snr_ornek_db(r, nlos=False):
    pr_dbm = PT_DBM + 2 * G_DBI + 20 * np.log10(LAM) - 30 * np.log10(4 * np.pi) + RCS_DBSM - 40 * np.log10(r)
    if nlos: pr_dbm -= NLOS_KAYIP_DB
    gurultu = -174 + 10 * np.log10(W) + NF + X_SI_DB - 5.0 * 0   # kTBF + artik oz-girisim payi
    return pr_dbm - gurultu

def radar(r, v, M, snr_db, rng):
    """Tek bir CPI: M sembol. Donus: menzil ekseni, hiz ekseni, |RD| (guc, lineer)."""
    n = np.arange(N)[:, None]; m = np.arange(M)[None, :]
    X = np.exp(1j * 2 * np.pi * rng.random((N, M)))
    a = 10 ** (snr_db / 20)                       # genlik: ornek basina SNR
    Y = a * X * np.exp(-1j * 2 * np.pi * n * SCS * 2 * r / C) * np.exp(1j * 2 * np.pi * m * TS * 2 * v / LAM)
    Y += (rng.normal(size=Y.shape) + 1j * rng.normal(size=Y.shape)) / np.sqrt(2)
    H = Y / X
    rd = np.fft.fftshift(np.fft.fft(np.fft.ifft(H, axis=0), axis=1), axes=1)
    rax = np.arange(N) * C / (2 * W)
    vax = (np.arange(M) - M // 2) / (M * TS) * LAM / 2
    return rax, vax, np.abs(rd) ** 2

def _parab(y0, y1, y2):
    """Uc nokta uzerinden parabolik tepe konumu (bin kesri)."""
    pay = y0 - 2 * y1 + y2
    return 0.0 if abs(pay) < 1e-12 else 0.5 * (y0 - y2) / pay

def tespit(rax, vax, P, rmax=450.0):
    """Tepe + parabolik interpolasyon (kuantizasyon yapay etkisini azaltir)."""
    sel = rax < rmax
    Pm = P[sel]
    k, l = np.unravel_index(Pm.argmax(), Pm.shape)
    taban = np.median(Pm)
    # Gurultu hucreleri ussel dagilimli: medyan = s2*ln2 ve P(maks > T) = Pfa  =>  T/medyan = (ln(Nhucre)+ln(1/Pfa))/ln2
    esik_db = 10 * np.log10((np.log(Pm.size) + np.log(1 / PFA)) / np.log(2))
    ok = 10 * np.log10(Pm[k, l] / taban) >= esik_db
    A = np.sqrt(Pm)
    dk = _parab(A[k - 1, l], A[k, l], A[k + 1, l]) if 0 < k < Pm.shape[0] - 1 else 0.0
    dl = _parab(A[k, l - 1], A[k, l], A[k, l + 1]) if 0 < l < Pm.shape[1] - 1 else 0.0
    dr = rax[1] - rax[0]; dv = vax[1] - vax[0]
    return ok, rax[sel][k] + dk * dr, vax[l] + dl * dv

# ------------------------------------------------ A) kaynak <-> basari (Monte Carlo)
def kaynak_basari():
    rng = np.random.default_rng(7)
    Ms = [4, 8, 14, 28, 56, 70, 140]
    Rs = [100, 200, 300, 400]
    sat = []
    for r in Rs:
        for M in Ms:
            ok = 0; hr = []; hv = []
            for _ in range(160):
                v0 = rng.uniform(-30, 30); r_g = r + rng.uniform(-6, 6)     # rastgele konum: izgara etkisini yok say
                rax, vax, P = radar(r_g, v0, M, snr_ornek_db(r), rng)
                tp, re, ve = tespit(rax, vax, P)
                if tp and abs(re - r_g) < 3 * C / (2 * W):
                    ok += 1; hr.append(re - r_g); hv.append(ve - v0)
            sat.append(dict(menzil_m=r, M=M, alpha=M / FRAME_SYM, pd=ok / 160,
                            rmse_menzil_m=float(np.sqrt(np.mean(np.square(hr)))) if (ok / 160 >= 0.5) else np.nan,
                            rmse_hiz_ms=float(np.sqrt(np.mean(np.square(hv)))) if (ok / 160 >= 0.5) else np.nan))
    df = pd.DataFrame(sat); df.to_csv(os.path.join(OUT, "kaynak_basari.csv"), index=False)
    fig, ax = plt.subplots(1, 3, figsize=(11.5, 3.5))
    for r, c in zip(Rs, ["#16a34a", "#2563eb", "#ea580c", "#dc2626"]):
        s = df[df.menzil_m == r]
        ax[0].plot(s.alpha * 100, s.pd, "o-", color=c, label=f"{r} m")
        ax[1].plot(s.alpha * 100, s.rmse_menzil_m, "o-", color=c)
        ax[2].plot(s.alpha * 100, s.rmse_hiz_ms, "o-", color=c)
    ax[0].set_ylabel("Tespit olasılığı")
    ax[1].set_ylabel("Menzil hatası RMSE (m)\n(yalnızca Pd ≥ 0,5 iken)")
    ax[2].set_ylabel("Hız hatası RMSE (m/s)\n(yalnızca Pd ≥ 0,5 iken)")
    for a_ in ax:
        a_.set_xlabel("Sensing kaynak payı α (% sembol)"); a_.grid(alpha=0.3)
    ax[0].legend(title="IHA menzili", frameon=False, fontsize=8)
    fig.suptitle("Sensing'e ayrılan kaynak arttıkça tespit ve doğruluk (simülasyon, oyuncak radar modeli)", fontsize=10.5)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "06_kaynak_basari.png"), dpi=140); plt.close(fig)
    print(df.pivot(index="alpha", columns="menzil_m", values="pd").round(2))
    return df

# ------------------------------------------------ B) takip filmi
def film():
    rng = np.random.default_rng(3)
    Ma, Mb = 14, 70                                  # alpha = %10 ve %50
    yolA, yolB = [], []
    kare = []
    for i in range(len(pos)):
        snr = snr_ornek_db(R[i], nlos=not los[i])
        rA = radar(R[i], Vr[i], Ma, snr, rng); rB = radar(R[i], Vr[i], Mb, snr, rng)
        tA = tespit(rA[0], rA[1], rA[2]); tB = tespit(rB[0], rB[1], rB[2])
        def deg(tt, i=i):
            dogru = bool(tt[0] and abs(tt[1] - R[i]) < 3 * C / (2 * W))
            return (dogru, tt[1], tt[2], bool(tt[0] and not dogru))      # (dogru tespit, menzil, hiz, yanlis alarm)
        yolA.append(deg(tA)); yolB.append(deg(tB)); kare.append((rA, rB))
    pd.DataFrame(dict(t=np.arange(len(pos)) * DT, menzil_gercek=R, hiz_gercek=Vr, los=los,
                      A_tespit=[x[0] for x in yolA], A_yanlis_alarm=[x[3] for x in yolA], A_menzil=[x[1] for x in yolA], A_hiz=[x[2] for x in yolA],
                      B_tespit=[x[0] for x in yolB], B_yanlis_alarm=[x[3] for x in yolB], B_menzil=[x[1] for x in yolB], B_hiz=[x[2] for x in yolB])
                 ).to_csv(os.path.join(OUT, "takip_sonuclar.csv"), index=False)
    pgdb = 10 * np.log10(np.maximum(pg, 1e-14))
    ext = [cc[..., 0].min(), cc[..., 0].max(), cc[..., 1].min(), cc[..., 1].max()]
    fig = plt.figure(figsize=(12.5, 7.2))
    gs = GridSpec(2, 3, height_ratios=[1.6, 1], hspace=0.38, wspace=0.28, figure=fig)
    axm = fig.add_subplot(gs[0, 0]); axa = fig.add_subplot(gs[0, 1]); axb = fig.add_subplot(gs[0, 2]); axt = fig.add_subplot(gs[1, :])
    def cizim(i):
        for a_ in (axm, axa, axb, axt): a_.clear()
        axm.imshow(pgdb, origin="lower", extent=ext, cmap="viridis", vmin=-130, vmax=-60)
        axm.plot(pos[:, 0], pos[:, 1], "-", color="white", lw=0.6, alpha=0.6)
        for j in range(len(pos) - 1):
            axm.plot(pos[j:j + 2, 0], pos[j:j + 2, 1], "-", color="#22c55e" if los[j] else "#ef4444", lw=2)
        axm.plot(*gnb[:2], "*", color="yellow", ms=14, mec="black", label="gNB")
        axm.plot(pos[i, 0], pos[i, 1], "o", color="white", mec="black", ms=9, label="İHA")
        axm.set_title(f"Münih: gNB kapsama haritası (RT)\nİHA rotası: yeşil=görüş hattı var, kırmızı=engelli", fontsize=9)
        axm.set_xlim(-260, 260); axm.set_ylim(-170, 260)
        axm.set_xlabel("x (m)"); axm.set_ylabel("y (m)"); axm.legend(loc="lower left", fontsize=7, framealpha=0.8)
        for ax_, (rr, tt, M) in zip((axa, axb), ((kare[i][0], yolA[i], Ma), (kare[i][1], yolB[i], Mb))):
            rax, vax, P = rr
            sel = rax < 450
            db = 10 * np.log10(P[sel] / np.median(P[sel]))
            ax_.imshow(db.T, origin="lower", aspect="auto", cmap="magma", vmin=0, vmax=40,
                       extent=[rax[sel][0], rax[sel][-1], vax[0], vax[-1]])
            ax_.plot(R[i], Vr[i], "o", mfc="none", mec="#22d3ee", ms=14, mew=1.6)
            ax_.set_ylim(-60, 60)
            durum, renk = (("TESPİT (doğru)", "#16a34a") if tt[0] else
                           (("YANLIŞ ALARM", "#f59e0b") if tt[3] else ("tespit YOK", "#dc2626")))
            ax_.set_title(f"Sensing kaynak payı α = %{100 * M / FRAME_SYM:.0f} (M={M} sembol)\n" + durum,
                          fontsize=9, color=renk)
            ax_.set_xlabel("Menzil (m)"); ax_.set_ylabel("Radyal hız (m/s)")
        tt_ = np.arange(len(pos)) * DT
        axt.plot(tt_, R, "-", color="black", lw=2, label="gerçek menzil")
        for yol, c, lab in ((yolA, "#ea580c", "α=%10"), (yolB, "#2563eb", "α=%50")):
            tk = [(tt_[j], yol[j][1]) for j in range(i + 1) if yol[j][0]]
            if tk: axt.plot(*zip(*tk), ".", color=c, ms=6, label=f"doğru tespit ({lab})")
            fa = [(tt_[j], yol[j][1]) for j in range(i + 1) if yol[j][3]]
            if fa: axt.plot(*zip(*fa), "x", color=c, ms=6, mew=1.5)
        axt.axvline(tt_[i], color="gray", ls=":")
        axt.set_xlim(0, tt_[-1]); axt.set_ylim(0, 450); axt.set_xlabel("zaman (s)"); axt.set_ylabel("menzil (m)")
        axt.legend(loc="upper right", fontsize=8, ncol=3, frameon=False); axt.grid(alpha=0.3)
        axt.set_title("İHA takibi: nokta = doğru tespit, çarpı (x) = yanlış alarm, boşluk = tespit edilemedi", fontsize=9)
    anim = FuncAnimation(fig, cizim, frames=len(pos), interval=200)
    yol = os.path.join(OUT, "05_takip_filmi.gif"); anim.save(yol, writer=PillowWriter(fps=5)); plt.close(fig)
    print("film:", yol, round(os.path.getsize(yol) / 1024 / 1024, 1), "MB")
    print("dogru tespit orani  alpha=10%:", np.mean([x[0] for x in yolA]).round(2), " alpha=50%:", np.mean([x[0] for x in yolB]).round(2))
    print("yanlis alarm sayisi alpha=10%:", sum(x[3] for x in yolA), " alpha=50%:", sum(x[3] for x in yolB), "(60 kareden)")
    print("LOS orani:", los.mean().round(2), "| menzil araligi %.0f-%.0f m" % (R.min(), R.max()))

if __name__ == "__main__":
    kaynak_basari(); film()

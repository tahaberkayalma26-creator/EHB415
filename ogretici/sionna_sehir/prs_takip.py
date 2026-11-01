"""PRS ile IHA tespiti: radar_takip.py ile AYNI harita, ayni IHA rotasi, ayni radar denklemi (SNR); tek fark gonderilen sinyal.
radar_takip.py her alt tasiyiciyi rastgele fazli sembollerle doldurur; burada gercek NR PRS gonderilir:
  - dizi: TS 38.211 7.4.1.7.2 (Gold dizisi, QPSK) -> OCUDU lib/phy/upper/signal_processors/prs/prs_generator_impl.cpp'den uyarlandi
  - yerlesim: TS 38.211 7.4.1.7.3 (tarak boyutu K, sembol sayisi L, her sembolde kayan tarak) -> ayni dosyadaki get_freq_offset
  - Gold dizisi tanimi: OCUDU tests/unittests/phy/upper/sequence_generators/pseudo_random_generator_test.cpp (Nc=1600)
Calistirma (rt_sehir.py ve radar_takip.py bir kez calismis olmali; cikti/rt_sonuclar.npz gerekir):
    python prs_takip.py
Cikti: cikti/07_prs_izgara.png, cikti/08_prs_harita.png, cikti/09_prs_basari.png, cikti/prs_takip_sonuclar.csv, cikti/prs_basari.csv
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import radar_takip as rt              # harita, rota, SNR ve tespit fonksiyonu radar_takip.py'den (film/analiz calismaz)

rt.RCS_DBSM = -12.81                              # TR 38.901 RCS model 1, kucuk IHA, ortalama (radar_takip.py'de -20 varsayimdi); snr_ornek_db bu degeri okur
C, LAM, OUT = rt.C, rt.LAM, rt.OUT
pos, los, gnb, R, Vr = rt.pos, rt.los, rt.gnb, rt.R, rt.Vr

# ------------------------------------------------ PARAM (PRS yapilandirmasi; hepsi OCUDU'nun kabul ettigi degerler)
SCS = 30e3                                        # alt tasiyici araligi (radar_takip.py ile ayni)
SLOT = 0.5e-3                                     # 30 kHz'te slot suresi
TSYM = SLOT / 14                                  # sembol araligi (CP dahil yaklasik; ilk sembolun uzunlugu farki yok sayildi)
K, L, L_START = 4, 4, 2                           # tarak boyutu, sembol sayisi (L, K'nin kati olmali), ilk sembol
NPRB = 84                                         # PRS bant genisligi: 24..276 arasi 4'un kati
N_ID, GAP = 0, 1                                  # dizi kimligi, tekrarlar arasi bosluk (slot)
NSC = NPRB * 12; W = NSC * SCS                    # alt tasiyici sayisi, bant (30,24 MHz)
VAMB = LAM / (4 * GAP * SLOT)                     # belirsizliksiz hiz siniri: GAP slotta bir ornek -> +-VAMB
COMB_SATIR = {2: [0, 1], 4: [0, 2, 1, 3], 6: [0, 3, 1, 4, 2, 5], 12: [0, 6, 3, 9, 1, 7, 4, 10, 2, 8, 5, 11]}

# ------------------------------------------------ PRS uretimi
def gold(c_init, n):
    """Gold dizisi c(0..n-1), Nc=1600 (OCUDU pseudo_random_generator_test.cpp'deki referans ile ayni)."""
    m = 1600 + n + 31
    x1 = [0] * m; x2 = [0] * m
    x1[0] = 1
    for i in range(31): x2[i] = (c_init >> i) & 1
    for i in range(1600 + n):
        x1[i + 31] = x1[i + 3] ^ x1[i]
        x2[i + 31] = x2[i + 3] ^ x2[i + 2] ^ x2[i + 1] ^ x2[i]
    return np.array([x1[1600 + i] ^ x2[1600 + i] for i in range(n)])

_onbellek = {}
def prs_dizi(slot, sembol):
    """Bir PRS sembolundeki dizi (uzunluk NPRB*12/K): r(m) = ((1-2c(2m)) + j(1-2c(2m+1))) / sqrt(2)."""
    if (slot, sembol) not in _onbellek:
        c_init = ((1 << 22) * (N_ID // 1024) + (1 << 10) * (14 * slot + sembol + 1) * (2 * (N_ID % 1024) + 1) + N_ID % 1024) % (1 << 31)
        c = gold(c_init, 2 * (12 // K) * NPRB)
        _onbellek[(slot, sembol)] = ((1 - 2 * c[0::2]) + 1j * (1 - 2 * c[1::2])) / np.sqrt(2)
    return _onbellek[(slot, sembol)]

def prs_yerlesim(tekrar):
    """'tekrar' kadar slot boyunca PRS: her kayit (alt tasiyici k, zaman n [sembol], dizi degeri)."""
    ks, ns, xs = [], [], []
    for t in range(tekrar):
        slot = t * GAP
        for j in range(L):
            l = L_START + j
            k0 = COMB_SATIR[K][j % K]                       # comb_offset = 0 varsayildi
            ks.append(K * np.arange(NSC // K) + k0); ns.append(np.full(NSC // K, slot * 14 + l)); xs.append(prs_dizi(slot % 20, l))
    return np.concatenate(ks), np.concatenate(ns), np.concatenate(xs)

# ------------------------------------------------ PRS radari (radar_takip.radar ile ayni kanal modeli, seyrek izgara)
_yer = {}
def radar_prs(r, v, tekrar, snr_db, rng):
    if tekrar not in _yer: _yer[tekrar] = prs_yerlesim(tekrar)
    ks, ns, X = _yer[tekrar]
    nt = (tekrar - 1) * GAP * 14 + 14
    a = 10 ** (snr_db / 20)
    Y = a * X * np.exp(-1j * 2 * np.pi * ks * SCS * 2 * r / C) * np.exp(1j * 2 * np.pi * ns * TSYM * 2 * v / LAM)
    Y = Y + (rng.normal(size=Y.shape) + 1j * rng.normal(size=Y.shape)) / np.sqrt(2)
    H = np.zeros((NSC, nt), complex); H[ks, ns] = Y / X     # bos kutular sifir
    rd = np.fft.fftshift(np.fft.fft(np.fft.ifft(H, axis=0), axis=1), axes=1)
    rax = np.arange(NSC) * C / (2 * W)
    vax = (np.arange(nt) - nt // 2) / (nt * TSYM) * LAM / 2
    p = np.abs(rd) ** 2
    s = np.abs(vax) < VAMB                                  # yalniz belirsizliksiz hiz penceresine bak (izgara loblari disarida kalir)
    return rax, vax[s], p[:, s]

def olc(r, v, tekrar, snr_db, rng):
    rax, vax, P = radar_prs(r, v, tekrar, snr_db, rng)
    ok, re, ve = rt.tespit(rax, vax, P, rmax=600.0)         # radar_takip'in varsayilan siniri 450 m; 500 m'deki IHA icin genisletildi
    dogru = bool(ok and abs(re - r) < 3 * C / (2 * W))
    return dogru, bool(ok and not dogru), re, ve, (rax, vax, P)

# ------------------------------------------------ 1) PRS izgarasi (ogretici sekil)
def sekil_izgara():
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.6), gridspec_kw=dict(width_ratios=[1.15, 1]))
    g = np.full((12 * 3, 14), np.nan)                      # 3 PRB x 14 sembol
    for j in range(L):
        k0 = COMB_SATIR[K][j % K]
        g[k0::K, L_START + j] = j + 1
    ax[0].imshow(g, origin="lower", aspect="auto", cmap="viridis", vmin=0, vmax=L + 0.5)
    ax[0].set_xticks(range(14)); ax[0].set_xlabel("OFDM sembolü (bir slot)"); ax[0].set_ylabel("alt taşıyıcı (3 PRB gösterildi)")
    ax[0].set_title(f"PRS yerleşimi: tarak K={K}, L={L} sembol, ilk sembol {L_START}\n(renk = kaçıncı PRS sembolü; boş kutu = PRS yok)", fontsize=9)
    ax[0].set_facecolor("#e5e7eb")
    d = prs_dizi(0, L_START)[:24]
    ax[1].scatter(d.real, d.imag, s=60, color="#2563eb")
    ax[1].axhline(0, color="gray", lw=0.5); ax[1].axvline(0, color="gray", lw=0.5); ax[1].set_aspect("equal")
    ax[1].set_title("PRS dizisinin ilk 24 değeri (QPSK: 4 nokta, genlik hep 1)\nGold dizisi, slot 0, sembol 2, n_ID=0", fontsize=9)
    ax[1].set_xlabel("gerçek"); ax[1].set_ylabel("sanal")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "07_prs_izgara.png"), dpi=140); plt.close(fig)

# ------------------------------------------------ 2) rota boyunca tespit + harita
def harita(tekrar=16):
    rng = np.random.default_rng(3)
    kayit, kare = [], None
    for i in range(len(pos)):
        snr = rt.snr_ornek_db(R[i], nlos=not los[i])
        dogru, yalanci, re, ve, rr = olc(R[i], Vr[i], tekrar, snr, rng)
        kayit.append(dict(t=i * rt.DT, menzil_gercek=R[i], hiz_gercek=Vr[i], los=bool(los[i]), snr_db=snr, dogru=dogru, yanlis_alarm=yalanci,
                          menzil_olculen=re, hiz_olculen=ve))
        if i == len(pos) // 2: kare = (i, rr)
    df = pd.DataFrame(kayit); df.to_csv(os.path.join(OUT, "prs_takip_sonuclar.csv"), index=False)

    pgdb = 10 * np.log10(np.maximum(rt.pg, 1e-14)); cc = rt.cc
    ext = [cc[..., 0].min(), cc[..., 0].max(), cc[..., 1].min(), cc[..., 1].max()]
    fig = plt.figure(figsize=(13, 6.8)); gs = GridSpec(2, 2, height_ratios=[1.5, 1], hspace=0.4, wspace=0.25, figure=fig)
    am = fig.add_subplot(gs[0, 0]); ar = fig.add_subplot(gs[0, 1]); at = fig.add_subplot(gs[1, :])
    am.imshow(pgdb, origin="lower", extent=ext, cmap="viridis", vmin=-130, vmax=-60)
    am.plot(*gnb[:2], "*", color="yellow", ms=14, mec="black", label="gNB (PRS yayınlıyor)")
    for i, k in df.iterrows():
        renk = "#22c55e" if k.dogru else ("#f59e0b" if k.yanlis_alarm else "#ef4444")
        am.plot(pos[i, 0], pos[i, 1], "o", color=renk, ms=6, mec="black", mew=0.4)
    am.plot([], [], "o", color="#22c55e", label="doğru tespit"); am.plot([], [], "o", color="#ef4444", label="tespit yok"); am.plot([], [], "o", color="#f59e0b", label="yanlış alarm")
    am.set_xlim(-260, 260); am.set_ylim(-170, 260); am.set_xlabel("x (m)"); am.set_ylabel("y (m)"); am.legend(loc="lower left", fontsize=7, framealpha=0.85)
    am.set_title(f"Münih haritası: İHA rotası, her nokta için PRS ile tespit sonucu\n(PRS: {NPRB} PRB, K={K}, L={L}, {tekrar} tekrar)", fontsize=9)
    i, (rax, vax, P) = kare
    sel = rax < 450; db = 10 * np.log10(P[sel] / np.median(P[sel]))
    ar.imshow(db.T, origin="lower", aspect="auto", cmap="magma", vmin=0, vmax=40, extent=[rax[sel][0], rax[sel][-1], vax[0], vax[-1]])
    ar.plot(R[i], Vr[i], "o", mfc="none", mec="#22d3ee", ms=14, mew=1.6)
    ar.set_xlabel("Menzil (m)"); ar.set_ylabel("Radyal hız (m/s)")
    ar.set_title(f"Bir anın menzil-hız haritası (nokta {i}); mavi halka = gerçek İHA\nmenzil {R[i]:.0f} m, hız {Vr[i]:.1f} m/s, SNR {df.snr_db[i]:.1f} dB/RE", fontsize=9)
    at.plot(df.t, df.menzil_gercek, "-", color="black", lw=2, label="gerçek menzil")
    d = df[df.dogru]; at.plot(d.t, d.menzil_olculen, ".", color="#16a34a", ms=7, label="PRS ile doğru tespit")
    y = df[df.yanlis_alarm]; at.plot(y.t, y.menzil_olculen, "x", color="#f59e0b", ms=7, mew=1.5, label="yanlış alarm")
    at.set_xlabel("zaman (s)"); at.set_ylabel("menzil (m)"); at.set_ylim(0, 450); at.grid(alpha=0.3); at.legend(loc="upper right", fontsize=8, ncol=3, frameon=False)
    fig.savefig(os.path.join(OUT, "08_prs_harita.png"), dpi=140, bbox_inches="tight"); plt.close(fig)
    print(f"rota: {len(df)} nokta | doğru tespit {df.dogru.mean():.2f} | yanlış alarm {int(df.yanlis_alarm.sum())} | LOS oranı {df.los.mean():.2f}")
    d = df[df.dogru]
    print(f"doğru tespitlerde menzil hatası RMSE {np.sqrt(np.mean((d.menzil_olculen - d.menzil_gercek) ** 2)):.2f} m, hız hatası RMSE {np.sqrt(np.mean((d.hiz_olculen - d.hiz_gercek) ** 2)):.2f} m/s")
    print(f"LOS'lu noktalarda doğru tespit {df[df.los].dogru.mean():.2f} | LOS'suz {df[~df.los].dogru.mean():.2f}")
    return df

# ------------------------------------------------ 3) tekrar sayisi <-> basari (Monte Carlo, radar_takip.kaynak_basari ile ayni yontem)
def basari():
    rng = np.random.default_rng(7)
    Rs, Ts, T_PER = [200, 300, 400, 500], [4, 8, 16, 32], 40    # 2 tekrar: hiz ekseninde tek kutu kalir, hiz olculemez
    sat = []
    for r in Rs:
        for t in Ts:
            ok = 0; hr, hv = [], []
            for _ in range(160):
                v0 = rng.uniform(-25, 25); rg = r + rng.uniform(-6, 6)
                d, _, re, ve, _ = olc(rg, v0, t, rt.snr_ornek_db(r), rng)
                if d: ok += 1; hr.append(re - rg); hv.append(ve - v0)
            iyi = ok / 160 >= 0.5
            sat.append(dict(menzil_m=r, tekrar=t, sure_ms=t * GAP * SLOT * 1e3, pd=ok / 160,
                            rmse_menzil_m=float(np.sqrt(np.mean(np.square(hr)))) if iyi else np.nan,
                            rmse_hiz_ms=float(np.sqrt(np.mean(np.square(hv)))) if iyi else np.nan,
                            ocudu_benzeri_kayip=t / T_PER * NPRB / 273))
    df = pd.DataFrame(sat); df.to_csv(os.path.join(OUT, "prs_basari.csv"), index=False)
    fig, ax = plt.subplots(1, 3, figsize=(11.5, 3.5))
    for r, c in zip(Rs, ["#16a34a", "#2563eb", "#ea580c", "#dc2626"]):
        s = df[df.menzil_m == r]
        ax[0].plot(s.tekrar, s.pd, "o-", color=c, label=f"{r} m"); ax[1].plot(s.tekrar, s.rmse_menzil_m, "o-", color=c); ax[2].plot(s.tekrar, s.rmse_hiz_ms, "o-", color=c)
    ax[0].set_ylabel("Tespit olasılığı"); ax[1].set_ylabel("Menzil hatası RMSE (m)"); ax[2].set_ylabel("Hız hatası RMSE (m/s)")
    for a_ in ax: a_.set_xlabel("PRS tekrar sayısı (art arda slot)"); a_.set_xscale("log", base=2); a_.set_xticks(Ts); a_.set_xticklabels(Ts); a_.grid(alpha=0.3)
    ax[0].legend(title="İHA menzili", frameon=False, fontsize=8)
    fig.suptitle("PRS tekrarı arttıkça tespit ve doğruluk (simülasyon, aynı oyuncak radar denklemi)", fontsize=10.5)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "09_prs_basari.png"), dpi=140); plt.close(fig)
    print(df.pivot(index="tekrar", columns="menzil_m", values="pd").round(2))
    # yanlis alarm: hedef yok
    n, k = 600, 0
    for _ in range(n):
        rax, vax, P = radar_prs(300.0, 0.0, 16, -np.inf, rng)      # snr = -inf dB -> yalnizca gurultu
        k += bool(rt.tespit(rax, vax, P, rmax=600.0)[0])
    print(f"Pf1 (hedefsiz, tekrar=16): {k}/{n} -> %{100 * k / n:.2f}   (hedef: <= %5)")
    return df

if __name__ == "__main__":
    print(f"PRS: K={K}, L={L}, {NPRB} PRB = {NSC} alt tasiyici, bant {W / 1e6:.2f} MHz, menzil cozunurlugu {C / (2 * W):.2f} m, belirsizliksiz hiz +-{VAMB:.1f} m/s")
    print(f"IHA rotasi: menzil {R.min():.0f}-{R.max():.0f} m, en buyuk |radyal hiz| {np.abs(Vr).max():.1f} m/s")
    sekil_izgara(); harita(16); basari()

"""[Nihat, gorev kartlari 4 + CLAUDE.md 'Sionna PRS Configuration'] ogretici/sionna_sehir/prs_takip.py'nin n78 / ortak izgara surumu.
Eski prs_takip.py: 4,9 GHz, 84 PRB (30,24 MHz), K=4, L=4, PRS art arda slotlarda (GAP = 1) tekrarlanir.
Bu surum:   3,5 GHz (rt_sehir_35.py npz'si, radar_takip_35 uzerinden), 30 kHz, hucre 273 PRB (100 MHz), PRS ayarlari
            ogretici/veri/ortak_prs_konfig.csv'den (K1..K11: periyot, sembol, comb, bw, sembol/slot ofseti).
            PRS PERIYOTLA gonderilir: 160 ms gozlem suresinde n_occ = 160 ms / T_PRS PRS firsati (K1: 32, K2: 16, K3: 8).
Dizi ve yerlesim prs_takip.py ile ayni kaynaklardan: TS 38.211 7.4.1.7.2 (Gold dizisi, QPSK), 7.4.1.7.3 (comb, k' tablosu).
Yanki modeli (tek nokta hedef ya da isin izlemeden gelen yol ciftleri), her PRS RE'si icin:
    Y = a * X * exp(-j2pi f_k tau0) * exp(j2pi f_D t) * exp(j2pi f_k f_D t / f_c) + gurultu,   f_D = -2 v_r / lambda
    (ucuncu terim menzil gocudur: hedef 160 ms'de v*t kadar yer degistirir; telafi EDILMEZ).
Isleme: her comb grubunun (ayni alt tasiyicilar) gercek sembol zamanlariyla ayrik Fourier donusumu (Doppler, 1/T_obs adim)
        + alt tasiyicilar boyunca IFFT (menzil). Belirsizliksiz hiz penceresi +-lambda/(4 T_PRS); pencere disindaki hiz katlanir.
Tespit: radar_takip_35.tespit (P_FA = 1e-3, hucre sayisina gore esik), rmax = 600 m; dogru tespit = |menzil hatasi| < 3 menzil kutusu.
Guc: PRS RE basina enerji (EPRE) veri RE'leriyle ayni (guc yukseltme yok, VARSAYIM); ornek basina SNR = radar_takip_35.snr_ornek_db
     (37 dBm, 26 dBi, RCS -12,81 dBsm, NF 5 dB, X_SI, 98,28 MHz gurultu bandi).
Calistirma:  python prs_takip_n78.py        Cikti: cikti/prs_n78/
"""
import os, sys, time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import radar_takip_35 as rt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "cikti", "prs_n78"); os.makedirs(OUT, exist_ok=True)
KONFIG_CSV = os.path.join(HERE, "..", "..", "..", "ogretici", "veri", "ortak_prs_konfig.csv")

# ------------------------------------------------ PARAM
C, FC = rt.C, rt.fc                                # 3,5 GHz (npz'den)
LAM = C / FC
SCS, SLOT = 30e3, 0.5e-3                           # ortak izgara: 30 kHz, 1 slot = 0,5 ms (ortak_degerler.xlsx B6, B10)
TSYM = SLOT / 14                                   # ortalama sembol suresi (CP dahil); ilk sembolun 16 kappa'lik uzun CP'si yok sayildi
NPRB_HUCRE = 273                                   # 100 MHz, 30 kHz (TS 38.101-1 Tablo 5.3.2-1)
T_GOZLEM = 0.160                                   # kart: "160 ms gozlemde hiz cozunurlugu"
N_ID = 0
COMB_SATIR = {2: [0, 1], 4: [0, 2, 1, 3], 6: [0, 3, 1, 4, 2, 5], 12: [0, 6, 3, 9, 1, 7, 4, 10, 2, 8, 5, 11]}   # TS 38.211 Tablo 7.4.1.7.3-1
RMAX = 600.0

def konfigler():
    df = pd.read_csv(KONFIG_CSV)
    return {r.id: dict(id=r.id, periyot=int(r.periyot_slot), L=int(r.sembol), K=int(r.comb), bw=int(r.bw_prb),
                       l0=int(r.sembol_ofset), s0=int(r.slot_ofset), aciklama=r.aciklama) for r in df.itertuples()}

# ------------------------------------------------ PRS dizisi (prs_takip.py ile ayni)
def gold(c_init, n):
    m = 1600 + n + 31
    x1 = [0] * m; x2 = [0] * m
    x1[0] = 1
    for i in range(31): x2[i] = (c_init >> i) & 1
    for i in range(1600 + n):
        x1[i + 31] = x1[i + 3] ^ x1[i]
        x2[i + 31] = x2[i + 3] ^ x2[i + 2] ^ x2[i + 1] ^ x2[i]
    return np.array([x1[1600 + i] ^ x2[1600 + i] for i in range(n)])

_dizi = {}
def prs_dizi(slot, sembol, n):
    key = (slot, sembol, n)
    if key not in _dizi:
        c_init = ((1 << 22) * (N_ID // 1024) + (1 << 10) * (14 * slot + sembol + 1) * (2 * (N_ID % 1024) + 1) + N_ID % 1024) % (1 << 31)
        c = gold(c_init, 2 * n)
        _dizi[key] = ((1 - 2 * c[0::2]) + 1j * (1 - 2 * c[1::2])) / np.sqrt(2)
    return _dizi[key]

# ------------------------------------------------ PRS yerlesimi (160 ms)
class Yerlesim:
    def __init__(self, kf, t_gozlem=T_GOZLEM):
        self.kf = kf; K, L = kf["K"], kf["L"]
        assert L % K == 0, "TS 38.211: sembol sayisi comb'un kati olmali"
        self.nsc = kf["bw"] * 12; self.T = kf["periyot"] * SLOT
        self.n_occ = int(round(t_gozlem / self.T))
        ks, ts, gs, xs = [], [], [], []
        for o in range(self.n_occ):
            slot = kf["s0"] + o * kf["periyot"]
            for j in range(L):
                l = kf["l0"] + j; kp = COMB_SATIR[K][j % K]
                k = K * np.arange(self.nsc // K) + kp
                ks.append(k); ts.append(np.full(k.size, (slot * 14 + l) * TSYM)); gs.append(np.full(k.size, kp))
                xs.append(prs_dizi(slot % 20, l, self.nsc // K))
        self.k = np.concatenate(ks); self.t = np.concatenate(ts); self.g = np.concatenate(gs); self.X = np.concatenate(xs)
        self.fk = (self.k - NPRB_HUCRE * 12 / 2) * SCS          # tasiyici merkezine gore alt tasiyici frekansi (PRS, hucrenin 0. PRB'sinden baslar)
        self.t_orta = float(self.t.mean())
        # Doppler DFT: her comb grubu icin (alt tasiyici x zaman) matris ve (zaman x frekans) cekirdegi
        self.fax = (np.arange(self.n_occ) - self.n_occ // 2) / (self.n_occ * self.T)
        self.gruplar = []
        for kp in sorted(set(COMB_SATIR[K][j % K] for j in range(L))):
            idx = np.where(self.g == kp)[0]
            kk = np.unique(self.k[idx]); tt = np.unique(self.t[idx])
            sira = np.lexsort((self.t[idx], self.k[idx]))          # once alt tasiyici, sonra zaman
            self.gruplar.append((idx[sira], kk, tt.size, np.exp(-2j * np.pi * tt[:, None] * self.fax[None, :])))
        self.dr = C / (2 * self.nsc * SCS)
        self.rax = np.arange(self.nsc) * self.dr
        self.vax = (-self.fax * LAM / 2)[::-1]                    # artan sirada hiz ekseni
        self.vmax = LAM / (4 * self.T)
        self.n_re = self.k.size

    def yanki(self, yollar):
        """yollar: [(genlik, tau0 [s], f_D [Hz]), ...] -> PRS RE'lerinde gurultusuz alinan sinyal."""
        s = np.zeros(self.n_re, complex)
        for a, tau0, fd in yollar:
            s += a * np.exp(-2j * np.pi * self.fk * tau0) * np.exp(2j * np.pi * fd * self.t) * np.exp(2j * np.pi * self.fk * fd * self.t / FC)
        return s * self.X

    def isle(self, Y):
        """Y: PRS RE'lerinde alinan sinyal -> (menzil ekseni, hiz ekseni, |RD|^2)."""
        Hs = Y / self.X
        D = np.zeros((self.nsc, self.n_occ), complex)
        for idx, kk, nt, E in self.gruplar:
            D[kk] = Hs[idx].reshape(kk.size, nt) @ E
        rd = np.fft.ifft(D, axis=0)[:, ::-1]
        return self.rax, self.vax, np.abs(rd) ** 2

def olc(yer, r, v, snr_db, rng):
    """Tek nokta hedef (gorus hatti, radar denklemi). Donus: dogru tespit, yanlis alarm, menzil hatasi, hiz hatasi (ham), hiz hatasi (katlanmis)."""
    a = 10 ** (snr_db / 20) if np.isfinite(snr_db) else 0.0
    Y = yer.yanki([(a, 2 * r / C, -2 * v / LAM)]) if a > 0 else np.zeros(yer.n_re, complex)
    Y = Y + (rng.normal(size=yer.n_re) + 1j * rng.normal(size=yer.n_re)) / np.sqrt(2)
    rax, vax, P = yer.isle(Y)
    ok, re, ve = rt.tespit(rax, vax, P, rmax=RMAX)
    r_ref = r + v * yer.t_orta
    dogru = bool(ok and abs(re - r_ref) < 3 * yer.dr)
    ev = ve - v
    return dogru, bool(ok and not dogru), re - r_ref, ev, (ev + yer.vmax) % (2 * yer.vmax) - yer.vmax

def p90(x): return float(np.percentile(np.abs(x), 90)) if len(x) else np.nan

# ------------------------------------------------ calistirma
if __name__ == "__main__":
    t0 = time.time()
    KF = konfigler()
    ids = [k for k in KF if KF[k]["periyot"] > 0]
    print(f"PRS n78: fc = {FC / 1e9:.2f} GHz, lambda = {100 * LAM:.2f} cm, SCS = {SCS / 1e3:.0f} kHz, hucre {NPRB_HUCRE} PRB, gozlem {1e3 * T_GOZLEM:.0f} ms, "
          f"RCS = {rt.RCS_DBSM} dBsm, X_SI = {rt.X_SI_DB} dB, gurultu bandi {rt.W / 1e6:.2f} MHz")
    # 1) yapilandirma tablosu (hesap)
    tab = []
    for i in ids:
        kf = KF[i]; y = Yerlesim(kf)
        top_re = NPRB_HUCRE * 12 * 14 * (T_GOZLEM / SLOT)
        tab.append(dict(id=i, periyot_ms=y.T * 1e3, sembol=kf["L"], comb=kf["K"], bw_prb=kf["bw"], sembol_ofset=kf["l0"],
                        bant_MHz=y.nsc * SCS / 1e6, menzil_kutusu_m=y.dr, n_firsat=y.n_occ, prs_re_160ms=y.n_re,
                        alfa_prs_yuzde=100 * y.n_re / top_re, islem_kazanci_db=10 * np.log10(y.n_re),
                        en_buyuk_hiz_ms=y.vmax, hiz_cozunurlugu_ms=LAM / (2 * y.n_occ * y.T)))
    tab = pd.DataFrame(tab)
    pd.set_option("display.width", 250)
    print("\n1) Yapilandirmalar (hesap)\n" + tab.round(3).to_string(index=False))

    # 2) Monte Carlo: menzile gore Pd (X_SI = 40), 300 m'de X_SI = 30
    Rs, NDEN = [100, 200, 300, 400, 500], 160
    sat = []
    for x in (40.0, 30.0):
        rt.X_SI_DB = x
        for i in ids:
            y = Yerlesim(KF[i]); rng = np.random.default_rng(7)
            for r in (Rs if x == 40.0 else [300]):
                snr = rt.snr_ornek_db(r)
                ok, yan, er, evh, evk = 0, 0, [], [], []
                for _ in range(NDEN):
                    v0 = rng.uniform(-30, 30); rg = r + rng.uniform(-6, 6)
                    d, f_, e_r, e_vh, e_vk = olc(y, rg, v0, snr, rng)
                    ok += d; yan += f_
                    if d: er.append(e_r); evh.append(e_vh); evk.append(e_vk)
                sat.append(dict(id=i, X_SI_dB=x, menzil_m=r, snr_ornek_db=snr, pd=ok / NDEN, yanlis_tespit=yan / NDEN,
                                menzil_p90_m=p90(er), hiz_p90_ham_ms=p90(evh), hiz_p90_katlanmis_ms=p90(evk)))
        print(f"   X_SI = {x:.0f} dB bitti ({time.time() - t0:.0f} s)", flush=True)
    rt.X_SI_DB = 40.0
    mc = pd.DataFrame(sat); mc.to_csv(os.path.join(OUT, "prs_n78_monte_carlo.csv"), index=False)
    piv = mc[mc.X_SI_dB == 40].pivot(index="id", columns="menzil_m", values="pd").loc[ids]
    print("\n2) Pd, menzile gore (X_SI = 40 dB, 160 deneme, hiz -30..30 m/s)\n" + piv.round(2).to_string())
    m300 = mc[mc.menzil_m == 300].pivot(index="id", columns="X_SI_dB", values="pd").loc[ids]
    print("\n   Pd (300 m): X_SI = 40 / 30 dB\n" + m300.round(2).to_string())
    d300 = mc[(mc.menzil_m == 300) & (mc.X_SI_dB == 40)].set_index("id").loc[ids]
    print("\n   300 m, X_SI = 40 dB, dogru tespitlerde %90 yuzdelik hatalar (menzil / hiz ham / hiz katlanmis):")
    for i in ids:
        s = d300.loc[i]; print(f"   {i:4s} menzil {s.menzil_p90_m:6.2f} m | hiz ham {s.hiz_p90_ham_ms:6.2f} m/s | katlanmis {s.hiz_p90_katlanmis_ms:5.2f} m/s")
    # Pmd <= %5 saglayan en buyuk menzil
    tab["pd_300m_xsi40"] = [m300.loc[i, 40.0] for i in ids]; tab["pd_300m_xsi30"] = [m300.loc[i, 30.0] for i in ids]
    tab["pd095_en_buyuk_menzil_m"] = [max([r for r in Rs if piv.loc[i, r] >= 0.95], default=np.nan) for i in ids]
    tab.to_csv(os.path.join(OUT, "prs_n78_ozet.csv"), index=False)

    # 3) Pf1 (hedefsiz) K1 ve K4
    rng = np.random.default_rng(11)
    for i in ("K1", "K4"):
        y = Yerlesim(KF[i]); n = 1000
        k = sum(bool(rt.tespit(*y.isle((rng.normal(size=y.n_re) + 1j * rng.normal(size=y.n_re)) / np.sqrt(2)), rmax=RMAX)[0]) for _ in range(n))
        print(f"\n3) Pf1 {i}: {k}/{n} hedefsiz gozlemde alarm -> %{100 * k / n:.2f} (hedef <= %5)", end="")
    print()
    hizli = np.mean(np.abs(np.random.default_rng(1).uniform(-30, 30, 100000)) > LAM / (4 * 5e-3))
    print(f"   hiz dagilimi -30..30 m/s icinde |v| > {LAM / (4 * 5e-3):.2f} m/s (K1 belirsizlik siniri) olan oran: {hizli:.2f}")

    # 4) sekiller: Pd-menzil ve K1 / K4 RD haritasi
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.2), gridspec_kw=dict(width_ratios=[1.3, 1]))
    renk = plt.cm.tab20(np.linspace(0, 1, len(ids)))
    for c, i in zip(renk, ids):
        ax[0].plot(Rs, piv.loc[i], "o-", color=c, label=f"{i} ({KF[i]['bw']} PRB, K={KF[i]['K']}, L={KF[i]['L']}, {KF[i]['periyot'] // 2} ms)")
    ax[0].axhline(0.95, color="gray", ls=":"); ax[0].set_xlabel("İHA menzili (m)"); ax[0].set_ylabel("tespit olasılığı Pd")
    ax[0].set_title("PRS ile tespit, n78 / 3,5 GHz / 100 MHz hücre (X_SI = 40 dB, 160 ms)", fontsize=9); ax[0].grid(alpha=0.3)
    ax[0].legend(fontsize=6.5, ncol=1, loc="lower left")
    xx = np.arange(len(ids))
    ax[1].bar(xx - 0.2, m300[40.0].values, 0.4, color="#2563eb", label="X_SI = 40 dB")
    ax[1].bar(xx + 0.2, m300[30.0].values, 0.4, color="#16a34a", label="X_SI = 30 dB")
    ax[1].axhline(0.95, color="gray", ls=":"); ax[1].set_xticks(xx); ax[1].set_xticklabels(ids, fontsize=8)
    ax[1].set_ylabel("Pd (300 m)"); ax[1].set_ylim(0, 1.05); ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3, axis="y")
    ax[1].set_title("300 m'de tespit olasılığı (simülasyon)", fontsize=9)
    rng = np.random.default_rng(3)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "prs_n78_pd_menzil.png"), dpi=140); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    for i, axx in zip(("K1", "K4"), ax):
        y = Yerlesim(KF[i]); r0, v0 = 300.0, 3.0
        Y = y.yanki([(10 ** (rt.snr_ornek_db(r0) / 20), 2 * r0 / C, -2 * v0 / LAM)])
        Y = Y + (rng.normal(size=y.n_re) + 1j * rng.normal(size=y.n_re)) / np.sqrt(2)
        rax, vax, P = y.isle(Y); s = rax < 450
        db = 10 * np.log10(P[s] / np.median(P[s]))
        im = axx.imshow(db.T, origin="lower", aspect="auto", cmap="magma", vmin=0, vmax=25, extent=[rax[s][0], rax[s][-1], vax[0], vax[-1]])
        fig.colorbar(im, ax=axx, fraction=0.04, label="medyana göre güç (dB)")
        axx.plot(r0 + v0 * y.t_orta, v0, "o", mfc="none", mec="#22d3ee", ms=14, mew=1.6)
        axx.set_xlim(240, 360); axx.set_xlabel("Menzil (m)"); axx.set_ylabel("Radyal hız (m/s)")
        axx.set_title(f"{i}: {KF[i]['bw']} PRB ({y.nsc * SCS / 1e6:.2f} MHz) → menzil kutusu {y.dr:.2f} m\n"
                      f"hız penceresi ±{y.vmax:.2f} m/s, {y.n_occ} PRS fırsatı, İHA 300 m / 3 m/s", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "prs_n78_rd_K1_K4.png"), dpi=140); plt.close(fig)
    print(f"\nbitti ({time.time() - t0:.0f} s); cikti: {os.path.relpath(OUT)}")

"""[Nihat, gorev kartlari 4, adim 1'in kampus karsiligi + PRS] ITU EEF kampus sahnesinde 4,9 GHz -> 3,5 GHz.
Neden ayri betik: ogretici/itu_sahne/prs_itu.py eski prs_takip.py'ye bagli (84 PRB, art arda slot tekrari, GAP = 1, 4,9 GHz);
periyotlu K1..K11 PRS ayarlarini ve 3,5 GHz'i desteklemiyor. Asil dosyalara dokunulmaz.
Bolum 1: yol kazanci. Kampus sahnesinde (ogretici/itu_sahne/sahne.xml, gNB EEF catisinda) 200 aday IHA konumu (yukseklik 1,5-300 m,
         3B uzaklik 30-300 m, bina icinde olmayan) icin Sionna RT yollari 4,9 ve 3,5 GHz'te cozulur (max_depth = 3, rt_sehir.py ile ayni);
         5 konum secilir: 3'u gorus hatli (farkli uzakliklar), 2'si gorus hatsiz ama yol bulunan. Tum adaylarda istatistik de verilir.
Bolum 2: PRS ile tespit, 3,5 GHz. prs_itu.py yontemi (TR 38.765 Tablo A-1: TX-hedef ve hedef-RX baglantilarinin birlestirilmesi):
         gNB->IHA yollari Sionna RT'den, yanki = gidis yolu i x donus yolu j, genlik a_i a_j sqrt(4 pi RCS)/lambda, -25 dB alti ciftler atilir.
         PRS yerlesimi ve isleme prs_takip_n78.py'den (K1, K2, K3, K4). IHA konumlari TR'deki gibi: yukseklik 25-300 m, yatay hiz 0-50 m/s.
Calistirma:  python itu_35ghz.py        Cikti: cikti/itu_35/
"""
import json, os, sys, time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely import wkt
from shapely.geometry import Point
import sionna.rt as srt
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, PathSolver
import prs_takip_n78 as pn
rt = pn.rt

HERE = os.path.dirname(os.path.abspath(__file__))
ITU = os.path.join(HERE, "..", "..", "..", "ogretici", "itu_sahne")
OUT = os.path.join(HERE, "..", "cikti", "itu_35"); os.makedirs(OUT, exist_ok=True)
O = json.load(open(os.path.join(ITU, "sahne_ozet.json"), encoding="utf-8")); GNB = np.array(O["gnb_xyz_m"])
BINALAR = [(wkt.loads(b["wkt"]), b["h"]) for b in json.load(open(os.path.join(ITU, "bina_izdusumleri.json")))]
t0 = time.time()
def log(m): print(f"[{time.time() - t0:6.1f} s] {m}", flush=True)

def bina_icinde(x, y, z): return any(z < h and p.contains(Point(x, y)) for p, h in BINALAR)

def sahne(fc):
    s = load_scene(os.path.join(ITU, "sahne.xml"), merge_shapes=True)
    s.frequency = fc
    s.tx_array = PlanarArray(num_rows=1, num_cols=1, pattern="iso", polarization="V")
    s.rx_array = PlanarArray(num_rows=1, num_cols=1, pattern="iso", polarization="V")
    s.add(Transmitter(name="gnb", position=[float(x) for x in GNB], power_dbm=rt.PT_DBM))
    return s

def konumlar(n, h_min, h_max, d_min, d_max, rng, hiz=False):
    out = []
    while len(out) < n:
        x, y = rng.uniform(-d_max, d_max, 2); z = rng.uniform(h_min, h_max)
        d = np.linalg.norm(np.array([x, y, z]) - GNB)
        if not (d_min <= d <= d_max) or bina_icinde(x, y, z): continue
        if hiz:
            v = rng.uniform(0, 50.0); psi = rng.uniform(0, 2 * np.pi); out.append((x, y, z, v * np.cos(psi), v * np.sin(psi)))
        else:
            out.append((x, y, z))
    return np.array(out)

def coz(fc, P, derinlik=3):
    s = sahne(fc)
    for i, p in enumerate(P): s.add(Receiver(name=f"rx{i:03d}", position=[float(p[0]), float(p[1]), float(p[2])]))
    paths = PathSolver()(s, max_depth=derinlik, samples_per_src=1_000_000)
    a, tau = paths.cir(normalize_delays=False, out_type="numpy")
    A = np.array(a)[:, 0, 0, 0, :, 0]; TAU = np.array(tau)[:, 0, :]
    p_los = PathSolver()(s, max_depth=1, los=True, specular_reflection=False, refraction=False, samples_per_src=200_000)
    _, tl = p_los.cir(normalize_delays=False, out_type="numpy")
    los = (np.array(tl).reshape(len(P), -1) > 0).any(axis=1)
    return paths, A, TAU, los

# ================================================ Bolum 1: yol kazanci
rng = np.random.default_rng(21)
ADAY = konumlar(200, 1.5, 300.0, 30.0, 300.0, rng)
d3 = np.linalg.norm(ADAY - GNB, axis=1)
kaz, losd = {}, {}
for fc in (4.9e9, 3.5e9):
    _, A, TAU, los = coz(fc, ADAY)
    kaz[fc] = np.array([10 * np.log10(np.sum(np.abs(A[i][TAU[i] > 0]) ** 2) + 1e-30) for i in range(len(ADAY))]); losd[fc] = los
    log(f"{fc / 1e9:.1f} GHz: {len(ADAY)} aday, LOS {int(los.sum())}, yol bulunan {int((kaz[fc] > -299).sum())}")
gec = (kaz[4.9e9] > -299) & (kaz[3.5e9] > -299)
secim = []
for lo, hi in ((30, 100), (100, 200), (200, 300)):
    c = np.where(gec & losd[3.5e9] & (d3 >= lo) & (d3 < hi) & (ADAY[:, 2] >= 25))[0]
    if len(c): secim.append(int(c[0]))
c = np.where(gec & ~losd[3.5e9])[0]
secim += [int(i) for i in c[:5 - len(secim)]]
fs = lambda f: 20 * np.log10(3e8 / f / (4 * np.pi * d3))
t1 = pd.DataFrame(dict(aday=secim, x_m=ADAY[secim, 0], y_m=ADAY[secim, 1], z_m=ADAY[secim, 2], uzaklik_3b_m=d3[secim],
                       los=losd[3.5e9][secim], kazanc_49_db=kaz[4.9e9][secim], kazanc_35_db=kaz[3.5e9][secim],
                       fark_35_eksi_49_db=kaz[3.5e9][secim] - kaz[4.9e9][secim],
                       serbest_uzay_49_db=fs(4.9e9)[secim], serbest_uzay_35_db=fs(3.5e9)[secim]))
t1.to_csv(os.path.join(OUT, "yol_kazanci_5_konum_itu.csv"), index=False, float_format="%.2f")
pd.set_option("display.width", 220)
print("\nBolum 1: ITU EEF kampusu, 5 konumda yol kazanci (dB; tum gecerli yollar, max_depth = 3, izotropik)\n" + t1.round(2).to_string(index=False))
f = kaz[3.5e9][gec] - kaz[4.9e9][gec]; L = losd[3.5e9][gec]
print(f"tum adaylar ({gec.sum()} konumda iki frekansta yol var): fark ortalama {f.mean():.2f} dB, medyan {np.median(f):.2f} dB | "
      f"LOS ({L.sum()}) ortalama {f[L].mean():.2f} dB | NLOS ({(~L).sum()}) ortalama {f[~L].mean() if (~L).any() else np.nan:.2f} dB "
      f"(serbest uzay: {20 * np.log10(4.9 / 3.5):.2f} dB)")
print(f"LOS siniflandirmasi iki frekansta ayni: {bool(np.array_equal(losd[4.9e9], losd[3.5e9]))}")

# ================================================ Bolum 2: PRS ile tespit (3,5 GHz)
N_KONUM, N_DENEME, ESIK_DB = 300, 10, 25.0
KON = konumlar(N_KONUM, 25.0, 300.0, 10.0, 300.0, np.random.default_rng(5), hiz=True)
paths, A, TAU, los = coz(rt.fc, KON[:, :3])
def vec(th, ph): return np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)], axis=-1)
KDEP = vec(np.array(paths.theta_t)[:, 0, :], np.array(paths.phi_t)[:, 0, :])
KARR = -vec(np.array(paths.theta_r)[:, 0, :], np.array(paths.phi_r)[:, 0, :])
log(f"PRS konumlari: {N_KONUM}, LOS {int(los.sum())}, en fazla {A.shape[1]} yol/konum")
LAM = rt.LAM; RCS_LIN = 10 ** (rt.RCS_DBSM / 10); G_DBI = rt.G_DBI
YARIM_DEMET = np.degrees(np.arccos(1 - 4 * np.pi / 10 ** (G_DBI / 10) / (2 * np.pi)))
GURULTU_DBM = -174 + 10 * np.log10(rt.W) + rt.NF + rt.X_SI_DB          # radar_takip_35 ile ayni RE basina gurultu (98,28 MHz)
SNR_KAT = 10 ** ((rt.PT_DBM - GURULTU_DBM) / 20)

def ciftler(i):
    ok = TAU[i] > 0
    if not ok.any(): return None
    u = KON[i, :3] - GNB; R = np.linalg.norm(u); u = u / R
    gdb = np.where(KDEP[i][ok] @ u >= np.cos(np.radians(YARIM_DEMET)), G_DBI, 0.0)
    g = 10 ** (gdb / 20) * A[i][ok]; ka = KARR[i][ok]; tau = TAU[i][ok]
    amp = (g[:, None] * g[None, :]) * np.sqrt(4 * np.pi * RCS_LIN) / LAM * SNR_KAT
    ts = tau[:, None] + tau[None, :]
    kv = (ka[:, None, :] + ka[None, :, :]) / LAM
    tut = np.abs(amp) ** 2 >= np.abs(amp).max() ** 2 * 10 ** (-ESIK_DB / 10)
    v = np.array([KON[i, 3], KON[i, 4], 0.0])
    return amp[tut], ts[tut], -(kv[tut] @ v), R, float(v @ u), int(tut.sum())

# dogrulama: LOS x LOS cifti SNR'i radar denklemiyle ayni olmali
i0 = int(np.argmax(los)); c0 = ciftler(i0)
print(f"DOGRULAMA (konum {i0}, R = {c0[3]:.1f} m): en guclu yanki cifti SNR = {20 * np.log10(np.abs(c0[0]).max()):.2f} dB/RE | "
      f"radar_takip_35.snr_ornek_db = {rt.snr_ornek_db(c0[3]):.2f} dB/RE")

KF = pn.konfigler(); IDS = ["K1", "K2", "K3", "K4"]
sat = []; rng = np.random.default_rng(9)
for kid in IDS:
    y = pn.Yerlesim(KF[kid])
    for i in range(N_KONUM):
        c = ciftler(i)
        if c is None:
            sat.append(dict(id=kid, konum=i, pd=0.0, R=np.linalg.norm(KON[i, :3] - GNB), vr=np.nan, los=bool(los[i]), n_cift=0)); continue
        amp, ts, fd, R, vr, nc = c
        sig = y.yanki(list(zip(amp, ts, fd)))
        ok = 0; er, ev = [], []
        for _ in range(N_DENEME):
            Y = sig + (rng.normal(size=y.n_re) + 1j * rng.normal(size=y.n_re)) / np.sqrt(2)
            det, re, ve = rt.tespit(*y.isle(Y), rmax=pn.RMAX)
            rref = R + vr * y.t_orta
            if det and abs(re - rref) < 3 * y.dr:
                ok += 1; er.append(re - rref); ev.append((ve - vr + y.vmax) % (2 * y.vmax) - y.vmax)
        sat.append(dict(id=kid, konum=i, pd=ok / N_DENEME, R=R, vr=vr, los=bool(los[i]), n_cift=nc,
                        menzil_hata_ort_m=float(np.mean(np.abs(er))) if er else np.nan,
                        hiz_hata_katlanmis_ort_ms=float(np.mean(np.abs(ev))) if ev else np.nan))
    log(f"{kid} bitti")
df = pd.DataFrame(sat); df.to_csv(os.path.join(OUT, "prs_itu_35_sonuclar.csv"), index=False, float_format="%.4f")
satir = []
for kid in IDS:
    d = df[df.id == kid]; y = pn.Yerlesim(KF[kid])
    satir.append(f"{kid} ({KF[kid]['bw']} PRB, comb {KF[kid]['K']}, {KF[kid]['L']} sembol, {KF[kid]['periyot'] // 2} ms, {y.n_occ} firsat): "
                 f"ort. Pd {d.pd.mean():.2f} (Pmd {100 * (1 - d.pd.mean()):.1f} %) | LOS ({int(d.los.sum())}) {d[d.los].pd.mean():.2f} | "
                 f"NLOS ({int((~d.los).sum())}) {d[~d.los].pd.mean() if (~d.los).any() else float('nan'):.2f} | Pd>=0,95 konum orani {np.mean(d.pd >= 0.95):.2f} | "
                 f"|v_r| > {y.vmax:.2f} m/s (katlanan) konum orani {np.mean(np.abs(d.vr) > y.vmax):.2f}")
    for lo, hi in ((0, 100), (100, 200), (200, 300)):
        dd = d[(d.R >= lo) & (d.R < hi)]
        if len(dd): satir.append(f"      3B uzaklik {lo:3d}-{hi:3d} m: {len(dd):3d} konum, ort. Pd {dd.pd.mean():.2f}")
    dd = d[d.pd > 0]
    satir.append(f"      dogru tespitlerde ortalama |menzil hatasi| medyan {dd.menzil_hata_ort_m.median():.2f} m, "
                 f"katlanmis |hiz hatasi| medyan {dd.hiz_hata_katlanmis_ort_ms.median():.2f} m/s")
print("\nBolum 2: PRS ile tespit, ITU EEF kampusu, 3,5 GHz, X_SI = 40 dB, RCS -12,81 dBsm\n" + "\n".join(satir))
open(os.path.join(OUT, "prs_itu_35_ozet.txt"), "w", encoding="utf-8").write("\n".join(satir) + "\n")

fig, ax = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw=dict(width_ratios=[1.1, 1]))
for p, h in BINALAR:
    xs, ys = p.exterior.xy if p.geom_type == "Polygon" else p.geoms[0].exterior.xy
    ax[0].fill(xs, ys, color="#d1d5db", ec="#6b7280", lw=0.3)
d = df[df.id == "K1"]
sc = ax[0].scatter(KON[d.konum, 0], KON[d.konum, 1], c=d.pd, cmap="RdYlGn", vmin=0, vmax=1, s=30, edgecolor="black", linewidth=0.3)
ax[0].plot(GNB[0], GNB[1], "*", color="yellow", ms=16, mec="black", label="gNB (EEF çatısı)")
ax[0].set_xlim(-310, 310); ax[0].set_ylim(-310, 310); ax[0].set_aspect("equal"); ax[0].legend(fontsize=8, loc="lower left")
fig.colorbar(sc, ax=ax[0], fraction=0.04, label="Pd (10 deneme)")
ax[0].set_title("ITU EEF, 3,5 GHz, PRS K1 (48 PRB, comb 4, 4 sembol, 5 ms, 160 ms)\nyankı: Sionna RT ışın izleme", fontsize=9)
for kid, c in zip(IDS, ["#2563eb", "#ea580c", "#dc2626", "#16a34a"]):
    dd = df[df.id == kid]; b = np.arange(0, 301, 50)
    ax[1].plot(b[:-1] + 25, [dd[(dd.R >= x) & (dd.R < x + 50)].pd.mean() for x in b[:-1]], "o-", color=c, label=kid)
ax[1].axhline(0.95, color="gray", ls=":"); ax[1].set_ylim(-0.02, 1.02); ax[1].grid(alpha=0.3); ax[1].legend()
ax[1].set_xlabel("gNB'ye 3B uzaklık (m)"); ax[1].set_ylabel("ortalama Pd"); ax[1].set_title("Uzaklığa göre tespit (TR hedefi Pd ≥ 0,95)", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "prs_itu_35_sonuc.png"), dpi=140); plt.close(fig)
log("bitti")

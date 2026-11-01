"""PRS ile IHA tespiti, ITU EEF sahnesinde, YANKI SIONNA RT ISIN IZLEMESIYLE (yansimalar dahil; yalnizca LOS bakilmiyor).
Yontem (TR 38.765 Table A-1: "Concatenation of TX-target and target-RX links"):
  1) gNB -> IHA yollari Sionna RT'den (max_depth=3: yer yansimasi + bina yansimalari). Monostatic oldugundan donus yollari ayni yollarin tersi (resiprosite).
  2) Gidis yolu i x donus yolu j cifti = bir yanki yolu: gecikme tau_i+tau_j, genlik a_i*a_j*sqrt(4*pi*RCS)/lambda, Doppler iki ayagin toplami.
  3) Zayif ciftler atilir (TR: "power threshold for path dropping after concatenation": -25 dB).
  4) PRS (prs_takip.py ile ayni: K=4, L=4, 84 PRB) bu yanki kanalindan gecer, 2B FFT, ayni tespit fonksiyonu.
Calistirma:  python prs_itu.py     (DRJIT_LIBLLVM_PATH ayarli olmali; sahne_uret.py once calismis olmali)
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

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "sionna_sehir"))
import prs_takip as pt                       # PRS yerlesimi, sabitler (rt.RCS_DBSM = -12,81 burada ayarlanir); import film/analiz calistirmaz
rt = pt.rt
O = json.load(open(os.path.join(HERE, "sahne_ozet.json"), encoding="utf-8")); GNB = np.array(O["gnb_xyz_m"])
BINALAR = [(wkt.loads(b["wkt"]), b["h"]) for b in json.load(open(os.path.join(HERE, "bina_izdusumleri.json")))]

# ------------------------------------------------ PARAM (varsayimlar acikca)
N_KONUM, N_DENEME, TEKRARLAR = 300, 10, [8, 16, 32]
MENZIL_MAX, H_MIN, H_MAX, V_MAX = 300.0, 25.0, 300.0, 50.0     # TR: yukseklik 25-300 m uniform, hiz 0-180 km/s = 0-50 m/s (menzil siniri BIZIM kapsam karari)
RCS_LIN = 10 ** (rt.RCS_DBSM / 10)                              # -12,81 dBsm sabit (aci bagimsiz; sapma 3,74 dB yok sayildi)
G_DBI = rt.G_DBI                                                # 26 dBi anten (eski modelle ayni VARSAYIM)
YARIM_DEMET = np.degrees(np.arccos(1 - 4 * np.pi / 10 ** (G_DBI / 10) / (2 * np.pi)))   # duz-tepe koni yaklasimi: Omega=4pi/G -> yaklasik 5,7 derece
ESIK_DB = 25.0                                                  # yanki cifti atma esigi (TR: -25 dB secenegi)
TOL_M = 10.0                                                    # dogru tespit: |olculen - gercek menzil| < 10 m (TR konum hedefi)
GURULTU_DBM = -174 + 10 * np.log10(pt.W) + rt.NF + rt.X_SI_DB   # eski modelle ayni: kTBF + artik oz-girisim
SNR_KATSAYI = 10 ** ((rt.PT_DBM - GURULTU_DBM) / 20)            # genlik olcegi: gurultu sigma^2=1 birimi
EK = ""
if len(sys.argv) > 1 and sys.argv[1] == "ops":                  # TR Table A-1: "optionally between 1.5m and 300m" -> binalarin etkisini gormek icin
    H_MIN, N_KONUM, TEKRARLAR, EK = 1.5, 600, [16, 32], "_ops"
rng = np.random.default_rng(5)

# ------------------------------------------------ sahne
scene = load_scene(os.path.join(HERE, "sahne.xml"), merge_shapes=True)
scene.frequency = rt.fc if hasattr(rt, "fc") else 4.9e9
scene.tx_array = PlanarArray(num_rows=1, num_cols=1, pattern="iso", polarization="V")
scene.rx_array = PlanarArray(num_rows=1, num_cols=1, pattern="iso", polarization="V")
scene.add(Transmitter(name="gnb", position=[float(x) for x in GNB], power_dbm=rt.PT_DBM))
LAM = float(rt.LAM)                          # radar_takip.py ile ayni dalga boyu (Sionna scene.frequency dizi dondurur)

def bina_icinde(x, y, z):
    return any(z < h and p.contains(Point(x, y)) for p, h in BINALAR)

def konum_ornekle():
    out = []
    while len(out) < N_KONUM:
        x, y = rng.uniform(-MENZIL_MAX, MENZIL_MAX, 2); z = rng.uniform(H_MIN, H_MAX)
        d = np.linalg.norm(np.array([x, y, z]) - GNB)
        if not (10.0 <= d <= MENZIL_MAX) or bina_icinde(x, y, z): continue
        v = rng.uniform(0, V_MAX); psi = rng.uniform(0, 2 * np.pi)
        out.append((x, y, z, v * np.cos(psi), v * np.sin(psi)))
    return np.array(out)

def vec(th, ph): return np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)], axis=-1)

t0 = time.time()
KON = konum_ornekle()
for i, p in enumerate(KON): scene.add(Receiver(name=f"rx{i:03d}", position=[float(p[0]), float(p[1]), float(p[2])]))
paths = PathSolver()(scene, max_depth=3, samples_per_src=1_000_000)
a, tau_ = paths.cir(normalize_delays=False, out_type="numpy")
A = np.array(a)[:, 0, 0, 0, :, 0]; TAU = np.array(tau_)[:, 0, :]
KDEP = vec(np.array(paths.theta_t)[:, 0, :], np.array(paths.phi_t)[:, 0, :])          # gNB'den cikis yonu (ilerleme yonu)
KARR = -vec(np.array(paths.theta_r)[:, 0, :], np.array(paths.phi_r)[:, 0, :])         # IHA'ya varis, ilerleme yonu (Sionna varis acisi kaynaga bakar; yol_incele.py ile dogrulandi)
print(f"yol cozumu: {len(KON)} konum, en fazla {A.shape[1]} yol/konum, {time.time()-t0:.0f} s", flush=True)

def yanki_ciftleri(i):
    """Konum i icin yanki yolu ciftleri: genlik (gurultu birimi), gecikme toplami, Doppler katsayisi (v ile carpilacak vektor)."""
    ok = TAU[i] > 0
    if not ok.any(): return None
    u = (KON[i, :3] - GNB); R = np.linalg.norm(u); u /= R
    cosb = np.cos(np.radians(YARIM_DEMET))
    gdb = np.where(KDEP[i][ok] @ u >= cosb, G_DBI, 0.0)                               # huzme IHA'ya cevrili: ana lobda 26 dBi, disinda 0 dBi (VARSAYIM)
    g = 10 ** (gdb / 20) * A[i][ok]                                                  # bacak genligi: a * sqrt(G)
    karr = KARR[i][ok]; tau = TAU[i][ok]
    amp = (g[:, None] * g[None, :]) * np.sqrt(4 * np.pi * RCS_LIN) / LAM * SNR_KATSAYI
    ts = tau[:, None] + tau[None, :]
    kv = karr[:, None, :] + karr[None, :, :]                                         # Doppler: (v.k_i + v.k_j)/lambda
    guc = np.abs(amp) ** 2
    tut = guc >= guc.max() * 10 ** (-ESIK_DB / 10)
    return amp[tut], ts[tut], kv[tut] / LAM, R, u, int(ok.sum()), int(tut.sum())

def olc_konum(i, tekrar, n_deneme):
    c = yanki_ciftleri(i)
    if c is None: return None
    amp, ts, kv, R, u, n_yol, n_cift = c
    v = np.array([KON[i, 3], KON[i, 4], 0.0]); fd = kv @ v
    if tekrar not in pt._yer: pt._yer[tekrar] = pt.prs_yerlesim(tekrar)
    ks, ns, _ = pt._yer[tekrar]; nt = (tekrar - 1) * pt.GAP * 14 + 14
    sig = np.zeros(len(ks), complex)
    for k in range(len(amp)):
        sig += amp[k] * np.exp(-1j * 2 * np.pi * ks * pt.SCS * ts[k]) * np.exp(1j * 2 * np.pi * ns * pt.TSYM * fd[k])
    ok = 0; hv = []
    for _ in range(n_deneme):
        H = np.zeros((pt.NSC, nt), complex); H[ks, ns] = sig + (rng.normal(size=sig.shape) + 1j * rng.normal(size=sig.shape)) / np.sqrt(2)
        rd = np.fft.fftshift(np.fft.fft(np.fft.ifft(H, axis=0), axis=1), axes=1)
        rax = np.arange(pt.NSC) * 3e8 / (2 * pt.W); vax = (np.arange(nt) - nt // 2) / (nt * pt.TSYM) * LAM / 2
        s = np.abs(vax) < pt.VAMB
        det, re, ve = rt.tespit(rax, vax[s], (np.abs(rd) ** 2)[:, s], rmax=600.0)
        if det and abs(re - R) < TOL_M: ok += 1; hv.append(ve - (v @ u))
    return ok / n_deneme, hv, R, float(v @ u), n_yol, n_cift

# ------------------------------------------------ dogrulama: LOS x LOS cifti, radar denklemiyle ayni SNR'i vermeli
i0 = int(np.argmax([(TAU[i] > 0).sum() == 2 for i in range(len(KON))]))
c = yanki_ciftleri(i0); R0 = c[3]
lc = int(np.argmin(np.where(TAU[i0] > 0, TAU[i0], np.inf)))
g_l = 10 ** (G_DBI / 20) * abs(A[i0][lc]); snr_rt = 20 * np.log10(g_l ** 2 * np.sqrt(4 * np.pi * RCS_LIN) / LAM * SNR_KATSAYI)
print(f"DOGRULAMA (konum {i0}, R={R0:.1f} m): isin-izleme LOS x LOS cifti SNR = {snr_rt:.2f} dB/RE | radar denklemi (radar_takip.snr_ornek_db) = {rt.snr_ornek_db(R0):.2f} dB/RE", flush=True)

# ------------------------------------------------ Monte Carlo
sat = []
for ti, tekrar in enumerate(TEKRARLAR):
    for i in range(len(KON)):
        r = olc_konum(i, tekrar, N_DENEME)
        if r is None: sat.append(dict(konum=i, tekrar=tekrar, pd=0.0, R=np.linalg.norm(KON[i, :3] - GNB), vr=np.nan, n_yol=0, n_cift=0, hiz_hata=np.nan)); continue
        pdv, hv, R, vr, ny, nc = r
        sat.append(dict(konum=i, tekrar=tekrar, pd=pdv, R=R, vr=vr, n_yol=ny, n_cift=nc, hiz_hata=float(np.mean(np.abs(hv))) if hv else np.nan))
    print(f"tekrar={tekrar} bitti ({time.time()-t0:.0f} s)", flush=True)
df = pd.DataFrame(sat)
df["x"] = KON[df.konum, 0]; df["y"] = KON[df.konum, 1]; df["z"] = KON[df.konum, 2]
# LOS: en kisa gecerli yol dogrudan mesafe ile ayni mi (<0,5 m fark)
tmin = np.array([np.min(np.where(TAU[i] > 0, TAU[i], np.inf)) * 3e8 for i in range(len(KON))])
Rg = np.linalg.norm(KON[:, :3] - GNB, axis=1)
lc_idx = [int(np.argmin(np.where(TAU[i] > 0, TAU[i], np.inf))) for i in range(len(KON))]
dogru_var = np.abs(tmin - Rg) < 0.5                                            # uzunlugu dogrudan mesafeyle ayni olan bir yol var (duvarin icinden gecen de olabilir: Sionna refraction acik)
ek_kayip = np.array([-(20 * np.log10(abs(A[i][lc_idx[i]]) + 1e-30) - 20 * np.log10(LAM / (4 * np.pi * Rg[i]))) if dogru_var[i] else np.nan for i in range(len(KON))])
los = dogru_var & (ek_kayip < 3.0)                                             # gercek gorus hatti: dogrudan yol serbest uzaydan en fazla 3 dB zayif (kesin sinir BIZIM secimimiz)
df["los"] = los[df.konum]; df["ek_kayip_db"] = ek_kayip[df.konum]; df["duvar_icinden"] = (dogru_var & ~los)[df.konum]
df.to_csv(os.path.join(HERE, f"prs_itu_sonuclar{EK}.csv"), index=False)

satir = []
for tekrar in TEKRARLAR:
    d = df[df.tekrar == tekrar]
    satir.append(f"tekrar {tekrar:2d}: ort. Pd {d.pd.mean():.2f} (Pmd {100*(1-d.pd.mean()):.1f} %) | LOS konumlar ({int(d.los.sum())}) Pd {d[d.los].pd.mean():.2f} | LOS olmayan ({int((~d.los).sum())}) Pd {d[~d.los].pd.mean():.2f}, bunlardan duvarin icinden gecen dogrudan yollu {int(d.duvar_icinden.sum())} konum (ort. ek kayip {d[d.duvar_icinden].ek_kayip_db.mean():.0f} dB, Pd {d[d.duvar_icinden].pd.mean():.2f}) | Pd>=0,95 olan konum orani {np.mean(d.pd >= 0.95):.2f}")
    for lo, hi in ((0, 100), (100, 200), (200, 300)):
        dd = d[(d.R >= lo) & (d.R < hi)]
        if len(dd): satir.append(f"      3B uzaklik {lo:3d}-{hi:3d} m: {len(dd):3d} konum, ort. Pd {dd.pd.mean():.2f}")
d = df[df.tekrar == TEKRARLAR[-1]]
ok = d[(d.pd > 0) & d.vr.abs().lt(pt.VAMB) & d.hiz_hata.notna()]
satir.append(f"hiz hatasi (tekrar {TEKRARLAR[-1]}, belirsizlik sinirinin icindeki {len(ok)} konum): medyan {ok.hiz_hata.median():.2f} m/s, %90 {ok.hiz_hata.quantile(0.9):.2f} m/s (hedef 5 m/s)")
satir.append(f"radyal hizi |v_r| > {pt.VAMB:.1f} m/s (belirsiz) olan konum orani: {np.mean(np.abs(KON[:,3]*(KON[:,0]-GNB[0])/Rg+KON[:,4]*(KON[:,1]-GNB[1])/Rg) > pt.VAMB):.2f}")
satir.append(f"yanki cifti sayisi (tekrar {TEKRARLAR[-1]}): ortalama {d.n_cift.mean():.1f}, en cok {int(d.n_cift.max())}; yol sayisi ortalama {d.n_yol.mean():.1f}")
print("\n".join(satir))
open(os.path.join(HERE, f"prs_itu_ozet{EK}.txt"), "w", encoding="utf-8").write("\n".join(satir) + "\n")

# ------------------------------------------------ sekil
d = df[df.tekrar == 32] if 32 in TEKRARLAR else df[df.tekrar == TEKRARLAR[-1]]
fig, ax = plt.subplots(1, 2, figsize=(13, 6), gridspec_kw=dict(width_ratios=[1.15, 1]))
for p, h in BINALAR:
    xs, ys = p.exterior.xy if p.geom_type == "Polygon" else p.geoms[0].exterior.xy
    ax[0].fill(xs, ys, color="#d1d5db", ec="#6b7280", lw=0.3)
sc = ax[0].scatter(d.x, d.y, c=d.pd, cmap="RdYlGn", vmin=0, vmax=1, s=np.where(d.los, 34, 34), marker="o", edgecolor="black", linewidth=0.3)
ax[0].scatter(d.x[~d.los], d.y[~d.los], s=70, facecolors="none", edgecolors="#1d4ed8", linewidth=1.2, label="görüş hattı yok (duvardan geçen / yansıyan yollar)")
ax[0].plot(GNB[0], GNB[1], "*", color="yellow", ms=16, mec="black", label="gNB (EEF çatısı)")
ax[0].set_xlim(-310, 310); ax[0].set_ylim(-310, 310); ax[0].set_aspect("equal"); ax[0].set_xlabel("x (m)"); ax[0].set_ylabel("y (m)")
ax[0].legend(fontsize=8, loc="lower left"); fig.colorbar(sc, ax=ax[0], fraction=0.04, label="tespit olasılığı (10 deneme)")
ax[0].set_title(f"İHA konumları (yukarıdan; yükseklik {H_MIN:g}–{H_MAX:g} m), PRS {TEKRARLAR[-1]} tekrar\nyankı = Sionna ışın izleme (yansımalar dahil)", fontsize=9)
for tekrar, c in zip(TEKRARLAR, ["#ea580c", "#2563eb", "#16a34a"]):
    dd = df[df.tekrar == tekrar]; bins = np.arange(0, 301, 50); m = [dd[(dd.R >= b) & (dd.R < b + 50)].pd.mean() for b in bins[:-1]]
    ax[1].plot(bins[:-1] + 25, m, "o-", color=c, label=f"{tekrar} tekrar")
ax[1].set_xlabel("baz istasyonuna 3B uzaklık (m)"); ax[1].set_ylabel("ortalama tespit olasılığı"); ax[1].grid(alpha=0.3); ax[1].legend(); ax[1].set_ylim(-0.02, 1.02)
ax[1].set_title("Uzaklığa göre tespit (TR hedefi: Pmd ≤ %5 → Pd ≥ 0,95)", fontsize=9)
fig.savefig(os.path.join(HERE, f"prs_itu_sonuc{EK}.png"), dpi=140, bbox_inches="tight")
print("bitti", f"{time.time()-t0:.0f} s")

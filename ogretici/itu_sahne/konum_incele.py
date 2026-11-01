"""Kacirilan tek bir LOS konumunu ayrintili inceler: yol gecikmeleri, genlikleri, serbest uzay beklentisiyle karsilastirma."""
import json, os, sys
import numpy as np, pandas as pd
import sionna.rt as srt
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, PathSolver
HERE = os.path.dirname(os.path.abspath(__file__))
GNB = np.array(json.load(open(os.path.join(HERE, "sahne_ozet.json"), encoding="utf-8"))["gnb_xyz_m"])
d = pd.read_csv(os.path.join(HERE, "prs_itu_sonuclar_ops.csv")); d = d[d.tekrar == 32]
kacan = d[d.los & (d.pd < 0.5) & (d.n_cift == 1) & (d.R > 150)].sort_values("z").head(3)
iyi = d[d.los & (d.pd >= 0.95) & (d.n_cift == 1) & (d.R > 150) & (d.z > 60)].head(2)
scene = load_scene(os.path.join(HERE, "sahne.xml"), merge_shapes=True); scene.frequency = 4.9e9
scene.tx_array = PlanarArray(num_rows=1, num_cols=1, pattern="iso", polarization="V")
scene.rx_array = PlanarArray(num_rows=1, num_cols=1, pattern="iso", polarization="V")
scene.add(Transmitter(name="gnb", position=[float(x) for x in GNB], power_dbm=37.0))
LAM = 3e8 / 4.9e9
for etiket, grup in (("KACIRILAN", kacan), ("TESPIT EDILEN", iyi)):
    for _, r in grup.iterrows():
        p = [float(r.x), float(r.y), float(r.z)]
        scene.add(Receiver(name="rx", position=p))
        paths = PathSolver()(scene, max_depth=3, samples_per_src=1_000_000)
        a, tau = paths.cir(normalize_delays=False, out_type="numpy"); a = np.array(a).reshape(-1); tau = np.array(tau).reshape(-1)
        R = np.linalg.norm(np.array(p) - GNB)
        print(f"\n{etiket}: konum {p}, 3B uzaklik {R:.1f} m, Pd={r.pd:.2f}, n_yol={int(r.n_yol)}, n_cift={int(r.n_cift)}, v_r={r.vr:.1f} m/s")
        beklenen = 20 * np.log10(LAM / (4 * np.pi * R))
        for t, aa in zip(tau, a):
            if t > 0: print(f"   yol: uzunluk-R = {t*3e8-R:+7.2f} m | genlik {20*np.log10(abs(aa)+1e-30):7.2f} dB (serbest uzay beklentisi {beklenen:.2f} dB)")
        scene.remove("rx")

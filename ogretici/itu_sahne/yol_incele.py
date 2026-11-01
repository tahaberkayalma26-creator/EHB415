"""Sionna PathSolver ciktisinin alanlarini ve aci yonlerini inceler (LOS yolu uzerinde): hangi isaret/yon kullaniliyor?"""
import json, os
import numpy as np
import sionna.rt as rt
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, PathSolver

HERE = os.path.dirname(os.path.abspath(__file__))
GNB = json.load(open(os.path.join(HERE, "sahne_ozet.json"), encoding="utf-8"))["gnb_xyz_m"]
scene = load_scene(os.path.join(HERE, "sahne.xml"), merge_shapes=True)
scene.frequency = 4.9e9
scene.tx_array = PlanarArray(num_rows=1, num_cols=1, pattern="iso", polarization="V")
scene.rx_array = PlanarArray(num_rows=1, num_cols=1, pattern="iso", polarization="V")
scene.add(Transmitter(name="gnb", position=GNB, power_dbm=37.0))
P = [[100.0, 0.0, 100.0], [-60.0, 90.0, 40.0]]
for i, p in enumerate(P): scene.add(Receiver(name=f"rx{i}", position=p))
paths = PathSolver()(scene, max_depth=3, samples_per_src=1_000_000)
print("Paths alanlari:", [n for n in dir(paths) if not n.startswith("_")])
for n in ("a", "tau", "theta_t", "phi_t", "theta_r", "phi_r", "valid", "interactions"):
    try:
        v = getattr(paths, n); v = v if not callable(v) else v()
        print(n, type(v).__name__, [np.array(x).shape for x in v] if isinstance(v, (tuple, list)) else np.array(v).shape)
    except Exception as e: print(n, "HATA", e)
a, tau = paths.cir(normalize_delays=False, out_type="numpy")
print("cir a:", np.array(a).shape, "tau:", np.array(tau).shape, a.dtype if hasattr(a, "dtype") else "")
tt = np.array(paths.theta_t); pt = np.array(paths.phi_t); tr = np.array(paths.theta_r); pr = np.array(paths.phi_r); tauv = np.array(paths.tau)
print("tau shape", tauv.shape)
def vec(th, ph): return np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])
for i, p in enumerate(P):
    d = np.array(p) - np.array(GNB); R = np.linalg.norm(d); u = d / R
    t = tauv.reshape(len(P), -1)[i]; k = int(np.argmin(np.where(t > 0, t, np.inf)))     # en kisa gecerli yol = LOS (varsa)
    kt = vec(tt.reshape(len(P), -1)[i, k], pt.reshape(len(P), -1)[i, k]); kr = vec(tr.reshape(len(P), -1)[i, k], pr.reshape(len(P), -1)[i, k])
    print(f"rx{i}: R={R:.1f} m, en kisa yol tau*c={t[k]*3e8:.1f} m | cikis yonu . u = {kt@u:+.3f} | varis aci-vektoru . u = {kr@u:+.3f}")
    print("   gecerli yol sayisi:", int((t > 0).sum()))

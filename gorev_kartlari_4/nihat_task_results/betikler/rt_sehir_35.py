"""[Nihat, gorev kartlari 4, adim 1] ogretici/sionna_sehir/rt_sehir.py'nin KOPYASI: FC = 4.9e9 -> 3.5e9 (ortak izgara, n78).
Asil dosyaya ve asil cikti/rt_sonuclar.npz'ye dokunulmaz; cikti ayri klasore yazilir:
  gorev_kartlari_4/nihat_task_results/cikti/rt_3p5GHz/   (varsayilan, FC = 3.5e9)
  gorev_kartlari_4/nihat_task_results/cikti/rt_4p9GHz/   (karsilastirma icin ayni betik 4.9e9 ile:  python rt_sehir_35.py 4.9e9)
Asil kopyadan farklar: FC satiri, OUT klasoru, sonda rota noktalarinin yol kazanci CSV'si (yol_kazanci_rota.csv). Geri kalan her sey ayni.
--- asil aciklama ---
Sionna RT ile sehir (Munih) projesi, 1. parca: sahne, kapsama haritasi, isin yollari, IHA rotasi boyunca gorus hatti (LOS).
Uretilenler (cikti/ klasorune):
  01_sahne.png        3B sahne + gNB
  02_kapsama_3b.png   kapsama haritasi 3B goruntu uzerinde
  03_kapsama_ustten.npz / rt_sonuclar.npz   ham veriler (radar parcasi kullanir)
  04_yollar.png       gNB -> UE isin yollari (3B)
Calistirma:  <venv python> rt_sehir.py   (DRJIT_LIBLLVM_PATH ayarli olmali)
"""
import os, sys, time
import numpy as np
import sionna.rt as rt
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, PathSolver, RadioMapSolver, Camera

FC = float(sys.argv[1]) if len(sys.argv) > 1 else 3.5e9   # asil dosyada: FC = 4.9e9  (ortak_degerler.xlsx 'Sionna' B2 = 3500000000)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "cikti", f"rt_{FC / 1e9:.1f}GHz".replace(".", "p")); os.makedirs(OUT, exist_ok=True)
t0 = time.time()
def log(m): print(f"[{time.time()-t0:6.1f} s] {m}", flush=True)

GNB = [8.5, 21.0, 27.0]
UE = [45.0, 90.0, 1.5]

scene = load_scene(rt.scene.munich, merge_shapes=True)
scene.frequency = FC
scene.tx_array = PlanarArray(num_rows=1, num_cols=1, pattern="iso", polarization="V")
scene.rx_array = PlanarArray(num_rows=1, num_cols=1, pattern="iso", polarization="V")
scene.add(Transmitter(name="gnb", position=GNB, power_dbm=37.0))
log("sahne yuklendi")

cam = Camera(position=[-250.0, 250.0, 150.0], look_at=[-15.0, 30.0, 28.0])

# 1) sahne
fig = scene.render(camera=cam, resolution=(900, 600), num_samples=48)
fig.savefig(os.path.join(OUT, "01_sahne.png"), dpi=130, bbox_inches="tight"); log("01_sahne.png")

# 2) kapsama haritasi
rm = RadioMapSolver()(scene, cell_size=(5.0, 5.0), samples_per_tx=2_000_000, max_depth=5)
log("radyo haritasi hesaplandi")
fig = scene.render(camera=cam, radio_map=rm, resolution=(900, 600), num_samples=48, rm_vmin=-120.0, rm_vmax=-60.0,
                   rm_show_color_bar=True)
fig.savefig(os.path.join(OUT, "02_kapsama_3b.png"), dpi=130, bbox_inches="tight"); log("02_kapsama_3b.png")
pg = np.array(rm.path_gain)[0]               # [ny, nx]  (lineer kazanc)
cc = np.array(rm.cell_centers)               # [ny, nx, 3]
log(f"harita boyutu {pg.shape}, x:[{cc[...,0].min():.0f},{cc[...,0].max():.0f}] y:[{cc[...,1].min():.0f},{cc[...,1].max():.0f}]")

# 3) gNB -> UE isin yollari
scene.add(Receiver(name="ue", position=UE))
paths = PathSolver()(scene, max_depth=3, samples_per_src=1_000_000)
a, tau = paths.cir(normalize_delays=False, out_type="numpy")
a = np.array(a).squeeze(); tau = np.array(tau).squeeze()
gec = tau > 0
order = np.argsort(-np.abs(a))
log(f"UE: {int(gec.sum())} gecerli yol")
fig = scene.render(camera=cam, paths=paths, resolution=(900, 600), num_samples=48)
fig.savefig(os.path.join(OUT, "04_yollar.png"), dpi=130, bbox_inches="tight"); log("04_yollar.png")
tab = [(float(tau.ravel()[i]) * 1e9, 20 * np.log10(abs(complex(a.ravel()[i])) + 1e-30)) for i in order[:8] if tau.ravel()[i] > 0]
np.savetxt(os.path.join(OUT, "04_yollar_tablo.csv"), np.array(tab), delimiter=",", header="gecikme_ns,genlik_dB", comments="")
scene.remove("ue")

# 4) IHA rotasi: her noktaya bir alici koy, tek cozumde LOS ve tek yon kazanc
N = 60
p0 = np.array([-130.0, 150.0, 20.0]); p1 = np.array([150.0, -70.0, 20.0])   # irtifa 20 m: gorus hatti karisik
pos = np.linspace(p0, p1, N)
for i, p in enumerate(pos):
    scene.add(Receiver(name=f"iha{i:03d}", position=[float(p[0]), float(p[1]), float(p[2])]))
paths = PathSolver()(scene, max_depth=3, samples_per_src=1_000_000)
a, tau = paths.cir(normalize_delays=False, out_type="numpy")
a = np.array(a); tau = np.array(tau)
log(f"iha cozum a:{a.shape} tau:{tau.shape}")
# tau: [num_rx, num_tx, paths]; en kisa gecerli yol = LOS ise gecikme ~ dogrudan mesafe/c
gnb = np.array(GNB)
dogru = np.linalg.norm(pos - gnb, axis=1) / 3e8
tau2 = tau.reshape(N, -1); a2 = a.reshape(N, -1)
tau2 = np.where(tau2 > 0, tau2, np.inf)
tmin = tau2.min(axis=1)
# Gorus hatti (LOS): yalnizca dogrudan yolu cozdur (max_depth=0). Yol bulunduysa LOS vardir.
p_los = PathSolver()(scene, max_depth=1, los=True, specular_reflection=False, refraction=False, samples_per_src=200_000)
a_l, tau_l = p_los.cir(normalize_delays=False, out_type="numpy")
tau_l = np.array(tau_l).reshape(N, -1)
los = (np.where(tau_l > 0, 1, 0).sum(axis=1) > 0)
log(f"debug: en kisa yol - dogrudan mesafe/c farki (ns), ilk 6: {np.round((tmin - dogru)[:6] * 1e9, 1)}")
kazanc = np.array([10 * np.log10(np.sum(np.abs(a2[i][np.isfinite(tau2[i])]) ** 2) + 1e-30) for i in range(N)])
log(f"LOS olan nokta sayisi: {int(los.sum())}/{N}")
np.savez(os.path.join(OUT, "rt_sonuclar.npz"), pos=pos, los=los, kazanc_db=kazanc, pg=pg, cc=cc, gnb=gnb, fc=FC)
# [eklenen] rota noktalarinin yol kazanci (tum gecerli yollarin toplam gucu, max_depth=3) ve serbest uzay referansi
d3 = np.linalg.norm(pos - gnb, axis=1)
fspl = 20 * np.log10(3e8 / FC / (4 * np.pi * d3))
np.savetxt(os.path.join(OUT, "yol_kazanci_rota.csv"),
           np.column_stack([np.arange(N), pos, d3, los.astype(int), kazanc, fspl]), delimiter=",", fmt="%.4f",
           header="nokta,x_m,y_m,z_m,uzaklik_3b_m,los,yol_kazanci_db,serbest_uzay_db", comments="")
pg_db = 10 * np.log10(pg[pg > 0])
log(f"FC = {FC / 1e9:.2f} GHz | kapsama haritasi: {pg_db.size} hucre, medyan yol kazanci {np.median(pg_db):.2f} dB")
print("tamam", time.time() - t0)

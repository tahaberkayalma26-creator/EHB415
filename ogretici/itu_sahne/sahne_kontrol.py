"""Uretilen ITU sahnesini Sionna RT ile yukler, gNB'yi EEF catisina koyar, 3B goruntu alir ve bir halka uzerinde LOS orani olcer.
Calistirma:  python sahne_kontrol.py   (DRJIT_LIBLLVM_PATH ayarli olmali)
Cikti: sahne_3b.png, kontrol_sonuc.txt
"""
import json, os
import numpy as np
import sionna.rt as rt
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, PathSolver, Camera

HERE = os.path.dirname(os.path.abspath(__file__))
O = json.load(open(os.path.join(HERE, "sahne_ozet.json"), encoding="utf-8"))
GNB = O["gnb_xyz_m"]

scene = load_scene(os.path.join(HERE, "sahne.xml"), merge_shapes=True)
scene.frequency = 4.9e9
scene.tx_array = PlanarArray(num_rows=1, num_cols=1, pattern="iso", polarization="V")
scene.rx_array = PlanarArray(num_rows=1, num_cols=1, pattern="iso", polarization="V")
scene.add(Transmitter(name="gnb", position=GNB, power_dbm=37.0))
print("sahne yuklendi; nesneler:", list(scene.objects.keys()))

cam = Camera(position=[-330.0, -330.0, 190.0], look_at=[0.0, 0.0, 15.0])
fig = scene.render(camera=cam, resolution=(900, 600), num_samples=48)
fig.savefig(os.path.join(HERE, "sahne_3b.png"), dpi=130, bbox_inches="tight")

# LOS orani: gNB cevresinde 3 yaricap x 3 yukseklik, her halkada 36 nokta
satir = []
for r in (100.0, 200.0, 300.0):
    for z in (25.0, 100.0, 250.0):
        ang = np.linspace(0, 2 * np.pi, 36, endpoint=False)
        pts = [[r * np.cos(a), r * np.sin(a), z] for a in ang]
        for i, p in enumerate(pts): scene.add(Receiver(name=f"rx{i:02d}", position=[float(x) for x in p]))
        p_los = PathSolver()(scene, max_depth=1, los=True, specular_reflection=False, refraction=False, samples_per_src=200_000)
        a_l, tau_l = p_los.cir(normalize_delays=False, out_type="numpy")
        los = (np.where(np.array(tau_l).reshape(len(pts), -1) > 0, 1, 0).sum(axis=1) > 0)
        for i in range(len(pts)): scene.remove(f"rx{i:02d}")
        satir.append(f"yatay {r:5.0f} m, yukseklik {z:5.0f} m: gorus hatti olan nokta {int(los.sum())}/36 = {los.mean():.2f}")
        print(satir[-1], flush=True)
open(os.path.join(HERE, "kontrol_sonuc.txt"), "w", encoding="utf-8").write("\n".join(satir) + "\n")

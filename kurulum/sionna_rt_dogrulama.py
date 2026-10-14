"""Sionna RT (ray tracing) CPU dogrulamasi: yerlesik 'munich' sahnesinde 1 verici, 1 alici, yol cozumu."""
import mitsuba as mi
print("mitsuba", mi.__version__, "| varyantlar:", [v for v in mi.variants() if "llvm" in v or "scalar_rgb" == v][:4])

import sionna.rt as rt
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, PathSolver

scene = load_scene(rt.scene.munich, merge_shapes=True)
scene.frequency = 4.9e9
scene.tx_array = PlanarArray(num_rows=1, num_cols=1, vertical_spacing=0.5, horizontal_spacing=0.5,
                             pattern="iso", polarization="V")
scene.rx_array = scene.tx_array
scene.add(Transmitter(name="gnb", position=[8.5, 21, 27]))
scene.add(Receiver(name="ue", position=[45, 90, 1.5]))

paths = PathSolver()(scene, max_depth=3, samples_per_src=100000)
a, tau = paths.cir(out_type="numpy")
print("yol cozucu OK | bulunan gecerli yol sayisi:", int((tau > 0).sum()))

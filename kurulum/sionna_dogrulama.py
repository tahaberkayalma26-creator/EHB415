"""Sionna kurulum dogrulamasi + OFDM radar (range-Doppler) kontrolu.
Calistirma:  C:\\Users\\<kullanici>\\venvs\\ehb415\\Scripts\\python.exe sionna_dogrulama.py
"""
import numpy as np
import tensorflow as tf
import sionna

print("sionna", sionna.__version__, "| tensorflow", tf.__version__,
      "| GPU:", tf.config.list_physical_devices("GPU"))

# 1) Tek hedefli OFDM radar: 2D FFT ile range-Doppler
c = 3e8
fc = 4.9e9
scs = 30e3
N, M = 1024, 128                     # alt tasiyici, OFDM sembol sayisi
W = N * scs                          # bant genisligi
Ts = (1 / scs) * (1 + 7 / 64)        # CP dahil sembol suresi (yaklasik)
lam = c / fc
R0, v0 = 120.0, 25.0                 # gercek mesafe (m), radyal hiz (m/s)

n = np.arange(N)[:, None]
m = np.arange(M)[None, :]
rng = np.random.default_rng(0)
X = np.exp(1j * 2 * np.pi * rng.random((N, M)))          # gonderilen semboller
tau = 2 * R0 / c
fd = 2 * v0 / lam
Y = X * np.exp(-1j * 2 * np.pi * n * scs * tau) * np.exp(1j * 2 * np.pi * m * Ts * fd)
Y = Y + 0.3 * (rng.normal(size=Y.shape) + 1j * rng.normal(size=Y.shape))

H = Y / X                                                # kanal tahmini
rd = np.fft.fftshift(np.fft.fft(np.fft.ifft(H, axis=0), axis=1), axes=1)
k, l = np.unravel_index(np.abs(rd).argmax(), rd.shape)
R_hat = k * c / (2 * W)
v_hat = (l - M // 2) / (M * Ts) * lam / 2

print(f"gercek   : R={R0:.1f} m, v={v0:.1f} m/s")
print(f"tahmin   : R={R_hat:.1f} m, v={v_hat:.1f} m/s")
print(f"cozunurluk (teorik): dR={c / (2 * W):.2f} m, dv={lam / (2 * M * Ts):.2f} m/s")

# 2) Sionna'nin kendi OFDM kaynak izgarasi
from sionna.phy.ofdm import ResourceGrid
rg = ResourceGrid(num_ofdm_symbols=14, fft_size=76, subcarrier_spacing=30e3,
                  num_tx=1, num_streams_per_tx=1)
print("Sionna ResourceGrid OK | veri sembolu sayisi:", rg.num_data_symbols)

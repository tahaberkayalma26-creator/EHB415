"""[Nihat, gorev kartlari 4, adim 3, teslim 3] PRS periyodu ve hiz: en buyuk hiz lambda/(4 T_PRS), hiz cozunurlugu lambda/(2 T_gozlem).
Calistirma:  python hiz_tablosu.py      (hesap; Monte Carlo yok)
Ek satirlar: ayni formuller 4,9 GHz'te; radar_takip.py'nin ardisik sembol modeli (T = sembol suresi); TR 38.765'teki en buyuk IHA hizi.
"""
import numpy as np

C = 3e8
T_GOZLEM = 0.160
TS_RADAR = (1 / 30e3) * (1 + 7 / 64)      # radar_takip.py satir 26
SLOT = 0.5e-3
K = [("K1", 10), ("K2", 20), ("K3", 40)]   # ortak_prs_konfig.csv: periyot_slot (30 kHz'te 1 slot = 0,5 ms)

for fc in (3.5e9, 4.9e9):
    lam = C / fc
    print(f"fc = {fc / 1e9:.1f} GHz, lambda = {100 * lam:.3f} cm")
    print("   konfig  periyot   PRS firsati (160 ms)   en buyuk hiz lambda/(4T)   hiz cozunurlugu lambda/(2*0,16 s)")
    for ad, ps in K:
        T = ps * SLOT
        print(f"   {ad:5s}  {T * 1e3:5.1f} ms   {int(round(T_GOZLEM / T)):4d}                   {lam / (4 * T):6.2f} m/s                 {lam / (2 * T_GOZLEM):5.2f} m/s")
    print(f"   radar_takip.py (ardisik semboller, T = {TS_RADAR * 1e6:.2f} us): en buyuk hiz {lam / (4 * TS_RADAR):6.1f} m/s; "
          f"cozunurluk M = 28 / 70 / 140 icin {lam / (2 * 28 * TS_RADAR):.2f} / {lam / (2 * 70 * TS_RADAR):.2f} / {lam / (2 * 140 * TS_RADAR):.2f} m/s")
    print(f"   tek slot arayla tekrar (PRS tekrar faktoru > 1, zaman boslugu 1 slot, T = 0,5 ms): en buyuk hiz {lam / (4 * SLOT):.2f} m/s")
    print(f"   TR 38.765 Tablo A-1: IHA yatay hizi 0-180 km/sa = 0-50 m/s -> 50 m/s'i katlamadan olcmek icin T <= lambda/(4*50) = {1e3 * lam / 200:.3f} ms\n")

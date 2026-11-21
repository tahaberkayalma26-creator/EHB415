"""[Nihat, gorev kartlari 4, adim 1, teslim 1] 4,9 GHz ve 3,5 GHz yol kazanci tablosu (Munih sahnesi, rt_sehir_35.py ciktilari).
Calistirma (once:  python rt_sehir_35.py   ve   python rt_sehir_35.py 4.9e9):
    python yol_kazanci_karsilastir.py
Secilen 5 konum (rota noktasi indisi): 0, 15, 30 (gorus hatti var) ve 39, 45 (gorus hatti yok, ama yol bulunan).
Secim gerekcesi: kart konumlari belirtmiyor; rota boyunca hem LOS hem NLOS durumu temsil edilsin ve her iki frekansta da
en az bir yol bulunsun diye secildi (NLOS bolumundeki 42, 48-59 noktalarinda max_depth = 3 ile hic yol yok: -300 dB).
Ayrica: 4,9 GHz yeniden kosusunun asil rt_sonuclar.npz ile ayni olup olmadigi (tekrarlanabilirlik) ve kapsama haritasi karsilastirmasi.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); CIK = os.path.join(HERE, "..", "cikti")
ASIL = os.path.join(HERE, "..", "..", "..", "ogretici", "sionna_sehir", "cikti", "rt_sonuclar.npz")
KONUM = [0, 15, 30, 39, 45]

d35 = np.load(os.path.join(CIK, "rt_3p5GHz", "rt_sonuclar.npz"))
d49 = np.load(os.path.join(CIK, "rt_4p9GHz", "rt_sonuclar.npz"))
das = np.load(ASIL)
assert float(d35["fc"]) == 3.5e9 and float(d49["fc"]) == 4.9e9 and float(das["fc"]) == 4.9e9
gnb = d35["gnb"]; pos = d35["pos"]
assert np.allclose(pos, das["pos"]) and np.allclose(gnb, das["gnb"])
d3 = np.linalg.norm(pos - gnb, axis=1)
fs = lambda f: 20 * np.log10(3e8 / f / (4 * np.pi * d3))          # serbest uzay yol kazanci (izotropik antenler)

sat = []
for i in KONUM:
    sat.append(dict(nokta=i, x_m=pos[i, 0], y_m=pos[i, 1], z_m=pos[i, 2], uzaklik_3b_m=d3[i],
                    los_49=bool(d49["los"][i]), los_35=bool(d35["los"][i]),
                    kazanc_49_asil_db=das["kazanc_db"][i], kazanc_49_db=d49["kazanc_db"][i], kazanc_35_db=d35["kazanc_db"][i],
                    fark_35_eksi_49_db=d35["kazanc_db"][i] - d49["kazanc_db"][i],
                    serbest_uzay_49_db=fs(4.9e9)[i], serbest_uzay_35_db=fs(3.5e9)[i]))
df = pd.DataFrame(sat)
df.to_csv(os.path.join(CIK, "yol_kazanci_5_konum.csv"), index=False, float_format="%.2f")
pd.set_option("display.width", 220)
print("5 konumda yol kazanci (dB; tum gecerli yollarin toplam gucu, max_depth = 3, izotropik antenler)")
print(df.round(2).to_string(index=False))
print(f"\nserbest uzayda beklenen fark: 20*log10(4,9/3,5) = {20 * np.log10(4.9 / 3.5):.2f} dB")

# rota geneli
m = (d35["kazanc_db"] > -299) & (d49["kazanc_db"] > -299)
fark = d35["kazanc_db"][m] - d49["kazanc_db"][m]
los = d35["los"][m]
print(f"\nrota geneli ({m.sum()}/60 noktada her iki frekansta yol var): fark ortalama {fark.mean():.2f} dB, "
      f"medyan {np.median(fark):.2f} dB, en kucuk {fark.min():.2f}, en buyuk {fark.max():.2f} dB")
print(f"   LOS noktalari ({los.sum()}): ortalama {fark[los].mean():.2f} dB | NLOS noktalari ({(~los).sum()}): ortalama {fark[~los].mean():.2f} dB")
y35 = int(((d35["kazanc_db"] > -299) & ~(d49["kazanc_db"] > -299)).sum()); y49 = int((~(d35["kazanc_db"] > -299) & (d49["kazanc_db"] > -299)).sum())
print(f"   yalniz 3,5 GHz'te yol bulunan nokta: {y35}, yalniz 4,9 GHz'te: {y49}")

# tekrarlanabilirlik: 4,9 GHz yeniden kosu vs asil npz
dk = d49["kazanc_db"] - das["kazanc_db"]
print(f"\ntekrarlanabilirlik (4,9 GHz yeniden kosu - asil rt_sonuclar.npz): en buyuk mutlak fark {np.abs(dk).max():.3f} dB, "
      f"LOS dizisi ayni: {bool(np.array_equal(d49['los'], das['los']))}")

# kapsama haritasi (ayni hucreler)
p35, p49 = d35["pg"], d49["pg"]
ortak = (p35 > 0) & (p49 > 0)
hf = 10 * np.log10(p35[ortak]) - 10 * np.log10(p49[ortak])
print(f"kapsama haritasi: her iki frekansta kapsanan {ortak.sum()} hucrede fark medyan {np.median(hf):.2f} dB "
      f"(%10-%90: {np.percentile(hf, 10):.2f} / {np.percentile(hf, 90):.2f} dB); kapsanan hucre sayisi 3,5 GHz {int((p35 > 0).sum())}, 4,9 GHz {int((p49 > 0).sum())}")

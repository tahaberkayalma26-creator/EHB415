"""TR 38.765 metriklerini radar_takip.py'nin radarindan olcer (3 bolum).
Calistirma (rt_sehir.py ve radar_takip.py bir kez calismis olmali; cikti/rt_sonuclar.npz ve cikti/kaynak_basari.csv gerekir):
    python tr_metrik_olc.py
1) Pf1: hedefsiz CPI'larda yanlis alarm orani (TR 38.765 Pf1 tanimi: hedef yokken en az bir nesne bulunan deneme orani).
2) Pmd hedefi: cikti/kaynak_basari.csv'den, her menzil icin Pmd <= %5 (Pd >= 0,95) saglayan en kucuk alfa.
3) Artik oz-girisim X_SI_DB 40 ve 30 iken 300 m'de Pd (radar_takip.py'deki Monte Carlo ile ayni yontem).
"""
import os
import numpy as np
import pandas as pd
import radar_takip as rt          # radar_takip.py'yi modul olarak yukler (film/analiz calismaz, yalnizca fonksiyonlar)

rng = np.random.default_rng(11)

# ---------------- 1) Pf1
print("1) Pf1 (hedef yok; radar_takip.PFA = %g, CPI basina)" % rt.PFA)
for M in (14, 70):                                   # alpha = %10 ve %50
    n = 3000; k = 0
    for _ in range(n):
        rax, vax, P = rt.radar(300.0, 0.0, M, -np.inf, rng)   # snr = -inf dB -> yanki genligi 0 -> yalnizca gurultu
        k += bool(rt.tespit(rax, vax, P)[0])
    print(f"   M={M:3d} (alpha={M/rt.FRAME_SYM:.0%}): {k}/{n} hedefsiz CPI'da alarm -> Pf1 = {100*k/n:.2f} %")

# ---------------- 2) Pmd <= %5 icin gereken alfa
print("\n2) Pmd <= %5 (Pd >= 0,95) icin en kucuk alfa (cikti/kaynak_basari.csv)")
df = pd.read_csv(os.path.join(rt.OUT, "kaynak_basari.csv"))
for r, g in df.groupby("menzil_m"):
    ok = g[g.pd >= 0.95].sort_values("alpha")
    print(f"   {int(r)} m: " + (f"alfa = {ok.alpha.iloc[0]:.1%} (Pd = {ok.pd.iloc[0]:.2f})" if len(ok) else f"taranan alfa degerlerinin hicbirinde yok (en yuksek Pd = {g.pd.max():.2f})"))

# ---------------- 3) X_SI deneyi
print("\n3) 300 m'de Pd, X_SI_DB'ye gore (160 deneme)")
def pd_olc(r, M, n=160):
    ok = 0
    for _ in range(n):
        v0 = rng.uniform(-30, 30); r_g = r + rng.uniform(-6, 6)
        rax, vax, P = rt.radar(r_g, v0, M, rt.snr_ornek_db(r), rng)
        tp, re_, ve = rt.tespit(rax, vax, P)
        ok += bool(tp and abs(re_ - r_g) < 3 * rt.C / (2 * rt.W))
    return ok / n
Ms = [28, 56, 70, 140]
print("   alpha:        " + "  ".join(f"{M/rt.FRAME_SYM:5.0%}" for M in Ms))
for x in (40.0, 30.0):
    rt.X_SI_DB = x                                    # snr_ornek_db() bu global degeri okur
    print(f"   X_SI={x:4.0f} dB: " + "  ".join(f"{pd_olc(300, M):5.2f}" for M in Ms))

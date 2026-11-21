"""[Nihat, CLAUDE.md 'Sionna PRS Configuration': PRS'in bos kutularinin veriye acilmasi ve throughput iyilesmesi] -- Yol 1 (hesap)
Yontem: TS 38.214 Madde 5.1.3.2 tasima blogu boyutu (TBS) hesabi, ortak izgarada (n78, 30 kHz, 100 MHz, TDD 6 DL + 1 karisik + 3 UL).
PDSCH yerlesimi:
  - PDSCH sembolleri 1..13 (13 sembol), sembol 0 PDCCH/CORESET0 (ogretici/gorev_karti_prs_gorsel.tex; esleme tipi A: VARSAYIM)
  - DMRS sembolleri {2, 7, 11} (TS 38.211 Tablo 7.4.1.1.2-3: dmrs-TypeA-Position pos2, dmrs-AdditionalPosition pos2),
    DMRS sembollerinde veri yok (veri icermeyen CDM grubu sayisi 2) -> PRB basina N_DMRS = 36 RE (VARSAYIM; OCUDU'da dogrulanmadi)
  - MCS 28, mcs_table qam64 (kurulum/ocudu_testmode_n78_100MHz.yml; test UE cqi 15, ri 1) -> Qm = 6, R = 948/1024
    (TS 38.214 Tablo 5.2.2.1-2 ve 5.1.3.1-1; CQI 15 -> MCS 28 eslemesi CIKARIM), 1 katman
  - xOverhead yok (N_oh = 0); karisik slotta PDSCH yok (ortak_degerler.xlsx: OCUDU testinde DL ok = 1200/s = 6 DL slot x 200 periyot/s)
PRS slotunda dort durum:
  M0  PRS yok (referans)
  M1  PRB kapatma (OCUDU bugunku hali, prs_scheduler.cpp dl_res_grid.fill): PRS'in PRB'leri o slotta PDSCH'ye tumuyle kapali
  M2  PRB x sembol duzeyinde rate matching (RRC RateMatchPattern ile UE'ye bildirilebilen tur): PRS PRB'lerinde PRS sembolleri bosaltilir
  M3  RE duzeyinde rate matching (comb): yalnizca PRS'in doldurdugu RE'ler veri disi (ust sinir; UE'ye RE duzeyinde
      bildirilebilirligi dogrulanmadi)
M2/M3'te TBS, kalan veri RE sayisiyla hesaplanir (N_RE = N_RE,baslangic - N_PRS,veri). Standart TBS
formulu rate matching RE'lerini dusmez; bu hesap 'etkin kod orani sabit' varsayimina karsilik gelir (VARSAYIM).
Senaryolar: A) veri genisligi 48 PRB [0..48) (ortak_degerler.xlsx, OCUDU test modundaki PDSCH araligi), B) 273 PRB (tum tasiyici; gercek 100 MHz sistemi
temsili, tek UE, 1 katman, 64QAM -- VARSAYIM).
Calistirma:  python prs_veri_tbs.py        Cikti: cikti/veri_tbs/
"""
import math, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "cikti", "veri_tbs"); os.makedirs(OUT, exist_ok=True)
KONFIG_CSV = os.path.join(HERE, "..", "..", "..", "ogretici", "veri", "ortak_prs_konfig.csv")

# ------------------------------------------------ PARAM
SLOT_S = 0.5e-3
PDSCH_SEM = list(range(1, 14))                     # 13 sembol
DMRS_SEM = {2, 7, 11}
QM, R = 6, 948 / 1024                              # MCS 28, qam64 tablosu
KATMAN = 1
N_OH = 0
TDD_DL = set(range(6))                             # 10 slotluk desende DL slotlari 0..5 (6: karisik, 7..9: UL)
UFUK = 40                                          # en buyuk PRS periyodu 40 slot -> 40 slotluk ufuk
COMB_SATIR = {2: [0, 1], 4: [0, 2, 1, 3], 6: [0, 3, 1, 4, 2, 5], 12: [0, 6, 3, 9, 1, 7, 4, 10, 2, 8, 5, 11]}
KART_PAY = dict(K1=7.7, K6=23.1, K7=15.4, K8=7.7, K11=7.7)     # kart: PRS slotunda kapanan pay (ust sinir, hesap), %

# TS 38.214 Tablo 5.1.3.2-1 (N_info <= 3824 icin)
TBS_TABLO = [24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128, 136, 144, 152, 160, 168, 176, 184, 192, 208, 224, 240, 256,
             272, 288, 304, 320, 336, 352, 368, 384, 408, 432, 456, 480, 504, 528, 552, 576, 608, 640, 672, 704, 736, 768, 808, 848,
             888, 928, 984, 1032, 1064, 1128, 1160, 1192, 1224, 1256, 1288, 1320, 1352, 1416, 1480, 1544, 1608, 1672, 1736, 1800,
             1864, 1928, 2024, 2088, 2152, 2216, 2280, 2408, 2472, 2536, 2600, 2664, 2728, 2792, 2856, 2976, 3104, 3240, 3368, 3496,
             3624, 3752, 3824]

def tbs(n_re, r=R, qm=QM, v=KATMAN):
    """TS 38.214 Madde 5.1.3.2 adim 2-4."""
    if n_re <= 0: return 0
    n_info = n_re * r * qm * v
    if n_info <= 3824:
        n = max(3, math.floor(math.log2(n_info)) - 6)
        nip = max(24, 2 ** n * math.floor(n_info / 2 ** n))
        return next(t for t in TBS_TABLO if t >= nip)
    n = math.floor(math.log2(n_info - 24)) - 5
    nip = max(3840, 2 ** n * math.floor((n_info - 24) / 2 ** n + 0.5))
    if r <= 0.25:
        c = math.ceil((nip + 24) / 3816); return 8 * c * math.ceil((nip + 24) / (8 * c)) - 24
    if nip > 8424:
        c = math.ceil((nip + 24) / 8424); return 8 * c * math.ceil((nip + 24) / (8 * c)) - 24
    return 8 * math.ceil((nip + 24) / 8) - 24

def n_re_prb():
    """PRB basina veri RE (PRS yok): min(156, 12*N_sembol - N_DMRS - N_oh)."""
    return min(156, 12 * len(PDSCH_SEM) - 12 * len(DMRS_SEM) - N_OH)

def prs_prb_maske(kf):
    """Bir PRB x 14 sembolde PRS'in doldurdugu RE'ler (12 x 14 bool), comb ofseti 0."""
    m = np.zeros((12, 14), bool)
    for j in range(kf["L"]):
        l = kf["l0"] + j; kp = COMB_SATIR[kf["K"]][j % kf["K"]]
        m[kp::kf["K"], l] = True
    return m

def veri_maske():
    m = np.zeros((12, 14), bool)
    for l in PDSCH_SEM:
        if l not in DMRS_SEM: m[:, l] = True
    return m

def kayip_re_prb(kf, mod):
    """PRS PRB'si basina PRS slotunda kaybedilen veri RE (M2: PRS sembolleri tumden; M3: yalniz comb RE'leri)."""
    v = veri_maske(); p = prs_prb_maske(kf)
    if mod == "M2":
        semboller = np.where(p.any(axis=0))[0]
        return int(v[:, semboller].sum())
    if mod == "M3":
        return int((v & p).sum())
    raise ValueError(mod)

def slot_n_re(kf, mod, w_veri):
    """PRS slotunda PDSCH veri RE sayisi."""
    base = n_re_prb()
    if kf is None or mod == "M0": return base * w_veri
    ortak = min(kf["bw"], w_veri)                       # PRS [0..bw) ile veri [0..w_veri) ortusmesi
    if mod == "M1": return base * (w_veri - ortak)       # ortusen PRB'ler o slotta kapali
    return base * w_veri - kayip_re_prb(kf, mod) * ortak

def throughput(kf, mod, w_veri):
    """40 slotluk ufukta ortalama DL hizi (Mbps) ve DL slot sayisi."""
    top = 0
    for s in range(UFUK):
        if s % 10 not in TDD_DL: continue
        prs = kf is not None and kf["periyot"] > 0 and s % kf["periyot"] == kf["s0"]
        top += tbs(slot_n_re(kf if prs else None, mod if prs else "M0", w_veri))
    return top / (UFUK * SLOT_S) / 1e6

def konfigler():
    df = pd.read_csv(KONFIG_CSV)
    return {r.id: dict(id=r.id, periyot=int(r.periyot_slot), L=int(r.sembol), K=int(r.comb), bw=int(r.bw_prb),
                       l0=int(r.sembol_ofset), s0=int(r.slot_ofset)) for r in df.itertuples()}

if __name__ == "__main__":
    KF = konfigler(); ids = [k for k in KF if KF[k]["periyot"] > 0]
    print(f"PRB basina veri RE (PRS yok) = 12*{len(PDSCH_SEM)} - 12*{len(DMRS_SEM)} - {N_OH} = {n_re_prb()}; MCS 28 qam64: Qm = {QM}, R = {R:.4f}")
    for w in (48, 273):
        t = tbs(n_re_prb() * w)
        print(f"   {w:3d} PRB: N_RE = {n_re_prb() * w}, TBS = {t} bit/slot -> {t * 1200 / 1e6:.2f} Mbps (1200 DL slot/s)")
    t6 = tbs((12 * 13 - 36 - 6) * 48)
    print(f"   duyarlilik: xOverhead = 6 alinsaydi 48 PRB TBS = {t6} -> {t6 * 1200 / 1e6:.2f} Mbps")

    # kontrol: kartin verdigi paylar
    print("\nKontrol: PRS'in 48 PRB'de PDSCH'den dusurdugu veri RE (M3) ve kartin verdigi pay:")
    for i, kart in KART_PAY.items():
        n = kayip_re_prb(KF[i], "M3") * 48
        print(f"   {i:3s}: model {n:5d} RE | PRS slotunda kayip pay: model {100 * n / (n_re_prb() * 48):5.1f} % "
              f"(DMRS haric 120 RE/PRB'ye gore), kart {kart:4.1f} % (13 sembole gore)")

    sat = []
    for senaryo, w in (("A (48 PRB)", 48), ("B (273 PRB)", 273)):
        c0 = throughput(None, "M0", w)
        for i in ["K0"] + ids:
            kf = KF[i] if i != "K0" else None
            row = dict(senaryo=senaryo, id=i, M0_Mbps=c0)
            for mod in ("M1", "M2", "M3"):
                c = throughput(kf, mod, w) if kf else c0
                row[f"{mod}_Mbps"] = c; row[f"{mod}_kayip_yuzde"] = 100 * (1 - c / c0)
            row["M2_kazanc_M1e_gore_yuzde"] = 100 * (row["M2_Mbps"] / row["M1_Mbps"] - 1) if row["M1_Mbps"] > 0 else np.nan
            row["M3_kazanc_M1e_gore_yuzde"] = 100 * (row["M3_Mbps"] / row["M1_Mbps"] - 1) if row["M1_Mbps"] > 0 else np.nan
            row["M3_kazanc_Mbps"] = row["M3_Mbps"] - row["M1_Mbps"]
            if kf:
                row["M2_prb_basina_kayip_re"] = kayip_re_prb(kf, "M2"); row["M3_prb_basina_kayip_re"] = kayip_re_prb(kf, "M3")
            sat.append(row)
    df = pd.DataFrame(sat); df.to_csv(os.path.join(OUT, "tbs_sonuclar.csv"), index=False, float_format="%.3f")
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    for senaryo in df.senaryo.unique():
        d = df[df.senaryo == senaryo]
        print(f"\nSenaryo {senaryo}: DL hizi (Mbps) ve PRS'siz duruma gore kayip (%)")
        cols = ["id", "M0_Mbps", "M1_Mbps", "M1_kayip_yuzde", "M2_Mbps", "M2_kayip_yuzde", "M3_Mbps", "M3_kayip_yuzde",
                "M3_kazanc_Mbps", "M3_kazanc_M1e_gore_yuzde"]
        print(d[cols].round(2).to_string(index=False))

    # ------------------------------------------------ sekil 1: PRB x slot RE haritalari
    goster = ["K1", "K6", "K7", "K8", "K11", "K9", "K10"]
    fig, axs = plt.subplots(1, len(goster), figsize=(2.0 * len(goster), 3.6), sharey=True)
    cmap = ListedColormap(["#f3f4f6", "#93c5fd", "#fde68a", "#f87171", "#6b7280"])   # bos/veri, veri, DMRS, PRS, PDCCH
    for ax, i in zip(axs, goster):
        g = np.ones((12, 14))
        g[:, 0] = 4
        for l in DMRS_SEM: g[:, l] = 2
        g[prs_prb_maske(KF[i])] = 3
        ax.imshow(g, origin="lower", aspect="auto", cmap=cmap, vmin=0, vmax=4)
        ax.set_xticks(range(0, 14, 2)); ax.set_xlabel("sembol", fontsize=8)
        ax.set_title(f"{i}: comb {KF[i]['K']}, {KF[i]['L']} sembol\nofset {KF[i]['l0']}; M3 kaybı {kayip_re_prb(KF[i], 'M3')} RE/PRB", fontsize=8)
        ax.set_xticks(np.arange(-0.5, 14, 1), minor=True); ax.set_yticks(np.arange(-0.5, 12, 1), minor=True)
        ax.grid(which="minor", color="white", lw=0.4); ax.tick_params(labelsize=7)
    axs[0].set_ylabel("alt taşıyıcı (1 PRB)", fontsize=8)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color="#6b7280", label="PDCCH (sembol 0)"), Patch(color="#93c5fd", label="PDSCH verisi"),
                        Patch(color="#fde68a", label="DMRS (2, 7, 11)"), Patch(color="#f87171", label="PRS")],
               loc="lower center", ncol=4, fontsize=8, frameon=False)
    fig.suptitle("PRS slotunda bir PRB'nin kaynak ızgarası (TS 38.211 §7.4.1.7.3 comb deseni, DMRS {2, 7, 11}, PDSCH sembol 1–13)", fontsize=9)
    fig.tight_layout(rect=(0, 0.08, 1, 0.95)); fig.savefig(os.path.join(OUT, "prs_prb_izgara.png"), dpi=140); plt.close(fig)

    # ------------------------------------------------ sekil 2: hiz karsilastirmasi
    fig, axs = plt.subplots(1, 2, figsize=(13, 4))
    for ax, senaryo in zip(axs, df.senaryo.unique()):
        d = df[df.senaryo == senaryo].set_index("id").loc[["K0"] + ids]
        x = np.arange(len(d))
        for j, (mod, c, ad) in enumerate((("M1", "#ef4444", "M1 PRB kapatma (OCUDU)"), ("M2", "#f59e0b", "M2 PRB×sembol rate matching"),
                                           ("M3", "#16a34a", "M3 RE (comb) rate matching"))):
            ax.bar(x + (j - 1) * 0.27, d[f"{mod}_Mbps"], 0.27, color=c, label=ad)
        ax.axhline(d.M0_Mbps.iloc[0], color="black", ls="--", lw=1, label="M0 PRS yok")
        if senaryo.startswith("A"):
            ax.set_ylim(20, 40)
        else:
            ax.set_ylim(150, 225)
        ax.set_xticks(x); ax.set_xticklabels(d.index, fontsize=8); ax.set_ylabel("DL hızı (Mbps)"); ax.grid(alpha=0.3, axis="y")
        ax.set_title(f"Senaryo {senaryo}: TBS hesabı (TS 38.214 §5.1.3.2), MCS 28 qam64, 1 katman", fontsize=9)
        ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "tbs_hiz_karsilastirma.png"), dpi=140); plt.close(fig)
    print(f"\ncikti: {os.path.relpath(OUT)}")

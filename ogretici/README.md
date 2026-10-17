# Öğretici (LaTeX)

`ogretici.tex` + `b0_...b8_*.tex` bölümlerinden **EHB415_ISAC_Ogretici.pdf** üretilir (30 sayfa).

| Klasör/dosya | Ne |
|---|---|
| `ogretici.tex`, `b*.tex` | LaTeX kaynağı |
| `betikler/make_figs.py` | Python şekilleri üretir (`numpy`, `matplotlib`, `pandas`) |
| `betikler/ocudu_prs_kos.sh`, `ocudu_prs_sweep.sh` | OCUDU PRS ölçümü (Ubuntu/WSL içinde) |
| `betikler/ns3_ue_sweep.sh` | ns-3 UE sayısı taraması (Ubuntu/WSL içinde) |
| `veri/` | Gerçek ölçüm çıktıları (CSV ve konsol kayıtları) |
| `sekiller/` | Üretilmiş şekiller |
| `fontlar/` | **Repoda yok**: Georgia, Arial, Consolas (telifli); `fontlar/README.txt`'e bakın |

## Derleme (Windows)

Tectonic kullanıldı (tek dosya, paketleri kendisi indirir): <https://github.com/tectonic-typesetting/tectonic/releases>

```powershell
cd ogretici
tectonic -X compile ogretici.tex
```

Şekilleri yeniden üretmek için: `python betikler\make_figs.py`

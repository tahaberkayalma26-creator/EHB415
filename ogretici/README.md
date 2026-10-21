# Öğretici (LaTeX)

`ogretici.tex` + `b0_...b8_*.tex` bölümlerinden **EHB415_ISAC_Ogretici.pdf** üretilir.

| Klasör/dosya | Ne |
|---|---|
| `ogretici.tex`, `b*.tex` | LaTeX kaynağı |
| `betikler/make_figs.py` | Python şekilleri üretir (`numpy`, `matplotlib`, `pandas`) |
| `betikler/ocudu_prs_kos.sh`, `ocudu_prs_sweep.sh` | OCUDU PRS ölçümü (Ubuntu/WSL içinde) |
| `betikler/ocudu_slot_log.sh` | OCUDU scheduler'ın slot başına kararlarını log'a döker (Bölüm 2.1) |
| `betikler/izgara_filmi.py` | OCUDU ızgara filmi (tek kullanıcı, PRS): `sekiller/ocudu_izgara_filmi.gif` |
| `betikler/ocudu_cok_ue.sh`, `ocudu_cok_ue_sweep.sh`, `ocudu_cok_ue_log.sh`, `ocudu_cok_ue_film.py` | OCUDU çok kullanıcılı deney ve film (Bölüm 4.5) |
| `betikler/ocudu_prs_yerlesim.sh` | PRS'i farklı yerlere koyar, OCUDU hangisini kabul ediyor? |
| `betikler/ilk_uygulama_referans.cc` | ns-3'te "iki bilgisayar, bir kablo" referans çözümü |
| `sionna_sehir/` | Sionna RT şehir projesi (kapsama, ışın yolları, İHA takip filmi); kendi `README.md`'si var |
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

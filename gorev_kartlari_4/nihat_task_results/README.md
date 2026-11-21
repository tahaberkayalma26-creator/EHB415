# Nihat – Görev Kartı 4 (ortak ızgara: n78, 3,5 GHz, 30 kHz, 100 MHz)

Görev tanımları iki kaynaktan alınmıştır: `gorev_kartlari_4/gorev_kartlari_4.pdf` ("Nihat: Sionna'da 3,5 GHz ve PRS sinyali" bölümü) ve `gorev_kartlari_4/CLAUDE.md` (Nihat – Sionna PRS Configuration, Nihat – Radar Configuration).

Değerler `ogretici/veri/ortak_degerler.xlsx` dosyasından alınmıştır. Asıl betiklere ve asıl `rt_sonuclar.npz` dosyasına dokunulmamıştır.

**Ana rapor (kısa, 11 sayfa):** [Nihat_Gorev_Karti_4_Rapor.md](Nihat_Gorev_Karti_4_Rapor.md), `.pdf`, `.docx`
**Ayrıntılı rapor (ara hesaplar ve ek tablolar, 27 sayfa):** [Nihat_Gorev_Karti_4_Rapor_ayrintili.md](Nihat_Gorev_Karti_4_Rapor_ayrintili.md), `.pdf`, `.docx`
**Ortak tablo (Sonuç şablonu G–K + ayrıntı sayfaları):** `Nihat_Ortak_Degerler_Tablosu.xlsx`
**Alınacak ekran görüntüleri:** [EKRAN_GORUNTULERI.md](EKRAN_GORUNTULERI.md)

## Teslimler

| Teslim | Kaynak | Raporda | Betik | Çıktı |
|---|---|---|---|---|
| (1) 4,9 / 3,5 GHz yol kazancı tablosu | Kart adım 1 | §A.1 | `rt_sehir_35.py`, `yol_kazanci_karsilastir.py`, `itu_35ghz.py` (kampüs) | `cikti/rt_3p5GHz/`, `cikti/rt_4p9GHz/`, `cikti/yol_kazanci_*`, `cikti/itu_35/` |
| (2) Pd tablosu (eski / yeni) ve RCS–frekans ayrıştırması | Kart adım 2 | §A.2 | `radar_takip_35.py`, `tr_metrik_olc_35.py` | `cikti/radar_35/`, `cikti/tr_metrik_olc_35_cikti.txt` |
| (3) K1–K3 hız tablosu ve üç sorunun cevabı | Kart adım 3 | §A.3 | `hiz_tablosu.py` | `cikti/hiz_tablosu_cikti.txt` |
| Menzil çözünürlüğü, 30 → 100 MHz | CLAUDE.md, Radar Configuration | §A.4 | `menzil_cozunurlugu.py` | `cikti/menzil_cozunurlugu/` |
| PRS'in n78'e taşınması ve K1–K11 denemesi | CLAUDE.md, Sionna PRS Configuration | §B.1–B.2 | `prs_takip_n78.py`, `itu_35ghz.py` | `cikti/prs_n78/`, `cikti/itu_35/` |
| Boş kaynakların veriye açılması, throughput iyileşmesi (TBS hesabı) | CLAUDE.md, Sionna PRS Configuration | §B.3 | `prs_veri_tbs.py` | `cikti/veri_tbs/` |
| Sonuç şablonu (G: Pd, H: hız çözünürlüğü, I: en büyük hız) | Kart kuralı | §C | `xlsx_doldur.py` | `Nihat_Ortak_Degerler_Tablosu.xlsx` |

## Klasör yapısı

```
nihat_task_results/
├── README.md, EKRAN_GORUNTULERI.md, Nihat_Ortak_Degerler_Tablosu.xlsx
├── Nihat_Gorev_Karti_4_Rapor.{md,tex,pdf,docx} (kısa), Nihat_Gorev_Karti_4_Rapor_ayrintili.{md,tex,pdf,docx}
├── ekran_goruntuleri/   terminal ekran görüntüleri (ve rapor için kırpılmış kopyalar)
├── betikler/   rt_sehir_35.py, radar_takip_35.py, tr_metrik_olc_35.py (asıl dosyaların kopyaları)
│               yol_kazanci_karsilastir.py, hiz_tablosu.py, prs_takip_n78.py, prs_veri_tbs.py,
│               menzil_cozunurlugu.py, itu_35ghz.py, xlsx_doldur.py (yeni)
└── cikti/      *_cikti.txt (her betiğin terminal çıktısı), rt_3p5GHz/, rt_4p9GHz/, radar_35/, prs_n78/,
                veri_tbs/, menzil_cozunurlugu/, itu_35/
```

## Yeniden üretme

Komutlar `betikler/` klasöründe çalıştırılmalıdır. Python yorumlayıcısı `~/venvs/ehb415/bin/python` (Sionna 1.2.2) olmalıdır. Sıra önemlidir.

```bash
cd gorev_kartlari_4/nihat_task_results/betikler
PY=~/venvs/ehb415/bin/python
$PY rt_sehir_35.py            # 3,5 GHz Münih sahnesi  -> ../cikti/rt_3p5GHz/        (~25 s)
$PY rt_sehir_35.py 4.9e9      # 4,9 GHz karşılaştırma  -> ../cikti/rt_4p9GHz/        (~25 s)
$PY yol_kazanci_karsilastir.py                                                     # (~2 s)
$PY radar_takip_35.py         # kaynak-başarı Monte Carlo -> ../cikti/radar_35/      (~1 dk)
$PY tr_metrik_olc_35.py       # Pd tablosu + ayrıştırma                            (~4 dk)
$PY hiz_tablosu.py
$PY prs_takip_n78.py          # PRS K1-K11, n78        -> ../cikti/prs_n78/          (~1,5 dk)
$PY prs_veri_tbs.py           # TBS / throughput       -> ../cikti/veri_tbs/
$PY menzil_cozunurlugu.py     #                        -> ../cikti/menzil_cozunurlugu/ (~1 dk)
$PY itu_35ghz.py              # ITU EEF kampüsü        -> ../cikti/itu_35/            (~2 dk)
$PY xlsx_doldur.py            #                        -> ../Nihat_Ortak_Degerler_Tablosu.xlsx
```

Rapor dosyaları `Nihat_Gorev_Karti_4_Rapor.md` kaynağından üretilir (`nihat_task_results` klasöründe çalıştırılır):

```bash
python3 betikler/rapor_tex_uret.py                      # -> Nihat_Gorev_Karti_4_Rapor.tex
pdflatex Nihat_Gorev_Karti_4_Rapor.tex && pdflatex Nihat_Gorev_Karti_4_Rapor.tex   # -> .pdf (iki kez)
python3 betikler/rapor_tex_uret.py Nihat_Gorev_Karti_4_Rapor_ayrintili.md --icindekiler   # ayrıntılı rapor (içindekiler sayfalı)
node betikler/rapor_docx_uret.js Nihat_Gorev_Karti_4_Rapor.md Nihat_Gorev_Karti_4_Rapor.docx   # Word (npm install docx)
```

Bu çalışma sırasında venv'e iki paket eklenmiştir: `openpyxl` 3.1.5 (xlsx yazımı için) ve `shapely` 2.1.2 (ITU sahnesindeki bina çokgenleri için; asıl `prs_itu.py` de bu pakete ihtiyaç duyar).

# Nihat – Görev Kartı 4: Alınması Gereken Ekran Görüntüleri

Kartın kuralı gereği her teslimde çalıştırılan komut ve görülen çıktı belgelenmelidir. Bütün çıktılar metin olarak `cikti/*_cikti.txt` dosyalarına kaydedilmiştir. Bu dosyada, terminal ekranından ayrıca alınması gereken görüntüler listelenmiştir. Görüntüler otomatik alınmamıştır; elle alınacaktır.

- **Hedef klasör:** `gorev_kartlari_4/nihat_task_results/ekran_goruntuleri/` (klasör henüz oluşturulmamıştır).
- **Biçim:** PNG. Komut satırı ve çıktının son satırı aynı görüntüde görünmelidir.
- **Çalışma dizini:** bütün komutlar `gorev_kartlari_4/nihat_task_results/betikler` klasöründe çalıştırılmalıdır. Python yorumlayıcısı `~/venvs/ehb415/bin/python` olmalıdır.

Grafik dosyaları (`cikti/**.png`) betikler tarafından üretildiğinden ekran görüntüsü olarak alınmaları gerekmez.

| # | Dosya adı | İlgili görev / teslim | Komut | Görüntüde görünmesi gereken | Süre |
|---|---|---|---|---|---|
| 1 | `ekran_01_rt_sehir_35.png` | Adım 1 (Teslim 1), Münih sahnesi, 3,5 GHz | `~/venvs/ehb415/bin/python rt_sehir_35.py` | `LOS olan nokta sayisi: 37/60` ve `FC = 3.50 GHz ... medyan yol kazanci -98.41 dB` satırları | ~25 s |
| 2 | `ekran_02_rt_sehir_49.png` | Adım 1, aynı betik 4,9 GHz ile (karşılaştırma) | `~/venvs/ehb415/bin/python rt_sehir_35.py 4.9e9` | `FC = 4.90 GHz ... medyan yol kazanci -101.74 dB` satırı | ~25 s |
| 3 | `ekran_03_yol_kazanci.png` | Teslim 1: 4,9 / 3,5 GHz yol kazancı tablosu | `~/venvs/ehb415/bin/python yol_kazanci_karsilastir.py` | 5 konumluk tablo; `tekrarlanabilirlik ... en buyuk mutlak fark 0.000 dB` satırı | ~2 s |
| 4 | `ekran_04_itu_35ghz.png` | Adım 1'in kampüs karşılığı ve PRS (ITU EEF) | `~/venvs/ehb415/bin/python itu_35ghz.py` | "Bolum 1" tablosu, `DOGRULAMA` satırı, "Bolum 2" K1–K4 satırları (çıktı uzunsa iki görüntü alınabilir: `_a`, `_b`) | ~2 dk |
| 5 | `ekran_05_radar_takip_35.png` | Adım 2: yeni radarın kaynak–başarı Monte Carlo'su | `~/venvs/ehb415/bin/python radar_takip_35.py` | İlk satır (`fc = 3.50 GHz ... N = 3276 ... RCS = -12.81`) ve sondaki Pd tablosu (alpha × menzil) | ~1 dk |
| 6 | `ekran_06_tr_metrik_olc_35.png` | Adım 2 (Teslim 2): Pd tablosu ve RCS / frekans ayrıştırması | `~/venvs/ehb415/bin/python tr_metrik_olc_35.py` | "3) 300 m'de Pd" bölümü, "4) Ayristirma" tablosu, "5) SNR butcesi" tablosu (gerekirse `_a` ve `_b` olarak iki görüntü) | ~4 dk |
| 7 | `ekran_07_hiz_tablosu.png` | Adım 3 (Teslim 3): K1–K3 hız tablosu | `~/venvs/ehb415/bin/python hiz_tablosu.py` | 3,5 GHz bloğu: K1 4,29 / K2 2,14 / K3 1,07 m/s ve 0,27 m/s | <1 s |
| 8 | `ekran_08_kod_satirlari.png` | Adım 3, soru 1–2: radar_takip.py'nin ardışık sembol modeli | `grep -n "m = np.arange(M)\|m \* TS\|vax = \|TS = \|FRAME_SYM = " ../../../ogretici/sionna_sehir/radar_takip.py` | 26, 32, 45, 48, 53. satırlar | <1 s |
| 9 | `ekran_09_prs_takip_n78.png` | CLAUDE.md – Sionna PRS yapılandırması (K1–K11 sensing) | `~/venvs/ehb415/bin/python prs_takip_n78.py` | "1) Yapilandirmalar" tablosu, "2) Pd, menzile gore" tablosu ve `Pf1` satırları (`_a`, `_b`) | ~1,5 dk |
| 10 | `ekran_10_prs_veri_tbs.png` | CLAUDE.md – boş kaynakların veriye açılması, throughput | `~/venvs/ehb415/bin/python prs_veri_tbs.py` | "Kontrol" bölümündeki beş satır (model RE sayısı ve kartın verdiği pay) ve Senaryo A tablosu (Senaryo B için `_b`) | ~3 s |
| 11 | `ekran_11_menzil_cozunurlugu.png` | CLAUDE.md – radar yapılandırması: 30 → 100 MHz menzil çözünürlüğü | `~/venvs/ehb415/bin/python menzil_cozunurlugu.py` | "1) Hesap" tablosu ve üç adet "2)" satırı (ayırma olasılığı) | ~1 dk |
| 12 | `ekran_12_sonuc_sablonu.png` | Kartın kuralı: sonuçların "Sonuç şablonu" sütunlarıyla verilmesi | `Nihat_Ortak_Degerler_Tablosu.xlsx` dosyası LibreOffice ya da Excel ile açılır; "Sonuç şablonu" sayfasına geçilir | G–K sütunları (K0–K11) ve tablonun altındaki dört not satırı | – |

Not: Betikler sabit tohumlarla çalıştığından, yeniden çalıştırıldığında aynı sayılar elde edilmelidir. Süreler bu makinede (12 çekirdek) ölçülmüştür.

## Durum (alınan dosyalar)

Görüntüler `ekran_goruntuleri/` klasörüne aşağıdaki adlarla konmuştur. Şekil numaraları kısa rapora (`Nihat_Gorev_Karti_4_Rapor.md`) göredir; ayrıntılı rapordaki numaralar parantez içinde verilmiştir. Rapora eklenmeyenler ilgili bölümde tek cümleyle anılmıştır.

| # | Kaydedilen dosya | Kısa raporda (ayrıntılı raporda) |
|---|---|---|
| 1 | `rt35.png` | Tek cümle, §A.1 (tek cümle) |
| 2 | `rt3549.png` | Tek cümle, §A.1 (tek cümle) |
| 3 | `yolkazancikarsilastir.png` | Şekil 1 (Şekil 1) |
| 4 | `itu35ghz.png` | Tek cümle, §A.1 ve §B.2 (Şekil 2) |
| 5 | `radartakip.png` | Tek cümle, §A.2 (tek cümle) |
| 6 | `tr_metrik_olc35.png` | Şekil 2, 3. ve 4. bölüm; kırpılmış kopya `tr_metrik_olc35_kirpilmis.png` (Şekil 3) |
| 7 | `hiz_tablosu.png` | Şekil 3, 3,5 GHz bölümü; kırpılmış kopya `hiz_tablosu_kirpilmis.png` (Şekil 4) |
| 8 | alınmadı | Kod satırları §A.3 Soru 1–2'de metin olarak verilmiştir |
| 9 | `prs_takip_n78.png` | Tek cümle, §B.2 (Şekil 7) |
| 10 | `prs_veri.png` | Tek cümle, Şekil 8 açıklaması (Şekil 10) |
| 11 | `menzil_cozunurlugu.png` | Tek cümle, §A.4 (Şekil 5; kırpılmış kopya `menzil_cozunurlugu_kirpilmis.png`) |
| 12 | alınmadı | "Sonuç şablonu" değerleri §C'de verilmiştir |

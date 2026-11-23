# Fatih - OCUDU proje dosyaları

Bu klasör Fatih'in OCUDU kurulumunu, Görev 2 ve Görev 4 teslimlerini, terminal ekran görüntülerini, ölçümleri ve kod değişikliklerini içerir.

## Rapor ve görseller

- [Görev 4 ekran görüntülü rapor](Gorev_4/Raporlar/Fatih_Gorev_Karti_4_Ekran_Goruntulu_Rapor.pdf)
- [Görev 4 tablolu rapor](Gorev_4/Raporlar/Fatih_Gorev_Karti_4_Rapor.pdf)
- [Görev 4 teslim özeti](Gorev_4/Raporlar/Fatih_Gorev_Karti_4_Teslim_Ozeti.pdf)
- [Doldurulmuş ortak değerler](Gorev_4/Raporlar/ortak_degerler_Fatih_sonuclar.xlsx)
- [Terminal ekran görüntüleri](Gorev_4/Ekran_Goruntuleri/Orijinaller)
- [Görev 2 sonuç özeti](Gorev_2/Raporlar/Fatih_Gorev_Karti_2_Sonuc_Ozeti.pdf)
- [İlk kurulum raporu](Kurulum/OCUDU_Kurulum_ve_Calistirma.pdf)

Word dosyaları da raporların yanındadır. Ekran görüntülü raporda beş terminal fotoğrafı kullanılır; altıncı fotoğraf tamamlanmış doğrulama koşularının arşiv özetidir. Word'deki kırpmalar kaynak fotoğrafların piksellerini değiştirmez. Tablolu ve ekran görüntülü rapor aynı sonuçların iki sunumudur.

## 100 MHz ve saat sorununun kodu

**Sistem saati elle 2 ms ileri alınmadı.** İki ayrı düzeltme yapıldı:

1. `lib/ru/dummy/ru_dummy_impl.cpp`, `ru_dummy_impl::run_slot()`, son kopyada 111-122. satırlar: sistem saatinden hesaplanan hedef slot geri gelirse yanlış slot ilerletme engellenir. Her bekleme turu 10 mikrosaniyedir; sistem saati değiştirilmez.
2. `lib/scheduler/ue_scheduling/cell_group_event_manager.cpp`, `handle_conres_ce_acked()`, son kopyada 226-232. satırlar: UE fallback modundan çıktığında `slice_sched.config_applied(ue_index)` bildirimi tamamlanır. Saat koruması tek başına 100 MHz sıfır veri sorununu gidermemiştir.

[İki düzeltmenin kodu ve açıklaması](100MHz_Duzeltmeleri/OKU_BENI.txt), [ZIP paketi](100MHz_Duzeltmeleri.zip), [ayrıntılı sorun analizi](Gorev_4/Notlar/100MHz_Sorun_Analizi.md).

Testte kullanılan `clock_step_inject.c` ayrı bir test yardımcısıdır: yalnız hedef sürecin saat okumasına -2 saniye sapma uygular. Gerçek düzeltme değildir ve bilgisayarın saatini değiştirmez.

## Kod, ölçümler ve tekrar çalıştırma

- `Gorev_4/Kod_Degisiklikleri`: yamalar, sekiz değişen OCUDU kaynak dosyasının son kopyaları, sürüm ve derleme kayıtları.
- `Gorev_4/Kaynaklar/Proje`: kullanılan ders projesi betikleri ve YAML ayarları.
- `Gorev_4/Araclar`: ölçüm, tekrar kontrolü ve rapor hazırlama araçları. Bu araçlarda Linux/Windows makinesine ait yollar yer alır; başka bilgisayarda çalışma dizinleri uyarlanmalıdır.
- `Gorev_4/Veriler`: toplu CSV/JSON sonuçlar.
- `Gorev_4/Ham_Kayitlar`: koşuların ayarları, terminal çıktıları, metrikleri ve mevcut sıkıştırılmış günlükleri.
- `Gorev_4/Dogrulama`: tekrar koşularının kayıt ve sonuçları.
- `Gorev_2/Proje`: önceki deneylerin betik, ayar, log ve görselleri.
- `Gorev_2/Ders_Projesi_Yerel_Kopya`: önceki Windows ders deposundaki yerel betik kopyası; Görev 4'teki sürümden ayrıdır.

OCUDU taban commit'i: `e0db566aac6e6376ddd60e83c84f58698fcc4d70`.
Ders projesi taban commit'i: `4c31d938648abb355e0befdd8221ae0d5cdfbbbb`.
OCUDU depo tamamı/derleme klasörü yerine değişen kaynaklar ve uygulanabilir yamalar eklenmiştir. PRS RE-TBS modeli deneysel bir scheduler/TBS modelidir; gerçek PHY rate matching veya standart UE desteği uygulandığı iddia edilmez.

Yamaların tümünü art arda uygulamayın: `00_referans_uyumluluk_toplu.patch` iki uyumluluk düzeltmesinin birleşimidir; `03_tum_deney_degisiklikleri.patch` bunları ve model değişikliklerini birlikte içerir. Alternatif paketler birbirinin üzerine uygulanmaz. Ayrıntı için kod açıklamalarını okuyun.

Makalelerin/standartların tam PDF kopyaları, kişisel okuma çevirileri, geçici kilit/önbellek dosyaları ve eski rapor sayfa denemeleri eklenmemiştir. Rapor ve deneylerin asıl dosyaları korunmuştur. `DOSYA_LISTESI.json` yüklenen dosyaların boyutlarını ve SHA-256 özetlerini içerir.

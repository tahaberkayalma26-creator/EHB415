# 100 MHz sorun analizi

20 Kasım 2026 — OCUDU `e0db566`, Ubuntu 24.04/WSL, n78 TDD, 30 kHz SCS, RU dummy test modu. İnceleme, birbirinden bağımsız iki sorun buldu. 100 MHz yapılandırması kabul ediliyor; bant genişliğinin desteklenmemesi ile sıfır trafik aynı durum değil.

## 1. Saat geri sıçraması ve yapay slot turu

`lib/ru/dummy/ru_dummy_impl.cpp:19–25`, slot sayısını `system_clock` üzerinden hesaplıyor. Özgün `run_slot()` ise hedefe yalnız ileri sayarak ulaşıyor. 30 kHz SCS için 500 µs olan slot süresinde sayaç çevrimi **20.971.520 slot**. Saat geri gittiğinde küçük bir geri fark, neredeyse tam çevrim kadar ileri işleme dönüşebiliyor.

Mevcut günlüklerin akış halinde incelenmesinde:

| Koşu | Günlükte büyük UTC geri sıçraması | MAC açık HyperSFN sayacının ileri ilerlemesi |
|---|---:|---:|
| `b100_r1` | 2,458618 s; satır 7024 | 20.978.466 slot; bir tam sayaç turu |
| `b100_r3` | 2,196986 s; satır 6483 | 20.977.741 slot; bir tam sayaç turu |

Yaklaşık 2,91 saatlik sanal slot ilerlemesi birkaç saniyelik günlük aralığında gerçekleşiyor. Milyonlarca MAC kuyruk dolu uyarısı ve yaklaşık 950 MB günlük bu davranışla uyumlu. Bu koşularda yüzlerce/binlerce metrik satırını duvar zamanı hız ölçümü gibi ortalamak geçerli değil.

İzole deney dalındaki saat koruması, çevrimin yarısından büyük modüler ileri farkı geri okuma olarak kaydedip o turda slot üretimini bekletiyor (`ru_dummy_impl.cpp:111–121`). **Saat sıçramasının alttaki nedeni henüz bilinmiyor:** TSC, WSL/VM zaman eşitlemesi veya başka bir etken arasında seçim yapılmadı. Kısa bağımsız saat testlerinde sıçrama görülmemesi, önceki günlük kanıtını ortadan kaldırmıyor. Doğal sıçrama olmayan yeni koşular tek başına bu korumanın etkinlik testi sayılmıyor.

## 2. ConRes tamamlandığında eksik planlayıcı bildirimi

Yalnız saat koruması bulunan 100 MHz ön kontrollerinde normal sayıda metrik satırı oluşmasına rağmen DL/UL sıfır kaldı. `tanisal100_info` kaydında Msg4 PDSCH `729.10` slotunda, ilk iki PUSCH `729.18/19` slotlarında görülüyor; ardından veri trafiği kesilip periyodik PUCCH devam ediyor. Test UE kuruluyor ve tamponlar dolu görünüyor.

Kaynakta olay sırası şöyle:

1. Test adaptörü Msg4 planlanınca `RRCSetupComplete` enjekte ediyor (`lib/du/du_high/test_mode/mac_test_mode_adapter.cpp:452–454`).
2. `handle_ue_config_applied()`, ConRes henüz tamamlanmadıysa UE'yi dilim planlayıcısına eklemiyor (`lib/scheduler/ue_scheduling/cell_group_event_manager.cpp:166–179`).
3. Daha sonra gelen Msg4/ConRes ACK'si UE'yi fallback durumundan çıkarıyor; özgün `handle_conres_ce_acked()` eksik dilim kaydını tamamlamıyordu.

Düzeltme, ACK gerçekten fallback çıkışını sağladığında `slice_sched.config_applied(ue_index)` çağrısını ekliyor (`cell_group_event_manager.cpp:226–232`). `BUILD_TESTING=OFF` bu sorunun nedeni değil: test modu adaptörleri koşulsuz derleniyor; seçenek GTest ve test hedeflerini yönetiyor.

## Doğrulanan trafik sonuçları

Saat koruması ve ConRes bildirimi birlikte bulunan `gnb_compat` ile üç 100 MHz referans koşusu (`ref100_1`–`ref100_3`) DL **36 Mbps**, UL **119 Mbps**, DL/UL başarılı işlem sayısı **1200/600** verdi. Bant taraması da trafik üretti:

| Bant genişliği | DL (Mbps) | UL (Mbps) |
|---:|---:|---:|
| 40 MHz | 36 | 44,9 |
| 60 MHz | 36 | 69,5 |
| 80 MHz | 36 | 94,6 |
| 100 MHz | 36 | 119 |

Ham kanıtlar ve değerlendirme aralıkları [Ham_Kayitlar](Ham_Kayitlar) altındaki koşu klasörlerinde saklanıyor. Bu sonuçlar ConRes düzeltmesi sonrasında trafiğin geri geldiğini gösteriyor; saat korumasının kontrollü geri sıçrama altında sınanması ayrı bir regresyon deneyi.

[Araclar/clock_step_inject.c](Araclar/clock_step_inject.c), bu deney için yalnız `gnb*` adlı süreçte `clock_gettime(CLOCK_REALTIME)` sonucunu beş saniye sonra kalıcı iki saniye geriye kaydıran yardımcı kaynaktır. İşletim sistemi saatini ve `CLOCK_MONOTONIC` değerini değiştirmez. Sonradan derlenerek aşağıdaki iki özel regresyon koşusunda kullanıldı.

## Kontrollü regresyon: sentetik, yalnız süreç içinde saat kaydırma

**Bu deney SENTETİK ve SÜREÇ YERELDİR; işletim sistemi/WSL saati ayarlanmadı.** İki koşunun terminalinde yardımcı kütüphanenin etkinleşme işareti var. PRS'siz 100 MHz ayarında, gNB'nin kendi gerçek zaman saati okumalarına beş saniye sonra kalıcı −2 s uygulandı. İşlem dışındaki komutlar ve `CLOCK_MONOTONIC` etkilenmedi.

| Kanıt | `clockstep2_korumasiz` | `clockstep2_korumali` |
|---|---:|---:|
| Metrik satırı | 21 | 22 |
| Toplam uyarı satırı | 5.099.968 | 26.967 |
| Geri saat koruması kaydı | yok | 26.965 |
| Sıkıştırılmamış günlük | 931.631.974 bayt | 35.030.897 bayt |
| Terminalde günlük kuyruğu dolu işareti | var | yok |

Korumalı koşunun ilk tanısı `previous=585509 observed=581509 backwards_slots=4000`: 500 µs slot süresinde tam **2 saniyelik geri okuma** yakalandı. Koruma, duvar saati önceki slotu yeniden yakalayana kadar slot üretimini bekletti; bu bekleme sırasında tanı uyarısını tekrarladığı için günlük bütünüyle uyarısız değil. Ölçüm penceresindeki korumalı satırlar DL 36 / UL 119 Mbps, DL/UL `ok` 1200/600 değerlerini verdi. Korumasız kontrolde günlük kuyruğu doldu, milyonlarca uyarı ve sıfır trafik satırları oluştu.

Bu karşılaştırma, geri saat okumasının eski ileri sayma döngüsünü bozabildiğini ve korumanın aynı yapay geri adım altında bu davranışı önlediğini doğruluyor. Doğal WSL saat sıçramasının TSC veya VM zaman eşitlemesinden kaynaklandığını kanıtlamıyor. **İki koşu da `measurement_valid=false` olarak, yalnız regresyon kanıtı şeklinde saklandı; hız veya işlemci performansı referanslarına katılmadı.** Normal aralıkta metrik satırı sayısı tek başına geçerlilik kanıtı değil.

Gerçek YAML ayarı her iki koşuda `all_level: info` idi. İlk özetlerdeki istek seviyesi `warning` gerçek ayarı yansıtmadığından metadata düzeltildi: `log_level: info`, `requested_log_level: warning` ve açıklama ayrı kaydedildi. Sonraki koşular için araçta mevcut tüm seviyeleri değiştiren düzeltme yapıldı. Sayımlar tam günlüklerden alınmıştır. İlk `clockstep_korumasiz` / `clockstep_korumali` denemeleri ortak günlük yolunu yeniden kullandığından geçersiz ve yerini bu ikinci çifte bırakmış tanı tekrarları olarak işaretlendi. Özgün referansın Windows'taki sıkıştırılmış günlüğü korunarak Linux kopyası geri yüklendi.

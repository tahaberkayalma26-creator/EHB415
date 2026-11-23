# PRS RE/TBS deneysel scheduler modeli

Hazırlanma tarihi: 20 Kasım 2026. Kaynak: `/home/fatih/ehb415/ocudu-gorev4`, commit `e0db566aac6e6376ddd60e83c84f58698fcc4d70` (`release26_10`).

Bu dosya başlangıçta altı dosyalık yama tasarımı olarak hazırlandı. Ardından yama izole çalışma ağacına uygulandı, başarıyla derlendi ve beş koşulda önce/sonra ölçümü yapıldı. Bu altı dosyalık alt yama saat ve ConRes düzeltmelerini içermez; uygulanan bütün değişikliklerin ve ek ölçüm izinin son hali 03_tum_deney_degisiklikleri.patch dosyasındadır.

## Amaç ve kapsam

Mevcut PRS scheduler, PRS'nin kullandığı comb alt taşıyıcıları yerine PRS bant genişliğinin bütün RB × sembol dikdörtgenini kapatıyor. Yama bu rezervasyonu kaldırır; slotun PRS PDU listesini korur ve yeni UE PDSCH tahsisinde yalnız PRS ile çakışan veri RE'lerini deneysel TBS hesabından düşer.

Model yalnız DU dummy/test UE üzerinde doygun trafik karşılaştırması içindir. Gerçek UE ile standartlara uygun birlikte çalışma veya ölçülmüş radyo throughput artışı iddiası taşımaz. Yapılandırmada PDSCH repetition kapalı olmalı; ölçüm kayıtları `retx=0` koşulunu doğrulamalıdır. Yama test mode'u veya bu koşulları otomatik zorlamaz.

## Dosyalar ve kaynak satırları

Satırlar yama öncesi kaynağa aittir; yama uygulandıktan sonra kayar.

| Dosya | Kaynak satırı / işlev | Değişiklik |
|---|---|---|
| `lib/scheduler/common_scheduling/prs_scheduler.cpp` | 189–193, `schedule_slot` | PRS PDU korunur; bütün PRS dikdörtgenini kapatan `dl_res_grid.fill` kaldırılır. |
| `lib/scheduler/ue_scheduling/ue_cell_grid_allocator.cpp` | 38–76, `calculate_dl_mcs_tbs` | Son fiziksel CRB aralıkları ve slot PRS PDU'ları ile yeni RE sayacı çağrılır. |
| `lib/scheduler/support/mcs_tbs_calculator.h` | 26–36, `compute_dl_mcs_tbs` | Varsayılan sıfır `nof_prs_data_re` parametresi eklenir; mevcut çağrılar korunur. |
| `lib/scheduler/support/mcs_tbs_calculator.cpp` | 204–264, `compute_dl_mcs_tbs` | İlk TBS hesabı (216–223), MCS azaltma TBS hesabı (245–251) ve iki kod oranı kontrolü (238, 256) aynı gideri kullanır. |
| `include/ocudu/ran/sch/tbs_calculator.h` | 74, yapı sonu | Sonuna varsayılan sıfır toplam `nof_re_excluded` alanı eklenir. |
| `lib/ran/sch/tbs_calculator.cpp` | 106–126, `tbs_calculator_calculate` | 109–110'daki RE bütçesinden toplam gider çıkarılır; sıfır bütçe sıfır byte döndürür. |

Yama sonrasında yeni `count_prs_data_re` işlevi allocator dosyasının 21. satırındadır. Ortak etkin kod oranı lambda'sı MCS/TBS dosyasının 248. satırındadır.

`intra_slice_scheduler.cpp:556–568` VRB'leri fiziksel CRB aralıklarına dönüştürür ve `set_pdsch_params` çağrısına iletir. Sayaç bu aşama sonrasındaki iki CRB aralığını kullandığı için interleaving ve kısmi frekans örtüşmesi hesaba katılır. `grant_params_selector.cpp:43–49` ilk PRB tahmini değiştirilmedi; nihai yeni iletim TBS'si düzeltilir. Doygun olmayan trafik için PRB seçimi PRS giderine göre yeniden optimize edilmez.

## RE hesabı

Yama öncesi TBS girdisi:

```text
N_RE_base = n_PRB × min(12 × N_sym - N_DMRS_per_PRB - N_oh_per_PRB, 156)
```

Her tahsis edilmiş fiziksel CRB ve PDSCH sembolü için aynı SCS'deki PRS kaynakları incelenir. Yalnız frekans ve sembol aralıkları kesişen kaynaklar alınır:

```text
offset(l) = (comb_offset + get_prs_freq_offset(comb, l - PRS_start_symbol)) mod comb
PRS_mask(l,rb) = union of {offset(l), offset(l)+comb, ... < 12}
data_mask(l,rb) = PRS_mask(l,rb) AND NOT DMRS_no_data_mask(l)
N_PRS_data = sum(popcount(data_mask(l,rb)))
N_RE_model = max(N_RE_base - N_PRS_data, 0)
```

PRS kaynaklarının maskeleri önce OR ile birleştirilir; aynı RE birden fazla PRS kaynağında bulunsa da bir kez sayılır. Geçerli PRS comb değerleri 12'yi böldüğü için aynı PRB içi comb maskesi her CRB'de kullanılabilir. Offset, hazır public `get_prs_freq_offset` yardımcısından alınır (`include/ocudu/ran/prs/prs.h:82`, `lib/ran/prs/prs.cpp:29–47`). Slot PDU listesinin kullanılması, scheduler'ın daha önce yaptığı periyot, slot offset, muting ve repetition seçimlerini tekrar kurmayı gerektirmez.

DMRS içeren sembollerde veri taşımayan RE'ler PRS giderinden çıkarılır. Maskeler PHY `get_dmrs_prb_mask` ile aynıdır (`include/ocudu/phy/upper/dmrs_mapping.h:37–53`): type 1 için `k % 2 < CDM_groups`, type 2 için `k % 6 < 2 × CDM_groups`. Bu işlem DMRS'nin veri bütçesinden iki kez düşülmesini önler; PRS–DMRS fiziksel çakışmasını çözmez.

Gider per-PRB 156 sınırından sonra toplam bütçeden düşülür. Bu, deney için açıkça seçilmiş toplam RE muhasebesidir; RRC `xOverhead` alanına dönüşüm yapılmaz. Sıfır RE'de minimum 24 bit TBS üretmek yerine sıfır byte döndürülür ve `compute_dl_mcs_tbs` geçersiz sonucu `nullopt` ile reddeder.

Etkin kod oranının kodlanmış bit paydası da her MCS adımında aynı `N_PRS_data × layers × Qm` kadar azaltılır. Sıfır veya negatif olacak payda için sonsuz oran kullanılır ve mevcut MCS azaltma/reddetme yolu çalışır. Ortak DL-SCH API'si değiştirilmez.

Tam 48 PRB ve bütün PRS sembolleri PDSCH ile kesiştiğinde ham PRS RE sayıları aşağıdadır. Bunlar deney sonucu değildir; yalnız aritmetik kontrol değerleridir.

| Senaryo | Sembol / comb | Ham PRS RE |
|---|---|---:|
| K1 | 4 / 4 | 576 |
| K6 | 12 / 4 | 1728 |
| K7 | 4 / 2 | 1152 |
| K8 | 12 / 12 | 576 |
| K11 | 6 / 6 | 576 |

Gerçek model girdisi tahsis genişliği, PDSCH sembol aralığı ve DMRS no-data kesişimine göre daha küçük olabilir. Ham sayıları otomatik olarak nihai veri kaybı kabul etmek doğru değildir. K1, K8 ve K11'in ham sayıları eşit olsa da DMRS ile kesişimleri farklı olabilir.

## HARQ, tekrarlar ve diğer kapsam sınırları

- `grant_params_selector.cpp:187–200` yeniden iletim için önceki RB sayısını ve MCS'yi korur. `ue_cell_grid_allocator.cpp:365–367` eski HARQ TBS'sini kullanır; yama bu davranışı değiştirmez. Yeniden iletim sırasında TB küçültülmez. Ancak yeni slotta PRS gideri arttığında eski TB'nin yeni kapasiteye sığıp sığmadığı ayrıca denetlenmez. Bu nedenle ölçümde `retx=0` şarttır.
- `ue_cell_grid_allocator.cpp:513–540` PDSCH repetition için aynı TBS/PDU'yu kopyalar. En kötü PRS örtüşmesine göre ortak TBS seçimi eklenmedi; repetition kapalı olmalıdır.
- SIB, paging, RAR ve fallback PDSCH yollarına yeni PRS muhasebesi eklenmedi. Genel PRS dikdörtgen rezervasyonu kaldırıldığı için bu iletimler de PRS ile fiziksel olarak çakışabilir. Deney penceresi ve trafik yorumunda bu sınır korunmalıdır.
- Soyut RRC `xOverhead`, CSI-RS ve DC muhasebesi için yeni bir ortak RE union modeli kurulmadı. CSI-RS'nin mevcut MCS yaklaşımı korunur. Bu sinyallerin ayarları ölçüm kaydına yazılmalı; basit model karşılaştırmasında `xOverhead=0`, CSI-RS kapalı ve DC taşıyıcı dışında tercih edilmelidir.
- Yeni PRS gideri varsayılan sıfırdır; PRS bulunmayan yeni UE PDSCH çağrıları mevcut hesap yolunu izler. Tamamen boş/geçersiz TBS RE bütçesi artık sıfır byte döndürür.

## PHY ve standart uyumluluğu sınırı

Bu yama PRS çevresinde gerçek PDSCH rate matching veya puncturing uygulamaz. `lib/fapi_adaptor/phy/p7/pdu_translators/pdsch.cpp:16–28` içindeki `fill_reserved_re_pattern` yalnız CSI-RS örüntülerini `proc_pdu.reserved` içine alır. PRS için PHY reserved maskesi, FAPI aktarımı veya UE'ye eşleşen bir kaynak eşleme bildirimi eklenmedi. PDSCH mapper bu RE'leri hâlâ veri için kullanabilir; PRS ve DMRS ile fiziksel yazım çakışmaları devam edebilir.

TS 38.214 §5.1.3.2 standart TBS hesabı DMRS ve yapılandırılmış `xOverhead` üzerinden tanımlıdır. Burada kullanılan exact PRS veri-RE gideri deneysel bir iç sayaçtır; standart bir UE'nin aynı DCI'dan aynı TBS'yi çıkardığını kanıtlamaz. §5.1.4.1 ve TS 38.331 `RateMatchPattern` RB × OFDM-sembol rezervasyonunu tanımlar; PRS alım yapılandırması kendiliğinden bu deneysel comb boşluklarını PDSCH alıcısına bildirmez. Gerçek UE desteği için PHY eşleme, kodlanmış bit sayısı, sinyal çakışmaları ve UE tarafındaki TBS/kaynak eşleme varsayımları birlikte tasarlanmalıdır.

## Yapılan doğrulama ve son durum

- İlk tasarımın `git apply --check` kontrolü başarılı oldu; ardından izole worktree üzerinde uygulandı.
- Clang 18/Ninja ile gNB derlemesi başarıyla tamamlandı. Gerçek derleme çıktıları `Derleme_Kayitlari/build_prs_model.log` ve `final_build_check.log` içinde saklandı.
- K1, K6, K7, K8 ve K11 önce/sonra çalıştırıldı. DL önce beşinde 29 Mbps iken sonra sırasıyla 35, 34, 35, 35 ve 35 Mbps oldu; UL 119 Mbps olarak kaldı.
- Tam 48 PRB tahsisinde günlükten okunan gerçek veri RE giderleri 432, 1296, 864, 432 ve 384 oldu. Bunlar yukarıdaki ham üst sınırlarla aynı değildir; DMRS kesişimi giderden çıkarıldı.
- Seçili on koşunun kaydedilmiş PDSCH grantlarında `nrtx=0` doğrulandı. Doğrulama `model_dogrulama.json` dosyasındadır. Bu sonuç gerçek UE veya yeniden iletim senaryosu doğrulaması değildir.
- Son kaynak için `git diff --check` ve bütün yamanın `git apply --reverse --check` kontrolü sıfır koduyla tamamlandı. Ters uygulama yapılmadı. Sonuçlar `final_kod_kontrolleri.json` dosyasındadır.
- Bağımsız birim testi eklenmedi; bu deneyin doğrulaması derleme, üç PRS’siz referans, seçili koşulların A/B ölçümü ve günlükteki RE/nrtx kanıtlarından oluşur.

Yeniden üretim için asıl dayanak `03_tum_deney_degisiklikleri.patch`, son kaynak kopyaları ve `surum_kaydi.json` dosyasındaki ikili özetlerdir. PHY ve gerçek UE sınırlamaları yukarıda belirtilmiştir.

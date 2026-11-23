# Fatih'in OCUDU görevi: ne yapıyoruz?

25 Ekim 2026. Kaynak: görev kartlarının 5. sayfasındaki "Fatih: OCUDU" kartı.

## Görevin tek cümlesi

OCUDU'da PRS için kaynak ayırdığımızda, kullanıcıya gönderilebilen verinin ne kadar azaldığını ölçmek ve bu azalmanın planlayıcı kodundaki nedenini açıklamak.

- **PRS:** Konumlandırma referans sinyali. Bu deneyde algılama tarafının kaynak maliyetini incelemek için kullanılıyor.
- **UE:** Kullanıcı cihazı; deneyde sanal telefon.
- **DL:** Baz istasyonundan kullanıcıya veri gönderimi.
- **Slot:** Kısa bir zaman dilimi. "Her 4 slotta PRS", bu sinyalin her dört zaman diliminde bir planlanması demek.
- **DL brate:** Kullanıcıya gönderilen verinin bit hızı.
- **ok:** Buradaki test tablosunda saniyedeki başarılı blok sayısı.

Ana araçların Ubuntu terminali, OCUDU ve kaynak kodunu okumak için VS Code. Sionna Nihat'ın, ns-3/5G-LENA Aziz'in ana çalışma alanı.

## Kartta beklenen çıktılar

1. **PRS tarama tablosu:** PRS periyodunu ve kapladığı bandı değiştir; DL hızını ve başarılı blok sayısını kaydet.
2. **Dört kullanıcı karşılaştırması:** PRS kapalı ve açıkken toplam hızı ve kullanıcı başına hızı karşılaştır.
3. **Kod incelemesi:** 4 sembollük PRS'nin neden 12 sembollük PRS kadar veri kaybına yol açabildiğini bir paragrafla açıkla. İncelenen dosya/fonksiyonları belirt.
4. **İsteğe bağlı bonus:** PRS yerleşimlerinin hangilerinin kabul edildiğini ve reddedildiğini not et.

Kartta temel teslimler için Perşembe akşamı belirtilmiş. Belge bir takvim tarihi vermiyor.

## Başlangıç olarak bilgisayarında yapılan iki ölçüm

Kurulu OCUDU 26.10.0, commit `e0db566aac6e6376ddd60e83c84f58698fcc4d70` kullanıldı. Deneyler sırayla, radyosuz test modunda ve bir sanal kullanıcıyla çalıştırıldı. Her koşulda 22 metrik satırı toplandı; son 15 satırın ortalaması alındı.

| Koşul | DL veri hızı | Başarılı blok/s |
|---|---:|---:|
| PRS kapalı | 59,0 Mbps | 1000 |
| Her 4 slotta PRS, 12 sembol, 104 PRB | 44,0 Mbps | 750 |

Bu koşulda veri hızı yaklaşık **%25,4**, başarılı blok sayısı **%25** azaldı. Her iki gNB koşusu da normal olarak, çıkış kodu 0 ile kapandı.

Ham kayıtlar, kullanılan YAML dosyaları, CSV ve sürüm bilgileri `ilk_iki_20261025T152612Z_298` alt klasöründe. Bunlar bizim güncel koşularımız; karttaki örnek değerlerden kopyalanmadı.

Bu ölçüm PRS'nin haberleşmeye kaynak maliyetini gösterir. WSL2 üzerinde koşul başına tek ölçümdür; gerçek radyo bağlantısı veya hedef algılama başarımı ölçümü değildir.

## Açık soru için ilk kod bulgusu

PRS yapılandırılan sembolleri ve frekans bloklarını ızgarada işaretliyor. Veri planlayıcısı ise PDSCH için bakılan uzun sembol aralığının herhangi bir yerinde dolu olan frekans bloğunu, o veri tahsisi açısından kullanılamaz sayabiliyor. Aynı frekans bandındaki 4 sembol ve 12 sembol bu nedenle aynı kullanılabilirlik sonucunu üretebiliyor. PDSCH tahsisi, kalan boş sembollere otomatik olarak kısaltılmıyor.

Bu, PRS'nin fiziksel olarak slotun tamamını doldurduğu anlamına gelmez. PRS'nin kullandığı kaynak ile veri planlayıcısının fiilen vazgeçtiği kaynak farklı olabilir.

Kurulu sürümde incelenen kaynaklar, `/home/fatih/ehb415/ocudu` altında:

- `lib/scheduler/common_scheduling/prs_scheduler.cpp`, 26-28 ve 189-193: PRS sembol/PRB aralığı ve rezervasyon; DL-PRS çevresinde PDSCH rate matching yapılmadığına ilişkin yorum.
- `lib/scheduler/ue_scheduling/intra_slice_scheduler.cpp`, 873-894: PDSCH aralığı boyunca kullanılan PRB'leri sorgulama.
- `lib/scheduler/cell/resource_grid.h`, 125-131 ve `resource_grid.cpp`, 138-146: sorgulanan sembollerden en az birinde dolu olan PRB'nin dolu kabul edilmesi.
- `lib/scheduler/config/time_domain_resource_helper.cpp`, 204-221: FDD varsayılan zaman tahsisi.
- `lib/scheduler/ue_scheduling/grant_params_selector.cpp`, 256-295: uygun zaman tahsisleri arasından en uzunun seçilmesi.

Bu bir kod incelemesi bulgusudur. Kendi 4/12 sembol karşılaştırmamız ve slot günlükleri henüz üretilmedi; araştırma cevabı bunlarla tamamlanmalı. Sinyalin fiziksel kaynak payı, rezervasyon dikdörtgeni ve ölçülen veri kaybını aynı oran olarak kabul etmemek gerekir. Ortak alfa tanımını Taha ile buna göre eşleştirebilirsiniz.

## Sıradaki çalışma

Tam PRS taraması ve dört kullanıcılı deneyler henüz yapılmadı. Yeni koşulları çalıştırmadan önce nasıl bir sonuç beklediğini bir-iki cümleyle yaz; sonra ölçümle karşılaştır. Değerler karttakilerden farklı olursa farkı ve olası nedenini kaydet.

Ubuntu'da proje klasörüne geçiş:

```bash
cd "/mnt/c/Users/fatih/OneDrive/Desktop/Data Com/EHB415"
```

İlk iki koşulu karttaki betikle kendin tekrarlamak için:

```bash
bash ogretici/betikler/ocudu_prs_kos.sh base 0 0 0
bash ogretici/betikler/ocudu_prs_kos.sh p4 4 12 104
```

Tekrarlanabilir başlangıç yardımcısı da `fatih_ocudu/ilk_iki_deney.sh` dosyasında; benzersiz etiketlerle çalışır ve ham kayıtları ayrı klasöre saklar. Yukarıdaki kısa komutlar ise kartın verdiği `/tmp` dosya adlarını yeniden kullanır. Aynı anda iki gNB deneyi çalıştırmayın.

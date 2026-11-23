PRS, “Positioning Reference Signal” demek; Türkçesi “Konumlandırma Referans Sinyali”. Baz istasyonunun gönderdiği, alıcının yapısını önceden bildiği özel bir radyo sinyalidir.Bunu ölçüm yapmak için gönderilen, tanınabilir bir işaret gibi düşünebilirsin. Alıcı, beklediği sinyalle eline ulaşanı karşılaştırarak sinyalin ne kadar geciktiği gibi bilgileri çıkarabilir. PRS normalde konum belirlemeye yardımcı olmak için kullanılır.



PDSCH / PDCCH: DL veri / DL kontrol kanalı.

PRB: 12 alt taşıyıcılık frekans birimi (kaynak bloğu)

SSB Senkronizasyon sinyali bloğu (hücreyi bulmak için)



OFDM sembolü, çok kısa bir süre boyunca birçok alt taşıyıcıda aynı anda gönderilen sinyallerin oluşturduğu bloktur. OFDM’de veri, frekans yönünde çok sayıda alt taşıyıcıya dağıtılır. Bunlar aynı anda çalışır. Bir OFDM sembolü boyunca her alt taşıyıcı, kendisine yerleştirilen bilgiyi taşır. Sonraki sembolde yeni bilgiler gönderilebilir. Örneğin “PRS, ofset 2’den başlayarak 4 sembol sürüyor” denirse PRS, slotun 2, 3, 4 ve 5. sembollerinde, kendisine ayrılan frekans kaynaklarında gönderiliyor demektir.

\----------------------------------------



Alt taşıyıcı, OFDM sinyalini oluşturan, belirli bir merkez frekansa sahip küçük taşıyıcı bileşenlerden biridir. Her biri bilginin bir bölümünü taşıyabilir; çok sayıda alt taşıyıcı aynı anda çalışır. Bunu yan yana uzanan veri taşıma şeritleri gibi düşünebilirsin.


***SCS, “Subcarrier Spacing”*** demek: alt taşıyıcı aralığı. Yan yana iki alt taşıyıcının merkez frekansları arasındaki farkı belirtir. Örneğin SCS 15 kHz ise komşu alt taşıyıcıların merkezleri arasında 15 kHz fark vardır. PRB ile birleştirelim: Bir PRB, yan yana 12 alt taşıyıcıdan oluşuyor.

**| SCS    | Bir PRB’nin frekans genişliği |**



| 15 kHz | 12 × 15 = \*\*180 kHz\*\* |

| 30 kHz | 12 × 30 = \*\*360 kHz\*\* |



\------------------------------------------






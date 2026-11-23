# PDSCH ve DL-PRS kaynak eşleme incelemesi

## Görev kartındaki soruya iki cümlelik cevap

Gerçek UE, gNB içindeki PRS RE maskesini kendiliğinden öğrenmez; TS 38.214 V18.2.0 §5.1.4-5.1.4.1 uyarınca RRC ile yapılandırılan rezervasyonları ve gerektiğinde DCI 1_1'in “Rate matching indicator” seçimini kullanarak PDSCH eşlemesini belirler. RateMatchPattern, PRS taşıyan RB/sembolleri korumaya elverişli olsa da PRS comb RE'lerini tek tek bildiren bir alan değildir; dolayısıyla PRS alım yapılandırması veya yalnız vericide RE çıkarılması, gerçek UE'nin aynı PDSCH boşluklarını uygulayacağını kanıtlamaz.

## Dayanaklar

1. **TS 38.214 V18.2.0, §5.1.4-5.1.4.1, s.43-44.** Yapılandırılmış/dinamik bildirilen kaynaklar PDSCH'ye kapalıdır. Bitmap çözünürlüğü RB ve OFDM sembolü düzeyindedir; gruplar DCI 1_1 ile seçilir.
   https://www.etsi.org/deliver/etsi_ts/138200_138299/138214/18.02.00_60/ts_138214v180200p.pdf
2. **TS 38.214 V18.2.0, §5.1.4.2, s.45-46; §5.1.6.5, s.65-67.** RE düzeyindeki tanımlı mekanizmalar LTE CRS ve ZP CSI-RS üzerinden açıklanır. PRS kaynak/comb parametreleri TS 37.355 §6.4.3'e bağlanır. Bu başlıklarda PRS'nin otomatik PDSCH boşaltma kaynağı olduğuna ilişkin genel bir kural bulunmadı.
3. **TS 38.331 V18.6.0, §6.3.2, RateMatchPattern, s.1021-1022.** resourceBlocks, symbolsInResourceBlock, periodicityAndPattern veya controlResourceSet alanları vardır; PRS comb RE maskesini tek tek taşıyan bir alan bulunmadı.
   https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/18.06.00_60/ts_138331v180600p.pdf
4. **TS 38.212 V18.2.0, §7.3.1.2.2, s.227.** Rate matching indicator alanı ve grupların dinamik seçimi açıklanır.
   https://www.etsi.org/deliver/etsi_ts/138200_138299/138212/18.02.00_60/ts_138212v180200p.pdf
5. **TS 38.211 V18.2.0, §7.3.1.5, s.122; §7.4.1.7.3, s.143-144.** PDSCH eşlemesi kullanılabilir kaynaklara, PRS comb eşlemesi ayrı sinyal kurallarına dayanır.
   https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/18.02.00_60/ts_138211v180200p.pdf

Resmi PDF kopyaları `Kaynaklar/Standart` klasöründe saklandı.

## Deneysel kodun sınırı

TS 38.214 §5.1.3.2'deki TBS hesabı DMRS ve RRC xOverhead parametrelerini kullanır. Deneysel PRS RE giderinin doğrudan TBS'den düşülmesi, standart bir UE'nin aynı taşıma bloğu büyüklüğünü çıkaracağını göstermez. Bu çalışmadaki kod denemesi, radyosuz testmodunda zamanlayıcı/TBS kapasite hesabını sınamaktadır; gerçek PHY PRS-PDSCH eşlemesi veya standart UE ile doğrulanmış haberleşme uygulanmış sayılmamaktadır.

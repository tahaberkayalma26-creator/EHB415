# Metrik Sözlüğü (TASLAK)

Amaç: ekipte biri "Pmd" ya da "α %10" dediğinde herkes aynı şeyi anlasın.
Kaynak: 3GPP TR 38.765 v20.0.0 (§4.1, §4.2, §6.2) ve Dickerson vd. (arXiv 2606.21677, denklem 9-12).

## 1. Radar ne kadar iyi çalıştı? (kazanç tarafı)

| Metrik | Sade anlamı | Nasıl hesaplanır | Birim | Hedef (TR 38.765, Tablo 4.2-1) | Hangi araçta |
|---|---|---|---|---|---|
| Kaçırma olasılığı (Pmd) | Drone vardı, bulamadık | her denemede (kaçırılan drone / gerçek drone), sonra denemelerin ortalaması (TR 38.765 §4.1: Pmd = (1/N) Σ Dn/Mn) | % | ≤ %5 | Sionna |
| Yanlış alarm Tip 1 (Pf1) | Hiç drone yokken "var" dedik | "en az bir nesne bulunan hedefsiz deneme sayısı" / "hedefsiz deneme sayısı" (Pf1 = (1/N) Σ Qn) | % | ≤ %5 | Sionna |
| Yanlış alarm Tip 2 (Pf2) | Drone varken, olmayan bir şeyi de "drone" sandık | her denemede (eşleşmeyen tespit / toplam tespit), en az bir tespitli denemeler üzerinden ortalama (Pf2 = (1/K) Σ D'n/M'n) | % | ≤ %5 | Sionna |
| Konum hatası | Bulduğumuz yer ile gerçek yer arasındaki fark | \|tahmin − gerçek\| | metre | 10 m (%90 güvenle) | Sionna |
| Hız hatası | Bulduğumuz hız ile gerçek hız arasındaki fark | \|tahmin − gerçek\| | m/s | 5 m/s (%90 güvenle) | Sionna |

"%90 güvenle": hataların en iyi %90'ı bu değerin altında kalmalı.
"Deneme (drop)": drone konumu ve gürültü her seferinde rastgele seçilen tek bir simülasyon koşusu.

## 2. İnternet ne kadar yavaşladı? (bedel tarafı)

| Metrik | Sade anlamı | Birim | Hangi araçta |
|---|---|---|---|
| Throughput (hız) | Saniyede taşınan veri | Mbps | OCUDU, ns-3 |
| Gecikme | Bir paketin gidiş süresi | ms | ns-3 |
| Paket kaybı | Gönderilip ulaşmayan paketlerin oranı | % | ns-3 |
| Başarılı slot / s | Saniyede kaç dilimde veri akabildi (OCUDU'da kaç slot PRS'e gitti) | adet/s | OCUDU |

Dickerson kuralı (denklem 12): radara α payı verilirse iletişim en fazla **(1 − α)** kadar kalır.
Yani T(η) = min{η, 1 − α}; η: istenen yük (0-1 arası).

## 3. α: radara giden kaynak payı (ortak eksen)

Standart (§6.2) üç tür kaynak tanımlıyor:
- **Tip 1:** sensing sinyali için kullanılan kaynak.
- **Tip 2:** Tip 1'in içinde, aynı zamanda iletişime de yarayan kısım (var olmayabilir).
- **Tip 3:** sensing sinyali değil ama sensing yüzünden iletişime de kullanılamayan kaynak.

İki hesap yolu, ikisi de raporlanmalı:
- **Seçenek 1** = (Tip 1 + Tip 3) / tüm DL+UL kaynak
- **Seçenek 2** = (Tip 1 − Tip 2 + Tip 3) / tüm DL+UL kaynak
- Tip 2 yoksa ikisi aynıdır.

## 4. α her araçta nasıl hesaplanıyor? (DOLDURULACAK / AÇIK NOKTALAR)

| Araç | α tanımı | Durum |
|---|---|---|
| Sionna | α = M / 140 (M: 10 ms'lik çerçevede sensing sembolü sayısı; 140 = 10 slot × 14 sembol) | Net |
| OCUDU | PRS'li slot oranı ≈ 1 / T_PRS (ölçüm: T=4 → 750/1000 slot kaldı → kayıp ≈ %25) | Net. Ölçüm (52 PRB, T=4): PRS 4 sembol da olsa 12 sembol de olsa, ofset 0, 2 ya da 10 olsa da DL 51 Mbps (kod: intra_slice_scheduler.cpp satır 876-878) |
| ns-3 / 5G-LENA | Sensing yükünü nasıl temsil edeceğimiz kararı yok (Aziz'in notuna ve Perşembe toplantısına bağlı) | **BELİRSİZ** |

Tip 2 ile ilgili not: OCUDU'daki PRS iletişimde kullanılmıyor, yani Tip 2 = 0 ve Seçenek 1 = Seçenek 2.

## 5. Dickerson hesabı (kendin yap)

α_sense = [Nb / (1 − OH)] × [f_sense / Nsym/s] × [N_PRB,sense / N_PRB,toplam]

| Terim | Anlamı | Değer |
|---|---|---|
| Nb | ışın sayısı | 1 (veya 8) |
| OH | sürekli giden kontrol/sinyal yükü payı | 0,14 |
| f_sense | saniyede kaç kez radar yapılıyor | 500 Hz |
| Nsym/s | saniyedeki toplam sembol | 14 000 |
| N_PRB,sense | radar sinyalinin kapladığı PRB (1291 / 12 → 108) | 108 |
| N_PRB,toplam | bantın toplam PRB'si | 270 |

Kontrol: Nb = 1 → %1,66; Nb = 8 → %13,29.

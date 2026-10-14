# EHB415 ISAC Projesi: Okuma Listesi

Bu klasördeki PDF'ler indirilmiş ve her biri için başlık, yazar, tarih arXiv/3GPP üzerinden doğrulanmıştır.
"Nerede ne var" notları, ilgili bölümü gerçekten okuyarak yazılmıştır. Sadece özetini okuduğum makaleler
**[özet düzeyinde]** diye işaretlidir; bunların bölüm referanslarını sen kontrol etmeden görev yapma.

> Bölüm numaraları PDF'teki numaralandırmayı izler. Sayfa numarası vermedim, çünkü arXiv sürümleri arasında kayabilir.

---

## Öncelik 0: Tüm grup okur (projenin omurgası)

### 0.1 `3GPP_TR_38.765_v20.0.0.pdf`: Study on ISAC for NR (Rel-20, 2026-06, 34 sayfa)
Proposal'daki ana referans. Hepsini okumana gerek yok, şu bölümler yeter:

| Bölüm | İçerik | Projeye faydası |
|---|---|---|
| 4.1 | Performans metrikleri: Missed detection (Pmd), False alarm Type 1/2 (Pf1, Pf2), konum ve hız doğruluğu. Formüller dahil | Sensing performans metriklerimizi **birebir buradan** alırız, kendimiz tanım uydurmayız |
| 4.2, Tablo 4.2-1 | Hedefler: Pmd, Pf1, Pf2 ≤ %5; yatay/dikey konum 10 m (%90 güven); hız 5 m/s (%90) | Sensing tarafında "başarılı" ne demek, eşiğimiz hazır |
| **6.2** | **Sensing resource ratio**: Type_1 (sensing sinyali kaynağı), Type_2 (Type_1'in haberleşmede de kullanılan kısmı), Type_3 (kullanılmayan ama haberleşmeye de açılamayan kaynak). Option 1: (T1+T3)/tüm DL+UL, Option 2: (T1−T2+T3)/tüm DL+UL | **Sensing overhead'ini nasıl tanımlayacağımızın standart cevabı** |
| 6.2, Tablo 6.2-1 | Baseline 1 (52 dBm, 80 dB izolasyon) ve Baseline 2 (37 dBm, 65 dB izolasyon) | Sionna ve ns-3'te kullanacağımız referans senaryolar |
| 5.1 | Ölçüm raporlama seviyeleri: A (ham veri), B (delay-Doppler-angle profili), C (tespit edilen nokta başına), D | Sensing verisinin ağda ne kadar yük getireceğini hesaplarken kullanırız |
| 7 ve 8 | Sensing mimarisi: SenF (Sensing Function), NsAP protokolü (gNB ile SenF arası), sensing initiation/report prosedürleri | OCUDU tarafında "sensing nereye takılır" sorusunun standart cevabı |
| 9 | Sonuç: Seviye A desteklenmedi, Seviye C ileri normatif çalışma için kabul edildi, sensing verisi için SCTP tabanlı protokol yığını (Option 1) önerildi | Tasarım kararlarımızı gerekçelendirmek için |
| Ek A | Değerlendirme varsayımları: UMa-AV, 100 MHz, 30 kHz SCS, 4/4.9 GHz, 7 site × 3 sektör, sektör başına 5 İHA, 0-180 km/s, RCS modeli | Simülasyon parametre tablomuz |

**Önemli gözlem:** 6.3.0'da şu not var: *"The performance of communication is not evaluated."* 3GPP çalışması sadece sensing
performansına bakıyor. Bizim projenin boşluğu tam burası: sensing eklenince **haberleşme performansına etkisi**.
Bunu raporda motivasyon olarak kullanabiliriz.

### 0.2 `arxiv_2608.11606.pdf`: Lin, *Integrated Sensing and Communication in 3GPP: Evolution from 5G-Advanced to 6G* (2026-08, 8 sayfa)
3GPP ISAC'in en güncel ve kısa özeti. Tek oturuşta okunur.

| Bölüm | İçerik | Projeye faydası |
|---|---|---|
| II, Tablo 1 | ISAC kullanım senaryosu aileleri ve baskın gereksinimleri | Senaryo seçimini gerekçelendirmek |
| III.A | SenF'in (Sensing Function) görevleri: yetkilendirme, sensing varlığı keşfi/seçimi, parametre sağlama, veri toplama | OCUDU'ya "SenF ile konuşan" bir bileşen eklemenin tarifi |
| III.B, Tablo 2 | Sensing bilgisi soyutlama seviyeleri (örnek, profil, tespit noktası, nesne) ve taşıma yükü | TR 38.765 5.1'deki Level A-D ile eşleştirilir; sinyalleşme overhead'i hesabı |
| IV.A | ISAC kanal modeli: hedef kanalı, arka plan kanalı, yerel kuplaj ayrımı | Sionna'da kanalı nasıl kuracağımız |
| IV.B | Monostatic sensing'in 5 adımı: sinyal yeniden oluşturma, kalibrasyon/self-interference bastırma, delay-Doppler-angle işleme, clutter bastırma/tespit, takip | Sionna'daki sensing zincirimizin iskeleti. Not: haberleşme zamanlaması boşluk bıraktığında Doppler işleme bozulur, bu bizim trade-off'umuzun fiziksel kaynağı |

### 0.3 `arxiv_2108.07165.pdf`: Liu vd., *ISAC: Towards Dual-functional Wireless Networks for 6G and Beyond* (JSAC 2022, 36 sayfa)
Alanın temel tutorial'ı. Baştan sona okumak gerekmez.
- **III (Performance Tradeoffs in ISAC)**, özellikle III.C (PHY trade-off) ve III.E (cross-layer): trade-off kavramının teorik zemini.
- **IV.A (Non-overlapped resource allocation)** ve IV.B (fully unified waveform): "sensing'e ayrı kaynak mı, aynı kaynak mı" ayrımı. Bizim senaryoda ayrı kaynak modeli (PRB rezervasyonu).
- **VII.C (Sensing-assisted resource allocation)**: sensing bilgisinin scheduler'a geri beslenmesi. Opsiyonel bir genişletme fikri.

> [özet düzeyinde] Bu makalenin içeriğini bölüm başlıkları seviyesinde okudum, formüllerine girmedim.

---

## Alan A: Sionna / fiziksel katman / sensing sinyal işleme

### A1 `arxiv_2505.24763.pdf`: Blandino vd. (NIST), *Detecting Airborne Objects with 5G NR Radars* (2025-05, 6 sayfa)
- **Ne yapıyor:** 5G NR PRS ile UMi/UMa ortamında İHA tespiti. Tam radar zinciri (clutter bastırma, açı/menzil tahmini, 3B konum). Sonuç: UMi'de %16'ya varan missed detection, konum hatası UMi'de 4 m, UMa'da 8 m içinde.
- **Projeye faydası:** TR 38.765'in tarif ettiği İHA senaryosunun açık kaynak bir uygulaması var: `github.com/usnistgov/5GNRad` (makale `5gnr-radar` adıyla veriyor, depo bu isme taşınmış). Sionna tarafı için **hazır başlangıç noktası** ve kendi sonuçlarımız için doğrulama referansı.

### A2 `arxiv_2408.00667.pdf`: Khosroshahi vd., *Leveraging PRS and PDSCH for ISAC* (2024-08, 6 sayfa)
- **Ne yapıyor:** Sensing için PRS, haberleşme için PDSCH kullanıyor. PRS'in ghost target problemini DMRS ile çözüyor. PRS ile PDSCH arasında zaman/frekans kaynak paylaşımı problemini kuruyor ve **Pareto optimal nokta** buluyor.
- **Projeye faydası:** Proposal'daki "sensing vs haberleşme trade-off" hedefinin **doğrudan fiziksel katman karşılığı**. Pareto eğrisi yöntemini kendi grafiklerimize uyarlarız.

### A3 `arxiv_2211.11488.pdf`: Wei vd., *5G PRS-Based Sensing: A Sensing Reference Signal Approach* (2022-11, 23 sayfa)
- **Ne yapıyor:** PRS tabanlı radar sensing şeması, menzil/hız kestirim performansı, çoklu frame ile hız doğruluğu, **CRLB türetimi**.
- **Projeye faydası:** Sionna simülasyonundaki sonuçları teorik sınırla (CRLB) karşılaştırmak için formüller.

### A4 `arxiv_2504.21719.pdf`: Aït Aoudia vd., *Sionna RT: Technical Report* (2025-04, 61 sayfa) ve `arxiv_2203.11854.pdf`: *Sionna: An Open-Source Library* (5 sayfa)
- Sionna'nın ne yaptığı, ray tracer'ın nasıl çalıştığı. Bunlar referans doküman, baştan sona okunmaz; Sionna kullanan kişi gerektiğinde bakar.

> [özet düzeyinde] İkisini de sadece özet ve içindekiler seviyesinde okudum.

### A5 `arxiv_2512.03506.pdf`: Liu vd., *Survey of 3GPP Release 19 ISAC Channel Modeling* (2025-12, 28 sayfa, ~22 MB)
- Rel-19'da ISAC kanal modelinin (E-GBSM, RCS, hedef hareketi, mekânsal tutarlılık) nasıl kurulduğu.
- **Projeye faydası:** Sionna'da hangi kanal bileşenlerini modellememiz gerektiğini anlamak.

> [özet düzeyinde] Sadece özet ve arama sonucundaki açıklamasını gördüm. Bölümlerini incelemedim.

---

## Alan B: ns-3 / 5G-LENA / ağ seviyesi

### B1 `arxiv_2508.04004.pdf`: Ropitault vd., *Enabling Site-Specific Cellular Network Simulation Through Ray-Tracing-Driven ns-3* (2025-08, 6 sayfa) ⭐
- **Ne yapıyor:** 5G-LENA'ya **SioLENA** adında bir modül ekliyor. Dış ray tracer'dan (örn. **Sionna RT**) gelen çok yollu bileşenleri (MPC: gecikme, genlik, faz, AoA/AoD) CSV olarak alıp 5G-LENA'nın kanal modeline besliyor. Kod: `github.com/usnistgov/siolena`, Sionna'dan CSV üreten araç: `github.com/wineslab/sionna-channel-generator`.
- **III.B** (SioLENA trace-based channel model) ve **III.C** (Sionna RT → ns-3 hattı) bölümleri kritik.
- **Projeye faydası:** Proposal'daki *"Sionna ve ns-3 arasında bağlantı kurulabilir mi"* sorusunun cevabı **zaten var**. Sionna RT ile üretilen kanal ns-3'e bu hat üzerinden girebilir. Mimari kararımız bu çalışmanın üstüne oturabilir.

### B2 `arxiv_2205.03278.pdf`: Koutlia vd., *Calibration of the 5G-LENA System Level Simulator in 3GPP reference scenarios* (2022-05, 26 sayfa)
- 5G-LENA'nın 3GPP referans sonuçlarıyla nasıl kalibre edildiği.
- **Projeye faydası:** Simülasyon sonuçlarımıza "bu simülatör güvenilir mi" sorusuna karşı referans verebiliriz. Ayrıca REM (radio environment map) çıktısı kurulumun doğruluğunu kontrol etmenin kolay yolu.

### B3 `Downlink_Packet_Scheduling_in_LTE_Cellular_Networks...pdf` (Capozzi vd., IEEE Surveys & Tutorials 2013, 23 sayfa; proposal klasöründe)
- Scheduler tasarım meseleleri (II-III) ve kanal-farkında/QoS-farkında stratejiler (IV.B, IV.C: PF, M-LWDF, EXP/PF). Sec. V sayısal sonuçlar.
- **Projeye faydası:** Sensing'e ayrılan kaynak, scheduler'ın dağıtabileceği PRB sayısını azaltır. LTE ve 2013 tarihli olduğu için **kavramsal temel**, 5G-LENA'nın scheduler'ları için doğrudan kılavuz değil. Metrik tanımları (gecikme, PLR, throughput, fairness) Sec. V'ten alınabilir.

---

## Alan C: Ağ mimarisi / OCUDU / açık RAN

### C1 `arxiv_2509.16917.pdf`: Lindenschmitt vd., *Analysis of an Architecture for ISAC in 5G OpenRAN* (2025-09, 9 sayfa) ⭐
- **Ne yapıyor:** ISAC'ı OpenRAN'a nasıl entegre ederiz sorusunu analiz ediyor: monostatic yarı-dupleks sensing, radar setup seçenekleri, sinyal verisi, radar işlemenin yeri.
- **3.3 + Tablo 1:** Radar işleme **RU, DU veya DU'ya bağlı RIC** içinde olabilir. Her birinin avantaj/dezavantajı karşılaştırılmış.
- **4.4 (Open Research):** *"Slicing ile farklı numerology/TDD pattern'lerinin sensing kalitesini nasıl etkilediği ve scheduler'ın sensing ile haberleşmeyi nasıl dengelemesi gerektiği iyi anlaşılmış değil."* Bu cümle bizim proje sorumuzla örtüşüyor.
- **5 (Architectural Recommendation):** İkinci bir "sniffer RU" ile hiçbir standart değişikliği gerektirmeyen mimari önerisi (Cat. B fronthaul).
- **Projeye faydası:** Proposal'daki "sensing hangi katmanda olmalı, önceden varsayma" hedefinin literatürdeki en yakın karşılığı. Entegrasyon noktası seçeneklerini buradan çıkarırız.

### C2 `arxiv_2608.10784.pdf`: Gurung vd., *Multi-UAV Tracking Evaluation Using 5G Uplink Signals on an O-RAN ISAC Simulation Testbed* (2026-08, 25 sayfa)
- **Ne yapıyor:** **OpenAirInterface + FlexRIC + Sionna RT** ile kurulmuş bir O-RAN ISAC test ortamı. Uplink SRS'i pasif radar dalga biçimi olarak kullanıyor. Takip sonuçları RIC üzerindeki bir xApp'ten dışarı aktarılıyor.
- **III (Testbed Architecture)** ve **IV (UL-SRS Sensing Pipeline)** bölümleri: mimari olarak "Sionna + açık kaynak RAN + RIC" kombinasyonunun nasıl bağlandığının örneği.
- **Projeye faydası:** Bizim planımıza (Sionna + açık kaynak RAN) çok yakın bir mimari. OAI kullanıyor, OCUDU değil, ama yapı tekrar kullanılabilir.

### C3 `arxiv_2601.03535.pdf`: Zhou vd., *OpenISAC: An Open-Source Real-Time Experimentation Platform for OFDM-ISAC* (2026-01, 16 sayfa)
- USRP tabanlı, gerçek zamanlı, C++ baseband + Python arayüzlü OFDM-ISAC platformu (monostatic ve bistatic delay-Doppler). Kod: `github.com/zhouzhiwen2000/OpenISAC`.
- **Projeye faydası:** Donanım yok ama OFDM sensing işlemesinin açık kaynak referans implementasyonunu incelemek için. Gerçek zamanlı prototipin "nasıl göründüğünü" gösterir.

---

## Alan D: Kaynak tahsisi ve trade-off (projenin asıl sorusu) ⭐

### D1 `arxiv_2606.21677.pdf`: Dickerson vd., *Adaptive 5G Resource Allocation for Multistatic ISAC-Based UAV Detection and Tracking* (2026-06, 10 sayfa) ⭐⭐
- **III.B (Communication Resource Model):** Sensing kaynak tüketimini PRB cinsinden modelliyor. Denklem (9): `α_sense = (N_b / (1−OH)) · (f_sense / N_sym/sec) · (N_PRB,sense / N_PRB,total)`. Denklem (10)-(12): fizibilite koşulu, adaptif ZC dizisi uzunluğu, normalize throughput `T(η) = min{η, 1 − α_sense}`. Dört politika: haberleşme-öncelikli, sensing-öncelikli, adaptif, adaptif + fırsat sinyalleri.
- **IV.A:** Tek ışın, ZC uzunluğu 1291, 500 Hz hızda sensing kaynakların sadece %1,66'sını tüketiyor; 8 ışında %13,29.
- **Projeye faydası:** Proposal'daki "sensing yükü ile haberleşme performansı arası trade-off" için **hazır analitik model**. Bunu ns-3'te simülasyonla doğrulayabiliriz: model `T(η)` öngörüyor, 5G-LENA ne ölçüyor? Bu bizim ana deney tasarımımız olabilir.

### D2 `arxiv_2412.20314.pdf`: Wang, Abanto-Leon, *Resource Allocation for ISAC Networks with Application to Target Tracking* (2024-12, 6 sayfa)
- Zaman, frekans, güç, uzay boyutlarında ortak kaynak tahsisi optimizasyonu. Hedef takibi (posterior CRB'nin izini minimize) + haberleşme throughput kısıtı.
- **Projeye faydası:** D1'in analitik modelinden daha ileri, optimizasyon tabanlı. Proje sonunda "ileri çalışma" ya da karşılaştırma olarak. Matematiği ağır, öncelik düşük.

> [özet düzeyinde] Sadece özetini okudum.

---

## Standardizasyon bağlamı (isteğe bağlı)

### E1 `arxiv_2506.11828.pdf`: Lin, *A Tale of Two Mobile Generations: 5G-Advanced and 6G in 3GPP Release 20* (2025-06, 9 sayfa)
- Rel-20 genel bakışı. ISAC bölümü **III.B**: Rel-19'da senaryolar + kanal modelleri, Rel-20'de gNB monostatic sensing İHA için; RAN sensing sinyalini iletir/ölçer, çekirdek ağ sensing verisini yönetir.
- Zaten 0.2'yi okuyan kişi için gerek yok. Sadece raporun giriş bölümü için bağlam.

> [özet düzeyinde] ISAC bölümünü okudum, gerisine bakmadım.

---

## Önerilen okuma sırası (kişi bazlı atama sende)

| Sıra | Herkes | Süre tahmini |
|---|---|---|
| 1 | 0.2 (Lin, 8 sayfa) | 1 oturum |
| 2 | 0.1 (TR 38.765): sadece 4, 6.2, 9 ve Ek A | 1 oturum |
| 3 | Kendi alanının makaleleri (A / B / C / D) | 2-3 oturum |

Atama önerisi (kendi kararına bırakıyorum):
- **Standart + metrik kişisi:** 0.1 tamamı, D1, D2
- **Sionna kişisi:** A1, A2, A3, A4, A5
- **ns-3 kişisi:** B1 ⭐, B2, B3
- **OCUDU kişisi:** C1 ⭐, C2, C3

# Görev Kartı 4 - yapılan işlemler ve sonuçlar

Çalışma: 19-20 Kasım 2026. Fatih için görev kartında istenen OCUDU adımları uygulandı. Açıklamalar, ölçüm sonuçları, komutlar ve kod değişiklikleri bu klasöre kaydedildi.

## Okunacak dosyalar

- `Fatih_Gorev_Karti_4_Teslim_Ozeti.pdf`: görev kartının dört teslim maddesine karşılık gelen kısa sonuç özeti.
- `Fatih_Gorev_Karti_4_Rapor.docx`: önceki Word raporundaki sade ve edilgen anlatıma uygun ayrıntılı açıklamalar; çalıştırılan komutlar ve gerçek çıktı alıntıları.
- `ortak_degerler_Fatih_sonuclar.xlsx`: ortak değerler, K0-K11 ölçümleri, bant taraması ve ayrı önce/sonra karşılaştırması. Özgün `ortak_degerler.xlsx` korunmuştur.
- `100MHz_Sorun_Analizi.md`: ilk sıfır hız sorununun, saat kararsızlığının ve kontrollü doğrulamanın ayrıntıları.
- `Standart_Incelemesi.md`: standart sorusunun iki cümlelik cevabı ve resmî kaynak kanıtları.

## Tamamlanan görevler

- Güncel proje betikleri ve n78 ayarları edinildi; eski proje ve önceki görevdeki kullanıcı dosyaları korunarak ayrı deney alanı açıldı.
- İlk 100 MHz denemeleri üç kez ve 40/60/80/100 MHz taraması yapıldı. Terminal, hata/uyarı günlükleri ve çalışma sırasındaki `top` çıktıları saklandı.
- Sıfır hız ve kararsız slot zamanlaması ayrı nedenler olarak incelendi. Saat koruması ve ConRes sonrası slice scheduler bildirimi eklendi; ayrı sürümlerle etkileri ayrıldı.
- Çalışan 100 MHz ızgarada üç PRS’siz referans ve PDSCH PRB aralığı ölçüldü.
- K1-K11 koşulları çalıştırıldı; DL/UL/ok, kabul/ret ve ilgili PDCCH hata sayıları kaydedildi.
- Ayrı OCUDU dalında PRS RE/TBS modeli uygulandı, derlendi; K1/K6/K7/K8/K11 önce/sonra karşılaştırıldı.
- 3GPP/ETSI standardındaki PDSCH/PRS kaynak eşleme sorusu bölüm numaralarıyla cevaplandı.

## Kullanılan ortam ve kaynaklar

- Ubuntu-24.04, WSL; OCUDU release26_10, `e0db566aac6e6376ddd60e83c84f58698fcc4d70`.
- Güncel ders projesi: `https://github.com/tahaberkayalma26-creator/EHB415`, commit `4c31d938648abb355e0befdd8221ae0d5cdfbbbb`.
- Ayrı proje kopyası: `/home/fatih/ehb415/gorev4_project`.
- Ayrı OCUDU çalışma ağacı: `/home/fatih/ehb415/ocudu-gorev4`, dal `fatih/gorev4-clockguard`.
- Asıl `/home/fatih/ehb415/ocudu` kurulumunun kaynaklarına ve Windows’taki önceki görev projesine müdahale edilmedi. Uzak depoya gönderim yapılmadı.
- Ortak ayarlar: n78, yaklaşık 3,5 GHz, ARFCN 633334, SCS 30 kHz, 100 MHz/273 PRB, TDD; no_core, dummy RU, tek test UE. Gerçek anten/telefon kullanılmadı.
- Kaynak YAML içindeki eski 15 kHz/20 MHz yorumu gerçek değerleri yansıtmadığı için değerlendirmede `common_scs` ve `channel_bandwidth_MHz` alanları esas alındı.

## Excel ve görev kartı arasındaki farklar

- Kullanıcının özgün Excel’inde K0-K10 vardı; K11 yoktu. K11 güncel proje Excel’inin `PRS konfigürasyonları!A13:H13` aralığından alındı: periyot10, sembol6, comb6, BW48, sembol ofset2, slot ofset1. Kaynağı ayrı belirtildi; parametre uydurulmadı.
- XLSX satırlarında tekrar/boşluk tanımlı olmadığından görev kartının K1 örneği ve güncel betik varsayılanı olan 1/1 kullanıldı. Tüm PRS koşullarında slot ofseti1 kullanıldı.
- Önceden girilmiş teorik kayıp hücreleri deney sonucu sayılmadı. Nihat’a ait radar tespit/menzil/hız değerleri ölçülmedi ve doldurulmadı.

## İlk 100 MHz sorunu ve düzeltmeler

1. İlk koşuların bir bölümünde normal yaklaşık22 rapor satırı yerine yüzlerce/binlerce satır ve yaklaşık950 MB günlük oluştu. Bu koşuların satır ortalamaları duvar zamanı throughput ölçümü olarak kullanılmadı. 40 MHz denemelerinden biri `std::system_error: cannot write to file: Resource temporarily unavailable` ile134 çıkış kodunda durdu.
2. UTC saatinde yaklaşık2,2-2,46 s geri sıçrama ile RU dummy’nin yalnız ileri giden slot döngüsünün tam tur atması birlikte görüldü. Geri hedefi fark edip bekleyen koruma eklendi. Alttaki WSL/TSC/VM saat sıçramasının kesin nedeni bulunamadı; ayrı8s saat problarında sıçrama yakalanmaması da kaydedildi.
3. Saat koruması bulunan 100 MHz koşusunda hız yine0 kaldı; dolayısıyla iki sorun aynı kabul edilmedi. Debug log ve kaynak incelemesinde, ConRes onayıyla fallback’ten çıkan UE’nin slice scheduler’a bildirilmemesi bulundu. Durum geçişine bağlı `slice_sched.config_applied` bildirimi eklendi.
4. `gnb_compat` yalnız bu iki düzeltmeyi içerir; ana referans ve tüm `oncesi_` PRS ölçümlerinin temelidir. RE/TBS modeline ait değişiklikler bu temel sürüme karıştırılmadı.
5. Düzeltilmiş100 MHz referansları üç kez DL36/UL119 Mbps, DLok1200/ULok600 verdi. Ham satır sayıları23/23/22, kullanılan iç satırlar21/21/20’dir.
6. Düzeltilmiş bant taraması: 40MHz36/44,9; 60MHz36/69,5; 80MHz36/94,6; 100MHz36/119 Mbps. Bu aralıkta akışın durduğu bir bant görülmedi; 40MHz yedeğe geçilmedi.
7. PDSCH günlüğünde 10.637 kez `rb=[0..48)` görüldü; yani baskın veri genişliği48 PRB. Daha dar tahsisler de vardı. 273 PRB taşıyıcının tamamı PDSCH verisi sayılmadı.

## PRS sonuçları

- K0: DL36, UL119 Mbps; DLok1200, ULok600.
- K1/K4/K6/K7/K8/K9/K10/K11: DL29, UL119; DLok1000, ULok600.
- K2: DL32, UL119; DLok1100, ULok600.
- K3: DL34, UL119; DLok1150, ULok600.
- K5: DL32, UL119; DLok1200, ULok600.
- K1-K11’in tamamı kabul edildi; ret mesajı oluşmadı. Kabul, hatasız günlük anlamına gelmez. K1/K9/K10’da sırasıyla1584/1593/531 SIB1 kaynak ayırma hata satırı kaydedildi.
- K1/K9/K10’da `Failed to allocate PUSCH. Cause: No space in PDCCH.` sayısı0, UL119 Mbps bulundu. Önceki farklı FDD deneyinin UL düşüşü bu TDD ızgarada tekrarlanmadı.
- Her koşunun komutu ve yapılandırması ayrı saklandı. Bit hızı terminalde yuvarlatılmıştır; yüzde kayıplar bu gösterilen değerlerden hesaplandı.

## RE/TBS kod deneyi

- Bütün PRS RB/sembol dikdörtgenini kapatan `dl_res_grid.fill` kaldırıldı; PRS PDU listesi korundu.
- Son fiziksel PDSCH tahsisi ile PRS comb maskesi kesişimi sayıldı. Maskeler birleştirildi; DMRS nedeniyle zaten veri taşımayan RE’ler iki kez düşülmedi. TBS ve etkin kod oranı yolları aynı giderle güncellendi.
- Tam48 PRB için günlükten okunan veri RE giderleri K1/K6/K7/K8/K11’de432/1296/864/432/384’tür. Ham576/1728/1152/576/576 üst sınırları ölçülmüş gider olarak gösterilmedi.
- DL önce beşinde29 iken sonra35/34/35/35/35 Mbps oldu; UL119, DLok1200, ULok600 kaldı.
- Seçili10 önce/sonra günlüğünün kaydedilmiş PDSCH tahsislerinde `nrtx=0` doğrulandı. Ayrıntı `model_dogrulama.json` içinde saklandı.
- Derleme tamamlandı. Son derleme, `git diff --check` ve yamanın ters uygulanabilirlik kontrolü başarılı oldu; ters uygulama yapılmadı.
- Bu scheduler/TBS deneyi gerçek PHY rate matching uygulaması değildir. PRS reserved-RE aktarımı, eşleşen UE bildirimi ve fiziksel sinyal çakışmalarının çözümü eklenmedi. Gerçek telefonda hız kazanımı veya standart uyumu kanıtlandığı söylenmedi.

## Kontrollü saat koruması doğrulaması

- Yalnız özel gNB sürecindeki CLOCK_REALTIME okumalarına5 saniye sonra -2s uygulayan yardımcı kullanıldı. İşletim sistemi saati ve CLOCK_MONOTONIC değiştirilmedi.
- `clockstep2_korumasiz`:5.099.968 uyarı,931.631.974 bayt günlük,21 metrik satırının4’ünde sıfır trafik.
- `clockstep2_korumali`:26.967 uyarı,35.030.897 bayt günlük,22 satırda sıfır trafik yok; DL36/UL119 korundu. İlk koruma satırında tam4000 slot geri fark görüldü. Koruma2s beklerken26.965 kez uyarı üretmiştir; tamamen uyarısız olduğu söylenmedi.
- Bu iki koşu sentetik tanıdır; ana hız tablosuna veya referans ortalamasına katılmadı. İkisinin gerçek YAML log seviyesi info idi; ilk özet alanındaki warning bilgisi düzeltilip istenen ve gerçek seviye ayrı kaydedildi.
- İlk iki saat tanısında yeniden kullanılan ayar dosyası ortak log yoluna yazdığı için tanı geçersiz/superseded etiketlendi. Terminal kayıtları korundu, kalan korumalı log ayrı arşivlendi; Linux referans günlüğü değişmemiş Windows arşivinden geri yüklendi. Esas referans arşivi ve metrikleri korunmuştur. Sonraki denemelerde her koşuya ayrı log yolu zorunlu kılındı.

## Ölçüm ve kayıt yöntemi

- Koşular art arda çalıştırıldı; aynı anda birden fazla gNB ölçümü yapılmadı. Ana hız ölçümleri sırasında derleme veya belge görselleştirmesi çalıştırılmadı.
- En az5 metrik satırı varsa ilk ve son satır ortalamadan çıkarıldı; aradaki kayıplı satırlar seçilerek atılmadı. Tüm ham satırlar saklandı.
- `top` yüzde100 değeri bir çekirdek kullanımına karşılık gelir. Günlük düzeyleri farklı koşular arasında CPU sayıları optimizasyon kazancı olarak karşılaştırılmadı.
- Betikte `script -e` ile gerçek gNB çıkış kodu aktarıldı. `GNB_BIN` ile temel/model ikilileri seçilebilir hale getirildi.
- Ekran yakalama bağlantısı hata verdi ve gerçek ekran görüntüsü alınamadı. Rapor, terminalin kaydedilmiş gerçek satırlarını metin olarak içerir. Ekran görüntüsü taklidi üretilmedi.

## Klasör düzeni ve yeniden inceleme

- `Ham_Kayitlar/<koşu>/`: command.txt, base/config.yml, terminal.txt, typescript.txt, top.txt, metrics.csv, tam gnb.log.gz ve summary.json. `veri_genisligi100` PDSCH genişliği kanıtıdır.
- `tum_olcumler.json` ve `tum_olcumler.csv`: tanısal/geçersiz koşular dahil envanter; measurement_valid ve açıklama alanı okunmalıdır. Bu dosyanın bütün satırlarının ortalaması alınmamalıdır.
- `Kod_Degisiklikleri/03_tum_deney_degisiklikleri.patch`: uygulanan bütün OCUDU değişiklikleri; `04_deney_betikleri.patch`: yalnız deney projesindeki betik değişiklikleri.
- `Kod_Degisiklikleri/Son_Kaynaklar`: değişen dosyaların son kopyaları. `Derleme_Kayitlari`: gerçek yapılandırma/derleme çıktıları. `surum_kaydi.json`: sürümler ve kullanılan ikililerin SHA-256 özetleri.
- `Araclar`: ölçüm ve belge üretme araçları. Yeniden koşu aracı aynı etiketli mevcut kaydı ezmez. Eski çıktıları silmeden yeni etiket seçilmelidir.
- `Kaynaklar/Proje` ve `Kaynaklar/Standart`: özgün kaynak kopyaları. Standart yanıtı TS38.214§5.1.4/§5.1.6.5, TS38.331 RateMatchPattern ve TS38.212 DCI kanıtlarına dayandırıldı.

## Teslim denetimi

- Kısa PDF’nin3 sayfası ve son Word önizlemesinin8 sayfası görüntülenerek kontrol edildi. Türkçe karakter, tablo ve sayfa akışında taşma görülmedi.
- Paketli Word renderer günlükleri incelendi; paketli LibreOffice bulunmadığından dönüştürme yapılamadı. Alternatif olarak Word salt okunur açılıp PDF’ye aktarıldı, Poppler ile bütün sayfaları görüntülendi. Kaynak DOCX değiştirilmeden önizleme üretildi; son kod satırı açıklaması eklenen sürüm ayrıca tekrar dönüştürülüp denetlendi.
- Sonuç Excel’inin11 sekmesi görüntülendi. ZIP bütünlüğü,409 korunması gereken kaynak hücresi,54 özgün formül, ana DL/UL değerleri ve kayıp formülleri bağımsız kontrol edildi.36 radar hücresi boş bırakıldı; önbellek Excel hata değeri0 bulundu. Özgün dosyanın SHA-256 özeti değişmedi.
- Excel’in tarih hücreleri ölçüm kaynağındaki UTC başlangıç zamanını taşır; Türkiye saatine çevirmek için3 saat eklenir. Günlüklerde de UTC kullanıldı. Rapor tarihi Türkiye takvimine göre20 Kasım2026’dır.
- Kullanıcının son isteği üzerine ekran alıntısı yeniden denendi. Ekran Alıntısı Aracı erişilebilir görünse de doğrudan açılan CMD penceresi yakalama envanterinde görünmedi ve gerçek terminal görüntüsü alınamadı. Not Defteri görüntüsü kullanılmadı. Tablolu rapor korunarak tamamlandı; ekran görüntülü ikinci rapor oluşturulmadı. Gerçek terminal kayıtları kendi klasörlerinde mevcuttur.
- Önizleme ve bağımsız dosya kontrol kayıtları `Araclar/Rapor_QA`, `Araclar/Ozet_QA`, `Araclar/Excel_QA` altındadır. Son dosya özetleri `teslim_dosyasi_kontrolu.json` içindedir.
- Görev kartında Fatih için istenen dört teslim maddesinin ölçüm, kod ve standart bölümleri tamamlandı. Radar veya gerçek UE/PHY sonuçları üretilmedi.


## 20 Kasım 2026 - kullanıcının isteği üzerine yeniden doğrulama

- İlk23 ana koşunun509 ham metrik satırı bağımsız, başlıkları esas alan bir okuyucuyla CSV, JSON, Word, PDF ve Excel’e karşı kontrol edildi. Hesap/aktarım hatası bulunmadı. CPU örnekleri ve gerçek YAML parametreleri de doğrulandı.
- Aynı dondurulmuş ikililerin SHA-256 özetleri kontrol edildi; üç100MHz referansı, dört bant taraması, K1-K11 ve seçili beş RE/TBS koşusu olmak üzere23 yeni koşu art arda çalıştırıldı. Eski kayıtlar ezilmedi; yeni kayıtlar `Ham_Kayitlar/v2_*` altında saklandı. Sentetik saat yardımcısı kullanılmadı.
- Yeni23 koşunun506 ham satırı da bağımsız okuyucuyla kontrol edildi; CSV/özet bütünlük hatası0 bulundu. V2'nin eski raporla karşılaştırıldığı54 hücre/token farkı, aynı küçük yeniden ölçüm değişimlerinin farklı dosyalarda tekrar gösterilmesidir; ilk verinin aktarım hatası değildir.
- Hız çiftleri17/23 koşuda birebir aynı; hız/ok/nok alanlarının tamamı14/23 koşuda aynı bulundu. En büyük DL farkı0,15 Mbps, UL farkı0,263158 Mbps ve göreli hız farkı yaklaşık%0,417 oldu. Kayba uğrayan iç satırlar ortalamadan çıkarılmadı.
- Yeni referans ortalaması DL35,983333 / UL119 Mbps oldu; ilk üç referansın36/119 sonucu kendi kayıtlarıyla doğrulandı. Bunlar yuvarlatılmış konsol satırlarının ortalamalarıdır; alt-Mbps fiziksel ölçüm doğruluğu anlamına gelmez.
- Bazı yeni koşularda FAPI late/real-time ve geri saat koruma kayıtları bulundu. K9 tekrarUL118,75 Mbps verdi; No space in PDCCH sayısı yine0 olduğundan bu küçük fark PDCCH alanı yetersizliği kanıtı sayılmadı.
- 24. ek debug koşusunda (`v2_veri_genisligi100`) baskın PDSCH aralığı tekrar[0..48) bulundu; VRB eşlemesi non-interleaved olduğu için48 fiziksel PRB olarak doğrulandı. Bu ek koşu da36/119 Mbps verdi.
- RE giderleri432/1296/864/432/384 ve TBS değerleri3969 referans;3713/3072/3393/3713/3713 byte, standart formülüyle ve özgün C++ hesaplayıcısı çağrılmadan yeniden hesaplanıp gerçek günlüklerle eşleştirildi. Yeni beş model koşusunda da beklenen RE izleri ve TBS değerleri bulundu.
- Seçili on yeni önce/sonra günlüğünün altısında bazı tahsisler için nrtx>0 bulundu. Bu yeni hızlar metrik tekrarı olarak kaydedildi; yeniden iletimsiz ideal model kazancının doğrudan ölçümü sayılmadı. İlk raporun seçili10 koşusundaki nrtx=0 kanıtı korunmuştur. PHY rate matching veya gerçek UE doğrulaması yapılmış sayılmadı.
- K11 teorik hücresi Word’de kaynak önbelleği boş olduğundan'-', sonuç Excel’inde yeniden hesaplandığından%16,67 gösterilmektedir. Bu sunum farkı doğrulama raporunda açıklandı; ölçülmüş29/119 değerleri çelişmemektedir.
- Beğenilen tablolu Word, kısa teslim PDF’si ve sonuç Excel’inin dosya özetleri kontrol edilerek değişmediği doğrulandı. Kanıt `Dogrulama/onceki_raporlar_korundu.json` içindedir.
- Yeni3 sayfalık `Fatih_Gorev_Karti_4_Dogrulama_Raporu.pdf` hazırlandı; bütün sayfaları görüntülenerek kontrol edildi. Tam denetim dosyaları `Araclar/Dogrulama_QA` ve `Dogrulama` altındadır.
- Gerçek terminal SS’leri için `Araclar/OCUDU_SS_icin_Ac.cmd` ve `Ekran_Goruntusu_Alma.txt` hazırlandı. Menü1-5 gerçek yeni koşuları yapıp sonuçları kullanıcı SS alana kadar bekletir;12 tamamlanan23 tekrarın açıkça etiketlenmiş arşiv özetini gösterir. Menü12 ve çıkış gerçek Ubuntu ortamında denendi; yeni gNB başlatılmadı.
- Kullanıcının göndereceği gerçek ekran görüntüleri geldikten sonra ayrı SS’li rapora eklenecektir. Tablolu rapor korunmaktadır. Henüz ekran görüntüsü veya SS’li rapor varmış gibi gösterilmedi.


## 20 Kasım 2026 - gerçek ekran görüntüleriyle ayrı rapor

- Kullanıcının gönderdiği altı terminal görüntüsü alındı; orijinal kopyaları `Ekran_Goruntuleri/Orijinaller` altında saklandı. Kaynak görüntülerin pikselleri ve ölçüm yazıları değiştirilmedi.
- Menü, önceki koşuya ait üst satırlar, ekran alıntısı alma talimatları ve boş kenarlar rapordaki görünür alandan kırpıldı. Koşul/koşu kimliği, DL-UL başlıkları, sekiz metrik satırı ve sonuç/ok satırları korundu.
- Beş yeni koşunun113 ham metrik satırı kontrol edildi. REF36/119;K1önce29/119,sonra35/119;K6önce29/119,sonra34/119 Mbps sonuçları görüntüler ve kayıtlarla eşleşti. Arşiv görüntüsünün23 satırı da doğrulama JSON’u ile eşleşti.
- Arşiv fotoğrafı ayrı ve yeni canlı koşu gibi sunulmadı; görüntüdeki arşiv açıklaması korundu.
- Ayrı6 sayfalık `Fatih_Gorev_Karti_4_Ekran_Goruntulu_Rapor.docx` ve aynı içerikli PDF hazırlandı. Önceki örnekteki açıklama-görüntü-sonuç akışı kullanıldı; K1 ve K6 önce/sonra görüntüleri kendi sayfalarında birlikte yerleştirildi. Siyah Times New Roman düzeni ve edilgen anlatım korundu.
- Altı görüntü raporda birer kez kullanıldı; okunabilirlik için6,5inç gövde genişliğine sığdırıldı. Tablolu rapor ve önceki Görev2 dosyası değiştirilmedi. Kaynak stilleri ve sayfa düzeni korundu; eski belgelerin dosya özetleri doğrulandı.
- Paketli renderer LibreOffice bulunmadığı için çalışmadı; hata kaydı saklandı. Word salt okunur PDF aktarımı ve Poppler ile bütün son6 sayfa görüntülenerek kontrol edildi. Sağ veri sütunları, altok satırları ve23 arşiv satırında kırpılma/taşma bulunmadı.
- Kontrol kayıtları, kırpma sınırları, kaynak görüntü özetleri ve bağımsız veri denetimi `Araclar/SS_Rapor_QA` içindedir. Bu aşamada yeni gNB ölçümü başlatılmadı.


## Son düzenleme - özgün rapor metni ve görev kartı kapsamı

- Kullanıcının isteğiyle SS’li rapordaki ayrı doğrulama/tekrar anlatımı, kontrollü saat regresyonu ve23koşuluk arşiv görüntüsü çıkarıldı. Ham kayıt ve kontrol belgeleri arşivden silinmedi.
- Beğenilen `Fatih_Gorev_Karti_4_Rapor.docx` doğrudan kaynak alındı. Sekiz ana bölüm sırası ve66 açıklama/komut paragrafı kelimesi kelimesine korundu; yalnız görsellere uygunluk veya doğru kayıt kapsamı için8 paragrafta küçük uyarlama yapıldı. Kaynak tabloların bütün gerekli sayıları metne taşındı;5 gerçek terminal görüntüsü kaldı.
- K1/K6 dışındaki koşulların verileri, bant taraması, üç referans/CPU değerleri, beş model koşulunun önce/sonra sonuçları, kod satırları ve standart cevabı korunarak görev kapsamının eksilmesi önlendi.
- Görev kartındaki literal hata/uyarı şartı için gerçek100MHz late günlük satırı ve40MHz fatal satırları eklendi. Bunlar kayıt dosyalarından aynen alındı.
- Son SS raporu9 sayfa oldu. Word ve PDF eşitlendi; bütün9 sayfa görüntülendi. Komutların sayfalar arasında bölünmesi düzeltildi. Beğenilen tablolu rapor,3sayfalık özet ve doldurulmuş Excel değiştirilmedi.
- Kapsam incelemesi yalnız Fatih’e ait OCUDU Görev4 bölümü içindir. Dört teslim maddesi rapor+özet tarafından cevaplanıyor. Ortak dosyanın doldurulması şartını da fiilen teslim etmek için `ortak_degerler_Fatih_sonuclar.xlsx` rapor ve özetle birlikte gönderilmelidir. Kod yamaları/derleme kayıtları ve ham günlükler ek kanıt olarak hazırdır.
- Eksik zorunlu deney veya cevap bulunmadı. Gerçek PHY rate matching/standart UE desteği uygulanmamış olması kartın istediği basit scheduler/TBS deneyinin yapılmadığı anlamına gelmez; bu sınır raporda açıkça korunmuştur. Diğer ekip üyelerinin görevlerinin tamamlandığı iddia edilmedi.
- Son değerlendirme `Araclar/SS_Rapor_QA/coverage_audit_final.json`, metin karşılaştırması `aligned/prose_preservation.json`, görsel kontroller `aligned/final` altındadır. Eski6sayfalık SS düzeni yalnız geri dönüş için `onceki_duzen` altında saklandı.

## 23.11.2026 - GitHub ve saat düzeltmesinin yeri

- EHB415 ders deposunun origin adresi https://github.com/tahaberkayalma26-creator/EHB415.git olarak kontrol edildi. Bu aşamada commit veya push yapılmadı; mevcut yerel değişikliklere dokunulmadı.
- Saatin 2 ms elle ileri alınmadığı kaynak koddan doğrulandı. Dummy RU run_slot fonksiyonuna geri saat okumasında slot ilerletmeyi durduran kontrol eklendiği; beklemenin her turda 10 mikrosaniye olduğu belirlendi.
- 100 MHz sıfır veri sorunu için gereken ayrı ConRes/slice scheduler bildirimi de ayırt edildi. Saat korumasının tek başına yeterli olduğu iddia edilmedi.
- Taha_100MHz_Duzeltmeleri klasörü ve ZIP paketi hazırlandı. İki yama, ilgili son .cpp kaynak kopyaları, fonksiyon/satır yerleri ve uygulama açıklaması eklendi. Test yardımcısının +2 ms değil, sürece özel -2 saniye okuma sapması oluşturduğu açıklamada belirtildi.
- Yeni gNB koşusu veya derleme yapılmadı. Raporlar, ham ölçümler ve mevcut Git değişiklikleri korundu.

## 23.11.2026 - GitHub Fatih klasörü için yayın hazırlığı

- Kullanıcının açık isteğiyle Taha'nın EHB415 deposunda Fatih klasörüne yayın yapılması için temiz, güncel bir depo kopyası hazırlandı. Önceki Windows ders deposundaki değişiklikler ve kişisel notebook değiştirilmedi.
- İlk kurulum raporu, Görev 2 teslimleri ve deney projesi; Görev 4 raporlarının iki sunumu, özet, doldurulmuş Excel, altı terminal ekran görüntüsü, kod değişiklikleri, ölçümler ve bütün mevcut ham deney kayıtları birlikte hazırlandı.
- Tam makale/standart PDF kopyaları, okuma çevirileri, önbellek ve eski QA sayfa görüntüleri eklenmedi. OCUDU kaynaklarının mevcut lisans ve atıf metinleri korundu ve ayrı dosya olarak eklendi.
- Kopyalar kaynak dosyalarla SHA-256 üzerinden karşılaştırıldı. Yükleme klasöründe 100 MiB üstünde dosya bulunmadı. Rapor PDF/Office metinlerinde öğrenci numarası alanı bulunmadı. Anahtar/parola değeri herhangi bir çıktı veya dosyaya yazılmadı.
- README içinde rapor/görsel bağlantıları, kaynak sürümler ve saat koruması/ConRes düzeltmesinin ayrı açıklamaları eklendi. Kök .gitignore yüzünden özgün teslim raporlarının dışarıda kalmaması için yalnız Fatih klasörüne özgü kurallar eklendi.
- Gönderim için GitHub cihaz onayı tamamlandı; hesabın hedef depoya yazma yetkisi doğrulandı. Gönderim sonucu ve commit bilgisi ayrıca kaydedilecektir.

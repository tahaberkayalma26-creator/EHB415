# 00: Genel Bakış

## Proje ne kullanıyor?

Proje, 5G ağlarında entegre sensing ve haberleşme (ISAC) fonksiyonlarının etkisini incelemek için üç araç ailesi kullanır:

| Araç | Ne işe yarar | Proje içindeki rolü |
|---|---|---|
| **Sionna** (+ Sionna RT) | Fiziksel katman ve kanal simülasyonu, ray tracing (TensorFlow tabanlı Python kütüphanesi) | OFDM radar/sensing sinyal işleme, kanal modelleme |
| **ns-3 + 5G-LENA** | Uçtan uca 5G NR ağ simülatörü (C++) | Ağ seviyesinde throughput, gecikme, paket kaybı, scheduler etkisi |
| **OCUDU** | Açık kaynak 5G CU/DU yazılımı (srsRAN'ın devamı, C++) | Gerçek bir gNB kod tabanı: mimari analiz, entegrasyon noktası, prototip |

## Neyin nerede çalıştığı

```
Windows 11
├── Git, VS Code                      (Windows'ta)
├── Python 3.10 + Sionna + Sionna RT  (Windows'ta, yerel sanal ortam)
├── LLVM                              (Windows'ta, Sionna RT için)
└── WSL2 (Ubuntu 24.04)
    ├── ns-3.48 + 5G-LENA v5.1        (Ubuntu içinde)
    └── OCUDU 26.10                   (Ubuntu içinde)
```

**Neden WSL2?** ns-3 ve 5G-LENA Linux/macOS için hazırlanır (5G-LENA dokümanı yalnızca Ubuntu ve macOS komutlarını verir).
OCUDU resmi dokümanında "gerçek zamanlı çekirdek desteği olan Linux" ister. Sionna ise bir Python kütüphanesidir ve Windows'ta yerel çalışır.

## Doğrulanmış sürümler

| Bileşen | Sürüm | Not |
|---|---|---|
| Windows | 11 Home, 10.0.26200 | Pro/Education da çalışır |
| WSL | 3.0.3 paketi, WSL2 | |
| Ubuntu | 24.04.5 LTS | |
| Python (Windows) | 3.10.11 | 3.10–3.12 uygundur |
| Sionna / sionna-rt | 1.2.2 | |
| TensorFlow / Keras | 2.21.0 / 3.12.4 | Yerel Windows'ta yalnızca CPU |
| Mitsuba / Dr.Jit | 3.8.0 / 1.3.1 | Sionna RT bağımlılığı |
| LLVM | 23.1.3 | Sionna RT'nin CPU modu için |
| ns-3 | **3.48** | 5G-LENA v5.1 bu sürümle uyumlu |
| 5G-LENA (nr) | **v5.1** (2026-08-06) | `contrib/nr` altında |
| OCUDU | **release_26_10** (26.10.0) | |
| Ubuntu içinde: g++ / clang / cmake / ninja | 13.3.0 / 18.1.3 / 3.28.3 / 1.11.1 | |

> **Uyarı:** ns-3 sürümünü 5G-LENA sürümüyle eşleştirmezseniz derleme kırılır. 5G-LENA v5.1 ile ns-3.49 kullanmayın.

## Donanım gereksinimleri

| Kaynak | Asgari | Bu makinede |
|---|---|---|
| RAM | 16 GB (WSL'e 10 GB ayrılır) | 15,7 GB |
| İşlemci | 8 mantıksal çekirdek önerilir | 12 çekirdek (i5-1240P) |
| Boş disk (C:) | **40 GB** | 97 GB (genişletme sonrası) |
| GPU | Gerekmez (CPU çalışır) | NVIDIA yok |
| BIOS | Intel VT-x / AMD-V açık | Açık |

Disk kullanımı (ölçülen): Sionna sanal ortamı ≈ 2,1 GB, LLVM ≈ 2-3 GB, ns-3 + 5G-LENA ≈ 0,5 GB, OCUDU ≈ 0,6 GB, Ubuntu kök disk ≈ 4 GB.
WSL sanal diski büyüdükçe C: üzerinden yer alır. Boş alanın az olduğu makinelerde önce [06-disk-genisletme.md](06-disk-genisletme.md) okunmalı.

## GPU hakkında

Yerel Windows'ta TensorFlow 2.11 ve sonrası GPU desteklemez, bu yüzden Sionna CPU'da çalışır. Bu proje için yeterlidir
(radar işleme ve küçük sahnelerde ray tracing denendi). NVIDIA GPU'su olan ekip üyesi isterse WSL2 içinde GPU yolunu kendi
başına deneyebilir; bu rehber bunu **kapsamaz ve doğrulamaz**.

## Kaynak doğrulama notu

Sürüm etiketlerinin varlığı (`v5.1`, `ns-3.48`, `release_26_10`) `git ls-remote` ile, PyPI'daki Sionna sürümü `pip index versions` ile,
ns-3 ve OCUDU gereksinimleri resmi dokümanlardan (`nsnam.org`, `docs.ocudu.org`, 5G-LENA README) kontrol edildi.

# 05: OCUDU 26.10 (WSL2 / Ubuntu içinde)

> **Doğrulama durumu (2026-10-14):**
> - **Doğrulandı:** bağımlılık kurulumu, kaynak indirme, Clang 18.1.3 ile derleme (ZeroMQ açık), `gnb` ikilisinin oluşması ve
>   `./apps/gnb/gnb --version` çıktısı: `OCUDU 5G gNB version 26.10.0 (e0db566)`.
> - **Doğrulanmadı:** `testmode` yük testi (6. adım) ve srsUE + Open5GS ile uçtan uca test (7. adım). Bu adımlar resmi dokümandan aktarıldı, bu makinede **çalıştırılmadı**.
>   Yani gNB'nin bir hücreyi gerçekten ayağa kaldırdığı henüz gösterilmedi.

**Ön koşul:** [02-wsl2-ubuntu.md](02-wsl2-ubuntu.md) tamamlanmış olmalı. Komutlar Ubuntu terminalinde çalışır.

**OCUDU nedir?** srsRAN Project'in devamı, Linux Foundation altındaki açık kaynak 5G CU/DU yazılımı.
Kaynak: `https://gitlab.com/ocudu/ocudu`. Resmi dokümantasyon: `https://docs.ocudu.org/`.

## Derleyici hakkında

Resmi kurulum sayfası derleyici olarak **gcc ≥ 15.2 veya Clang ≥ 14** önerir. Ubuntu 24.04'ün gcc'si 13.3'tür, bu yüzden **Clang 18** kullanıldı.
Clang ile derleme bu makinede başarılı oldu. gcc 13 ile denenmedi.

## Yol A: Otomatik (önerilen)

```bash
bash /mnt/c/Users/<kullanici>/Desktop/EHB415/kurulum/wsl_ocudu_kur.sh 2>&1 | tee ~/ehb415_ocudu.log
```

Başarı kriteri: çıktıda `=== OCUDU BUILD OK ===` ve `OCUDU 5G gNB version 26.10.0` satırları.

## Yol B: Adım adım

### 1. Bağımlılıklar

```bash
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    cmake make gcc g++ clang pkg-config \
    libmbedtls-dev libsctp-dev libyaml-cpp-dev libgtest-dev \
    libfftw3-dev libeigen3-dev libzmq3-dev ccache
```

| Paket | Neden |
|---|---|
| `clang`, `cmake`, `make` | Derleme |
| `libmbedtls-dev`, `libsctp-dev`, `libyaml-cpp-dev` | OCUDU'nun zorunlu bağımlılıkları (mbedTLS, SCTP, yaml-cpp) |
| `libfftw3-dev` | FFT kütüphanesi (fftw / oneMKL / AOCL'den biri zorunlu) |
| `libeigen3-dev` | Yalnızca DOA (varış açısı) kestirimi için, isteğe bağlı |
| `libzmq3-dev` | **ZeroMQ**: gerçek radyo (USRP) olmadan sanal RF için |
| `libgtest-dev` | Yalnızca testleri derlemek için |

### 2. Kaynak kodu indir

```bash
mkdir -p ~/ehb415 && cd ~/ehb415
git clone --depth 1 --branch release_26_10 https://gitlab.com/ocudu/ocudu.git
```

`release_26_10` en güncel etikettir (2026-10-14). Daha eski: `release_26_04`.

### 3. Derle (ZMQ açık, Clang)

```bash
cd ~/ehb415/ocudu
mkdir -p build && cd build
CC=clang CXX=clang++ cmake ../ -DENABLE_EXPORT=ON -DENABLE_ZEROMQ=ON \
    -DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache
make -j4 gnb
```

- `-DENABLE_ZEROMQ=ON -DENABLE_EXPORT=ON`: ZMQ varsayılan olarak kapalıdır. CMake çıktısında şu satırları görmelisin:
  `-- The CXX compiler identification is Clang 18.1.3` ve `-- Found libZEROMQ: /usr/lib/x86_64-linux-gnu/libzmq.so`.
  Görmezsen `libzmq3-dev` kurulumunu kontrol et, `build` klasörünü silip tekrar `cmake` çalıştır.
- `make -j4 gnb`: yalnızca gNB uygulamasını derler (tüm testleri değil), süre ve disk tasarrufu. `-j4`, 10 GB WSL belleğinde güvenlidir.
- Derleme sırasında dosya adlarında geçen "error" kelimeleri (`..._error_handler_impl.cpp`) hata değildir.
- Süre: bu makinede (i5-1240P, `-j4`) paket kurulumu + klonlama + derleme toplam **yaklaşık 23 dakika** sürdü. Daha zayıf makinede 40–60 dakika bekle.
- İlerleme yüzde olarak gösterilir (`[ 92%] Building CXX object ...`). Son yüzdeler bağlama (link) aşamasıdır.

### 4. Doğrulama

```bash
ls -la ~/ehb415/ocudu/build/apps/gnb/gnb
~/ehb415/ocudu/build/apps/gnb/gnb --version
```

Beklenen (bu makinede):

```
-rwxr-xr-x 1 ehb ehb 51501384 ... apps/gnb/gnb

--== OCUDU gNB (commit e0db566) ==--

OCUDU 5G gNB version 26.10.0 (e0db566)
```

## Disk ve bellek (ölçülen)

`~/ehb415/ocudu` yaklaşık **0,6 GB** (kaynak + yalnızca `gnb` derlemesi).

## 5. Kod ağacına bakış

Depoda kullanıma hazır yapılandırma dosyaları var: `~/ehb415/ocudu/configs/` (örn. `cell_cfg_mid_band_capacity_layer.yml`,
`cell_cfg_max_32_ues.yml`, `cu.yml`, `cu_cp.yml`, `cu_up.yml`, `amf.yml`). Docker tabanlı Open5GS çekirdek ağı ve izleme araçları: `~/ehb415/ocudu/docker/`.

Mimari dokümantasyonu: `https://docs.ocudu.org/dev_guide/codebase_guide/` ve `.../dev_guide/architecture_guide/`.

## 6. [Doğrulanmadı] Radyosuz yük testi (`testmode`)

Resmi doküman: `https://docs.ocudu.org/tutorials/testmode/`. gNB'yi radyo ve çekirdek ağ olmadan çalıştırmak için yapılandırma dosyasında
`ru_dummy` ve `no_core` seçeneklerini kullanır ve `testmode` ile UE trafiği taklit eder. Bu, derlemenin ve gNB'nin çalıştığını gösteren
en az bağımlılıklı testtir. **Bu makinede henüz yapılmadı;** ilk deneyen kişi sonucu bu dokümana eklesin.

## 7. [Doğrulanmadı] srsUE + Open5GS ile uçtan uca (ZMQ)

Resmi doküman: `https://docs.ocudu.org/tutorials/srsue/`. Open5GS çekirdek ağı (OCUDU'nun `docker/` klasöründe Docker'lı sürümü var),
srsRAN 4G'den srsUE ve ZMQ gerekir. Doküman şunları belirtir:
- srsUE'nin 5G desteği artık aktif geliştirilmiyor, yalnızca kavram kanıtı içindir.
- SCS 15 kHz ile sınırlı (yalnızca FDD bantları), bant genişliği 5/10/15/20 MHz.

Docker için Windows'ta **Docker Desktop (WSL2 backend)** gerekir; bu ayrı bir kurulumdur ve disk yer kaplar. **Bu makinede kurulmadı.**

## Sınırlamalar

- WSL2'nin çekirdeği gerçek zamanlı (real-time) değildir. OCUDU dokümanı gerçek zamanlı çekirdek önerir. Radyosuz (ZMQ / testmode) çalışmalar için sorun beklenmez, ama **gerçek radyo (USRP) bağlantısı WSL2'de desteklenmez** ve bu proje için gerekmez.
- Bu makinede yalnızca `gnb` derlendi. Test paketi (`-DBUILD_TESTING=On`) derlenmedi.

## Sorun giderme

Bkz. [07-sorun-giderme.md](07-sorun-giderme.md).

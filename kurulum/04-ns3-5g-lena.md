# 04: ns-3.48 + 5G-LENA v5.1 (WSL2 / Ubuntu içinde)

> **Doğrulama durumu:** Bu dokümandaki adımlar bu makinede (WSL2, Ubuntu 24.04.5, WSL'e 10 GB bellek, `-j6`) baştan sona çalıştırıldı.
> Derleme 1876 hedefle hatasız bitti ve `cttc-nr-demo` çalıştı. Otomatik betik: `wsl_ns3_kur.sh`.

**Ön koşul:** [02-wsl2-ubuntu.md](02-wsl2-ubuntu.md) tamamlanmış olmalı. Tüm komutlar **Ubuntu terminalinde** çalışır
(Başlat → Ubuntu 24.04, ya da PowerShell'de `wsl`).

## Sürümler (birbirine kilitli)

- **ns-3: 3.48**, **5G-LENA (nr modülü): v5.1**. 5G-LENA her sürüm için önerilen ns-3 sürümünü belirtir; v5.1 → ns-3.48.
  ns-3.49 gibi başka bir sürümle derlemeyi denemeyin.

## Yol A: Otomatik (önerilen)

Windows'ta bu klasörde olan `wsl_ns3_kur.sh` betiğini Ubuntu içinden çalıştır:

```bash
bash /mnt/c/Users/<kullanici>/Desktop/EHB415/kurulum/wsl_ns3_kur.sh 2>&1 | tee ~/ehb415_ns3.log
```

(Yolu kendi Windows kullanıcı adına göre düzelt.) Betik aşağıdaki 1–4. adımları sırayla yapar ve sonunda demo'yu çalıştırır.
Başarı kriteri: çıktıda `=== NS3 BUILD OK ===` ve `=== NS3 DEMO OK ===` satırları.

## Yol B: Adım adım

### 1. Bağımlılıklar

```bash
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential g++ python3 python3-venv python3-pip cmake ninja-build git ccache pkg-config \
    libc6-dev sqlite3 libsqlite3-dev libeigen3-dev
```

| Paket | Neden |
|---|---|
| `g++`, `build-essential` | ns-3 için C++ derleyici (g++ ≥ 11.1 gerekir; Ubuntu 24.04'te 13.3) |
| `cmake`, `ninja-build` | Derleme sistemi |
| `python3` | ns-3'ün `./ns3` aracı (≥ 3.10; Ubuntu 24.04'te 3.12) |
| `libc6-dev` | 5G-LENA için (`semaphore.h`) |
| `sqlite3`, `libsqlite3-dev` | 5G-LENA'nın kalibrasyon örnekleri (isteğe bağlı özellikler) |
| `libeigen3-dev` | 5G-LENA'nın MIMO özellikleri |
| `ccache` | Yeniden derlemeyi hızlandırır |

### 2. ns-3'ü indir

```bash
mkdir -p ~/ehb415 && cd ~/ehb415
git clone --depth 1 --branch ns-3.48 https://gitlab.com/nsnam/ns-3-dev.git
```

`--depth 1` yalnızca o etiketin dosyalarını indirir (hızlıdır, geçmiş yok). Geçmişi de istersen `--depth 1` olmadan klonlayıp `git checkout ns-3.48` yap.

### 3. 5G-LENA'yı `contrib` altına koy

```bash
git clone --depth 1 --branch v5.1 https://gitlab.com/cttc-lena/nr.git ns-3-dev/contrib/nr
```

Klasör adı **`nr`** olmalı ve `ns-3-dev/contrib/` altında durmalı.

### 4. Yapılandır ve derle

```bash
cd ~/ehb415/ns-3-dev
./ns3 configure --enable-examples -d optimized -G Ninja
./ns3 build -j6
```

- `--enable-examples`: 5G-LENA'nın örneklerini (cttc-nr-demo gibi) derler.
- `-d optimized`: optimizasyonlu derleme; simülasyonlar çok daha hızlı koşar. Hata ayıklamak için `-d debug` kullan.
- `-G Ninja`: Ninja ile derler (Make'ten hızlıdır).
- `-j6`: 6 paralel iş. 10 GB WSL belleğinde güvenli. "Killed" hatası alırsan `-j4` veya `-j2` dene.
- Süre: bu makinede (i5-1240P, `-j6`) paket kurulumu + klonlama + derleme toplam **yaklaşık 18 dakika** sürdü (1876 hedef). Daha zayıf makinede 30–60 dakika beklemelisin. İlerleme `[1514/1876]` biçiminde gösterilir.
- Yapılandırma çıktısında **"Modules configured to be built"** listesini ve ardından **"Finished executing the following commands"** mesajını gör.
  Hem yapılandırmadan hem derlemeden sonra bu mesaj çıkar. Hata varsa [07-sorun-giderme.md](07-sorun-giderme.md)'ye bak.

### 5. Doğrulama

```bash
cd ~/ehb415/ns-3-dev
./ns3 run cttc-nr-demo
```

Beklenen çıktının sonu (bu makinede gerçek çıktı):

```
Flow 1 (1.0.0.2:49153 -> 7.0.0.2:1234) proto UDP
  Tx Packets: 6000
  TxOffered:  10.240000 Mbps
  Throughput: 10.236587 Mbps
  Mean delay:  0.276044 ms
  Mean jitter:  0.030032 ms
  Rx Packets: 5998
Flow 2 (1.0.0.2:49154 -> 7.0.0.3:1235) proto UDP
  Tx Packets: 6000
  TxOffered:  102.400000 Mbps
  Throughput: 102.229333 Mbps
  Mean delay:  0.900967 ms
  Mean jitter:  0.119907 ms
  Rx Packets: 5990

  Mean flow throughput: 56.232960
  Mean flow delay: 0.588505
```

İki akışın throughput değerlerinin gönderilen değerlere yakın (10,2 ve 102,2 Mbps) ve gecikmenin milisaniyenin altında olması simülatörün sağlıklı çalıştığını gösterir.

## Örnekler ve devam

5G-LENA örnekleri: `~/ehb415/ns-3-dev/contrib/nr/examples/` (örn. `cttc-3gpp-channel-simple-ran.cc`, `cttc-error-model.cc`,
`cttc-channel-randomness.cc`). Bir örneği çalıştırmak için dosya adından `.cc` uzantısını at: `./ns3 run cttc-error-model`.

Kodu VS Code ile açmak için: `cd ~/ehb415/ns-3-dev && code .` (Remote - WSL eklentisi kurulu olmalı).

## Disk ve bellek (ölçülen)

- `~/ehb415/ns-3-dev` yaklaşık **0,5 GB** (kaynak + optimized derleme).
- Derleme sırasında 6 `cc1plus` süreci her biri ≈ 0,7 GB bellek kullandı; toplam kullanım ≈ 4 GB.

## 5G-LENA'ya özel not (FDD)

5G-LENA v5.0 duyurusu, 3GPP spektrum modelinde **FDD** kullanıcıları için bir hata düzeltmesinin ns-3 tarafında olduğunu belirtir
(NLOS'ta alıcı gücünün 30 dB'ye kadar düşük çıkabilmesi, ns-3 merge request MR2929). TDD etkilenmez. Senaryolarımız FDD kullanırsa bu yama uygulanmalıdır.

## Sonraki adım (isteğe bağlı): SioLENA

Sionna RT ile üretilen ray-tracing kanalını ns-3'e besleyen modül: `github.com/usnistgov/siolena`
(Sionna'dan CSV üreten araç: `github.com/wineslab/sionna-channel-generator`). Bu **kurulmadı ve denenmedi**; temel kurulum çalıştıktan sonra denenmeli.

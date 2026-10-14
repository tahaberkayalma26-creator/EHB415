# 02: WSL2 + Ubuntu 24.04

> **Doğrulama durumu:** Aşağıdaki akış bu makinede baştan sona yapıldı (yönetici kurulumu → gerçek yeniden başlatma → Ubuntu kurulumu →
> kullanıcı oluşturma → paket kurulumu). Tek fark: Ubuntu'nun ilk açılışındaki kullanıcı/parola sorusu burada komutla atlandı (bkz. 5. adım).
> Etkileşimli ilk açılış (4. adım) bu makinede **denenmedi**, standart Microsoft akışıdır.

**Gereksinimler:** Windows 11, BIOS'ta sanallaştırma (Intel VT-x / AMD-V) açık, en az 40 GB boş disk, yönetici yetkisi.

## 1. Ön kontrol

PowerShell'de:

```powershell
(Get-CimInstance Win32_ComputerSystem).HypervisorPresent
[math]::Round((Get-PSDrive C).Free / 1GB, 1)
```

- İlk komut `True` olmalı. `False` ise BIOS/UEFI'ye girip **Intel Virtualization Technology (VT-x)** veya AMD **SVM Mode**'u aç.
- İkinci komut 40'tan büyük olmalı. Değilse önce [06-disk-genisletme.md](06-disk-genisletme.md) oku.

> Not: `VirtualizationFirmwareEnabled` değeri `False` görünebilir; bu, Windows'un hypervisor'ı zaten çalıştırdığı makinelerde normaldir (bu makinede de öyleydi ve WSL2 çalıştı). Karar kriteri `HypervisorPresent`.

## 2. WSL2'yi kur (yönetici PowerShell)

1. Başlat menüsünde "PowerShell" yaz, **Yönetici olarak çalıştır**'ı seç.
2. Bu klasöre git ve betiği çalıştır:

```powershell
cd C:\...\EHB415\kurulum
Set-ExecutionPolicy -Scope Process Bypass -Force
.\kur-wsl.ps1
```

Betik: boş disk alanını yazar (40 GB altındaysa uyarır), sonra `wsl --install -d Ubuntu-24.04` ve `wsl --set-default-version 2` çalıştırır.
Beklenen çıktı (bu makinedeki gerçek çıktı):

```
Installing: Windows Subsystem for Linux 3.0.3
Windows Subsystem for Linux 3.0.3 has been installed.
Installing Windows optional component: VirtualMachinePlatform
...
The requested operation is successful. Changes will not be effective until the system is rebooted.
```

Betiğin kendi logu `kur-wsl.log` dosyasına yazılır.

Betiği kullanmadan doğrudan çalıştırmak istersen (yönetici PowerShell):

```powershell
wsl --install -d Ubuntu-24.04
```

## 3. Gerçek yeniden başlatma yap (**atlama**)

**Başlat → Güç → Yeniden başlat**. "Kapat" ile kapatıp açmak **yetmez**: Windows'ta "Hızlı Başlatma" (Fast Startup) açıkken kapat-aç tam bir açılış yapmaz,
sanal makine bileşenleri devreye girmez. Bu makinede tam olarak bu yaşandı: ilk denemede `wsl --status` şu hatayı verdi:

```
WSL2 is unable to start since virtualization is not enabled on this machine.
```

Gerçek yeniden başlatmadan sonra hata kayboldu. Kontrol (yeniden başlatma sonrası):

```powershell
(Get-CimInstance Win32_OperatingSystem).LastBootUpTime     # az önceki bir saat olmalı
Test-Path C:\Windows\System32\vmcompute.exe                # True olmalı
```

## 4. Ubuntu'yu kur ve ilk açılışı yap (yönetici gerekmez)

Betik Ubuntu'yu kurmadıysa ya da kurulum yarım kaldıysa:

```powershell
wsl --install -d Ubuntu-24.04
```

Kurulum bitince Başlat menüsünden **Ubuntu 24.04**'ü aç. İlk açılışta bir kullanıcı adı ve parola ister; küçük harfli, boşluksuz bir kullanıcı adı seç (örn. `ehb`) ve bir parola belirle. Parolayı unutma, `sudo` için gerekir.

## 5. Alternatif: etkileşimsiz kullanıcı oluşturma (bu makinede kullanılan yol)

Bu makinede otomasyon için şu yol kullanıldı. **Parolasız sudo** verir, paylaşılan veya hassas bir makinede kullanma.

```powershell
wsl --install -d Ubuntu-24.04 --no-launch
```

Sonra Ubuntu içinde root olarak (bir betik dosyası üzerinden) şunlar çalıştırıldı:

```bash
useradd -m -s /bin/bash -G sudo ehb
echo 'ehb ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/ehb && chmod 440 /etc/sudoers.d/ehb
printf '[user]\ndefault=ehb\n' > /etc/wsl.conf
```

ve `wsl --shutdown` ile Ubuntu yeniden başlatıldı. Bu durumda `wsl -d Ubuntu-24.04 -- whoami` çıktısı `ehb` olur.

## 6. Doğrulama

```powershell
wsl -l -v
```

Beklenen:

```
  NAME            STATE     VERSION
* Ubuntu-24.04    Running   2
```

Ubuntu terminalinde:

```bash
lsb_release -ds     # Ubuntu 24.04.x LTS
whoami              # kendi kullanıcı adın
nproc; free -g      # çekirdek sayısı ve bellek
```

## 7. Bellek ve işlemci ayarı (`.wslconfig`)

WSL varsayılan olarak RAM'in yarısını kullanır. Derlemeler sırasında bellek yetmezse işlem "Killed" ile ölür. `C:\Users\<kullanici>\.wslconfig` dosyasını oluştur:

```ini
[wsl2]
memory=10GB
processors=8
```

16 GB RAM'li makinede bu değerler güvenlidir (bu makinede kullanıldı). Değişiklik için:

```powershell
wsl --shutdown
```

komutunu çalıştırıp Ubuntu'yu yeniden aç. Kontrol: `free -m` yaklaşık 9,9 GB toplam gösterir.

## 8. Dosyalar nerede durmalı?

- Projeleri **Ubuntu dosya sisteminde** tut: `~/ehb415/`. `/mnt/c/...` altında derleme ve dosya erişimi çok yavaştır.
- Windows'tan erişmek için Dosya Gezgini adres çubuğuna `\\wsl$\Ubuntu-24.04\home\<kullanici>\ehb415` yaz.
- Ubuntu'dan Windows dosyalarına erişim: `/mnt/c/Users/<kullanici>/...`

## 9. Ubuntu'da temel araçlar

Sonraki dokümanlardaki betikler gereken paketleri kendileri kurar. Elle kurmak istersen:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential git cmake ninja-build ccache python3 python3-venv python3-pip pkg-config
```

## Sorun giderme

Bkz. [07-sorun-giderme.md](07-sorun-giderme.md): "WSL2 is unable to start since virtualization is not enabled", disk dolması, derleme sırasında "Killed".

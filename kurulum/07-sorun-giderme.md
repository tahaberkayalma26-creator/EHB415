# 07: Sorun Giderme

Bu listedeki her madde bu makinede **gerçekten yaşanmış** bir sorundur, çözümü de denenmiştir.
Eksik bir şey bulursan hatanın tam metniyle birlikte buraya ekleyin.

## WSL2

### `WSL2 is unable to start since virtualization is not enabled on this machine`
`wsl --status` veya `wsl -l -v` bu hatayı veriyorsa ve WSL az önce kurulduysa: **gerçek yeniden başlatma yapılmamıştır.**
- Windows'ta Hızlı Başlatma açıkken **Kapat → aç** tam açılış yapmaz. **Başlat → Güç → Yeniden başlat** kullan.
- Kontrol: `(Get-CimInstance Win32_OperatingSystem).LastBootUpTime` az önceki bir saat göstermeli ve `Test-Path C:\Windows\System32\vmcompute.exe` `True` olmalı.
- Hâlâ düzelmezse BIOS/UEFI'de Intel VT-x / AMD SVM'in açık olduğunu kontrol et. Tanı için `kurulum\wsl-tani.ps1` (yönetici) → `wsl-tani.log`.

### `WSL1 is not supported with your current machine configuration`
Bu mesaj tek başına sorun değildir (WSL1 bileşeni kurulu değil, zaten WSL2 kullanıyoruz). Önemli olan `wsl -l -v` çıktısında `VERSION 2` görünmesi.

### Derleme sırasında `Killed` veya işlem aniden ölüyor
Bellek yetmiyor. `C:\Users\<kullanici>\.wslconfig` dosyasında `memory=10GB` olduğundan emin ol, `-j` değerini düşür (`-j4`, `-j2`), `wsl --shutdown` ile yeniden başlat.

### Windows PowerShell'den `wsl -- bash -c '...'` ile karmaşık komutlar bozuluyor
Tırnak ve özel karakterler (`$`, `|`, `"`) PowerShell ile bash arasında karışır. Çözüm: komutu bir `.sh` dosyasına yaz ve
`wsl -d Ubuntu-24.04 -- bash /mnt/c/.../betik.sh` ile çalıştır. (Kurulum betikleri bu yüzden dosya olarak verildi.)

## Sionna

### `ImportError: ... LLVM backend is inactive ... "LLVM-C.dll" could not be found`
LLVM kurulu değil veya ortam değişkeni ayarlı değil. [03-sionna-windows.md](03-sionna-windows.md) 5. adım: `kur-llvm.ps1` (yönetici), sonra **yeni terminal aç**.
Elle kontrol: `[Environment]::GetEnvironmentVariable('DRJIT_LIBLLVM_PATH','User')` çıktısı `C:\Program Files\LLVM\bin\LLVM-C.dll` olmalı.

### `TypeError: PathSolver.__call__() got an unexpected keyword argument 'samples_per_tx'`
Sionna 1.2.2'de parametre `samples_per_src`'dir. Eski örnek kodlarda `samples_per_tx` geçebilir.

### `TensorFlow GPU support is not available on native Windows`
Beklenen ve zararsız uyarı. Sionna CPU'da çalışır.

### `pip install` sırasında çok uzun sessizlik
TensorFlow ve Mitsuba büyük paketlerdir. İlk 10 dakika çıktı yavaş olabilir. Kurulum 15–30 dakika sürer. Disk alanını kontrol et (≈ 2,1 GB gerekir).

### Global Python'daki paketlerle çakışma
Her zaman sanal ortamın Python'unu kullan: `C:\Users\<kullanici>\venvs\ehb415\Scripts\python.exe`. Global `python` komutu Sionna'yı bulamaz.

## ns-3 / 5G-LENA

### `./ns3 run cttc-nr-demo` programı bulamıyor
`contrib/nr` yolunu ve yapılandırma çıktısında nr modülünün listelendiğini kontrol et. Klasörün adı `nr` olmalı.

### Etiket (tag) bulunamıyor
Sığ klon yaptıysan (`--depth 1 --branch ...`) `git checkout` ile başka etikete geçemezsin; `git fetch --depth 1 origin tag <etiket>` ya da yeniden klon.

### ns-3.49 ile deneme
Yapma; 5G-LENA v5.1, ns-3.48 için tasarlandı.

## OCUDU

### CMake çıktısında `Found libZEROMQ` görünmüyor
`sudo apt install libzmq3-dev` kur, `build` klasörünü sil ve `cmake`'i yeniden çalıştır (ZMQ yalnızca yapılandırma sırasında algılanır).

### Derleyici sürümü uyarısı / hatası
Clang kullan: `CC=clang CXX=clang++ cmake ../ ...` (Ubuntu 24.04'te `sudo apt install clang`). gcc 13 ile denenmedi.

### Derleme çıktısında "error" kelimesi
Dosya adlarında geçebilir (`..._error_handler_impl.cpp`). Gerçek hata `error:` ile ve derleyicinin dosya:satır bilgisiyle başlar.

## Disk

### C: dolmak üzere
- WSL sanal diski zamanla büyür. `ccache -C` (Ubuntu içinde) ve `~/ehb415/*/build` klasörlerini temizlemek yer açar.
- Gerekirse [06-disk-genisletme.md](06-disk-genisletme.md) (yönetici gerekir, riskli).

## PowerShell (Windows PowerShell 5.1)

- `&&` / `||` zincirleme operatörleri yoktur: `A; if ($?) { B }` kullan.
- `Test-Path -Force` parametresi yoktur: `[System.IO.File]::Exists($yol)` kullan.
- Script çalıştırma izni için: `Set-ExecutionPolicy -Scope Process Bypass -Force` (yalnızca o pencere için geçerli).

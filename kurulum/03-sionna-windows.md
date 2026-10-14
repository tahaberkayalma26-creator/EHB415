# 03: Sionna ve Sionna RT (Windows, yerel Python, CPU)

> **Doğrulama durumu:** Bu dokümandaki tüm adımlar bu makinede çalıştırıldı ve doğrulandı
> (Sionna çekirdeği, OFDM radar testi, LLVM kurulumu, Sionna RT yol çözücü).

**Ne kuruluyor:** Python sanal ortamı + Sionna 1.2.2 + sionna-rt 1.2.2 + TensorFlow 2.21.0 + Mitsuba 3.8.0 + Dr.Jit 1.3.1 + JupyterLab 4.6.4 + LLVM 23.1.3.

## 1. Python 3.10–3.12

```powershell
py -0p
python --version
```

- 3.10, 3.11 veya 3.12 uygundur. Bu makinede 3.10.11 kullanıldı. **3.13 ile denemedik**, kullanma.
- Yoksa: `winget install --id Python.Python.3.12 -e`, ardından yeni bir PowerShell aç.

## 2. Sanal ortam oluştur (global Python'a dokunmadan)

```powershell
mkdir C:\Users\$env:USERNAME\venvs
python -m venv C:\Users\$env:USERNAME\venvs\ehb415
C:\Users\$env:USERNAME\venvs\ehb415\Scripts\python.exe -m pip install --upgrade pip
```

`py` ile belirli bir sürüm seçmek için: `py -3.10 -m venv ...`

**Neden sanal ortam?** Sionna, TensorFlow ve bağımlılıkları büyüktür ve başka kurulu paketlerle (örneğin PyTorch) çakışabilir.
Bu makinede global Python'da PyTorch 2.10 vardı; sanal ortam sayesinde karışmadı.

## 3. Paketleri kur

```powershell
C:\Users\$env:USERNAME\venvs\ehb415\Scripts\python.exe -m pip install sionna jupyterlab matplotlib scipy
```

- Süre: **15–30 dakika** (TensorFlow ve Mitsuba büyük). İlk 10 dakika sessiz görünebilir.
- Sanal ortam sonunda ≈ **2,1 GB** yer kaplar.
- `sionna` paketi `sionna-rt`, `tensorflow`, `mitsuba` ve `drjit`'i de getirir.

Kurulan sürümleri kontrol et:

```powershell
C:\Users\$env:USERNAME\venvs\ehb415\Scripts\python.exe -m pip list | findstr /i "sionna tensorflow keras mitsuba drjit jupyterlab"
```

Beklenen (bu makinede): `sionna 1.2.2`, `sionna-rt 1.2.2`, `tensorflow 2.21.0`, `keras 3.12.4`, `mitsuba 3.8.0`, `drjit 1.3.1`, `jupyterlab 4.6.4`.

## 4. Sionna doğrulaması

Bu klasördeki betiği çalıştır (komut satırını `EHB415` klasöründen ver):

```powershell
$env:TF_CPP_MIN_LOG_LEVEL='3'
C:\Users\$env:USERNAME\venvs\ehb415\Scripts\python.exe kurulum\sionna_dogrulama.py
```

Beklenen çıktı (bu makinedeki gerçek çıktı):

```
sionna 1.2.2 | tensorflow 2.21.0 | GPU: []
gercek   : R=120.0 m, v=25.0 m/s
tahmin   : R=122.1 m, v=25.9 m/s
cozunurluk (teorik): dR=4.88 m, dv=6.47 m/s
Sionna ResourceGrid OK | veri sembolu sayisi: tf.Tensor(1064, shape=(), dtype=int32)
```

Betik ne yapar:
1. Sionna ve TensorFlow'u içe aktarır, sürümleri yazar.
2. Saf NumPy ile tek hedefli bir **OFDM radar simülasyonu** yapar (1024 alt taşıyıcı × 30 kHz, 128 sembol, 4,9 GHz: TR 38.765 Ek A'daki parametrelerle uyumlu). Kanal tahmininden 2B FFT ile range-Doppler haritası çıkarıp hedefin mesafe ve hızını bulur.
3. Sionna'nın kendi `ResourceGrid` nesnesini oluşturur.

Tahmin hataları (2,1 m ve 0,9 m/s) teorik çözünürlük hücresinin (4,88 m, 6,47 m/s) içinde olduğu için sonuç doğrudur.
Çıktıda görünen *"TensorFlow GPU support is not available on native Windows"* uyarısı beklenen ve zararsızdır. oneDNN mesajları da zararsızdır.

## 5. LLVM'i kur (Sionna RT için, **yönetici gerekir**)

Sionna RT (ray tracing) CPU'da çalışmak için LLVM'e ihtiyaç duyar. LLVM yoksa `import sionna.rt` şu hatayı verir:

```
ImportError: jit_init_thread_state(): the LLVM backend is inactive because the LLVM shared library ("LLVM-C.dll") could not be found!
Set the DRJIT_LIBLLVM_PATH environment variable to specify its path.
```

Kurulum (yönetici PowerShell, bu klasörde):

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\kur-llvm.ps1
```

Betik: `winget install LLVM.LLVM` (≈ 609 MB indirme, LLVM 23.1.3) çalıştırır, `C:\Program Files\LLVM\bin\LLVM-C.dll` dosyasını bulur ve
`DRJIT_LIBLLVM_PATH` kullanıcı ortam değişkenini bu yola ayarlar. Betiğin logu `kur-llvm.log`'a yazılır.

**Betik bittikten sonra yeni bir PowerShell penceresi aç** (ortam değişkeni eski pencerelere yansımaz). Kontrol:

```powershell
[Environment]::GetEnvironmentVariable('DRJIT_LIBLLVM_PATH','User')
Test-Path 'C:\Program Files\LLVM\bin\LLVM-C.dll'
```

## 6. Sionna RT doğrulaması

```powershell
$env:TF_CPP_MIN_LOG_LEVEL='3'
C:\Users\$env:USERNAME\venvs\ehb415\Scripts\python.exe kurulum\sionna_rt_dogrulama.py
```

Beklenen (bu makinede):

```
mitsuba 3.8.0 | varyantlar: ['scalar_rgb', 'llvm_ad_rgb', 'llvm_ad_mono', 'llvm_ad_mono_polarized']
yol cozucu OK | bulunan gecerli yol sayisi: 12
```

Betik Sionna'nın yerleşik Münih sahnesini yükler, 4,9 GHz'de 1 verici (gNB) ve 1 alıcı yerleştirir ve `PathSolver` ile ışın yollarını hesaplar.
Yol sayısı sahne ve rastgele örneklemeye göre değişebilir; önemli olan `yol cozucu OK` satırıdır.

> Sionna 1.2.2'de `PathSolver` çağrısının parametresi `samples_per_src`'dir (eski belgelerde `samples_per_tx` geçebilir ve hata verir).

## 7. JupyterLab

```powershell
C:\Users\$env:USERNAME\venvs\ehb415\Scripts\jupyter-lab.exe
```

Tarayıcıda açılır. VS Code kullanıyorsan Python yorumlayıcısı olarak `C:\Users\<kullanici>\venvs\ehb415\Scripts\python.exe` seç
(Ctrl+Shift+P → "Python: Select Interpreter").

## 8. Bilinen sınırlamalar

1. **GPU kullanılamaz.** Yerel Windows'ta TensorFlow ≥ 2.11 GPU desteklemez. Ray tracing CPU'da daha yavaştır, küçük sahnelerde sorun olmaz.
2. LLVM yüklü değilse yalnızca Sionna RT çalışmaz, Sionna çekirdeği (OFDM, kanal, kodlama) çalışır.
3. İlk `import sionna` birkaç saniye (TensorFlow yüklenmesi yüzünden ~20 saniye) sürebilir.

## Sorun giderme

Bkz. [07-sorun-giderme.md](07-sorun-giderme.md).

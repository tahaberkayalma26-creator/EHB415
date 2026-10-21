# Sionna şehir projesi (Münih): ISAC görsel turu

Sionna RT ile bir şehirde gNB, kapsama haritası, ışın yolları ve bir İHA'nın radarla takibi.
Ayrıntılı anlatım ve bulgular: `ogretici/` PDF'inde Bölüm 4.4.

| Dosya | Ne yapar | Süre |
|---|---|---|
| `rt_sehir.py` | Sionna RT: sahne render, kapsama haritası, UE'ye ışın yolları, İHA rotası boyunca görüş hattı (LOS). `cikti/rt_sonuclar.npz` üretir | ~1 dk (ilk çalıştırma), sonra ~20 sn |
| `radar_takip.py` | OFDM radar: İHA takip filmi ve "sensing kaynağı ↔ başarı" Monte Carlo analizi | ~2 dk |
| `cikti/` | Üretilen şekiller, `05_takip_filmi.gif` (≈10 MB), CSV'ler |  |

## Çalıştırma (Windows)

```powershell
$env:DRJIT_LIBLLVM_PATH = [Environment]::GetEnvironmentVariable('DRJIT_LIBLLVM_PATH','User')
cd ogretici\sionna_sehir
C:\Users\<kullanici>\venvs\ehb415\Scripts\python.exe rt_sehir.py       # Sionna 1.2.2 + LLVM gerekir (kurulum/03)
python radar_takip.py                                                  # numpy, matplotlib, pandas, pillow gerekir
```

## Önemli notlar

- `rt_sehir.py`: Sionna'nın `paths.cir()` fonksiyonu varsayılan olarak **gecikmeleri normalize eder** (ilk yol = 0). Gerçek gecikme için `normalize_delays=False` verilmelidir; aksi halde doğrudan yol "gecikme 0" sayılıp filtrelenir.
- LOS tespiti için `PathSolver(max_depth=1, los=True, specular_reflection=False, refraction=False)` kullanıldı (`max_depth=0` hiç yol döndürmüyor).
- `radar_takip.py`'deki tüm radar varsayımları (güç, kazanç, RCS, öz-girişim X, NLOS kaybı, Pfa) dosyanın başındaki PARAM bölümünde; sonuçlar **eğilimi** gösterir, mutlak sayılar gerçek sistem için geçerli değildir.

# EHB415 ISAC Projesi: Kurulum Dokümanları (Windows 11)

Bu klasör, projede kullanılan tüm yazılımların **Windows 11** üzerinde nasıl kurulacağını anlatır.
Dokümanlar 2026-10-14'te bir Windows 11 Home dizüstü bilgisayarda (i5-1240P, 16 GB RAM, NVIDIA GPU yok) **fiilen kurularak** yazıldı.
Her dokümanın başında hangi adımların gerçekten çalıştırılıp doğrulandığı, hangilerinin doğrulanmadığı yazar.

## Sırayla izle

| # | Doküman | Ne kuruyor | Yönetici gerekir mi | Tahmini süre |
|---|---|---|---|---|
| 0 | [00-genel-bakis.md](00-genel-bakis.md) | Neyin nerede çalıştığı, sürümler, donanım gereksinimi | Hayır | okuma: 5 dk |
| 1 | [01-git-vscode.md](01-git-vscode.md) | Git, VS Code, ortak repo kuralları | Hayır | 10 dk |
| 2 | [02-wsl2-ubuntu.md](02-wsl2-ubuntu.md) | WSL2 + Ubuntu 24.04 | **Evet** + yeniden başlatma | 20 dk |
| 3 | [03-sionna-windows.md](03-sionna-windows.md) | Python 3.10, Sionna, Sionna RT, LLVM | Sadece LLVM için | 30-40 dk |
| 4 | [04-ns3-5g-lena.md](04-ns3-5g-lena.md) | ns-3.48 + 5G-LENA v5.1 (WSL içinde) | Hayır | ~18 dk ölçüldü (zayıf makinede 30-60) |
| 5 | [05-ocudu.md](05-ocudu.md) | OCUDU 26.10 gNB (WSL içinde) | Hayır | ~23 dk ölçüldü (zayıf makinede 40-60) |
| 6 | [06-disk-genisletme.md](06-disk-genisletme.md) | **İsteğe bağlı:** disk alanı açmak | **Evet** | 5 dk |
| 7 | [07-sorun-giderme.md](07-sorun-giderme.md) | Gerçekten karşılaşılan hatalar ve çözümleri | - | - |

Sıra önemli: 2 bitmeden 4 ve 5 yapılamaz. 3, 2'den bağımsızdır.

## Hızlı kontrol listesi (kurulum bitince hepsi işaretli olmalı)

```powershell
# PowerShell
git --version                                  # git version 2.4x veya üzeri
wsl -l -v                                      # Ubuntu-24.04, VERSION 2
C:\Users\$env:USERNAME\venvs\ehb415\Scripts\python.exe kurulum\sionna_dogrulama.py      # radar testi + ResourceGrid OK
C:\Users\$env:USERNAME\venvs\ehb415\Scripts\python.exe kurulum\sionna_rt_dogrulama.py   # "yol cozucu OK"
```

```bash
# Ubuntu terminali
cd ~/ehb415/ns-3-dev && ./ns3 run cttc-nr-demo      # "Mean flow throughput" satırı görünmeli
~/ehb415/ocudu/build/apps/gnb/gnb --version         # OCUDU 5G gNB version 26.10.0 ...
```

## Bu klasördeki dosyalar

| Dosya | Amaç |
|---|---|
| `kur-wsl.ps1` | Yönetici PowerShell: WSL2 ve Sanal Makine Platformu kurar |
| `kur-llvm.ps1` | Yönetici PowerShell: LLVM kurar, `DRJIT_LIBLLVM_PATH` ayarlar |
| `disk-genislet.ps1` | Yönetici PowerShell: C: sürücüsünü genişletir (**sadece 06'ya bak**) |
| `wsl-tani.ps1` | Yönetici PowerShell: WSL2 sanallaştırma tanısı |
| `wsl_ns3_kur.sh` | Ubuntu içinde ns-3 + 5G-LENA kurulumu (otomatik) |
| `wsl_ocudu_kur.sh` | Ubuntu içinde OCUDU kurulumu (otomatik) |
| `sionna_dogrulama.py` | Sionna ve OFDM radar doğrulaması |
| `sionna_rt_dogrulama.py` | Sionna RT (ray tracing) doğrulaması |
| `loglar/` | Bu makinedeki gerçek kurulum çıktıları (referans için) |

## Bir şey ters giderse

Önce [07-sorun-giderme.md](07-sorun-giderme.md), orada yoksa hatanın tam metnini ve hangi adımda olduğunu proje grubuna yaz, çözümü ilgili dokümana ekleyelim.

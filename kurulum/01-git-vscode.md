# 01: Git, VS Code ve Ortak Repo (Windows)

> **Doğrulama durumu:** Bu makinede Git 2.53.0 ve VS Code 1.141.1 **önceden kuruluydu**, bu yüzden `winget install` komutları burada
> çalıştırılmadı. Komutlar standarttır ama bu makinede denenmedi. VS Code eklenti komutları da denenmedi.
> Sürüm kontrolleri (`git --version`, `code --version`) çalıştırıldı.

## 1. Mevcut kurulumu kontrol et

PowerShell'de (yönetici gerekmez):

```powershell
git --version
code --version
winget --version
```

Üçü de bir sürüm yazdırıyorsa 3. adıma geç.

## 2. Kurulum (eksik olanlar için)

```powershell
winget install --id Git.Git -e
winget install --id Microsoft.VisualStudioCode -e
```

- `winget` yoksa Microsoft Store'dan "Uygulama Yükleyicisi" (App Installer) güncelle.
- Kurulumdan sonra **yeni bir PowerShell penceresi** aç, yoksa PATH güncellenmez.

## 3. Git kimliği (her üye kendi bilgisayarında, bir kez)

```powershell
git config --global user.name "Ad Soyad"
git config --global user.email "okul-epostan@itu.edu.tr"
git config --global core.autocrlf input
git config --global init.defaultBranch main
```

`core.autocrlf input`: Windows'ta dosyalar CRLF ile kaydedilebilir; Linux'ta `.sh` betikleri CRLF ile çalışmaz.
Bu ayar, commit sırasında satır sonlarını LF'ye çevirir.

Kontrol: `git config --global --list`

## 4. VS Code eklentileri

```powershell
code --install-extension ms-vscode-remote.remote-wsl
code --install-extension ms-python.python
code --install-extension ms-toolsai.jupyter
code --install-extension ms-vscode.cpptools
```

| Eklenti | Ne için |
|---|---|
| Remote - WSL | VS Code'u Ubuntu içindeki klasörlerle açmak (ns-3 ve OCUDU kodunu düzenlemek için) |
| Python, Jupyter | Sionna notebook'ları |
| C/C++ | ns-3 ve OCUDU kodunu okumak |

WSL kurulduktan sonra (02 numaralı doküman) Ubuntu terminalinde `code .` yazarsan VS Code o klasörü Ubuntu bağlamında açar.

## 5. Ortak repo (öneri)

Repo yapısı:

```
ehb415-isac/
  docs/            # metrik sözlüğü, tasarım kararları, kurulum dokümanları
  sionna/          # notebook ve Python betikleri
  ns3/             # senaryo dosyaları ve CSV çıktıları (ns-3'ün kendisi DEĞİL)
  ocudu/           # notlar, diyagramlar, yama dosyaları (OCUDU'nun kendisi DEĞİL)
  results/         # ortak sonuç CSV'leri ve grafikler
  literature/      # okuma özetleri (PDF'ler hariç)
```

Kurallar:
- ns-3 ve OCUDU gibi büyük dış projeleri repoya **kopyalama**. Yalnızca kendi senaryolarını, yamalarını ve sonuçlarını koy.
- Sürümleri `docs/versions.md` içinde tut: ns-3.48, 5G-LENA v5.1, OCUDU release_26_10, Sionna 1.2.2.
- Her Jira görevi için bir dal aç: `ehb415-12-sionna-radar`.
- Her görevin çıktısı repoda bir dosya olmalı (notebook, CSV, markdown).
- Büyük dosyaları (>20 MB, PDF, ham trace) repoya koyma; `.gitignore`'a ekle.

Örnek `.gitignore`:

```
*.pdf
*.pcap
*.h5
*.npz
__pycache__/
.ipynb_checkpoints/
```

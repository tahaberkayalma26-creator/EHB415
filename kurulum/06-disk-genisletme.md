# 06: Disk Alanı Açmak, C: Sürücüsünü Genişletmek (İSTEĞE BAĞLI, RİSKLİ)

> **Bunu sadece C: sürücünde 40 GB'den az boş alan varsa ve aşağıdaki "uygunluk" koşulunu sağlıyorsan yap.**
> Disk bölümlerini değiştirir. Hata ya da elektrik kesintisi durumunda veri veya önyükleme sorunu riski vardır.
> **Önce önemli verilerini yedekle.**

> **Doğrulama durumu:** Bu işlem bu makinede yapıldı ve başarıyla tamamlandı (C: 395,1 GB → 475,7 GB; boş alan 16 GB → 97 GB; WinRE yeniden etkin).
> Başka bir makinede aynı sonucu garanti edemeyiz; betik, düzen farklıysa hiçbir şey değiştirmeden durur.

## Ne zaman uygun?

`Get-Partition -DiskNumber 0` çıktısı şu düzende olmalı ve C: ile Recovery'nin arkasında **ayrılmamış (unallocated) alan** olmalı:

```
PartitionNumber DriveLetter SizeGB Type
              1                0.1 System
              2                  0 Reserved
              3           C  395.1 Basic
              4                0.9 Recovery      <- C'nin hemen arkasında
                                                 <- bunun arkasında ayrılmamış alan (>= 10 GB)
```

Ayrılmamış alan miktarı: `Get-Disk 0 | Select Size, AllocatedSize` (fark = ayrılmamış alan).

**Neden doğrudan genişletilemez?** Windows bir bölümü yalnızca **hemen arkasındaki** boş alanla genişletir. Burada arada Recovery bölümü vardır.
Betik şunu yapar: WinRE'yi devre dışı bırakır (kurtarma imajı `Winre.wim` C: içine kopyalanır, varlığı doğrulanır) → Recovery bölümünü siler →
C:'yi genişletir (sondan 1 GB bırakır) → 1 GB'lik yeni Recovery bölümü oluşturur ve GPT niteliklerini ayarlar → WinRE'yi yeniden etkinleştirir.

## Alternatif (daha güvenli): ayrı bölüm

C:'yi genişletmek istemiyorsan ayrılmamış alandan yeni bir **D:** bölümü açıp WSL'i ve projeleri oraya koyabilirsin.
Bu yaklaşımda Recovery'ye dokunulmaz. Disk Yönetimi'nde (`diskmgmt.msc`) ayrılmamış alana sağ tık → "Yeni Basit Birim". **Bu yol bu makinede denenmedi.**

## Çalıştırma (yönetici PowerShell)

```powershell
cd C:\...\EHB415\kurulum
Set-ExecutionPolicy -Scope Process Bypass -Force
.\disk-genislet.ps1
```

Betik şu güvenlik kontrollerini yapar ve **hepsi geçmezse hiçbir şeye dokunmadan "DURDU" yazıp çıkar**:
- Yönetici yetkisi var mı?
- Disk 0 GPT mi?
- C: bölümünden sonra **tam 1** bölüm var mı, o bölüm Recovery mi, boyutu ≤ 2 GB mı, C: ile bitişik mi?
- Recovery'nin arkasında en az 10 GB ayrılmamış alan var mı?
- `C:\Windows\System32\Recovery\Winre.wim` kurtarma imajı yedekte mi? (Yoksa Recovery bölümünü silmeden durur.)

Log dosyası: `disk-genisletme.log` (aynı klasörde). Sonda "TAMAMLANDI." yazmalı ve `reagentc /info` çıktısı **Windows RE status: Enabled** göstermeli.

## Doğrulama

```powershell
Get-Partition -DiskNumber 0 | Select PartitionNumber, DriveLetter, @{n='SizeGB';e={[math]::Round($_.Size/1GB,1)}}, Type
reagentc /info
[math]::Round((Get-PSDrive C).Free/1GB,1)
```

Beklenen: C: büyümüş, bölüm 4 yine `Recovery` (≈ 1 GB), `Windows RE status: Enabled`.

## Bu makinedeki yaşanan sorunlar (betiğin son hali bunları çözer)

1. **İlk deneme:** tek bölüm bulunduğunda PowerShell sonucu dizi saymadığı için `.Count` boş çıktı ve betik güvenlik kontrolünde durdu. Disk değişmedi. Düzeltme: `@(...)`.
2. **İkinci deneme:** `reagentc /disable` çalıştı ama sonra `Test-Path -Force` Windows PowerShell 5.1'de yok olduğu için hata verip durdu. WinRE devre dışı kaldı, bölüm silinmedi. `Winre.wim` (756,5 MB) C: içinde yedekteydi.
   Düzeltme: `[System.IO.File]::Exists(...)`, WinRE zaten kapalıysa devam etme, hata durumunda ve bölüm silinmediyse WinRE'yi yeniden açma.
3. **Üçüncü deneme:** tamamlandı.

## Geri alma / kurtarma notu

Betik yarıda kesilirse: `reagentc /info` ile WinRE durumuna bak. Recovery bölümü silinmişse ve yeni bölüm oluşmamışsa
WinRE devre dışı kalır; Windows normal çalışır ama "Bu bilgisayarı sıfırla"/başlangıç onarımı çalışmayabilir.
`reagentc /enable` ve yeni bir Recovery bölümü oluşturularak (GPT türü `de94bba4-06d1-4d40-a16a-bfd50179d6ac`) düzeltilir.

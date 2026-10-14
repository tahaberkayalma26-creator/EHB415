# EHB415 - C: surucusunu, Recovery bolumunun arkasindaki ayrilmamis alanla genisletir.
# Yonetici PowerShell gerektirir. Beklenen duzen tutmazsa HICBIR SEY DEGISTIRMEDEN durur.
#
# Beklenen duzen (Disk 0, GPT):  ... | C: (NTFS) | Recovery (~1 GB) | ayrilmamis alan (>= 10 GB)
# Adimlar:
#   1) Duzeni dogrula
#   2) WinRE'yi devre disi birak (winre.wim C: icine kopyalanir) ve dosyanin varligini dogrula
#   3) Recovery bolumunu sil
#   4) C: bolumunu genislet (sondan 1 GB birakarak)
#   5) 1 GB'lik yeni Recovery bolumu olustur, GPT niteliklerini ayarla
#   6) WinRE'yi yeniden etkinlestir

$ErrorActionPreference = 'Stop'
$log = Join-Path $PSScriptRoot 'disk-genisletme.log'
Start-Transcript -Path $log -Append | Out-Null

function Stop-Script($msg) {
    Write-Host "DURDU: $msg" -ForegroundColor Red
    Stop-Transcript | Out-Null
    Read-Host "Kapatmak icin Enter'a bas"
    exit 1
}

try {
    $admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $admin) { Stop-Script "Yonetici olarak calistirilmali." }

    # ---- 1) Duzen dogrulama ----
    $disk = Get-Disk -Number 0
    if ($disk.PartitionStyle -ne 'GPT') { Stop-Script "Disk 0 GPT degil." }
    $parts = Get-Partition -DiskNumber 0 | Sort-Object Offset
    $c = $parts | Where-Object DriveLetter -eq 'C'
    if (-not $c) { Stop-Script "C: bolumu Disk 0'da bulunamadi." }
    $after = @($parts | Where-Object { $_.Offset -gt $c.Offset } | Sort-Object Offset)
    if ($after.Count -ne 1) { Stop-Script "C: bolumunden sonra tam 1 bolum olmali, $($after.Count) bulundu." }
    $rec = $after[0]
    if ($rec.Type -ne 'Recovery') { Stop-Script "C: sonrasi bolum Recovery degil ($($rec.Type))." }
    if ($rec.Size -gt 2GB) { Stop-Script "Recovery bolumu beklenenden buyuk ($([math]::Round($rec.Size/1GB,1)) GB)." }
    $gap = [math]::Abs(($c.Offset + $c.Size) - $rec.Offset)
    if ($gap -gt 16MB) { Stop-Script "C: ile Recovery bitisik degil." }
    $free = $disk.Size - ($rec.Offset + $rec.Size)
    if ($free -lt 10GB) { Stop-Script "Recovery sonrasi ayrilmamis alan yetersiz ($([math]::Round($free/1GB,1)) GB)." }
    Write-Host ("Duzen dogru. C: {0} GB, Recovery {1} GB (bolum {2}), ayrilmamis ~{3} GB" -f [math]::Round($c.Size/1GB,1), [math]::Round($rec.Size/1GB,2), $rec.PartitionNumber, [math]::Round($free/1GB,1))

    # ---- 2) WinRE devre disi + yedek dogrulama ----
    $info = (reagentc /info | Out-String)
    Write-Host $info
    $script:reDisabledByUs = $false
    if ($info -match 'Enabled') {
        reagentc /disable
        if ($LASTEXITCODE -ne 0) { Stop-Script "reagentc /disable basarisiz." }
        $script:reDisabledByUs = $true
    } else {
        Write-Host "WinRE zaten devre disi, /disable atlandi."
    }
    $wim = 'C:\Windows\System32\Recovery\Winre.wim'
    if (-not [System.IO.File]::Exists($wim)) {
        if ($script:reDisabledByUs) { reagentc /enable }
        Stop-Script "Winre.wim C: icinde bulunamadi, Recovery bolumu SILINMEDI."
    }
    Write-Host ("Winre.wim C: icinde yedekte: {0} MB" -f [math]::Round(([System.IO.FileInfo]$wim).Length/1MB,1))

    # ---- 3) Recovery bolumunu sil ----
    $recNo = $rec.PartitionNumber
    Remove-Partition -DiskNumber 0 -PartitionNumber $recNo -Confirm:$false
    Write-Host "Recovery bolumu silindi."

    # ---- 4) C: genislet (sondan 1 GB birak) ----
    $sup = Get-PartitionSupportedSize -DriveLetter C
    $newSize = $sup.SizeMax - 1GB
    Resize-Partition -DriveLetter C -Size $newSize
    Write-Host ("C: genisletildi: {0} GB" -f [math]::Round((Get-Partition -DriveLetter C).Size/1GB,1))

    # ---- 5) Yeni Recovery bolumu ----
    $np = New-Partition -DiskNumber 0 -UseMaximumSize -GptType '{de94bba4-06d1-4d40-a16a-bfd50179d6ac}'
    $np | Format-Volume -FileSystem NTFS -NewFileSystemLabel 'Recovery' -Confirm:$false | Out-Null
    $dp = "select disk 0`r`nselect partition $($np.PartitionNumber)`r`ngpt attributes=0x8000000000000001`r`nexit`r`n"
    $tmp = Join-Path $env:TEMP 'dp_rec.txt'
    Set-Content -Path $tmp -Value $dp -Encoding ascii
    diskpart /s $tmp
    Remove-Item -LiteralPath $tmp -ErrorAction SilentlyContinue

    # ---- 6) WinRE yeniden etkinlestir ----
    reagentc /enable
    reagentc /info
    Get-Volume -DriveLetter C | Select DriveLetter, @{n='SizeGB';e={[math]::Round($_.Size/1GB,1)}}, @{n='FreeGB';e={[math]::Round($_.SizeRemaining/1GB,1)}} | Format-Table | Out-String | Write-Host
    Write-Host "TAMAMLANDI." -ForegroundColor Green
}
catch {
    Write-Host "HATA: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Durumu kontrol et: Get-Partition -DiskNumber 0 ; reagentc /info."
    # Recovery bolumu hala varsa WinRE'yi eski haline dondur
    $stillThere = Get-Partition -DiskNumber 0 -ErrorAction SilentlyContinue | Where-Object Type -eq 'Recovery'
    if ($stillThere) { Write-Host "Recovery bolumu duruyor, WinRE yeniden etkinlestiriliyor."; reagentc /enable }
}
Stop-Transcript | Out-Null
Read-Host "Kapatmak icin Enter'a bas"

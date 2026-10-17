# Python 3.10.11'i kaldirir (yonetici gerekir). Kullanici dizinindeki paketlere (AppData\Roaming\Python\Python310) dokunmaz.
# Once pip freeze listesi C:\Users\<kullanici>\python310_pip_freeze.txt dosyasina yedeklenmis olmali.
Start-Transcript -Path (Join-Path $PSScriptRoot 'kaldir-python310.log') -Force | Out-Null
winget uninstall --id Python.Python.3.10 -e --silent --accept-source-agreements
"cikis kodu: $LASTEXITCODE"
Test-Path 'C:\Program Files\Python310\python.exe'
Stop-Transcript | Out-Null

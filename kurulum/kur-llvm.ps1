# EHB415 - Sionna RT (CPU) icin LLVM kurulumu ve DRJIT_LIBLLVM_PATH ayari.
# Yonetici PowerShell gerektirir.
$ErrorActionPreference = 'Continue'
Start-Transcript -Path (Join-Path $PSScriptRoot 'kur-llvm.log') -Append | Out-Null

winget install --id LLVM.LLVM -e --accept-package-agreements --accept-source-agreements

$dll = @('C:\Program Files\LLVM\bin\LLVM-C.dll') | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($dll) {
    [Environment]::SetEnvironmentVariable('DRJIT_LIBLLVM_PATH', $dll, 'User')
    Write-Host "DRJIT_LIBLLVM_PATH = $dll (kullanici duzeyinde ayarlandi; yeni terminal ac)"
} else {
    Write-Warning "LLVM-C.dll bulunamadi. LLVM kurulumunu kontrol et."
}
Stop-Transcript | Out-Null
Read-Host "Kapatmak icin Enter'a bas"

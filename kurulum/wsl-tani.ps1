# WSL2 tani betigi (yonetici). Sonucu wsl-tani.log dosyasina yazar.
$log = Join-Path $PSScriptRoot 'wsl-tani.log'
Start-Transcript -Path $log -Force | Out-Null
foreach ($f in 'VirtualMachinePlatform','Microsoft-Windows-Subsystem-Linux','HypervisorPlatform','Microsoft-Hyper-V-All') {
    $s = Get-WindowsOptionalFeature -Online -FeatureName $f -ErrorAction SilentlyContinue
    "{0}: {1}" -f $f, $(if ($s) { $s.State } else { 'bulunamadi' })
}
"--- hypervisorlaunchtype"
bcdedit /enum '{current}' | Select-String 'hypervisor'
"--- vmcompute"
sc.exe query vmcompute
"--- bios sanallastirma"
(Get-CimInstance Win32_Processor | Select-Object Name, VirtualizationFirmwareEnabled | Format-List | Out-String)
"--- wsl"
wsl --status
Stop-Transcript | Out-Null

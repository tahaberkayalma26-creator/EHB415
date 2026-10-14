# EHB415 - WSL2 + Ubuntu 24.04 kurulum betigi
# KULLANIM: PowerShell'i "Yonetici olarak calistir" ile ac, sonra:
#   Set-ExecutionPolicy -Scope Process Bypass -Force
#   .\kur-wsl.ps1
# Betik bitince bilgisayari yeniden baslat, sonra 02-wsl2-ubuntu.md'deki 3. adimdan (gercek yeniden baslatma) devam et.

$ErrorActionPreference = 'Stop'
Start-Transcript -Path (Join-Path $PSScriptRoot 'kur-wsl.log') -Append | Out-Null

$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $admin) { Write-Error "Bu betik yonetici olarak calistirilmali."; exit 1 }

$free = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
Write-Host "C: uzerinde bos alan: $free GB"
if ($free -lt 40) { Write-Warning "40 GB'den az bos alan var. ns-3 ve OCUDU derlemeleri sirasinda disk dolabilir. Devam etmeden once yer ac." }

Write-Host "WSL2 ve Ubuntu-24.04 kuruluyor..."
wsl --install -d Ubuntu-24.04
wsl --set-default-version 2

Write-Host ""
Write-Host "Kurulum tamamlandi. Bilgisayari YENIDEN BASLAT, ardindan Baslat menusunden 'Ubuntu 24.04' ac ve kullanici adi/sifre olustur."
Stop-Transcript | Out-Null
Read-Host "Kapatmak icin Enter'a bas"


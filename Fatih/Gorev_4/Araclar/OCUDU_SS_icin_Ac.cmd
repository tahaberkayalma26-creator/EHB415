@echo off
chcp 65001 >nul
title OCUDU gercek kosu ve ekran goruntusu
echo Ubuntu aciliyor. Dogrulama bitmeden yeni kosu baslatilmaz.
wsl.exe -d Ubuntu-24.04 -u fatih --cd /home/fatih/ehb415/gorev4_project -- bash "/mnt/c/Users/fatih/OneDrive/Desktop/Data Com/4. Görev Kartı Belgeleri/Araclar/ss_icin_calistir.sh"
if errorlevel 1 echo Calistirma tamamlanamadi. Yukaridaki hata mesajini kaydedin.
pause

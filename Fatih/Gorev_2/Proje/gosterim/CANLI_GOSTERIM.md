# OCUDU'nun çalıştığını ve ölçüm ürettiğini gösterme

Komutları Windows Başlat menüsünden açılan **Ubuntu 24.04** terminaline yaz.

1. Sürümü göster:

```bash
~/ehb415/ocudu/build/apps/gnb/gnb --version
```

Beklenen sürüm: `OCUDU 5G gNB version 26.10.0`.

2. Hazır radyosuz testi çalıştır:

```bash
cd ~/ehb415/ocudu/build/apps/gnb
./gnb -c ~/ehb415/ocudu_testmode.yml
```

`Cell ... bw=20 MHz ... (n3)` ve `==== gNB started ===` satırlarının ekran görüntüsünü al.

3. Aynı pencereye **t** yazıp **Enter** tuşuna bas. Yeni bir komut penceresi açma.

DL/UL başlıkları altında yeni ölçüm satırları akacak. Pencereyi büyütüp başlıklarla birlikte birkaç satırın ekran görüntüsünü al.

- DL `brate`: indirme yönündeki bit hızı; `59M` yaklaşık 59 Mbps.
- DL `ok`: saniyedeki başarılı blok sayısı; önceki PRS kapalı koşuda yaklaşık 1000.
- DL `nok`: başarısız blok sayacı.

4. **Ctrl+C** ile durdur.

5. Önceki iki koşunun karşılaştırmasını göster:

| Koşul | DL hız | Başarılı blok/s |
|---|---:|---:|
| PRS kapalı | 59 Mbps | 1000 |
| PRS her 4 slotta | 44 Mbps | 750 |

Aynı klasördeki `ocudu_karsilastirma.png` bu ölçümlerin grafiğidir. Ham kayıtlar ve CSV, üst klasördeki `ilk_iki_20261025T152612Z_298` klasöründedir.

Sunumda kapsamı "radyosuz, bir sanal kullanıcılı test modu" olarak belirt. Bu gösterim hücrenin başladığını ve OCUDU'nun test trafiğiyle DL/UL sayaçları ürettiğini gösterir. Başarılı blok sayısı ile paket sayısını karıştırma. Sabit CQI=15 ayarı test girdisidir.

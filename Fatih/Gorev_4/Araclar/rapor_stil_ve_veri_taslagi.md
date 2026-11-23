# Görev 4 rapor hazırlık sözleşmesi

Bu hazırlık notu nihai Word raporu değildir. Ölçümler tamamlanmadan belge üreticisi ve render çalıştırılmayacaktır.

Referans belge C:\Users\fatih\OneDrive\Desktop\Data Com\2. Görev Kartı Belgeleri\Fatih_Görev_Kartı_2_Çıktıları.docx dosyasıdır. SHA256 d1585e9f56a7461e709f2285b8913f2bbf638aa310f1efa234a81e44252ba12c değeriyle salt okunur incelendi. Sayfa sistemi tek bölüm, Letter 8,5 × 11 inç, dört kenarda 1 inç, üstbilgi ve altbilgi uzaklığı 708 twip, tek sütundur. Temel metin 12 punto Times New Roman, siyah; başlıklar kalın ve sadedir. Önceki belgenin içeriği yeni sonuçlarla değiştirilir; sayfa sistemi ve sade yazı görünümü korunur. Başlık çizgisi, renkli kutu ve süslü sayfa bileşeni eklenmez.

Yazı tüm metinde edilgen anlatım kullanır; birinci şahıs kullanılmaz. Komutlar ve birebir gerçek terminal alıntıları okuma için Consolas 9 punto istisnasıdır; normal metin, başlık ve tablolar Times New Roman 12 puntodur. Yeni tablolar sayısal karşılaştırmalar için kullanılır; açık gri başlık, görünür D9D9D9 ince sınır, değişken satır yüksekliği ve yinelenen başlık taşır.

Üretici Araclar/rapor_uret.py dosyasıdır. Yalnız --final-data-ready ile çalışır. Yetkili kaynak Ham_Kayitlar/*/summary.json, config.yml, command.txt, terminal.txt, metrics.csv ve gnb.log.gz dosyalarıdır. Büyüyen tum_olcumler.json nihai koşu verisi yerine kullanılmaz. Kaynakların hiçbiri üreticide değiştirilmez.

K0, ref100_1–3 ortalamasıdır. K1–K11 oncesi_Kn koşularıdır. RE denemesi K1 K6 K7 K8 K11 için oncesi ve sonrasi çiftlerini kullanır. Koşul tanımları Araclar/prs_kosullari.json üzerinden okunur. K11 güncel 4c31d938 depo Excel kaynağıyla ayrıca belirtilir; özgün 22 505 bayt Excel ile aynı kaynak gibi sunulmaz. Kaynak model öngörüsü ölçümden ayrılır. Boş K11 formül önbelleğinden sayı uydurulmaz.

İlk b100_r1 b100_r2 b100_r3 ve ilk band40 band60 band80 band100 koşuları tanısaldır. Uyarı fırtınası ve zamanlama bozulması bulunan koşular duvar zamanı hız ortalaması sayılmaz. ConRes bildirim hatası ve dummy saat geri okuma hatası iki ayrı bulgu olarak işlenir. SIB1, late, NOK ve PDCCH hata kayıtları gizlenmez; sıfır NOK tüm koşunun temiz olduğu iddiasına dönüştürülmez.

Rapor sekiz ana içerik bölümüyle tasarlanmıştır. Her bölüm doğal sayfa akışına göre gerekirse taşabilir. Gerçek ekran görüntüleri varsa belgenin sonunda kaynağıyla eklenir. Ekran görüntüsü yoksa gerçek terminal.txt metrik satırından DL ve UL bölümleri doğrudan alıntılanır. Terminal UI veya sahte ekran görüntüsü oluşturulmaz.

Nihai veri bildirildikten sonra referans ve sonuç Word sayfaları render edilip tüm PNG sayfaları kontrol edilir. Paket Python yolu C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1118-904-0_26.1118.904.0_x64__3k8sg7r9htsxt\dependencies\python\python.exe olarak çözüldü. Paket Windows ortamında LibreOffice bulunmadığından önce canonical render_docx.py bir kez denenip tanı kaydı saklanacaktır; root onayıyla Word COM salt okunur PDF dışa aktarma ve paket Poppler ile PNG denetimi yedek yöntemdir. Kullanıcının masaüstü LibreOffice kurulumu kullanılmaz.

Hazırlık aşamasında referans render ve sayfa sayısı henüz doğrulanmadı; root FINAL VERİ HAZIR bildirimi bekleniyor. Nihai teslim yalnız son rapor DOCX dosyasıdır; render PNG/PDF dosyaları iç denetim çıktısıdır.

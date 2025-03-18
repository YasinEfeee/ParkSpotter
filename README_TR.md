# ParkSpotter

Bu proje, yapay zekâ destekli bir sistem ile park alanı arama sürecini daha hızlı, verimli ve erişilebilir hale getirmeyi amaçlamaktadır.
Sistem; çarşı, alışveriş merkezi ve özel mülk park alanlarında gerçek zamanlı izleme, engelli bireylere öncelikli erişim sağlama, anomalilerin tespiti ve düşük maliyetli teknoloji altyapısıyla öne çıkmaktadır.
Python ve YOLOv8 modeli ile geliştirilen proje, çevresel sürdürülebilirlik hedeflerine katkı sunarken trafik akışını optimize etmeyi hedeflemektedir.

## Firebase Entegrasyonu Uyarı !!
Bu proje, otopark verilerini verimli bir şekilde depolamak ve yönetmek için veritabanı olarak Firebase'i kullanır. 
Sorunsuz entegrasyon sağlamak için Firebase hesabınızı yapılandırdığınızdan ve serviceAccountKey.json dosyasını sağladığınızdan emin olun.

## Proje Amacı
Kentleşmenin artmasıyla birlikte, kullanılabilir park alanlarını bulmak önemli bir zorluk haline gelmiş, zaman kaybı, finansal maliyetler ve çevresel sorunlara yol açmıştır. ParkSpotter sistemi, şu amaçlarla geliştirilmiştir:

- **Park arama sürecini hızlandırmak** ve daha verimli hale getirmek.
- **Engelli bireyler için erişilebilirliği artırmak**, belirlenmiş park yerlerinin doğru kullanımını sağlamak.
- Belediyeler ve özel park alanları için **uygun fiyatlı ve ölçeklenebilir bir yapay zeka tabanlı** çözüm sunmak.
- **Uygunsuz park yerlerinin kullanımını** tespit etmek.

## Özellikler

- **Görüntü Analizi:** Kamera görüntüleri, videolar veya fotoğraflar üzerinden park alanı doluluk analizi.
- **Park Alanı Seçme:** Video, Canlı Kamera veya fotoğraf üzeriden park alanı seçebilirsiniz.
- **Gerçek Zamanlı Tespit:** Canlı kamera akışları ve video kayıtları üzerinden analiz yapma.
- **Engelli Dostu Tasarım:** Engelli park alanlarının özel park alanı seçimi, takibi ve uyarı sistemleri.
- **Firebase Entegrasyonu:** Veri tabanı bağlantısı ile analiz sonuçlarının bulut üzerinde depolanması.
- **Kullanıcı Dostu Arayüz:** PyQt5 tabanlı grafiksel arayüz ile kolay kullanım.
- **Moniterizasyon:** Park alanlarının etkin yönetimi ve anomalilerin tespiti.
- **Otopark Yeniden Düzenleme:** Kullanıcıların otoparklarını yeniden düzenlemelerine olanak tanır ve tüm değişiklikler otomatik olarak Firebase'e kaydedilir.

## Kullanılan Teknolojiler

- **Programming Language:** Python
- **Machine Learning Model:** Ultralytics YOLOv8
- **GUI Development:** PyQt5
- **Image Processing:** OpenCV
- **Database:** Firebase
- **IDE:** PyCharm

## Kullanım

1. **Görsel Yükleme:** Kamera görüntüleri veya fotoğraflar yükleyerek analiz başlatabilirsiniz.
2. **Park Alanı Seçme:** Video, Canlı Kamera veya fotoğraf üzeriden park alanı seçebilirsiniz 
3. **Gerçek Zamanlı Analiz:** Canlı kamera akışlarını kullanarak park alanı doluluk durumunu izleyin.
4. **Analiz Sonuçları:** Sonuçları hem görsel hem de Firebase veri tabanında görüntüleyin.
5. **Engelli Park Alanları:** Engelli bireylere ayrılmış park alanlarının seçin ve özel takibini yapın.
6. **Veritabanına kaydet** Analiz sonuçlarını bir veritabanı bağlantısı kullanarak bulutta depolayın.

## Uygulama Ana Penceresi

![image alt](https://github.com/YasinEfeee/ParkSpotter/blob/43947c8396f464e87bd02297a8e1635db1595e50/Full_app_with_live_video_and_camera_tracing/In-app%20images/%C5%9Eekil%20main.jpg)

## Uygulama Analizi Örneği

![image alt](https://github.com/YasinEfeee/ParkSpotter/blob/43947c8396f464e87bd02297a8e1635db1595e50/Full_app_with_live_video_and_camera_tracing/In-app%20images/%C5%9Eekil%205.jpg)

## Park Alanı Seçimi

![image alt](https://github.com/YasinEfeee/ParkSpotter/blob/b34d4735ced14b02195b081a865ff75a05e215f7/Full_app_with_live_video_and_camera_tracing/In-app%20images/Parking%20spot%20selecting.jpg)


## Gelecekteki İyileştirmeler

  * Kullanıcı deneyimini geliştirmek ve sistem doğruluğunu artırmak.
  * Yapay zeka modelinin gerçek zamanlı performansını iyileştirmek.
  * Veritabanı işlemlerini daha hızlı yanıt süreleri için optimize etmek.
  * Kullanıcı dostu etkileşim için mobil uygulama sürümüne geçiş yapmak.

## Katkıda Bulunun ve Destek Olun

ParkSpotter projesini daha iyi bir hale getirmek için öneri ve fikirlerinize açığız. Projeye katkıda bulunmak için aşağıdaki yolları kullanabilirsiniz:

- **Hata ve Öneri Bildirimi:** Projeyle ilgili karşılaştığınız sorunları ya da geliştirme önerilerinizi paylaşmak için lütfen bir "issue" açın. Her geri bildirim bizim için çok değerli!
- **Paylaşım:** Projeyi arkadaşlarınızla ve ilgi duyabilecek kişilerle paylaşarak daha geniş bir kitleye ulaşmamıza yardımcı olabilirsiniz.

### İletişim

Daha fazla bilgi almak ya da katkılarınızı paylaşmak için bizimle iletişime geçmekten çekinmeyin. Desteğiniz için şimdiden teşekkür ederiz!



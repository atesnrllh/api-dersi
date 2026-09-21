# Ders İçeriğini Hazırlama Yaklaşımı

**Çıkış noktası:** Öğrenci, yeni terimi açıklanan kodda veya gördüğü sonuçta bulabilmeli. Birinci haftadaki kitap uygulaması, sonraki haftaların anlatım temposu için ölçüttür.

## Önce çalışan örnek, sonra kavramların özeti

1. Önceki uygulamanın son çalışan sürümünü aç; yeni haftanın ihtiyacını bunun üzerinden belirle.
2. Bu ihtiyacı karşılayan en küçük örneği çalıştır. Başlangıç verisini, isteği ve beklenen sonucu doğrula.
3. Uygulama föyünü küçük adımlarla yaz. Her yeni adımın hangi soruyu cevapladığı görülsün.
4. Lecture Notes'u bu uygulamaya dayanarak hazırla. Aynı kodları tekrar tekrar vermek yerine terimleri kısa kod parçaları, görseller ve somut sonuçlarla açıkla.
5. İki belgeyi birlikte kontrol et: alan adları, yollar, örnek veriler ve sonuçlar aynı olmalı. Öğrencinin takıldığı noktalar sonraki düzenlemelerin dayanağıdır.

## Bir uygulama adımında bulunması gerekenler

| Öğe | Öğrencinin bilmesi gereken |
|---|---|
| **Amaç** | Şimdi ne yapıyoruz, önceki örnekle neden yetinmiyoruz? |
| **Başlangıç** | Hangi dosya sürümü ve hangi kayıtlarla başlıyoruz? Sunucu çalışıyor mu? |
| **Değişiklik** | Hangi dosyayı değiştiriyoruz? Değişen Python dosyasının tamamı verilir; önemli yeni satırlar ayrıca açıklanır. |
| **Çalıştırma** | Neyi kaydedip hangi terminalde hangi komutu çalıştırıyoruz? Sunucu değiştiyse yeniden başlatma açıkça yazılır. |
| **Gözlem** | Beklenen durum kodu, yanıt ve veri değişikliği nedir? Kısaltılmış çıktı, “çıktının ilgili kısmı” olarak belirtilir. |
| **Anlam** | Gördüğümüz sonuç hangi kavramı açıklıyor? Başarı veya hata neden oluştu? |

Bir adımın merkezinde tek yeni fikir bulunur. Verinin ulaşması, kaydedilmesi ve geri okunması ayrı ayrı görünür olmalıdır. Yeni davranış önce bilinen araçla gösterilir.

Kodda kullanılan fonksiyon, değişken veya tür tanımı ilk kez geliyorsa görevi bulunduğu yerde açıklanır. Değişiklik kutusu kullanıldığında virgül ve girinti gibi çalışmayı etkileyen ayrıntılar da gösterilir. Salt satır sayısını azaltmak için anlama adımları çıkarılmaz.

## Veri değiştiğinde deneyi yeniden üretmek

Kayıt ekleyen, değiştiren veya silen her adımda **önceki durum ve sonraki durum** belirtilir. Aynı istemciyi yeniden çalıştırmanın etkisi ayrıca gösterilir. Sunucuyu yeniden başlatmak deneyin sonucunu değiştiriyorsa öğrenci bu adımı yapmadan önce nedenini bilmelidir.

## Kapsam ve anlatım

- **Temel, devam ve ek çalışma ayrılır.** Ders süresindeki öncelik ve öğrencinin kendi başına tamamlayacağı bölüm baştan belirtilir. Ek çalışmalar zorunlu bitirme ölçütü değildir.
- **Terim, ihtiyaç duyulduğunda gelir.** Tanımın yanında hangi kodda veya çıktıda görüldüğü gösterilir. İngilizce kod adları ve adresler iki belgede de aynı kalır.
- **Görsel, kodun yerini açıklamalıdır.** Örneğin isteği gönderen HTTPX, uygulamayı çalıştıran Uvicorn ve bizim yazdığımız fonksiyon birbirinden ayırt edilebilmelidir.
- **Bilinen konu yeni amaçla kullanılır.** Daha önce görülen GET veya `422`, yeniden uzun tanımlarla başlamaz; yeni adımda neyi açıkladığı söylenir.
- **Sorular anlamayı kontrol eder.** Her başlığın sonuna soru eklemek zorunlu değildir. Öğrencinin gerçek soruları, belirsiz cümleleri bulmak için kullanılır.

## Tamamlanma kontrolü

Örnekler belirtilen başlangıç durumundan çalıştırılır; önemli başarı ve hata sonuçları doğrulanır. Metindeki açıklama, kodun yaptığı işle eşleşmelidir. Çalışan kod tek başına yeterli değildir: öğrenci ne gönderdiğini, sunucunun ne yaptığını ve yanıtın ne anlattığını açıklayabilmelidir.

Haftalık kapsam [Weekly Course Plan](01_Weekly_Course_Plan.md), araçlar [Technologies and Tools](02_Technologies_and_Tools.md) belgesindedir.

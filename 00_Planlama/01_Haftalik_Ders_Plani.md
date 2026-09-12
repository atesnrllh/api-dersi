# Haftalık Ders Planı

**Ders:** Uygulama Programı Arayüzü (API)  
**Süre:** 14 hafta — haftada **3 ders saati teorik + 2 ders saati uygulama**

| Hafta | Teorik — 3 ders saati | Uygulama — 2 ders saati |
|:---:|---|---|
| **1** | API Kavramları ve Türleri, İstemci–Sunucu Mimarisi ve JSON’a Giriş | VS Code ve Python Ortamı; FastAPI ile Yerel Kitap Sunucusu, HTTPX İstemcisi, GET İstekleri, JSON ve Temel Hata Deneyleri |
| **2** | HTTP İstek–Yanıt Yapısı; Yol, Sorgu ve Gövde; Metot Anlamları, Başlıklar, Durum Kodları ve İstek Tekrarının Etkisi | Aynı Kitap Kataloğunda Postman ile GET; Gövde Modeli, POST ve `Location` Adımlarını Ayrı Kurma; `200`/`201`/`404`/`405`/`422` Deneyleri; HTTPX ile Oluşturma ve Okuma |
| **3** | RESTful API Tasarımı, Kaynaklar, Uç Noktalar ve Yönlendirme | Dönem Projesinin Başlatılması, Projenin İlk GET Uç Noktaları ve Dokümantasyona Giriş |
| **4** | CRUD İşlemleri, İstek Gövdeleri ve Yanıt Modelleri | Bellek İçi Verilerle Listeleme, Ekleme, Güncelleme ve Silme |
| **5** | Veri Doğrulama ve Hata Yönetimi | Doğrulama Kuralları ve Tutarlı Hata Yanıtlarının Oluşturulması |
| **6** | Veri Modelleme, ORM ve Veritabanı Entegrasyonu | Veritabanı Bağlantısı ve CRUD İşlemlerinin Kalıcı Hâle Getirilmesi |
| **7** | API Testleri, Test Otomasyonu ve Hata Ayıklama | Başarılı ve Hatalı İstek Senaryolarının Otomatik Test Edilmesi |
| **8** | **Ara Sınav / Ara Değerlendirme ve Tekrar** | **Uygulamalı Ara Değerlendirme ve Proje Kontrolü** |
| **9** | Kimlik Doğrulama, Token Tabanlı Erişim ve Yetkilendirme | Hazır Kimlik Doğrulama İskeletiyle Korumalı Uç Noktalar ve Kayıt Sahipliği Denetimi |
| **10** | API Güvenliği, Erişim Kontrolü, CORS ve İstek Sınırlama | Yerel Test Ortamında Yetki Denetimleri, Güvenlik Açıklarının Giderilmesi ve Güvenlik Testleri |
| **11** | Yayına Alma, Günlükleme, İzleme ve Ölçeklendirmeye Giriş | Hazırlanmış Test Ortamına İlk Yayın, Günlük Kayıtları ve Sağlık Kontrolü |
| **12** | Harici API Entegrasyonu, Hata Dayanıklılığı ve Redis ile Önbellekleme Temelleri | Harici Servis İsteği ve Hata Yönetimi; Yanıtı Redis'te Önbellekleme, TTL ve Önbelleği Geçersiz Kılma |
| **13** | OpenAPI, API Dokümantasyonu, Versiyonlama ve Geriye Uyumluluk | Kullanım Dokümanının Tamamlanması, Sürüm Karşılaştırması ve Güncel Sürümün Yayınlanması |
| **14** | **Proje Sunumları ve Tasarım Kararlarının Değerlendirilmesi** | **Çalışan Proje Gösterimi, Test Sonuçları ve Bireysel Kod Değerlendirmesi** |

**Uygulama düzeni:** Birinci haftada kavramları görünür kılmak için bellekte veri tutan küçük bir kitap kataloğu sunucusu ve istemcisi geliştirilecek. Bu çalışma dönem projesinin başlangıcı değildir. Üçüncü haftadan itibaren tek dönem projesi geliştirilecek. Otomatik testler yedinci haftadan sonra her yeni özellikle sürdürülecek. Dokümantasyon üçüncü haftada başlayıp on üçüncü haftada tamamlanacak. İlk yayın on birinci haftada yapılacak.

**Konu derinliği:** Birinci hafta `GET`, başlıklar, `200`, `404`, `422`, bağlantı hatası ve basit doğrulama çalışan örnek içinde gözlemlenecek. HTTP kuralları ikinci haftada, veri doğrulama ve tutarlı hata modelleri beşinci haftada sistemli biçimde ele alınacak.

**İkinci haftanın sınırı ve yöntemi:** Birinci haftanın üç kitaplı son sürümü korunarak ilerlenir. Önce aynı GET farklı istemcide kurulur. Yeni kitap için önce gövdenin alınıp geri gösterilmesi, sonra kaydedilmesi ve yeni adresinin bildirilmesi gözlemlenir. Böylece veri göndermekle kayıt oluşturmanın farklı işler olduğu görülür. Python istemcisinde de ham yanıtı görmekle alanları yorumlamak ayrı adımlardır. Aynı isteği tekrarlama ve geçersiz gövde deneyleri, başlangıç verisi ve beklenen sonuç belirtilerek yapılır. PUT/PATCH/DELETE anlamları karşılaştırılır; çalışan güncelleme ve silme uygulamaları dördüncü haftaya aittir. İkinci haftanın model tanımı, beşinci haftadaki ayrıntılı iş kurallarının hazırlığıdır.

**Öğretim düzeni:** Her uygulama adımı ne yapıldığını, neden yapıldığını ve teorideki yerini açıklar; tahmin, çalıştırma ve sonuç yorumlama ile ilerler. Değişen Python dosyası her seferinde tam verilir. Ayrıntılı föyleri iki ders saatine sığdırmak için öğrenme adımları kaldırılmaz; gerektiğinde çalışma sonraki oturumda sürer.

**İçerik hazırlama sırası:** Önceki haftanın uygulaması ders temposunun ölçütüdür. Yeni haftanın önce örneklerle teorisi, ardından uygulaması hazırlanır; son olarak uygulamaya bakılarak teori tekrar denetlenir. Ayrıntılar [ders işleme yaklaşımında](03_Ders_Isleme_Yaklasimi.md) tutulur.

**Takvim notu:** Sekizinci hafta ara değerlendirmeye ayrıldı; kesin sınav tarihine göre yeri değiştirilebilir.

**Materyal hazırlığı:** Bu çizelgeden hareketle her hafta için ayrı teorik ders notu ve uygulama föyü hazırlanacak. Kurulum ve araç kullanım yönergeleri ayrı teknik rehberlerde tutulacak.

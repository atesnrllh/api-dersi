# Haftalık Ders Planı

**Ders:** Uygulama Programı Arayüzü (API)  
**Süre:** 14 hafta — haftada 3 ders saati teori ve 2 ders saati uygulama.

| Hafta | Teoride açıklanacak kavramlar | Uygulama ve beklenen sonuç |
|:---:|---|---|
| **1** | API, istemci–sunucu, HTTP ve JSON; kullanılan araçların görevleri | FastAPI sunucusu ve HTTPX istemcisiyle kitap okuma, arama ve filtreleme. Öğrenci isteğin hangi kodu çalıştırdığını ve gelen yanıtı açıklar. |
| **2** | İstek gövdesi, veri modeli, POST, `200`/`201`, `Location` ve isteği tekrarlama | Aynı kataloğa HTTPX ile kitap gönderme. Önce gövdeyi alıp geri gösterme, sonra yeni kayıt oluşturma; devamında kaydı adresinden okuma ve hatalı gövdeyi deneme. |
| **3** | Kaynak ve işlem tasarımı; REST yaklaşımı; REST, SOAP ve GraphQL'in kısa karşılaştırması | Küçük dönem projesinin ilk işlemlerini seçme. Öğrenilen okuma ve oluşturma işlemlerini projeye aktarma; ilk kullanım örneklerini belgeleme. |
| **4** | CRUD: oluşturma, okuma, güncelleme ve silme; PUT/PATCH farkı; yanıt modelleri | Mevcut işlemlere güncelleme ve silmeyi sırayla ekleme. Öğrenci her isteğin kayıt üzerinde yaptığı değişikliği gösterir. |
| **5** | Alanların türleri, kabul edilen değerler ve hata yanıtları | Mevcut modellere açık kurallar ekleme. Geçerli ve geçersiz değerleri gönderip reddetme nedenini ve dönen hata bilgisini açıklama. |
| **6** | Veriyi kalıcı saklama; tablo, kayıt ve Python modeli ilişkisi | Hazırlanmış PostgreSQL ortamında SQLModel ile küçük veri modelini kaydetme ve okuma. Sunucu yeniden başlayınca kaydın korunduğunu görme; mevcut işlemleri sırayla veritabanına taşıma. |
| **7** | Otomatik test ve hata ayıklama | Başarılı ve hatalı istekleri pytest ile tekrar çalıştırma. Kod değişikliğinin beklenen sonucu bozup bozmadığını testlerle görme. |
| **8** | Ara değerlendirme ve tekrar | Çalışan projeyi, istek–yanıt ilişkisini ve testleri uygulamalı değerlendirme; eksik kalan adımları tamamlama. |
| **9** | Kullanıcıyı tanıma ve işlem yapma izni; token kullanımı | Hazır kimlik doğrulama iskeletiyle bir işlemi koruma. Kullanıcının kimliğini ve kaydın sahibini denetleme. |
| **10** | Erişim denetimi ve temel API güvenliği | Başka kullanıcının kaydına erişme gibi başarısız olması gereken istekleri deneme; erişim hatalarını düzeltip test etme. |
| **11** | Yayına alma, çalışma ayarları, günlük kayıtları ve sağlık kontrolü | Hazırlanmış test ortamına ilk yayını yapma. Uygulamanın erişilebilir olduğunu kontrol etme ve bir isteğin kaydını inceleme. |
| **12** | Harici API kullanımı; yanıt alınamadığında uygulamanın davranışı; önbellek fikri | HTTPX ile başka bir servisten veri alma; cevap gelmediğinde kontrollü sonuç üretme. Ek çalışmada hazırlanmış Redis ortamıyla bir okuma sonucunu geçici saklama. |
| **13** | API dokümantasyonu, sürüm değişikliği ve eski istemcilerle uyum | Kullanım belgesini tamamlama. Bir yanıt değişikliğinin istemciyi nasıl etkilediğini karşılaştırma; güncel sürümü test edip yayımlama. |
| **14** | Proje sunumları ve tasarım kararları | Çalışan işlemleri, testleri ve hata durumlarını gösterme; her öğrencinin kendi kodunu açıklaması. |

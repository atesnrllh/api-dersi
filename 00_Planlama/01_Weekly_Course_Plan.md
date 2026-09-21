# Haftalık Ders Planı

**Ders:** Uygulama Programı Arayüzü (API)  
**Süre:** 14 hafta — haftada 3 ders saati teori ve 2 ders saati uygulama.

İlk iki hafta aynı kitap kataloğuyla çalışılır. Üçüncü haftada küçük bir dönem projesi başlatılır; sonraki haftalarda bu proje geliştirilir. Bir konunun örnekte görülmesi ile öğrencinin onu kendi başına uygulayabilmesi ayrı değerlendirilir.

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

## İkinci haftanın sınırı

[İkinci hafta Practice](../02_Haftalik_Materyaller/Hafta_02/02_Practice.md), birinci haftanın üç kitaplı son sürümünden devam eder. `/book` yolları, kitap alanları, Python ortamı ve `server.py`/`client.py` dosyaları korunur.

| Çalışma | Kapsam |
|---|---|
| **Temel — Deney 1–3** | GET isteğini doğrulama; JSON gövdesini alıp kaydetmeden `200` ile geri gösterme; ardından kitabı listeye ekleyip `201` döndürme. |
| **Yönlendirilmiş devam — Deney 4–6** | `Location` başlığındaki yeni adresi GET ile okuma; `title` gönderilmediğinde `422` alıp kayıt eklenmediğini görme; aynı POST isteğini tekrarlayıp iki kayıt oluştuğunu ve sunucu yeniden başlatılınca eklenen kayıtların kaybolduğunu gözlemleme. |
| **İsteğe bağlı ek çalışma** | Aynı isteği Postman ile gönderme; desteklenmeyen bir metot için `405` yanıtını kısaca karşılaştırma. |

İki uygulama saatinin önceliği Deney 1–3'tür. Deney 4–6, süreye göre sınıfta veya yönlendirilmiş bireysel çalışmada tamamlanır. Ek çalışmalar zorunlu bitirme ölçütü değildir.

Güncelleme ve silme kodları dördüncü haftaya; alanlara ayrıntılı değer sınırları koymak ve hata yanıtlarını düzenlemek beşinci haftaya bırakılır.

## Kapsam notları

- SOAP ve GraphQL için ayrı sunucu kurulmaz. CORS, istek sınırlama ve ölçeklendirme ek örneklerle tanıtılabilir; ayrı bir ön yüz projesi eklenmez.
- Altıncı haftada küçük veri modeli ve hazır veritabanı ortamı kullanılır. Redis ek çalışması, tek bir yanıtın geçici saklanması, süresinin dolması ve silinmesiyle sınırlıdır.
- Dokümantasyon üçüncü haftadan, otomatik testler yedinci haftadan itibaren yeni özelliklerle sürer. Ara değerlendirme kurumun sınav takvimine göre kaydırılabilir.

Araç seçimi [Technologies and Tools](02_Technologies_and_Tools.md), materyal hazırlama yöntemi [Teaching Approach](03_Teaching_Approach.md) belgesindedir.

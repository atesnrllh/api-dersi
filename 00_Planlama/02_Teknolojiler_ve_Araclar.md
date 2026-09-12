# Kullanılacak Teknolojiler ve Araçlar

**Ana yapı: Python + FastAPI + PostgreSQL**

| İşlev | Seçilen araç | Dersteki kullanım amacı |
|---|---|---|
| **Programlama dili** | **Python 3** | API’nin uygulama mantığını, veri işlemlerini ve erişim kontrollerini yazmak. |
| **API geliştirme çatısı** | **FastAPI** | Uç noktaları, istek–yanıt modellerini ve API işlemlerini oluşturmak. |
| **Veri modelleri ve gövde doğrulama** | **Pydantic** | İkinci haftada POST gövdesinin beklenen alanlarını tanımlamak; beşinci haftada ayrıntılı tür ve iş kuralı doğrulaması yapmak. |
| **Ana veritabanı** | **PostgreSQL** | Dönem projesindeki kayıtları kalıcı olarak saklamak ve ilişkisel veri yapılarıyla çalışmak. |
| **Veritabanı erişimi / ORM** | **SQLModel** | Python modellerini veritabanı tablolarıyla ilişkilendirmek ve veri işlemlerini uygulama içinden yürütmek. |
| **Önbellekleme** | **Redis** | Sık okunan verileri geçici olarak saklamak; önbellekten okuma, süre dolması (TTL) ve veri değiştiğinde önbelleği silme veya güncelleme davranışlarını öğrenmek. |
| **Kod editörü ve hata ayıklama** | **VS Code + Python eklentisi** | İlk haftadan başlayarak dosyaları ve iki terminali birlikte yönetmek; kodu çalıştırmak ve hataları incelemek. |
| **Elle API denemesi** | **Postman + curl** | Postman ile ikinci haftadan itibaren metotları, başlıkları ve gövdeleri değiştirerek istek hazırlamak; curl ile terminalden kısa HTTP kontrolleri yapmak. |
| **Otomatik test** | **pytest + FastAPI TestClient** | Başarılı işlemleri, hatalı girdileri ve yetkisiz erişimleri tekrar çalıştırılabilir testlerle kontrol etmek. |
| **HTTP istemcisi ve harici entegrasyon** | **HTTPX** | İlk hafta GET gönderen `client.py`, ikinci hafta POST gönderen `create_book.py` ile kendi FastAPI sunucumuzu kullanmak; ilerleyen haftalarda harici API isteklerini ve bağlantı durumlarını yönetmek. |
| **Veritabanını inceleme ve sorgulama** | **pgAdmin** | Tabloları ve kayıtları incelemek, temel SQL sorguları çalıştırmak. |
| **API tanımı ve dokümantasyon** | **OpenAPI + Swagger UI** | API işlemlerini, veri modellerini ve kullanım biçimini belgelemek; etkileşimli dokümantasyon üzerinden denemek. |
| **Sürüm takibi ve proje paylaşımı** | **Git + GitHub** | Haftalık kod değişikliklerini kaydetmek, önceki sürümlere dönmek ve proje teslimlerini paylaşmak. |
| **Paket ve çalışma ortamı yönetimi** | **venv + uv** | Projeye özel `api-env` sanal ortamını ayırmak ve paketleri bu ortama kurmak. |
| **Uygulama sunucusu** | **Uvicorn** | İlk haftadan başlayarak FastAPI uygulamasını çalıştırmak ve gelen HTTP isteklerini karşılamak. |

**Teknik kapsam:** Ana uygulama dili Python olacak; veritabanı çalışmaları için temel SQL de kullanılacak. PostgreSQL ana veritabanı olarak kalacak; dönem içinde zorunlu bir veritabanı değişikliği yapılmayacak. Redis, PostgreSQL'in yerine değil, seçilmiş okuma işlemlerinde geçici önbellek olarak kullanılacak. Ayrı bir ön yüz geliştirme çatısı eklenmeyecek.

**İlk üç haftadaki araç akışı:** Birinci hafta VS Code, `venv`, uv, FastAPI, Uvicorn ve HTTPX ile çalışan yerel örnek kurulur. İkinci hafta aynı GET isteği Postman'da hazırlanır; FastAPI ile gelen Pydantic'in gövde modeli açıkça tanıtılır. POST önce Postman, sonra HTTPX ile gönderilir. curl gerektiğinde kısa kontroller için yardımcıdır; ikinci hafta föyünde zorunlu ayrı bir istemci deneyine dönüştürülmez. Üçüncü hafta bu temel, dönem projesinin tasarlanmış uç noktalarına aktarılır.

**Hazırlık düzeni:** Kurulum ve araç kullanım yönergeleri ayrı teknik rehberlerde tutulacak. Öğrencilere dağıtılacak ortamın sürümleri kurulum hazırlığında belirlenip sabitlenecek.

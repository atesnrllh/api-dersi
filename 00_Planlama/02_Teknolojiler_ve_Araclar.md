# Kullanılacak Teknolojiler ve Araçlar

**Ana yapı: Python + FastAPI + PostgreSQL**

| İşlev | Seçilen araç | Dersteki kullanım amacı |
|---|---|---|
| **Programlama dili** | **Python 3** | API’nin uygulama mantığını, veri işlemlerini ve erişim kontrollerini yazmak. |
| **API geliştirme çatısı** | **FastAPI** | Uç noktaları, istek–yanıt modellerini ve API işlemlerini oluşturmak. |
| **Ana veritabanı** | **PostgreSQL** | Dönem projesindeki kayıtları kalıcı olarak saklamak ve ilişkisel veri yapılarıyla çalışmak. |
| **Veritabanı erişimi / ORM** | **SQLModel** | Python modellerini veritabanı tablolarıyla ilişkilendirmek ve veri işlemlerini uygulama içinden yürütmek. |
| **Önbellekleme** | **Redis** | Sık okunan verileri geçici olarak saklamak; önbellekten okuma, süre dolması (TTL) ve veri değiştiğinde önbelleği silme veya güncelleme davranışlarını öğrenmek. |
| **Kod editörü ve hata ayıklama** | **VS Code + Python eklentisi** | Kod yazmak, uygulamayı çalıştırmak ve hataları incelemek. |
| **Elle API denemesi** | **Postman** | İstek hazırlamak; metotları, başlıkları ve gövdeleri değiştirmek; yanıtları incelemek. |
| **Otomatik test** | **pytest + FastAPI TestClient** | Başarılı işlemleri, hatalı girdileri ve yetkisiz erişimleri tekrar çalıştırılabilir testlerle kontrol etmek. |
| **HTTP istemcisi ve harici entegrasyon** | **HTTPX** | Uygulama içinden başka API’lere istek göndermek ve zaman aşımı gibi bağlantı durumlarını yönetmek. |
| **Veritabanını inceleme ve sorgulama** | **pgAdmin** | Tabloları ve kayıtları incelemek, temel SQL sorguları çalıştırmak. |
| **API tanımı ve dokümantasyon** | **OpenAPI + Swagger UI** | API işlemlerini, veri modellerini ve kullanım biçimini belgelemek; etkileşimli dokümantasyon üzerinden denemek. |
| **Sürüm takibi ve proje paylaşımı** | **Git + GitHub** | Haftalık kod değişikliklerini kaydetmek, önceki sürümlere dönmek ve proje teslimlerini paylaşmak. |
| **Paket ve çalışma ortamı yönetimi** | **uv** | Projenin bağımlılıklarını ve çalışma ortamını yönetmek; sınıfta tutarlı kurulum kullanmak. |
| **Uygulama sunucusu** | **Uvicorn** | FastAPI uygulamasını çalıştırmak ve gelen HTTP isteklerini karşılamak. |

**Teknik kapsam:** Ana uygulama dili Python olacak; veritabanı çalışmaları için temel SQL de kullanılacak. PostgreSQL ana veritabanı olarak kalacak; dönem içinde zorunlu bir veritabanı değişikliği yapılmayacak. Redis, PostgreSQL'in yerine değil, seçilmiş okuma işlemlerinde geçici önbellek olarak kullanılacak. Ayrı bir ön yüz geliştirme çatısı eklenmeyecek.

**Hazırlık düzeni:** Kurulum ve araç kullanım yönergeleri ayrı teknik rehberlerde tutulacak. Öğrencilere dağıtılacak ortamın sürümleri kurulum hazırlığında belirlenip sabitlenecek.

# Kullanılacak Teknolojiler ve Araçlar

**Ana yapı:** Python + FastAPI + PostgreSQL

| İşlev | Seçilen araç | Dersteki kullanım amacı |
|---|---|---|
| **Programlama dili** | **Python 3.10 veya üzeri** | Sunucu ve istemci kodunu, veri işlemlerini ve erişim kontrollerini yazmak. |
| **API geliştirme** | **FastAPI** | API işlemlerini tanımlamak, gelen HTTP isteklerini ilgili fonksiyonlarla karşılamak ve yanıt hazırlamak. |
| **Uygulama sunucusu** | **Uvicorn** | FastAPI uygulamasını çalıştırmak ve HTTP bağlantılarını kabul etmek. |
| **Veri modelleri ve doğrulama** | **Pydantic 2** | Verinin alanlarını, türlerini ve kabul edilecek değerlerini tanımlamak; gelen bilgileri bu kurallara göre kontrol etmek. |
| **HTTP istemcisi ve harici API kullanımı** | **HTTPX** | Python kodundan kendi sunucumuza veya harici API'lere istek göndermek; yanıtları ve bağlantı hatalarını işlemek. |
| **Elle API denemesi** | **Postman + curl** | Metot, adres, başlık ve gövdeyi belirleyerek HTTP istekleri göndermek ve yanıtları incelemek. |
| **Kalıcı veri saklama** | **PostgreSQL** | Uygulamanın kayıtlarını kalıcı olarak saklamak ve ilişkili verilerle çalışmak. |
| **Veritabanı erişimi / ORM** | **SQLModel** | Python modellerini veritabanı tablolarıyla ilişkilendirmek; kayıt ekleme, okuma, güncelleme ve silme işlemlerini yapmak. |
| **Veritabanını inceleme ve sorgulama** | **pgAdmin** | Tabloları ve kayıtları incelemek, SQL sorguları çalıştırmak. |
| **Önbellekleme** | **Redis** | Sık kullanılan verileri geçici saklamak; saklama süresini ve veri değiştiğinde önbelleğin yenilenmesini öğrenmek. |
| **Otomatik test** | **pytest + FastAPI TestClient** | Başarılı işlemleri, hatalı girdileri ve yetkisiz erişimleri tekrar çalıştırılabilir testlerle kontrol etmek. |
| **API tanımı ve dokümantasyon** | **OpenAPI + Swagger UI** | API işlemlerini ve veri modellerini belgelemek; etkileşimli dokümantasyon üzerinden istekleri denemek. |
| **Sürüm takibi ve proje paylaşımı** | **Git + GitHub** | Kod değişikliklerini kaydetmek, önceki sürümlere dönmek ve projeyi paylaşmak. |
| **Kod editörü ve hata ayıklama** | **VS Code + Python eklentisi** | Dosyaları düzenlemek, programları çalıştırmak ve hataları incelemek. |
| **Paket ve çalışma ortamı yönetimi** | **venv + uv** | Projeye özel Python ortamı oluşturmak ve paketleri bu ortama kurmak. |

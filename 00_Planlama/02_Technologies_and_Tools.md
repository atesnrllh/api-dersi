# Kullanılacak Teknolojiler ve Araçlar

**Ana yapı:** Python + FastAPI + PostgreSQL. Araçlar ihtiyaç duyuldukları haftada tanıtılır; hepsi ilk derste kurulup öğretilmez.

## İlk iki haftada kullanılanlar

| Araç | Görevi |
|---|---|
| **Python 3.10 veya üzeri** | Sunucu ve istemci kodunu yazmak ve çalıştırmak. |
| **VS Code + Python eklentisi** | Dosyaları düzenlemek; sunucu ve istemciyi iki terminalde çalıştırmak. |
| **venv + uv** | Projeye özel `api-env` Python ortamını kullanmak ve paketleri bu ortama kurmak. |
| **FastAPI** | Gelen HTTP isteğini yazdığımız fonksiyonla ilişkilendirmek ve yanıt hazırlamak. |
| **Uvicorn** | FastAPI uygulamasını çalıştırıp HTTP bağlantılarını kabul etmek. |
| **HTTPX** | `client.py` içinden önce GET, ikinci haftada POST göndermek ve yanıtı incelemek. |
| **Pydantic 2** | İstek gövdesinin beklenen alanlarını ve türlerini tanımlamak. |

İlk iki haftada aynı ortam, `server.py` ve `client.py` kullanılır. HTTPX ana istemcidir.

## Dönem projesinde eklenecekler

| Araç | Ne zaman ve ne için? |
|---|---|
| **Git + GitHub** | Üçüncü haftadan itibaren proje değişikliklerini kaydetmek ve çalışmayı paylaşmak. |
| **OpenAPI + Swagger UI** | Üçüncü haftadan itibaren API işlemlerini ve modellerini incelemek; kullanım belgesini dönem boyunca geliştirmek. |
| **PostgreSQL** | Altıncı haftadan itibaren proje kayıtlarını sunucu kapansa da korumak. Ana veritabanı dönem içinde değiştirilmez. |
| **[SQLModel](https://sqlmodel.tiangolo.com/)** | Python modelleriyle veritabanındaki kayıtlar arasında çalışmak; mevcut ekleme, okuma, güncelleme ve silme işlemlerini veritabanına taşımak. |
| **pytest + FastAPI TestClient** | Yedinci haftadan itibaren başarılı ve hatalı istekleri otomatik olarak kontrol etmek. |

## Yardımcı araçlar ve ek çalışmalar

- **Postman:** İkinci haftanın sonunda bilinen isteği farklı bir araçla gönderme; isteğe bağlı.
- **curl:** Gerektiğinde terminalden kısa HTTP kontrolü.
- **pgAdmin:** Veritabanındaki tablo ve kayıtları görsel olarak inceleme.
- **Redis:** On ikinci haftada hazır ortamla geçici önbellek örneği. Kalıcı kayıtlar PostgreSQL'de kalır.

## Ortam hazırlığı

Veritabanı, kimlik doğrulama ve yayın için gerekli ortam önceden hazırlanır; verilen hazır kodun görevi açıklanır. Paket sürümleri, örnekler birlikte doğrulandıktan sonra sabitlenir. Kurulum ayrıntıları rehberlerde, kullanılacak komutlar uygulama föyünde yer alır. Haftalık sıra [Weekly Course Plan](01_Weekly_Course_Plan.md) belgesindedir.

# Hafta 07 — Uygulama Föyü

## 0. Sunucuyu kim kontrol ediyor?

Şimdiye kadar her deneyde aynı şeyi yaptık: Sunucuyu başlattık, bir istemci çalıştırdık ve çıktıyı föydekiyle gözle karşılaştırdık. Hafta 6'da kitapları veritabanına taşıdıktan sonra API'nin bozulmadığından emin olmak için Hafta 5'in yedi istemcisini tek tek yeniden çalıştırmak gerekirdi.

Bu yolun iki zayıf yanı var: Yavaş, ve uzun bir çıktıda bir sayının değiştiğini gözden kaçırmak kolay. Bu hafta bu kontrolü koda yazacağız. Bir **test**, bir istek gönderen ve yanıtın beklediğimiz gibi olup olmadığını kendisi kontrol eden küçük bir fonksiyondur. Testleri **pytest** adlı araç çalıştırır ve hangilerinin geçip hangilerinin kaldığını söyler.

Haftanın sonunda şu soruya cevap verebileceksin: **Kodda yaptığım bir değişikliğin bir şeyi bozup bozmadığını nasıl anlarım; bozduysa hatanın yerini nasıl bulurum?**

Bu hafta sırasıyla şunları yapacağız:

- **Deney 1:** İlk testi yazmak, çalıştırmak ve kalan bir testin çıktısını okumak
- **Deney 2:** Başarılı ve hatalı istekleri test etmek; testlerin birbirini etkilememesini sağlamak
- **Deney 3:** Bir kod değişikliğinin bozduğu işlemi testle yakalamak ve uzun hata çıktısını okumak
- **Deney 4:** Hata vermeden yanlış sonuç üreten bir değişikliğin yerini adım adım bulmak
- **Deney 5** (ödev): Veritabanına doğrudan bakan bir test yazmak

### 0.1 Başlangıç dosyaları

Hafta 6'nın sonundaki dosyalarla başla:

| Dosya | Hafta 6 föyündeki yeri |
|---|---|
| `server.py` | 7.3 bölümü. Bu hafta değişmeyecek. |
| `database.py` | 7.1 bölümü. Deney 1'de bir fonksiyon ekleyeceğiz. |
| `reset_db.py` | 7.2 bölümü. Deney 1'de kısalacak. |

Kendi dosyalarından emin değilsen bu haftanın başlangıç dosyalarını kullan: [server.py](Starting_Code/server.py), [database.py](Starting_Code/database.py), [reset_db.py](Starting_Code/reset_db.py). Föydeki çıktılar bu dosyalarla alındı.

Bu hafta `client.py` dosyasını kullanmayacağız; istekleri testler gönderecek. Yeni dosyamız `test_server.py` olacak.

### 0.2 Veritabanını başlat ve paketleri kur

Testler veritabanını kullanıyor; Hafta 6'daki kapsayıcının çalıştığından emin ol:

```bash
docker start book-db
```

Sanal ortam etkinken iki paket kur:

```bash
uv pip install pytest httpx2
```

| Paket | Görevi |
|---|---|
| **pytest** | Test fonksiyonlarını bulur, çalıştırır ve sonuçları raporlar. |
| **httpx2** | FastAPI'nin test aracı `TestClient`, istekleri göndermek için bu paketi kullanır. `httpx2`, Hafta 1'den beri kullandığımız HTTPX'in devamıdır: Pydantic ekibi HTTPX'in bakımını bu adla sürdürüyor ve kullanımı aynı. Kurulmazsa testler eski `httpx` ile yine çalışır, ama her çalıştırmada `install httpx2 instead` diyen bir uyarı görünür. |

Kurulumu kontrol et:

```bash
python -m pytest --version
```

Çıktı `pytest 9.2.0` gibi bir sürüm göstermeli. Föydeki çıktılar pytest 9.2.0 ile alındı.

> **Sunucuyu başlatmana gerek yok:** Bu hafta testleri çalıştırırken `uvicorn` ile sunucu başlatmıyoruz. Nedenini Deney 1'de göreceğiz. Veritabanı ise çalışıyor olmalı.

---

## Deney 1 — İlk test

**Amaç:** Tek bir isteği kontrol eden bir test yazmak, pytest ile çalıştırmak ve kalan bir testin çıktısını okumak.

### 1.1 Sıfırlamayı bir fonksiyona taşı

Hafta 6'da her deneyden önce `python reset_db.py` ile veritabanını başlangıç hâline getiriyorduk. Testler de her seferinde aynı başlangıç hâlinden yola çıkmalı. Ama bir test, `reset_db.py` dosyasını bir komut gibi çalıştıramaz; bunun için sıfırlama kodunun, istediğimiz an çağırabileceğimiz bir fonksiyon olması gerekir.

`database.py` dosyasında import satırlarını değiştir:

| Eski satır | Yeni satır |
|---|---|
| `from sqlalchemy import Column` | `from sqlalchemy import Column, text` |
| `from sqlmodel import Field, SQLModel, create_engine` | `from sqlmodel import Field, Session, SQLModel, create_engine` |

`database.py` dosyasının sonuna şu fonksiyonu ekle. İçeriği, `reset_db.py` dosyasındaki kodun bir fonksiyonun içine taşınmış hâlidir:

```python
# Veritabanını başlangıç hâline getirir: tabloları siler, yeniden oluşturur ve başlangıç kayıtlarını yazar.
def reset_database():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(Book(
            id=42,
            title="API Yolculuğu",
            author={"first_name": "Deniz", "last_name": "Kaya"},
            available=True,
            tags=["software", "education"],
            rating=None,
            internal_note="Kapağı yıpranmış, yenisi sipariş edildi.",
        ))
        session.add(Book(
            id=57,
            title="Veriyle İlk Adımlar",
            author={"first_name": "Ece", "last_name": "Yılmaz"},
            available=False,
            tags=[],
            rating=0,
        ))
        session.add(Book(
            id=73,
            title="Python ile Web API",
            author={"first_name": "Can", "last_name": "Demir"},
            available=True,
            tags=["python", "api"],
            rating=4.5,
        ))
        session.add(Review(
            id=1,
            book_id=42,
            reader="Ece",
            comment="Konuları örneklerle anlatıyor.",
            score=5,
        ))
        session.commit()

        # Kimlik sayaçlarını en büyük kimliğe getir: yeni kitabın kimliği 74, yeni yorumunki 2 olsun.
        session.execute(text("SELECT setval(pg_get_serial_sequence('book', 'id'), (SELECT MAX(id) FROM book))"))
        session.execute(text("SELECT setval(pg_get_serial_sequence('review', 'id'), (SELECT MAX(id) FROM review))"))
        session.commit()
```

`reset_db.py` dosyasının içeriğini şununla değiştir:

```python
from database import reset_database

reset_database()
print("Database reset: 3 books, 1 review")
```

Program aynı işi yapıyor, ama işin kendisi artık `database.py` dosyasındaki fonksiyonda. Çalıştır:

```bash
python reset_db.py
```

```text
Database reset: 3 books, 1 review
```

### 1.2 `test_server.py`

`server.py` ile aynı klasörde `test_server.py` adlı bir dosya oluştur:

```python
from fastapi.testclient import TestClient

from database import reset_database
from server import app

client = TestClient(app)


# Tek kitap: 42 numaralı kitap okunabilmeli.
def test_get_book():
    reset_database()

    response = client.get("/books/42")

    assert response.status_code == 200
    assert response.json()["title"] == "API Yolculuğu"
```

| Kod | Ne yapar? |
|---|---|
| `from server import app` | `server.py` dosyamızdaki FastAPI uygulamasını alır. |
| `client = TestClient(app)` | Bu uygulamaya istek gönderecek bir test istemcisi oluşturur. `TestClient`, isteği ağ üzerinden değil, doğrudan uygulamaya iletir; bu yüzden `uvicorn` ile sunucu başlatmaya gerek yok. |
| `def test_get_book():` | Bir test fonksiyonu. pytest, adı `test_` ile başlayan dosyalardaki, adı `test_` ile başlayan fonksiyonları kendisi bulur ve çalıştırır. |
| `reset_database()` | Test, veritabanını başlangıç hâline getirerek başlar. |
| `client.get("/books/42")` | `httpx.get(base_url + "/books/42")` gibi bir `GET` isteği gönderir. Adresin başını yazmaya gerek yok; istek doğrudan `app` uygulamasına gidiyor. Yanıt, Hafta 1'den beri kullandığımız `response` nesnesiyle aynı biçimde okunur. |
| `assert response.status_code == 200` | Bir **iddia (assertion)**: "Durum kodu 200 olmalı." Python'un `assert` ifadesi, yanındaki koşul doğruysa hiçbir şey yapmaz; yanlışsa bir hata verir ve test orada **kalır**. |
| `assert response.json()["title"] == "API Yolculuğu"` | İkinci iddia: Kitabın adı bu olmalı. Bir testte birden fazla `assert` olabilir; testin geçmesi için hepsinin doğru olması gerekir. |

Bir testin üç bölümü var: hazırlık (`reset_database()`), istek (`client.get(...)`) ve kontrol (`assert`). Bölümleri boş satırlarla ayırdık.

Testi, `server.py` ile aynı klasördeyken çalıştır:

```bash
python -m pytest
```

```text
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.2.0, pluggy-1.7.0
rootdir: /mnt/c/Users/MONSTER/Desktop/book-catalog-api
plugins: anyio-4.16.0
collected 1 item

test_server.py .                                                         [100%]

============================== 1 passed in 1.43s ===============================
```

| Çıktıdaki satır | Anlamı |
|---|---|
| `test session starts` | pytest çalışmaya başladı. |
| `platform linux -- Python 3.10.12, ...` | İşletim sistemi ve sürümler. Senin bilgisayarında farklı olabilir. |
| `rootdir: ...` | pytest'in testleri aradığı klasör. Senin klasörünün yolu görünür. |
| `plugins: anyio-4.16.0` | pytest'e eklenen yardımcı paketler; FastAPI ile birlikte kurulmuş olanlar burada görünür. |
| `collected 1 item` | Bir test buldu. |
| `test_server.py .` | Dosyadaki her test için bir işaret: `.` geçen bir test demektir. |
| `1 passed in 1.43s` | Sonuç: Bir test geçti. Süre her çalıştırmada biraz farklı olur. |

### 1.3 Testi bilerek boz

Bir test ancak kalabildiği zaman işe yarar. Ne olduğunu görmek için beklenen adı bilerek yanlış yazalım. Son satırdaki `"API Yolculuğu"` yazımını `"API Yolculugu"` yap (ğ yerine g) ve testi tekrar çalıştır:

```text
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.2.0, pluggy-1.7.0
rootdir: /mnt/c/Users/MONSTER/Desktop/book-catalog-api
plugins: anyio-4.16.0
collected 1 item

test_server.py F                                                         [100%]

=================================== FAILURES ===================================
________________________________ test_get_book _________________________________

    def test_get_book():
        reset_database()

        response = client.get("/books/42")

        assert response.status_code == 200
>       assert response.json()["title"] == "API Yolculugu"
E       AssertionError: assert 'API Yolculuğu' == 'API Yolculugu'
E
E         - API Yolculugu
E         ?            ^
E         + API Yolculuğu
E         ?            ^

test_server.py:16: AssertionError
=========================== short test summary info ============================
FAILED test_server.py::test_get_book - AssertionError: assert 'API Yolculuğu'...
============================== 1 failed in 1.47s ===============================
```

| Çıktıdaki bölüm | Anlamı |
|---|---|
| `test_server.py F` | `F` kalan bir test demektir (*failed*). |
| `FAILURES` ve altındaki `test_get_book` | Kalan her testin ayrıntısı. pytest testin kodunu gösterir. |
| `>` ile başlayan satır | Testin kaldığı satır: Bu `assert` doğru değildi. |
| `E   AssertionError: assert 'API Yolculuğu' == 'API Yolculugu'` | `E` ile başlayan satırlar hatayı anlatır. pytest, karşılaştırmanın iki yanındaki gerçek değerleri yazar: Solda yanıttan gelen ad, sağda bizim beklediğimiz ad. |
| `- API Yolculugu` ve `+ API Yolculuğu` | İki değerin farkı: `-` satırı karşılaştırmanın sağındaki, yani beklediğimiz değer; `+` satırı solundaki, yani gerçekte gelen değer. `^` işareti farklı olan harfi gösterir. |
| `test_server.py:16: AssertionError` | Hatanın dosyası ve satır numarası: `test_server.py` dosyasının 16. satırı |
| `FAILED test_server.py::test_get_book - ...` | Kalan testlerin kısa listesi. Çok sayıda test olduğunda önce buraya bakılır. |
| `1 failed` | Sonuç: Bir test kaldı. |

Bu sefer kalan test bir hata bulmadı; testin kendisi yanlıştı. Bir test kaldığında iki olasılık vardır: Ya kod beklediğimiz gibi çalışmıyor ya da beklentimiz yanlış. Çıktı ikisini ayırmaz; hangisi olduğuna değerlere bakarak biz karar veririz.

`"API Yolculugu"` yazımını `"API Yolculuğu"` olarak düzelt ve testin yeniden geçtiğini gör.

> **Ana fikir:** Bir test, bir istek gönderip yanıtı `assert` ile kontrol eden bir fonksiyondur. `TestClient` isteği sunucu başlatmadan doğrudan uygulamaya iletir. pytest, `test_` ile başlayan fonksiyonları bulup çalıştırır; kalan bir testte beklenen ve gelen değeri yan yana gösterir.

---

## Deney 2 — Başarılı ve hatalı istekler

**Amaç:** Önceki haftalarda gözle kontrol ettiğimiz davranışları testlere çevirmek ve testlerin birbirini etkilemesini önlemek.

### 2.1 Sekiz test daha

`test_server.py` dosyasında `client = TestClient(app)` satırının altına, testlerde kullanacağımız kitabı ekle:

```python
new_book = {
    "title": "Test Kitabı",
    "author": {
        "first_name": "Ada",
        "last_name": "Yıldız"
    },
    "available": True,
    "tags": []
}
```

`test_get_book` fonksiyonunun altına şu sekiz testi ekle. Her biri, `test_get_book` gibi `reset_database()` ile başlıyor:

```python
# Olmayan kitap: 404 ve açıklaması.
def test_get_missing_book():
    reset_database()

    response = client.get("/books/43")

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}


# Yeni kitap: 201, Location başlığı ve o adresten okunabilen kitap.
def test_create_book():
    reset_database()

    response = client.post("/books", json=new_book)

    assert response.status_code == 201
    assert response.headers["Location"] == "/books/74"

    response = client.get("/books/74")
    assert response.json()["title"] == "Test Kitabı"


# Arama: büyük ve küçük harfi ayırmaz, sonuçlar kimlik sırasıyla gelir.
def test_search_books():
    reset_database()

    response = client.get("/books", params={"search": "api"})

    ids = []
    for book in response.json():
        ids.append(book["id"])
    assert ids == [42, 73]


# Hatalı puan: 422 ve hatanın yeri.
def test_rating_out_of_range():
    reset_database()

    book = new_book.copy()
    book["rating"] = 7

    response = client.post("/books", json=book)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "rating"]


# Negatif kimlik: yol parametresinin kuralı.
def test_negative_book_id():
    reset_database()

    response = client.get("/books/-5")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "book_id"]


# PATCH: yalnızca gönderilen alan değişir.
def test_patch_rating():
    reset_database()

    response = client.patch("/books/57", json={"rating": 3})

    assert response.status_code == 200
    assert response.json()["rating"] == 3
    assert response.json()["title"] == "Veriyle İlk Adımlar"


# PATCH: ad null olamaz; istek reddedilir ve kitap değişmez.
def test_patch_null_title():
    reset_database()

    response = client.patch("/books/42", json={"title": None})
    assert response.status_code == 422

    response = client.get("/books/42")
    assert response.json()["title"] == "API Yolculuğu"


# Yorum: aynı okur aynı kitaba ikinci kez yorum yazamaz.
def test_second_review_conflict():
    reset_database()

    review = {"reader": "Ece", "comment": "Tekrar okudum.", "score": 4}

    response = client.post("/books/42/reviews", json=review)

    assert response.status_code == 409
```

Her test, önceki haftalarda bir istemciyle denediğimiz bir davranışı kontrol ediyor:

| Test | Neyi kontrol ediyor? | İlk gördüğümüz yer |
|---|---|---|
| `test_get_missing_book` | Olmayan kitap `404` alır. | Hafta 1 |
| `test_create_book` | Yeni kitap `201` alır, `Location` başlığı kitabın adresini verir ve kitap o adresten okunur. | Hafta 2 |
| `test_search_books` | `api` araması, adında `API` geçen iki kitabı kimlik sırasıyla bulur. | Hafta 1, Hafta 6 |
| `test_rating_out_of_range` | Puanı 7 olan kitap `422` alır ve hatanın yeri `['body', 'rating']` olur. `new_book.copy()`, ortak kitabı bozmadan bir kopyasını değiştirir (Hafta 5, Deney 1). | Hafta 5 |
| `test_negative_book_id` | `/books/-5` adresi `422` alır; hata yol parametresinde. | Hafta 5 |
| `test_patch_rating` | `PATCH` yalnızca puanı değiştirir, ad olduğu gibi kalır. `3` ile `3.0` Python'da eşit sayılır. | Hafta 4 |
| `test_patch_null_title` | Ada `null` gönderen `PATCH` reddedilir ve kitabın adı değişmez. Testin ikinci isteği, kitabın gerçekten bozulmadığını kontrol ediyor. | Hafta 5 |
| `test_second_review_conflict` | Ece'nin 42 numaralı kitaba ikinci yorumu `409` alır. | Hafta 5 |

Testleri çalıştır. Bu kez `-v` seçeneğiyle: Her testin adı ayrı bir satırda görünür.

```bash
python -m pytest -v
```

Başlıktaki satırları bundan sonra göstermiyoruz:

```text
collecting ... collected 9 items

test_server.py::test_get_book PASSED                                     [ 11%]
test_server.py::test_get_missing_book PASSED                             [ 22%]
test_server.py::test_create_book PASSED                                  [ 33%]
test_server.py::test_search_books PASSED                                 [ 44%]
test_server.py::test_rating_out_of_range PASSED                          [ 55%]
test_server.py::test_negative_book_id PASSED                             [ 66%]
test_server.py::test_patch_rating PASSED                                 [ 77%]
test_server.py::test_patch_null_title PASSED                             [ 88%]
test_server.py::test_second_review_conflict PASSED                       [100%]

============================== 9 passed in 1.89s ===============================
```

Dokuz test iki saniyede çalıştı. Testler dosyadaki sırayla çalışır; köşeli parantezdeki yüzde, testlerin ne kadarının bittiğini gösterir.

### 2.2 Sıfırlama olmasaydı

Her testin ilk satırı aynı: `reset_database()`. Bu satırın neden gerektiğini görelim. Dokuz testten de `reset_database()` satırını (ve altındaki boş satırı) sil. Sonra veritabanını bir kez sıfırla ve testleri **iki kez** çalıştır:

```bash
python reset_db.py
python -m pytest
python -m pytest
```

İlk çalıştırmada bütün testler geçer:

```text
collected 9 items

test_server.py .........                                                 [100%]

============================== 9 passed in 1.40s ===============================
```

İkinci çalıştırmada bir test kalır:

```text
collected 9 items

test_server.py ..F......                                                 [100%]

=================================== FAILURES ===================================
_______________________________ test_create_book _______________________________

    def test_create_book():
        response = client.post("/books", json=new_book)

        assert response.status_code == 201
>       assert response.headers["Location"] == "/books/74"
E       AssertionError: assert '/books/75' == '/books/74'
E
E         - /books/74
E         ?         ^
E         + /books/75
E         ?         ^

test_server.py:40: AssertionError
=========================== short test summary info ============================
FAILED test_server.py::test_create_book - AssertionError: assert '/books/75' ...
========================= 1 failed, 8 passed in 1.47s ==========================
```

Kodda hiçbir şey değişmedi, ama aynı test bir kez geçti, bir kez kaldı. İlk çalıştırmada `test_create_book` 74 numaralı kitabı ekledi. Hafta 6'dan beri kayıtlar kalıcı: Testler bittiğinde 74 numaralı kitap veritabanında kaldı. İkinci çalıştırmada yeni kitap `75` kimliğini aldı.

Öteki testler bu sefer şans eseri geçti. Örneğin `test_patch_rating` ilk çalıştırmada 57 numaralı kitabın puanını 3 yaptı; ikinci çalıştırmada da puanı 3 yaptığı için fark görünmedi. Testler önceki testlerin ya da önceki çalıştırmaların bıraktığı veriye bağlı olmamalı: Her test aynı başlangıç hâliyle başlamalı.

### 2.3 Her testten önce: hazırlık fonksiyonu

Sıfırlama satırını her teste tekrar yazmak yerine pytest'e "her testten önce bunu çalıştır" diyebiliriz. `test_server.py` dosyasının en başına şu satırı ekle:

```python
import pytest
```

`new_book` sözlüğünün altına, ilk testin üstüne şu fonksiyonu ekle:

```python
# Her testten önce çalışır: her test, veritabanının başlangıç hâliyle başlar.
@pytest.fixture(autouse=True)
def fresh_database():
    reset_database()
```

| Kod | Ne yapar? |
|---|---|
| `@pytest.fixture` | Fonksiyonu bir **hazırlık fonksiyonu (fixture)** yapar: Testler için ortamı hazırlayan bir fonksiyon. `@` ile başlayan satır bir dekoratördür; `@app.get(...)` satırlarımız gibi, altındaki fonksiyonu pytest'e tanıtır (Hafta 1'deki [dekoratör ek notu](../Week_01/05_Supplement_Decorator.md)). |
| `autouse=True` | Bu hazırlık fonksiyonunu **her testten önce kendiliğinden** çalıştırır. Testlerin onu ayrıca çağırması gerekmez. |
| `reset_database()` | Hazırlığın kendisi: veritabanını sıfırlamak. |

Testlerden sildiğin `reset_database()` satırları silinmiş olarak kalsın. Testleri yine iki kez çalıştır. İki seferde de sonuç aynı:

```text
============================== 9 passed in 1.75s ===============================
```

Sıfırlama artık tek yerde ve hiçbir test onu unutamaz.

> **Testler veritabanını sıfırlar:** Testleri çalıştırdığında `catalog` veritabanı başlangıç hâline döner; elle eklediğin kitaplar silinir. Föy boyunca zaten böyle çalışıyoruz. Gerçek projelerde testler ayrı bir veritabanı kullanır; bunun bir yolunu [ek notta](03_Supplement_Test_Database.md) görebilirsin.

> **Ana fikir:** Önceki haftalarda gözle kontrol ettiğimiz davranışların her biri artık bir test: İstek ve beklenen sonuç kodda yazılı. Veritabanı kalıcı olduğu için bir testin bıraktığı veri ötekileri etkileyebilir; `autouse=True` olan bir hazırlık fonksiyonu her testi aynı başlangıç hâliyle başlatır.

---

## Deney 3 — Bir değişiklik bir şeyi bozdu mu?

**Amaç:** Bir kod değişikliğinin, önceden çalışan bir işlemi bozduğunu testlerle görmek ve uzun hata çıktısında hatanın yerini bulmak.

### 3.1 "Kodu sadeleştirelim"

Bir arkadaşın `update_book` fonksiyonunu okuyor ve `exclude_unset=True` yazımını gereksiz buluyor: "Nasılsa yalnızca gönderilen alanlar gelir." `server.py` dosyasında `update_book` fonksiyonundaki satırı onun önerdiği gibi değiştir:

| Eski satır | Yeni satır |
|---|---|
| `changes = book_data.model_dump(exclude_unset=True)` | `changes = book_data.model_dump()` |

Sunucuyu başlatıp elle denemek yerine testleri çalıştır. Bu kez `--tb=short` seçeneğiyle: Hata izi kısaltılmış olarak gösterilir.

```bash
python -m pytest --tb=short
```

Çıktının ilk satırları bir testin kaldığını söylüyor:

```text
test_server.py ......F..                                                 [100%]
```

Yedinci test kaldı: `test_patch_rating`. Değişiklik yalnızca `PATCH` işlemini etkiliyor ve onu bozmuş. Önceden çalışan bir şeyin bir değişiklikten sonra bozulmasına **gerileme (regression)** denir. Testleri yazmamızın asıl nedeni bu: Gerilemeyi, kodu kullanan biri fark etmeden yakalamak.

### 3.2 Uzun hata çıktısını okumak

Çıktının geri kalanı uzun: Kısaltılmış hâliyle bile yüz elli satıra yakın. Satırların çoğu FastAPI, SQLAlchemy ve psycopg gibi kütüphanelerin kendi dosyalarından geliyor. Böyle bir **hata izinde (traceback)** üç yere bak. Aşağıda yalnızca bu yerler alındı; aradaki satırlar `...` ile kısaltıldı:

```text
______________________________ test_patch_rating _______________________________
...
test_server.py:84: in test_patch_rating
    response = client.patch("/books/57", json={"rating": 3})
...
server.py:133: in update_book
    session.commit()
...
E   sqlalchemy.exc.IntegrityError: (psycopg.errors.NotNullViolation) null value in column "title" of relation "book" violates not-null constraint
E   DETAIL:  Failing row contains (57, null, null, null, null, 3, null).
E   [SQL: UPDATE book SET title=%(title)s::VARCHAR, author=%(author)s::JSONB, available=%(available)s, tags=%(tags)s::JSONB, rating=%(rating)s WHERE book.id = %(book_id)s::INTEGER]
E   [parameters: {'title': None, 'author': Jsonb(None), 'available': None, 'tags': Jsonb(None), 'rating': 3.0, 'book_id': 57}]
E   (Background on this error at: https://sqlalche.me/e/20/gkpj)
=========================== short test summary info ============================
FAILED test_server.py::test_patch_rating - sqlalchemy.exc.IntegrityError: (ps...
========================= 1 failed, 8 passed in 2.37s ==========================
```

| Nereye bak? | Çıktıda | Ne öğreniyoruz? |
|---|---|---|
| 1. En alttaki `E` satırları | `NotNullViolation: null value in column "title" ...` | **Ne oldu?** Veritabanı, adı boş (`null`) olan bir kaydı reddetti. `Failing row` satırı yazılmak istenen kaydı gösteriyor: Kimlik ve puan dışındaki her sütun `null`. |
| 2. Kendi dosyalarımızın satırları | `test_server.py:84: in test_patch_rating` ve `server.py:133: in update_book` | **Nerede oldu?** Testin 84. satırındaki istek, `server.py` dosyasının 133. satırında, `update_book` fonksiyonundaki `session.commit()` satırında hataya yol açtı. Kütüphanelerin satırlarını atlayıp yalnızca bizim dosyalarımızın adını arıyoruz. |
| 3. `[SQL: ...]` ve `[parameters: ...]` satırları | `UPDATE book SET title=..., author=..., available=..., tags=..., rating=...` | **Neden oldu?** `PATCH` yalnızca puanı göndermişti, ama `UPDATE` komutu beş sütunun hepsini yazmaya çalışıyor; dördünün değeri `None`. |

Hafta 6'nın Deney 6'sında aynı `PATCH` isteğinin `UPDATE` komutunu görmüştük: `UPDATE book SET rating=%(rating)s WHERE ...`. Orada yalnızca `rating` vardı. `exclude_unset=True` olmadan `model_dump()`, gönderilmeyen alanları da varsayılan değerleri olan `None` ile verir (Hafta 5, Deney 4). `sqlmodel_update` hepsini kitaba yazar ve veritabanı adı boş bir kitabı kabul etmez.

Gerçek bir istemci bu hatayı yalnızca `500 Internal Server Error` olarak görürdü; ayrıntılar sunucunun terminalinde kalırdı. `TestClient` ise sunucuda çıkan hatayı teste taşır, bu yüzden hatanın kendisini test çıktısında okuyabiliyoruz. Bu davranışın nasıl değiştirileceğini [ek notta](04_Supplement_Server_Exceptions.md) görebilirsin.

### 3.3 Düzelt ve tekrar çalıştır

Satırı eski hâline getir:

```python
        changes = book_data.model_dump(exclude_unset=True)
```

Testleri yeniden çalıştır:

```text
============================== 9 passed in 1.80s ===============================
```

Değişikliği geri aldığımızı da testler doğruladı. Kodda her değişiklikten sonra bütün testleri çalıştırmak iki saniye sürüyor.

> **Ana fikir:** Testler, bir değişikliğin önceden çalışan bir işlemi bozup bozmadığını hemen gösterir. Uzun bir hata izinde önce en alttaki `E` satırlarına (ne oldu?), sonra kendi dosyalarımızın satırlarına (nerede oldu?) bakılır. `TestClient`, sunucudaki hatayı teste taşıdığı için hatanın kendisi test çıktısında görünür.

---

## Deney 4 — Hata yok, sonuç yanlış

**Amaç:** Hiçbir hata vermeden yanlış sonuç üreten bir değişikliğin yerini adım adım bulmak.

Deney 3'teki değişiklik bir hataya yol açtı ve hata izi bize yeri gösterdi. Bazı değişiklikler ise hata vermez; yalnızca yanlış sonuç üretir.

### 4.1 Bir harf

`server.py` dosyasında `get_books` fonksiyonundaki satırı şöyle değiştir:

| Eski satır | Yeni satır |
|---|---|
| `statement = select(Book).where(Book.title.icontains(search, autoescape=True))` | `statement = select(Book).where(Book.title.contains(search, autoescape=True))` |

Testleri çalıştır:

```text
test_server.py ...F.....                                                 [100%]

=================================== FAILURES ===================================
______________________________ test_search_books _______________________________

    def test_search_books():
        response = client.get("/books", params={"search": "api"})

        ids = []
        for book in response.json():
            ids.append(book["id"])
>       assert ids == [42, 73]
E       assert [] == [42, 73]
E
E         Right contains 2 more items, first extra item: 42
E         Use -v to get more diff

test_server.py:60: AssertionError
=========================== short test summary info ============================
FAILED test_server.py::test_search_books - assert [] == [42, 73]
========================= 1 failed, 8 passed in 1.92s ==========================
```

Bu kez hata izinde `server.py` yok; kalan şey testin kendi `assert` satırı. Arama boş liste döndürdü: `[]`. `Right contains 2 more items`, sağdaki listede, yani beklediğimizde iki öğe fazla olduğunu söylüyor. Sunucu bir hata vermedi, `200` ile yanıt verdi; ama yanıt yanlış.

Hatanın yerini bulmak, yani **hata ayıklamak (debugging)** için adım adım ilerleyelim.

### 4.2 Daralt: yalnızca bir testi çalıştır

Tek bir testle uğraşırken hepsini çalıştırmaya gerek yok. `-k` seçeneği, adında verilen kelime geçen testleri çalıştırır:

```bash
python -m pytest -k search -v
```

Çıktının başı:

```text
collecting ... collected 9 items / 8 deselected / 1 selected

test_server.py::test_search_books FAILED                                 [100%]
```

`8 deselected`: Sekiz test seçilmedi; yalnızca `test_search_books` çalıştı.

### 4.3 Bak: yanıtın tamamını yazdır

`assert` satırı yalnızca kimliklerin listesini gösteriyor. Yanıtın tamamını görmek için teste geçici bir `print` satırı ekle:

```python
    response = client.get("/books", params={"search": "api"})
    print("Response:", response.status_code, response.json())
```

Aynı komutu `-v` olmadan çalıştır: `python -m pytest -k search`. Kalan bir testin `print` çıktısını pytest ayrı bir bölümde gösterir:

```text
----------------------------- Captured stdout call -----------------------------
Response: 200 []
```

*Captured stdout*, "yakalanan çıktı" demek: pytest, testin ekrana yazdıklarını saklar ve yalnızca test kalırsa gösterir. Yanıt `200` ve gerçekten boş bir liste. Demek ki arama hiçbir kitabın adında `api` bulamadı.

### 4.4 Tahmin et ve dene

Kitapların adlarında `api` yok, ama `API` var. Bir tahmin: Arama artık büyük ve küçük harfi ayırıyor olabilir. Tahmini denemek için testteki `"api"` yazımını geçici olarak `"API"` yap ve testi tekrar çalıştır:

```text
======================= 1 passed, 8 deselected in 1.44s ========================
```

Büyük harfle arama çalışıyor; tahmin doğru. Şimdi aramayı yapan koda bakıyoruz: `get_books` fonksiyonundaki `where` satırı. `contains`, büyük ve küçük harfi ayırır; `icontains` ayırmaz. Hafta 6'da `icontains` yazmıştık; baştaki `i`, İngilizcede *ignore case*, yani "harf büyüklüğüne bakma" demek. Değişiklik tek bir harfti.

Üç şeyi eski hâline getir:

1. `server.py` dosyasında `contains` yazımını `icontains` yap.
2. Testteki `"API"` yazımını `"api"` yap.
3. `print` satırını sil.

Bütün testleri çalıştır:

```text
============================== 9 passed in 1.83s ===============================
```

Bu deneyde izlediğimiz yol, hata ayıklamanın genel yoludur:

| Adım | Bu deneyde |
|---|---|
| 1. Hatayı tekrar üret | Testi çalıştırınca hata her seferinde görünüyor. |
| 2. Daralt | `-k search` ile yalnızca ilgili testi çalıştırdık. |
| 3. Bak | `print` ile yanıtın tamamını gördük: `200 []`. |
| 4. Tahmin et ve dene | "Arama harf büyüklüğüne bakıyor" dedik; `"API"` ile denedik. |
| 5. Düzelt ve bütün testleri çalıştır | `icontains` yazımına döndük; dokuz test geçti. |

Deney 3'teki gibi bir hata izi olsaydı 3. adımda nereye bakacağımızı o gösterirdi. Burada yoktu; ipucunu kendimiz topladık. pytest'in kullandığımız seçeneklerini ve birkaç yenisini [ek notta](05_Supplement_Pytest_Options.md) bir arada bulabilirsin.

> **Ana fikir:** Bir değişiklik hata vermeden yanlış sonuç da üretebilir; onu yalnızca beklenen sonucu bilen bir test yakalar. Hatanın yerini bulmak için önce daraltırız (`-k`), sonra bakarız (`print`), sonra bir tahmini deneriz. Düzelttikten sonra yalnızca o testi değil, bütün testleri çalıştırırız.

---

## Deney 5 — Veritabanına bakan test

**Amaç:** API'nin göstermediği bir sonucu doğrudan veritabanına bakarak kontrol etmek.

Bu deney ödev: Derste zaman kalmazsa evde yap.

Hafta 6'nın Deney 5'inde 42 numaralı kitabı sildik ve yorumlarının da silindiğini psql ile gördük; API bize yalnızca `404` diyordu. Test, aynı kontrolü veritabanına bakarak yapabilir.

### 5.1 Testi yaz

`test_server.py` dosyasının başındaki import satırlarını şöyle değiştir: SQLModel'den iki ad, `database.py` dosyasından da iki ad daha alıyoruz.

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from database import Review, engine, reset_database
from server import app
```

Dosyanın sonuna şu testi ekle:

```python
# Kitap silme: kitabın yorumlarını veritabanı da siler.
def test_delete_book_deletes_reviews():
    response = client.delete("/books/42")
    assert response.status_code == 204

    with Session(engine) as session:
        statement = select(Review).where(Review.book_id == 42)
        reviews = session.exec(statement).all()

    assert reviews == []
```

Test, kitabı API üzerinden siliyor; yorumları ise sunucunun kullandığı veritabanından, Hafta 6'da öğrendiğimiz `select` ile okuyor. Testleri `-v` ile çalıştır:

```text
collecting ... collected 10 items

test_server.py::test_get_book PASSED                                     [ 10%]
test_server.py::test_get_missing_book PASSED                             [ 20%]
test_server.py::test_create_book PASSED                                  [ 30%]
test_server.py::test_search_books PASSED                                 [ 40%]
test_server.py::test_rating_out_of_range PASSED                          [ 50%]
test_server.py::test_negative_book_id PASSED                             [ 60%]
test_server.py::test_patch_rating PASSED                                 [ 70%]
test_server.py::test_patch_null_title PASSED                             [ 80%]
test_server.py::test_second_review_conflict PASSED                       [ 90%]
test_server.py::test_delete_book_deletes_reviews PASSED                  [100%]

============================== 10 passed in 1.88s ==============================
```

### 5.2 Kuralı kaldırınca

Test gerçekten veritabanındaki kuralı mı kontrol ediyor? `database.py` dosyasında `Review` modelindeki kuralı geçici olarak kaldır:

| Eski satır | Yeni satır |
|---|---|
| `book_id: int = Field(foreign_key="book.id", ondelete="CASCADE")` | `book_id: int = Field(foreign_key="book.id")` |

Testleri `--tb=short` ile çalıştır. Uzun çıktının üç yeri:

```text
test_server.py .........F                                                [100%]
...
test_server.py:112: in test_delete_book_deletes_reviews
...
server.py:104: in delete_book
...
E   sqlalchemy.exc.IntegrityError: (psycopg.errors.ForeignKeyViolation) update or delete on table "book" violates foreign key constraint "review_book_id_fkey" on table "review"
E   DETAIL:  Key (id)=(42) is still referenced from table "review".
```

Kural olmadan veritabanı, yorumu olan kitabın silinmesini reddetti: `Key (id)=(42) is still referenced from table "review"`, 42 numaralı kitaba hâlâ bir yorumun bağlı olduğunu söylüyor. Bu, Hafta 4'teki [ek notta](../Week_04/04_Supplement_Deleted_Book_Reviews.md) tartıştığımız 3. seçenek: "Yorumu olan kitap silinemez." Yabancı anahtarın varsayılan davranışı bu; `ondelete="CASCADE"` onu "yorumları da sil" olarak değiştiriyordu.

Hafta 6'nın 8.3 alıştırmasında tablo modelini değiştirdikten sonra `reset_db.py` çalıştırmak gerekmişti. Burada gerekmedi: Hazırlık fonksiyonu her testten önce `reset_database()` ile tabloları modellere göre yeniden oluşturuyor.

Kuralı geri koy ve testlerin yeniden geçtiğini gör.

> **Ana fikir:** Bir test yalnızca API yanıtına değil, veritabanına da bakabilir. Böylece API'nin göstermediği sonuçlar, örneğin silinen kitabın yorumları, de kontrol edilir. Bir kuralı kaldırıp testin kaldığını görmek, testin o kuralı gerçekten kontrol ettiğini gösterir.

---

## 6. Bu haftanın sonundaki dosyalar

`server.py` bu hafta değişmedi; Hafta 6'nın 7.3 bölümündeki hâliyle kalıyor. `database.py` dosyasının başı ve sonu, `reset_db.py` dosyası ve `test_server.py` dosyası şöyle olmalı. Hafta 8'e bu dosyalarla başlayacağız.

### 6.1 `database.py`

Import satırları:

```python
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Session, SQLModel, create_engine
```

`DATABASE_URL`, `engine`, `Book` ve `Review` Hafta 6'daki gibi. Dosyanın sonunda 1.1'deki `reset_database` fonksiyonu var.

### 6.2 `reset_db.py`

```python
from database import reset_database

reset_database()
print("Database reset: 3 books, 1 review")
```

### 6.3 `test_server.py`

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from database import Review, engine, reset_database
from server import app

client = TestClient(app)

new_book = {
    "title": "Test Kitabı",
    "author": {
        "first_name": "Ada",
        "last_name": "Yıldız"
    },
    "available": True,
    "tags": []
}


# Her testten önce çalışır: her test, veritabanının başlangıç hâliyle başlar.
@pytest.fixture(autouse=True)
def fresh_database():
    reset_database()


# Tek kitap: 42 numaralı kitap okunabilmeli.
def test_get_book():
    response = client.get("/books/42")

    assert response.status_code == 200
    assert response.json()["title"] == "API Yolculuğu"


# Olmayan kitap: 404 ve açıklaması.
def test_get_missing_book():
    response = client.get("/books/43")

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}


# Yeni kitap: 201, Location başlığı ve o adresten okunabilen kitap.
def test_create_book():
    response = client.post("/books", json=new_book)

    assert response.status_code == 201
    assert response.headers["Location"] == "/books/74"

    response = client.get("/books/74")
    assert response.json()["title"] == "Test Kitabı"


# Arama: büyük ve küçük harfi ayırmaz, sonuçlar kimlik sırasıyla gelir.
def test_search_books():
    response = client.get("/books", params={"search": "api"})

    ids = []
    for book in response.json():
        ids.append(book["id"])
    assert ids == [42, 73]


# Hatalı puan: 422 ve hatanın yeri.
def test_rating_out_of_range():
    book = new_book.copy()
    book["rating"] = 7

    response = client.post("/books", json=book)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "rating"]


# Negatif kimlik: yol parametresinin kuralı.
def test_negative_book_id():
    response = client.get("/books/-5")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "book_id"]


# PATCH: yalnızca gönderilen alan değişir.
def test_patch_rating():
    response = client.patch("/books/57", json={"rating": 3})

    assert response.status_code == 200
    assert response.json()["rating"] == 3
    assert response.json()["title"] == "Veriyle İlk Adımlar"


# PATCH: ad null olamaz; istek reddedilir ve kitap değişmez.
def test_patch_null_title():
    response = client.patch("/books/42", json={"title": None})
    assert response.status_code == 422

    response = client.get("/books/42")
    assert response.json()["title"] == "API Yolculuğu"


# Yorum: aynı okur aynı kitaba ikinci kez yorum yazamaz.
def test_second_review_conflict():
    review = {"reader": "Ece", "comment": "Tekrar okudum.", "score": 4}

    response = client.post("/books/42/reviews", json=review)

    assert response.status_code == 409


# Kitap silme: kitabın yorumlarını veritabanı da siler.
def test_delete_book_deletes_reviews():
    response = client.delete("/books/42")
    assert response.status_code == 204

    with Session(engine) as session:
        statement = select(Review).where(Review.book_id == 42)
        reviews = session.exec(statement).all()

    assert reviews == []
```

---

## 7. Ödev: belge ve kendi testlerin

Bu bölümü, Deney 5 ile birlikte evde tamamla.

### 7.1 `README.md` belgesine testleri eklemek

Hafta 6'da `README.md` belgesine eklediğin "Veritabanı" bölümünün altına şu bölümü ekle:

````markdown
## Testler

Testler `test_server.py` dosyasında. Veritabanı çalışırken bütün testleri çalıştırmak için:

```bash
python -m pytest
```

Testler her testten önce veritabanını başlangıç hâline getirir; veritabanındaki kayıtlar silinir.
````

### 7.2 Kendin yaz: yorum ve arama testleri

Yorum işlemlerinin yalnızca bir durumu test ediliyor: ikinci yorumun `409` alması. Hafta 6'nın [arama ek notunda](../Week_06/06_Supplement_Search_Differences.md) gördüğümüz davranışın da bir testi yok.

**İstenenler:** `test_server.py` dosyasına dört test ekle:

1. `test_get_reviews`: 42 numaralı kitabın yorumları `200` ile gelir; listede tek yorum vardır ve okuru Ece'dir.
2. `test_create_review`: 42 numaralı kitaba Can'in yorumu `201` ile eklenir; yorumun kimliği `2`, kitabı `42` olur.
3. `test_review_for_missing_book`: 43 numaralı kitaba yorum `404` alır.
4. `test_search_turkish_letters`: `ilk` araması yalnızca 57 numaralı kitabı bulur.

**İpucu:** Bir listenin öğe sayısını `len(...)` verir. Arama testinde `test_search_books` testindeki kimlik listesini kullanabilirsin.

**Kontrol et:** Testleri çalıştır. Sonuç `14 passed` olmalı.

Kodunu yazıp denedikten sonra [ek nottaki cevapla](06_Supplement_Exercise_7_2_Answer.md) karşılaştır.

### 7.3 Kendin yaz: hiçbir testin yakalamadığı hata

Hafta 6'nın [ek notunda](../Week_06/07_Supplement_Refresh.md) `session.refresh(book)` satırı unutulunca `PATCH` isteğinin `500` aldığını görmüştük.

**İstenenler:**

1. `server.py` dosyasında `replace_book` fonksiyonundaki `session.refresh(book)` satırını sil ve testleri çalıştır. Kaç test kaldı?
2. Bu hatayı yakalayacak bir test yaz: `test_replace_book`. Test, `PUT /books/73` isteğiyle `new_book` kitabını göndersin; yanıtın `200` olduğunu ve kitabın adının değiştiğini kontrol etsin.
3. Testin, satır silinmişken kaldığını, satırı geri koyunca geçtiğini gör.

**İpucu:** 1. adımda hiçbir test kalmıyorsa bir şeyi yanlış yapmış değilsin.

Kodunu yazıp denedikten sonra [ek nottaki cevapla](07_Supplement_Exercise_7_3_Answer.md) karşılaştır.

---

## 8. Kendini kontrol et: Bu haftanın yedi sorusu

1. `TestClient` ile gönderilen bir istek, `httpx` ile gönderilen istekten nasıl ayrılır? Testleri çalıştırırken neden `uvicorn` ile sunucu başlatmadık?
2. Bir testi kaldıran nedir? Bir test kaldığında hangi iki olasılığı düşünmeliyiz?
3. Deney 2.2'de aynı test neden bir kez geçti, bir kez kaldı?
4. `@pytest.fixture(autouse=True)` ile yazılan `fresh_database` fonksiyonu ne işe yarıyor?
5. Uzun bir hata izinde hatanın ne olduğunu ve kodun neresinde olduğunu nasıl buluruz?
6. Deney 4'teki hata neden bir hata izi üretmedi? Yerini hangi adımlarla bulduk?
7. Bütün testlerin geçmesi kodda hiç hata olmadığını gösterir mi? 7.3 alıştırması ne gösterdi?

### 8.1 Soruların cevapları

1. `TestClient` isteği ağ üzerinden göndermez; doğrudan `server.py` dosyasındaki `app` uygulamasına iletir. Bu yüzden ayrıca çalışan bir sunucuya gerek yok. Yanıt yine `response` nesnesiyle, `status_code`, `json()` ve `headers` ile okunur. Veritabanı ise gerçek: Testler Hafta 6'daki PostgreSQL veritabanını kullanıyor.
2. Bir `assert` satırındaki koşulun yanlış olması ya da test çalışırken bir hata çıkması. Bir test kaldığında ya kod beklediğimiz gibi çalışmıyordur ya da beklentimiz, yani testin kendisi yanlıştır. Deney 1.3'te testin kendisi yanlıştı.
3. Testler veritabanını sıfırlamıyordu. İlk çalıştırmada `test_create_book` 74 numaralı kitabı ekledi; kayıtlar kalıcı olduğu için kitap veritabanında kaldı. İkinci çalıştırmada yeni kitap `75` kimliğini aldı ve `Location` başlığı beklenenden farklı oldu.
4. Her testten önce kendiliğinden çalışır ve veritabanını sıfırlar. Böylece her test aynı başlangıç hâliyle başlar, testler birbirini ve önceki çalıştırmaları etkilemez; sıfırlama satırını da her teste ayrı ayrı yazmak gerekmez.
5. Önce en alttaki `E` satırlarına bakarız: Hatanın türü ve açıklaması orada. Sonra kütüphanelerin satırlarını atlayıp kendi dosyalarımızın adının geçtiği satırları ararız: `test_server.py:84` ve `server.py:133: in update_book` gibi. Bunlar hatanın kodumuzun neresinde çıktığını söyler.
6. Kodda bir hata çıkmadı; sunucu `200` ile yanıt verdi, ama yanıt yanlıştı. Yalnızca testteki `assert` kaldı. Yerini bulmak için önce `-k search` ile daralttık, sonra `print` ile yanıtın tamamına baktık, sonra "arama harf büyüklüğüne bakıyor" tahminini `"API"` ile denedik ve sonunda `contains` yazımını bulduk.
7. Göstermez. Testler yalnızca kontrol ettikleri davranışları korur. 7.3'te `replace_book` fonksiyonu bozukken on testin hepsi geçti, çünkü hiçbiri `PUT` isteği göndermiyordu. Hatayı ancak `PUT` için bir test yazınca gördük.

---

## 9. Resmî belgeler

- [FastAPI — Testing](https://fastapi.tiangolo.com/tutorial/testing/): Belgeler `TestClient` için `httpx` kurulmasını söylüyor; 0.2'deki uyarı nedeniyle biz `httpx2` kurduk.
- [Starlette — Test Client](https://starlette.dev/testclient/): `raise_server_exceptions` ayarı bu sayfada.
- [pytest — Get Started](https://docs.pytest.org/en/stable/getting-started.html)
- [pytest — How to write and report assertions in tests](https://docs.pytest.org/en/stable/how-to/assert.html)
- [pytest — How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html): `autouse` bu sayfada.
- [pytest — How to invoke pytest](https://docs.pytest.org/en/stable/how-to/usage.html): `-k` seçeneği bu sayfada.
- [pytest — Managing pytest's output](https://docs.pytest.org/en/stable/how-to/output.html): `-v`, `-q` ve `--tb` seçenekleri bu sayfada.
- [pytest — How to capture stdout/stderr output](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html)
- [Python — The assert statement](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement)

# Hafta 08 — Uygulama Föyü

## 0. Yedi haftada ne kurduk?

Bu hafta yeni bir araç ya da yeni bir kavram yok. Yedi haftada kurduğumuz kataloğu baştan sona birlikte düşüneceğiz: Bir istek sunucuya geldiğinde hangi adımlardan geçiyor, yanıtı hangi adım veriyor ve testlerimiz bu adımların hangilerini gerçekten koruyor?

Kataloğun bugünkü hâli, her haftanın eklediği bir parçadan oluşuyor:

| Hafta | Projeye eklenen | Bugün nerede? |
|---|---|---|
| 1 | Kitapları okuma ve adında arama (`GET`), yol ve sorgu parametreleri | `server.py`: `get_books`, `get_book` |
| 2 | Kitap ekleme (`POST`), istek gövdesi, `201` ve `Location` başlığı | `server.py`: `create_book`, `BookCreate` |
| 3 | Kaynaklara göre adresler (`/books`, `/books/{book_id}/reviews`), yorumlar ve `README.md` | `server.py`: yorum işlemleri; `README.md` |
| 4 | Silme, tümüyle değiştirme ve kısmen değiştirme (`DELETE`, `PUT`, `PATCH`); yanıt modelleri | `server.py`: `delete_book`, `replace_book`, `update_book`, `BookPublic` |
| 5 | Alan kuralları, `422` ve `409` yanıtları | `server.py`: modellerdeki `Field`, `Path`, `ConfigDict` |
| 6 | Kalıcı veri: PostgreSQL ve SQLModel | `database.py`, `reset_db.py` |
| 7 | Otomatik testler: pytest | `test_server.py` |

Haftanın sonunda şu soruya cevap verebileceksin: **Bir isteğin yanıtına bakarak sunucuda hangi adımda ne olduğunu söyleyebilir miyim; söylediğimi bir testle kanıtlayabilir miyim?**

Bu hafta sırasıyla şunları yapacağız:

- **Deney 1:** On isteğin yanıtını önce tahmin etmek, sonra görmek; yanıtı hangi adımın verdiğini bulmak
- **Deney 2:** Bütün testleri geçen bir değişikliğin bozduğu davranışı, bir hata bildiriminden yola çıkarak bulmak
- **Deney 3:** Hangi işlemin testi olmadığını bulmak ve eksik testin yakaladığı hatayı düzeltmek
- **4. bölüm:** Ara değerlendirmeden önce projendeki eksikleri tamamlamak

### 0.1 Başlangıç dosyaları

Hafta 7'nin sonundaki dosyalarla başla:

| Dosya | Hafta 7 föyündeki yeri |
|---|---|
| `server.py` | Hafta 6'nın 7.3 bölümü. Hafta 7'de değişmedi. |
| `database.py` | 6.1 bölümü |
| `reset_db.py` | 6.2 bölümü |
| `test_server.py` | 6.3 bölümü: on test |

Kendi dosyalarından emin değilsen bu haftanın başlangıç dosyalarını kullan: [server.py](Starting_Code/server.py), [database.py](Starting_Code/database.py), [reset_db.py](Starting_Code/reset_db.py), [test_server.py](Starting_Code/test_server.py). Föydeki çıktılar bu dosyalarla alındı.

> **Hafta 7'nin ödevini yaptıysan:** 7.2 ve 7.3 alıştırmalarında eklediğin testler dosyanda kalabilir. O zaman test sayıların föydekinden fazla olur ve satır numaraları farklı görünür. Deney 3'teki bir istisnayı orada ayrıca belirttik.

### 0.2 Veritabanını başlat ve testleri çalıştır

```bash
docker start book-db
```

Sanal ortam etkinken, `server.py` ile aynı klasörde testleri çalıştır:

```bash
python -m pytest
```

Hafta 7'deki gibi başlıktaki satırları göstermiyoruz:

```text
collected 10 items

test_server.py ..........                                                [100%]

============================== 10 passed in 1.85s ==============================
```

On test geçiyorsa başlamaya hazırsın. Geçmeyen bir test varsa önce onu Hafta 7'deki adımlarla düzelt: Ara değerlendirmeye testleri geçen bir projeyle girmelisin.

---

## Deney 1 — Yanıtı kim verdi?

**Amaç:** Bir isteğin yanıtını göndermeden önce tahmin etmek ve yanıtı sunucuda hangi adımın verdiğini söylemek.

### 1.1 Önce tahmin et

Aşağıdaki on isteğin her biri için **durum kodunu** tahmin et ve tablonun son sütununa yaz. İstekler sırayla gönderilecek; veritabanı başlangıç hâlinde: 42, 57 ve 73 numaralı kitaplar var, 42 numaralı kitabın Ece'den bir yorumu var.

| No | İstek | Gövde | Tahminin |
|---|---|---|---|
| 1 | `GET /books/abc` | Yok | |
| 2 | `GET /book/42` | Yok | |
| 3 | `DELETE /books` | Yok | |
| 4 | `PATCH /books/43` | `{"rating": 9}` | |
| 5 | `PATCH /books/43` | `{"rating": 4}` | |
| 6 | `POST /books/42/reviews` | `{"reader": "Ece", "comment": "", "score": 4}` | |
| 7 | `POST /books/42/reviews` | `{"reader": "Ece", "comment": "Yine güzel.", "score": 4}` | |
| 8 | `GET /books?available=hayır` | Yok | |
| 9 | `DELETE /books/57` | Yok | |
| 10 | `DELETE /books/57` | Yok | |

Bazı istekler iki ayrı nedenle reddedilebilir gibi görünüyor. Örneğin 4. istekte hem kitap yok hem de puan kurala uymuyor. Böyle bir istekte hangi kontrolün önce yapıldığını düşün.

### 1.2 İstekleri gönder

`server.py` ile aynı klasörde `journey.py` adlı bir dosya oluştur. Sunucu başlatmaya gerek yok: Hafta 7'deki gibi `TestClient` istekleri doğrudan uygulamaya iletecek.

```python
from fastapi.testclient import TestClient

from database import reset_database
from server import app

client = TestClient(app)


# Yanıtın durum kodunu yazar; hata varsa açıklamasını ya da yerini de yazar.
def show(label, response):
    if response.status_code == 204:
        print(label, 204)
    elif response.status_code == 422:
        print(label, 422, response.json()["detail"][0]["loc"])
    else:
        print(label, response.status_code, response.json())


reset_database()

show("1: ", client.get("/books/abc"))
show("2: ", client.get("/book/42"))
show("3: ", client.delete("/books"))
show("4: ", client.patch("/books/43", json={"rating": 9}))
show("5: ", client.patch("/books/43", json={"rating": 4}))
show("6: ", client.post("/books/42/reviews", json={"reader": "Ece", "comment": "", "score": 4}))
show("7: ", client.post("/books/42/reviews", json={"reader": "Ece", "comment": "Yine güzel.", "score": 4}))
show("8: ", client.get("/books", params={"available": "hayır"}))
show("9: ", client.delete("/books/57"))
show("10:", client.delete("/books/57"))
```

| Kod | Ne yapar? |
|---|---|
| `show(label, response)` | Bir yanıtı tek satırda yazar. `204` yanıtının gövdesi yoktur, bu yüzden yalnızca durum kodu yazılır. `422` yanıtının `detail` listesindeki ilk hatanın yalnızca yeri (`loc`) yazılır, çünkü hatanın tamamı uzundur. Öteki yanıtlarda gövdenin tamamı yazılır. |
| `reset_database()` | İstekleri veritabanının başlangıç hâliyle göndermek için. Hafta 7'de testlerin başında yaptığımızın aynısı. |
| `show("1: ", client.get(...))` | İsteği gönderir ve yanıtı hemen `show` fonksiyonuna verir. |

Çalıştır:

```bash
python journey.py
```

```text
1:  422 ['path', 'book_id']
2:  404 {'detail': 'Not Found'}
3:  405 {'detail': 'Method Not Allowed'}
4:  422 ['body', 'rating']
5:  404 {'detail': 'Book not found'}
6:  422 ['body', 'comment']
7:  409 {'detail': 'This reader has already reviewed this book'}
8:  422 ['query', 'available']
9:  204
10: 404 {'detail': 'Book not found'}
```

Tahminlerini çıktıyla karşılaştır.

### 1.3 Kararı hangi adım verdi?

Bir istek sunucuya geldiğinde FastAPI şu sırayla ilerler. Bir adım isteği reddederse sonraki adımlara hiç geçilmez:

1. **Yolu ve metodu eşleştirmek:** İsteğin yolunu ve metodunu karşılayan bir fonksiyon var mı? Bu soruyu dekoratörler cevaplar: `@app.get("/books/{book_id}")` gibi.
2. **Parametreleri ve gövdeyi kontrol etmek:** Yol parametresi, sorgu parametresi ve gövde, fonksiyonun parametrelerinde yazılı türlere ve kurallara uyuyor mu?
3. **Fonksiyonu çalıştırmak:** Bizim kodumuz çalışır. Kitap veritabanında var mı, bu okur bu kitaba daha önce yorum yazmış mı gibi veriye bakmayı gerektiren kurallar burada kontrol edilir.
4. **Yanıtı hazırlamak:** Fonksiyonun döndürdüğü nesne yanıt modeline göre JSON'a çevrilir ve durum koduyla gönderilir.

| No | Yanıt | Kararı veren adım | Neden? | İlk gördüğümüz yer |
|---|---|---|---|---|
| 1 | `422`, `['path', 'book_id']` | 2. Parametreler | `abc` bir tam sayıya çevrilemez. Hatanın yeri yol parametresi. | Hafta 1, Hafta 5 |
| 2 | `404`, `Not Found` | 1. Eşleştirme | `/book/42` yolunu karşılayan bir fonksiyon yok. Hafta 1 ve 2'de kullandığımız bu tekil adresi Hafta 3'te `/books` yaptık. Açıklama bizim yazdığımız `Book not found` değil, FastAPI'nin `Not Found` yanıtı: Fonksiyonlarımızın hiçbiri çalışmadı. | Hafta 1, Hafta 3 |
| 3 | `405`, `Method Not Allowed` | 1. Eşleştirme | `/books` yolu var, ama yalnızca `GET` ve `POST` için. Koleksiyonun tamamını silen bir fonksiyon yazmadık. | Hafta 2 |
| 4 | `422`, `['body', 'rating']` | 2. Gövde | 43 numaralı kitap yok, ama bunu söyleyecek olan fonksiyon hiç çalışmadı: Gövdedeki puan, fonksiyon çağrılmadan önce reddedildi. | Hafta 5 |
| 5 | `404`, `Book not found` | 3. Fonksiyon | Gövde bu kez kurallara uyuyor. Fonksiyon çalıştı, kitabı veritabanında bulamadı ve bizim `HTTPException` satırımız yanıt verdi. | Hafta 1, Hafta 6 |
| 6 | `422`, `['body', 'comment']` | 2. Gövde | Ece'nin bu kitaba zaten yorumu var, yani istek `409` alabilirdi. Ama boş yorum, fonksiyon çalışmadan reddedildi. | Hafta 5 |
| 7 | `409`, `This reader has ...` | 3. Fonksiyon | Gövde kurallara uyuyor. Fonksiyon, Ece'nin bu kitaba yazdığı yorumu veritabanında buldu. | Hafta 5 |
| 8 | `422`, `['query', 'available']` | 2. Parametreler | `hayır` bir mantıksal değere (`True` ya da `False`) çevrilemez. `false`, `0` ya da `no` gönderilseydi kabul edilirdi. | Hafta 1, Hafta 6 |
| 9 | `204` | 3. Fonksiyon | Kitap silindi. Yanıtın gövdesi yok. | Hafta 4 |
| 10 | `404`, `Book not found` | 3. Fonksiyon | Aynı istek ikinci kez geldi; silinecek kitap artık yok. 9. ve 10. istek aynı, yanıtları farklı: Yanıt, isteğin yanında sunucudaki veriye de bağlı. | Hafta 4 |

Tablodan iki sonuç çıkıyor:

- **Aynı durum kodunu farklı adımlar verebilir.** 2. ve 5. isteklerin ikisi de `404` aldı. 2. istekte FastAPI "bu yol yok" dedi; 5. istekte bizim fonksiyonumuz "bu kitap yok" dedi. Açıklamaya bakmadan ikisini ayıramazsın.
- **Bir istek iki kuralı birden çiğnediğinde önce 2. adımın kuralı yanıt verir.** 4. ve 6. isteklerde fonksiyonun kontrol edeceği kural (`404`, `409`) hiç sorulmadı. Hafta 5'te kuralları iki yere yazmıştık: Değerin kendisine bakan kurallar modele, veriye bakan kurallar fonksiyona. Bu ayrım, kuralların hangi sırayla kontrol edileceğini de belirliyor.

Fonksiyonun içinde de bir sıra var: `create_review` önce kitabın var olup olmadığına, sonra okurun yorumuna bakıyor. Bu yüzden 43 numaralı kitaba yazılan bir yorum `409` değil `404` alır. Kontrollerin sırasını ve bir istekte birden fazla `422` hatası olduğunda ne olduğunu [ek notta](03_Supplement_Check_Order.md) görebilirsin.

> **Ana fikir:** Bir istek sırasıyla yol ve metot eşleştirmesinden, parametre ve gövde kontrolünden ve fonksiyonumuzdan geçer. `404 Not Found` ve `405` ilk adımdan, `422` ikinci adımdan, `404 Book not found` ve `409` bizim fonksiyonumuzdan gelir. Bir istek birden fazla kuralı çiğnediğinde, yanıtı ilk sıradaki adım verir.

---

## Deney 2 — Testler geçiyor, ama…

**Amaç:** Bütün testleri geçen bir kod değişikliğinin bozduğu davranışı, kullanıcının bildirdiği belirtiden yola çıkarak bulmak ve düzeltmek.

### 2.1 Üç "sadeleştirme"

Bir ekip arkadaşın `server.py` dosyasını okuyor ve üç satırı "sadeleştirmeyi" öneriyor: ikisini kısaltmayı, birini de benzer bir fonksiyona benzetmeyi. Önerdiği değişiklikleri yap:

| Fonksiyon | Eski satır | Yeni satır | Arkadaşının gerekçesi |
|---|---|---|---|
| `get_books` | `if available is not None:` | `if available:` | "`is not None` yazmaya gerek yok." |
| `replace_book` | `book.sqlmodel_update(book_data.model_dump())` | `book.sqlmodel_update(book_data.model_dump(exclude_unset=True))` | "`update_book` fonksiyonunda böyle yazdık; iki fonksiyon aynı olsun." |
| `create_review` | `statement = select(Review).where(Review.book_id == book_id).where(Review.reader == review_data.reader)` | `statement = select(Review).where(Review.reader == review_data.reader)` | "Okurun adına bakmak yeterli." |

Hafta 7'de öğrendiğimiz gibi, değişiklikten sonra testleri çalıştır:

```bash
python -m pytest
```

```text
collected 10 items

test_server.py ..........                                                [100%]

============================== 10 passed in 1.84s ==============================
```

On testin hepsi geçti. Ekip arkadaşın "Testler geçiyor, demek ki bir şey bozulmadı." diyor. Bu deneyin ve Deney 3'ün sonunda bu cümlenin neden yanlış olduğunu göreceğiz. Şimdilik değişiklikler kodda kalsın.

### 2.2 Bir hata bildirimi

Bir hafta sonra kataloğu kullanan bir kütüphaneci şunu bildiriyor:

> "Ödünç verilmiş kitapları görmek için `GET /books?available=false` isteğini gönderdim. Üç kitabın üçü de geldi; oysa ödünçte yalnızca 57 numaralı kitap var."

Hafta 7'de hatayı bulmanın ilk adımının onu tekrar üretmek olduğunu görmüştük. Bunun en iyi yolu, bildirilen davranışı kontrol eden bir test yazmaktır. Test, hata düzelene kadar kalacak; düzeldikten sonra da hatanın geri dönmesini önleyecek.

`test_server.py` dosyasının sonuna şu testi ekle:

```python
# Süzme: available=false yalnızca ödünç verilmiş kitapları getirir.
def test_filter_not_available():
    response = client.get("/books", params={"available": False})

    ids = []
    for book in response.json():
        ids.append(book["id"])
    assert ids == [57]
```

`params={"available": False}` yazımı, Python'un `False` değerini adreste `?available=false` olarak gönderir. Kimlik listesini Hafta 7'deki `test_search_books` testindeki gibi topluyoruz.

Yalnızca bu testi çalıştır:

```bash
python -m pytest -k not_available
```

```text
collected 11 items / 10 deselected / 1 selected

test_server.py F                                                         [100%]

=================================== FAILURES ===================================
__________________________ test_filter_not_available ___________________________

    def test_filter_not_available():
        response = client.get("/books", params={"available": False})

        ids = []
        for book in response.json():
            ids.append(book["id"])
>       assert ids == [57]
E       assert [42, 57, 73] == [57]
E
E         At index 0 diff: 42 != 57
E         Left contains 2 more items, first extra item: 57
E         Use -v to get more diff

test_server.py:129: AssertionError
=========================== short test summary info ============================
FAILED test_server.py::test_filter_not_available - assert [42, 57, 73] == [57]
======================= 1 failed, 10 deselected in 1.41s =======================
```

Test kaldı ve kütüphanecinin gördüğünü gösterdi:

| Çıktıdaki satır | Anlamı |
|---|---|
| `assert [42, 57, 73] == [57]` | Solda yanıttan gelen kimlikler, sağda beklediğimiz. Üç kitabın üçü de geldi. |
| `At index 0 diff: 42 != 57` | pytest listeleri öğe öğe karşılaştırır. İlk öğeler (sıra numarası 0) farklı: `42` ve `57`. |
| `Left contains 2 more items, first extra item: 57` | Soldaki listede iki öğe fazla. pytest, sağdaki listenin uzunluğu kadar öğeyi eşleştirir, kalanları "fazla" sayar; sağda tek öğe olduğu için fazlalık soldaki ikinci öğeden, `57` değerinden başlıyor. Bu satırı "57 fazla" diye okuma: Hangi kimliklerin fazla olduğunu ilk satırdaki iki listeyi karşılaştırarak görürüz: `42` ve `73`. |
| `Use -v to get more diff` | `-v` ile daha ayrıntılı bir karşılaştırma gösterilir. Burada ilk satır yeterli. |

Hata artık her çalıştırmada tekrar üretilebiliyor.

### 2.3 Bak: fonksiyona ne geldi?

Hata izinde `server.py` yok: Sunucu bir hata vermedi, yalnızca yanlış bir liste döndürdü. Hafta 7'nin Deney 4'ündeki durum. Bu kez `print` satırını testin değil, sunucudaki fonksiyonun içine koyalım; çünkü merak ettiğimiz şey, `available` parametresinin fonksiyona hangi değerle geldiği.

`server.py` dosyasında `get_books` fonksiyonunun ilk satırı olarak geçici bir `print` ekle:

```python
def get_books(search: str = "", available: bool | None = None):
    print("available:", repr(available))
    with Session(engine) as session:
```

`repr`, değeri Python'da yazıldığı gibi gösterir; Hafta 5'te boş metni `''` olarak görmek için kullanmıştık. Burada `False` değeri ile `'false'` metnini ayırmamızı sağlıyor. Testi yeniden çalıştır. Çıktının `Captured stdout call` bölümü:

```text
----------------------------- Captured stdout call -----------------------------
available: False
```

Parametre doğru gelmiş: `"false"` metni FastAPI tarafından `False` değerine çevrilmiş. Demek ki sorun parametrede değil, parametreyi kullanan satırda:

```python
        if available:
            statement = statement.where(Book.available == available)
```

Python'da `if` satırı, koşul olarak yazılan değer `False` ya da `None` ise altındaki satırı çalıştırmaz. `0`, boş metin `""` ve boş liste `[]` de aynı şekilde "yanlış" sayılır. `available` üç değer alabiliyor ve bu satır üçünü şöyle ayırıyor:

| İstek | `available` | `if available:` | `if available is not None:` |
|---|---|---|---|
| `GET /books` | `None` | Süzme yok: bütün kitaplar. Doğru. | Süzme yok: bütün kitaplar. Doğru. |
| `GET /books?available=true` | `True` | Süzer: 42 ve 73. Doğru. | Süzer: 42 ve 73. Doğru. |
| `GET /books?available=false` | `False` | **Süzme yok: bütün kitaplar. Yanlış.** | Süzer: yalnızca 57. Doğru. |

Kısa yazım, `False` ile `None` değerini ayıramıyor. `is not None`, "parametre gönderildi mi?" sorusunu soruyor; `False` gönderildiğinde de süzmenin yapılmasını sağlayan bu soru. Hafta 1'de `available: bool | None = None` parametresini tam bu üç durumu ayırmak için yazmış, süzmeyi `available is None or ...` koşuluyla yapmıştık. Hafta 6'daki `is not None` satırı aynı ayrımı korur.

### 2.4 Düzelt ve bütün testleri çalıştır

1. `print` satırını sil.
2. `if available:` satırını `if available is not None:` olarak geri al.

Bütün testleri çalıştır:

```text
============================== 11 passed in 2.06s ==============================
```

On bir test geçti. Yeni test dosyada kalıyor: Bu satırı biri yine "sadeleştirirse" test kalacak.

Bu deneyde izlediğimiz yol, Hafta 7'deki hata ayıklama yolunun başına bir adım ekliyor:

| Adım | Bu deneyde |
|---|---|
| 1. Bildirimi teste çevir | Kütüphanecinin isteği ve beklediği sonuç: `test_filter_not_available` |
| 2. Testin kaldığını gör | `assert [42, 57, 73] == [57]`: Hata tekrar üretildi. |
| 3. Daralt ve bak | `-k not_available` ile tek test; `print` ile fonksiyona gelen değer: `False` |
| 4. Düzelt | `if available is not None:` |
| 5. Bütün testleri çalıştır | On bir test geçti. |

Hatayı önce düzeltip sonra test yazsaydık, testin bu hatayı gerçekten yakalayıp yakalamadığını hiç görmezdik. Önce kalan, düzeltmeden sonra geçen bir test, hem hatayı hem de düzeltmeyi kanıtlar.

> **Ana fikir:** Bütün testlerin geçmesi, yalnızca testlerin kontrol ettiği davranışların bozulmadığını gösterir. Bir hata bildirildiğinde önce bildirimi bir teste çeviririz ve testin kaldığını görürüz; sonra hatayı düzeltiriz. Test dosyada kalır ve aynı hatanın geri dönmesini önler.

---

## Deney 3 — Hangi davranışın testi yok?

**Amaç:** Testlerin hangi işlemleri kontrol ettiğini bir tabloda görmek, testi olmayan bir işlem için test yazmak ve bu testin bulduğu hatayı düzeltmek.

Deney 2'deki hata bir kullanıcı bildirince bulundu. Daha iyisi, hatayı kullanıcıdan önce bulmak. Bunun için önce hangi davranışların hiç testi olmadığını görmemiz gerekiyor.

### 3.1 Testlerin haritası

`test_server.py` dosyasındaki on bir testin her birini oku. Her test için aşağıdaki tabloda ilgili işlemin satırını bul ve testin adını başarılı ya da hatalı istek sütununa yaz.

| İşlem | Başarılı istek | Hatalı istek |
|---|---|---|
| `GET /books` | | |
| `GET /books/{book_id}` | | |
| `POST /books` | | |
| `PUT /books/{book_id}` | | |
| `PATCH /books/{book_id}` | | |
| `DELETE /books/{book_id}` | | |
| `GET /books/{book_id}/reviews` | | |
| `POST /books/{book_id}/reviews` | | |

Doldurduktan sonra şununla karşılaştır:

| İşlem | Başarılı istek | Hatalı istek |
|---|---|---|
| `GET /books` | `test_search_books`, `test_filter_not_available` | Yok |
| `GET /books/{book_id}` | `test_get_book` | `test_get_missing_book` (`404`), `test_negative_book_id` (`422`) |
| `POST /books` | `test_create_book` | `test_rating_out_of_range` (`422`) |
| `PUT /books/{book_id}` | **Yok** | **Yok** |
| `PATCH /books/{book_id}` | `test_patch_rating` | `test_patch_null_title` (`422`) |
| `DELETE /books/{book_id}` | `test_delete_book_deletes_reviews` | Yok |
| `GET /books/{book_id}/reviews` | **Yok** | **Yok** |
| `POST /books/{book_id}/reviews` | Yok | `test_second_review_conflict` (`409`) |

İki işlemin hiç testi yok: `PUT` ve yorumları okumak. Hafta 7'nin 7.2 alıştırmasını yaptıysan yorum işlemlerinin testleri sende var. `PUT` ise ekip arkadaşının Deney 2'de değiştirdiği fonksiyonlardan biri, ve onu hiçbir test kontrol etmiyor.

### 3.2 `PUT` için bir test

Hafta 4'te `PUT` isteğinin kuralını şöyle yazmıştık: `PUT` kitabın tamamını gövdede gönderilen hâliyle değiştirir. Gönderilmeyen alan eski değerini korumaz; varsayılan değeri varsa o değer yazılır. 73 numaralı kitabın puanı `4.5`; `new_book` sözlüğünde puan yok.

`test_server.py` dosyasının sonuna şu testi ekle:

```python
# PUT: kitabın tamamı değişir; gönderilmeyen puan None olur.
def test_replace_book():
    response = client.put("/books/73", json=new_book)

    assert response.status_code == 200
    assert response.json()["title"] == "Test Kitabı"
    assert response.json()["rating"] is None
```

Son satırdaki `is None`, değerin `None` olup olmadığını kontrol eder. Yanıttaki `null`, Python'da `None` olarak okunur.

> **Hafta 7'nin 7.3 alıştırmasını yaptıysan:** Dosyanda zaten `test_replace_book` adlı bir test var. Aynı adla ikinci bir fonksiyon yazma: Python'da aynı adlı ikinci fonksiyon birincinin yerine geçer ve pytest yalnızca birini çalıştırır. Bunun yerine, var olan testine son `assert` satırını ekle. O testin Deney 2'deki değişiklikten sonra neden geçtiğini de düşün: Yalnızca adı kontrol ediyordu.

Testleri çalıştır:

```text
collected 12 items

test_server.py ...........F                                              [100%]

=================================== FAILURES ===================================
______________________________ test_replace_book _______________________________

    def test_replace_book():
        response = client.put("/books/73", json=new_book)

        assert response.status_code == 200
        assert response.json()["title"] == "Test Kitabı"
>       assert response.json()["rating"] is None
E       assert 4.5 is None

test_server.py:138: AssertionError
=========================== short test summary info ============================
FAILED test_server.py::test_replace_book - assert 4.5 is None
========================= 1 failed, 11 passed in 2.04s =========================
```

Kitabın adı değişti, ama puanı `4.5` olarak kaldı. Kalan satırı ve yanıtı birlikte düşünelim:

- İstek gövdesinde `rating` yok.
- `exclude_unset=True` ile `model_dump()`, gönderilmeyen alanları sözlüğe koymaz (Hafta 5, Deney 4).
- `sqlmodel_update`, yalnızca sözlükteki alanları kitaba yazar. Sözlükte `rating` olmadığı için kitabın puanı dokunulmadan kalır.

`PATCH` için doğru olan bu davranış, `PUT` için yanlış. Ekip arkadaşının "iki fonksiyon aynı olsun" gerekçesi, iki işlemin farkını gözden kaçırıyor: `PATCH` "yalnızca gönderdiğimi değiştir", `PUT` ise "kitap artık tam olarak bu olsun" der.

### 3.3 Düzelt

`replace_book` fonksiyonundaki satırı geri al:

```python
        book.sqlmodel_update(book_data.model_dump())
```

Testleri çalıştır:

```text
============================== 12 passed in 1.88s ==============================
```

Ekip arkadaşının üç değişikliğinden ikisini bulduk. Üçüncüsü, yorumlardaki değişiklik, hâlâ kodda. Hiçbir test onu yakalamıyor ve henüz kimse bildirmedi. Onu ödevde bulacaksın (6.2).

> **Ana fikir:** Testlerin her işlemi ve her önemli durumu kontrol edip etmediğini görmek için işlemleri ve testleri bir tabloda eşleştiririz. Boş kalan hücreler, hiçbir testin korumadığı davranışlardır. Bir test, kontrol etmediği alandaki hatayı yakalamaz: Yalnızca adı kontrol eden bir `PUT` testi, puandaki hatayı görmez.

---

## 4. Ara değerlendirmeye hazır mısın?

Ara değerlendirmede kendi bilgisayarında, kendi projen üzerinde çalışacaksın. Aşağıdaki her maddeyi föye bakmadan yapabiliyor olmalısın. Yapamadığın bir madde varsa son sütundaki yere dön ve eksik adımı şimdi tamamla.

### 4.1 Proje çalışıyor mu?

| Kontrol | Nasıl? | Eksikse |
|---|---|---|
| Veritabanı çalışıyor ve sıfırlanabiliyor. | `docker start book-db`, sonra `python reset_db.py`: `Database reset: 3 books, 1 review` | Hafta 6, 0.2 ve 1.2 |
| Sunucu başlıyor. | `python -m uvicorn server:app`, sonra tarayıcıda `http://127.0.0.1:8000/docs` | Hafta 1, Hafta 4 |
| Bütün testler geçiyor. | `python -m pytest` | Hafta 7 |
| Sunucu yeniden başlayınca eklenen kitap kalıyor. | Bir kitap ekle, sunucuyu durdurup başlat, kitabı oku. | Hafta 6, 4.3 |

### 4.2 İstek ve yanıtı açıklayabiliyor musun?

| Yapabilmen gereken | Örnek | Eksikse |
|---|---|---|
| Bir isteğin metodunu, yolunu, sorgu parametrelerini ve gövdesini ayırmak | `GET /books?search=api` ve gövdesi `{"rating": 3}` olan `PATCH /books/57`: Yol, sorgu parametresi ve gövde hangisi? | Hafta 1, Hafta 2, Hafta 3 |
| Bir isteği curl ile göndermek ve yanıtın başlıklarını görmek | `curl -i -X DELETE http://127.0.0.1:8000/books/57` | Hafta 4, 5.1 |
| Bir yanıtın durum kodunu ve gövdesini, onu hangi adımın verdiğiyle birlikte açıklamak | Deney 1'in on isteği | Bu hafta, Deney 1 |
| `PUT` ile `PATCH` arasındaki farkı bir örnekle göstermek | Deney 3 | Hafta 4 |
| Bir `422` yanıtında hatanın yerini (`loc`) ve nedenini (`msg`) okumak | `['body', 'rating']` | Hafta 5 |
| Bir kuralın modele mi, fonksiyona mı yazılacağına karar vermek | `score` 1 ile 5 arasında; okur bir kitaba bir yorum | Hafta 5, Deney 5 |

### 4.3 Kodu değiştirip kontrol edebiliyor musun?

| Yapabilmen gereken | Eksikse |
|---|---|
| Modele yeni bir alan ya da kural eklemek ve geçerli ve geçersiz değerlerle denemek | Hafta 5 |
| Tablo modeline bir alan ekledikten sonra veritabanını sıfırlamak gerektiğini bilmek | Hafta 6, 8.3 alıştırması |
| Bir davranış için test yazmak: hazırlık, istek, kontrol | Hafta 7, Deney 1 ve 2 |
| Kalan bir testin çıktısında beklenen ve gelen değeri, hatanın satırını bulmak | Hafta 7, Deney 1.3 ve 3.2 |
| Hata vermeden yanlış sonuç üreten bir kodun yerini daraltarak bulmak | Hafta 7, Deney 4; bu hafta, Deney 2 |

### 4.4 Belgen tam mı?

`README.md` belgende şu bölümler olmalı:

| Bölüm | Eklendiği yer |
|---|---|
| `## İşlemler` ve `## Örnekler` | Hafta 3, Deney 6; Hafta 4, 5.2 |
| `## Alan kuralları` | Hafta 5, 8.2 |
| `## Veritabanı` | Hafta 6, 8.1 |
| `## Testler` | Hafta 7, 7.1 |
| `## Hata yanıtları` | Bu hafta, 6.1 |

Belgedeki her örnek isteği bir kez gönder ve yanıtın belgedeki gibi olduğunu kontrol et. Belge ile kod arasındaki fark da bir hatadır: Belgeyi okuyup istek gönderen biri, yazanı değil kodun yaptığını görür.

---

## 5. Bu haftanın sonundaki dosyalar

`server.py`, `database.py` ve `reset_db.py` bu hafta değişmedi; Hafta 7'nin sonundaki hâlleriyle kalıyor. Deney 2'de ve Deney 3'te yaptığın değişiklikleri geri aldın. 6.2 alıştırmasında üçüncü değişikliği de geri alacaksın. `journey.py` dosyasını Hafta 9'da kullanmayacağız.

`test_server.py` dosyasının sonunda, Hafta 7'nin on testinin altında bu haftanın iki testi var:

```python
# Süzme: available=false yalnızca ödünç verilmiş kitapları getirir.
def test_filter_not_available():
    response = client.get("/books", params={"available": False})

    ids = []
    for book in response.json():
        ids.append(book["id"])
    assert ids == [57]


# PUT: kitabın tamamı değişir; gönderilmeyen puan None olur.
def test_replace_book():
    response = client.put("/books/73", json=new_book)

    assert response.status_code == 200
    assert response.json()["title"] == "Test Kitabı"
    assert response.json()["rating"] is None
```

Hafta 9'a bu dosyalarla ve 6.2 alıştırmasında düzelttiğin `server.py` ile başlayacağız.

---

## 6. Ödev: belge ve bildirilen hata

### 6.1 `README.md` belgesine hata yanıtlarını eklemek

Deney 1'de aynı durum kodunun farklı nedenlerle gelebildiğini gördük. API'yi kullanan biri, aldığı hatanın ne anlama geldiğini belgeden öğrenebilmeli. `## Testler` bölümünün üstüne şu bölümü ekle:

```markdown
## Hata yanıtları

| Durum kodu | `detail` | Anlamı |
|---|---|---|
| `404` | `Not Found` | Böyle bir yol yok. Adresi kontrol et: Koleksiyonun adı `/books`. |
| `404` | `Book not found` | Yol doğru, ama bu kimlikle bir kitap yok. |
| `405` | `Method Not Allowed` | Yol var, ama bu HTTP metoduyla bir işlem yok. |
| `409` | `This reader has already reviewed this book` | Bu okur bu kitaba daha önce yorum yazmış. |
| `422` | Hata listesi | İstek alan kurallarına uymuyor. Bkz. "Alan kuralları". |

Bir istek birden fazla kurala uymuyorsa önce `422` döner: Gövde ve parametreler, kitabın var olup olmadığına bakılmadan kontrol edilir.
```

### 6.2 Kendin yaz: bildirilen ikinci hata

Ekip arkadaşının üçüncü değişikliği hâlâ kodda. Bir okur şunu bildiriyor:

> "Ben Ece. 42 numaralı kitaba yorum yazmıştım. Şimdi 73 numaralı kitaba ilk yorumumu yazmak istedim, ama `409 Conflict` aldım: 'Bu okur bu kitaba zaten yorum yazmış' diyor. Ben bu kitaba hiç yorum yazmadım."

**İstenenler:**

1. Bildirimi bir teste çevir: `test_review_other_book`. Test, Ece'nin 73 numaralı kitaba yorumunu göndersin; yanıtın `201` olduğunu ve yorumun kitabının `73` olduğunu kontrol etsin.
2. Testin kaldığını gör. Hata izindeki değerler bildirimle aynı mı?
3. Hatanın yerini bul ve düzelt. Bütün testleri çalıştır.
4. Hafta 7'nin 7.2 alıştırmasındaki `test_create_review` testi (Can'in 42 numaralı kitaba yorumu) bu hatayı neden yakalamadı? Bir cümleyle açıkla.

**İpucu:** `409` yanıtını yalnızca bir satır veriyor. O satıra hangi koşulda gelindiğini oku: Sorgu, Ece'nin yorumlarından hangilerini buluyor?

**Kontrol et:** Düzeltmeden sonra sonuç `13 passed` olmalı (7.2 ve 7.3 testlerin varsa daha fazla).

Kodunu yazıp denedikten sonra [ek nottaki cevapla](04_Supplement_Exercise_6_2_Answer.md) karşılaştır.

### 6.3 Kendin yaz: Deney 1'in testleri

Deney 1'deki isteklerden üçünün sonucu hiçbir testte yok: 2. istek (`404 Not Found`), 3. istek (`405`) ve 4. istek (önce `422`).

**İstenenler:** Bu üç davranış için birer test yaz:

1. `test_wrong_path`: `GET /book/42` isteği `404` alır ve gövde tam olarak `{"detail": "Not Found"}` olur.
2. `test_method_not_allowed`: `DELETE /books` isteği `405` alır.
3. `test_invalid_body_before_missing_book`: 43 numaralı kitaba `{"rating": 9}` gönderen `PATCH` isteği `404` değil `422` alır; hatanın yeri `['body', 'rating']` olur.

**İpucu:** Testlerin her biri Hafta 7'deki `test_get_missing_book` ve `test_negative_book_id` testlerine benziyor. 1. testteki gövde kontrolü, `Book not found` ile `Not Found` yanıtlarını birbirinden ayırıyor; neden önemli olduğunu Deney 1'deki 2. ve 5. isteklerde gördük.

**Kontrol et:** Sonuç `16 passed` olmalı (7.2 ve 7.3 testlerin varsa daha fazla).

Kodunu yazıp denedikten sonra [ek nottaki cevapla](05_Supplement_Exercise_6_3_Answer.md) karşılaştır.

---

## 7. Kendini kontrol et: Bu haftanın yedi sorusu

1. Bir istek sunucuya geldiğinde FastAPI hangi adımlardan geçer? `405` yanıtı hangi adımdan gelir?
2. Deney 1'deki 2. ve 5. isteklerin ikisi de `404` aldı. İkisini ne ayırıyor?
3. 43 numaralı kitaba `{"rating": 9}` gönderen `PATCH` isteği neden `404` değil `422` alıyor?
4. Deney 1'in 9. ve 10. istekleri aynı. Yanıtları neden farklı?
5. `if available:` ile `if available is not None:` hangi istekte farklı sonuç verir? Neden?
6. Bir hata bildirildiğinde neden önce test yazıp testin kaldığını görüyoruz? Önce düzeltseydik ne eksik kalırdı?
7. Ekip arkadaşının üç değişikliğinden sonra on testin hepsi geçti. Bu, değişikliklerin doğru olduğunu gösterir mi? Deney 3'teki tablo bunun nedenini nasıl gösterdi?

### 7.1 Soruların cevapları

1. Önce isteğin yolu ve metodu bir fonksiyonla eşleştirilir. Sonra yol parametreleri, sorgu parametreleri ve gövde, fonksiyonun parametrelerindeki türlere ve kurallara göre kontrol edilir. Bunlar geçerse fonksiyonumuz çalışır ve döndürdüğü nesne yanıt modeline göre JSON'a çevrilir. `405` ilk adımdan gelir: Yol var, ama o metodu karşılayan bir fonksiyon yok.
2. Açıklamaları. 2. istekteki `Not Found` FastAPI'nin yanıtıdır: `/book/42` yolu hiçbir fonksiyonla eşleşmedi ve kodumuz hiç çalışmadı. 5. istekteki `Book not found` bizim `HTTPException` satırımızdan gelir: Yol doğru, fonksiyon çalıştı, ama kitap veritabanında yoktu.
3. Gövde, fonksiyon çağrılmadan önce kontrol edilir. Puan 5'ten büyük olduğu için istek bu adımda `422` ile reddedilir. Kitabın var olup olmadığına bakan kod fonksiyonun içinde olduğu için hiç çalışmaz.
4. Yanıt, isteğin yanında sunucudaki veriye de bağlıdır. 9. istek 57 numaralı kitabı sildi ve `204` aldı. 10. istek geldiğinde kitap artık yoktu; fonksiyon onu bulamadı ve `404` döndü.
5. `GET /books?available=false` isteğinde. `available` değeri `False` olur. `if available:` satırı `False` ile `None` değerini ayırmaz; ikisinde de süzme satırını atlar ve bütün kitaplar gelir. `is not None` ise yalnızca parametrenin hiç gönderilmediği durumda süzmeyi atlar.
6. Kalan bir test, bildirilen hatayı tekrar ürettiğimizi gösterir. Düzeltmeden sonra aynı testin geçmesi, düzeltmenin o hatayı gerçekten giderdiğini kanıtlar. Önce düzeltseydik testin bu hatayı yakalayıp yakalamadığını hiç görmezdik. Test dosyada kaldığı için hata geri dönerse yine kalır.
7. Göstermez. Testler yalnızca kontrol ettikleri davranışları korur. Tabloda `PUT` işleminin hiç testi yoktu; `GET /books` için `available` süzmesinin ve başka bir kitaba yorum yazmanın da. Değişikliklerin üçü de tam bu boş hücrelerdeki davranışları bozdu.

---

## 8. Resmî belgeler

- [FastAPI — Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/): `HTTPException` ve FastAPI'nin kendi hata yanıtları bu sayfada.
- [FastAPI — Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/): Mantıksal değer olarak kabul edilen yazımlar (`true`, `1`, `yes`, `on` ve karşılıkları) bu sayfada.
- [MDN — 405 Method Not Allowed](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/405)
- [MDN — HTTP PUT](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/PUT)
- [pytest — How to write and report assertions in tests](https://docs.pytest.org/en/stable/how-to/assert.html)
- [Python — Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing): `if` satırının hangi değerleri yanlış saydığı bu sayfada.

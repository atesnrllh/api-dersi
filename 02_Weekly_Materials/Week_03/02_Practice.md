# Hafta 03 — Uygulama Föyü

## 0. REST nedir?

REST, bir web API'sini nasıl düzenleyeceğimizi anlatan bir **kurallar bütünüdür**. Bir program, kütüphane ya da standart değildir; bir tasarım tarzıdır. Adı İngilizce *Representational State Transfer* sözcüklerinin kısaltması. Roy Fielding 2000 yılında doktora tezinde tanımladı. Fielding web'in neden bu kadar iyi çalıştığını incelemiş ve kurallarını yazıya dökmüştü.

Günlük kullanımda "REST API" denince beş kural kastedilir. Fielding'in asıl tanımındaki altı kısıt [ek notta](07_Supplement_REST_Constraints.md).

**1. Sunucudaki her şey bir kaynaktır ve her kaynağın bir yolu vardır.**

| Yol | Kaynak |
|---|---|
| `/books` | Bütün kitaplar |
| `/books/42` | 42 numaralı kitap |
| `/books/42/reviews` | O kitabın yorumları |

**2. Ne yapılacağını HTTP metodu söyler.** İş HTTP metodunda söylendiği için yolda fiile gerek kalmaz; yolda kaynağın adı yazılır.

| Yaygın biçim | Yolda fiil olan biçim |
|---|---|
| `GET /books` | `GET /getAllBooks` |
| `POST /books` | `POST /createNewBook` |

Okumak için `GET`, eklemek için `POST` kullanılır. İleriki haftalarda güncellemek için `PUT`/`PATCH`, silmek için `DELETE` gelecek.

**3. Sunucu kaynağın kendisini değil, bir temsilini gönderir.** Kitap sunucunun belleğinde bir Python sözlüğüdür; istemciye onun JSON hâli gider. Adın "Representational" (temsil) kısmı buradan gelir. Aynı kitap JSON yerine XML olarak da gönderilebilirdi; kaynak aynı, temsili farklı olurdu.

**4. Her istek kendi başına yeterlidir.** Sunucu bir önceki isteği hatırlamaz. `GET /books/42` isteği, "hangi kitap?" sorusunun cevabını kendi içinde taşır. "Az önce baktığım kitabı getir" diye bir istek olmaz. İleride giriş yapmayı gördüğümüzde bunun sonucunu göreceğiz: istemci, kim olduğunu gösteren bilgiyi her istekte yeniden gönderecek.

**5. Sonucu durum kodu söyler.** Örneğin `200` "tamam", `201` "oluşturuldu", `404` "böyle bir kaynak yok" demektir.

**Kural ile alışkanlığı ayıralım.** Yukarıdaki örneklerde iki farklı şey var: Bazıları kuraldır, bazıları REST API'lerinin çoğunun uyduğu alışkanlıklardır.

| | Kural mı? | Nereden gelir? |
|---|---|---|
| Her kaynağın kendi yolu olur | **Evet** | REST'in temel fikri |
| `GET` okur, `POST` ekler | **Evet** | HTTP standardı. HTTP metotlarının anlamı her API'de aynıdır. |
| Koleksiyonun adı çoğul olur: `/books` | **Hayır**, alışkanlık | `/book` ya da `/kitaplar` da REST'e aykırı değildir. |
| Tek kitap koleksiyonun altında durur: `/books/42` | **Hayır**, alışkanlık | Çok yaygın, ama zorunlu değil. |
| Yolda fiil olmaz | **Hayır**, güçlü bir alışkanlık | İşi HTTP metodu söylediği için yoldaki fiil gereksiz kalır; yine de yasak değildir. |

Alışkanlıklar zorunlu değildir. Ama REST API'lerinin çoğu bunlara uyduğu için, hiç görmediğimiz bir API'nin yollarını da çoğu zaman tahmin edebiliriz.

**Ayırt edici nokta:** SOAP ve GraphQL'de istekler genellikle tek bir yola (`/BookService`, `/graphql`) ve `POST` ile gider. Ne istendiği mesajın içinde yazar. REST'te ise ne istendiğini HTTP metodu ve yol birlikte söyler: `GET /books/42`.

**Bizim API'miz zaten REST'e uygun.** Hafta 1 ve 2'de yazdığımız API'de bir tek `/book` yolu, koleksiyonun adını çoğul yazma alışkanlığına uymuyor. Deney 2 de onu `/books` yapıyor. Yani REST'i ilk iki haftada farkında olmadan uygulamış olduk; bu hafta bu kurallara bir ad veriyoruz.

### 0.1 Başlangıç dosyaları

Hafta 2'nin sonundaki dosyalarla başla:

| Dosya | Hafta 2 föyündeki yeri |
|---|---|
| `server.py` | 4.2: Hafta 2'nin son `server.py` dosyası |
| `client.py` | 4.3: `Location` başlığını okuyup kitabı geri isteyen istemci |

---

## Deney 1 — Kitap kataloğunda hangi kaynaklar ve işlemler var?

**Amaç:** Yazdığımız API'yi kaynaklar ve işlemler açısından okumak.

### 1.1 Kaynak, koleksiyon ve işlem

| Kavram | Anlamı | Kitap kataloğunda |
|---|---|---|
| **Kaynak** | Sunucuda bir yolu olan şey | Bir kitap: `/book/42` |
| **Koleksiyon** | Aynı türden kaynakların topluluğu | Bütün kitaplar: `/book` |
| **İşlem** | Bir kaynak üzerinde yapılan iş. Bizim API'mizde **HTTP metodu + yol** ile belirtilir. | `GET /book/42`: 42 numaralı kitabı oku |

Hafta 2'nin sonundaki sunucumuzda üç işlem var:

| HTTP metodu | Yol | Fonksiyon | Hangi kaynak? | Ne yapar? |
|---|---|---|---|---|
| `GET` | `/book` | `get_books` | Kitap koleksiyonu | Kitapları listeler; arama ve filtre uygulayabilir. |
| `POST` | `/book` | `create_book` | Kitap koleksiyonu | Koleksiyona yeni bir kitap ekler. |
| `GET` | `/book/{book_id}` | `get_book` | Tek bir kitap | Kimliği verilen kitabı döndürür. |

Dikkat et: İki işlem aynı yolu (`/book`) kullanıyor. Yol **hangi kaynağın** istendiğini, HTTP metodu **onunla ne yapılacağını** söylüyor.

Tabloda `GET` ile `get_books` yan yana duruyor. "get" kelimesi bu derste dört yerde geçer; bunlar ayrı şeylerdir:

**1. Mesajın içinde: HTTP metodu**

| Yazım | Ne? |
|---|---|
| `GET` | Sunucuya giden mesajın ilk kelimesi. İsteğin türünü söyler: "oku". Bir kod değildir; curl, Postman ve HTTPX aynı kelimeyi gönderir. |

**2. Python kodunda: "get" geçen üç ad**

| Yazım | Nerede? | Ne iş yapar? |
|---|---|---|
| `httpx.get(...)` | İstemcide | Başında `GET` yazan mesajı hazırlar ve sunucuya **gönderir**. |
| `@app.get("/book")` | Sunucuda | Başında `GET` yazan mesaj gelince hangi fonksiyonun çalışacağını FastAPI'ye **bildirir**. FastAPI'nin metodudur. |
| `def get_books(...)` | Sunucuda | O mesaj gelince **çalışan** bizim fonksiyonumuz. Adındaki `get` kelimesini biz seçtik. |

### 1.2 Koleksiyonu ve tek bir kitabı iste

Hafta 2'nin sunucusunu başlat. Koleksiyonu ve tek bir kitabı curl ile iste:

```bash
curl http://127.0.0.1:8000/book
```

```text
[{"id":42,"title":"API Yolculuğu","author":{"first_name":"Deniz","last_name":"Kaya"},"available":true,"tags":["software","education"],"rating":null},{"id":57,"title":"Veriyle İlk Adımlar","author":{"first_name":"Ece","last_name":"Yılmaz"},"available":false,"tags":[],"rating":0},{"id":73,"title":"Python ile Web API","author":{"first_name":"Can","last_name":"Demir"},"available":true,"tags":["python","api"],"rating":4.5}]
```

```bash
curl http://127.0.0.1:8000/book/42
```

```text
{"id":42,"title":"API Yolculuğu","author":{"first_name":"Deniz","last_name":"Kaya"},"available":true,"tags":["software","education"],"rating":null}
```

```python
# client.py
import httpx

response = httpx.get("http://127.0.0.1:8000/book")
print(response.text)

response = httpx.get("http://127.0.0.1:8000/book/42")
print(response.text)
```

| İstek | Yanıtın JSON türü | Neden? |
|---|---|---|
| `GET /book` | Dizi `[...]` | Koleksiyon birden çok kitap içerir. |
| `GET /book/42` | Nesne `{...}` | Tek bir kitap istendi. |

> **Ana fikir:** Bir API'yi tasarlamak iki soruya cevap vermektir:
>
> 1. **Hangi kaynaklar var?** Bizim API'mizde iki kaynak var: bütün kitaplar (koleksiyon) ve tek bir kitap. Her kaynağın bir yolu vardır: `/book` ve `/book/42`.
> 2. **Her kaynakla ne yapılabilir?** Bunu HTTP metodu söyler: Kitap koleksiyonunu `GET` ile okuruz, ona `POST` ile yeni kitap ekleriz; tek bir kitabı `GET` ile okuruz.
>
> Yol ile HTTP metodu bir araya gelince bir işlem ortaya çıkar: `GET /book` "kitapları listele", `POST /book` "kitap ekle", `GET /book/42` "42 numaralı kitabı getir" demektir.

---

## Deney 2 — Koleksiyonun adı neden çoğul olmalı?

**Amaç:** Yolları REST'te yaygın olan biçime getirmek: koleksiyon için `/books`, tek kitap için `/books/42`.

### 2.1 Neden `/books`?

Yol, kaynağın adıdır. `/book` yolu tek bir kitabı mı, bütün kitapları mı anlatıyor, adından anlaşılmıyor. Çoğul ad kullanınca yol kendini anlatır:

| Yol | Okunuşu |
|---|---|
| `/books` | Kitaplar koleksiyonu |
| `/books/42` | Kitaplar koleksiyonundaki 42 numaralı kitap |

REST'te koleksiyonların adı genellikle çoğul yazılır. Bu bir zorunluluk değil, yaygın bir alışkanlıktır. Ama bir API içinde **tutarlı** olmak önemlidir: Bir yerde `/books`, başka bir yerde `/user` yazmayız.

### 2.2 Sunucuda yolları değiştir

`server.py` dosyasında yolun geçtiği dört satırı değiştir:

| Eski satır | Yeni satır |
|---|---|
| `@app.get("/book")` | `@app.get("/books")` |
| `@app.get("/book/{book_id}")` | `@app.get("/books/{book_id}")` |
| `@app.post("/book", status_code=201)` | `@app.post("/books", status_code=201)` |
| `response.headers["Location"] = f"/book/{new_id}"` | `response.headers["Location"] = f"/books/{new_id}"` |

`server.py` dosyasında değişen yerler:

```python
@app.get("/books")
def get_books(search: str = "", available: bool | None = None):
    ...


@app.get("/books/{book_id}")
def get_book(book_id: int):
    ...


@app.post("/books", status_code=201)
def create_book(book_data: BookCreate, response: Response):
    ...
    response.headers["Location"] = f"/books/{new_id}"
    ...
```

Fonksiyonların adları ve içindeki kod değişmiyor; yalnızca yollar değişiyor. `server.py` dosyasının bu haftaki tam hâlini Deney 5'in sonunda (5.4) bulabilirsin.

### 2.3 Eski yol artık çalışmıyor

Sunucuyu yeniden başlat ve eski yolu iste:

```bash
curl -i http://127.0.0.1:8000/book
```

```text
HTTP/1.1 404 Not Found
date: Thu, 22 Oct 2026 05:46:36 GMT
server: uvicorn
content-length: 22
content-type: application/json

{"detail":"Not Found"}
```

Sunucuda artık `/book` diye bir yol yok. Eski yolu kullanan bütün istemciler bu yüzden çalışmaz hâle gelir. API'yi değiştirirken eski istemcileri bozmamayı 13. haftada ele alacağız.

### 2.4 İstemciyi yeni yollara göre güncelle

`client.py` dosyasında `"/book"` geçen iki satırı değiştir:

| Eski satır | Yeni satır |
|---|---|
| `response = httpx.post(base_url + "/book", json=new_book)` | `response = httpx.post(base_url + "/books", json=new_book)` |
| `list_response = httpx.get(base_url + "/book")` | `list_response = httpx.get(base_url + "/books")` |

`client.py` dosyasında değişen yerler:

```python
try:
    # Yeni kitap: POST ile gönder.
    response = httpx.post(base_url + "/books", json=new_book)
    ...

    # Kitap listesi: toplam sayıyı kontrol et.
    list_response = httpx.get(base_url + "/books")
    ...
```

İstemciyi çalıştır:

```text
Status code: 201
Location: /books/74
Read status: 200
Book id: 74
Book title: HTTP ile Yeni Bir Kitap
Book count: 4
```

`Location` başlığı da artık `/books/74` geliyor, çünkü sunucuda o satırı da değiştirdik. Kitabı geri okuyan `httpx.get(base_url + location)` satırını ise değiştirmedik: Bu satır yolu `Location` başlığından alıyor, bu yüzden kitabı `/books/74` yolundan okudu.

> **Ana fikir:** Yol, kaynağın adıdır. Koleksiyon için çoğul bir ad (`/books`), koleksiyondaki tek bir kitap için onun altında bir kimlik (`/books/42`) kullanırız. Yollar değişince eski istemciler bozulur; bu yüzden yollar baştan dikkatle seçilir.

---

## Deney 3 — Yolda neden fiil değil isim kullanılır?

**Amaç:** Aynı işleri yapan ama yollarında fiil kullanan bir API ile kendi API'mizi karşılaştırmak.

### 3.1 İşlem adlarını yola yazan bir sunucu

Aşağıdaki sunucu çalışır, ama REST API'lerindeki yaygın alışkanlıklara uymaz. Bunu denemek için proje klasöründe `bad_server.py` adlı ayrı bir dosya oluştur:

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {"id": 42, "title": "API Yolculuğu"},
    {"id": 57, "title": "Veriyle İlk Adımlar"}
]


@app.get("/getAllBooks")
def get_all_books():
    return books


@app.get("/getBookById")
def get_book_by_id(id: int):
    for book in books:
        if book["id"] == id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")


@app.post("/createNewBook")
def create_new_book(title: str):
    created_book = {"id": books[-1]["id"] + 1, "title": title}
    books.append(created_book)
    return created_book
```

Kendi sunucunu **Ctrl+C** ile durdur ve bu sunucuyu başlat. Dosyanın adı `bad_server.py` olduğu için komut da değişir:

```bash
python -m uvicorn bad_server:app
```

Üç işlemi curl ile dene:

```bash
curl http://127.0.0.1:8000/getAllBooks
```

```text
[{"id":42,"title":"API Yolculuğu"},{"id":57,"title":"Veriyle İlk Adımlar"}]
```

```bash
curl "http://127.0.0.1:8000/getBookById?id=42"
```

```text
{"id":42,"title":"API Yolculuğu"}
```

```bash
curl -X POST "http://127.0.0.1:8000/createNewBook?title=Yeni%20Kitap"
```

```text
{"id":58,"title":"Yeni Kitap"}
```

Bütün işlemler çalışıyor. Adresteki `%20`, boşluk karakterinin adreste yazılış biçimidir. HTTPX'in boşluğu nasıl gönderdiği [ek notta](05_Supplement_Space_Encoding.md).

### 3.2 İki tasarımı karşılaştır

| İşlem | `bad_server.py` | Bizim API'miz |
|---|---|---|
| Bütün kitaplar | `GET /getAllBooks` | `GET /books` |
| Tek kitap | `GET /getBookById?id=42` | `GET /books/42` |
| Yeni kitap | `POST /createNewBook?title=Yeni%20Kitap` | `POST /books`, kitap bilgileri gövdede |

`bad_server.py` tasarımındaki sorunlar:

| Sorun | Açıklama |
|---|---|
| Fiil iki kez yazılıyor | `GET /getAllBooks` isteğinde "getir" anlamı hem HTTP metodunda (`GET`) hem yolda (`get`) var. REST'te işi HTTP metodu söyler, yol yalnızca kaynağı adlandırır. |
| Her işlem için yeni bir ad gerekiyor | `getAllBooks`, `getBookById`, `createNewBook`… İstemci bütün adları o API'nin belgesinden tek tek öğrenmek zorundadır: `getBook` mu, `getBookById` mi, `fetchBook` mu? |
| Kitap bilgileri adreste gidiyor | Yeni kitabın adı sorgu bölümünde (`?title=...`) gönderiliyor. Bir kitabın bütün alanlarını (yazar, etiketler…) adreste göndermek zordur; bu bilgiler gövdeye aittir. İki mesajın farkı [ek notta](06_Supplement_Query_vs_Body.md). |

Denemeden sonra `bad_server.py` sunucusunu durdur ve kendi sunucunu yeniden başlat.

> **Ana fikir:** Bir API'nin çalışması, iyi tasarlandığı anlamına gelmez. REST'te **yol kaynağı (ismi), HTTP metodu yapılacak işi (fiili)** söyler. REST API'lerinin çoğu aynı yol alışkanlıklarına uyduğu için istemci, yolları tek tek ezberlemek yerine aynı kalıbı her kaynakta kullanabilir.

Yaygın REST alışkanlığıyla yollar aynı kalıba uyar:

| İş | Kitaplar | Yazarlar (aynı kalıp) |
|---|---|---|
| Hepsini listele | `GET /books` | `GET /authors` |
| Birini getir | `GET /books/42` | `GET /authors/7` |
| Yeni ekle | `POST /books` | `POST /authors` |

Yolda fiil kullanan API'lerde de bir kalıp kurulabilir, ama bu kalıbı her API'yi yazan kişi kendisi seçer. Aynı işi yapan üç API üç farklı ad kullanabilir:

| İş | API 1 | API 2 | API 3 | Yaygın REST biçimi |
|---|---|---|---|---|
| Kitapları listele | `GET /getAllBooks` | `GET /listBooks` | `GET /fetchBookList` | `GET /books` |
| Bir kitabı getir | `GET /getBookById?id=42` | `GET /bookDetail?id=42` | `GET /fetchBook?bookId=42` | `GET /books/42` |

---

## Deney 4 — GET isteği neden veriyi değiştirmemeli?

**Amaç:** GET ile veri değiştiren bir işlemin neden sorun çıkardığını görmek.

### 4.1 GET ile kitap ekleyen bir sunucu

Aşağıdaki sunucuda kitap eklemek için GET kullanılıyor. Denemek için ayrı bir `bad_get_server.py` dosyası oluştur:

```python
from fastapi import FastAPI

app = FastAPI()

books = [
    {"id": 42, "title": "API Yolculuğu"},
    {"id": 57, "title": "Veriyle İlk Adımlar"}
]


@app.get("/books")
def get_books():
    return books


@app.get("/books/add")
def add_book(title: str):
    created_book = {"id": books[-1]["id"] + 1, "title": title}
    books.append(created_book)
    return created_book
```

Kendi sunucunu durdur ve bu sunucuyu başlat:

```bash
python -m uvicorn bad_get_server:app
```

Aynı adresi **iki kez** iste. İkinci istek, tarayıcıda sayfayı yenilemekle aynı şeydir:

```bash
curl "http://127.0.0.1:8000/books/add?title=Yeni%20Kitap"
```

```text
{"id":58,"title":"Yeni Kitap"}
```

```bash
curl "http://127.0.0.1:8000/books/add?title=Yeni%20Kitap"
```

```text
{"id":59,"title":"Yeni Kitap"}
```

Şimdi listeyi iste:

```bash
curl http://127.0.0.1:8000/books
```

```text
[{"id":42,"title":"API Yolculuğu"},{"id":57,"title":"Veriyle İlk Adımlar"},{"id":58,"title":"Yeni Kitap"},{"id":59,"title":"Yeni Kitap"}]
```

Aynı kitap iki kez eklendi.

### 4.2 Bu neden sorun?

GET isteği, "yalnızca oku" anlamına gelir. Bu yüzden birçok program GET isteğini **kullanıcıya sormadan** tekrar gönderir:

- Tarayıcı, sayfa yenilendiğinde GET isteğini yeniden gönderir.
- Mesajlaşma uygulamaları, paylaşılan bir bağlantının önizlemesini göstermek için o adrese kendileri GET isteği gönderebilir.

Bu programlar GET isteğinin hiçbir şeyi değiştirmeyeceğini varsayar. GET ile kitap ekleyen bir API'de bunların her biri istemeden yeni bir kayıt oluşturur.

HTTP standardı da GET'i **güvenli (safe)** bir HTTP metodu olarak tanımlar: GET isteği sunucudaki veriyi değiştirmemelidir.

| HTTP metodu | Veriyi değiştirir mi? | Tekrar gönderilirse? | Derste |
|---|---|---|---|
| `GET` | Hayır | Bir şey değişmez; aynı veri yeniden okunur. | Hafta 1 |
| `POST` | Evet: yeni kayıt oluşturur | Bizim API'mizde her seferinde yeni bir kayıt oluşur. | Hafta 2 |
| `PUT`, `PATCH`, `DELETE` | Evet: günceller ya da siler | Hafta 4'te göreceğiz. | Hafta 4 |

Denemeden sonra `bad_get_server.py` sunucusunu durdur ve kendi sunucunu yeniden başlat.

> **Ana fikir:** GET yalnızca okumak içindir ve sunucudaki veriyi değiştirmemelidir. Programlar GET isteğini kendiliğinden tekrar gönderebildiği için, veri değiştiren işlemler POST gibi başka HTTP metotlarıyla yapılır.

---

## Deney 5 — Bir kitabın yorumlarını okuma ve ekleme

**Amaç:** Hafta 1 ve 2'de öğrendiğimiz okuma ve ekleme işlemlerini **yeni bir kaynak** için yazmak: kitapların yorumları.

### 5.1 Yorumlar için yollar

Her yorum bir kitaba aittir. Bu ilişkiyi yolda da gösteririz: Bir kitabın yorumları, o kitabın yolunun altında durur.

| HTTP metodu | Yol | Ne yapar? |
|---|---|---|
| `GET` | `/books/{book_id}/reviews` | Kitabın yorumlarını listeler. |
| `POST` | `/books/{book_id}/reviews` | Kitaba yeni bir yorum ekler. |

`/books/42/reviews` şöyle okunur: "Kitaplar koleksiyonundaki 42 numaralı kitabın yorumları." Bir kaynağın altında duran bu tür kaynaklara **iç içe kaynak** denir. Yorumları ayrı bir koleksiyon olarak tasarlamak da mümkündür; farkı [ek notta](04_Supplement_Nested_Resources.md) anlatıyoruz.

### 5.2 Sunucuya yorumları ekle

`server.py` dosyasına üç şey ekliyoruz.

**1. Yorum modeli.** `BookCreate` sınıfının altına ekle:

```python
class ReviewCreate(BaseModel):
    reader: str
    comment: str
    score: int
```

Puanın 1 ile 5 arasında olması gibi kuralları 5. haftada ekleyeceğiz; şimdilik her tam sayı kabul edilir.

**2. Yorum listesi.** `books` listesinin altına ekle. Sunucu bu tek yorumla başlayacak:

```python
reviews = [
    {
        "id": 1,
        "book_id": 42,
        "reader": "Ece",
        "comment": "Konuları örneklerle anlatıyor.",
        "score": 5
    }
]
```

`book_id` alanı, yorumun hangi kitaba ait olduğunu gösterir.

**3. İki yeni işlem.** Dosyanın sonuna ekle:

```python
# Kitabın yorumları: kitap yoksa 404.
@app.get("/books/{book_id}/reviews")
def get_reviews(book_id: int):
    book_exists = False
    for book in books:
        if book["id"] == book_id:
            book_exists = True

    if not book_exists:
        raise HTTPException(status_code=404, detail="Book not found")

    results = []
    for review in reviews:
        if review["book_id"] == book_id:
            results.append(review)

    return results


# Yeni yorum: kitaba ekler, 201 döner.
@app.post("/books/{book_id}/reviews", status_code=201)
def create_review(book_id: int, review_data: ReviewCreate):
    book_exists = False
    for book in books:
        if book["id"] == book_id:
            book_exists = True

    if not book_exists:
        raise HTTPException(status_code=404, detail="Book not found")

    new_id = 1
    for review in reviews:
        if review["id"] >= new_id:
            new_id = review["id"] + 1

    created_review = review_data.model_dump()
    created_review["id"] = new_id
    created_review["book_id"] = book_id
    reviews.append(created_review)
    return created_review
```

| Kod | Ne yapar? |
|---|---|
| `book_exists` | Bir **bayrak** değişkenidir. Başta `False`'tur; döngüde kitap bulunursa `True` olur. Döngü bitince bayrağa bakılır: Kitap yoksa yorumlara hiç geçmeden `404` verilir. |
| `get_reviews` içindeki ikinci döngü | Yalnızca `book_id` değeri istenen kitapla aynı olan yorumları toplar. Hafta 1'deki `get_books` aramasıyla aynı kalıp. |
| `create_review` içindeki kimlik hesabı | Yeni yoruma, en büyük yorum kimliğinin bir fazlasını verir. Hafta 2'deki `create_book` ile aynı kalıp. |
| `created_review["book_id"] = book_id` | Yorumun hangi kitaba ait olduğunu yoldan alıp yorumun `book_id` alanına yazar. İstemci bunu gövdede göndermez. |

`get_book` fonksiyonunda kitabı bulunca hemen `return` ediyorduk, çünkü iş orada bitiyordu. Burada kitabı bulmak işin yalnızca ilk adımı; asıl iş yorumlarla ilgili. Bu yüzden "kitap var mı?" sorusunun cevabını bayrakta saklıyor, döngüden sonra kullanıyoruz.

Bu kontrol iki fonksiyonda da aynen tekrar ediyor. Şimdilik her fonksiyonun tek başına okunabilmesi için böyle bırakıyoruz.

### 5.3 Bir fonksiyon, üç ayrı yerden bilgi alabilir

`create_review` fonksiyonu bilgiyi iki farklı yerden alıyor. Hafta 1'deki sorgu parametresiyle birlikte, bir fonksiyonun bilgi alabileceği üç yeri de görmüş olduk:

| Fonksiyon parametresi | Bilgi nereden gelir? | FastAPI bunu nereden anlar? | İlk gördüğümüz yer |
|---|---|---|---|
| `book_id: int` | Yoldan: `/books/42/reviews` | Adı yoldaki `{book_id}` ile aynı | Hafta 1 |
| `search: str = ""` | Sorgudan: `/books?search=API` | Yolda yok ve basit bir türde | Hafta 1 |
| `review_data: ReviewCreate` | İsteğin gövdesinden | Türü bir Pydantic modeli | Hafta 2 |

### 5.4 `server.py` dosyasının bu haftaki son hâli

```python
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel


class Author(BaseModel):
    first_name: str
    last_name: str


class BookCreate(BaseModel):
    title: str
    author: Author
    available: bool
    tags: list[str]
    rating: float | None = None


class ReviewCreate(BaseModel):
    reader: str
    comment: str
    score: int


app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": {
            "first_name": "Deniz",
            "last_name": "Kaya"
        },
        "available": True,
        "tags": ["software", "education"],
        "rating": None
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": {
            "first_name": "Ece",
            "last_name": "Yılmaz"
        },
        "available": False,
        "tags": [],
        "rating": 0
    },
    {
        "id": 73,
        "title": "Python ile Web API",
        "author": {
            "first_name": "Can",
            "last_name": "Demir"
        },
        "available": True,
        "tags": ["python", "api"],
        "rating": 4.5
    }
]

reviews = [
    {
        "id": 1,
        "book_id": 42,
        "reader": "Ece",
        "comment": "Konuları örneklerle anlatıyor.",
        "score": 5
    }
]


# Kitap listesi: ada ve ödünç durumuna göre süzülebilir.
@app.get("/books")
def get_books(search: str = "", available: bool | None = None):
    results = []

    for book in books:
        title_matches = search.casefold() in book["title"].casefold()
        availability_matches = (
            available is None or book["available"] == available
        )

        if title_matches and availability_matches:
            results.append(book)

    return results


# Tek kitap: kimliğe göre bulur, yoksa 404.
@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")


# Yeni kitap: listeye ekler, 201 ve Location döner.
@app.post("/books", status_code=201)
def create_book(book_data: BookCreate, response: Response):
    new_id = 1
    for book in books:
        if book["id"] >= new_id:
            new_id = book["id"] + 1

    created_book = book_data.model_dump()
    created_book["id"] = new_id
    books.append(created_book)
    response.headers["Location"] = f"/books/{new_id}"
    return created_book


# Kitabın yorumları: kitap yoksa 404.
@app.get("/books/{book_id}/reviews")
def get_reviews(book_id: int):
    book_exists = False
    for book in books:
        if book["id"] == book_id:
            book_exists = True

    if not book_exists:
        raise HTTPException(status_code=404, detail="Book not found")

    results = []
    for review in reviews:
        if review["book_id"] == book_id:
            results.append(review)

    return results


# Yeni yorum: kitaba ekler, 201 döner.
@app.post("/books/{book_id}/reviews", status_code=201)
def create_review(book_id: int, review_data: ReviewCreate):
    book_exists = False
    for book in books:
        if book["id"] == book_id:
            book_exists = True

    if not book_exists:
        raise HTTPException(status_code=404, detail="Book not found")

    new_id = 1
    for review in reviews:
        if review["id"] >= new_id:
            new_id = review["id"] + 1

    created_review = review_data.model_dump()
    created_review["id"] = new_id
    created_review["book_id"] = book_id
    reviews.append(created_review)
    return created_review
```

### 5.5 İstemci: yorumları oku, yorum ekle, tekrar oku

`client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"

new_review = {
    "reader": "Can",
    "comment": "İlk API projemi bu kitapla yazdım.",
    "score": 4
}

try:
    # Kitabın yorumları: eklemeden önce oku.
    response = httpx.get(base_url + "/books/42/reviews")
    print("Reviews before:", response.status_code, len(response.json()))

    # Yeni yorum: 42 numaralı kitaba ekle.
    response = httpx.post(base_url + "/books/42/reviews", json=new_review)
    print("Create status:", response.status_code)
    print("Created review:", response.text)

    # Kitabın yorumları: ekledikten sonra tekrar oku.
    response = httpx.get(base_url + "/books/42/reviews")
    print("Reviews after:", response.status_code, len(response.json()))

    # Olmayan kitap: 404 beklenir.
    response = httpx.get(base_url + "/books/99/reviews")
    print("Book 99:", response.status_code, response.text)
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Sunucuyu yeniden başlat ve istemciyi **bir kez** çalıştır:

```text
Reviews before: 200 1
Create status: 201
Created review: {"reader":"Can","comment":"İlk API projemi bu kitapla yazdım.","score":4,"id":2,"book_id":42}
Reviews after: 200 2
Book 99: 404 {"detail":"Book not found"}
```

| Satır | Anlamı |
|---|---|
| `Reviews before: 200 1` | Kitabın başlangıçta bir yorumu var. |
| `Create status: 201` | Yeni yorum eklendi. |
| `Created review` | Sunucu yoruma `2` kimliğini verdi ve `book_id` alanına yoldaki `42`'yi yazdı. |
| `Reviews after: 200 2` | Kitabın artık iki yorumu var. |
| `Book 99: 404` | 99 numaralı kitap yok; bu yüzden yorumları da yok. |

> **Ana fikir:** Yeni bir kaynak eklemek için yeni bir kalıp öğrenmedik. Kitaplarda kullandığımız okuma ve ekleme işlemlerini yorumlara uyguladık. Yorumlar bir kitaba ait olduğu için yolları da kitabın yolunun altında durur: `/books/42/reviews`.

---

## Deney 6 — API'mizi `README.md` ile belgele

**Amaç:** API'mizi kullanacak birine, hangi istekleri nasıl göndereceğini örneklerle anlatmak.

### 6.1 Neden belgeleriz?

İstemciyi yazan kişi sunucunun kodunu görmeyebilir. Hangi yolların olduğunu, hangi HTTP metoduyla ne gönderileceğini ve ne cevap geleceğini ancak bir belgeden öğrenebilir. Bu belgeye **API belgesi (dokümantasyon)** denir.

Bu hafta belgeyi elle, proje klasöründe bir `README.md` dosyası olarak yazacağız. `README.md`, bir proje klasörünün tanıtım dosyasıdır; GitHub'da bir klasör açılınca ilk bu dosya görünür. Her örneği önce kendimiz curl ile çalıştıracak, sonra gerçek yanıtı belgeye koyacağız.

### 6.2 Belgenin başlangıcı

Proje klasöründe `README.md` dosyasını oluştur ve şu içerikle başla. Sunucuyu yeniden başlat, örneklerdeki istekleri curl ile gönder ve gelen yanıtları belgedekilerle karşılaştır.

Aşağıdaki örneğin başındaki ve sonundaki dört ters tırnaklı satırlar (` ```` `) yalnızca bu föyde içeriği göstermek içindir; onları `README.md` dosyasına kopyalama.

````markdown
# Kitap Kataloğu API'si

Sunucu adresi: `http://127.0.0.1:8000`

## İşlemler

| HTTP metodu | Yol | Ne yapar? |
|---|---|---|
| `GET` | `/books` | Kitapları listeler. `search` ve `available` sorgu parametreleriyle filtrelenebilir. |
| `GET` | `/books/{book_id}` | Kimliği verilen kitabı döndürür. |
| `POST` | `/books` | Yeni kitap ekler. |
| `GET` | `/books/{book_id}/reviews` | Kitabın yorumlarını listeler. |
| `POST` | `/books/{book_id}/reviews` | Kitaba yeni yorum ekler. |

## Örnekler

### Tek bir kitabı okumak

```bash
curl http://127.0.0.1:8000/books/42
```

Yanıt: `200 OK`

```json
{"id":42,"title":"API Yolculuğu","author":{"first_name":"Deniz","last_name":"Kaya"},"available":true,"tags":["software","education"],"rating":null}
```

Kitap yoksa yanıt `404 Not Found` olur: `{"detail":"Book not found"}`

### Yeni kitap eklemek

```bash
curl -i -X POST http://127.0.0.1:8000/books -H "Content-Type: application/json" -d '{"title": "HTTP ile Yeni Bir Kitap", "author": {"first_name": "Ada", "last_name": "Yıldız"}, "available": true, "tags": ["http", "python"], "rating": null}'
```

Yanıt: `201 Created`. `Location` başlığı yeni kitabın yolunu verir: `/books/74`

```json
{"title":"HTTP ile Yeni Bir Kitap","author":{"first_name":"Ada","last_name":"Yıldız"},"available":true,"tags":["http","python"],"rating":null,"id":74}
```

`title`, `author`, `available` ve `tags` alanları zorunludur. Eksik ya da yanlış türde bir alan gönderilirse yanıt `422 Unprocessable Entity` olur.

### Bir kitabın yorumlarını okumak

```bash
curl http://127.0.0.1:8000/books/42/reviews
```

Yanıt: `200 OK`

```json
[{"id":1,"book_id":42,"reader":"Ece","comment":"Konuları örneklerle anlatıyor.","score":5}]
```
````

### 6.3 Belgeyi tamamla

Belgede iki işlemin örneği eksik: bütün kitapları listelemek ve yorum eklemek. Bu ikisini de aynı biçimde ekle:

1. İsteği curl ile kendin gönder.
2. Komutu ve gerçek yanıtı belgeye koy.
3. Yanıtın durum kodunu ve varsa hata durumunu yaz.

> **Ana fikir:** API belgesi, API'yi kullanacak kişiye her işlemin yolunu, HTTP metodunu, ne göndereceğini ve ne cevap alacağını söyler. Belgedeki örnekler, gerçekten gönderilmiş isteklerden ve gelen yanıtlardan alınmalıdır.

---

## Deney 7 — Aynı istek REST, SOAP ve GraphQL'de nasıl görünür?

**Amaç:** REST'in tek yaklaşım olmadığını görmek ve üç yaklaşımı aynı istek üzerinden karşılaştırmak.

Bu deneydeki SOAP ve GraphQL mesajları **örnektir**; derste bu yaklaşımlarla bir sunucu kurmayacağız. Amaç, aynı isteğin nasıl yazıldığını yan yana görmektir: "42 numaralı kitabın adını ve yazarını getir." Mesajların satır satır açıklaması [ek notta](03_Supplement_SOAP_GraphQL.md).

### 7.1 REST

```http
GET /books/42 HTTP/1.1
Host: 127.0.0.1:8000
```

Yanıt (bizim API'mizin gerçek yanıtı):

```json
{"id":42,"title":"API Yolculuğu","author":{"first_name":"Deniz","last_name":"Kaya"},"available":true,"tags":["software","education"],"rating":null}
```

### 7.2 SOAP

SOAP'ta bütün istekler genellikle aynı yola (`/BookService`), POST ile gönderilir. Hangi işlemin istendiği XML biçimindeki mesajın içinde yazar:

```http
POST /BookService HTTP/1.1
Content-Type: text/xml; charset=utf-8
SOAPAction: "GetBook"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetBook>
      <BookId>42</BookId>
    </GetBook>
  </soap:Body>
</soap:Envelope>
```

Yanıt da XML'dir:

```xml
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetBookResponse>
      <Book>
        <Id>42</Id>
        <Title>API Yolculuğu</Title>
        <AuthorFirstName>Deniz</AuthorFirstName>
        <AuthorLastName>Kaya</AuthorLastName>
      </Book>
    </GetBookResponse>
  </soap:Body>
</soap:Envelope>
```

### 7.3 GraphQL

GraphQL'de de istekler genellikle tek bir yola (`/graphql`), POST ile gönderilir. İstemci, istediği alanları bir **sorgu** ile kendisi seçer:

```http
POST /graphql HTTP/1.1
Content-Type: application/json

{"query": "{ book(id: 42) { title author { first_name last_name } } }"}
```

Yanıt JSON'dur ve yalnızca sorguda istenen alanları içerir:

```json
{"data": {"book": {"title": "API Yolculuğu", "author": {"first_name": "Deniz", "last_name": "Kaya"}}}}
```

### 7.4 Üç yaklaşımın karşılaştırması

|  | REST | SOAP | GraphQL |
|---|---|---|---|
| İşlem nasıl belirtilir? | HTTP metodu ve yol: `GET /books/42` | Mesajın içindeki işlem adı: `GetBook` | Sorgu metni: `book(id: 42)` |
| Yol | Her kaynak için ayrı yol: `/books/42` | Genellikle tek yol: `/BookService` | Genellikle tek yol: `/graphql` |
| HTTP metodu | İşe göre: GET, POST… | Genellikle POST | Genellikle POST |
| Veri biçimi | Genellikle JSON | XML | JSON |
| Yanıtta hangi alanlar gelir? | Sunucunun belirlediği alanlar | Sunucunun belirlediği alanlar | İstemcinin sorguda istediği alanlar |
| Nerede karşılaşılır? | Bugünkü web API'lerinin çoğu | Bankacılık gibi alanlardaki daha eski kurumsal sistemler | Farklı verileri tek istekte almak isteyen web ve mobil uygulamalar |

REST yanıtında kitabın bütün alanları geldi; `tags` ve `rating` alanlarını istemesek de. GraphQL'de ise istemci yalnızca istediği alanları aldı. Buna karşılık GraphQL'de sunucuyu kurmak ve sorguları işlemek daha fazla iş gerektirir.

> **Ana fikir:** REST, SOAP ve GraphQL aynı işi farklı biçimlerde ister. REST'te işi HTTP metodu ve yol, SOAP'ta XML mesajındaki işlem adı, GraphQL'de istemcinin yazdığı sorgu belirtir. Bu derste REST yaklaşımıyla devam ediyoruz.

---

## 8. Ek çalışmalar: curl, `/docs` ve kendi kodunu yazmak

### 8.1 Yorumu curl ile eklemek

Sunucuyu yeniden başlat ve 42 numaralı kitaba curl ile bir yorum ekle:

```bash
curl -i -X POST http://127.0.0.1:8000/books/42/reviews -H "Content-Type: application/json" -d '{"reader": "Can", "comment": "İlk API projemi bu kitapla yazdım.", "score": 4}'
```

```text
HTTP/1.1 201 Created
date: Thu, 22 Oct 2026 05:24:32 GMT
server: uvicorn
content-length: 95
content-type: application/json

{"reader":"Can","comment":"İlk API projemi bu kitapla yazdım.","score":4,"id":2,"book_id":42}
```

Yanıtta `Location` başlığı yok, çünkü `create_review` fonksiyonunda bu başlığı eklemedik. 8.3'te bunu sen ekleyeceksin.

PowerShell kullanıyorsan Hafta 2 föyündeki 7.2.4 bölümüne bak: `curl.exe` kullan ve gövdeyi bir dosyadan gönder.

### 8.2 FastAPI'nin `/docs` sayfasına kısa bir bakış

Sunucu çalışırken tarayıcıda şu adresi aç:

```text
http://127.0.0.1:8000/docs
```

FastAPI, yazdığımız işlemlerden bu sayfayı **kendisi** oluşturur. Sayfada şu beş işlem listelenir:

```text
GET /books
POST /books
GET /books/{book_id}
GET /books/{book_id}/reviews
POST /books/{book_id}/reviews
```

Bir işleme tıklayıp **Try it out** düğmesiyle tarayıcıdan istek gönderebilirsin. Bu sayfayı ayrıntılı olarak 13. haftada inceleyeceğiz. 6. deneydeki `README.md` ile farkı şudur: `README.md` belgesini biz yazıyoruz; `/docs` sayfasını ise FastAPI koddan üretiyor.

### 8.3 Kendin yaz: tek bir yorumu okumak

Şimdiye kadar bir kitabın bütün yorumlarını okuyabiliyoruz. Bu alıştırmada **tek bir yorumu** okuyan işlemi sen yazacaksın.

**İstenenler:**

1. `GET /books/{book_id}/reviews/{review_id}` işlemini ekle. Hem kitap kimliği hem yorum kimliği eşleşen yorumu döndürsün. Böyle bir yorum yoksa `404` ve `{"detail":"Review not found"}` döndürsün.
2. `create_review` fonksiyonunda, Hafta 2'deki `create_book` gibi, yanıta `Location` başlığını ekle. Başlık yeni yorumun yolunu göstersin.

**İpuçları:**

- Yolda süslü parantez içinde iki ad var: `{book_id}` ve `{review_id}`. Fonksiyonun da bu adlarla iki parametresi olur: `book_id: int` ve `review_id: int`.
- Döngüde iki koşulu birlikte kontrol etmek için Hafta 1'deki `and` kullanımını hatırla.
- `Location` başlığı için fonksiyona `response: Response` parametresini eklemen gerekir.

**Kontrol et:** Sunucuyu yeniden başlat. Önce 8.1'deki curl komutuyla bir yorum ekle, sonra aşağıdaki istekleri gönder. Sonuçlar şöyle olmalı:

| İstek | Durum kodu | Neden? |
|---|---|---|
| 8.1'deki `POST /books/42/reviews` | `201` ve `location: /books/42/reviews/2` | Yeni yorumun yolu |
| `GET /books/42/reviews/1` | `200` | Ece'nin yorumu |
| `GET /books/42/reviews/2` | `200` | Az önce eklediğin yorum |
| `GET /books/42/reviews/9` | `404` | Böyle bir yorum yok. |
| `GET /books/57/reviews/1` | `404` | 1 numaralı yorum var, ama 57 numaralı kitaba değil 42'ye ait. |

---

## 9. Kendini kontrol et: Bu haftanın altı sorusu

1. Kaynak, koleksiyon ve işlem arasındaki fark nedir? `POST /books` isteğinde kaynak ve işlem hangisidir?
2. Koleksiyonun yolu neden `/book` değil `/books` olarak seçilir? Yolları değiştirmenin istemcilere etkisi nedir?
3. `GET /getAllBooks` yolunun REST açısından sorunu nedir?
4. GET isteğiyle kitap eklemek neden sorun çıkarır?
5. Yorumların yolu neden `/reviews` değil de `/books/42/reviews` biçimindedir?
6. REST, SOAP ve GraphQL'de "42 numaralı kitabı getir" isteğinde işlem nasıl belirtilir?

### 9.1 Soruların cevapları

1. Kaynak, sunucuda bir yolu olan şeydir (bir kitap: `/books/42`); koleksiyon aynı türden kaynakların topluluğudur (bütün kitaplar: `/books`); işlem ise bir kaynak üzerinde yapılan iştir ve REST'te HTTP metodu ile yolla belirtilir. `POST /books` isteğinde kaynak kitap koleksiyonu, işlem bu koleksiyona yeni bir kitap eklemektir.
2. Çoğul ad, yolun bir koleksiyonu anlattığını açıkça gösterir: `/books` kitaplar, `/books/42` kitaplardan biri. Yol değişince eski yolu kullanan istemciler `404` alır ve çalışmaz.
3. "Getir" anlamı hem HTTP metodunda hem yolda yazılıyor. REST'te işi HTTP metodu söyler, yol yalnızca kaynağı adlandırır: `GET /books`.
4. GET'in veriyi değiştirmediği varsayılır. Tarayıcılar ve başka programlar GET isteğini kullanıcıya sormadan tekrar gönderebilir; her tekrar yeni bir kitap ekler.
5. Her yorum bir kitaba aittir. Yorumların yolunu kitabın yolunun altına koymak bu ilişkiyi gösterir; sunucu da hangi kitabın yorumlarının istendiğini yoldan öğrenir. Yorumları ayrı bir koleksiyon olarak (`/reviews?book_id=42`) tasarlamak da mümkündür; ne zaman tercih edildiği [ek notta](04_Supplement_Nested_Resources.md).
6. REST'te HTTP metodu ve yolla (`GET /books/42`), SOAP'ta XML mesajındaki işlem adıyla (`GetBook`), GraphQL'de istemcinin yazdığı sorguyla (`book(id: 42)`).

---

## 10. Resmî belgeler

- [MDN — REST](https://developer.mozilla.org/en-US/docs/Glossary/REST)
- [Roy Fielding — REST'in tanımlandığı tez, 5. bölüm](https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
- [HTTP standardı (RFC 9110) — Güvenli HTTP metotları](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.1)
- [FastAPI — Body: Multiple Parameters](https://fastapi.tiangolo.com/tutorial/body-multiple-params/)
- [GraphQL — Learn](https://graphql.org/learn/)
- [W3C — SOAP](https://www.w3.org/TR/soap/)

# Hafta 03 — Uygulama Föyü

## 0. Bu hafta ne yapacağız: API'yi kaynaklara göre tasarlamak

İlk iki haftada kitap kataloğumuza okuma ve ekleme işlemleri yazdık. Bu hafta önce bir adım geri çekilip şunu soracağız: **İşlemlerimizin yolları ve metotları nasıl seçilmeli?** Bu sorunun en yaygın cevabı **REST** yaklaşımıdır.

REST, web API'lerini tasarlamak için yaygın kullanılan bir yaklaşımdır. Temel fikri şudur:

- Sunucudaki veriler, adreslerle ulaşılan **kaynaklar** olarak düşünülür: kitaplar, bir kitap, bir kitabın yorumları…
- Bir kaynak üzerinde yapılacak iş **HTTP metoduyla** belirtilir: okumak için GET, eklemek için POST…

REST bir program ya da kütüphane değildir; bir tasarım yaklaşımıdır. FastAPI ile REST'e uyan da, uymayan da bir API yazabiliriz. Bu hafta ikisini karşılaştıracağız.

Bu haftanın ek notları:

- [SOAP ve GraphQL mesajları nasıl okunur?](03_Supplement_SOAP_GraphQL.md)
- [İç içe kaynak mı, ayrı koleksiyon mu?](04_Supplement_Nested_Resources.md)

### 0.1 Bu haftanın sonunda neler yapabileceksin?

- Bir API'deki kaynakları ve işlemleri ayırt edebileceksin.
- Koleksiyon ve tek kayıt için yol seçebileceksin: `/books` ve `/books/42`.
- Yolda neden fiil değil isim kullanıldığını açıklayabileceksin.
- GET isteğinin neden veriyi değiştirmemesi gerektiğini açıklayabileceksin.
- Bir kaynağın altındaki başka bir kaynak için okuma ve ekleme işlemi yazabileceksin: bir kitabın yorumları.
- API'nin kullanımını `README.md` dosyasında örneklerle belgeleyebileceksin.
- Aynı isteğin REST, SOAP ve GraphQL'de nasıl yazıldığını karşılaştırabileceksin.

### 0.2 Bu föy nasıl okunur?

Her deney aynı sırayla ilerler: **Amaç → Kod → Çalıştır → Çıktı → Ana fikir.**

Kod değiştiğinde ya dosyanın tamamı ya da yalnızca değişen kısım verilir. Hangisi olduğu kodun hemen üstünde yazar.

> **Kayıt sayılarını izlemek için:** Sunucu her başlatıldığında dosyada yazılı üç kitapla başlar. Deney 5'ten sonra bir de dosyada yazılı tek bir yorumla başlar. İstekle eklenen kayıtlar yalnızca sunucu çalıştığı sürece bellekte durur. Deneylerdeki "sunucuyu yeniden başlat" adımlarını izlersen çıktıların föydekilerle aynı olur.

### 0.3 Başlangıç dosyaları

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
| **Kaynak** | Sunucunun bir adresle sunduğu şey | Bir kitap |
| **Koleksiyon** | Aynı türden kaynakların topluluğu | Bütün kitaplar |
| **İşlem** | Bir kaynak üzerinde yapılan iş: **metot + yol** | `GET /book/42`: 42 numaralı kitabı oku |

Hafta 2'nin sonundaki sunucumuzda üç işlem var:

| Metot | Yol | Fonksiyon | Hangi kaynak? | Ne yapar? |
|---|---|---|---|---|
| `GET` | `/book` | `get_books` | Kitap koleksiyonu | Kitapları listeler; arama ve filtre uygulayabilir. |
| `POST` | `/book` | `create_book` | Kitap koleksiyonu | Koleksiyona yeni bir kitap ekler. |
| `GET` | `/book/{book_id}` | `get_book` | Tek bir kitap | Kimliği verilen kitabı döndürür. |

Dikkat et: İki işlem aynı yolu (`/book`) kullanıyor. Yol **hangi kaynağın** istendiğini, metot **onunla ne yapılacağını** söylüyor.

### 1.2 Koleksiyonu ve tek kaydı iste

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

| İstek | Yanıtın JSON türü | Neden? |
|---|---|---|
| `GET /book` | Dizi `[...]` | Koleksiyon birden çok kitap içerir. |
| `GET /book/42` | Nesne `{...}` | Tek bir kitap istendi. |

> **Ana fikir:** API'yi tasarlarken önce kaynakları belirleriz: kitaplar ve bir kitap. Sonra her kaynakta yapılacak işleri metotlarla ifade ederiz. Bir işlem, metot ile yolun birleşimidir.

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

İstemciyi çalıştır:

```text
Status code: 201
Location: /books/74
Read status: 200
Book id: 74
Book title: HTTP ile Yeni Bir Kitap
Book count: 4
```

`Location` başlığı da artık `/books/74` geliyor, çünkü sunucuda o satırı da değiştirdik.

> **Ana fikir:** Yol, kaynağın adıdır. Koleksiyon için çoğul bir ad (`/books`), koleksiyondaki tek kayıt için onun altında bir kimlik (`/books/42`) kullanırız. Yollar değişince eski istemciler bozulur; bu yüzden yollar baştan dikkatle seçilir.

---

## Deney 3 — Yolda neden fiil değil isim kullanılır?

**Amaç:** Aynı işleri yapan ama yollarında fiil kullanan bir API ile REST'e uygun API'mizi karşılaştırmak.

### 3.1 İşlem adlarını yola yazan bir sunucu

Aşağıdaki sunucu çalışır, ama REST'e uymaz. Bunu denemek için proje klasöründe `bad_server.py` adlı ayrı bir dosya oluştur:

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

Bütün işlemler çalışıyor. Adresteki `%20`, boşluk karakterinin adreste yazılış biçimidir.

### 3.2 İki tasarımı karşılaştır

| İşlem | `bad_server.py` | REST'e uygun API'miz |
|---|---|---|
| Bütün kitaplar | `GET /getAllBooks` | `GET /books` |
| Tek kitap | `GET /getBookById?id=42` | `GET /books/42` |
| Yeni kitap | `POST /createNewBook?title=Yeni%20Kitap` | `POST /books`, kitap bilgileri gövdede |

`bad_server.py` tasarımındaki sorunlar:

| Sorun | Açıklama |
|---|---|
| Fiil iki kez yazılıyor | `GET /getAllBooks` isteğinde "getir" anlamı hem metotta (`GET`) hem yolda (`get`) var. REST'te işi metot söyler, yol yalnızca kaynağı adlandırır. |
| Her işlem için yeni bir ad gerekiyor | `getAllBooks`, `getBookById`, `createNewBook`… İstemci bütün adları tek tek öğrenmek zorundadır ve adları tahmin edemez: `getBook` mu, `getBookById` mi, `fetchBook` mu? |
| Kitap bilgileri adreste gidiyor | Yeni kitabın adı sorgu bölümünde (`?title=...`) gönderiliyor. Bir kitabın bütün alanlarını (yazar, etiketler…) adreste göndermek zordur; bu bilgiler gövdeye aittir. |

Denemeden sonra `bad_server.py` sunucusunu durdur ve kendi sunucunu yeniden başlat.

> **Ana fikir:** Bir API'nin çalışması, iyi tasarlandığı anlamına gelmez. REST'te **yol kaynağı (ismi), metot yapılacak işi (fiili)** söyler. Böylece istemci, yolları tek tek ezberlemek yerine aynı kalıbı her kaynakta kullanabilir.

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

HTTP standardı da GET'i **güvenli (safe)** bir metot olarak tanımlar: GET isteği sunucudaki veriyi değiştirmemelidir.

| Metot | Veriyi değiştirir mi? | Tekrar gönderilirse? | Derste |
|---|---|---|---|
| `GET` | Hayır | Bir şey değişmez; aynı veri yeniden okunur. | Hafta 1 |
| `POST` | Evet: yeni kayıt oluşturur | Bizim API'mizde her seferinde yeni bir kayıt oluşur. | Hafta 2 |
| `PUT`, `PATCH`, `DELETE` | Evet: günceller ya da siler | Hafta 4'te göreceğiz. | Hafta 4 |

Denemeden sonra `bad_get_server.py` sunucusunu durdur ve kendi sunucunu yeniden başlat.

> **Ana fikir:** GET yalnızca okumak içindir ve sunucudaki veriyi değiştirmemelidir. Programlar GET isteğini kendiliğinden tekrar gönderebildiği için, veri değiştiren işlemler POST gibi başka metotlarla yapılır.

---

## Deney 5 — Bir kitabın yorumlarını okuma ve ekleme

**Amaç:** Hafta 1 ve 2'de öğrendiğimiz okuma ve ekleme işlemlerini **yeni bir kaynak** için yazmak: kitapların yorumları.

### 5.1 Yorumlar için yollar

Her yorum bir kitaba aittir. Bu ilişkiyi yolda da gösteririz: Bir kitabın yorumları, o kitabın yolunun altında durur.

| Metot | Yol | Ne yapar? |
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
| `created_review["book_id"] = book_id` | Yorumun hangi kitaba ait olduğunu yoldan alıp kayda yazar. İstemci bunu gövdede göndermez. |

`get_book` fonksiyonunda kitabı bulunca hemen `return` ediyorduk, çünkü iş orada bitiyordu. Burada kitabı bulmak işin yalnızca ilk adımı; asıl iş yorumlarla ilgili. Bu yüzden "kitap var mı?" sorusunun cevabını bayrakta saklıyor, döngüden sonra kullanıyoruz.

Bu kontrol iki fonksiyonda da aynen tekrar ediyor. Şimdilik her fonksiyonun tek başına okunabilmesi için böyle bırakıyoruz.

### 5.3 Bir fonksiyon, üç ayrı yerden bilgi alabilir

`create_review` fonksiyonu bilgiyi iki farklı yerden alıyor. Hafta 1'deki sorgu parametresiyle birlikte, bir fonksiyonun bilgi alabileceği üç yeri de görmüş olduk:

| Parametre | Bilgi nereden gelir? | FastAPI bunu nereden anlar? | İlk gördüğümüz yer |
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


@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")


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
    response = httpx.get(base_url + "/books/42/reviews")
    print("Reviews before:", response.status_code, len(response.json()))

    response = httpx.post(base_url + "/books/42/reviews", json=new_review)
    print("Create status:", response.status_code)
    print("Created review:", response.text)

    response = httpx.get(base_url + "/books/42/reviews")
    print("Reviews after:", response.status_code, len(response.json()))

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

İstemciyi yazan kişi sunucunun kodunu görmeyebilir. Hangi yolların olduğunu, hangi metotla ne gönderileceğini ve ne cevap geleceğini ancak bir belgeden öğrenebilir. Bu belgeye **API belgesi (dokümantasyon)** denir.

Bu hafta belgeyi elle, proje klasöründe bir `README.md` dosyası olarak yazacağız. `README.md`, bir proje klasörünün tanıtım dosyasıdır; GitHub'da bir klasör açılınca ilk bu dosya görünür. Her örneği önce kendimiz curl ile çalıştıracak, sonra gerçek yanıtı belgeye koyacağız.

### 6.2 Belgenin başlangıcı

Proje klasöründe `README.md` dosyasını oluştur ve şu içerikle başla. Sunucuyu yeniden başlat, örneklerdeki istekleri curl ile gönder ve gelen yanıtları belgedekilerle karşılaştır.

Aşağıdaki örneğin başındaki ve sonundaki dört ters tırnaklı satırlar (` ```` `) yalnızca bu föyde içeriği göstermek içindir; onları `README.md` dosyasına kopyalama.

````markdown
# Kitap Kataloğu API'si

Sunucu adresi: `http://127.0.0.1:8000`

## İşlemler

| Metot | Yol | Ne yapar? |
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

> **Ana fikir:** API belgesi, API'yi kullanacak kişiye her işlemin yolunu, metodunu, ne göndereceğini ve ne cevap alacağını söyler. Belgedeki örnekler, gerçekten gönderilmiş isteklerden ve gelen yanıtlardan alınmalıdır.

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

SOAP'ta bütün istekler genellikle aynı adrese, POST ile gönderilir. Hangi işlemin istendiği XML biçimindeki mesajın içinde yazar:

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

GraphQL'de de istekler genellikle tek bir adrese, POST ile gönderilir. İstemci, istediği alanları bir **sorgu** ile kendisi seçer:

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
| İşlem nasıl belirtilir? | Metot ve yol: `GET /books/42` | Mesajın içindeki işlem adı: `GetBook` | Sorgu metni: `book(id: 42)` |
| Adres | Her kaynak için ayrı yol | Genellikle tek adres: `/BookService` | Genellikle tek adres: `/graphql` |
| Metot | İşe göre: GET, POST… | Genellikle POST | Genellikle POST |
| Veri biçimi | Genellikle JSON | XML | JSON |
| Yanıtta hangi alanlar gelir? | Sunucunun belirlediği alanlar | Sunucunun belirlediği alanlar | İstemcinin sorguda istediği alanlar |
| Nerede karşılaşılır? | Bugünkü web API'lerinin çoğu | Bankacılık gibi alanlardaki daha eski kurumsal sistemler | Farklı verileri tek istekte almak isteyen web ve mobil uygulamalar |

REST yanıtında kitabın bütün alanları geldi; `tags` ve `rating` alanlarını istemesek de. GraphQL'de ise istemci yalnızca istediği alanları aldı. Buna karşılık GraphQL'de sunucuyu kurmak ve sorguları işlemek daha fazla iş gerektirir.

> **Ana fikir:** REST, SOAP ve GraphQL aynı işi farklı yollarla yapar. REST'te işi metot ve yol, SOAP'ta XML mesajındaki işlem adı, GraphQL'de istemcinin yazdığı sorgu belirtir. Bu derste REST yaklaşımıyla devam ediyoruz.

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

- Yolda iki parametre var. Fonksiyonun da iki parametresi olur: `book_id: int` ve `review_id: int`.
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

1. Kaynak, sunucunun adresle sunduğu şeydir (bir kitap); koleksiyon aynı türden kaynakların topluluğudur (bütün kitaplar); işlem ise metot ile yolun birleşimidir. `POST /books` isteğinde kaynak kitap koleksiyonu, işlem bu koleksiyona yeni bir kitap eklemektir.
2. Çoğul ad, yolun bir koleksiyonu anlattığını açıkça gösterir: `/books` kitaplar, `/books/42` kitaplardan biri. Yol değişince eski yolu kullanan istemciler `404` alır ve çalışmaz.
3. "Getir" anlamı hem metotta hem yolda yazılıyor. REST'te işi metot söyler, yol yalnızca kaynağı adlandırır: `GET /books`.
4. GET'in veriyi değiştirmediği varsayılır. Tarayıcılar ve başka programlar GET isteğini kullanıcıya sormadan tekrar gönderebilir; her tekrar yeni bir kitap ekler.
5. Her yorum bir kitaba aittir. Yorumların yolunu kitabın yolunun altına koymak bu ilişkiyi gösterir; sunucu da hangi kitabın yorumlarının istendiğini yoldan öğrenir. Yorumları ayrı bir koleksiyon olarak (`/reviews?book_id=42`) tasarlamak da mümkündür; ne zaman tercih edildiği [ek notta](04_Supplement_Nested_Resources.md).
6. REST'te metot ve yolla (`GET /books/42`), SOAP'ta XML mesajındaki işlem adıyla (`GetBook`), GraphQL'de istemcinin yazdığı sorguyla (`book(id: 42)`).

---

## 10. Kaynaklar: Konuların resmî belgeleri

- [MDN — REST](https://developer.mozilla.org/en-US/docs/Glossary/REST)
- [Roy Fielding — REST'in tanımlandığı tez, 5. bölüm](https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
- [HTTP standardı (RFC 9110) — Güvenli metotlar](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.1)
- [FastAPI — Body: Multiple Parameters](https://fastapi.tiangolo.com/tutorial/body-multiple-params/)
- [GraphQL — Learn](https://graphql.org/learn/)
- [W3C — SOAP](https://www.w3.org/TR/soap/)

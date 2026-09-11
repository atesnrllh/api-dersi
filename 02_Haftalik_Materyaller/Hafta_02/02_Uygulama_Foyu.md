# Hafta 02 — Uygulama Föyü

## Kitap Kataloğunda HTTP’yi Görmek: Postman, GET, POST ve Yanıt Ayrıntıları

**Ders:** Uygulama Programı Arayüzü (API)

**Ön koşul:** Birinci haftanın son çalışan `server.py` ve `client.py` dosyaları

**Ana araçlar:** VS Code, Python, FastAPI, Uvicorn, HTTPX ve Postman

**Sürüm:** 1.0 — 11 Eylül 2026

> Bu föy [birinci hafta uygulamasının](../Hafta_01/02_Uygulama_Foyu.md) devamıdır. Yeni bir örnek kurmak yerine aynı kitap kataloğunu geliştiriyoruz. Her deneyde önce **neyi yaptığımızı**, **neden yaptığımızı** ve [ikinci hafta teorisindeki](01_Teorik_Ders_Notu.md) yerini okuyup sonra adımları uygula.

> **Kod gösterimi:** `diff` kutusunda `-` ile başlayan satırlar kaldırılan, `+` ile başlayan satırlar eklenen bölümlerdir. GitHub bunları genellikle kırmızı ve yeşil gösterir. Her kod değişikliğinden sonra ilgili `.py` dosyasının yeni hâli eksiksiz verilir.

## 1. Bu haftanın öğrenme yolu

Birinci hafta istemci–sunucu iletişimini kurduk. İkinci hafta aynı iletişimin HTTP ayrıntılarını görünür yapacağız:

```text
Birinci hafta
client.py ── GET isteği ──► server.py ── JSON yanıtı ──► client.py

İkinci hafta
Postman ─┬─ metot
         ├─ yol ve sorgu
         ├─ başlıklar
         └─ JSON gövdesi ──► server.py
```

Deney sırası:

1. Birinci haftanın son kodunu çalıştırmak.
2. Mevcut GET isteğini Postman’da yeniden kurmak.
3. Yol, sorgu ve başlıkları ayrı ayrı değiştirmek.
4. Tanımlanmamış POST isteğiyle `405` görmek.
5. Sunucuya `POST /api/books` işlemini eklemek.
6. `201`, `Location` ve yanıt gövdesini incelemek.
7. Aynı POST’u tekrarlayıp idempotentlik farkını görmek.
8. Hatalı gövdelerde `422` yanıtını okumak.
9. Aynı POST isteğini Python istemcisiyle göndermek.
10. Yeni kitabı mevcut `client.py` ile aramak.
11. Uygulanmamış metotları deneyip dördüncü haftanın sınırını görmek.

## 2. Başlangıç durumunu doğrula

### Ne yapıyoruz?

Birinci haftanın son sunucu ve istemci dosyalarını aynı proje klasöründe çalıştırıyoruz.

### Neden yapıyoruz?

Yeni deneylerin eski çalışan durumdan başladığını doğruluyoruz. Başlangıç hatalıysa ikinci haftadaki HTTP sonuçlarını doğru yorumlayamayız.

### Teorideki yeri

- Hafta 01, istemci–sunucu rolleri
- Hafta 02, Bölüm 1: Birinci haftadan ikinci haftaya geçiş

### 2.1. Proje klasörünü ve dosyaları kontrol et

VS Code terminalinde:

```bash
pwd
ls
```

En azından şu öğeleri görmelisin:

```text
api-env  client.py  server.py
```

`api-env` görünmüyorsa birinci haftadaki ortam kurulumu tamamlanmamış olabilir. Ortam varsa iki terminalde de etkinleştir:

```bash
source api-env/bin/activate
```

### 2.2. Postman’ı hazırla

Bu hafta yerel sunucuya elle istek göndermek için Postman masaüstü uygulamasını kullanacağız. Bilgisayarında yoksa [Postman’ın resmî indirme sayfasından](https://www.postman.com/downloads/) işletim sistemine uygun masaüstü sürümünü kur.

Tarayıcıdaki Postman sürümünü kullanırsan `127.0.0.1` üzerindeki yerel sunucuya erişim için Desktop Agent gerekebilir. Bu föyde doğrudan masaüstü uygulamasını kullanmak daha açıktır.

Postman’ı açtıktan sonra boş bir HTTP isteği oluşturabileceğin çalışma alanına geç. Arayüz sürüme göre değişse de kullanacağımız bölümler şunlardır:

- Metot seçimi
- URL alanı
- Params
- Headers
- Body
- Send düğmesi
- Yanıtın status, headers ve body bölümleri

### 2.3. Başlangıç `server.py` dosyasının tamamı

Dosyan farklıysa aşağıdaki birinci hafta son sürümünü kullan:

```python
from fastapi import FastAPI, HTTPException

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


@app.get("/api/books")
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


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

### 2.4. Başlangıç `client.py` dosyasının tamamı

```python
import httpx

try:
    response = httpx.get(
        "http://127.0.0.1:8000/api/books",
        params={
            "search": "Python",
            "available": "true"
        },
        headers={"Accept": "application/json"}
    )
except httpx.ConnectError:
    print("Connection failed: Could not connect to the server.")
    print("Check that the server is running at http://127.0.0.1:8000.")
else:
    print("Request URL:", response.request.url)
    print("Request Accept:", response.request.headers.get("Accept"))
    print("Status code:", response.status_code)
    print("Response Content-Type:", response.headers.get("Content-Type"))
    print("Response body:", response.text)

    if response.status_code == 200:
        books = response.json()

        print("Book count:", len(books))
        print()

        if not books:
            print("No books matched your search.")

        for book in books:
            print("Book title:", book["title"])
            print(
                "Book author:",
                book["author"]["first_name"],
                book["author"]["last_name"]
            )

            if book["available"]:
                print("Availability: Available to borrow")
            else:
                print("Availability: Not available to borrow")

            if book["tags"]:
                print("Tags:")
                for tag in book["tags"]:
                    print("-", tag)
            else:
                print("Tags: No tags")

            if book["rating"] is None:
                print("Rating: Not rated yet")
            else:
                print("Rating:", book["rating"])

            print()
    else:
        print("Book information could not be retrieved.")
```

### 2.5. İki terminalde çalıştır

Sunucu terminali:

```bash
python -m uvicorn server:app
```

İstemci terminali:

```bash
python client.py
```

Temel sonuç `200`, bir kitap ve **Python ile Web API** olmalıdır. Sunucu çalışırken sunucu terminalini açık bırak.

### Sonuç

Başlangıçta yalnızca GET işlemleri vardır. Birazdan aynı `/api/books` yoluna POST gönderdiğimizde alacağımız sonuç, sonraki sunucu değişikliğini anlamamız için karşılaştırma noktası olacak.

## 3. Deney 1 — GET isteğini Postman’da kur

### Ne yapıyoruz?

`client.py` dosyasının yaptığı isteği Postman arayüzünde elle oluşturuyoruz.

### Neden yapıyoruz?

Python kütüphanesinin bizim yerimize hazırladığı HTTP parçalarını ayrı alanlarda görmek istiyoruz.

### Teorideki yeri

- Bölüm 3: HTTP isteğinin parçaları
- Bölüm 13: Postman’ın istemci rolü

### Adım adım

1. Postman masaüstü uygulamasını aç.
2. Yeni bir HTTP request sekmesi oluştur.
3. Metot listesinden **GET** seç.
4. Adres alanına şunu yaz:

```text
http://127.0.0.1:8000/api/books
```

5. **Params** sekmesine şu iki satırı ekle:

| KEY | VALUE |
|---|---|
| `search` | `Python` |
| `available` | `true` |

6. **Headers** sekmesine şu satırı ekle:

| KEY | VALUE |
|---|---|
| `Accept` | `application/json` |

7. **Send** düğmesine bas.

Beklenen URL:

```text
http://127.0.0.1:8000/api/books?search=Python&available=true
```

Beklenen durum kodu `200`, yanıt gövdesi bir elemanlı JSON dizisidir.

### Gözlem tablosu

| İncelenecek bölüm | Bulman gereken bilgi |
|---|---|
| İstek metodu | `GET` |
| İstek yolu | `/api/books` |
| Sorgu parametreleri | `search`, `available` |
| İstek `Accept` başlığı | `application/json` |
| Yanıt durum kodu | `200` |
| Yanıt `Content-Type` başlığı | `application/json` ile başlayan değer |
| Yanıt gövdesinin dış türü | Dizi |

Postman ek veya gizli başlıklar gösterebilir. Bunlar aracın otomatik hazırladığı HTTP ayrıntılarıdır; hata değildir.

### Deneyin sonucu

Postman ve `client.py` farklı arayüzlere sahiptir, fakat ikisi de aynı sunucu işlemine aynı tür HTTP isteği gönderen istemcilerdir.

## 4. Deney 2 — Yol, sorgu ve başlığın görevlerini ayır

### Ne yapıyoruz?

Postman’daki mevcut isteğin yalnızca bir parçasını her seferinde değiştiriyoruz.

### Neden yapıyoruz?

Sonucun hangi istek parçası nedeniyle değiştiğini tek tek gözlemlemek istiyoruz.

### Teorideki yeri

- Bölüm 4: Girdi nerede taşınır?
- Bölüm 10: HTTP başlıkları

### 4.1. Sorgu değerini değiştir

`search` değerini `API`, `available` değerini `true` yap ve gönder.

Beklenen kitap: **API Yolculuğu**.

Burada yol değişmedi. Aynı koleksiyon işlemi farklı koşulla çalıştı.

### 4.2. Sorgu parametrelerini kaldır

Params tablosundaki iki satırın işaretini kaldır veya satırları sil. İstek şu hâle gelmeli:

```http
GET /api/books
```

Beklenen sonuç üç kitaptır. Parametre gönderilmediğinde sunucudaki varsayılan değerler bütün kitapların eşleşmesini sağlar.

### 4.3. Tek kitap yoluna geç

Adresi değiştir:

```text
http://127.0.0.1:8000/api/books/57
```

Beklenen dış JSON yapısı artık dizi değil, tek kitap nesnesidir. `57` sorgu parametresi değildir; yolun bir parçasıdır.

### 4.4. `Accept` değerini değiştir

Headers bölümündeki `Accept` değerini geçici olarak `text/plain` yap ve GET isteğini yeniden gönder.

FastAPI örneğimiz yine JSON dönebilir. Bunun anlamı şudur:

- `Accept`, istemcinin kabul ettiği biçimi bildirir.
- Mevcut sunucu kodumuz içerik uzlaşması yapıp metin yanıt üreten ikinci bir temsil tanımlamadı.
- Bir başlık yazmak, sunucuda bulunmayan davranışı kendiliğinden oluşturmaz.

Deney bittikten sonra `Accept` değerini tekrar `application/json` yap.

### Deneyin sonucu

Yol hedef kaynağı, sorgu parametreleri sonuç koşullarını, `Accept` ise istemcinin yanıt tercihini taşır. Aynı bilgi alanları değildir.

## 5. Deney 3 — Tanımlanmamış POST ile `405` gör

### Ne yapıyoruz?

Sunucunun henüz yalnızca GET kabul ettiği `/api/books` yoluna POST gönderiyoruz.

### Neden yapıyoruz?

Sunucunun işlemi yalnızca yola göre değil, **metot + yol** çiftine göre seçtiğini kanıtlamak istiyoruz.

### Teorideki yeri

- Bölüm 5: Metot ile yol birlikte işlemi seçer
- Bölüm 9: `405 Method Not Allowed`

### Adım adım

1. Postman’da adresi şu yap:

```text
http://127.0.0.1:8000/api/books
```

2. Metodu **GET** yerine **POST** seç.
3. Şimdilik gövde ekleme.
4. **Send** düğmesine bas.

Beklenen temel sonuç:

```text
Status: 405 Method Not Allowed
```

```json
{"detail": "Method Not Allowed"}
```

Yanıt başlıklarında `Allow: GET` benzeri bir değer görebilirsin. FastAPI/Starlette sürümüne göre başlıkların görünümü değişebilir.

### Neden `404` değil?

`/api/books` yolu vardır. Fakat mevcut sunucuda bu yol için POST işlemi tanımlı değildir. Bu nedenle sorun “yol yok” değil, “bu metot burada kullanılamıyor” durumudur.

### Deneyin sonucu

POST seçmek, mevcut GET fonksiyonunu POST işlemi hâline getirmez. Sunucu sözleşmesinde POST için ayrı davranış yazmamız gerekir.

## 6. Deney 4 — Kitap oluşturmak için POST işlemi ekle

### Ne yapıyoruz?

Sunucuya JSON gövdesi alan, yeni kimlik üreten ve kitabı bellekteki listeye ekleyen `POST /api/books` işlemi ekliyoruz.

### Neden yapıyoruz?

İstek gövdesi, `201 Created`, `Location` başlığı ve sunucu durumunun değişmesi kavramlarını tek anlamlı işlemde görmek istiyoruz.

### Teorideki yeri

- Bölüm 3: İstek gövdesi
- Bölüm 6: POST metodu
- Bölüm 8–10: `201`, `Location` ve `Content-Type`

### Yeni kavramlar

- `BaseModel`: İstek gövdesinde beklenen alanları ve türleri tanımlar.
- `BookCreate`: Yeni kitap oluştururken istemciden beklediğimiz yapı.
- `AuthorCreate`: `author` iç nesnesinin yapısı.
- `status.HTTP_201_CREATED`: Başarılı oluşturma yanıtının durum kodu.
- `Response`: Yanıta `Location` başlığı eklememizi sağlar.

Bu hafta modelin yalnızca HTTP gövdesinin beklenen yapısını tanımladığını kullanıyoruz. Ayrıntılı alan ve iş kuralı doğrulamasını beşinci haftada işleyeceğiz.

### `server.py` dosyasında değişen satırlar

```diff
- from fastapi import FastAPI, HTTPException
+ from fastapi import FastAPI, HTTPException, Response, status
+ from pydantic import BaseModel
 
  app = FastAPI()
+
+
+ class AuthorCreate(BaseModel):
+     first_name: str
+     last_name: str
+
+
+ class BookCreate(BaseModel):
+     title: str
+     author: AuthorCreate
+     available: bool
+     tags: list[str]
+     rating: float | None
...
+
+ @app.post("/api/books", status_code=status.HTTP_201_CREATED)
+ def create_book(book: BookCreate, response: Response):
+     new_book = {
+         "id": max(existing_book["id"] for existing_book in books) + 1,
+         **book.model_dump()
+     }
+
+     books.append(new_book)
+     response.headers["Location"] = f"/api/books/{new_book['id']}"
+
+     return new_book
```

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

app = FastAPI()


class AuthorCreate(BaseModel):
    first_name: str
    last_name: str


class BookCreate(BaseModel):
    title: str
    author: AuthorCreate
    available: bool
    tags: list[str]
    rating: float | None


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


@app.get("/api/books")
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


@app.post("/api/books", status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, response: Response):
    new_book = {
        "id": max(existing_book["id"] for existing_book in books) + 1,
        **book.model_dump()
    }

    books.append(new_book)
    response.headers["Location"] = f"/api/books/{new_book['id']}"

    return new_book


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

Dosyayı **Ctrl+S** ile kaydet. Sunucu terminalinde Ctrl+C ile eski süreci kapat ve yeniden başlat:

```bash
python -m uvicorn server:app
```

### Kodun yaptığı iş

```python
new_book = {
    "id": max(existing_book["id"] for existing_book in books) + 1,
    **book.model_dump()
}
```

- `max(...) + 1`, mevcut en büyük kimlikten sonraki sayıyı üretir.
- `book.model_dump()`, doğrulanmış istek modelini Python sözlüğüne dönüştürür.
- `**`, bu sözlüğün alanlarını `new_book` sözlüğüne ekler.
- İstemci gövdede `id` göndermez; kimlik üretme sorumluluğu sunucudadır.

### Deneyin sonucu

Aynı `/api/books` yolu artık GET ve POST için iki farklı işlem sunar. Metot, istemcinin liste okumak mı yoksa yeni kitap oluşturmak mı istediğini ayırır.

## 7. Deney 5 — Postman’dan geçerli kitap oluştur

### Ne yapıyoruz?

Postman’dan yeni kitap JSON’u gönderip oluşturma yanıtını inceliyoruz.

### Neden yapıyoruz?

İstek gövdesiyle yanıt gövdesinin aynı şey olmadığını ve sunucunun yanıta yeni kimlik eklediğini görmek istiyoruz.

### Teorideki yeri

- Bölüm 8: HTTP yanıtının parçaları
- Bölüm 14: Kitap ekleme işleminin yolculuğu

### Adım adım

1. Postman’da metodu **POST** seç.
2. Adresi yaz:

```text
http://127.0.0.1:8000/api/books
```

3. **Body → raw → JSON** seç.
4. Aşağıdaki gövdeyi yaz:

```json
{
  "title": "HTTP'yi Anlamak",
  "author": {
    "first_name": "Selin",
    "last_name": "Aras"
  },
  "available": true,
  "tags": ["http", "web"],
  "rating": null
}
```

5. Headers bölümünde `Content-Type: application/json` bulunduğunu kontrol et. Postman, **raw → JSON** seçimi nedeniyle bunu otomatik ekleyebilir.
6. `Accept: application/json` başlığını ekle.
7. **Send** düğmesine bas.

### Beklenen yanıt

```text
Status: 201 Created
Location: /api/books/74
Content-Type: application/json
```

```json
{
  "id": 74,
  "title": "HTTP'yi Anlamak",
  "author": {
    "first_name": "Selin",
    "last_name": "Aras"
  },
  "available": true,
  "tags": ["http", "web"],
  "rating": null
}
```

Sunucuyu daha önce yeniden başlatmadan başka kitaplar eklediysen kimlik `74` yerine daha büyük olabilir. Önemli olan kimliğin istemci gövdesinde bulunmaması ve sunucu tarafından yanıta eklenmesidir.

### İstek ve yanıtı karşılaştır

| Alan | İstek gövdesinde | Yanıt gövdesinde | Nedeni |
|---|:---:|:---:|---|
| `title` | Var | Var | İstemci yeni kitabın başlığını gönderdi. |
| `author` | Var | Var | İstemci yazar bilgisini gönderdi. |
| `id` | Yok | Var | Kimliği sunucu üretti. |

### Deneyin sonucu

`201`, yalnızca JSON döndüğünü değil, yeni bir kaynak oluşturulduğunu bildirir. `Location`, bu kaynağın daha sonra hangi yoldan istenebileceğini gösterir.

Postman başlık adını `Location` veya `location` biçiminde gösterebilir. HTTP başlık adları büyük/küçük harfe duyarlı değildir; ikisi aynı başlıktır.

## 8. Deney 6 — Oluşturulan kaynağı GET ile doğrula

### Ne yapıyoruz?

POST yanıtındaki `Location` yolunu GET isteğinde kullanıyoruz.

### Neden yapıyoruz?

POST ile oluşturulan kaynağın koleksiyona gerçekten eklendiğini ve başka bir HTTP işlemiyle okunabildiğini görmek istiyoruz.

### Teorideki yeri

- Bölüm 2: Her isteğin ayrı değerlendirilmesi
- Bölüm 10.3: `Location` başlığı

### Adım adım

1. Postman’da yeni istek sekmesi aç veya mevcut isteği çoğalt.
2. Metodu **GET** yap.
3. POST yanıtındaki Location değerini adresle birleştir:

```text
http://127.0.0.1:8000/api/books/74
```

4. Body bölümünü **none** yap. GET için kitap gövdesi gönderme.
5. İsteği gönder.

Beklenen sonuç `200` ve az önce oluşturulan tek kitap nesnesidir.

Ardından `GET /api/books` isteğini gönder. Kitap sayısı sunucu yeniden başlatılmadıysa dörde çıkmıştır.

### Deneyin sonucu

POST ve sonraki GET iki ayrı HTTP alışverişidir. GET’in başarılı olması, önceki POST ile değişen bellek durumunu okuduğunu gösterir.

## 9. Deney 7 — Aynı POST’u tekrar gönder

### Ne yapıyoruz?

Aynı kitap gövdesini değiştirmeden ikinci kez POST ediyoruz.

### Neden yapıyoruz?

POST metodunun genel olarak idempotent olmadığını çalışan örnekte görmek istiyoruz.

### Teorideki yeri

- Bölüm 7: Güvenli ve idempotent metotlar

### Adım adım

1. Bir önceki geçerli POST isteğine dön.
2. Gövdede hiçbir alanı değiştirme.
3. **Send** düğmesine yeniden bas.

İlk yanıtta `id: 74` aldıysan ikinci yanıtta `id: 75` beklenir. Ardından `GET /api/books` gönderdiğinde başlıkları aynı, kimlikleri farklı iki kitap görürsün.

```text
POST 1 → 201 → /api/books/74
POST 2 → 201 → /api/books/75
```

### Burada hata mı var?

Bu öğretim sözleşmesinde aynı başlığa sahip kitap yasaklanmadı. Sunucu her POST’u yeni oluşturma isteği kabul eder. Başlığın benzersiz olmasını veya tekrar gönderilen isteğin tek işlem sayılmasını isteseydik ayrıca kural tasarlamamız gerekirdi.

### Deneyin sonucu

POST’u tekrarlamak, ilk isteğin yanıtını tekrar okumak değildir. Her gönderim sunucuda yeniden çalışır ve yeni yan etki oluşturabilir.

## 10. Deney 8 — Hatalı JSON gövdelerinde `422` yanıtını oku

### Ne yapıyoruz?

İstek gövdesini farklı biçimlerde bozup FastAPI’nin hangi aşamada isteği reddettiğini gözlemliyoruz.

### Neden yapıyoruz?

`422` yanıtındaki ayrıntıların, hatanın hangi alanda olduğunu gösterebildiğini öğreniyoruz. Yalnızca durum koduna bakıp gövdeyi atlamıyoruz.

### Teorideki yeri

- Bölüm 9.1–9.2: `400`, `415` ve `422`
- Bölüm 12: FastAPI’nin istek işleme adımları

Her alt deneyden sonra gövdeyi tekrar geçerli sürüme döndür.

### 10.1. Zorunlu iç alan eksik

`author` nesnesinden `last_name` alanını kaldır:

```json
{
  "title": "HTTP'yi Anlamak",
  "author": {
    "first_name": "Selin"
  },
  "available": true,
  "tags": ["http", "web"],
  "rating": null
}
```

Beklenen durum `422`dir. Hata gövdesindeki konum yaklaşık olarak şunu gösterir:

```json
["body", "author", "last_name"]
```

Bu yol, sorunun istek gövdesindeki `author.last_name` alanıyla ilgili olduğunu anlatır.

### 10.2. Mantıksal değer yerine anlaşılamayan metin

```json
"available": "belki"
```

JSON yazımı geçerlidir; fakat `belki` değeri `bool` türüne dönüştürülemez. Beklenen durum yine `422`dir. `"false"` gibi bazı metinleri FastAPI/Pydantic dönüştürebilir; bu hafta dönüşüm listesini ezberlemek yerine API’ye doğru JSON türünü göndereceğiz:

```json
"available": false
```

### 10.3. Geçersiz JSON yazımı

Son alandan sonra virgül bırak:

```json
{
  "title": "HTTP'yi Anlamak",
}
```

Standart JSON geçersizdir. FastAPI fonksiyon çalışmadan önce gövdeyi ayrıştıramaz ve `422` döndürür.

### Önemli gözlem

Bu üç istekte `create_book()` işleminin içi çalışmadığı için `books.append(...)` çağrılmaz. Hatalı denemeler listeye kitap eklememelidir.

### Deneyin sonucu

`422`, “sunucu kapalı” anlamına gelmez. Sunucu isteği almış, gövdeyi beklenen modele dönüştüremediği için düzenli bir HTTP hata yanıtı üretmiştir.

## 11. Deney 9 — `Content-Type` ile `Accept` farkını Postman’da göster

### Ne yapıyoruz?

Başarılı POST isteğinin iki başlığını mesaj yönlerine göre inceliyoruz.

### Neden yapıyoruz?

İki başlıkta da `application/json` yazmasının görevlerini aynı yapmadığını görmek istiyoruz.

### Teorideki yeri

- Bölüm 10: HTTP başlıkları
- Bölüm 11: Gövde ile JSON ayrımı

Başarılı POST isteğinde:

| Başlık | Mesaj yönü | Söylediği şey |
|---|---|---|
| İstek `Content-Type` | Postman → sunucu | “Gönderdiğim gövde JSON’dur.” |
| İstek `Accept` | Postman → sunucu | “JSON yanıt kabul ediyorum.” |
| Yanıt `Content-Type` | Sunucu → Postman | “Döndürdüğüm gövde JSON’dur.” |

Postman’da **Body → raw → JSON** seçimi istek `Content-Type` başlığını otomatik ekleyebilir. Headers sekmesinde **hidden** veya otomatik başlık göstergesi varsa ayrıntısını aç.

`Content-Type` işlemin başarılı olduğunu söylemez. 422 hata gövdesinin yanıt `Content-Type` değeri de `application/json` olabilir.

### Deneyin sonucu

Başlıkları yalnızca değerleriyle değil, hangi mesajda ve hangi yönde bulunduklarıyla yorumlamalıyız.

## 12. Deney 10 — Kitap oluşturan Python istemcisini yaz

### Ne yapıyoruz?

Postman’da elle hazırladığımız POST isteğini `create_book_client.py` adlı anlamlı bir Python programıyla gönderiyoruz.

### Neden yapıyoruz?

Postman’ın görünür alanlarının HTTPX kodundaki karşılıklarını görmek ve aynı API işleminin farklı istemcilerce kullanılabildiğini göstermek istiyoruz.

### Teorideki yeri

- Bölüm 3: HTTP isteğinin parçaları
- Bölüm 13: Postman ile HTTPX istemcisinin ortak rolü

### Neden yeni dosya?

`client.py` kitap arama ve listeleme görevini sürdürüyor. Yeni dosyanın görevi kitap oluşturmak olduğu için `create_book_client.py` adını kullanıyoruz. `first.py` veya `test.py` gibi adlar dosyanın yaptığı işi açıklamazdı.

### Yeni dosya — değişen satırlar

```diff
+ import httpx
+
+ new_book = {
+     "title": "İstemciden Sunucuya",
+     "author": {
+         "first_name": "Mert",
+         "last_name": "Aydın"
+     },
+     "available": True,
+     "tags": ["http", "client"],
+     "rating": None
+ }
+
+ try:
+     response = httpx.post(
+         "http://127.0.0.1:8000/api/books",
+         json=new_book,
+         headers={"Accept": "application/json"}
+     )
+ except httpx.ConnectError:
+     print("Connection failed: Could not connect to the server.")
+ else:
+     print("Request method:", response.request.method)
+     print("Request URL:", response.request.url)
+     print("Request Content-Type:", response.request.headers.get("Content-Type"))
+     print("Status code:", response.status_code)
+     print("Response Location:", response.headers.get("Location"))
+     print("Response Content-Type:", response.headers.get("Content-Type"))
+     print("Response body:", response.text)
+
+     if response.status_code == 201:
+         created_book = response.json()
+         print("Created book id:", created_book["id"])
+         print("Created book title:", created_book["title"])
+     else:
+         print("Book could not be created.")
```

### `create_book_client.py` dosyasının tamamı

```python
import httpx

new_book = {
    "title": "İstemciden Sunucuya",
    "author": {
        "first_name": "Mert",
        "last_name": "Aydın"
    },
    "available": True,
    "tags": ["http", "client"],
    "rating": None
}

try:
    response = httpx.post(
        "http://127.0.0.1:8000/api/books",
        json=new_book,
        headers={"Accept": "application/json"}
    )
except httpx.ConnectError:
    print("Connection failed: Could not connect to the server.")
else:
    print("Request method:", response.request.method)
    print("Request URL:", response.request.url)
    print("Request Content-Type:", response.request.headers.get("Content-Type"))
    print("Status code:", response.status_code)
    print("Response Location:", response.headers.get("Location"))
    print("Response Content-Type:", response.headers.get("Content-Type"))
    print("Response body:", response.text)

    if response.status_code == 201:
        created_book = response.json()
        print("Created book id:", created_book["id"])
        print("Created book title:", created_book["title"])
    else:
        print("Book could not be created.")
```

İstemci terminalinde çalıştır:

```bash
python create_book_client.py
```

Beklenen temel çıktı:

```text
Request method: POST
Request URL: http://127.0.0.1:8000/api/books
Request Content-Type: application/json
Status code: 201
Response Location: /api/books/...
Response Content-Type: application/json
Created book title: İstemciden Sunucuya
```

Kimlik, o anda bellekte bulunan kitaplara göre değişebilir.

### `json=new_book` ne yaptı?

HTTPX, Python sözlüğünü JSON gövdesine dönüştürür ve istek `Content-Type` başlığını `application/json` olarak ayarlar. `headers` içindeki `Accept` ise yanıt tercihidir. Aynı değer görünse de iki başlığın görevi farklıdır.

### Deneyin sonucu

Postman ve `create_book_client.py`, aynı POST işlemini kullanan iki farklı istemcidir. Sunucu, istemcinin hangi arayüzle yazıldığına göre ayrı API işlemi gerektirmez.

## 13. Deney 11 — Oluşturulan kitabı mevcut istemciyle ara

### Ne yapıyoruz?

Birinci haftadan gelen `client.py` dosyasının arama kelimesini, yeni oluşturduğumuz kitabın başlığına uygun biçimde değiştiriyoruz.

### Neden yapıyoruz?

Bir istemcinin oluşturduğu kaynağın başka bir istemci işlemiyle okunabildiğini görmek istiyoruz.

### Teorideki yeri

- Bölüm 2.1: Her isteğin ayrı değerlendirilmesi
- Bölüm 14: POST sonrasında kaynağın okunması

### Değişen satırlar

```diff
          params={
-             "search": "Python",
+             "search": "İstemciden",
              "available": "true"
          },
```

### `client.py` dosyasının tamamı

```python
import httpx

try:
    response = httpx.get(
        "http://127.0.0.1:8000/api/books",
        params={
            "search": "İstemciden",
            "available": "true"
        },
        headers={"Accept": "application/json"}
    )
except httpx.ConnectError:
    print("Connection failed: Could not connect to the server.")
    print("Check that the server is running at http://127.0.0.1:8000.")
else:
    print("Request URL:", response.request.url)
    print("Request Accept:", response.request.headers.get("Accept"))
    print("Status code:", response.status_code)
    print("Response Content-Type:", response.headers.get("Content-Type"))
    print("Response body:", response.text)

    if response.status_code == 200:
        books = response.json()

        print("Book count:", len(books))
        print()

        if not books:
            print("No books matched your search.")

        for book in books:
            print("Book title:", book["title"])
            print(
                "Book author:",
                book["author"]["first_name"],
                book["author"]["last_name"]
            )

            if book["available"]:
                print("Availability: Available to borrow")
            else:
                print("Availability: Not available to borrow")

            if book["tags"]:
                print("Tags:")
                for tag in book["tags"]:
                    print("-", tag)
            else:
                print("Tags: No tags")

            if book["rating"] is None:
                print("Rating: Not rated yet")
            else:
                print("Rating:", book["rating"])

            print()
    else:
        print("Book information could not be retrieved.")
```

İstemci terminalinde:

```bash
python client.py
```

Sunucu bu arada yeniden başlatılmadıysa beklenen kitap **İstemciden Sunucuya**dır.

### Sonuç boş gelirse

Önce `create_book_client.py` dosyasını yeniden çalıştır. Çünkü eklenen kitap yalnızca çalışan sunucu sürecinin belleğinde bulunur. Ardından sunucuyu kapatmadan `client.py` dosyasını çalıştır.

### Deneyin sonucu

POST isteği sunucu durumunu değiştirdi; sonraki GET isteği değişen durumu okudu. İki istemci dosyasının görevleri farklı, kullandıkları API aynıdır.

## 14. Deney 12 — Uygulanmayan `PUT`, `PATCH` ve `DELETE` metotlarını dene

### Ne yapıyoruz?

Postman’dan mevcut bir kitap yoluna henüz sunucuda tanımlamadığımız metotları gönderiyoruz.

### Neden yapıyoruz?

Metotların adını bilmekle sunucunun bu işlemleri desteklemesinin aynı olmadığını görmek ve dördüncü haftaya geçiş sınırını belirlemek istiyoruz.

### Teorideki yeri

- Bölüm 5–6: Metot ile yolun birlikte işlem seçmesi
- Bölüm 9: `405 Method Not Allowed`

Şu istekleri sırayla dene:

```http
PUT /api/books/57
```

```http
PATCH /api/books/57
```

```http
DELETE /api/books/57
```

Mevcut sunucuda `/api/books/{book_id}` yolu yalnızca GET için tanımlıdır. Bu nedenle temel beklenti `405` yanıtıdır.

| Metot | Teorideki amaç | Bu haftaki sunucuda sonuç |
|---|---|---|
| `PUT` | Tam temsil ile değiştirme | Henüz uygulanmadı → `405` |
| `PATCH` | Kısmi değişiklik | Henüz uygulanmadı → `405` |
| `DELETE` | Kaynağı silme | Henüz uygulanmadı → `405` |

### Neden şimdi kodlamıyoruz?

Bu metotların gerçek davranışları; bulunmayan kayıt, tam/kısmi güncelleme ayrımı, silme sonrası yanıt ve veri kurallarıyla birlikte tasarlanmalıdır. Bunları dördüncü haftadaki CRUD uygulamasında kitap kataloğuna ekleyeceğiz.

### Deneyin sonucu

Postman’daki metot listesinden DELETE seçebilmek, API’nin DELETE işlemi sunduğu anlamına gelmez. Sunucu kodunda karşılık gelen sözleşme ve davranış bulunmalıdır.

## 15. Deney 13 — Sunucuyu yeniden başlat ve bellek kalıcılığını gözle

### Ne yapıyoruz?

Uvicorn’u kapatıp yeniden çalıştırdıktan sonra eklediğimiz kitapları arıyoruz.

### Neden yapıyoruz?

HTTP isteğinin başarılı olmasıyla verinin kalıcı depolamada saklanmasının farklı konular olduğunu görmek istiyoruz.

### Teorideki yeri

- Bölüm 14: Bellekte tutulan verinin sınırı
- Hafta 01: Sunucu ile veritabanının farklı sorumlulukları

### Adım adım

1. Sunucu terminalinde Ctrl+C kullan.
2. Sunucuyu yeniden başlat:

```bash
python -m uvicorn server:app
```

3. `client.py` ile `search=İstemciden` aramasını tekrar çalıştır.

Beklenen sonuç:

```text
Book count: 0
No books matched your search.
```

### Neden kayboldu?

`books.append(new_book)` çalışan Python listesini değiştirdi. Diskteki `server.py` kaynak koduna yeni kitap yazılmadı ve veritabanı kullanılmadı. Yeni süreç başlarken liste yeniden üç başlangıç kitabıyla oluşturuldu.

### Deneyin sonucu

Önceki POST isteği gerçekten `201` ile başarılı olmuştu. Verinin süreç yeniden başladığında kaybolması, depolama yaklaşımının geçici olmasından kaynaklanır. Kalıcı veri saklamayı altıncı haftada PostgreSQL ile ele alacağız.

## 16. Bir isteği okuma şablonu

Yeni bir HTTP isteği gördüğünde şu sırayı kullan:

```text
1. İstemci kim?
2. Metot ne?
3. Sunucu adresi ve port ne?
4. Yol hangi kaynağı hedefliyor?
5. Sorgu parametresi var mı?
6. İstek başlıkları ne bildiriyor?
7. İstek gövdesi var mı; biçimi ne?
8. Hangi sunucu işlemi eşleşiyor?
9. Durum kodu ne söylüyor?
10. Yanıt başlıkları ve gövdesi ne taşıyor?
```

Örnek:

```http
POST http://127.0.0.1:8000/api/books
Content-Type: application/json
Accept: application/json
```

- İstemci Postman veya `create_book_client.py` olabilir.
- Metot POST’tur.
- Sunucu `127.0.0.1`, port `8000`dir.
- Yol kitap koleksiyonudur.
- Sorgu parametresi yoktur.
- Gövde yeni kitap alanlarını taşır.
- `create_book()` işlemi eşleşir.
- Başarıda `201`, `Location` ve kitap JSON’u döner.

## 17. Çalışırken karşılaşılabilecek sorunlar

### Postman `Could not send request` gösteriyor

Sunucu terminalinin açık olduğunu kontrol et:

```bash
ss -ltnp 'sport = :8000'
```

Uvicorn çalışmıyorsa:

```bash
source api-env/bin/activate
python -m uvicorn server:app
```

### POST hâlâ `405` dönüyor

`server.py` dosyasını kaydetmiş fakat Uvicorn’u yeniden başlatmamış olabilirsin. Ctrl+C ile kapatıp yeniden çalıştır.

### POST `422` dönüyor

Şunları sırayla kontrol et:

1. Body seçimi **raw → JSON** mı?
2. JSON’da tek tırnak, sondan fazla virgül veya Python `True`/`None` değeri var mı?
3. `title`, `author`, `available`, `tags` ve `rating` alanlarının tümü bulunuyor mu?
4. `author` içinde `first_name` ve `last_name` var mı?
5. Hata gövdesindeki `loc` alanı hangi yolu gösteriyor?

### Beklenen kimlik 74 değil

Sunucuyu kapatmadan her başarılı POST yeni kitap ekler. Üretilen kimlik mevcut en büyük kimliğe göre belirlenir. Deneyin amacı belirli sayıyı ezberlemek değildir.

### Postman’da `Content-Type` satırını ben eklemedim

Body bölümünde JSON seçtiğinde Postman bu başlığı otomatik ekleyebilir. Headers bölümündeki gizli veya otomatik başlıkları gösteren bölümü incele.

### Yeni kitap aramada bulunmuyor

- POST gerçekten `201` döndü mü?
- Arama metni yalnızca `title` alanında aranıyor; başlığa uyuyor mu?
- `available=true` koşulu kitabın değeriyle aynı mı?
- POST’tan sonra sunucuyu yeniden başlatıp geçici veriyi sildin mi?

## 18. Haftalık değerlendirme

### Sorular

1. `GET /api/books` ile `POST /api/books` neden aynı fonksiyonu tetiklemez?
2. Postman bu çalışmada istemci mi, sunucu mu, API mi?
3. `search` bilgisi neden gövde yerine sorgu parametresinde taşındı?
4. Yeni kitabın alanları neden istek gövdesinde taşındı?
5. `Accept` ile istek `Content-Type` başlığını karşılaştır.
6. `201 Created` ve `Location` birlikte ne anlatır?
7. POST işleminden sonra GET isteği neden dört kitap görebildi?
8. Aynı POST’un tekrarında neden yeni kimlik oluştu?
9. `404`, `405` ve `422` durumlarını kitap örneğiyle ayır.
10. `DELETE` metodunun Postman’da seçilebilmesi neden sunucunun silme işlemini desteklediğini kanıtlamaz?
11. Hatalı JSON gövdesinde `create_book()` fonksiyonu neden çalışmayabilir?
12. Sunucu yeniden başlayınca eklenen kitabın kaybolması önceki `201` yanıtını yanlış yapar mı?
13. HTTP gövdesi ile JSON neden aynı kavram değildir?
14. POST güvenli veya idempotent midir? Gerekçeni bu uygulamadan ver.
15. Postman ile `create_book_client.py` arasındaki ortak rolü ve kullanım farkını açıkla.

### Cevaplarda aranacak noktalar

- Sunucu metot ve yolu birlikte eşleştirir.
- Postman istemci rolündedir; API sözleşmesini kullanır.
- Sorgu koleksiyon sonucunu süzer, gövde oluşturulacak temsili taşır.
- `Accept` yanıt tercihini, `Content-Type` mesaj gövdesinin biçimini bildirir.
- `201` oluşturmayı, `Location` yeni kaynağın yolunu belirtir.
- POST listeyi değiştirdiği için sonraki GET yeni durumu okur.
- POST genel olarak idempotent değildir; tekrar yeni kayıt oluşturabilir.
- `404` hedef yok, `405` yol var ama metot yok, `422` içerik beklenen yapıya çevrilemiyor ayrımını göstermek gerekir.
- Araçta bir metodu seçmek sunucuda davranış oluşturmaz.
- Bellek verisi süreçle birlikte kaybolabilir; kalıcılık ayrı sorumluluktur.
- Gövde mesaj bölümü, JSON veri biçimidir.
- Postman elle keşif, HTTPX programlı istemci için kullanılır.

## 19. Haftanın sonunda korunacak dosyalar

Proje klasöründe şunlar bulunmalıdır:

```text
book-catalog-api/
├── api-env/
├── server.py
├── client.py
└── create_book_client.py
```

- `server.py`: GET ve POST işlemlerini sunar.
- `client.py`: Kitap listesini sorgular ve gösterir.
- `create_book_client.py`: Yeni kitabı POST ile oluşturur.
- `api-env`: Yerel sanal ortamdır; GitHub’a gönderilmez.

## 20. Kaynaklar

- [Postman — İstek oluşturma ve gönderme](https://learning.postman.com/docs/sending-requests/requests/)
- [Postman — Parametreler ve gövde](https://learning.postman.com/docs/send-requests/create-requests/parameters/)
- [Postman — Başlıkları yapılandırma](https://learning.postman.com/docs/use/send-requests/create-requests/headers/)
- [FastAPI — Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI — Response Status Code](https://fastapi.tiangolo.com/tutorial/response-status-code/)
- [FastAPI — Response Headers](https://fastapi.tiangolo.com/advanced/response-headers/)
- [HTTPX — QuickStart](https://www.python-httpx.org/quickstart/)
- [MDN — HTTP istek metotları](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)
- [MDN — HTTP durum kodları](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)

Bu föyde Postman arayüzünün düğme konumları sürüme göre küçük farklılıklar gösterebilir. Değişmeyen kavramlar metot, URL, parametre, başlık, gövde ve yanıttır.

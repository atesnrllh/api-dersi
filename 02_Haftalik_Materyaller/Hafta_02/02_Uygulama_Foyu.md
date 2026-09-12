# Hafta 02 — Uygulama Föyü

## Aynı Kitap Kataloğunda HTTP Deneyleri

**Ders:** Uygulama Programı Arayüzü (API)  
**Ön koşul:** Birinci haftanın son üç kitaplı `server.py` ve `client.py` dosyaları  
**Araçlar:** VS Code, Python, FastAPI, Uvicorn, HTTPX, Pydantic ve Postman  
**Sürüm:** 1.1 — 12 Eylül 2026 · Üzerinde çalışılıyor

Önce [teorik notu](01_Teorik_Ders_Notu.md) oku. Bu föyde aynı kitap kataloğuyla çalışacağız: bildiğimiz GET isteğini Postman'da kuracak, sonra bir kitabı istek gövdesiyle sunucuya göndereceğiz. Birinci haftanın konuşarak ilerleyen düzenini sürdüreceğiz: **amacı oku → tahmin et → çalıştır → sonucu açıkla**.

> **Kod kutularını kullanma:** Her değişiklikte önce `diff`, hemen ardından değişen `.py` dosyasının tamamı bulunur. GitHub, `diff` içindeki eklenen satırları yeşil, kaldırılanları kırmızı gösterir. Çalışan dosyaya **tam Python kutusunu** kopyala. `+`, `-`, `@@` işaretlerini veya üçlü ters tırnakları dosyaya koyma. Renk tek gösterge değildir; işaretler de değişikliği belirtir.

> **İlerleme:** Sonraki deneye geçmeden beklenen durumla kendi çıktını karşılaştır. Bir deney birden fazla Send düğmesi kullanabilir; her gönderimin amacı ayrı yazılıdır. Süre yetişsin diye adımları atlama. Bu föyün tamamını iki ders saatinde bitirmek zorunlu değil.

### Deney haritası

| Adım | Öğreneceğimiz ayrım | Kod değişikliği |
|---|---|---|
| [Hazırlık](#x00) | Birinci haftanın çalışan durumunu kurmak | Başlangıç dosyaları |
| [1](#x01) | Aynı isteği başka istemciden göndermek | Yok |
| [2](#x02) | Sorgu parametreleri ve iki koşul | Yok |
| [3](#x03) | Tek kitap, boş liste, `404` ve `422` | Yok |
| [4](#x04) | `Accept` ile yanıt `Content-Type` | Yok |
| [5](#x05) | Yolun bulunması ile metot desteği | Yok |
| [6](#x06) | Gövde modelini tanımlamak | `server.py` |
| [7](#x07) | POST ile veri eklemek, `201` | `server.py` |
| [8](#x08) | `Location` ile yeni kaynağı bulmak | `server.py` |
| [9](#x09) | Aynı GET ve POST'u tekrar etmek | Yok |
| [10](#x10) | Zorunlu alan ile `null` değeri | Yok |
| [11](#x11) | Geçerli JSON içindeki yanlış veri | Yok |
| [12](#x12) | JSON yazım hatasını ayırmak | Yok |
| [13](#x13) | Aynı POST'u Python ile göndermek | Yeni `create_book.py` |
| [14](#x14) | Eklenen kitabı diğer istemciden okumak | `client.py` |
| [15](#x15) | Bellekte kayıt ile kalıcı kayıt | Yok |

<a id="x00"></a>

## Hazırlık — Birinci haftanın son durumundan başla

**Ne yapıyoruz?** Üç kitaplı sunucuyu ve son okuma istemcisini çalıştırıyoruz.  
**Neden?** Yeni bir davranışı, başlangıç verisi ve çalışan kod belli olduğunda yorumlayabiliriz.  
**Teorideki yeri:** [Bölüm 1 — Aynı isteği başka istemciyle göndermek](01_Teorik_Ders_Notu.md#t01).

### VS Code ve iki terminal

1. VS Code'da birinci hafta kullandığın proje klasörünü aç. Masaüstündeki örnek `/home/nuri/Desktop/API`, dizüstündeki örnek WSL içindeki `book-catalog-api` idi; bilgisayarında hangi klasörü kullanıyorsan onu aç.
2. `server.py` ve `client.py` dosyalarını kontrol et. Mevcut çalışmanı korumak için düzenlemeden önce iki dosyanın kopyasını proje içinde ayrı bir yedek klasöre koyabilirsin.
3. **Terminal → New Terminal** ile iki terminal aç. İkisinde de `pwd` ile proje klasöründe olduğunu kontrol et.
4. Her iki terminalde sanal ortamı etkinleştir:

```bash
source api-env/bin/activate
```

`api-env` yoksa [birinci haftanın kurulum adımlarını](../Hafta_01/02_Uygulama_Foyu.md) tamamla. Aynı bilgisayarda çalışan ortamın varsa yeniden kurmana gerek yoktur. Paket kontrolü:

```bash
python -c "import fastapi, uvicorn, httpx, pydantic; print('Packages are ready.')"
```

Eksik paket hatası varsa, daha önce kurduğun uv ile **bu proje ortamına** kur:

```bash
uv pip install --python api-env/bin/python fastapi uvicorn httpx
```

Pydantic, FastAPI ile birlikte kurulur; ayrı bir rakip API çatısına geçmiyoruz. Bu föy Python 3.10 veya üzerini ve Pydantic 2'deki `model_dump()` yöntemini kullanır.

### Başlangıç `server.py` dosyasının tamamı

Bu sürüm birinci haftanın son sürümüdür. Özellikle 73 numaralı üçüncü kitabın bulunduğuna dikkat et.

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

### Başlangıç `client.py` dosyasının tamamı

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

### Sunucuyu ve istemciyi çalıştır

Dosyaları **Ctrl+S** ile kaydet. Sunucu terminalinde:

```bash
python -m uvicorn server:app
```

`Uvicorn running on http://127.0.0.1:8000` satırını gördükten sonra bu terminali açık bırak. İstemci terminalinde:

```bash
python client.py
```

Beklenen temel sonuç `200`, bir kitap ve **Python ile Web API** başlığıdır. Sunucu terminalinin adı çalışan süreç nedeniyle `python`, istemci işi bitince terminalin adı `bash` görünebilir. Bu, iki farklı sunucu olduğu anlamına gelmez.

### Bu föyde yeniden başlatma ne demek?

Sunucu kodunu değiştirdiğimiz her adımda:

1. Dosyayı **Ctrl+S** ile kaydet.
2. Sunucunun çalıştığı terminalde **Ctrl+C** yap; kapanış mesajını bekle.
3. Aynı terminalde yeniden çalıştır:

```bash
python -m uvicorn server:app
```

**Ctrl+Z kullanma:** Süreci duraklatıp portu meşgul bırakabilir. Bu föyde `--reload` kullanmıyoruz; yeniden başlatmanın veriyi ne zaman sıfırladığını birlikte takip edeceğiz. İstemci dosyası değişince sunucuyu yeniden başlatmak gerekmez; istemciyi tekrar çalıştırırız.

### Postman'da ilk düzen

Postman masaüstü uygulamasını aç. Yüklü değilse [resmî indirme sayfasından](https://www.postman.com/downloads/) işletim sistemine uygun sürümü kur. Web sürümünde yerel sunucuya erişim için Desktop Agent kullanmak gerekebilir; adımlar masaüstü uygulamasına göredir.

1. **New → HTTP Request** ile bir istek aç. Arayüz sürümüne göre bu seçenek `+` sekmesinden de açılabilir.
2. **Authorization → No Auth** seç. Bu sunucu henüz kimlik doğrulaması istemiyor.
3. Metot seçiciyi, URL alanını, **Params**, **Headers**, **Body** ve **Send** bölümlerini bul.
4. Yanıt alanında durum kodunun, yanıt **Headers** ve yanıt **Body** bölümlerinin yerini gör.

İstekleri ayırmak için GET deneylerini bir sekmede, POST deneylerini yeni bir sekmede yapacağız. Bir isteği kaydetmek düzenlemeyi korur; sunucuya gönderen işlem **Send** düğmesidir. Arayüzü bulmak için [Postman başlangıç rehberi](https://learning.postman.com/docs/getting-started/quick-start/) kullanılabilir.

<a id="x01"></a>

## Deney 1 — Bildiğimiz GET isteğini Postman ile gönder

**Ne yapıyoruz?** `client.py` içindeki isteğin aynısını Postman'da hazırlıyoruz.  
**Neden?** API iletişiminin tek bir istemci programa bağlı olmadığını görmek için.  
**Teorideki yeri:** [Bölüm 1–2 — İstemci ve istek parçaları](01_Teorik_Ders_Notu.md#t01).

**Başlangıç:** Sunucu çalışıyor; listede 42, 57 ve 73 var. Kod değişmiyor.

### Uygula

1. Metot: **GET**.
2. URL alanına yalnızca şunu yaz:

```text
http://127.0.0.1:8000/api/books
```

3. **Params** bölümünde etkin iki satır ekle:

| Key | Value |
|---|---|
| `search` | `Python` |
| `available` | `true` |

4. İstek **Headers** bölümüne `Accept` → `application/json` ekle.
5. **Body → none** seç; Send'e bas.

Oluşan URL:

```text
http://127.0.0.1:8000/api/books?search=Python&available=true
```

### Gözlem ve anlam

Durum `200`, yanıt `Content-Type` değeri `application/json` olmalı. Gövde, 73 numaralı kitabı içeren **tek elemanlı liste** olmalı. Python istemcisi başlığı ayrı satırda yazmıştı; Postman JSON'u gösterir. Verinin aynı olması, ekranın aynı görünmesini gerektirmez.

**Kontrol sorusu:** İstemciyi değiştirince `server.py` kodunu değiştirdik mi?

<details><summary>Cevap</summary>

Hayır. Aynı API işlemini başka istemciden kullandık. Postman sunucuyu veya kitap listesini oluşturmadı.

</details>

<a id="x02"></a>

## Deney 2 — Her seferinde bir sorgu değerini değiştir

**Ne yapıyoruz?** Aynı GET yolunda filtreleri kontrollü değiştiriyoruz.  
**Neden?** Sonucu hangi girdinin değiştirdiğini görebilmek; `search` adını otomatik, bütün alanları arayan bir komut sanmamak için.  
**Teorideki yeri:** [Bölüm 3 — Yol, sorgu ve dönen alanlar](01_Teorik_Ders_Notu.md#t03).

**Başlangıç:** Deney 1'in GET sekmesi. Kod değişmiyor. Her satırda Send'e basmadan önce gelecek kimlikleri tahmin et.

| Adım | Yapılacak tek değişiklik | Tam sorgu | Beklenen kimlikler |
|---|---|---|---|
| A | `search` değerini `API` yap | `?search=API&available=true` | 42 ve 73 |
| B | `available` değerini `false` yap | `?search=API&available=false` | Hiçbiri: `[]` |
| C | `search` değerini tamamen sil; satır etkin kalsın | `?search=&available=false` | 57 |
| D | `available` satırının işaretini kaldır | `?search=` | 42, 57, 73 |
| E | `search` satırının da işaretini kaldır | Sorgu yok | 42, 57, 73 |

Her adım `200` döndürür. B'de kitap olmaması başarısız HTTP işlemi değildir. C'deki boş değer bir boşluk karakteri içermez; boş metindir. D'de boş metin bütün başlıklarla eşleşir. E'de parametre olmadığı için sunucudaki boş metin varsayılanı kullanılır; D ile aynı sonuca farklı yoldan ulaşırız.

A'da iki kitap beklememizin nedeni: **Python ile Web API** başlığında da API bulunur. `search`, bu uygulamada başlığın içinde arama yapar; etiketleri kontrol etmez. `available=false`, uygunluk değeri false olan kayıtları seçer; filtreyi kapatmak değildir.

**Kontrol sorusu:** URL'de `available=true&search=API` yazsaydık sonuç değişir miydi?

<details><summary>Cevap</summary>

Bu sunucuda hayır. Parametrelerin URL'deki sırası, fonksiyonun koşulları değerlendirme sırasını belirlemez. Fonksiyonumuz iki koşulu birlikte uygular.

</details>

<a id="x03"></a>

## Deney 3 — Koleksiyon ile tek kitabın yanıtını ayır

**Ne yapıyoruz?** Sorgu parametrelerini kaldırıp yolun sonundaki kimliği değiştiriyoruz.  
**Neden?** Boş liste, bulunamayan kaynak ve geçersiz kimlik arasındaki farkı yanıt üzerinden okuyabilmek için.  
**Teorideki yeri:** [Bölüm 3–4 — Yol parametresi ve yanıt](01_Teorik_Ders_Notu.md#t03).

**Başlangıç:** GET sekmesinde tüm Params satırları devre dışı, Body none. Kod değişmiyor.

Sırayla şu tam URL'leri gönder:

| URL | Beklenen kod | Okunacak sonuç |
|---|---|---|
| `http://127.0.0.1:8000/api/books/57` | `200` | Tek kitap nesnesi; dışta liste köşeli parantezi yok. |
| `http://127.0.0.1:8000/api/books/999` | `404` | `{"detail":"Book not found"}` |
| `http://127.0.0.1:8000/api/books/abc` | `422` | Hata konumunda `path` ve `book_id`. |

`999` tam sayıdır; bizim kitap arama fonksiyonumuz çalışır, kitabı bulamaz. `abc`, `book_id: int` beklentisine uymaz; FastAPI bizim arama fonksiyonumuzu çağırmadan doğrulama hatası döndürür.

**Kontrol sorusu:** `404` gördüğümüzde “sunucu yanıt vermedi” diyebilir miyiz?

<details><summary>Cevap</summary>

Hayır. `404` bir HTTP yanıtının kodudur. Bağlantı kurulamasaydı bir HTTP kodu yerine bağlantı hatası görürdük.

</details>

<a id="x04"></a>

## Deney 4 — İstenen yanıt biçimiyle gelen biçimi karşılaştır

**Ne yapıyoruz?** Aynı GET isteğinde yalnızca `Accept` başlığını değiştiriyoruz.  
**Neden?** Bir başlığın anlamını bilmek ile sunucunun o başlığı desteklemesi arasındaki farkı görmek için.  
**Teorideki yeri:** [Bölüm 5 — Başlıkların yönü](01_Teorik_Ders_Notu.md#t05).

**Başlangıç:** GET `http://127.0.0.1:8000/api/books/57`, Params boş, Body none. Kod değişmiyor.

1. `Accept: application/json` ile gönder. `200` ve JSON kitabı gör.
2. Aynı başlık satırının değerini `text/plain` yap; tekrar gönder.
3. Yanıt **Headers** bölümündeki `Content-Type` değerini oku.

Bizim sunucumuz yine `application/json` döndürür. `Accept: text/plain`, sunucudaki JSON üretimini otomatik olarak metin üretimine dönüştürmedi. Sunucuya bu tercihe göre farklı biçim üretme veya tercihi reddetme davranışı eklemedik.

**Sonraki adım için:** İstek `Accept` değerini tekrar `application/json` yap. Bir başlığı ikinci kez eklemek yerine mevcut satırı düzenle.

**Kontrol sorusu:** İstek `Accept` ile yanıt `Content-Type` aynı yöndeki mesajda mı bulunuyor?

<details><summary>Cevap</summary>

Hayır. İlki istemcinin gönderdiği tercihtir; ikincisi sunucunun gönderdiği gövdenin biçimini bildirir.

</details>

<a id="x05"></a>

## Deney 5 — Yol var; POST işlemi var mı?

**Ne yapıyoruz?** Kitap koleksiyonu yoluna POST gönderiyoruz.  
**Neden?** Aynı yolun farklı metotlarla farklı işlemler tanımladığını göstermek için.  
**Teorideki yeri:** [Bölüm 6 — Metot ile yol](01_Teorik_Ders_Notu.md#t06).

**Başlangıç:** Sunucuda henüz yalnızca iki GET işlemi var. Kod değişmiyor.

1. Postman'da **yeni bir HTTP Request sekmesi** aç. Authorization: No Auth.
2. Metodu **POST**, URL'yi `http://127.0.0.1:8000/api/books` yap.
3. Params boş olsun. `Accept: application/json` ekle. Body: none.
4. Send'e bas; yanıt kodunu, gövdesini ve yanıt **Headers → Allow** değerini oku.

Beklenen yanıt:

```text
Status: 405 Method Not Allowed
Allow: GET
Body: {"detail":"Method Not Allowed"}
```

Bu aşamada sorun eksik kitap gövdesi değildir; henüz POST'u karşılayan işlem yoktur. JSON yazmak tek başına bunu çözmez. `Allow`, bu hedef için desteklenen metodu gösterir; bütün API'nin uç nokta listesi değildir.

**Kontrol sorusu:** `client.py` dosyasını değiştirerek sunucuya POST desteği ekleyebilir miyiz?

<details><summary>Cevap</summary>

Hayır. İstemcinin isteğini değiştirmek ve sunucunun o isteği işleyecek fonksiyonunu yazmak ayrı işlerdir.

</details>

<a id="x06"></a>

## Deney 6 — Yeni kitabın gövde modelini tanımla

**Ne yapıyoruz?** Yazar ve kitap için beklenen alanları tanımlıyoruz.  
**Neden?** İstekten hangi veriyi beklediğimizi açıkça yazmak; ardından bu tanımı POST işlemine bağlamak için.  
**Teorideki yeri:** [Bölüm 7 — İstek gövdesi ve model](01_Teorik_Ders_Notu.md#t07).

Bu adımın yeni konusu yalnızca **gövdenin yapısıdır**. Henüz POST fonksiyonunu eklemiyoruz.

### Yeni Python ifadelerini oku

| İfade | Burada yaptığı iş |
|---|---|
| `from pydantic import BaseModel` | Doğrulama modeli yazmak için kullanacağımız sınıfı içe aktarır. |
| `class AuthorCreate(BaseModel)` | Yazar verisinin alanlarını tanımlayan model sınıfını oluşturur. |
| `first_name: str` | Gönderilmesi gereken metin alanını bildirir. |
| `class BookCreate(BaseModel)` | Yeni kitap isteğinin veri modelini tanımlar. |
| `author: AuthorCreate` | Yazar alanında beklenen iç içe yapıyı belirtir. |
| `tags: list[str]` | Etiketlerin metinlerden oluşan liste olacağını belirtir. |
| `rating: float \| None` | Puanın sayı veya `None` olabileceğini belirtir; varsayılan olmadığı için alan zorunludur. |

Buradaki sınıflar kitap kayıtlarının kendisi değildir; gelecek verinin tanımıdır. Birinci haftadaki `books` listesi ve GET fonksiyonları aynı kalır. `id` oluşturma modelinde yoktur: onu birazdan sunucu üretecek. Bu basit modelde fazladan alanları reddetme kuralı da yazmadık; istemcinin eklediği bir `id` bizim kimlik üretimimizi belirlemez.

### Değişen satırlar

```diff
--- server.py
+++ server.py
@@ -1,4 +1,18 @@
 from fastapi import FastAPI, HTTPException
+from pydantic import BaseModel
+
+class AuthorCreate(BaseModel):
+    first_name: str
+    last_name: str
+
+
+class BookCreate(BaseModel):
+    title: str
+    author: AuthorCreate
+    available: bool
+    tags: list[str]
+    rating: float | None
+
 
 app = FastAPI()
```

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class AuthorCreate(BaseModel):
    first_name: str
    last_name: str


class BookCreate(BaseModel):
    title: str
    author: AuthorCreate
    available: bool
    tags: list[str]
    rating: float | None


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

### Çalıştır ve gözlemle

1. Kaydet; sunucuyu hazırlık bölümündeki gibi Ctrl+C ile kapatıp yeniden başlat.
2. GET sekmesinde `http://127.0.0.1:8000/api/books` isteğini parametresiz gönder: üç kitap, `200`.
3. POST sekmesinde önceki gövdesiz isteği gönder: hâlâ `405`.

**Bu sonuç beklenir.** Model sınıfı yazmak kendiliğinden bir POST uç noktası oluşturmaz. Sonraki adım modeli bir işleme bağlayacak.

**Kontrol sorusu:** `rating` alanını yazıp `null` göndermek ile bu alanı hiç yazmamak aynı mı?

<details><summary>Cevap</summary>

Bu modelde aynı değil. Değer `null` olabilir ama alanın gönderilmesi gerekir. Deney 10'da bunu yanıttan doğrulayacağız.

</details>

<a id="x07"></a>

## Deney 7 — POST gövdesiyle kitap oluştur ve `201` gör

**Ne yapıyoruz?** Modeli yeni bir POST fonksiyonuna bağlıyor, geçerli kitabı listeye ekliyoruz.  
**Neden?** İstemciden gelen veriyle sunucudaki durumun değişmesini ve oluşturma yanıtını görmek için.  
**Teorideki yeri:** [Bölüm 8 — Kitabı oluşturmak](01_Teorik_Ders_Notu.md#t08).

### Yeni fonksiyonu sırayla oku

1. `@app.post(..., status_code=201)`, bu yolun POST işlemini ve normal başarı kodunu tanımlar.
2. `book_data: BookCreate`, gövdenin bu modele göre doğrulanmasını sağlar. Geçerli veri fonksiyona bir model nesnesi olarak gelir.
3. Döngü, mevcut en büyük kimliğin bir fazlasını bulur. 42, 57, 73 için sonuç 74'tür. `len(books) + 1` kullanmıyoruz; kitap sayısı en büyük kimlik değildir.
4. `model_dump()`, modeli ve içindeki yazar modelini sözlüğe dönüştürür. Böylece birinci haftadan gelen liste/sözlük düzeni korunur.
5. Yeni kimliği sözlüğe ekler, `books.append(new_book)` ile listeye koyarız.
6. `return new_book`, oluşturulan veriyi JSON yanıtının gövdesi olarak döndürür.

Bu kimlik yöntemi sırayla istek gönderdiğimiz tek süreçli ders deneyi içindir. Çok kullanıcılı kalıcı bir sistemde kimlik üretimini veritabanıyla düzenleyeceğiz.

### Değişen satırlar

```diff
--- server.py
+++ server.py
@@ -76,3 +76,18 @@
             return book
 
     raise HTTPException(status_code=404, detail="Book not found")
+
+
+@app.post("/api/books", status_code=201)
+def create_book(book_data: BookCreate):
+    next_book_id = 1
+
+    for book in books:
+        if book["id"] >= next_book_id:
+            next_book_id = book["id"] + 1
+
+    new_book = book_data.model_dump()
+    new_book["id"] = next_book_id
+    books.append(new_book)
+
+    return new_book
```

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class AuthorCreate(BaseModel):
    first_name: str
    last_name: str


class BookCreate(BaseModel):
    title: str
    author: AuthorCreate
    available: bool
    tags: list[str]
    rating: float | None


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


@app.post("/api/books", status_code=201)
def create_book(book_data: BookCreate):
    next_book_id = 1

    for book in books:
        if book["id"] >= next_book_id:
            next_book_id = book["id"] + 1

    new_book = book_data.model_dump()
    new_book["id"] = next_book_id
    books.append(new_book)

    return new_book
```

### POST isteğini hazırla

1. Kaydet ve sunucuyu yeniden başlat. Başlangıç yine **üç kitap**.
2. POST sekmesinde metot **POST**, URL `http://127.0.0.1:8000/api/books`, Params boş olsun.
3. **Body → raw → JSON** seç. Açılır biçim seçeneğinde JSON'u seçtiğinde Postman istek `Content-Type: application/json` başlığını hazırlar. Headers bölümünden kontrol et; çelişen ikinci bir Content-Type satırı ekleme.
4. `Accept: application/json` başlığı kalsın.
5. Body alanına aşağıdaki **gövdenin tamamını** koy:

```json
{
  "title": "HTTP'yi Anlamak",
  "author": {
    "first_name": "Selin",
    "last_name": "Aras"
  },
  "available": true,
  "tags": [
    "http",
    "web"
  ],
  "rating": null
}
```

JSON'da `true` ve `null`; Python'da `True` ve `None` yazdığımızı hatırla. Bu kutu Python dosyasına değil, Postman'ın JSON gövdesine yazılır.

6. **Bir kez** Send'e bas.

### Beklenen sonuç

- Kod: `201 Created`.
- Yanıt `Content-Type`: `application/json`.
- Gövde: Gönderdiğin kitap bilgileri ve sunucunun eklediği `id: 74`.
- `Location`: Henüz eklemedik; sonraki deneyde ekleyeceğiz.

GET sekmesinde `http://127.0.0.1:8000/api/books/74` isteğini gönder. `200` ve yeni kitap gelmeli. Ardından parametresiz `GET /api/books` gönder: **dört kitap** olmalı.

`201` kodunu yazmış olmamız tek başına kayıt yaratmaz. Kaydı yapan satır `books.append(new_book)`; GET ile okuma, o değişikliği ayrıca gözlemlememizi sağlar.

**Kontrol sorusu:** Postman gövdesine kimlik yazmadık. Yanıttaki 74 nereden geldi?

<details><summary>Cevap</summary>

Sunucudaki oluşturma fonksiyonu mevcut kimliklerden üretti. Bu API'de istemcinin verdiği kitap bilgisi ile sunucunun eklediği kimlik ayrı sorumluluklardır.

</details>

<a id="x08"></a>

## Deney 8 — Yeni kitabın adresini `Location` ile bildir

**Ne yapıyoruz?** Oluşturma yanıtına yalnızca yeni kaynağın adresini ekliyoruz.  
**Neden?** İstemcinin başarılı oluşturma sonrasında kaynağa nereden ulaşacağını yanıttan öğrenmesi için.  
**Teorideki yeri:** [Bölüm 5 ve 8 — Yanıt başlıkları ve Location](01_Teorik_Ders_Notu.md#t08).

`Response` içe aktarılır. Fonksiyondaki `response: Response` nesnesini FastAPI sağlar; POST gövdesine `response` diye alan eklemeyiz. `response.headers[...]` yanıtın başlığını ayarlar. `f"/api/books/{next_book_id}"` ifadesi kimliği metne yerleştirir: 74 için `/api/books/74`.

### Değişen satırlar

```diff
--- server.py
+++ server.py
@@ -1,4 +1,4 @@
-from fastapi import FastAPI, HTTPException
+from fastapi import FastAPI, HTTPException, Response
 from pydantic import BaseModel
 
 class AuthorCreate(BaseModel):
@@ -79,7 +79,7 @@
 
 
 @app.post("/api/books", status_code=201)
-def create_book(book_data: BookCreate):
+def create_book(book_data: BookCreate, response: Response):
     next_book_id = 1
 
     for book in books:
@@ -90,4 +90,6 @@
     new_book["id"] = next_book_id
     books.append(new_book)
 
+    response.headers["Location"] = f"/api/books/{next_book_id}"
+
     return new_book
```

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

class AuthorCreate(BaseModel):
    first_name: str
    last_name: str


class BookCreate(BaseModel):
    title: str
    author: AuthorCreate
    available: bool
    tags: list[str]
    rating: float | None


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


@app.post("/api/books", status_code=201)
def create_book(book_data: BookCreate, response: Response):
    next_book_id = 1

    for book in books:
        if book["id"] >= next_book_id:
            next_book_id = book["id"] + 1

    new_book = book_data.model_dump()
    new_book["id"] = next_book_id
    books.append(new_book)

    response.headers["Location"] = f"/api/books/{next_book_id}"

    return new_book
```

### Çalıştır ve gözlemle

1. Kaydet, sunucuyu yeniden başlat. **Deney 7'de eklenen kayıt silindi; tekrar üç başlangıç kitabı var.**
2. POST sekmesindeki Deney 7 gövdesini değiştirmeden **bir kez** gönder.
3. `201` yanıtında **Headers → Location** değerini oku: `/api/books/74`.
4. GET sekmesine geç; sunucu adresi ile bu yolu birleştirerek gönder:

```text
http://127.0.0.1:8000/api/books/74
```

Beklenen sonuç `200` ve **HTTP'yi Anlamak** kitabıdır. Parametresiz GET listesinde dört kitap bulunur.

Bu adımda yeni kayıt eklendiği için `201`, o kaydı okuduğumuz için `200` aldık. `Location` bir yanıt başlığıdır; JSON gövdesindeki yeni bir kitap alanı değildir.

**Kontrol sorusu:** `Location` alanını eklemek Postman'ın kendiliğinden GET isteği göndermesi anlamına mı gelir?

<details><summary>Cevap</summary>

Hayır. Burada `201` yanıtından adresi öğrendik ve ikinci isteği kendimiz gönderdik. Bu bir `3xx` yönlendirme yanıtı değildir.

</details>

<a id="x09"></a>

## Deney 9 — Aynı isteği tekrar göndermenin etkisini ölç

**Ne yapıyoruz?** GET ve POST tekrarlarının kitap sayısına etkisini karşılaştırıyoruz.  
**Neden?** İdempotentlik kavramını yalnızca tanımla değil, değişen kaynak durumu üzerinden anlamak için.  
**Teorideki yeri:** [Bölüm 9 — İsteği tekrarlamak](01_Teorik_Ders_Notu.md#t09).

**Başlangıç:** Deney 8 tamamlandı; dört kitap var, son kimlik 74. Sunucuyu yeniden başlatma. Kod değişmiyor.

| Sıra | Yap | Beklenen gözlem |
|---|---|---|
| 1 | Parametresiz `GET /api/books` gönder | `200`, dört kitap. |
| 2 | Aynı GET'i tekrar gönder | `200`, yine dört kitap. |
| 3 | POST sekmesinde aynı kitap gövdesini bir kez daha gönder | `201`, kimlik 75, `Location: /api/books/75`. |
| 4 | Parametresiz GET listesini tekrar oku | Beş kitap; 74 ve 75 aynı başlığı taşır. |

GET yalnızca okudu. POST ise ikinci gönderimde yeni kayıt ekledi. İki başarılı yanıtın ikisi de `201` olsa bile sunucudaki etki tekrarlandı; bu POST idempotent değildir.

Aynı başlık bizim uygulamada yasaklanmadı. “Aynı kitap zaten var” denetimi HTTP'nin kendiliğinden yaptığı bir iş değildir; gerekiyorsa API'nin iş kuralı olarak yazılır.

**Kontrol sorusu:** GET yanıtındaki kitap sayısı başka bir kullanıcı kitap ekleyince değişirse GET idempotent olmaktan çıkar mı?

<details><summary>Cevap</summary>

Hayır. Tanım yanıtın sonsuza kadar aynı kalmasıyla değil, aynı okuma isteğinin amaçlanan etkisiyle ilgilidir. Başka bir işlemin veriyi değiştirmesi ayrı konudur.

</details>

<a id="x10"></a>

## Deney 10 — Eksik alan ile `null` değerini ayır

**Ne yapıyoruz?** JSON yazımını doğru tutarak iki zorunlu alanı ayrı ayrı eksiltiyoruz.  
**Neden?** Geçerli JSON'un model için yeterli olmayabileceğini; “değer yok” ile “alan gönderilmedi” ayrımını görmek için.  
**Teorideki yeri:** [Bölüm 7 ve 10 — Model ve doğrulama](01_Teorik_Ders_Notu.md#t10).

**Başlangıç:** Beş kitap var. POST aynı URL'de; Body raw/JSON, Accept application/json. Kod değişmiyor. Her hata denemesinde aşağıdaki gövdenin **tamamını** kullan; önceki hatayı taşımayalım.

### A. Yalnızca yazar soyadını çıkar

```json
{
  "title": "HTTP'yi Anlamak",
  "author": {
    "first_name": "Selin"
  },
  "available": true,
  "tags": [
    "http",
    "web"
  ],
  "rating": null
}
```

Bir kez gönder. Beklenen kod `422`. Yanıttaki `detail` listesinde ilgili hata öğesinin `loc` değeri:

```json
["body", "author", "last_name"]
```

Sırayla “gövde → yazar nesnesi → soyadı alanı” diye oku. `type` değeri eksik alanı, `msg` açıklamayı belirtir. Bu, kitap bulunamadı hatası değildir; yeni kitap verisi eksiktir.

### B. Soyadını geri koy; yalnızca `rating` alanını çıkar

```json
{
  "title": "HTTP'yi Anlamak",
  "author": {
    "first_name": "Selin",
    "last_name": "Aras"
  },
  "available": true,
  "tags": [
    "http",
    "web"
  ]
}
```

Bir kez gönder. Beklenen kod yine `422`; bu kez hata konumu `body` → `rating` olur. Deney 8'de `rating: null` kabul edilmişti. Burada alanı hiç göndermedik.

Parametresiz GET ile kitap sayısını kontrol et: **hâlâ beş**. İki istek de oluşturma fonksiyonuna geçemedi; listeye ekleme yapılmadı.

**Önemli çalışma ayrıntısı:** Bir hatayı düzeltmek için geçerli gövdeyi yeniden göndermek yeni kitap ekler. Bu bölümde başarılı istek göndermemiz gerekmiyor; olumlu örneği zaten Deney 8'de gördük.

**Kontrol sorusu:** `rating: float | None` yazmak neden “istersen bu alanı hiç gönderme” anlamına gelmedi?

<details><summary>Cevap</summary>

Tür bildirimi değerin neler olabileceğini söyler. Bu modelde varsayılan değer vermediğimiz için alan zorunludur. `None` kabul etmek ayrı bir özelliktir.

</details>

<a id="x11"></a>

## Deney 11 — JSON doğru; mantıksal değer dönüştürülemiyor

**Ne yapıyoruz?** Tam gövdede yalnızca `available` değerini `"belki"` yapıyoruz.  
**Neden?** JSON'un metin değerini kabul etmesiyle API modelinin o alan için metni kabul etmesinin farklı olduğunu görmek için.  
**Teorideki yeri:** [Bölüm 10 — Türler ve dönüşüm](01_Teorik_Ders_Notu.md#t10).

**Başlangıç:** Beş kitap. POST raw/JSON. Kod değişmiyor; tam gövde:

```json
{
  "title": "HTTP'yi Anlamak",
  "author": {
    "first_name": "Selin",
    "last_name": "Aras"
  },
  "available": "belki",
  "tags": [
    "http",
    "web"
  ],
  "rating": null
}
```

Gönder. Beklenen kod `422`; hata konumunda `body` → `available`, hata türünde mantıksal değere dönüştürmeyle ilgili açıklama bulunur. GET listesinde hâlâ beş kitap vardır.

`"belki"` geçerli bir JSON metnidir; bu yüzden sorun JSON yazımı değildir. Bizim alanımız mantıksal değer bekler. Pydantic bazı tanınan metinleri dönüştürebildiğinden yanlış örnek olarak `"true"` kullanmadık. Normal gövdelerimizde doğru JSON türünü, yani tırnaksız `true` veya `false` gönderiyoruz.

**Kontrol sorusu:** URL'de `available=false` yazabiliyorken gövdede neden JSON türünü ayrıca konuşuyoruz?

<details><summary>Cevap</summary>

URL sorgusu metinsel girdiler taşır; FastAPI bunları parametrenin türüne çevirir. JSON ise metin, sayı, mantıksal değer ve null gibi türleri kendi yazımıyla ayırır. Bunlar verinin iki farklı taşınma biçimidir.

</details>

<a id="x12"></a>

## Deney 12 — Bu kez JSON yazımını boz

**Ne yapıyoruz?** Bütün alanları doğru tutup son alanın sonuna fazladan virgül koyuyoruz.  
**Neden?** Önceki model hatalarından farklı olarak gövdenin JSON olarak bile çözümlenemediği durumu görmek için.  
**Teorideki yeri:** [Bölüm 10 — JSON yazımı ve hata katmanları](01_Teorik_Ders_Notu.md#t10).

**Başlangıç:** Beş kitap. POST raw/JSON. Kod değişmiyor. Aşağıdaki metin **bilerek geçersizdir**; hata `rating` satırının sonundaki virgüldür:

```text
{
  "title": "HTTP'yi Anlamak",
  "author": {
    "first_name": "Selin",
    "last_name": "Aras"
  },
  "available": true,
  "tags": [
    "http",
    "web"
  ],
  "rating": null,
}
```

Gönder. Bu FastAPI uygulamasının varsayılanında `422` ve JSON çözümlemeyle ilgili hata ayrıntısı bekleriz. Hata türü `json_invalid` olarak görülebilir; konum, JSON içindeki hata yerini gösterebilir. Gövde tümüyle çözümlenemediği için bir alanın veri türünü tartışma aşamasına gelmedik.

GET listesinde hâlâ beş kitap olmalı. Deney 10–12'de aynı `422` kodunu görmüş olsak da **hata nedenleri aynı değildi**. `detail` içeriğini okumamızın nedeni budur. Diğer API'ler JSON yazım hatasını `400` ile bildirebilir; buradaki gözlemi evrensel kural saymayacağız.

**Sonraki adım için:** POST sekmesine aşağıdaki geçerli gövdeyi geri koy; **Send'e basma**.

```json
{
  "title": "HTTP'yi Anlamak",
  "author": {
    "first_name": "Selin",
    "last_name": "Aras"
  },
  "available": true,
  "tags": [
    "http",
    "web"
  ],
  "rating": null
}
```

**Kontrol sorusu:** `422` gördüğümüz için JSON yazımının kesin doğru olduğunu söyleyebilir miyiz?

<details><summary>Cevap</summary>

Bu FastAPI örneğinde hayır. Kodun yanında hata ayrıntısını da okumak gerekir; varsayılan davranış JSON çözümleme hatalarını da `422` ile bildirir.

</details>

<a id="x13"></a>

## Deney 13 — Aynı kitabı Python istemcisiyle oluştur

**Ne yapıyoruz?** Postman'da kullandığımız kitap verisini bu kez HTTPX ile POST ediyoruz.  
**Neden?** İstemciyi değiştirip aynı HTTP işlemini program içinden kurabilmek için.  
**Teorideki yeri:** [Bölüm 11 — İletişimin bütünü](01_Teorik_Ders_Notu.md#t11).

**Başlangıç:** Sunucu kodu Deney 8 sürümüdür. Karşılaştırmayı aynı veriyle yapabilmek için şimdi sunucuyu Ctrl+C ile kapatıp yeniden başlat. Parametresiz GET'te **üç kitap** olduğunu doğrula. POST sekmesindeki Send'e basma.

### Yeni dosyanın görevi

VS Code Explorer'da `server.py` ile **aynı klasörde** `create_book.py` oluştur. `api-env` klasörünün içine oluşturma. Mevcut `client.py` okuma yapmayı sürdürecek; yeni dosya kitap oluşturma isteğini gönderecek. Böylece çalıştırdığın dosyanın görevi adından anlaşılır.

Yeni olan ifadeler:

- `httpx.post(...)`: GET yerine POST gönderir.
- `json=new_book`: Python sözlüğünü JSON gövdesi olarak gönderir; istek `Content-Type` başlığını HTTPX hazırlar.
- `response.status_code == 201`: Bu işlemin oluşturma başarı kodunu kontrol eder.
- `response.headers.get("Location")`: Yeni kaynağın yanıt başlığındaki adresini okur.

Python sözlüğündeki `True` ve `None`, gönderilirken JSON'da `true` ve `null` olur. Elle `json.dumps` çağırmamıza gerek yoktur.

### Değişen satırlar

```diff
--- create_book.py
+++ create_book.py
@@ -0,0 +1,37 @@
+import httpx
+
+new_book = {
+    "title": "HTTP'yi Anlamak",
+    "author": {
+        "first_name": "Selin",
+        "last_name": "Aras"
+    },
+    "available": True,
+    "tags": ["http", "web"],
+    "rating": None
+}
+
+try:
+    response = httpx.post(
+        "http://127.0.0.1:8000/api/books",
+        json=new_book,
+        headers={"Accept": "application/json"}
+    )
+except httpx.ConnectError:
+    print("Connection failed: Could not connect to the server.")
+    print("Check that the server is running at http://127.0.0.1:8000.")
+else:
+    print("Request method:", response.request.method)
+    print("Request URL:", response.request.url)
+    print("Request Content-Type:", response.request.headers.get("Content-Type"))
+    print("Status code:", response.status_code)
+    print("Response Content-Type:", response.headers.get("Content-Type"))
+    print("Location:", response.headers.get("Location"))
+    print("Response body:", response.text)
+
+    if response.status_code == 201:
+        created_book = response.json()
+        print("Created book ID:", created_book["id"])
+        print("Created book title:", created_book["title"])
+    else:
+        print("Book could not be created. Read the status code and response body.")
```

### `create_book.py` dosyasının tamamı

```python
import httpx

new_book = {
    "title": "HTTP'yi Anlamak",
    "author": {
        "first_name": "Selin",
        "last_name": "Aras"
    },
    "available": True,
    "tags": ["http", "web"],
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
    print("Check that the server is running at http://127.0.0.1:8000.")
else:
    print("Request method:", response.request.method)
    print("Request URL:", response.request.url)
    print("Request Content-Type:", response.request.headers.get("Content-Type"))
    print("Status code:", response.status_code)
    print("Response Content-Type:", response.headers.get("Content-Type"))
    print("Location:", response.headers.get("Location"))
    print("Response body:", response.text)

    if response.status_code == 201:
        created_book = response.json()
        print("Created book ID:", created_book["id"])
        print("Created book title:", created_book["title"])
    else:
        print("Book could not be created. Read the status code and response body.")
```

### Çalıştır ve gözlemle

Dosyayı kaydet. İstemci terminalinde **bir kez** çalıştır:

```bash
python create_book.py
```

Beklenen temel satırlar:

```text
Request method: POST
Request URL: http://127.0.0.1:8000/api/books
Request Content-Type: application/json
Status code: 201
Response Content-Type: application/json
Location: /api/books/74
Created book ID: 74
Created book title: HTTP'yi Anlamak
```

Program ayrıca Response body satırını yazar. Postman GET sekmesinde `/api/books/74` ile aynı kitabı oku. Kataloğun artık dört kitabı olmalı.

Yalnızca istemciyi değiştirdik. Aynı POST yolu, aynı kitap verisi ve aynı sunucu işlevi kullanıldı. Programı yeniden çalıştırmak aynı kitabı ekranda yeniden göstermekle sınırlı kalmaz; **bir POST daha gönderir ve yeni kayıt ekler**.

**Kontrol sorusu:** `json=new_book` ile `response.json()` hangi yönlerde dönüşüm yapıyor?

<details><summary>Cevap</summary>

`json=new_book` gönderilecek Python verisini JSON'a dönüştürür. `response.json()` alınan JSON yanıtını Python verisine dönüştürür.

</details>

<a id="x14"></a>

## Deney 14 — Oluşturulan kitabı eski okuma istemcisiyle bul

**Ne yapıyoruz?** `client.py` dosyasında yalnızca arama metnini değiştiriyoruz.  
**Neden?** Oluşturma ve okumanın ayrı HTTP işlemleri olduğunu, aynı sunucu verisinde buluştuğunu görmek için.  
**Teorideki yeri:** [Bölüm 3 ve 11 — Filtreleme ve istemciler](01_Teorik_Ders_Notu.md#t11).

**Başlangıç:** Deney 13'te bir POST yapıldı; dört kitap var. **Sunucuyu yeniden başlatma.** `available=true` filtresi aynı kalacak. Yeni kitabın başlığında HTTP var ve uygunluğu true.

### Değişen satırlar

```diff
--- client.py
+++ client.py
@@ -4,7 +4,7 @@
     response = httpx.get(
         "http://127.0.0.1:8000/api/books",
         params={
-            "search": "Python",
+            "search": "HTTP",
             "available": "true"
         },
         headers={"Accept": "application/json"}
```

### `client.py` dosyasının tamamı

```python
import httpx

try:
    response = httpx.get(
        "http://127.0.0.1:8000/api/books",
        params={
            "search": "HTTP",
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

Kaydet; istemci terminalinde çalıştır:

```bash
python client.py
```

Beklenen temel çıktı:

```text
Request URL: http://127.0.0.1:8000/api/books?search=HTTP&available=true
Request Accept: application/json
Status code: 200
Response Content-Type: application/json
Book count: 1

Book title: HTTP'yi Anlamak
Book author: Selin Aras
Availability: Available to borrow
Tags:
- http
- web
Rating: Not rated yet
```

Program Response body satırını da yazar. HTTP isteğinin yanıt gövdesinde `rating: null`, ekrandaysa `Rating: Not rated yet` görürüz. İstemci verinin anlamını kullanıcıya sunar; sunucudaki kaydı değiştirmez.

**Kontrol sorusu:** İstemciyi yeniden çalıştırınca kitap sayısı ikiye çıkar mı?

<details><summary>Cevap</summary>

Hayır. Bu dosya GET gönderir; kitap eklemez. `create_book.py` dosyası ise POST gönderir. Hangi dosyayı çalıştırdığımıza dikkat etmeliyiz.

</details>

<a id="x15"></a>

## Deney 15 — Sunucuyu yeniden başlatınca ne kalıyor?

**Ne yapıyoruz?** Çalışan sunucuyu kapatıp açıyor, aynı okuma isteğini tekrar gönderiyoruz.  
**Neden?** HTTP işleminin başarısı ile verinin kalıcı saklanmasının ayrı konular olduğunu görmek için.  
**Teorideki yeri:** [Bölüm 11 — Verinin ömrü](01_Teorik_Ders_Notu.md#t11).

**Başlangıç:** Dört kitap; son `client.py` HTTP başlığını arıyor. Kod değişmiyor.

1. Sunucu terminalinde Ctrl+C yap; kapanışın bitmesini bekle.
2. İstemci terminalinde `python client.py` çalıştır. Bağlantı kurulamadığını belirten iki satır beklenir. **Bu sonuç bir 404 değildir; HTTP yanıtı alınamadı.**
3. Sunucu terminalinde yeniden başlat:

```bash
python -m uvicorn server:app
```

4. Çalıştığını belirten satırı görünce istemci terminalinde `python client.py` çalıştır.

Bu kez `200`, `Response body: []`, `Book count: 0` ve `No books matched your search.` beklenir. Sunucu var; fakat yeni eklediğimiz kitap bellekteydi ve yeniden başlatınca kayboldu.

5. Postman'da parametresiz `GET http://127.0.0.1:8000/api/books` gönder: dosyadaki üç başlangıç kitabı yerindedir.
6. `GET http://127.0.0.1:8000/api/books/74` gönder: `404 Book not found` beklenir.

**Kontrol sorusu:** Daha önce alınan `201` yanlış mıydı?

<details><summary>Cevap</summary>

Hayır. O anda kitap oluşturulmuş ve GET ile okunmuştu. `201`, sunucunun daha sonra yeniden başlatılmasına karşı kalıcılık sözü değildir. Bu uygulama henüz dosya veya veritabanına kayıt yazmıyor.

</details>

## Deneylerin durum çizelgesi

Beklenen kimlik ve sayılar için bu çizelgeyi kullan. Fazladan başarılı POST gönderdiysen sayı artar; başarısız istekler ve GET istekleri yeni kitap eklemez.

| Nokta | Kitap sayısı | Sonradan oluşan kimlikler |
|---|---|---|
| Hazırlık ve Deney 1–6 | 3 | Yok |
| Deney 7 sonunda | 4 | 74 |
| Deney 8 başında yeniden başlatma | 3 | Yok |
| Deney 8 sonunda | 4 | 74 |
| Deney 9 sonunda | 5 | 74, 75 |
| Deney 10–12 sonunda | 5 | 74, 75 |
| Deney 13 başında yeniden başlatma | 3 | Yok |
| Deney 13–14 sonunda | 4 | 74 |
| Deney 15 sonunda | 3 | Yok |

## Takıldığında sonucu açıklayarak ilerle

| Gözlem | Önce kontrol et | Açıklama / yapılacak işlem |
|---|---|---|
| Bağlantı kurulamıyor | Sunucu terminalinde Uvicorn çalışıyor mu? URL ve port doğru mu? | Sunucuyu çalıştır; yalnızca istemciyi açmak yeterli değildir. |
| `address already in use` | Aynı portta eski sunucu var mı? | Çalışan sunucunun terminalinde Ctrl+C kullan. Gerekirse `ss -ltnp 'sport = :8000'` ile süreci belirle; rastgele süreç kapatma. |
| POST eklediğim hâlde `405` | Doğru `server.py` kaydedildi ve doğru klasördeki sunucu yeniden başladı mı? | Eski süreç eski kodu çalıştırıyor olabilir. |
| Beklediğimden çok kitap var | Kaç başarılı POST gönderdim? | Send ve `python create_book.py` her çalıştırmada yeni POST yapar. Durum çizelgesine dön. |
| Yeni kimlik 74 değil | Önceden kitap ekledim mi? | Dönen `id` ve `Location` değerini kullan; adresi tahmin etme. Kesin deney sonucu için belirtilen başlangıcı kur. |
| GET sonucu boş | Params'ta eski filtre kaldı mı? Sunucu yeniden mi başladı? | Önce parametresiz listeyi oku. Nedenini anlamadan yeniden POST gönderme. |
| `422` | Body raw/JSON mu? İstek Content-Type doğru mu? Hata `loc` ve `type` ne diyor? | Hatalı alanı veya JSON yazımını belirle; kod tek başına nedeni anlatmaz. |
| Postman ve Python farklı kitap döndürüyor | Metot, URL, etkin Params, gövde ve sunucunun verisi aynı mı? | Önce istekleri ve başlangıç durumunu aynı yap. Görünüm farkı veri farkı olmayabilir. |
| Puan `0.0` görünüyor | Puan tipi modelde `float` mı? | Sayı dönüştürülmüş olabilir; `null` olmuş demek değildir. |
| POST sırasında zaman aşımı / beklenmeyen bağlantı kesilmesi | Sunucunun kitap listesi ve kayıtları ne durumda? | Yanıt alınamaması işlemin kesin yapılmadığını kanıtlamaz. Kontrol etmeden tekrar POST gönderme. |

Bu istemciler bağlantı kurma hatasını yakalar. Her tür ağ ve JSON hatasını kapsayan üretim istemcisi henüz yazmadık; kapsamlı hata yönetimini ileride genişleteceğiz.

## Haftalık değerlendirme — İsteği, sonucu ve gerekçeyi birlikte anlat

1. Postman'dan yeni bir kitap oluşturulmasını, metot, URL, başlıklar ve gövde üzerinden anlat.
2. Sonuç `201` geldiğinde yeni kaydı nereden okuyacağını ve okumanın beklenen kodunu söyle.
3. Bir alan eksik olduğu için `422` aldığında kayıt sayısının neden artmadığını açıkla.
4. GET ile boş liste almak, tek kitap için `404` almak ve hiç bağlantı kuramamak arasındaki farkı anlat.
5. Aynı isteği tekrar göndermeden önce bunun GET mi POST mu olduğunu neden önemseriz?
6. POST'u bir kez gönderip farklı istemciden okuduğun kitabın yeniden başlatmadan sonra kaybolmasını açıkla.

<details>
<summary>Değerlendirmede aranacak noktalar</summary>

1. POST `/api/books`, istek `Content-Type: application/json`, yanıt tercihi `Accept: application/json`, model alanlarını taşıyan JSON gövdesi. Postman bu mesajı hazırlayan istemcidir.
2. `Location` başlığındaki yolu sunucu adresiyle birleştirip GET göndeririz. Başarılı okumada `200` ve kitap nesnesi bekleriz.
3. FastAPI girdiyi doğrularken isteği reddeder; oluşturma fonksiyonundaki listeye ekleme satırı çalışmaz.
4. Boş liste `200` ile başarılı bir arama sonucu olabilir. `404` istenen tek kaynağın bulunamadığı HTTP yanıtıdır. Bağlantı hatasında HTTP yanıtı ve durum kodu alınmamıştır.
5. GET okumayı tekrarlar; bizim POST'umuz her seferinde yeni kayıt oluşturur. Yanıt kodunun aynı olması etkisinin aynı olduğunu göstermez.
6. İki istemci aynı sunucu verisini kullanmıştır. Veri yalnızca bellekte tutulmuş, yeniden başlatmada kaynak dosyadaki başlangıç listesi yüklenmiştir.

</details>

### Haftanın sonunda dosyalar

| Dosya | Son sürümü | Görevi |
|---|---|---|
| `server.py` | [Deney 8](#x08) | İki GET ve bir POST işlemi; üç başlangıç kitabı; bellekte ekleme; Location. |
| `create_book.py` | [Deney 13](#x13) | Bir yeni kitap oluşturma isteği göndermek. |
| `client.py` | [Deney 14](#x14) | Başlığında HTTP geçen, uygun kitapları okumak. |

Deney 15 sonunda sunucu çalışır ve üç başlangıç kitabı vardır; bu nedenle son okuma istemcisinin boş liste alması beklenir. Bu durum tamamlanmamış kurulum değildir.

### Sonraki haftalara bağlantı

Üçüncü haftada bu deneyden hareketle kaynakları ve uç noktaları tasarlayacağız. Dördüncü haftada güncelleme ve silmeyi uygulayacağız; PUT/PATCH/DELETE adlarını seçip `405` görmek onların işlevlerini öğrenmek için yeterli değildir. Beşinci haftada modelleri iş kurallarıyla, altıncı haftada saklamayı veritabanıyla genişleteceğiz.

**Geri dön:** [İkinci hafta teorisi](01_Teorik_Ders_Notu.md) · [Birinci hafta uygulaması](../Hafta_01/02_Uygulama_Foyu.md) · [Haftalık plan](../../00_Planlama/01_Haftalik_Ders_Plani.md)

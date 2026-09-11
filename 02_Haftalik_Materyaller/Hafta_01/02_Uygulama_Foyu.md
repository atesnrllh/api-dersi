# Hafta 01 — Uygulama Föyü

## Çalışan İlk Kitap Kataloğu API'si: Sunucu, İstemci, HTTP ve JSON

**Ders:** Uygulama Programı Arayüzü (API)

**Düzey:** API konusunda başlangıç

**Ana araçlar:** VS Code, Python 3.10+, FastAPI, Uvicorn, HTTPX ve uv

**Sürüm:** 2.0 — 11 Eylül 2026

> Bu föy yalnızca çalışacak kodu vermez. Her deneyde önce **neyi ve neden yaptığımızı**, sonra teorideki karşılığını, değişen satırları, dosyanın tam hâlini, beklenen gözlemi ve çıkarılacak sonucu gösterir. Kodu bir defada kopyalayıp geçmek yerine her deneyin sorusunu cevaplayarak ilerle.

> **Kod renkleri:** “Değişen satırlar” başlıklı `diff` kutularında silinen satırlar `-`, eklenen satırlar `+` ile gösterilir. GitHub ve destekleyen editörler bunları genellikle kırmızı ve yeşil renklendirir. Hemen altındaki Python kutusu ise değişiklikten sonra dosyada bulunması gereken kodun tamamıdır.

## 1. Uygulamanın amacı ve kapsamı

Bu çalışmada hem API sunucusunu hem istemci programını kendimiz yazacağız. İki program aynı bilgisayarda çalışacak, fakat farklı roller üstlenecek:

```text
client.py  ── HTTP isteği ──►  server.py
client.py  ◄─ HTTP yanıtı ───  server.py
```

Çalışmanın sonunda şunları yapabilmelisin:

- VS Code'da proje klasörü, dosya ve terminal düzenini kurmak.
- Projeye özel Python sanal ortamı oluşturup paketleri bu ortama kurmak.
- FastAPI ile GET isteği karşılayan küçük bir sunucu yazmak.
- HTTPX ile bu sunucuya istek gönderen istemci yazmak.
- Yol parametresiyle tek kitap, koleksiyon yolu ile kitap listesi istemek.
- `200`, `404`, `422` ve bağlantı hatasını birbirinden ayırmak.
- JSON nesnesi, dizisi, metni, sayısı, mantıksal değeri ve `null` değerini uygulamada okumak.
- Sorgu parametreleriyle başlık araması ve ödünç alınabilirlik filtresi yapmak.
- `Accept` ile `Content-Type` başlıklarının farklı görevlerini açıklamak.
- Geçersiz JSON, yanlış veri türü ve iş kuralına aykırı değeri ayırmak.
- REST, SOAP ve GraphQL'in aynı ihtiyacı nasıl farklı ifade ettiğini giriş düzeyinde görmek.

### 1.1. Teori ile uygulamadaki adların eşleştirilmesi

Teori notu Türkçe alan adları kullanır. Kodda ise yaygın geliştirme alışkanlığına uymak için İngilizce adlar kullanıyoruz. Kavramlar aynıdır:

| Teori notu | Uygulama kodu | Anlamı |
|---|---|---|
| `kitaplar` | `books` | Kitap koleksiyonu |
| `kitap_id` | `book_id` | Kitap kimliği |
| `ad` | `title` | Kitap başlığı |
| `yazar` | `author` | Yazar bilgisi |
| `odunc_alinabilir` | `available` | Ödünç alınabilirlik |
| `etiketler` | `tags` | Etiket dizisi |
| `puan` | `rating` | Kitap puanı |
| `/api/kitaplar` | `/api/books` | Kitap koleksiyonunun yolu |

### 1.2. Çalışma süresi

İlk defa VS Code ve Python ortamı kuran bir öğrenci için föyün tamamı 90 dakikadan uzun sürebilir. Sınıftaki iki ders saatinde en azından 2–9. bölümler tamamlanmalıdır. JSON ayrıntıları, filtreleme, hata deneyleri ve değerlendirme aynı hafta içindeki yönlendirilmiş çalışma olarak sürdürülebilir. Hız için öğrenme adımları atlanmamalıdır.

## 2. VS Code'da başlangıç düzenini kur

### 2.1. Ne yapıyoruz, neden yapıyoruz?

Kodlarımızı ve Python ortamımızı tek bir proje klasöründe düzenliyoruz. VS Code'da doğru klasörü açmak, terminal komutlarının ve dosya yollarının aynı proje üzerinde çalışmasını sağlar.

**Teorideki karşılığı:** API tek bir ekran değildir; arkasında çalışan istemci ve sunucu kodları vardır. Bu bölüm o kodların çalışma ortamını hazırlar.

### 2.2. Proje klasörünü aç

1. Masaüstünde `book-catalog-api` adlı klasör oluştur.
2. VS Code'da **File → Open Folder** ile bu klasörü aç.
3. **Terminal → New Terminal** ile terminal aç.
4. Linux veya WSL terminalinde bulunduğun yeri kontrol et:

```bash
pwd
```

Örnek sonuç:

```text
/home/nuri/Desktop/book-catalog-api
```

Windows klasörünü WSL üzerinden açtıysan yol `/mnt/c/Users/.../book-catalog-api` biçiminde de olabilir. Önemli olan son bölümün proje klasörünü göstermesidir.

Klasörü daha önce `API` adıyla oluşturduysan yeniden oluşturman gerekmez; terminaldeki yolun o klasörü göstermesi yeterlidir. Projeye özel `book-catalog-api` adı, klasörün ne içerdiğini daha açık anlatır.

VS Code'un solundaki **Explorer** bölümünde **New File** düğmesini kullanarak `server.py` ve `client.py` dosyalarını oluştur. Kodu değiştirdikten sonra **Ctrl+S** ile dosyayı kaydet; terminal, diske kaydedilmiş sürümü çalıştırır.

### 2.3. Python'u kontrol et

```bash
python3 --version
```

Bu föydeki `bool | None` tür gösterimi için Python 3.10 veya daha yeni bir sürüm kullan.

### 2.4. Sanal ortamı oluştur

```bash
python3 -m venv api-env
```

Sanal ortam, bu projenin Python paketlerini diğer projelerden ayırır. Ayrı bir bilgisayar veya sanal makine değildir; proje için Python çalıştırıcısı ve paket klasörleri sağlar.

Oluşacak düzen:

```text
book-catalog-api/
├── api-env/      ← sanal ortam; uygulama kodunu buraya yazma
├── server.py     ← birazdan oluşturulacak
└── client.py     ← birazdan oluşturulacak
```

Ortamı etkinleştir:

```bash
source api-env/bin/activate
```

Terminal satırının başında `(api-env)` görünmelidir. Sunucu ve istemci aynı projenin parçaları olduğu için aynı ortamı kullanabilir.

### 2.5. uv aracını kur ve doğrula

Önce kontrol et:

```bash
uv --version
```

Komut bulunamazsa Linux veya WSL üzerinde uv'nin resmî kurucusunu çalıştır:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Mevcut terminal uv'yi bulamazsa:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Ardından yeniden kontrol et:

```bash
uv --version
```

> Bazı kurulum çıktıları `source "$HOME/.local/bin/env"` önerebilir. Bu dosya sisteminde yoksa yukarıdaki `export PATH=...` komutunu kullan. Bu komut yalnızca açık terminalin komut arama yolunu günceller.

### 2.6. Paketleri proje ortamına kur

```bash
uv pip install --python api-env/bin/python fastapi uvicorn httpx
```

| Paket | Bu uygulamadaki görevi |
|---|---|
| FastAPI | Hangi HTTP isteğine hangi Python fonksiyonunun cevap vereceğini tanımlar. |
| Uvicorn | FastAPI uygulamasını çalıştırır ve bağlantıları dinler. |
| HTTPX | `client.py` içinden HTTP isteği gönderir ve yanıtı okur. |

`Failed to hardlink files; falling back to full copy` uyarısı görülürse kurulum başarısız olmuş sayılmaz. Önbellek ve proje farklı dosya sistemlerindeyse uv dosyaları kopyalayarak devam edebilir.

### 2.7. İki terminal kullan

- **Sunucu terminali:** Uvicorn çalışır ve istek bekler. Bu terminal komut satırına dönmeden açık kalır.
- **İstemci terminali:** `client.py` çalıştırılır ve yeni istekler gönderilir.

Yeni terminal açıldığında sanal ortamı yeniden etkinleştir:

```bash
source api-env/bin/activate
```

Python dosyalarını klasik anlamda ayrıca derlemeyeceğiz. Python yorumlayıcısıyla çalıştıracağız.

VS Code'un terminal listesinde sunucu terminalinin adı çalışırken `python`, istemci terminalinin adı ise `bash` görünebilir. İki terminal de Bash veya WSL kabuğuyla açılmıştır. Uvicorn önde çalışmaya devam ettiği için ilk terminal o anki işlemin adını gösterir; `client.py` bitip komut satırına döndüğü için ikinci terminal yeniden kabuğun adını gösterir.

## 3. Deney 1 — İlk API sunucusunu yaz

### Ne yapıyoruz?

Sunucunun belleğinde bir kitap sözlüğü tutuyor ve yalnızca `/api/books/42` adresindeki GET isteğine cevap veren bir işlem tanımlıyoruz.

### Neden yapıyoruz?

API tanımındaki **işlem, girdi ve sonuç** kavramlarını çalışan bir programda görmek istiyoruz. İlk örneği küçük tutarak istemci–sunucu iletişimine odaklanıyoruz.

### Teorideki yeri

- Bölüm 3: API tam olarak nedir?
- Bölüm 4: API, uygulama ve veritabanı ayrımı
- Bölüm 5–7: İstemci, sunucu, istek, yanıt ve uç nokta

Bu aşamada veritabanı yoktur. Kitap bilgisi `server.py` içindeki Python sözlüğünde tutulur. Sunucu yeniden başladığında veri koddan yeniden yüklenir.

### Yeni dosya — değişen satırlar

```diff
+ from fastapi import FastAPI
+
+ app = FastAPI()
+
+ book = {
+     "id": 42,
+     "title": "API Yolculuğu",
+     "author": "Deniz Kaya"
+ }
+
+
+ @app.get("/api/books/42")
+ def get_book():
+     return book
```

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI

app = FastAPI()

book = {
    "id": 42,
    "title": "API Yolculuğu",
    "author": "Deniz Kaya"
}


@app.get("/api/books/42")
def get_book():
    return book
```

### Sunucuyu çalıştır

```bash
python -m uvicorn server:app
```

Komuttaki `server`, `server.py` dosyasını; `app`, dosyadaki FastAPI uygulama nesnesini belirtir.

Beklenen mesaj:

```text
Uvicorn running on http://127.0.0.1:8000
```

- `127.0.0.1`: İstemcinin çalıştığı ortamın kendisini gösteren yerel adres.
- `8000`: Sunucunun bağlantı beklediği port.

### Deneyin sonucu

API ayrı bir makine değildir. Bu örnekte `server.py` içindeki FastAPI uygulamasının dışarı sunduğu işlem ve kullanım kuralıdır. Uvicorn bu uygulamayı çalıştırır.

## 4. Deney 2 — İlk istemciyi yaz

### Ne yapıyoruz?

İkinci Python programından sunucuya GET isteği gönderiyor ve dönen JSON içindeki kitap başlığını gösteriyoruz.

### Neden yapıyoruz?

API'yi başka bir yazılımın kullandığını görmek istiyoruz. İnsan `client.py` programını çalıştırır; HTTP isteğini oluşturan taraf istemci yazılımıdır.

### Teorideki yeri

- Bölüm 3.2: Kullanıcı arayüzü ile API ayrımı
- Bölüm 5: İstemci–sunucu rolleri
- Bölüm 6: İsteğin yolculuğu
- Bölüm 12.6: JSON ayrıştırma

### Yeni dosya — değişen satırlar

```diff
+ import httpx
+
+ response = httpx.get("http://127.0.0.1:8000/api/books/42")
+ book = response.json()
+ print(book["title"])
```

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books/42")
book = response.json()
print(book["title"])
```

Sunucu terminalini açık bırak. İkinci terminalde:

```bash
source api-env/bin/activate
python client.py
```

Beklenen çıktı:

```text
API Yolculuğu
```

### Deneyin sonucu

`server.py` üç alan gönderdi; `client.py` yalnızca `title` alanını gösterdi. Sunucu veriyi üretir, istemci aldığı veriyi nasıl kullanacağına karar verir.

## 5. Deney 3 — HTTP yanıtını görünür hâle getir

### Ne yapıyoruz?

İstemcide durum kodunu, ham yanıt gövdesini ve seçilen alanları ayrı ayrı gösteriyoruz.

### Neden yapıyoruz?

Bir HTTP yanıtının yalnızca kitap verisinden oluşmadığını görmek istiyoruz. İşlemin sonucunu belirten durum kodu ile gövde farklı bilgilerdir.

### Teorideki yeri

- Bölüm 7.3: Durum satırı, başlık ve gövde
- Bölüm 10–11: JSON'u okuma

### Değişen satırlar

```diff
  response = httpx.get("http://127.0.0.1:8000/api/books/42")
+ print("Status code:", response.status_code)
+ print("Response body:", response.text)
  book = response.json()
- print(book["title"])
+ print("Book title:", book["title"])
+ print("Book author:", book["author"])
```

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books/42")

print("Status code:", response.status_code)
print("Response body:", response.text)

book = response.json()

print("Book title:", book["title"])
print("Book author:", book["author"])
```

Beklenen temel çıktı:

```text
Status code: 200
Response body: {"id":42,"title":"API Yolculuğu","author":"Deniz Kaya"}
Book title: API Yolculuğu
Book author: Deniz Kaya
```

### Deneyin sonucu

`200` isteğin başarıyla karşılandığını, JSON gövdesi ise kaynağın temsilini gösterir. `response.json()` bu JSON'u istemcinin kullanacağı Python sözlüğüne dönüştürür.

## 6. Deney 4 — JSON gelmesi başarı demek midir?

### Ne yapıyoruz?

Henüz tanımlamadığımız `/api/books/99` adresini istiyoruz. Sonra istemcinin her JSON yanıtını kitap sanmasının neden hata olduğunu gözlemliyoruz.

### Neden yapıyoruz?

Başarısız bir işlemde de JSON gövdesi gelebileceğini ve istemcinin durum koduna bakması gerektiğini göstermek istiyoruz.

### Teorideki yeri

- Bölüm 5.4: Yanıt ile bağlantı sorununu ayırma
- Bölüm 7.4: `404 Not Found`
- Bölüm 14: “JSON geldiyse işlem başarılıdır” yanılgısı

### Değişen satırlar

```diff
- response = httpx.get("http://127.0.0.1:8000/api/books/42")
+ response = httpx.get("http://127.0.0.1:8000/api/books/99")
```

### `client.py` dosyasının tamamı — hatayı gözlemleme sürümü

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books/99")

print("Status code:", response.status_code)
print("Response body:", response.text)

book = response.json()

print("Book title:", book["title"])
print("Book author:", book["author"])
```

Beklenen sonuç:

```text
Status code: 404
Response body: {"detail":"Not Found"}
KeyError: 'title'
```

Sunucu JSON göndermiştir, fakat JSON'da `title` alanı yoktur. `KeyError` sunucuda değil, hata yanıtını kitap sanan istemci kodunda oluşur.

### İstemciyi durum koduna göre düzelt

```diff
  print("Response body:", response.text)
- book = response.json()
- print("Book title:", book["title"])
- print("Book author:", book["author"])
+ if response.status_code == 200:
+     book = response.json()
+     print("Book title:", book["title"])
+     print("Book author:", book["author"])
+ else:
+     print("Book information could not be retrieved.")
```

### `client.py` dosyasının tamamı — kontrollü sürüm

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books/99")

print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    book = response.json()
    print("Book title:", book["title"])
    print("Book author:", book["author"])
else:
    print("Book information could not be retrieved.")
```

### Deneyin sonucu

`404`, sunucunun hiç cevap vermediğini göstermez. Sunucu bir HTTP hata yanıtı vermiştir. İstemci başarılı kitap yanıtıyla hata yanıtını farklı işlemelidir.

## 7. Deney 5 — Yol parametresiyle farklı kitap kimliklerini karşıla

### Ne yapıyoruz?

Sabit `/api/books/42` yolunu `/api/books/{book_id}` biçimine getiriyoruz. Aynı fonksiyon farklı kitap kimliklerini alabilecek.

### Neden yapıyoruz?

Her kitap için ayrı fonksiyon yazmak yerine, istemcinin istediği kaynak kimliğini adres üzerinden sunucuya iletmesini istiyoruz.

### Teorideki yeri

- Bölüm 3.4: API sözleşmesindeki girdi
- Bölüm 7.1: Kaynak ve uç nokta
- Bölüm 13: Kitap kimliğinin yolda taşınması

### Değişen satırlar

```diff
- from fastapi import FastAPI
+ from fastapi import FastAPI, HTTPException
...
- @app.get("/api/books/42")
- def get_book():
-     return book
+ @app.get("/api/books/{book_id}")
+ def get_book(book_id: int):
+     if book_id == book["id"]:
+         return book
+
+     raise HTTPException(status_code=404, detail="Book not found")
```

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

book = {
    "id": 42,
    "title": "API Yolculuğu",
    "author": "Deniz Kaya"
}


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    if book_id == book["id"]:
        return book

    raise HTTPException(status_code=404, detail="Book not found")
```

Sunucuyu değiştirdiğimiz için sunucu terminalinde **Ctrl+C** ile kapat ve yeniden çalıştır:

```bash
python -m uvicorn server:app
```

`/api/books/99` artık tanımlı yol kalıbıyla eşleşir; fonksiyon çalışır ve kitabı bulamadığı için bilinçli olarak şu gövdeyi döndürür:

```json
{"detail": "Book not found"}
```

`/api/books/42` isteğinde ise `book_id` değeri `42` olur ve kitap `200` ile döner.

### Deneyin sonucu

`404` bu kodda beklenmedik sunucu arızası değildir. Kitabın bulunamayacağı olasılığı API davranışında açıkça tanımlanmıştır.

## 8. Deney 6 — Bir kitap koleksiyonu oluştur

### Ne yapıyoruz?

Tek sözlük yerine kitap sözlüklerinden oluşan liste tutuyoruz. Bütün kitapları ve kimliği verilen tek kitabı sunan iki işlem oluşturuyoruz.

### Neden yapıyoruz?

Tek kaynak yanıtıyla koleksiyon yanıtının farklı JSON yapılarına sahip olduğunu görmek istiyoruz.

### Teorideki yeri

- Bölüm 7: `/api/kitaplar` ve `/api/kitaplar/42`
- Bölüm 11.4: Tek nesne ile listenin farkı

### Değişen satırlar

```diff
- book = { ... }
+ books = [
+     {"id": 42, ...},
+     {"id": 57, ...}
+ ]
+
+ @app.get("/api/books")
+ def get_books():
+     return books
...
+     for book in books:
+         if book["id"] == book_id:
+             return book
```

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": "Deniz Kaya"
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": "Ece Yılmaz"
    }
]


@app.get("/api/books")
def get_books():
    return books


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

Sunucuyu yeniden başlat. İstemcinin adresini `/api/books` olarak değiştir ve gelen listeyi döngüyle işle.

### Değişen satırlar

```diff
- response = httpx.get("http://127.0.0.1:8000/api/books/99")
+ response = httpx.get("http://127.0.0.1:8000/api/books")
...
-     book = response.json()
-     print("Book title:", book["title"])
+     books = response.json()
+     print("Book count:", len(books))
+     for book in books:
+         print("Book title:", book["title"])
+         print("Book author:", book["author"])
```

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books")

print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

    for book in books:
        print("Book title:", book["title"])
        print("Book author:", book["author"])
        print()
else:
    print("Book information could not be retrieved.")
```

### Gözlem ve sonuç

| İstek | JSON gövdesi | Python karşılığı |
|---|---|---|
| `GET /api/books/57` | `{...}` | Sözlük |
| `GET /api/books` | `[{...}, {...}]` | Sözlüklerden oluşan liste |

Sunucu listeyi gönderir; `len(books)` ile kitap sayısını istemci hesaplar.

## 9. Deney 7 — JSON türlerini çalışan API'de gör

### Ne yapıyoruz, neden yapıyoruz?

Kitap temsilini adım adım genişletip mantıksal değer, dizi, `null`, sayı ve iç içe nesneyi hem sunucuda üretiyor hem istemcide anlamına göre işliyoruz. Böylece JSON türlerinin yalnızca yazım biçimi olmadığını, istemcinin davranışını etkilediğini görüyoruz.

### Teorideki yeri

- Bölüm 10–12: JSON kuralları, veri türleri, iç içe yapılar ve ayrıştırma
- Bölüm 14: `false`, `null` ve `0` değerlerini ayırma

### 9.1. Mantıksal değer: `available`

**Amaç:** Sunucunun yalnızca metin göndermediğini, istemcinin mantıksal değere göre farklı davranabildiğini görmek.

Python'daki `True` ve `False`, FastAPI tarafından JSON'daki `true` ve `false` değerlerine dönüştürülür.

#### Değişen satırlar

```diff
      "author": "Deniz Kaya",
+     "available": True
...
      "author": "Ece Yılmaz",
+     "available": False
```

#### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": "Deniz Kaya",
        "available": True
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": "Ece Yılmaz",
        "available": False
    }
]


@app.get("/api/books")
def get_books():
    return books


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

Sunucuyu yeniden başlat. Ardından istemciye görünüm kuralını ekle.

#### Değişen satırlar

```diff
          print("Book author:", book["author"])
+
+         if book["available"]:
+             print("Availability: Available to borrow")
+         else:
+             print("Availability: Not available to borrow")
```

#### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books")

print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

    for book in books:
        print("Book title:", book["title"])
        print("Book author:", book["author"])

        if book["available"]:
            print("Availability: Available to borrow")
        else:
            print("Availability: Not available to borrow")

        print()
else:
    print("Book information could not be retrieved.")
```

**Sonuç:** `false`, alanın eksik olduğunu söylemez. “Ödünç alınamaz” şeklinde anlamlı bir cevaptır.

### 9.2. Dizi ve boş dizi: `tags`

**Amaç:** Tek kitap nesnesinin içinde birden fazla değerin diziyle taşınmasını ve `[]` değerinin hata olmadığını görmek.

#### Değişen satırlar

```diff
      "available": True,
+     "tags": ["software", "education"]
...
      "available": False,
+     "tags": []
```

#### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": "Deniz Kaya",
        "available": True,
        "tags": ["software", "education"]
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": "Ece Yılmaz",
        "available": False,
        "tags": []
    }
]


@app.get("/api/books")
def get_books():
    return books


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

#### Değişen satırlar

```diff
          else:
              print("Availability: Not available to borrow")
+
+         if book["tags"]:
+             print("Tags:")
+             for tag in book["tags"]:
+                 print("-", tag)
+         else:
+             print("Tags: No tags")
```

#### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books")

print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

    for book in books:
        print("Book title:", book["title"])
        print("Book author:", book["author"])

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

        print()
else:
    print("Book information could not be retrieved.")
```

**Sonuç:** `tags: []`, etiket alanının bulunduğunu fakat dizide sıfır eleman olduğunu anlatır. Bu durum tek başına HTTP hatası değildir.

### 9.3. `null` ile `0`: `rating`

**Amaç:** “Henüz puan verilmemiş” ile “puanı sıfır” bilgisini ayırmak.

Bizim API sözleşmemizde `None` henüz puan verilmediğini, `0` ise verilmiş sayısal puanı anlatır. FastAPI, Python `None` değerini JSON `null` değerine dönüştürür.

#### Değişen satırlar

```diff
      "tags": ["software", "education"],
+     "rating": None
...
      "tags": [],
+     "rating": 0
```

#### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": "Deniz Kaya",
        "available": True,
        "tags": ["software", "education"],
        "rating": None
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": "Ece Yılmaz",
        "available": False,
        "tags": [],
        "rating": 0
    }
]


@app.get("/api/books")
def get_books():
    return books


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

#### Değişen satırlar

```diff
          else:
              print("Tags: No tags")
+
+         if book["rating"] is None:
+             print("Rating: Not rated yet")
+         else:
+             print("Rating:", book["rating"])
```

#### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books")

print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

    for book in books:
        print("Book title:", book["title"])
        print("Book author:", book["author"])

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

`if not book["rating"]` kullanılsaydı hem `None` hem `0` yanlış kabul edilirdi. `is None` yalnızca `null` karşılığını ayırır. Bu kontrol genel bir istemci koruması değildir; alan eksikse, tür yanlışsa veya JSON bozuksa ayrıca kontrol gerekir.

### 9.4. İç içe nesne: `author`

**Amaç:** Bir alanın değerinin kendi alanları bulunan başka bir nesne olabileceğini görmek.

`author` alanını metinden nesneye çevirmek API yanıt sözleşmesini değiştirir. Eski yapıyı bekleyen istemciyi de güncellememiz gerekir.

#### Değişen satırlar

```diff
-     "author": "Deniz Kaya",
+     "author": {
+         "first_name": "Deniz",
+         "last_name": "Kaya"
+     },
...
-     "author": "Ece Yılmaz",
+     "author": {
+         "first_name": "Ece",
+         "last_name": "Yılmaz"
+     },
```

#### `server.py` dosyasının tamamı

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
    }
]


@app.get("/api/books")
def get_books():
    return books


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

#### Değişen satırlar

```diff
-         print("Book author:", book["author"])
+         print(
+             "Book author:",
+             book["author"]["first_name"],
+             book["author"]["last_name"]
+         )
```

#### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books")

print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

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

`book["author"]` yazar sözlüğünün tamamını; `book["author"]["last_name"]` yalnızca soyadını verir. Sunucudaki yapı değişse bile istemci ad ve soyadı birleştirerek kullanıcıya aynı görünümü sunabilir.

## 10. Deney 8 — Başlıkta arama yapmak için sorgu parametresi kullan

### Ne yapıyoruz?

İstemci `/api/books?search=API` isteğini gönderiyor. Sunucu `search` değerini kitapların yalnızca `title` alanında arıyor.

### Neden yapıyoruz?

İstemcinin istediği sonucu sorgu parametresiyle daraltabildiğini ve parametrenin anlamını sunucu sözleşmesinin belirlediğini görmek istiyoruz.

### Teorideki yeri

- Bölüm 7.1: URL'nin sorgu bileşeni
- Bölüm 13.2–13.3: Arama parametresini okuma ve sonuç üretme

### Sunucudaki değişen satırlar

```diff
  @app.get("/api/books")
- def get_books():
-     return books
+ def get_books(search: str = ""):
+     results = []
+     for book in books:
+         if search.casefold() in book["title"].casefold():
+             results.append(book)
+     return results
```

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": {"first_name": "Deniz", "last_name": "Kaya"},
        "available": True,
        "tags": ["software", "education"],
        "rating": None
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": {"first_name": "Ece", "last_name": "Yılmaz"},
        "available": False,
        "tags": [],
        "rating": 0
    }
]


@app.get("/api/books")
def get_books(search: str = ""):
    results = []

    for book in books:
        if search.casefold() in book["title"].casefold():
            results.append(book)

    return results


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

### İstemcideki değişen satırlar

```diff
- response = httpx.get("http://127.0.0.1:8000/api/books")
+ response = httpx.get(
+     "http://127.0.0.1:8000/api/books",
+     params={"search": "API"}
+ )
+ print("Request URL:", response.request.url)
```

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get(
    "http://127.0.0.1:8000/api/books",
    params={"search": "API"}
)

print("Request URL:", response.request.url)
print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

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

### Gözlem ve tartışma

- `search=API`, yalnızca `title` alanında aranır. Etikette `python` bulunması, başlık eşleşmiyorsa bu kodda sonuç üretmez.
- `search` HTTP veya FastAPI'nin özel kelimesi değildir; adını ve anlamını biz seçtik.
- `casefold()` sayesinde `API` ile `api` büyük ölçüde aynı arama sonucunu verir.
- Boş metin `""` sıfır karakter içerir ve Python'da her metnin içinde bulunur. Bu nedenle parametre verilmezse bütün kitaplar döner.
- Bir boşluk içeren `" "` ise boş metin değildir; yalnızca başlığında boşluk bulunan kitaplarla eşleşebilir.

## 11. Deney 9 — Başarılı boş sonuç ile 404'ü ayır

### Ne yapıyoruz?

`search=astronomy` ile eşleşmeyen bir arama yapıyor ve istemcide boş listeyi açıklıyoruz.

### Neden yapıyoruz?

Koleksiyonda sıfır eşleşmenin, belirli bir kitabın bulunamamasından farklı olduğunu görmek istiyoruz.

### Teorideki yeri

- Bölüm 7.4: Başarılı yanıt ile bulunamayan kaynak ayrımı
- Bölüm 11.4: Boş dizi ile boş nesne ayrımı

### Değişen satırlar

```diff
-     params={"search": "API"}
+     params={"search": "astronomy"}
...
      print()
+     if not books:
+         print("No books matched your search.")
```

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get(
    "http://127.0.0.1:8000/api/books",
    params={"search": "astronomy"}
)

print("Request URL:", response.request.url)
print("Status code:", response.status_code)
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

Beklenen sonuç:

```text
Status code: 200
Response body: []
Book count: 0
No books matched your search.
```

**Sonuç:** Arama başarıyla tamamlanmıştır; yalnızca eşleşen kayıt yoktur. Tek kitap işleminde `/api/books/999` belirli bir kaynağı hedefler ve kaynak yoksa `404` döner.

## 12. Deney 10 — İstek ve yanıt başlıklarını incele

### Ne yapıyoruz?

İstemci `Accept: application/json` gönderiyor; sunucunun `Content-Type` yanıt başlığını okuyoruz.

### Neden yapıyoruz?

İletişimde adres, durum kodu ve gövde dışında başlıkların da bulunduğunu; `Accept` ile `Content-Type` değerlerinin farklı taraflardan gönderildiğini görmek istiyoruz.

### Teorideki yeri

- Bölüm 7.2–7.3: HTTP isteği, yanıt başlıkları ve gövde

### Değişen satırlar

```diff
-     params={"search": "astronomy"}
+     params={"search": "API"},
+     headers={"Accept": "application/json"}
 )
  print("Request URL:", response.request.url)
+ print("Request Accept:", response.request.headers.get("Accept"))
  print("Status code:", response.status_code)
+ print("Response Content-Type:", response.headers.get("Content-Type"))
```

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get(
    "http://127.0.0.1:8000/api/books",
    params={"search": "API"},
    headers={"Accept": "application/json"}
)

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

| Başlık | Gönderen | Anlamı |
|---|---|---|
| `Accept: application/json` | İstemci | “JSON yanıt kabul ediyorum.” |
| `Content-Type: application/json` | Sunucu | “Bu yanıt gövdesi JSON'dur.” |

`Accept` başlığı sunucunun mutlaka istenen biçimde başarıyla yanıt vereceğini garanti etmez. `Content-Type` da tek başına işlemin başarılı olduğunu göstermez; hata gövdesi de JSON olabilir.

## 13. Deney 11 — İki sorgu parametresini birlikte uygula

### Ne yapıyoruz?

Başlık aramasıyla ödünç alınabilirlik filtresini birlikte sunuyoruz:

```text
/api/books?search=API&available=true
```

### Neden yapıyoruz?

İstemcinin birden fazla koşulu iletebildiğini ve sunucunun bu koşulları birlikte değerlendirdiğini görmek istiyoruz.

### Teorideki yeri

- Bölüm 7.1–7.2: URL sorgu bileşeni ve HTTP isteği
- Bölüm 13: Sunucunun girdileri okuyup koşullara göre sonuç üretmesi

### Sunucudaki değişen satırlar

```diff
- def get_books(search: str = ""):
+ def get_books(search: str = "", available: bool | None = None):
      results = []
      for book in books:
-         if search.casefold() in book["title"].casefold():
+         title_matches = search.casefold() in book["title"].casefold()
+         availability_matches = (
+             available is None or book["available"] == available
+         )
+         if title_matches and availability_matches:
              results.append(book)
```

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": {"first_name": "Deniz", "last_name": "Kaya"},
        "available": True,
        "tags": ["software", "education"],
        "rating": None
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": {"first_name": "Ece", "last_name": "Yılmaz"},
        "available": False,
        "tags": [],
        "rating": 0
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

### İstemcideki değişen satırlar

```diff
-     params={"search": "API"},
+     params={
+         "search": "API",
+         "available": "true"
+     },
```

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get(
    "http://127.0.0.1:8000/api/books",
    params={
        "search": "API",
        "available": "true"
    },
    headers={"Accept": "application/json"}
)

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

### Gözlem ve tartışma

- URL'deki `&`, iki sorgu parametresini ayırır.
- Sunucu kodundaki `and`, kitabın iki koşulu da sağlamasını ister.
- Parametrelerin URL'deki veya fonksiyondaki yazım sırası bu bağımsız filtrelerin sonucunu değiştirmez.
- `available: bool | None = None`, filtre için üç durumu ayırır: `True`, `False` ve parametrenin gönderilmemesi.
- URL'deki `true` JSON gövdesi değildir. HTTPX bunu URL metni içinde taşır; FastAPI tür bildirimine göre Python `True` değerine dönüştürür.

## 14. Deney 12 — Geçerli JSON ile doğru uygulama verisini ayır

### Ne yapıyoruz?

Bu bölüm HTTP isteği göndermez. API yanıt gövdesini temsil eden metinleri ayrı bir `book_validation.py` dosyasında ayrıştırıp doğruluyoruz.

### Neden yapıyoruz?

JSON yazımının geçerli olması, alan türlerinin ve uygulama değerlerinin doğru olduğu anlamına gelmez. Hatanın hangi katmanda oluştuğunu ayırmak istiyoruz.

### Teorideki yeri

- Bölüm 10.3 ve 12.1: JSON yazım kuralları ve ayrıştırma
- Bölüm 12.4–12.5: Tür doğrulaması ve iş kuralı doğrulaması

### 14.1. Geçerli JSON, geçersiz iş değeri

**Amaç:** JSON'un negatif sayıya izin vermesinin, kitap uygulamasının negatif sayfa sayısını kabul edeceği anlamına gelmediğini görmek.

#### Yeni dosya — değişen satırlar

```diff
+ import json
+
+ response_body = '{"title": "API Yolculuğu", "page_count": -20}'
+ book = json.loads(response_body)
+
+ if book["page_count"] <= 0:
+     print("Validation failed: Page count must be greater than zero.")
```

#### `book_validation.py` dosyasının tamamı

```python
import json

response_body = '{"title": "API Yolculuğu", "page_count": -20}'

book = json.loads(response_body)

print("JSON parsed successfully.")
print("Book title:", book["title"])
print("Page count:", book["page_count"])

if book["page_count"] <= 0:
    print("Validation failed: Page count must be greater than zero.")
else:
    print("Validation passed.")
```

**Sonuç:** JSON okunmuştur; `-20` ise uygulamanın “sayfa sayısı sıfırdan büyük olmalı” kuralını geçememiştir.

### 14.2. Geçerli JSON, yanlış veri türü

**Amaç:** Ekranda `240` görmekle değerin sayı olmasının aynı şey olmadığını göstermek.

#### Değişen satırlar

```diff
- response_body = '{"title": "API Yolculuğu", "page_count": -20}'
+ response_body = '{"title": "API Yolculuğu", "page_count": "240"}'
...
+ page_count = book["page_count"]
+ print("Python type:", type(page_count).__name__)
- if book["page_count"] <= 0:
+ if type(page_count) is not int:
+     print("Validation failed: Page count must be an integer.")
+ elif page_count <= 0:
```

#### `book_validation.py` dosyasının tamamı

```python
import json

response_body = '{"title": "API Yolculuğu", "page_count": "240"}'

book = json.loads(response_body)

print("JSON parsed successfully.")
print("Book title:", book["title"])

page_count = book["page_count"]

print("Page count:", page_count)
print("Python type:", type(page_count).__name__)

if type(page_count) is not int:
    print("Validation failed: Page count must be an integer.")
elif page_count <= 0:
    print("Validation failed: Page count must be greater than zero.")
else:
    print("Validation passed.")
```

`"240"` metindir; `240` sayıdır. `print()` metnin tırnaklarını göstermediği için türü ayrıca inceledik.

### 14.3. Geçersiz JSON yazımı

**Amaç:** Alanları ve iş kurallarını kontrol etmeden önce metnin JSON olarak okunabilmesi gerektiğini görmek.

#### Değişen satırlar

```diff
- response_body = '{"title": "API Yolculuğu", "page_count": "240"}'
- book = json.loads(response_body)
+ response_body = '{"title": "API Yolculuğu", "page_count": 240,}'
+ try:
+     book = json.loads(response_body)
+ except json.JSONDecodeError:
+     print("JSON parsing failed: Invalid JSON syntax.")
+ else:
+     # Alan ve değer kontrolleri yalnızca JSON okunursa burada çalışır.
```

#### `book_validation.py` dosyasının tamamı

```python
import json

response_body = '{"title": "API Yolculuğu", "page_count": 240,}'

try:
    book = json.loads(response_body)
except json.JSONDecodeError:
    print("JSON parsing failed: Invalid JSON syntax.")
else:
    print("JSON parsed successfully.")
    print("Book title:", book["title"])

    page_count = book["page_count"]

    print("Page count:", page_count)
    print("Python type:", type(page_count).__name__)

    if type(page_count) is not int:
        print("Validation failed: Page count must be an integer.")
    elif page_count <= 0:
        print("Validation failed: Page count must be greater than zero.")
    else:
        print("Validation passed.")
```

### Üç hata katmanının özeti

| Örnek | Sonuç |
|---|---|
| `{"page_count": 240,}` | JSON yazımı hatalı; ayrıştırılamaz. |
| `{"page_count": "240"}` | JSON geçerli; alanın türü yanlış. |
| `{"page_count": -20}` | JSON ve tür geçerli; iş kuralı sağlanmıyor. |
| `{"page_count": 240}` | Üç kontrolü de geçer. |

## 15. Deney 13 — 404 ile bağlantı kuramamayı ayır

### Ne yapıyoruz?

Önce sunucuyu kapatıp mevcut istemcinin bağlantı hatasını gözlemliyor, sonra bu hatayı kontrollü biçimde yakalıyoruz.

### Neden yapıyoruz?

`404` durumunda sunucudan HTTP yanıtı gelir. Sunucu kapalıyken ise HTTP durum kodu alınmaz. Bu iki durumu aynı hata mesajıyla açıklamamak gerekir.

### Teorideki yeri

- Bölüm 5.4: Sunucu yanıtı ile kullanılamayan bağlantının ayrımı
- Bölüm 7.4 ve Bölüm 14: `404` yanılgısı

Sunucu terminalinde **Ctrl+C** ile sunucuyu kapat. İstemciyi çalıştırdığında `httpx.ConnectError: [Errno 111] Connection refused` benzeri bir hata beklenir.

### Değişen satırlar

```diff
- response = httpx.get(...)
+ try:
+     response = httpx.get(...)
+ except httpx.ConnectError:
+     print("Connection failed: Could not connect to the server.")
+     print("Check that the server is running at http://127.0.0.1:8000.")
+ else:
+     # Yanıt ancak bağlantı kurulursa burada işlenir.
```

### `client.py` dosyasının tamamı

```python
import httpx

try:
    response = httpx.get(
        "http://127.0.0.1:8000/api/books",
        params={
            "search": "API",
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

Sunucu kapalıyken beklenen kısa çıktı:

```text
Connection failed: Could not connect to the server.
Check that the server is running at http://127.0.0.1:8000.
```

Bu mesaj bağlantıyı düzeltmez; istemcinin sorunu anlaşılır biçimde bildirmesini sağlar.

## 16. Deney 14 — Yol doğrulaması ve yönlendirme sırasını anla

### Ne yapıyoruz?

Tam sayı bekleyen yola metin gönderiyor, ardından sabit ve dinamik yolların nasıl eşleştiğini karşılaştırıyoruz.

### Neden yapıyoruz?

İstemcinin gönderdiği her yol değerinin fonksiyona ulaşmadığını ve kaynak yolunu seçmenin sunucudaki yönlendirme kurallarına bağlı olduğunu görmek istiyoruz.

### Teorideki yeri

- Bölüm 7.1: Yol, kaynak ve uç nokta
- Bölüm 12.4: Beklenen veri türünün doğrulanması

### 16.1. `404` ile `422` aynı değildir

Sunucu çalışırken şu isteği gönder:

```bash
curl -i http://127.0.0.1:8000/api/books/abc
```

`book_id: int` tanımı nedeniyle FastAPI `abc` değerini tam sayıya çeviremez. `get_book()` fonksiyonu çalışmadan yaklaşık şu sonuç alınır:

```text
422 Unprocessable Entity
```

```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["path", "book_id"],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "abc"
    }
  ]
}
```

FastAPI sürümüne göre ayrıntılar değişebilir.

| İstek | Sonuç | Açıklama |
|---|---:|---|
| `/api/books/57` | `200` | Kimlik geçerli ve kitap var. |
| `/api/books/999` | `404` | Kimlik geçerli; hedef kitap yok. |
| `/api/books/abc` | `422` | Yol değeri beklenen tam sayı türüne uymuyor. |

### 16.2. İki mevcut yolun sırası

Şu iki yol arasında eşleşme belirsizliği yoktur:

```python
@app.get("/api/books")
def get_books():
    ...
```

```python
@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    ...
```

`/api/books` yolunda `{book_id}` için fazladan bölüm bulunmaz. Bu nedenle bu iki tanımın sırası değişse de istekler ayrılabilir. Okunabilirlik için önce koleksiyon, sonra tek kaynak işlemini yazıyoruz.

Sabit ve dinamik yollar aynı bölümde çakışabilirse sıra önemlidir:

```python
@app.get("/api/books/latest")
def get_latest_book():
    ...


@app.get("/api/books/{book_id}")
def get_book(book_id: str):
    ...
```

Sabit `/api/books/latest` yolu, `latest` sözcüğünün `book_id` sanılmaması için dinamik yoldan önce yazılır.

Sorgu parametreleri başka bir yol oluşturmaz. Şu istek yine `/api/books` işlemine gider:

```text
/api/books?search=Python&available=true
```

## 17. Kısa karşılaştırma — REST, SOAP ve GraphQL

Bu bölümde kod değiştirmiyoruz. Aynı “57 numaralı kitabın adını getir” ihtiyacının farklı yaklaşımlarda nasıl ifade edildiğini görüyoruz.

### Kaynak odaklı HTTP örneğimiz

```http
GET /api/books/57
```

Adres hangi kaynağı, `GET` o kaynağın bilgisini almak istediğimizi belirtir. JSON kullanmamız tek başına bütün REST kısıtlarını sağladığımızı kanıtlamaz.

### SOAP mesajı

```xml
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Body>
    <GetBook>
      <BookId>57</BookId>
    </GetBook>
  </soap:Body>
</soap:Envelope>
```

SOAP bir mesajlaşma protokolüdür; örnekte işlem ve girdi XML zarfının gövdesinde taşınır.

### GraphQL sorgusu

```graphql
{
  book(id: 57) {
    title
    author {
      first_name
      last_name
    }
  }
}
```

`book(id: 57)` hangi kaydı istediğimizi, içindeki alanlar kaydın hangi bilgilerini istediğimizi belirtir. Başlıkta veya etiketlerde arama yapmakla bu alan seçimi aynı şey değildir.

| Kavram | Türü | Bu örnekteki ifade biçimi |
|---|---|---|
| REST | Mimari stil | Kaynak yolu ve HTTP metodu |
| SOAP | Mesajlaşma protokolü | XML zarfındaki işlem ve alanlar |
| GraphQL | Sorgu dili ve yürütme sistemi | Kayıt ile istenen alanların sorguda seçilmesi |

## 18. Son uygulama — Üçüncü kitabı ekle ve filtrele

### Ne yapıyoruz?

Öğrendiğimiz veri yapılarıyla üçüncü kitabı koleksiyona ekliyor; istemciden başlık ve ödünç durumu koşullarını birlikte gönderiyoruz.

### Neden yapıyoruz?

Haftanın veri türleri, sorgu parametreleri, koşulları ve istemci görünümü çalışmalarını tek çalışan örnekte birleştiriyoruz.

### Teorideki yeri

- Bölüm 6: İsteğin uçtan uca yolculuğu
- Bölüm 13: Kitap arama örneği

### Sunucudaki değişen satırlar

```diff
      {
          "id": 57,
          ...
          "rating": 0
+     },
+     {
+         "id": 73,
+         "title": "Python ile Web API",
+         "author": {
+             "first_name": "Can",
+             "last_name": "Demir"
+         },
+         "available": True,
+         "tags": ["python", "api"],
+         "rating": 4.5
      }
```

### Son `server.py` dosyasının tamamı

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

### İstemcideki değişen satırlar

```diff
      params={
-         "search": "API",
+         "search": "Python",
          "available": "true"
      },
```

### Son `client.py` dosyasının tamamı

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

Beklenen temel sonuç:

```text
Book count: 1
Book title: Python ile Web API
Book author: Can Demir
Availability: Available to borrow
Tags:
- python
- api
Rating: 4.5
```

## 19. Çalışırken karşılaşılan sorunlar

### `python: command not found`

Sanal ortam etkin değilse Linux veya WSL'de `python3` kullan. Sanal ortam etkinleştirildiğinde `python` komutu ortamın çalıştırıcısını göstermelidir:

```bash
source api-env/bin/activate
```

### `uv: command not found`

uv kurulduğu hâlde mevcut terminal bulamıyorsa:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### `address already in use`

8000 portunda eski sunucu çalışıyor olabilir:

```bash
ss -ltnp 'sport = :8000'
```

Sunucu terminalinde **Ctrl+C** işlemi kapatır. **Ctrl+Z** işlemi kapatmak yerine duraklatabilir; duraklatılan işlem portu tutmaya devam eder. Süreç numarası biliniyorsa önce ne olduğunu kontrol et:

```bash
ps -p 4225 -o pid,ppid,stat,args
```

Buradaki `4225` yalnızca örnektir; kendi çıktındaki PID değerini kullan.

### Kod değişti ama eski sonuç geliyor

Uvicorn'u otomatik yenileme seçeneği olmadan başlattık. `server.py` değişince sunucuyu Ctrl+C ile kapatıp yeniden çalıştır:

```bash
python -m uvicorn server:app
```

Yalnızca `client.py` değiştiyse sunucuyu yeniden başlatmaya gerek yoktur.

### Web sitesindeki 404 ile API'deki 404

İkisi de HTTP durum kodudur. Bir web sitesi genellikle insan için HTML hata sayfası, API ise istemci program için JSON hata gövdesi döndürür. Her iki durumda da HTTP yanıtı alınmıştır.

## 20. Haftalık değerlendirme

### Sorular

1. `client.py` ve `server.py` hangi rolleri üstlenir? Uvicorn'un görevi nedir?
2. `GET /api/books/57` içinde `GET` ve `57` ayrı ayrı neyi belirtir?
3. `404` ile `httpx.ConnectError` arasındaki temel fark nedir?
4. `false`, `null` ve `0` neden aynı kabul edilmemelidir?
5. `search=Python` parametresi mevcut sunucu kodunda hangi alanda aranır? Yalnızca `tags` içinde `python` bulunması yeterli midir?
6. URL'deki `&` ile Python kodundaki `and` ne iş yapar?
7. `/api/books?search=astronomy` neden `200` ve `[]`; `/api/books/999` neden `404` döndürür?
8. `/api/books/abc` neden `404` yerine `422` döndürebilir?
9. `Accept` ile `Content-Type` başlıklarını hangi taraf gönderir ve ne anlatırlar?
10. `GET /api/books?search=Python&available=true` isteğinden kitabın terminalde görünmesine kadar süreci altı kısa adımda anlat.

### Cevapları değerlendirirken aranacak noktalar

- İstemci isteği başlatır; sunucu isteği karşılar; Uvicorn uygulamayı çalıştırıp bağlantıları dinler.
- `GET` bilgi alma niyetini, `/57` hedef kitap kimliğini belirtir.
- `404` alınmış HTTP yanıtıdır; bağlantı hatasında kullanılabilir HTTP yanıtı yoktur.
- `false` mantıksal cevap, `null` sözleşmeye göre yorumlanan özel boş/yok değeri, `0` sayıdır.
- `search` yalnızca `title` alanında aranır; parametrenin anlamını sunucu kodu belirler.
- `&` URL parametrelerini ayırır; `and` iki koşulun birlikte doğru olmasını ister.
- Koleksiyon araması sıfır sonuçla tamamlanabilir; tek kaynak isteğinde hedef yoksa `404` verilir.
- `abc`, `book_id: int` tür doğrulamasını geçemez.
- `Accept` istemcinin kabul ettiği biçimi, `Content-Type` sunucunun gönderdiği gövde biçimini bildirir.
- Yol eşleşmesi, parametre dönüşümü, filtreleme, serileştirme, HTTP yanıtı, ayrıştırma ve istemci görünümü birbirinden ayrılmalıdır.

## 21. Kaynaklar

- [FastAPI — First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [FastAPI — Path Parameters](https://fastapi.tiangolo.com/tutorial/path-params/)
- [HTTPX — QuickStart](https://www.python-httpx.org/quickstart/)
- [HTTPX — Exceptions](https://www.python-httpx.org/exceptions/)
- [uv — Installation](https://docs.astral.sh/uv/getting-started/installation/)
- [Python — `json` modülü](https://docs.python.org/3/library/json.html)

Bu föydeki uygulama `localhost` üzerinde çalışır; genel internet bağlantısı API iletişimi için gerekli değildir. İnternet yalnızca araçların ilk kurulumu sırasında gerekebilir.

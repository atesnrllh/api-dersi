# Hafta 02 — Practice

## İstemciden yeni kitap eklemek: POST ve istek gövdesi

Birinci haftanın sonunda kataloğumuzda üç kitap vardı. Üçüncü kitabı eklemek için `server.py` dosyasını açıp `books` listesine yeni bir sözlük yazmıştık.

**Bu hafta kitabın bilgilerini `client.py` dosyasına yazıp sunucuya göndereceğiz.** Bunun için **POST** adlı HTTP metodunu kullanacağız. Sunucuya, “Bu bilgilerle kataloğa yeni bir kitap ekle” isteğinde bulunacağız. Kitabı listeye ekleyecek fonksiyonu da `server.py` içinde yazacağız. Bu fonksiyonu hazırladıktan sonra her yeni kitap için sunucu dosyasındaki listeyi elle değiştirmemiz gerekmeyecek.

Önce mevcut üç kitabı GET ile okuyacağız. Ardından yeni kitabın bilgilerinin sunucuya ulaştığını kontrol edecek, bir sonraki deneyde bu bilgileri listeye ekleyeceğiz. Sonraki deneylerde eklenen kitabı okuyacak; başlık eksik gönderildiğinde, aynı istek tekrarlandığında ve sunucu yeniden başlatıldığında ne olduğunu göreceğiz.

## Başlamadan önce

Bu hafta sunucuya gönderilen kitap bilgilerinin kontrolü için **Pydantic** paketini kullanacağız. Örneğin, gönderilen bilgilerde kitap başlığının bulunmasını isteyeceğiz. Pydantic, FastAPI ile birlikte kurulur. Şu komutla sürümünü kontrol et:

```bash
python -c "import pydantic; print(pydantic.__version__)"
```

Komut, yüklü Pydantic sürümünü ekrana yazar. Çıktı `2.` ile başlamalı; örneğin `2.13.5`. Örneklerde kullanacağımız `model_dump()` işlemi bu sürüme aittir. Çıktı `1.` ile başlıyorsa etkin ortamda `uv pip install --upgrade fastapi "pydantic>=2,<3"` çalıştır, sonra sunucuyu yeniden başlat.

**Kitap sayılarını doğru izlemek için:** Bu haftaki sunucu her açıldığında dosyada yazılı üç kitapla başlar: `42`, `57`, `73`. İstekle eklediğimiz kitaplar, sunucu çalıştığı sürece bellekteki `books` listesinde tutulur. Henüz onları bir dosyaya veya veritabanına kaydeden kod yazmıyoruz. Bu yüzden sunucuyu yeniden başlatınca başlangıçtaki üç kitaba döneriz. Deneylerdeki “yeniden başlat” ve “bir kez çalıştır” adımlarını izlersen ekrandaki kitap sayıları aşağıdaki çıktılarla aynı olur.

## Deney 1 — Bildiğimiz kataloğu aç

Önce birinci haftadaki sunucu ile istemcinin çalıştığını ve katalogda üç kitap bulunduğunu kontrol edeceğiz. Aşağıdaki `server.py`, birinci haftanın son sunucusudur: `GET /book` kitap listesini, `GET /book/42` ise `42` kimlikli kitabı döndürür.

Arama ve kitabın bir okuyucuya verilebilir olup olmadığını seçen `available` filtresi kodda duruyor. Bu deneyde filtre göndermeyip üç kitabın tamamını okuyacağız.

### `server.py` dosyasının tamamı

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


@app.get("/book")
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


@app.get("/book/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

İstemcinin çıktısını bu hafta yapacağımız değişiklikleri izlemek için kısaltıyoruz: durum kodunu, kitap sayısını, kimlik ve başlıkları yazdırması yeterli. Sunucudaki diğer kitap alanları silinmiyor.

### `client.py` dosyasının tamamı

```python
import httpx

try:
    response = httpx.get("http://127.0.0.1:8000/book")
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
else:
    print("Status code:", response.status_code)
    if response.status_code == 200:
        books = response.json()
        print("Book count:", len(books))
        for book in books:
            print(book["id"], "-", book["title"])
    else:
        print("Response body:", response.text)
```

Beklenen çıktı:

```text
Status code: 200
Book count: 3
42 - API Yolculuğu
57 - Veriyle İlk Adımlar
73 - Python ile Web API
```

Bu istemci sunucudan kitap listesini istedi. Sonraki deneyde ise istemcide hazırladığımız yeni bir kitabın bilgilerini sunucuya göndereceğiz.

## Deney 2 — Kitap bilgilerini sunucuya gönder ve ulaştığını kontrol et

Kataloğa eklemek istediğimiz kitabın başlığı **HTTP ile Yeni Bir Kitap**, yazarı **Ada Yıldız** olsun. Bu bilgiler önce istemcide bulunacak. Sunucunun kitabı ekleyebilmesi için başlığı, yazarı ve diğer alanları ona göndermemiz gerekir.

### Kitap bilgileri HTTP isteğinin neresinde gönderilir?

Birinci haftada `GET /book/42` gönderdiğimizde, adresin sonundaki `42` ile **hangi kitabı istediğimizi** belirtiyorduk. Kitabın başlığını veya yazarını sunucuya göndermiyorduk; bu bilgileri sunucunun yanıtından alıyorduk.

Şimdi `POST /book` isteğinde bulunacağız. `POST`, HTTP isteğinin metot adıdır; uygulamamızda yeni kitap ekleme işlemi için bu metodu kullanacağız. Adres yine `http://127.0.0.1:8000/book` olacak. Yeni kitabın bilgilerini adresin sonuna yazmak yerine, isteğin **gövde (body)** denilen veri bölümüne JSON biçiminde koyacağız.

İstek ile yanıt iki ayrı HTTP mesajıdır. **İstek gövdesi**, istemcinin sunucuya gönderdiği veriyi; **yanıt gövdesi**, sunucunun istemciye gönderdiği veriyi taşır. [FastAPI: istek gövdesi](https://fastapi.tiangolo.com/tutorial/body/)

| Bu deneydeki mesaj | Gönderen → alan | Gövdede ne var? |
|---|---|---|
| `POST /book` isteği | İstemci → sunucu | İstemcide hazırladığımız yeni kitabın başlığı, yazarı ve diğer alanları. |
| Bu POST isteğinin yanıtı | Sunucu → istemci | Sunucunun aldığı ve kontrol ettiği kitap bilgileri. İstemci bunları terminale yazdıracak. |

Önce istemcinin göndereceği kitabı ve isteği, ardından sunucunun bu isteği nasıl karşılayacağını inceleyelim. İki dosyayı da hazırladıktan sonra bölümün sonundaki adımda çalıştıracağız.

### `client.py` dosyasının tamamı

```python
import httpx

new_book = {
    "title": "HTTP ile Yeni Bir Kitap",
    "author": {
        "first_name": "Ada",
        "last_name": "Yıldız"
    },
    "available": True,
    "tags": ["http", "python"],
    "rating": None
}

try:
    response = httpx.post(
        "http://127.0.0.1:8000/book",
        json=new_book
    )
    list_response = httpx.get("http://127.0.0.1:8000/book")
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
else:
    print("Request method:", response.request.method)
    print("Request Content-Type:", response.request.headers.get("Content-Type"))
    print("Status code:", response.status_code)
    print("Response body:", response.text)
    if list_response.status_code == 200:
        print("Book count:", len(list_response.json()))
    else:
        print("List status:", list_response.status_code)
```

Bu istemci sırayla **iki ayrı istek** gönderir. İlk `httpx.post(...)` çağrısı kitabı gönderir ve sunucunun yanıtını `response` değişkenine verir. Ardından `httpx.get(...)` çağrısı katalogdaki kitap listesini ister ve onun yanıtını `list_response` değişkenine verir. İkinci isteğin amacı kitap sayısının değişip değişmediğini kontrol etmektir.

### İstemcide kitabı hazırla ve POST ile gönder

Yukarıdaki `client.py` içinde yeni kitabın bilgilerini `new_book` adlı **Python sözlüğüne** yazıyoruz. `httpx.post(..., json=new_book)` satırındaki `json=`, HTTPX'e “Bu sözlüğü JSON'a çevir ve isteğin gövdesinde gönder” der. `new_book` sözlüğünde anahtarlar ve değerler bizim hazırladığımız kitap bilgileridir; `json` ise HTTPX'in bu amaçla kullandığı parametre adıdır.

Python sözlüğünde `True` ve `None` yazacağız. HTTPX JSON'a çevirirken bunları `true` ve `null` olarak gönderir; dönüştürmeyi elle yapmamız gerekmez.

Birinci haftadaki `params=` ile bu deneydeki `json=` farklı yerlerde bilgi taşır:

| Kullandığımız ifade | Bilginin gittiği yer |
|---|---|
| `params={"search": "Python"}` | Birinci haftadaki gibi adresin sorgu bölümü: `/book?search=Python`. |
| `json=new_book` | Bu deneydeki gibi isteğin gövdesi. Kitabın bilgileri adresin sonuna eklenmez. |

#### Content-Type başlığı nereden geliyor?

HTTPX ayrıca isteğe `Content-Type: application/json` başlığını ekler. **HTTP başlığı**, mesajla ilgili ek bilgi taşıyan ad–değer çiftidir. Burada `Content-Type`, gönderdiğimiz gövdenin biçimini; `application/json` ise bu biçimin JSON olduğunu bildirir. Bu başlık kitabın başlığı olan `title` alanından farklıdır. [HTTPX: JSON gönderme](https://www.python-httpx.org/quickstart/#sending-json-encoded-data)

**Kodda bu başlığı açıkça yazmadık; `json=new_book` kullandığımız için HTTPX kendisi ekliyor.**

Şu çağrıda:

```python
response = httpx.post(
    "http://127.0.0.1:8000/book",
    json=new_book
)
```

HTTPX, `json=new_book` nedeniyle:

1. `new_book` sözlüğünü JSON’a çevirip isteğin gövdesine koyar.
2. Gövdenin JSON olduğunu sunucuya bildirmek için isteğe otomatik olarak `Content-Type: application/json` başlığını ekler. [HTTPX kaynak kodu](https://github.com/encode/httpx/blob/master/httpx/_content.py#L160-L167)

Örneğimizde bu başlığı **görmek için** şu satır bulunuyor:

```python
print("Request Content-Type:", response.request.headers.get("Content-Type"))
```

Çıktısı:

```text
Request Content-Type: application/json
```

Bu `print` satırı başlığı **eklemez**; HTTPX’in gönderdiği istekteki başlığı **okuyup ekrana yazar**. Buradaki `response.request`, sunucudan gelen yanıta yol açan, bizim gönderdiğimiz isteğe erişmemizi sağlar.

#### İstemcinin terminale yazdırdığı bilgiler

| İstemcide okuduğumuz ifade | Terminalde gösterdiği bilgi |
|---|---|
| `response.request.method` | İlk isteği `POST` metoduyla gönderdiğimizi gösterir. |
| `response.request.headers.get("Content-Type")` | Gönderdiğimiz **isteğin** gövde biçimini gösterir: `application/json`. |
| `response.status_code` | Sunucunun POST isteğine verdiği **yanıtın** durum kodudur. |
| `response.text` | POST yanıtının gövdesini metin olarak gösterir; sunucunun geri gönderdiği kitap bilgilerini burada göreceğiz. |
| `len(list_response.json())` | GET yanıtındaki JSON kitap listesini Python listesine çevirip eleman sayısını bulur. |

### Sunucunun kabul edeceği kitap alanlarını tanımla

Sunucuda, “Kitabın `title` alanında bir başlık, `author` alanında yazar bilgisi bulunmalı” gibi kuralları **biz yazacağız**. FastAPI bu kuralları kendiliğinden tahmin etmez. **Alan**, `title` veya `author` gibi bir bilginin adıdır; **tür** ise o alanda metin, sayı veya liste gibi hangi çeşit değer beklediğimizdir.

Bu kuralları Pydantic'in `BaseModel` sınıfını kullanarak tanımlarız. Tanıma **veri modeli** denir. Aşağıdaki `Author`, yazar bilgisinin; `BookCreate`, sunucuya gönderilecek yeni kitap bilgisinin modelidir. Bu sınıfları `server.py` içine yazıyoruz; tam dosya biraz aşağıda verilmiştir.

```python
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
```

| Satır | Bu kitap örneğinde anlamı |
|---|---|
| `from pydantic import BaseModel` | Pydantic paketindeki `BaseModel` sınıfını kodumuzda kullanmak üzere alır. |
| `class Author(BaseModel):` | `Author` adlı bir sınıf tanımlar. Parantezdeki `BaseModel`, Pydantic'in alanları kontrol etme ve gelen değerleri tutma özelliklerini bu sınıfa kazandırır. |
| `first_name: str`, `last_name: str` | Yazarın adı ve soyadı metin olmalıdır. Göndereceğimiz örnekte bunlar `"Ada"` ve `"Yıldız"` olacak. |
| `class BookCreate(BaseModel):` | Yeni kitap gönderirken kullanılacak modeli tanımlar. `BookCreate` adını biz seçtik; sınıfın adı listeye kitap ekleyen bir komut değildir. |
| `title: str` | JSON içindeki `"title"` alanından metin beklediğimizi belirtir; bu satır bir başlık değeri atamaz. Göndereceğimiz değer `"HTTP ile Yeni Bir Kitap"` olacak. |
| `author: Author` | `author` içinde, yukarıdaki `Author` modeline uygun `first_name` ve `last_name` alanları bulunmalıdır. İstemci `"author": {"first_name": "Ada", "last_name": "Yıldız"}` gönderecek. |
| `available: bool` | Kitap şu anda bir okuyucuya verilebilir mi? `bool` iki mantıksal değeri belirtir: Python'da `True` / `False`, JSON'da `true` / `false`. |
| `tags: list[str]` | Etiketler metinlerden oluşan bir liste olmalıdır; örneğin `["http", "python"]`. Etiket yoksa `[]` gönderilebilir. |
| `rating: float \| None = None` | `float`, `4.5` gibi bir sayıyı; `None`, henüz puan bulunmadığını belirtir. `\|`, bu iki türden birini kabul ettiğimizi söyler. Sondaki `= None` ise alan hiç gönderilmezse kullanılacak değerdir. |

Bu modelde `title`, `author`, `available`, `tags` ve yazarın iki alanına bir **varsayılan değer** atamadık; bu yüzden istemcinin bunları göndermesi gerekir. `rating` içinse `= None` yazdık: istemci puanı göndermeyebilir. Henüz puan olmadığını JSON içinde belirtmek isterse `"rating": null` kullanır. Bu durumda da Python tarafındaki değer `None` olur.

Modeli tanımlarken belirli bir kitabın başlığını ve yazarını sınıfa yazmadık. **Sınıf, beklediğimiz alanları tanımlar; model nesnesi ise bir istekle gelen gerçek değerleri tutar.** Örneğin Ada Yıldız'ın kitabı geldiğinde, bu değerleri taşıyan bir `BookCreate` nesnesi oluşturulur. [Pydantic: modeller](https://docs.pydantic.dev/latest/concepts/models/)

`id` alanı bu modelde yok. İstemci yeni kitabın kimliğini seçmeyecek; Deney 3'te bunu sunucudaki kod hesaplayacak.

### Gelen bilgileri fonksiyonda al ve yanıt olarak döndür

```python
@app.post("/book")
def create_book(book_data: BookCreate):
    return book_data.model_dump()
```

| Satır | Ne yapıyor? |
|---|---|
| `@app.post("/book")` | FastAPI'ye, `POST /book` isteğini altındaki `create_book` fonksiyonunun karşılayacağını bildirir. |
| `def create_book(book_data: BookCreate):` | `book_data`, fonksiyon içinde gelen kitap bilgilerine erişeceğimiz parametredir. `: BookCreate`, bu bilgilerin hangi modele göre kontrol edileceğini belirtir. |
| `return book_data.model_dump()` | `book_data` içindeki değerleri bir Python sözlüğüne çevirip döndürür. FastAPI bu sözlüğü JSON'a çevirerek istemciye yanıt gönderir. |

İstemci POST isteğini gönderdiğinde **FastAPI önce JSON gövdesini okur ve Pydantic ile `BookCreate` kurallarına göre kontrol eder**. Bilgiler uygunsa oluşturduğu model nesnesini `book_data` parametresine vererek `create_book` fonksiyonunu çağırır. Böylece fonksiyonun içinde `book_data.title`, gönderdiğimiz `"HTTP ile Yeni Bir Kitap"` değeridir. Kitap başlığı gibi zorunlu bir alan eksikse fonksiyon çağrılmadan hata yanıtı verilir; bunu Deney 5'te deneyeceğiz.

`book_data`, bizim seçtiğimiz Python parametre adıdır. JSON'a `book_data` adında ek bir alan yazmayacağız. FastAPI, bu parametrenin türü `BookCreate` adlı Pydantic modeli olduğu için kitap bilgilerini isteğin gövdesinden alır. Birinci haftadaki `search: str = ""` ise arama değerini `/book?search=Python` adresinin sorgu bölümünden alıyordu.

`book_data`, istemcinin gönderdiği kitap bilgilerini tutan bir **`BookCreate` nesnesidir**. Örneğin başlığı `book_data.title` yazarak okuruz.

Pydantic’in sağladığı **`model_dump()`**, bu nesnedeki alan adlarını ve değerlerini alıp **yeni bir Python sözlüğü oluşturur**:

```python
book_dict = book_data.model_dump()
```

Bu tek satır, dönüşümün sonucunu ayrı bir değişkende göstermek için verilmiş bir açıklama örneğidir. `book_dict` adını biz seçtik; oluşturulan sözlüğü tutar. Bu satırı `server.py` dosyasına ayrıca eklemiyoruz. Tam dosyadaki `return book_data.model_dump()` satırı, sözlüğü ayrı bir değişkene atamadan doğrudan döndürür.

Bu işlemden sonra `book_dict` şu bilgileri içerir:

```python
{
    "title": "HTTP ile Yeni Bir Kitap",
    "author": {
        "first_name": "Ada",
        "last_name": "Yıldız"
    },
    "available": True,
    "tags": ["http", "python"],
    "rating": None
}
```

**Kitap bilgileri aynıdır; onları tuttuğumuz yapı ve okuma biçimimiz değişmiştir:**

| Bilgi | `book_data` nesnesinden okuma | Oluşturulan sözlükten okuma |
|---|---|---|
| Kitap başlığı | `book_data.title` | `book_dict["title"]` |
| Yazarın adı | `book_data.author.first_name` | `book_dict["author"]["first_name"]` |

İçerideki `author` nesnesi de bir sözlüğe dönüşür. Ancak **`book_data` değişmez**; model nesnesi olarak kalır. Oluşturulan yeni sözlüğü `book_dict` değişkeninde tutarız. [Pydantic belgeleri](https://docs.pydantic.dev/latest/concepts/serialization/#python-mode)

`model_dump()` tek başına:

- **JSON metni oluşturmaz.** Yukarıdaki sonuç bir Python sözlüğüdür.
- **Kitabı listeye eklemez veya dosyaya kaydetmez.**
- **İstemciye yanıt göndermez.**

Bizim kodumuzdaki:

```python
return book_data.model_dump()
```

satırı iki işi birleştirir: `model_dump()` sözlüğü oluşturur; `return` bu sözlüğü fonksiyonun sonucu olarak FastAPI’ye verir. **FastAPI de JSON yanıtını oluşturur.**

Şimdilik sözlüğü yanıt olarak döndürüyoruz. Sonraki deneyde sözlüğe kitabın `id` bilgisini ekleyip onu `books` listesine koyacağız.

Aynı `/book` yolunda hem okuma hem kitap gönderme işlemi bulunabilir. FastAPI, hangi fonksiyonu çağıracağını seçerken **hem HTTP metoduna hem yola** bakar:

| İstek | Çalışan fonksiyon |
|---|---|
| `GET /book` | `get_books(...)` |
| `POST /book` | `create_book(...)` |
| `GET /book/42` | `get_book(book_id=42)` |

### Sunucu neden aldığı kitabı hemen listeye eklemiyor?

Bu deneyde `client.py`, yeni kitabın bilgilerini sunucuya gönderecek. FastAPI, gönderilen bilgileri okuyup kontrol edecek ve `create_book` fonksiyonuna verecek. Fonksiyon bu bilgileri henüz kitap listesine eklemeyecek; yanıt olarak istemciye geri gönderecek. Böylece istemcinin gönderdiği başlık ve yazar bilgilerinin sunucudaki fonksiyona ulaştığını çıktıda göreceğiz.

Bu kontrolden sonra GET ile listeyi tekrar okuyacağız. Sayı hâlâ üç olacak; çünkü henüz listeye ekleme kodunu yazmadık. Deney 3'te aynı fonksiyona ekleme satırlarını yazıp sayının dörde çıktığını göreceğiz. Sunucu, gönderilen kitap bilgilerini kontrol ettikten sonra doğrudan listeye ekleyebilir. Biz bu deneyde henüz ekleme kodunu yazmıyoruz. Önce bilgilerin sunucuya doğru ulaştığını görmek için onları yanıt olarak geri gönderiyoruz; listeye eklemeyi sonraki deneyde yapacağız.

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException
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


@app.get("/book")
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


@app.get("/book/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")


@app.post("/book")
def create_book(book_data: BookCreate):
    return book_data.model_dump()
```

### İki dosya hazır: isteği gönder ve sonucu kontrol et

Sunucuyu yeniden başlat ve istemciyi **bir kez** çalıştır.

Beklenen çıktı:

```text
Request method: POST
Request Content-Type: application/json
Status code: 200
Response body: {"title":"HTTP ile Yeni Bir Kitap","author":{"first_name":"Ada","last_name":"Yıldız"},"available":true,"tags":["http","python"],"rating":null}
Book count: 3
```

`Response body` satırında **HTTP ile Yeni Bir Kitap** ve **Ada Yıldız** bilgilerini görüyorsan sunucu gönderdiğimiz bilgileri alıp yanıt olarak döndürmüştür. Bu fonksiyon için farklı bir başarı kodu belirtmediğimizden FastAPI, yanıtı varsayılan `200` durum koduyla gönderir.

`Book count: 3`, sunucudaki listeye henüz kitap eklenmediğini gösterir. Fonksiyonda yalnızca `return book_data.model_dump()` var; bu satır yanıtı oluşturmak için veri döndürür. Listeye ekleme işlemini yapacak `books.append(...)` satırı henüz yok. Sonraki deneyde onu ekleyeceğiz.

## Deney 3 — Gelen kitabı listeye ekle

Deney 2'de bilgilerin sunucuya ulaştığını gördük. Şimdi **aynı POST isteği geldiğinde yeni kitabı sunucudaki `books` listesine ekleyeceğiz**. GET fonksiyonları bu listeyi okuduğu için, eklediğimiz kitap daha sonraki GET yanıtlarında da görünecek.

Bu deneyde yalnızca `server.py` değişecek. `client.py` yine kitabı POST ile gönderecek ve ardından GET ile listedeki kitap sayısını okuyacak.

### Ekleme işlemi için fonksiyona yazacağımız satırlar

Aşağıdaki karşılaştırmada `-` ile başlayan satırlar eski kodu, `+` ile başlayan satırlar yeni kodu gösterir. Bu işaretleri Python dosyasına yazma; hemen alttaki tam `server.py` kodunu kullan.

```diff
-@app.post("/book")
-def create_book(book_data: BookCreate):
-    return book_data.model_dump()
+@app.post("/book", status_code=201)
+def create_book(book_data: BookCreate):
+    new_id = 1
+    for book in books:
+        if book["id"] >= new_id:
+            new_id = book["id"] + 1
+
+    new_book = book_data.model_dump()
+    new_book["id"] = new_id
+    books.append(new_book)
+    return new_book
```

| Satır veya bölüm | Ne yapıyor? |
|---|---|
| `status_code=201` | Fonksiyon başarıyla döndüğünde yanıta **201 Created** durum kodunu koyar. Bu kod, isteğin sonucunda yeni kayıt oluşturduğumuzu bildirir. |
| `new_id = 1` ve `for` döngüsü | Yeni kitap için kullanılmamış bir kimlik bulur. Her kitabın kimliğine bakar; `new_id` değerini gerekirse o kimliğin bir fazlasına çıkarır. `42`, `57`, `73` sırasıyla incelendiğinde `new_id` önce `43`, sonra `58`, son olarak `74` olur. |
| `new_book = book_data.model_dump()` | İstekten gelen kitap bilgilerini model nesnesinden Python sözlüğüne dönüştürür. Bu sözlükte henüz `id` yoktur. |
| `new_book["id"] = new_id` | Sunucunun belirlediği kimliği bu sözlüğe ekler. |
| `books.append(new_book)` | `new_book` sözlüğünü `books` listesinin sonuna ekler; üç kitaplık liste dört kitap olur. **Kitabı listeye ekleyen satır budur.** |
| `return new_book` | Eklenen kitabı, kimliğiyle birlikte yanıt olarak döndürür. |

`books`, `server.py` içinde fonksiyonların dışında tanımlanmış listedir. Hem `get_books` hem `create_book` bu listeye erişir. `append`, mevcut listenin içeriğini değiştirir; bu nedenle bu satır için `global books` yazmamız gerekmez.

İstemcideki `new_book` sözlüğü ile sunucudaki `new_book` sözlüğü ayrı programlardadır. Sunucu kendi sözlüğüne `id` eklediğinde istemcinin gönderdiği sözlük değişmez. İstemci yeni kimliği sunucunun gönderdiği **yanıtın içinden** öğrenir. Kitap sayısı dört olurken kimliğin `74` olmasının nedeni, kimliği kitap sayısından değil en büyük mevcut kimlikten hesaplamamızdır.

Burada kimliği, sırayla eklediğimiz birkaç kitap için döngüyle hesaplıyoruz. Veritabanına geçtiğimizde yeni kayıtların kimliklerini veritabanına ürettireceğiz.

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException
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


@app.get("/book")
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


@app.get("/book/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")


@app.post("/book", status_code=201)
def create_book(book_data: BookCreate):
    new_id = 1
    for book in books:
        if book["id"] >= new_id:
            new_id = book["id"] + 1

    new_book = book_data.model_dump()
    new_book["id"] = new_id
    books.append(new_book)
    return new_book
```

Sunucuyu yeniden başlat; Deney 2'deki istemciyi **bir kez** çalıştır.

Beklenen çıktı:

```text
Request method: POST
Request Content-Type: application/json
Status code: 201
Response body: {"title":"HTTP ile Yeni Bir Kitap","author":{"first_name":"Ada","last_name":"Yıldız"},"available":true,"tags":["http","python"],"rating":null,"id":74}
Book count: 4
```

Bu kez yanıt gövdesinde `"id":74` var ve GET ile okuduğumuz liste **4** kitap içeriyor. Sunucu yeni kitaba `74` kimliğini verdi ve `append` satırıyla onu listeye ekledi.

Deney 2’de durum kodunu kodda belirtmemiştik; FastAPI varsayılan olarak `200` göndermişti. Deney 3’te yeni kitap oluşturduğumuz için, bu sonucu istemciye bildirmek amacıyla `@app.post(...)` satırına `status_code=201` yazdık. Kitabı listeye ekleyen satır `books.append(new_book)`; yanıtta `201` gönderilmesini sağlayan ayar ise `status_code=201` ifadesidir. [FastAPI: yanıt durum kodu](https://fastapi.tiangolo.com/tutorial/response-status-code/)

## Deney 4 — Yanıta Location başlığı ekle ve istemcide oku

### Deney 3'te zaten neleri yapabiliyorduk?

Deney 3'te eklediğimiz kitap, sunucudaki `books` listesinde duruyor. Veritabanına yazmadık; ancak bu örnekte sunucu çalıştığı sürece kitaba hem bütün listeyi isteyerek hem de kimliğiyle tek başına erişebiliriz.

Şu üç işlemin görevleri farklıdır:

- `books.append(new_book)`, kitabı sunucudaki listeye ekler.
- `return new_book`, ekleme isteğine cevap olarak kitabın bilgilerini gönderir.
- Daha sonra göndereceğimiz GET isteği, listede duran kitabı yeniden okumamızı sağlar.

Yeni kitabın kimliği `74` ise, **Deney 3'ün sunucusuyla bile** şu istek çalışır:

```python
response = httpx.get("http://127.0.0.1:8000/book/74")
```

Çünkü sunucuda `@app.get("/book/{book_id}")` ile tanımladığımız `get_book` fonksiyonu zaten var. Bu fonksiyon yalnızca son eklenen kitabı değil, kimliğini verdiğimiz herhangi bir kitabı listede arar. Deney 4'te yeni bir GET yolu veya kitap arama fonksiyonu eklemeyeceğiz.

### Bu deneyin amacı: yanıt başlığı eklemek ve okumak

Sunucu yeni kitaba `74` kimliğini veriyor. İstemci `/book` yolunu zaten biliyor; kimliği de yanıt gövdesindeki `"id": 74` alanından öğrenip `/book/74` yolunu kendisi oluşturabilir. Biz bu deneyde aynı yolu `Location` başlığında da göndererek **sunucuda yanıt başlığı eklemeyi ve istemcide bu başlığı okumayı** öğreniyoruz. Kitaba erişmek için bu başlığı kullanmak zorunlu değildir.

Kitap ekleme işlemi aynı kalacak. İlk eklemenin HTTP/1.1 yanıtı aşağıdaki gibi görünür; tarih ve saat örnektir:

```http
HTTP/1.1 201 Created
date: Tue, 22 Sep 2026 09:00:00 GMT
server: uvicorn
content-length: 152
content-type: application/json
location: /book/74

{"title":"HTTP ile Yeni Bir Kitap","author":{"first_name":"Ada","last_name":"Yıldız"},"available":true,"tags":["http","python"],"rating":null,"id":74}
```

İlk satır **durum satırı**, sonraki beş satır **başlıklar**, boş satır **ayırıcı**, son satır ise **yanıt gövdesidir**. `date` yanıtın zamanını, `server` sunucu yazılımını, `content-length` gövdenin bayt cinsinden uzunluğunu, `content-type` ise gövdenin JSON biçiminde olduğunu bildirir.

Bu beş başlıktan `Location` başlığını kodda biz ekleyeceğiz; diğerlerini FastAPI ve Uvicorn hazırlayacak. [HTTP standardı: Location](https://www.rfc-editor.org/rfc/rfc9110.html#section-10.2.2)

POST yanıtı kitabın bilgilerini zaten içerir. Bu deneyde başlıktan okuduğumuz yola ayrıca GET göndererek kitabı yeniden okuyacağız. Bu adım, başlığı nasıl kullandığımızı görmek içindir; kitap ekleme işleminin zorunlu bir parçası değildir.

### İstek başlığı ile yanıt başlığını ayır

| Başlık | Kim gönderiyor? | Bu örnekte ne bildiriyor? |
|---|---|---|
| `Content-Type: application/json` | İstemci, POST **isteğinde** | “Gönderdiğim kitap bilgileri JSON biçiminde.” Deney 2'de HTTPX bunu eklemişti. |
| `Location: /book/74` | Sunucu, POST **yanıtında** | “Oluşturduğum kitaba bu yoldan ulaşabilirsin.” Şimdi bu başlığı ekleyeceğiz. |

### `server.py`: yanıta Location başlığını ekle

Aşağıdaki fark gösterimi değişen satırları gösterir. `...`, aradaki mevcut kodun devam ettiğini belirtir; bunu dosyana yazma. Hemen altında kopyalayabileceğin tam `server.py` var.

```diff
-from fastapi import FastAPI, HTTPException
+from fastapi import FastAPI, HTTPException, Response

 @app.post("/book", status_code=201)
-def create_book(book_data: BookCreate):
+def create_book(book_data: BookCreate, response: Response):
     ...
     books.append(new_book)
+    response.headers["Location"] = f"/book/{new_id}"
     return new_book
```

`from fastapi import ... Response` satırıyla FastAPI'nin `Response` sınıfını alıyoruz. `create_book` içindeki iki parametrenin görevi farklıdır:

| Parametre | Nereden gelir, ne için kullanılır? |
|---|---|
| `book_data: BookCreate` | FastAPI'nin istek gövdesinden okuyup kontrol ettiği kitap bilgilerini taşır. Bu bilgilerle yeni kaydı oluştururuz. |
| `response: Response` | FastAPI'nin, göndereceğimiz yanıtı hazırlamak için fonksiyona verdiği nesnedir. Burada `headers` üzerinden `Location` başlığını ekleriz. İstemci `response` adlı bir alan göndermez. |

Burada büyük harfle başlayan `Response` sınıfın adı, küçük harfli `response` ise fonksiyon içinde kullandığımız parametrenin adıdır. `response.headers["Location"] = ...` başlığı ayarlar; `return new_book` yine JSON gövdesini belirler. FastAPI ikisini aynı HTTP yanıtında gönderir. [FastAPI: yanıt başlıkları](https://fastapi.tiangolo.com/advanced/response-headers/)

`f"/book/{new_id}"`, `new_id` değerini metne yerleştirir: değer `74` ise sonuç `"/book/74"` olur. Burada belirli bir kitap için yol metni oluşturuyoruz. `@app.get("/book/{book_id}")` ise farklı kimliklerle gelen GET isteklerini karşılayan yol tanımıdır.

<a id="final-server"></a>

### `server.py` dosyasının tamamı

`server.py` içeriğini aşağıdaki kodla değiştir.

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


@app.get("/book")
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


@app.get("/book/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")


@app.post("/book", status_code=201)
def create_book(book_data: BookCreate, response: Response):
    new_id = 1
    for book in books:
        if book["id"] >= new_id:
            new_id = book["id"] + 1

    new_book = book_data.model_dump()
    new_book["id"] = new_id
    books.append(new_book)
    response.headers["Location"] = f"/book/{new_id}"
    return new_book
```

### `client.py`: verilen adrese GET isteği gönder

Bu istemci, ekleme yanıtından kitabın adresini okuyacak ve o adrese GET gönderecek. Sonunda da önceki deneydeki gibi bütün listeyi isteyip kitap sayısını kontrol edecek.

<a id="final-client"></a>

### `client.py` dosyasının tamamı

`client.py` içeriğini aşağıdaki kodla değiştir.

```python
import httpx

base_url = "http://127.0.0.1:8000"

new_book = {
    "title": "HTTP ile Yeni Bir Kitap",
    "author": {
        "first_name": "Ada",
        "last_name": "Yıldız"
    },
    "available": True,
    "tags": ["http", "python"],
    "rating": None
}

try:
    response = httpx.post(base_url + "/book", json=new_book)
    print("Status code:", response.status_code)

    if response.status_code == 201:
        location = response.headers["Location"]
        print("Location:", location)

        read_response = httpx.get(base_url + location)
        print("Read status:", read_response.status_code)
        if read_response.status_code == 200:
            book = read_response.json()
            print("Book id:", book["id"])
            print("Book title:", book["title"])
        else:
            print("Response body:", read_response.text)
    else:
        print("Response body:", response.text)

    list_response = httpx.get(base_url + "/book")
    if list_response.status_code == 200:
        print("Book count:", len(list_response.json()))
    else:
        print("List status:", list_response.status_code)
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

### İstemci kodu hangi sırayla çalışıyor?

Başarılı akışta istemci **üç ayrı HTTP isteği** gönderir:

| Sıra | İstek | Amacı |
|---|---|---|
| 1 | `POST /book` | Kitabı eklemek ve yanıtın `Location` başlığını okumak. |
| 2 | `GET /book/74` | Başlıktan okuduğumuz yolu kullanarak o kitabı istemek. |
| 3 | `GET /book` | Önceki deneydeki gibi toplam kitap sayısını kontrol etmek. |

İstemci önce POST yapacak. Yanıt `201` ise `response.headers["Location"]` ile sunucunun verdiği yolu okuyacak. `base_url + location`, sunucu adresiyle bu yolu birleştirir: `http://127.0.0.1:8000` + `/book/74` → `http://127.0.0.1:8000/book/74`.

Ardından `httpx.get(base_url + location)` satırı kitabı okumak için **yeni bir istek** gönderecek. `201` yanıtındaki `Location` başlığı kendi başına GET isteği göndermez; bu adımı istemcide biz yazıyoruz. Sondaki `GET /book` ile de katalogdaki toplam kitap sayısını kontrol edeceğiz.

İstemcide her yanıtı ayrı bir değişkende tutuyoruz; böylece hangi isteğin sonucunu okuduğumuz bellidir:

| İstemcideki değişken | Tuttuğu yanıt |
|---|---|
| `response` | Kitap eklemek için gönderilen POST'un yanıtı. `201` kodunu ve `Location` başlığını buradan okuruz. |
| `read_response` | `GET /book/74` yanıtı **tek bir kitap** içerir. JSON'u okuduktan sonra `book["title"]` ile başlığı alırız. |
| `list_response` | `GET /book` yanıtı **kitap listesi** içerir. `len(list_response.json())` ile bu listedeki kitap sayısını buluruz. |

`response.text`, alınmış yanıtın gövdesini metin olarak verir. `response.json()` aynı gövdeyi Python'da kullanabileceğimiz sözlük veya listeye çevirir. **İkisi de yeni HTTP isteği göndermez**; yeni istekleri `httpx.post(...)` ve `httpx.get(...)` satırları gönderir. [HTTPX: yanıt gövdesini okuma](https://www.python-httpx.org/quickstart/#response-content)

Sunucudaki `response` parametresi ile istemcideki `response` değişkeni ayrı programlardadır. Sunucuda bir başlık **yazıyoruz**; istemcide HTTPX'in aldığı yanıttan bu başlığı **okuyoruz**. İsimlerinin aynı olması bu iki nesneyi ortak yapmaz.

Üç kitapla başlamak için sunucuyu yeniden başlat; istemciyi **bir kez** çalıştır.

Beklenen çıktı:

```text
Status code: 201
Location: /book/74
Read status: 200
Book id: 74
Book title: HTTP ile Yeni Bir Kitap
Book count: 4
```

| Çıktı | Bu deneyde neyi gösteriyor? |
|---|---|
| `Status code: 201` | POST isteğiyle kitap oluşturulduğunu bildirir. Bu kodu Deney 3'te `status_code=201` ile belirlemiştik. |
| `Location: /book/74` | İstemcinin yanıtın `Location` başlığından okuduğu yoldur. |
| `Read status: 200` | Bu yola gönderdiğimiz ayrı GET isteğinin kitabı bulduğunu gösterir. |
| `Book id: 74`, `Book title: HTTP ile Yeni Bir Kitap` | İkinci isteğin yanıtından okuduğumuz kitabın kimliği ve başlığıdır. |
| `Book count: 4` | Son GET isteğiyle aldığımız listede toplam dört kitap olduğunu gösterir. |

![Kitap ekleme ve ayrı bir GET ile geri okuma](Gorseller/01_kitap_ekleme_akisi.svg)

Şema, POST isteğini ve verilen adrese gönderilen GET isteğini gösterir. İstemci en son kitap sayısını kontrol etmek için bir `GET /book` isteği daha gönderir.

## Deney 5 — Başlık gönderilmezse ne olur?

Sunucunun eksik bilgiyle kitap ekleyip eklemediğini kontrol edeceğiz. `BookCreate` modelinde `title: str` yazmıştık. Bu alan için varsayılan değer vermediğimizden istemcinin başlığı göndermesi gerekiyor. Aşağıdaki istemcide yalnızca `title` alanını çıkarıyoruz; JSON'un yazımı geçerli, fakat kitap bilgisi eksik olacak.

**`server.py` Deney 4'teki haliyle kalacak.** Sunucuyu yeniden başlatıp üç kitapla başla. `client.py` içeriğini aşağıdaki kodla değiştir. İstemci eksik bilgili bir POST gönderecek, sonra GET ile kitap sayısına bakacak; bu sayede başarısız isteğin listeyi değiştirip değiştirmediğini göreceğiz.

### `client.py` dosyasının tamamı

```python
import httpx

new_book = {
    "author": {
        "first_name": "Ada",
        "last_name": "Yıldız"
    },
    "available": True,
    "tags": ["http", "python"],
    "rating": None
}

try:
    response = httpx.post(
        "http://127.0.0.1:8000/book",
        json=new_book
    )
    list_response = httpx.get("http://127.0.0.1:8000/book")
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
else:
    print("Request method:", response.request.method)
    print("Request Content-Type:", response.request.headers.get("Content-Type"))
    print("Status code:", response.status_code)
    print("Response body:", response.text)
    if list_response.status_code == 200:
        print("Book count:", len(list_response.json()))
    else:
        print("List status:", list_response.status_code)
```

Bu istemciyi çalıştırdığında POST yanıtının durum kodu **422** olur. **422, sunucunun isteği aldığı ancak gönderilen bilgiler beklenen koşulları karşılamadığı için işleyemediği anlamına gelen HTTP durum kodudur.** Bu istekte eksik olan bilgi kitap başlığıdır. Kitap sayısı **3** kalır; sebebini yanıt gövdesinden de okuyabiliriz.

`Response body` satırında, `detail` adlı listenin içinde bir hata açıklaması bulunur. Aşağıda bu açıklamanın ilgili alanları gösteriliyor; çıktında `input` gibi ek alanlar da olabilir:

```json
{
  "type": "missing",
  "loc": ["body", "title"],
  "msg": "Field required"
}
```

| Hata bilgisindeki bölüm | Bu istekte ne söylüyor? |
|---|---|
| `loc: ["body", "title"]` | Eksik bilgi, isteğin gövdesindeki `title` alanı. |
| `msg: "Field required"` | Bu alanı göndermelisin. |
| `type: "missing"` | Hatanın türü: eksik alan. |

**Bu `422` yanıtını FastAPI oluşturur; fonksiyonumuza hata kodu yazmamız gerekmedi.** FastAPI, `create_book` fonksiyonunu çağırmadan önce gövdeyi Pydantic ile `BookCreate` modeline göre kontrol eder. Eksik `title` nedeniyle kontrol başarısız olur ve FastAPI `422` yanıtını gönderir. **`create_book` çağrılmadığından** kimlik hesaplayan kod ve `books.append(...)` çalışmaz; kitap sayısı üç kalır. [FastAPI: istek doğrulama hataları](https://fastapi.tiangolo.com/tutorial/handling-errors/#override-request-validation-exceptions)

Model, alanların türlerini de kontrol eder; ancak bu deneyde yalnızca zorunlu bir alanın eksik olmasını denedik. Başlığın boş olmaması veya puanın belirli aralıkta olması gibi ek kuralları beşinci haftada yazacağız.

## Deney 6 — Aynı isteği tekrar gönder ve sunucuyu yeniden başlat

Önce aynı POST istemcisini iki kez çalıştırıp aynı bilgilerle iki kayıt oluştuğunu göreceğiz. Ardından sunucuyu yeniden başlatıp eklenen kayıtların hâlâ bulunup bulunmadığını GET ile kontrol edeceğiz.

**`server.py` Deney 4'teki haliyle kalacak.** `client.py` içeriğini aşağıdaki kodla değiştir. Bu, Deney 4'teki geçerli kitap gönderen istemcidir; `title` alanı yeniden vardır.

### `client.py` dosyasının tamamı

```python
import httpx

base_url = "http://127.0.0.1:8000"

new_book = {
    "title": "HTTP ile Yeni Bir Kitap",
    "author": {
        "first_name": "Ada",
        "last_name": "Yıldız"
    },
    "available": True,
    "tags": ["http", "python"],
    "rating": None
}

try:
    response = httpx.post(base_url + "/book", json=new_book)
    print("Status code:", response.status_code)

    if response.status_code == 201:
        location = response.headers["Location"]
        print("Location:", location)

        read_response = httpx.get(base_url + location)
        print("Read status:", read_response.status_code)
        if read_response.status_code == 200:
            book = read_response.json()
            print("Book id:", book["id"])
            print("Book title:", book["title"])
        else:
            print("Response body:", read_response.text)
    else:
        print("Response body:", response.text)

    list_response = httpx.get(base_url + "/book")
    if list_response.status_code == 200:
        print("Book count:", len(list_response.json()))
    else:
        print("List status:", list_response.status_code)
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

### Sunucu çalışırken istemciyi iki kez çalıştır

1. Sunucuyu yeniden başlatarak üç kitapla başla.
2. İstemciyi çalıştır. POST ile `74` kimlikli kitap eklenir ve kitap sayısı **4** olur. İstemci çıktıyı yazdırıp kapanır.
3. Sunucuyu açık bırakıp istemciyi tekrar çalıştır. Yeni bir POST gönderilir; bu kez `75` kimlikli kitap eklenir ve kitap sayısı **5** olur.

İkinci çalıştırmanın çıktısı:

```text
Status code: 201
Location: /book/75
Read status: 200
Book id: 75
Book title: HTTP ile Yeni Bir Kitap
Book count: 5
```

`client.py` her çalıştırıldığında baştan başlar ve kodundaki POST isteğini yeniden gönderir. Sunucudaki `create_book` da her geçerli POST'ta yeni kimlik hesaplayıp bir kayıt ekler. Başlığı ve yazarı aynı olan kitapları birleştiren bir kural yazmadık. Bu nedenle aynı bilgilerle **iki ayrı kayıt** oluşur: `74` ve `75`.

İlk istemci kapanmasına rağmen `74` kimlikli kitap kaybolmadı. Çünkü `books` listesi sunucu programındadır ve sunucu çalışmaya devam etmektedir. Sonraki istemci çalışması, sunucuda duran aynı listeye bir kitap daha ekler.

### Sunucuyu yeniden başlatınca listeyi kontrol et

Şimdi **yalnızca `client.py` dosyasını** aşağıdaki GET istemcisiyle değiştir. POST istemcisini kullanmaya devam etseydik her kontrolde bir kitap daha eklerdik. Bu istemci yalnızca mevcut listeyi okuyacak.

### `client.py` dosyasının tamamı

```python
import httpx

try:
    response = httpx.get("http://127.0.0.1:8000/book")
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
else:
    print("Status code:", response.status_code)
    if response.status_code == 200:
        books = response.json()
        print("Book count:", len(books))
        for book in books:
            print(book["id"], "-", book["title"])
    else:
        print("Response body:", response.text)
```

1. Sunucuyu yeniden başlatmadan GET istemcisini çalıştır: **5** kitap görmelisin.
2. Sunucuyu yeniden başlat.
3. Aynı GET istemcisini tekrar çalıştır: başlangıçtaki **3** kitap görünür.

Son çıktı:

```text
Status code: 200
Book count: 3
42 - API Yolculuğu
57 - Veriyle İlk Adımlar
73 - Python ile Web API
```


## Ek çalışma — Aynı kitabı Postman ile gönder

Şimdi `client.py` yerine Postman kullanarak aynı POST isteğini göndereceğiz. Postman, adresi, metodu ve gövdeyi arayüzünden seçerek HTTP isteği hazırladığımız bir uygulamadır. Sunucu açısından isteğin Python programından veya Postman'dan gelmesi işlemi değiştirmez.

`server.py`, Deney 4'teki haliyle VS Code terminalinde çalışmaya devam etsin.

Postman'ın web sürümü de vardır; bu derste yardımcı program ve tarayıcı bağlantı ayarlarıyla uğraşmadan istek göndermek için **masaüstü uygulamasını** kullanacağız. Kurulu değilse [resmî indirme sayfasından](https://www.postman.com/downloads/) işletim sistemine uygun sürümü indirip kur, ardından uygulamayı aç. [Postman'ın başlangıç yönergesi](https://learning.postman.com/docs/getting-started/quick-start/) yeni isteğin nereden açıldığını gösterir.

Hesap açma ekranı gelirse **Without an account…** bölümündeki **Open Lightweight API Client** düğmesine tıkla; bu deney için hesap açman gerekmez.

Sunucuyu yeniden başlatarak üç kitapla başla, sonra Postman'da:

1. Yeni bir **HTTP isteği** aç.
2. Adresin yanındaki metot seçimini **POST** yap; adresi `http://127.0.0.1:8000/book` yaz.
3. **Body → raw → JSON** seç. Aşağıdaki JSON'u gövde alanına yapıştır.

```json
{
  "title": "HTTP ile Yeni Bir Kitap",
  "author": {
    "first_name": "Ada",
    "last_name": "Yıldız"
  },
  "available": true,
  "tags": [
    "http",
    "python"
  ],
  "rating": null
}
```

4. İsteği hazırladığın bölümdeki **Headers** sekmesinde `Content-Type: application/json` bulunduğunu kontrol et. **raw → JSON** seçimi bu istek başlığını ekler. [Postman: istek gövdesi](https://learning.postman.com/docs/use/send-requests/create-requests/parameters/#raw-data)
5. **Send** düğmesine **bir kez** bas. Gelen yanıtın durum kodu `201`, JSON gövdesindeki `id` değeri `74` olmalı. Bu kez **yanıtın Headers bölümüne** bak: `Location` değeri `/book/74` olmalı. İsteğin Headers sekmesi gönderdiğin, yanıtın Headers bölümü ise sunucudan gelen başlıkları gösterir.
6. Yeni bir HTTP isteği aç. Metodu **GET**, adresi `http://127.0.0.1:8000/book/74` yap ve **Send** düğmesine bas. Eklenen kitabı `200` yanıtıyla görmelisin.

Postman'a JSON yazdığımız için `true` ve `null` kullandık. Python sözlüğünde bunlar `True` ve `None` idi; HTTPX onları JSON'a çeviriyordu. Sunucu iki istekte de aynı kitap bilgilerini alır.

POST isteğinin **Send** düğmesine yeniden basarsan Deney 6'daki gibi bir kitap daha eklenir. GET isteğini tekrar göndermek ise kitap eklemez; mevcut kaydı okur.

![Postman'da POST /book isteği ve 201 Created yanıtı](Gorseller/03_postman_book_created.png)

*Bu ekran örneğinde birkaç kez kitap eklendiği için yeni kitabın kimliği `77` olmuştur.*

## Ek çalışma — Yol var ama metot desteklenmiyorsa

**Bu deneyin amacı**, istemcide `httpx.delete(...)` yazmanın kitabı kendiliğinden silmediğini görmektir. İstemci silme isteği gönderir; işlemin gerçekleşmesi için sunucuda bu isteği karşılayan bir fonksiyon ve kitabı listeden çıkaran kod bulunmalıdır. Adresin yanında **GET veya DELETE gibi metot seçimi de hangi işlemin yapılacağını belirler.**

Sunucumuzda `@app.get("/book/{book_id}")` ile okuma işlemi tanımlı; aynı yol için DELETE işlemi tanımlamadık. Şimdi GET ile okuyabildiğimiz `/book/42` yoluna DELETE gönderip sonucu göreceğiz.

**`server.py` değişmeyecek.** Sunucu çalışırken `client.py` içeriğini aşağıdaki kodla değiştir. Silme kodunu dördüncü haftada yazacağız.

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.delete("http://127.0.0.1:8000/book/42")
print("Status code:", response.status_code)
print("Response body:", response.text)
```

Bu DELETE isteğinin beklenen yanıtı:

```text
Status code: 405
Response body: {"detail":"Method Not Allowed"}
```

**405 Method Not Allowed**, bu adreste gönderdiğimiz HTTP metodunun desteklenmediğini bildirir. Sunucu DELETE isteğini GET fonksiyonuna yönlendirmez; `get_book` çalışmaz ve kitap silinmez. Aynı adrese GET gönderirsek kitabı yine okuyabiliriz. [HTTP standardı: 405](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.5.6)

Bu uygulamada iki hata farklı yerde oluşur: `GET /book/999` isteğinde `get_book` çalışır, kitabı bulamaz ve kodumuzdaki **404** yanıtını verir. `DELETE /book/42` isteğinde ise bu metodu karşılayan fonksiyon olmadığı için sunucu **405** yanıtını verir.

Bu ek çalışmadan sonra kitap listesini görmek için Deney 6'nın sonundaki tam GET istemcisini `client.py` dosyasına geri koy.

## Kendini kontrol et

1. Deney 2'de kitap bilgileri yanıtta geldiği halde kitap sayısı neden artmadı?
2. Kaydı gerçekten ekleyen satır hangisi? `201` hangi bilgiyi bildiriyor?
3. `Location: /book/74` hangi mesajda gelir ve istemci bu bilgiyle ne yapar?
4. `title` eksik olduğunda `422` yanıtını kim oluşturur? `books.append(...)` neden çalışmaz?
5. Aynı POST istemcisini iki kez çalıştırınca neden iki kayıt oluşur? Sunucuyu yeniden başlatınca bu kayıtlar neden kaybolur?

**Cevaplarını karşılaştır:**

1. Deney 2'deki fonksiyon yalnızca aldığı bilgileri geri döndürür; listeye ekleyen satır henüz yoktur.
2. Kaydı `books.append(new_book)` ekler. `201`, istemciye yeni kayıt oluşturulduğunu bildirir.
3. `Location`, POST yanıtının başlığıdır. İstemci bu yolu sunucu adresiyle birleştirip kitabı okumak için GET gönderir.
4. Eksik başlığı model kontrolü yakalar; FastAPI `422` yanıtını oluşturur. `create_book` çağrılmadığından içindeki ekleme satırı çalışmaz.
5. İstemci her çalışmada yeni POST gönderir ve sunucu her geçerli POST'ta yeni kayıt ekler. Kayıtlar yalnızca çalışan sunucunun belleğinde tutulduğu için sunucu yeniden başladığında başlangıçtaki listeye dönülür.

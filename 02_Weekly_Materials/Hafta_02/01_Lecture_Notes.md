# Week 02 — Lecture Notes

## İstemciden yeni kitap göndermek: HTTP isteği, gövde ve yanıt

İlk hafta sunucudaki kitapları istedik, aradık ve filtreledik. Kitap bilgileri `server.py` içindeki `books` listesinde hazırdı. Bu hafta şu soruyla ilerliyoruz: **Sunucu çalışırken, `server.py` dosyasını elle değiştirmeden yeni bir kitabı istemciden nasıl ekleriz?**

Örneğimizde başlangıçta 42, 57 ve 73 numaralı üç kitap var. Kitap eklemek için önce bilgiyi sunucuya gönderecek, sonra sunucudaki kodun bu bilgiyle ne yaptığını gözleyeceğiz.

Bu not, [Practice](02_Practice.md) içindeki deneylerin anlamını toparlar. Aşağıdaki kodlar ilgili satırları gösterir; çalıştırılacak dosyaların tam sürümleri Practice içindedir.

## 1. Aynı adreste farklı işlemler yapabiliriz

İlk haftadan bildiğimiz iki istek var:

| İstek | Bu uygulamada yaptığı iş |
|---|---|
| `GET /book` | Kitap listesini ister. |
| `GET /book/42` | 42 numaralı kitabı ister. |

**GET**, HTTP isteğinin metodudur; istemcinin hangi tür işlem istediğini belirtir. Bu hafta yeni kitabın bilgilerini **POST** metoduyla göndereceğiz.

```python
@app.get("/book")
def get_books(search: str = "", available: bool | None = None):
    # Listeleme ve filtreleme kodu burada çalışır.
    ...

@app.post("/book")
def create_book(book_data: BookCreate):
    # Yeni kitapla ilgili kod burada çalışır.
    ...
```

Bu parça, GET ve POST isteklerini ayrı fonksiyonlarla eşleştirdiğimizi gösterir; `...` yerlerinde Practice'teki işlem kodları bulunur.

**FastAPI fonksiyonu seçerken hem metoda hem yola bakar.** Yol ikisinde de `/book` olsa da GET isteği `get_books`, POST isteği `create_book` ile karşılanır. Fonksiyon adını istemciden göndermeyiz.

POST yazmak, kitabın kendiliğinden ekleneceği anlamına gelmez. Gönderilen bilgiyi alacak ve listeye ekleyecek sunucu kodunu da yazmalıyız.

## 2. Arama ölçütü ile yeni kitabın bilgileri nereye yazılır?

Arama yaparken bir ölçüt gönderiyorduk:

```python
response = httpx.get(
    "http://127.0.0.1:8000/book",
    params={"search": "API"}
)
```

`params=`, HTTPX'in sorgu parametresi göndermek için kullandığı seçenektir. İsteğin adresi `/book?search=API` olur. Sunucu başlığında “API” geçen mevcut kitapları arar.

Yeni kitap eklerken ise kitabın alanlarını göndeririz:

```python
new_book = {
    "title": "HTTP ile Yeni Bir Kitap",
    "author": {"first_name": "Ada", "last_name": "Yıldız"},
    "available": True,
    "tags": ["http", "python"],
    "rating": None
}

response = httpx.post(
    "http://127.0.0.1:8000/book",
    json=new_book
)
```

Buradaki `new_book`, istemcide oluşturduğumuz **Python sözlüğüdür**. HTTPX, `json=new_book` sayesinde bunu JSON biçimine dönüştürüp **isteğin gövdesine** koyar. Gövde, bu istekte kitap bilgilerini taşıyan bölümdür. Adres yine `/book` olarak kalır.

| Kodda | Gönderilen HTTP isteğinde |
|---|---|
| `httpx.post(...)` | Metot: `POST` |
| Adresin `/book` bölümü | Yol: `/book` |
| `json=new_book` | Gövde: yeni kitabın JSON biçimindeki bilgileri |
| HTTPX'in eklediği `Content-Type: application/json` | Gövdenin JSON olduğunu belirten başlık |

Python'daki `True` ve `None`, gönderilen JSON içinde `true` ve `null` olur. İstemci bir Python değişkenini sunucuyla paylaşmaz; değişkendeki bilgileri bir mesaj içinde gönderir. [HTTPX'in JSON gönderme örnekleri](https://www.python-httpx.org/quickstart/#sending-json-encoded-data) bu kullanımı gösterir.

**İstek gövdesi** istemciden sunucuya gider. **Yanıt gövdesi** sunucudan istemciye gelir. İkisinde de JSON bulunabilir; hangi taraftan gönderildiğine göre adlandırırız.

## 3. Sunucu gönderilen alanlardan ne bekliyor?

İstemcinin göndereceği yeni kitap için bir **veri modeli** tanımlıyoruz. Burada model, hangi alanları ve hangi türde değerleri beklediğimizi kodla belirtir.

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

**Pydantic**, bu alanları kontrol etmeyi sağlayan Python kütüphanesidir. `BaseModel` onun sunduğu bir sınıftır. `class BookCreate(BaseModel)` yazarak alanlarımızı Pydantic'in okuyup kontrol edebileceği bir model tanımlarız.

| Tanım | Bu kitap için anlamı |
|---|---|
| `title: str` | Kitap başlığını metin olarak bekleriz. |
| `author: Author` | Yazar bilgisinde `first_name` ve `last_name` alanlarını bekleriz. |
| `available: bool` | Kitabın okuyucuya verilip verilemeyeceğini belirten mantıksal değer bekleriz. |
| `tags: list[str]` | Metinlerden oluşan bir etiket listesi bekleriz; `[]` da uygundur. |
| `rating: float \| None = None` | Puan bir sayı veya değeri belirtilmemiş olabilir. Alan gönderilmezse `None` kullanılır. |

`rating` dışındaki alanların varsayılan değeri yoktur; bu modelde bunların gönderilmesi gerekir. `rating` satırındaki iki parça farklı işler yapar: **`| None` değerin `None` olabilmesine, `= None` alanın gönderilmeden bırakılabilmesine izin verir.**

İstemciden `id` istemiyoruz. Yeni kitabın kimliğini, mevcut kitaplarla çakışmayacak biçimde sunucu belirleyecek.

Modeli isteği karşılayacak fonksiyona bağlayan satır şudur:

```python
def create_book(book_data: BookCreate):
```

FastAPI bu tanımı okuyarak istek gövdesini `BookCreate` modeline göre Pydantic ile kontrol eder. Kontrol başarılıysa fonksiyon çalışır; `book_data` içinde kontrol edilmiş model nesnesi bulunur. Bu davranış [FastAPI'nin istek gövdesi işleyişinin](https://fastapi.tiangolo.com/tutorial/body/) parçasıdır.

**Python'da bir parametrenin yanına tür yazmak, tek başına bu kontrolleri çalıştırmaz.** Bu örnekte tür bildirimlerini okuyup kontrolü yapan FastAPI ve Pydantic'tir. Bazı uygun değerleri türler arasında dönüştürebilirler; her farklı yazımın mutlaka reddedileceğini varsaymayız.

## 4. Bilgiyi almak, listeye eklemek ve yanıt vermek ayrı işlerdir

İlk POST deneyinde yalnızca gönderilen bilgiyi geri döndürüyoruz:

```python
@app.post("/book")
def create_book(book_data: BookCreate):
    return book_data.model_dump()
```

`model_dump()`, Pydantic modelindeki alanları Python sözlüğü olarak verir. İçindeki `author` modeli de sözlüğe dönüştürülür. FastAPI bu sonucu JSON yanıtı olarak istemciye gönderir. [Pydantic model belgeleri](https://docs.pydantic.dev/latest/concepts/models/#model-methods) bu metodu açıklar.

Bu kodda `books` listesine ekleme yapılmaz. Yanıtta gönderdiğimiz kitabı görmek, kitabın sunucudaki listeye eklendiğini kanıtlamaz. GET ile listeyi yeniden istediğimizde hâlâ üç kitap vardır. Bu ilk sürümün yanıt kodu `200` olur.

Sonraki deneyde, POST fonksiyonunun içine aşağıdaki işlemleri ekleriz:

```python
new_id = 1
for book in books:
    if book["id"] >= new_id:
        new_id = book["id"] + 1

new_book = book_data.model_dump()
new_book["id"] = new_id
books.append(new_book)
return new_book
```

| Satır veya işlem | Etkisi |
|---|---|
| Döngüyle `new_id` hesabı | Listedeki en büyük kimliğin bir fazlasını bulur. 42, 57 ve 73 için sonuç 74'tür. |
| `new_book = book_data.model_dump()` | Gelen modelin bilgilerini sözlüğe dönüştürür. |
| `new_book["id"] = new_id` | Yeni kimliği bu sözlüğe ekler. |
| `books.append(new_book)` | Kitabı sunucunun belleğindeki listeye ekler. |
| `return new_book` | Eklenen kitabın bilgilerini yanıt olarak gönderir. |

**Listeyi değiştiren satır `books.append(new_book)` satırıdır.** `return`, sonucu istemciye iletmek için kullanılır. İstemcideki `new_book` ile sunucudaki `new_book` aynı değişken değildir; ayrı programların kendi değişkenleridir.

## 5. `201` ve `Location` neyi bildirir?

Kitabı gerçekten ekleyen sürümde, başarılı yanıtın durum kodunu açıkça seçeriz:

```python
@app.post("/book", status_code=201)
```

**`201 Created`**, isteğin sonucunda yeni bir kaynak oluşturulduğunu bildirir. Bizim örneğimizde bu kaynak, yeni kitap kaydıdır. Bu sayı kitabı ekleyen komut değildir; ekleme işini fonksiyonun içindeki kod yapar.

İstemcinin eklenen kitabı daha sonra isteyebilmesi için yanıtın `Location` başlığına kitabın yolunu da yazabiliriz:

```python
from fastapi import Response

# POST fonksiyonunun parametreleri:
def create_book(book_data: BookCreate, response: Response):
    # Kimlik belirleme ve listeye ekleme kodundan sonra:
    response.headers["Location"] = f"/book/{new_id}"
    return new_book
```

Bu, fonksiyonun yalnızca ilgili kısmını gösterir. `response` parametresini `Response` türüyle tanımladığımızda FastAPI bu parametreye yanıt başlıklarını düzenleyebileceğimiz bir nesne verir. Başlık eklemek [FastAPI'de bu şekilde yapılır](https://fastapi.tiangolo.com/advanced/response-headers/).

İlk kitap eklenince yanıtın üç parçasını ayrı ayrı okuyabiliriz:

| Yanıtın parçası | Örnekteki bilgi |
|---|---|
| Durum kodu | `201`: yeni kitap oluşturuldu. |
| `Location` başlığı | `/book/74`: yeni kitabın yolu. |
| Gövde | `id` değeri 74 olan kitabın JSON bilgileri. |

`Location`, JSON içindeki bir kitap alanı değildir; yanıt başlığıdır. İstemcide `response.headers["location"]` ile okunur. HTTP başlık adlarında büyük/küçük harf farkı bu erişimi değiştirmez.

```python
base_url = "http://127.0.0.1:8000"

if response.status_code == 201:
    location = response.headers["location"]
    saved_response = httpx.get(base_url + location)
    print(saved_response.json())
```

Buradaki `response`, istemcinin önceki POST isteğine aldığı yanıttır; sunucuda başlığını düzenlediğimiz nesneyle aynı Python nesnesi değildir. `/book/74` yolunu sunucu adresiyle birleştirip **ikinci bir istek** gönderiyoruz. Bu GET isteği yeni kitap eklemez; daha önce eklenen kitabı ister.

`201` yanıtındaki `Location` otomatik yönlendirme yapmaz. Kitabı tekrar isteyen işlem, bizim yazdığımız `httpx.get(...)` satırıdır.

![Kitap bilgilerinin POST ile gönderilmesi, listeye eklenmesi, 201 yanıtı ve ayrı bir GET ile geri okunması](Gorseller/01_kitap_ekleme_akisi.svg)

## 6. Başlık alanı gönderilmezse ne olur?

Gönderdiğimiz kitaptan `title` alanını çıkardığımızı düşünelim. `BookCreate` bu alanı zorunlu tuttuğu için FastAPI `422` yanıtı verir.

**`422`, sunucunun isteği aldığı ancak gönderilen bilgiler beklenen koşulları karşılamadığı için işleyemediği anlamına gelen HTTP durum kodudur.** Bu örnekte eksik olan bilgi kitap başlığıdır.

Kontrol POST fonksiyonu çalışmadan yapılır. Dolayısıyla `create_book` içindeki `books.append(...)` satırına ulaşılmaz; listeye yeni kitap eklenmez. Yanıt gövdesindeki hata bilgisi, sorunun gövdedeki `title` alanıyla ilgili olduğunu gösterir.

| Durum | Bu uygulamada gözlenecek sonuç |
|---|---|
| Kitap bilgileri modele uygun | POST fonksiyonu çalışır; ekleme sürümünde kitap listeye eklenir. |
| `title` alanı eksik | `422`; POST fonksiyonu çalışmaz. |
| `available` değeri `"belki"` | Mantıksal değere dönüştürülemediği için `422`. |

Bir alanın bulunması ve beklenen türde olması, her uygulama kuralının kontrol edildiği anlamına gelmez. Örneğin bu model puanın 0–5 arasında olmasını istemiyor; böyle bir kuralı ayrıca yazmak gerekir. Ayrıntılı doğrulamayı sonraki haftalarda ele alacağız.

## 7. Aynı POST isteğini yeniden gönderirsek ne olur?

Kitap ekleyen bu uygulamada, aynı bilgilerle yapılan her başarılı POST yeni bir kayıt ekler. Üç kitapla başlayan sunucuda ilk istek 74, ikinci istek 75 numaralı kitabı oluşturur. Çünkü kod her istekte yeni kimlik hesaplayıp `append` çalıştırır.

Bu hafta aynı başlıkta kitabın zaten bulunup bulunmadığını kontrol eden bir kural yazmıyoruz. Dolayısıyla aynı kitap bilgileri listede iki ayrı kimlikle bulunabilir.

GET isteğini tekrar göndermek ise listeye kitap eklemez. GET fonksiyonlarımız yalnızca mevcut listeyi okur, arar ve sonucu döndürür.

| İşlem | Başlangıçta üç kitap varsa |
|---|---|
| Başarılı POST | Kitap sayısı 4 olur; yeni kimlik 74'tür. |
| Aynı POST'u tekrar göndermek | Kitap sayısı 5 olur; yeni kimlik 75'tir. |
| GET ile listeyi tekrar istemek | Kitap sayısı değişmez. |

Practice'in ek çalışmasında kullandığımız Postman ile aynı POST isteğini göndermek de yeni kayıt ekler. Aracın değişmesi işlemi denemelik veya etkisiz yapmaz; sunucu yine gelen isteği işler.

## 8. Eklenen kitap nerede duruyor?

`books.append(...)`, **çalışan sunucu programının belleğindeki listeyi** değiştirir. `server.py` dosyasındaki kod metnini değiştirmez. Bu uygulamada henüz veritabanına veya başka bir dosyaya yazmıyoruz.

Sunucuyu kapatıp yeniden başlattığımızda Python, `server.py` içindeki başlangıç listesini yeniden oluşturur. Dosyada yalnızca 42, 57 ve 73 varsa liste yine bu üç kitapla başlar. Çalışırken eklediğimiz 74 ve 75 artık bulunmaz; sonraki ilk ekleme yeniden 74 kimliğini alır.

İstemciyi kapatıp yeniden çalıştırmak sunucuyu yeniden başlatmaz. Sunucu çalışmaya devam ettiği sürece onun belleğindeki liste de kalır. Dosyayı değiştirince sunucuyu yeniden başlatmak veya otomatik yeniden yükleme kullanmak ise bu listeyi yeniden oluşturur.

![İstemci sona erdiğinde kitapların korunması; ikinci POST ile 75 numaralı kitabın eklenmesi ve sunucu yeniden başlatıldığında üç kitaba dönülmesi](Gorseller/02_kaydin_omru.svg)

Bu hafta kitap eklemenin üç ayrı sonucunu gözlüyoruz: **sunucu bilgiyi alır ve kontrol eder; bizim kodumuz listeyi değiştirir; HTTP yanıtı istemciye sonucu bildirir.** Verinin sunucu yeniden başladıktan sonra da kalmasını sağlamak, ayrıca kurulacak bir saklama düzeni gerektirir.

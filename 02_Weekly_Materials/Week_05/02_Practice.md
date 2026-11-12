# Hafta 05 — Uygulama Föyü

## 0. Kural kimin işi?

Hafta 2'den beri sunucumuz bazı hatalı istekleri `422` ile reddediyor. Örneğin kitabın adını metin yerine sayı olarak gönderince (`"title": 123`) kitap eklenmiyor. Ama sunucu bazı hatalı değerleri hâlâ kabul ediyor: Adı boş bir kitap ya da `9` puanlı bir yorum eklenebiliyor. Bu hafta bu değerleri reddeden kuralları yazacağız.

Haftanın sonunda şu soruya cevap verebileceksin: **Bir kuralı nereye yazmalıyım?** Bazı kurallar için gelen değere bakmak yeter: `""` boş bir metindir, `9` beşten büyüktür. Bazıları içinse sunucudaki veriye bakmak gerekir: 43 numaralı bir kitap var mı? İlk türden kuralları FastAPI, fonksiyonumuz çalışmadan önce kontrol edebilir; ikinci türden kuralları yalnızca fonksiyonumuz bilebilir, çünkü kitap listesi (`books`) bizim kodumuzda duruyor; FastAPI onu tanımıyor. Deney 5'in sonunda bu ayrımı bir tabloda toplayacağız.

Bu hafta sırasıyla şunları yapacağız:

- **Deney 1:** Sunucunun bugün hangi hatalı değerleri kabul ettiğini görmek ve hata yanıtını okumak
- **Deney 2:** Boş metinleri ve aralık dışı puanları reddetmek
- **Deney 3:** Türü sıkılaştırmak ve modelde olmayan alanları reddetmek
- **Deney 4:** `PATCH` isteğinde `null` gönderilen zorunlu alanları reddetmek
- **Deney 5:** Kuralın modele mi, fonksiyona mı yazılacağına karar vermek
- **Deney 6** (ödev): Hata yanıtını istemcide okunur biçimde göstermek

### 0.1 Başlangıç dosyaları

Hafta 4'ün sonundaki dosyalarla başla:

| Dosya | Hafta 4 föyündeki yeri |
|---|---|
| `server.py` | Deney 4 sonundaki hâli: 4.3'te dekoratörlerine `response_model` eklenmiş sunucu |
| `client.py` | Her deneyde içeriğini baştan yazacağız. |

Kendi `server.py` dosyandan emin değilsen, bu haftanın [başlangıç dosyasını](Starting_Code/server.py) kullan; föydeki çıktılar bu dosyayla alındı. Dosyada 42 numaralı kitabın `internal_note` alanı ve Ece'nin yorumu olmalı; Deney 3 ve Deney 5 bunlara dayanıyor.

Hafta 4'teki 5.3 alıştırmasını yaptıysan, eklediğin `delete_review` fonksiyonu da dosyada kalabilir; bu haftanın değişiklikleriyle çakışmaz.

> **Çıktıları föydekilerle aynı görmek için:** Sunucu her başlatıldığında dosyada yazılı üç kitapla ve bir yorumla başlar. Deneylerdeki "sunucuyu yeniden başlat" adımlarını izle; istemcinin eklediği kitaplar ve yorumlar böylece silinir.

---

## Deney 1 — Sunucu bugün neyi kabul ediyor?

**Amaç:** Sunucuya hatalı değerler gönderip hangilerini kabul ettiğini görmek ve reddettiği isteklerin hata yanıtını okumak.

Kural yazmadan önce sunucunun bugün ne yaptığını bilmemiz gerekiyor. Bu deneyde kitabın her seferinde tek bir alanını bozarak `POST /books` isteği gönderiyoruz.

### 1.1 Hatalı değerler göndermek

`client.py` dosyasının içeriğini şununla değiştir:

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
    "tags": ["http", "python"]
}


# Kitabın bir alanını değiştirip gönderir, sunucunun ne yaptığını yazar.
def send_book(label, field, value):
    body = new_book.copy()
    body[field] = value
    response = httpx.post(base_url + "/books", json=body)

    if response.status_code == 201:
        print(label, response.status_code, "stored:", repr(response.json().get(field)))
    else:
        print(label, response.status_code, response.json()["detail"][0]["msg"])


try:
    send_book("Empty title:     ", "title", "")
    send_book("Blank title:     ", "title", "   ")
    send_book("Rating 7:        ", "rating", 7)
    send_book("Rating -1:       ", "rating", -1)
    send_book("Rating as text:  ", "rating", "4.5")
    send_book("Available 'yes': ", "available", "yes")
    send_book("Unknown field:   ", "isbn", "975-0-00-000000-0")
    send_book("Title as number: ", "title", 123)

    # Yorum: puanı 9, okuru ve yorumu boş.
    review = {"reader": "", "comment": "", "score": 9}
    response = httpx.post(base_url + "/books/42/reviews", json=review)
    if response.status_code == 201:
        print("Review score 9:  ", response.status_code, "stored:", response.json())
    else:
        print("Review score 9:  ", response.status_code, response.json()["detail"][0]["msg"])
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

| Kod | Ne yapar? |
|---|---|
| `new_book.copy()` | Kitap sözlüğünün bir kopyasını oluşturur. Her istekte yalnızca kopya değişir; `new_book` bozulmadan kalır. |
| `body[field] = value` | Kopyada tek bir alanı değiştirir ya da yeni bir alan ekler. |
| `response.json().get(field)` | Yanıttaki kitapta bu alanın değerini verir. Alan yanıtta yoksa hata vermez, `None` verir. |
| `repr(...)` | Değeri tırnaklarıyla yazar. Böylece boş metin `''` olarak görünür. |
| `response.json()["detail"][0]["msg"]` | İstek reddedildiyse hata yanıtındaki ilk açıklamayı alır. Bu yanıtı 1.2'de inceleyeceğiz. |

Sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Empty title:      201 stored: ''
Blank title:      201 stored: '   '
Rating 7:         201 stored: 7.0
Rating -1:        201 stored: -1.0
Rating as text:   201 stored: 4.5
Available 'yes':  201 stored: True
Unknown field:    201 stored: None
Title as number:  422 Input should be a valid string
Review score 9:   201 stored: {'reader': '', 'comment': '', 'score': 9, 'id': 2, 'book_id': 42}
```

Dokuz istekten yalnızca biri reddedildi. Tablonun her satırı, çıktının aynı sıradaki satırını açıklıyor:

| Çıktıdaki satır | Gönderilen | Sunucu ne yaptı? Neden? | Sorun |
|---|---|---|---|
| `Empty title` | `"title": ""` | Kitabı ekledi. `title: str` yalnızca değerin metin olup olmadığına bakar. `""` de bir metindir; yalnızca içinde hiç karakter yoktur. | Katalogda adı olmayan bir kitap var. Kitap listesinde bu kitabın adının yeri boş görünür. Ada göre yapılan hiçbir aramada da çıkmaz. Hata istemcideydi, ama istemci `201` aldığı için kitabın doğru eklendiğini sanıyor. |
| `Blank title` | `"title": "   "` | Kitabı ekledi. Üç boşluk da bir metindir. | Aynı sorun, ama fark etmesi daha zor. Ad ekranda boş görünür, ama Python için boş değildir: Üç boşluk karakterinden oluşan, uzunluğu 3 olan bir metindir. Bu yüzden yalnızca "metin boş mu?" diye bakan bir kontrol bu adı yakalayamaz. Bunu Deney 2'de göreceğiz. |
| `Rating 7` | `"rating": 7` | Kitabı ekledi. `rating: float` yalnızca değerin sayı olup olmadığına bakar, aralığına bakmaz. `7` tam sayısı ondalıklı sayıya çevrildi; bu yüzden `7.0` kaydedildi. | Puan 0 ile 5 arasında olmalı; 5 üzerinden 7 puan olmaz. Bu kitap, puanı gerçekten 5 olan kitaplardan daha iyi görünür. Puanları yıldızla gösteren bir istemci de 7 yıldız çizmeye çalışır. Sunucu isteği kabul ettiği için istemci yanlış puan gönderdiğini öğrenmiyor. |
| `Rating -1` | `"rating": -1` | Kitabı ekledi. `-1` de bir sayıdır. | Aynı sorun, aralığın öteki ucunda: Bu ölçekte eksi puan yok. Kitapların puan ortalamasını hesaplayan bir istemci, bu değer yüzünden gerçekte olandan daha düşük bir ortalama bulur. |
| `Rating as text` | `"rating": "4.5"` | Metni sayıya çevirdi. Pydantic, sayı gibi okunabilen bir metni varsayılan olarak sayıya çevirir. | İstemci puanı sayı yerine tırnak içinde, metin olarak gönderdi. Bu, istemcinin kodundaki bir hata; büyük olasılıkla puanı bir metin kutusundan okuyup sayıya çevirmeyi unuttu. Sunucu metni sessizce çevirdiği için istemci bu hatayı fark etmiyor. Aynı istemci bir gün `"4,5"` gibi çevrilemeyen bir metin gönderirse `422` alır. Hata o zaman ortaya çıkar ve nedeni anlaşılmaz, çünkü `"4.5"` gönderirken her şey çalışıyordu. |
| `Available 'yes'` | `"available": "yes"` | `"yes"` metnini `True` yaptı. Pydantic bazı metinleri varsayılan olarak mantıksal değer sayar. | Aynı durum: `available` alanı `true` ya da `false` bekliyor, istemci ise metin gönderdi. Pydantic bazı İngilizce metinleri tanır: `"yes"`, `"on"` ve `"1"` metinlerini `True`; `"no"`, `"off"` ve `"0"` metinlerini `False` yapar. `"evet"` gibi tanımadığı bir metni ise reddeder. İstemci hangi metinlerin kabul edildiğini bilemez. Bugün `"yes"` ile çalışan kod, `"evet"` gönderildiği gün `422` alır. |
| `Unknown field` | `"isbn": "..."` | Kitabı ekledi, ama `isbn` alanını sessizce süzdü: Kaydedilen kitapta bu alan yok. Pydantic, modelde olmayan alanları varsayılan olarak hata vermeden atar. | İstemci `201` aldığı için ISBN numarasının da kaydedildiğini sanıyor. Kitabı daha sonra okuduğunda `isbn` alanını bulamaz ve nedenini anlayamaz. Alan adını yanlış yazmak da aynı sonucu verir: `"rating"` yerine `"ratng"` gönderen istemcinin puanı sessizce kaybolur, kitabın puanı `None` olur ve istemci hiçbir hata almaz. |
| `Title as number` | `"title": 123` | `422` ile reddetti. `123` bir metin değil. Pydantic metni sayıya çevirebiliyor (`"4.5"` satırı), ama sayıyı metne çevirmiyor. | Yok. İstemci hatasını hemen öğrendi. |
| `Review score 9` | `"score": 9`, boş `reader` ve `comment` | Yorumu ekledi. `score: int` yalnızca değerin tam sayı olup olmadığına bakar. `reader: str` ve `comment: str` de yalnızca metin olup olmadıklarına bakar. | Üç sorun birden var. Yorum puanı 1 ile 5 arasında olmalı; 9 bu ölçekte anlamsız. Okurun adı boş olduğu için yorumu kimin yazdığı belli değil. Yorum metni de boş, yani okunacak bir şey yok. Sunucu üçünü de kaydetti; kitabın yorumlarını okuyan herkes bu boş yorumu görür. |

`"4.5"`, `"yes"` ve `isbn` satırlarındaki davranışlar bir hata değil, Pydantic'in bilinçli varsayılanları; Deney 3'te bizim API'miz için neden değiştirdiğimizi tartışacağız. `"4.5"` ve `"yes"` metinlerinin neden kabul edildiğini ve başka hangi değerlerin çevrildiğini [ek nottaki tabloda](03_Supplement_Lax_Type_Conversion.md) görebilirsin.

### 1.2 Hata yanıtını okumak

Reddedilen tek istek `"title": 123` idi. Şimdi hata yanıtının tamamına bakalım. Hata yalnızca gövdede değil, yol parametresinde ve sorgu parametresinde de olabilir (Hafta 1, Deney 8); üçünü birden gönderiyoruz.

`client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"

new_book = {
    "title": 123,
    "author": {
        "first_name": "Ada",
        "last_name": "Yıldız"
    },
    "available": True,
    "tags": ["http", "python"]
}

try:
    # Gövdede hata: kitabın adı metin değil.
    response = httpx.post(base_url + "/books", json=new_book)
    print("Body: ", response.status_code, response.json())

    # Yol parametresinde hata: kitap kimliği sayı değil.
    response = httpx.get(base_url + "/books/abc")
    print("Path: ", response.status_code, response.json())

    # Sorgu parametresinde hata: available true ya da false değil.
    response = httpx.get(base_url + "/books", params={"available": "maybe"})
    print("Query:", response.status_code, response.json())
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Body:  422 {'detail': [{'type': 'string_type', 'loc': ['body', 'title'], 'msg': 'Input should be a valid string', 'input': 123}]}
Path:  422 {'detail': [{'type': 'int_parsing', 'loc': ['path', 'book_id'], 'msg': 'Input should be a valid integer, unable to parse string as an integer', 'input': 'abc'}]}
Query: 422 {'detail': [{'type': 'bool_parsing', 'loc': ['query', 'available'], 'msg': 'Input should be a valid boolean, unable to interpret input', 'input': 'maybe'}]}
```

Üç yanıtın gövdesi aynı biçimde: `detail` alanında bir **liste** var ve listenin her öğesi bir hatayı anlatıyor. Bir hatanın parçaları:

| Parça | Anlamı | `"title": 123` örneğinde |
|---|---|---|
| `type` | Hatanın türünün kısa adı | `string_type`: metin bekleniyordu. |
| `loc` | Hatanın **nerede** olduğu. İlk öğe isteğin hangi bölümü, son öğe hangi alan ya da parametre. | `['body', 'title']`: gövdedeki `title` alanı |
| `msg` | Hatanın insanların okuyacağı açıklaması. Bu metni biz yazmadık; Pydantic üretir. | `Input should be a valid string` |
| `input` | İstemcinin gönderdiği değer | `123` |

`loc` alanının ilk öğesi, değerin isteğin hangi bölümünden geldiğini söylüyor:

| `loc` içinde | Ne demek? | Bu örnekte |
|---|---|---|
| `body` | **Gövde (body):** `json=` ile gönderilen veri | Kitabın `title` alanı |
| `path` | **Yol parametresi (path parameter):** adresin yolundaki değer | `/books/abc` içindeki `abc` |
| `query` | **Sorgu parametresi (query parameter):** `params=` ile gönderilen, adresin `?` işaretinden sonraki değer | `?available=maybe` |

`loc` isteğin adresini değil, hatalı değerin durduğu yeri söyler. Birinci ve üçüncü isteğin yolu aynı, `/books`; ama hatalı değer birinde gövdede, ötekinde sorguda. İkinci istekte ise yolun kendisi bir değer taşıyor. Sunucudaki `@app.get("/books/{book_id}")` dekoratöründe `{book_id}`, "buraya bir değer gelecek" demek. FastAPI `abc` değerini `book_id: int` parametresine koymak istedi, ama `abc` tam sayıya çevrilemedi.

Path ve Query satırlarında `input` değeri tırnak içinde: `'abc'` ve `'maybe'`. Adresteki değerler her zaman metin olarak gelir; FastAPI onları parametrenin türüne çevirmeye çalışır. Hata, bu çeviri yapılamayınca oluşur. Body satırındaki `123` ise tırnaksız, çünkü JSON gövdesinde sayı, sayı olarak gönderilebilir.

Hafta 1'deki [URL ek notunda](../Week_01/03_Supplement_URL.md) adresin parçalarına ad vermiştik: `/books/abc` kısmı **yol (path)**, `?` işaretinden sonraki kısım **sorgu (query)**. Bu parçaların içindeki değerler de parametredir: `abc` bir yol parametresi, `available=maybe` bir sorgu parametresi. Bu yüzden "sorgudaki `available`" ile "`available` sorgu parametresi" aynı şeyi anlatır. Yol, sorgu ve gövde ayrımını Hafta 3'teki [sorgu ve gövde ek notunda](../Week_03/06_Supplement_Query_vs_Body.md) da görmüştük.

`detail` alanının değeri `[` ile başlayıp `]` ile bitiyor; bu, onun bir liste olduğunu gösterir. Bu isteklerde tek hata olduğu için listelerde tek öğe var; bir istekte birden fazla hata olunca hepsi bu listede sıralanır. Bunu Deney 2'de göreceğiz.

Bu hataların hepsinde durum kodu `422`. Kodun adı sunucunun terminalinde `422 Unprocessable Entity` olarak görünür; HTTP standardının güncel sürümü aynı koda `Unprocessable Content` diyor ve Python 3.13 ve sonrasıyla çalışan sunucular bu yeni adı yazar. İki ad aynı kodu anlatır. Bazı API'ler benzer hatalar için `400` kullanır; aradaki fark [ek notta](04_Supplement_400_vs_422.md).

> **Ana fikir:** Sunucu şu an yalnızca türü yanlış olan değerleri reddediyor. Türü doğru ama anlamsız değerler (boş ad, `9` puan) ve modelde olmayan alanlar kabul ediliyor. Reddedilen her istekte `422` yanıtının `detail` listesi, hatanın ne olduğunu (`msg`) ve nerede olduğunu (`loc`) söylüyor.

---

## Deney 2 — Değer sınırları: `Field`

**Amaç:** Modellere boş metinleri ve aralık dışı puanları reddeden kurallar eklemek.

Önceki haftalarda iki kuralı bu haftaya bırakmıştık: Hafta 2'de "kitabın adı boş olmasın", Hafta 3'te "yorumun puanı 1 ile 5 arasında olsun". Bu tür kuralları Pydantic'in `Field` fonksiyonuyla modeldeki alanın yanına yazıyoruz.

Kuralları yazmadan önce, 2.1'de değiştireceğimiz satırlardan birini yakından okuyalım.

### Önce bir hatırlatma: `rating: float | None = None` satırını okumak

Hafta 2'de yazdığımız `rating: float | None = None` satırı iki ayrı soruyu cevaplıyor. Python satırı üç parçaya ayırır:

| Parça | Bu satırda | Hangi soruyu cevaplar? |
|---|---|---|
| Alanın adı | `rating` | |
| Alanın türü | `float \| None` | İstemci bu alana `null` gönderebilir mi? Evet. |
| **Varsayılan değer (default value)** | `= None` | İstemci bu alanı hiç göndermeyebilir mi? Evet. Gönderilmezse değeri `None` olur. |

Türdeki `|` işaretine **dikey çizgi (pipe)** denir. Tür yazımında "ya da" anlamına gelir: `float | None` "ondalıklı sayı ya da `None`" demek. Python bu yazıma **birleşim türü (union type)** der.

Satırda iki tane `None` var ve ikisi farklı işler yapıyor:

- `|` işaretinden sonraki `None` türün bir parçası. "`null` da kabul edilir" diyor.
- `=` işaretinden sonraki `None` varsayılan değer. Yalnızca dikey çizgiden sonraki `None`'a değil, bütün alana ait. "Gönderilmezse değer `None` olsun" diyor.

Üç yazımı karşılaştıralım:

| Yazım | Gönderilmeyebilir mi? | `null` olabilir mi? | Nerede? |
|---|---|---|---|
| `available: bool` | Hayır, zorunlu | Hayır | `BookCreate` |
| `available: bool = None` | Evet | Hayır | `BookUpdate`, Deney 4'ten sonra |
| `rating: float \| None = None` | Evet | Evet | `BookCreate` ve `BookUpdate` |

`rating` için üçüncü yazımı seçiyoruz, çünkü puan için `null` anlamlı bir değer: "Bu kitabın puanı yok." 42 numaralı kitabın puanı da `null`. İkinci yazımın neden işe yaradığını Deney 4'te göreceğiz.

**Kısacası:** Varsayılan değer (`= None`), alanın gönderilmeyebileceğini söyler. Türdeki `| None` ise `null` gönderilebileceğini söyler. `rating` alanında ikisi de var.

2.1'de bu satırın türü değişmeyecek. Yalnızca varsayılan değer `Field` fonksiyonunun içine taşınacak: `= None` yazımı, `= Field(default=None, ...)` olacak. Şimdi bu satıra ve öteki alanlara kuralları ekleyelim.

### 2.1 Modellere kuralları ekle

`server.py` dosyasında şu satırları değiştir:

| Eski satır | Yeni satır |
|---|---|
| `from pydantic import BaseModel` | `from pydantic import BaseModel, Field` |
| `BookCreate` içinde `title: str` | `title: str = Field(min_length=1)` |
| `BookCreate` içinde `rating: float \| None = None` | `rating: float \| None = Field(default=None, ge=0, le=5)` |
| `BookUpdate` içinde `title: str \| None = None` | `title: str \| None = Field(default=None, min_length=1)` |
| `BookUpdate` içinde `rating: float \| None = None` | `rating: float \| None = Field(default=None, ge=0, le=5)` |
| `ReviewCreate` içinde `reader: str` | `reader: str = Field(min_length=1)` |
| `ReviewCreate` içinde `comment: str` | `comment: str = Field(min_length=1)` |
| `ReviewCreate` içinde `score: int` | `score: int = Field(ge=1, le=5)` |

Değişen modellerin yeni hâli:

```python
from pydantic import BaseModel, Field

...

class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    author: Author
    available: bool
    tags: list[str]
    rating: float | None = Field(default=None, ge=0, le=5)

...

class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    author: Author | None = None
    available: bool | None = None
    tags: list[str] | None = None
    rating: float | None = Field(default=None, ge=0, le=5)


class ReviewCreate(BaseModel):
    reader: str = Field(min_length=1)
    comment: str = Field(min_length=1)
    score: int = Field(ge=1, le=5)
```

| Yazım | Anlamı |
|---|---|
| `Field(min_length=1)` | Metin en az 1 karakter olmalı. Boş metin `""` reddedilir. |
| `Field(ge=0, le=5)` | Sayı 0'dan büyük ya da eşit (greater than or equal), 5'ten küçük ya da eşit (less than or equal) olmalı. |
| `Field(default=None, ...)` | Alanın varsayılan değeri. Eskiden `= None` diye yazdığımız değer artık `Field` içinde `default=None` olarak yazılıyor. Eşittir işaretinin sağında artık `Field(...)` var ve oraya ikinci bir değer yazılamaz. |

Üç model için üç not:

- **Kitap puanı neden 0 ile 5 arasında?** 57 numaralı kitabın puanı `0`; alt sınırı `1` yapsaydık bu kitap okunamaz olurdu. Nedenini [ek notta](05_Supplement_Inherited_Rules.md) görebilirsin.
- **`BookUpdate` modeline neden aynı kurallar?** `PATCH` istekleri bu modelle kontrol ediliyor. Kural eklemeseydik `PATCH` ile boş bir ad kaydedilebilirdi.
- **`BookUpdate` modelindeki `| None` ne olacak?** Şimdilik kalıyor; Deney 4'te ele alacağız.

### 2.2 Tekrar dene

Sunucuyu yeniden başlat ve Deney 1.1'deki istemciyi tekrar çalıştır:

```text
Empty title:      422 String should have at least 1 character
Blank title:      201 stored: '   '
Rating 7:         422 Input should be less than or equal to 5
Rating -1:        422 Input should be greater than or equal to 0
Rating as text:   201 stored: 4.5
Available 'yes':  201 stored: True
Unknown field:    201 stored: None
Title as number:  422 Input should be a valid string
Review score 9:   422 String should have at least 1 character
```

Çıktıdaki yeni mesajlar ne sunucuda ne istemcide yazıyor. Biz sunucuya yalnızca `le=5` gibi kuralı yazdık. Değer kurala uymayınca mesajı Pydantic kendisi üretiyor, FastAPI de onu yanıtın `msg` alanına koyuyor. İstemci bu metni `["detail"][0]["msg"]` ile alıp yazdırıyor.

Tablonun her satırı, çıktının aynı sıradaki satırını açıklıyor:

| Çıktıdaki satır | Gönderilen | Deney 1'de | Şimdi | Neden? |
|---|---|---|---|---|
| `Empty title` | `"title": ""` | `201` | `422` | `min_length=1`: Ad en az 1 karakter olmalı. |
| `Blank title` | `"title": "   "` | `201` | `201`, değişmedi | Üç boşluk da bir metin ve uzunluğu 3; kurala uyuyor. Reddetmenin yolu [ek notta](06_Supplement_Blank_Strings.md). |
| `Rating 7` | `"rating": 7` | `201` | `422` | `le=5`: Puan en fazla 5 olabilir. |
| `Rating -1` | `"rating": -1` | `201` | `422` | `ge=0`: Puan en az 0 olabilir. |
| `Rating as text` | `"rating": "4.5"` | `201` | `201`, değişmedi | Kural yalnızca sayının aralığına bakıyor. Metin önce `4.5` sayısına çevrildi; bu sayı 0 ile 5 arasında olduğu için kabul edildi. Çeviriyi durdurmak Deney 3'te. |
| `Available 'yes'` | `"available": "yes"` | `201` | `201`, değişmedi | `available` alanına kural eklemedik. `"yes"` metni yine `True` yapıldı. Deney 3'te. |
| `Unknown field` | `"isbn": "..."` | `201` | `201`, değişmedi | Kuralları yalnızca modeldeki alanlara yazdık. Modelde olmayan `isbn` yine sessizce süzüldü. Deney 3'te. |
| `Title as number` | `"title": 123` | `422` | `422`, değişmedi | Modelde `title: str` yazıyor, yani ad bir metin olmalı. `123` ise bir sayı. Pydantic metni sayıya çevirebiliyor (`"4.5"` satırı), ama sayıyı metne çevirmiyor. Bu yüzden bu istek Deney 1'de de reddedilmişti; yeni kural bunu değiştirmedi. |
| `Review score 9` | `"score": 9`, boş `reader` ve `comment` | `201` | `422` | Üç alan da kurala uymuyor. Çıktıda yalnızca ilk hata görünüyor; hepsine 2.3'te bakacağız. |

### 2.3 Bir istekte birden fazla hata

Son satırda yalnızca ilk hatanın açıklamasını yazdırdık: `String should have at least 1 character`. Oysa o yorumda üç alan birden kurala uymuyordu. Hepsine bakalım.

`client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"

try:
    # Üç alanı da kurala uymayan bir yorum.
    review = {"reader": "", "comment": "", "score": 9}
    response = httpx.post(base_url + "/books/42/reviews", json=review)
    print("Status:", response.status_code)

    for error in response.json()["detail"]:
        print(error)
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Status: 422
{'type': 'string_too_short', 'loc': ['body', 'reader'], 'msg': 'String should have at least 1 character', 'input': '', 'ctx': {'min_length': 1}}
{'type': 'string_too_short', 'loc': ['body', 'comment'], 'msg': 'String should have at least 1 character', 'input': '', 'ctx': {'min_length': 1}}
{'type': 'less_than_equal', 'loc': ['body', 'score'], 'msg': 'Input should be less than or equal to 5', 'input': 9, 'ctx': {'le': 5}}
```

FastAPI üç hatayı tek yanıtta listeledi. İstemci, hangi alanları düzeltmesi gerektiğini tek bir istekle öğreniyor.

Hatalarda yeni bir parça da var: `ctx`, yani hatanın bağlamı. Kuralın kendisini söyler: `{'min_length': 1}` "en az 1 karakter" kuralı, `{'le': 5}` "en fazla 5" kuralıdır. Tür hatalarında böyle bir kural olmadığı için Deney 1'deki yanıtlarda `ctx` yoktu.

> **Ana fikir:** `Field` ile modeldeki alana kural yazılır: metin için `min_length`, sayı için `ge` ve `le`. Kurala uymayan değer, türü doğru olsa bile `422` ile reddedilir. Bir istekteki bütün hatalar aynı yanıtta listelenir.

---

## Deney 3 — Türü ve alanları sıkılaştırmak

**Amaç:** Metnin sayıya ya da mantıksal değere çevrilmesini durdurmak ve modelde olmayan alanları reddetmek.

Deney 2'den sonra üç sorun kaldı: `"4.5"` metni puan olarak, `"yes"` metni `available` değeri olarak kabul ediliyor; `isbn` alanı da sessizce süzülüyor. Bu sorunlar tek tek alanlarla ilgili değil, modelin bütün alanlarına nasıl davrandığıyla ilgili. Bu yüzden kuralı alanların yanına değil, modelin kendisine yazıyoruz.

### 3.1 İstek modellerine ayar ekle

`server.py` dosyasında import satırını değiştir:

| Eski satır | Yeni satır |
|---|---|
| `from pydantic import BaseModel, Field` | `from pydantic import BaseModel, ConfigDict, Field` |

`BookCreate`, `BookUpdate` ve `ReviewCreate` modellerinin her birine, alanlardan önce aynı satırı ekle:

```python
class BookCreate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    title: str = Field(min_length=1)
    ...


class BookUpdate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    title: str | None = Field(default=None, min_length=1)
    ...


class ReviewCreate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    reader: str = Field(min_length=1)
    ...
```

| Yazım | Anlamı |
|---|---|
| `model_config = ConfigDict(...)` | **Modelin ayarları (model configuration).** Alanlardan biri değil; Pydantic'e bu modelin nasıl çalışacağını söyler. |
| `strict=True` | **Sıkı mod (strict mode):** Değer, alanın türünde gönderilmeli; Pydantic başka türden çeviri yapmaz. `"4.5"` metni `float` alanına, `"yes"` metni `bool` alanına artık girmez. |
| `extra="forbid"` | Modelde olmayan bir alan, yani bir **fazla alan (extra field)** gönderilirse istek reddedilir. Hata mesajındaki `Extra inputs` bu alanlardır. Varsayılan davranış, böyle alanları sessizce süzmektir. |

> **Sorgu parametresi bu ayardan etkilenmez.** Bu ayarlar yalnızca eklendikleri modelleri etkiler. Kitap listesini süzen `GET /books?available=true` isteğindeki `available` bir model alanı değil, `get_books` fonksiyonunun parametresi. Bu yüzden bu istek eskisi gibi çalışır. Sorgu parametresinde sıkı mod zaten işe yaramazdı: Adresteki değerler her zaman metin olarak gelir; `?available=true` içindeki `true` da bir metindir. FastAPI bu metni `bool` türüne çevirmek zorundadır. 1.2'deki `?available=maybe` isteği, bu çeviri yapılamadığı için `422` almıştı.

> **Bu bir tasarım seçimi.** Pydantic'in varsayılan davranışı (değerleri çevirmek, fazla alanları süzmek) yanlış değildir; birçok API bilerek böyle çalışır. Biz kitap kataloğunda istemcinin hatasını hemen öğrenmesini seçtik.

### 3.2 Tekrar dene

Sunucuyu yeniden başlat ve Deney 1.1'deki istemciyi tekrar çalıştır:

```text
Empty title:      422 String should have at least 1 character
Blank title:      201 stored: '   '
Rating 7:         422 Input should be less than or equal to 5
Rating -1:        422 Input should be greater than or equal to 0
Rating as text:   422 Input should be a valid number
Available 'yes':  422 Input should be a valid boolean
Unknown field:    422 Extra inputs are not permitted
Title as number:  422 Input should be a valid string
Review score 9:   422 String should have at least 1 character
```

`"4.5"`, `"yes"` ve `isbn` artık reddediliyor. Yalnızca boşluklardan oluşan ad kaldı; o, [ek nottaki](06_Supplement_Blank_Strings.md) ayarla düzelir.

### 3.3 Bir şey bozuldu

İstekler doğru reddediliyor, ama kitapları okumayı da deneyelim. `client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"

try:
    # Tek kitap: 42 numaralı kitabın sözlüğünde internal_note var.
    response = httpx.get(base_url + "/books/42")
    print("Book 42:  ", response.status_code, response.text)

    # Kitap listesi: 42 numaralı kitap da listede.
    response = httpx.get(base_url + "/books")
    print("Book list:", response.status_code)
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Book 42:   500 Internal Server Error
Book list: 500
```

Hafta 4'te çalışan iki istek artık `500` alıyor.

İstemci yalnızca `Internal Server Error` metnini görüyor. Şimdiye kadarki yanıtların gövdesi hep JSON'du; hata yanıtlarında da `detail` alanı vardı. Bu yanıt farklı: Gövdesi JSON değil, yalnızca bu iki kelimelik düz bir metin. Sorun istemcinin isteğinde değil sunucuda olduğu için FastAPI ayrıntıyı istemciye göndermez, yalnızca sunucunun terminaline yazar. `response.json()` gövdeyi JSON olarak okumaya çalışır ve JSON olmayan bir gövdede hata verir. Bu yüzden bu istemcide gövdeyi olduğu gibi, metin olarak veren `response.text` kullandık.

Nedenini sunucunun çalıştığı terminalde görebiliriz. Uzun hata çıktısının içinde şu satırlar var:

```text
INFO:     127.0.0.1:55002 - "GET /books/42 HTTP/1.1" 500 Internal Server Error
...
fastapi.exceptions.ResponseValidationError: 1 validation error:
  {'type': 'extra_forbidden', 'loc': ('response', 'internal_note'), 'msg': 'Extra inputs are not permitted', 'input': 'Kapağı yıpranmış, yenisi sipariş edildi.'}
```

Hatanın adındaki *Validation*, **doğrulama (validation)** demek: Bir değeri modeldeki kurallara göre kontrol etmek. `ResponseValidationError`, yanıtın doğrulanamadığını söylüyor. Hata bu kez istekte değil, yanıtta: `loc` alanının ilk öğesi `response`. Adım adım:

1. `get_book` fonksiyonu 42 numaralı kitabı döndürdü. Sözlükte `internal_note` alanı da var (Hafta 4, Deney 4).
2. FastAPI, yanıtı göndermeden önce bu sözlüğü `BookPublic` modeline göre hazırlamak istedi.
3. `BookPublic` modeli `BookCreate` modelinden türüyor; alanlarıyla birlikte `model_config` ayarlarını da alıyor. Yani `BookPublic` modelinde de `extra="forbid"` var.
4. `internal_note` alanı `BookPublic` modelinde yok. Model bu fazla alanı süzmek yerine reddetti; yanıt hazırlanamadı ve istemciye `500` gitti.

### 3.4 Yanıt modelinin ayarını düzelt

İstek modeli ile yanıt modelinin fazla alanlara karşı davranışı farklı olmalı:

| Model | Fazla alan gelirse ne yapmalı? | Neden? |
|---|---|---|
| İstek modeli (`BookCreate`, `BookUpdate`, `ReviewCreate`) | **Reddetmeli** | İstemci yanlış bir alan gönderdiyse bunu öğrenmeli. |
| Yanıt modeli (`BookPublic`) | **Süzmeli** | Sunucunun kendi verisinde fazladan alan olabilir; istemciye yalnızca modeldeki alanlar gitmeli (Hafta 4, Deney 4). |

`server.py` dosyasında `BookPublic` modelini şöyle değiştir:

```python
class BookPublic(BookCreate):
    model_config = ConfigDict(strict=False, extra="ignore")

    id: int
```

Bu satır, `BookCreate` modelinden gelen iki ayarı değiştirir:

- **`extra="ignore"`:** Fazla alanları süzer; `ignore` İngilizcede "yok say" demek. Deney 1'de `isbn` alanına olan da buydu; Pydantic'in varsayılan davranışı budur.
- **`strict=False`:** Sıkı modu kapatır. Yanıt modeli istemcinin değil, sunucunun kendi verisini kontrol ediyor; orada sıkı moda gerek yok.

> Bu satır yalnızca modelin ayarlarını değiştirir; alanların kurallarına dokunmaz. İkisi modelde ayrı yerlere yazılır:
>
> - **Ayarlar** `model_config` satırında durur ve modelin bütün alanlarına birden uygulanır: `strict` ve `extra`. `BookPublic` kendi `model_config` satırını yazınca, `BookCreate` modelinden gelen bu iki ayarın yerine kendi değerleri geçer.
> - **Kurallar** her alanın kendi satırında, `Field(...)` içinde durur: `title` için `min_length=1`, `rating` için `ge=0` ve `le=5`. `BookPublic` modelinde bu alanların satırları yeniden yazılmadı; modelde yalnızca `model_config` ve `id` var. Bu yüzden `title` ve `rating` alanları, kurallarıyla birlikte `BookCreate` modelinden olduğu gibi gelir.
>
> Yani yanıt hazırlanırken kitabın adı yine boş olmamalı, puanı da yine 0 ile 5 arasında olmalı. Kitap puanının alt sınırını Deney 2'de bu yüzden 0 yaptık.

Sunucuyu yeniden başlat ve aynı istemciyi çalıştır:

```text
Book 42:   200 {"title":"API Yolculuğu","author":{"first_name":"Deniz","last_name":"Kaya"},"available":true,"tags":["software","education"],"rating":null,"id":42}
Book list: 200
```

Kitaplar yeniden okunuyor ve `internal_note` yanıtta yok.

> **Ana fikir:** `model_config` modelin bütün alanlarına uygulanan ayarları taşır. `strict=True` türler arasında çeviri yapılmasını, `extra="forbid"` modelde olmayan alanların kabul edilmesini engeller. Türeyen model bu ayarları da alır; yanıt modelinde fazla alanların reddedilmesi değil, süzülmesi gerekir, sıkı moda da gerek yoktur.

---

## Deney 4 — PATCH: gönderilmeyebilir, ama `null` olamaz

**Amaç:** `PATCH` isteğinde şu kuralı kurmak: Bir alanı göndermek zorunlu değil, ama bir alan gönderilirse değeri `null` olamaz.

Kuralın iki yarısı var:

- **Alanı göndermek zorunlu değil.** `PATCH` kitabın yalnızca gönderilen alanlarını değiştirir (Hafta 4). İstemci yalnızca değiştirmek istediği alanları gönderir. Örneğin yalnızca puanı değiştirmek isteyen, kitabın adını göndermez; ad olduğu gibi kalır.
- **Gönderilen alan `null` olamaz.** Bir alanı göndermek, ona yeni bir değer vermek demektir. `{"title": null}` göndermek "kitabın adını sil" demek olur. Oysa adı olmayan bir kitap olamaz; bu yüzden böyle bir istek reddedilmeli. Bunun tek istisnası `rating`: Puan için `null` anlamlı bir değer, "Bu kitabın puanı yok." demek.

Sunucumuz bugün kuralın yalnızca ilk yarısını uyguluyor. Hafta 4'teki [`null` ek notunda](../Week_04/05_Supplement_Patch_Unset_vs_Null.md) `{"title": null}` gövdesiyle bir `PATCH` isteği göndermiştik. Sunucu bu isteği kabul etti ve kitabın adını `None` yaptı. Ardından FastAPI yanıtı hazırlamak istedi ve takıldı: Yanıt modeli `BookPublic`'te kitabın adı bir metin olmak zorunda, `None` ise metin değil. İstemciye `500` gitti. Ama kitabın adı yanıt hazırlanmadan önce `None` olmuştu ve bu değişiklik geri alınmadı. Bu yüzden kitap bozuk kaldı: Bu kitabı okuyan sonraki istekler de, örneğin `GET /books/42`, `500` aldı.

Doğrusu, böyle bir isteği kitaba dokunmadan önce `422` ile reddetmek.

Deney 3'teki sıkı mod bunu çözmedi. Sıkı mod yalnızca bir türden ötekine çeviri yapılmasını engeller. `None` ise `str | None` türünün zaten izin verdiği bir değer.

### 4.1 `BookUpdate` modelinde `| None` yazımını kaldır

Deney 2'nin başında, bir alan satırının iki ayrı soruyu cevapladığını görmüştük. Kuralın iki yarısı bu iki soruya karşılık geliyor:

- **"Alan gönderilmeyebilir mi?"** sorusunu varsayılan değer cevaplıyor. Cevap "evet" olmalı; bu yüzden varsayılan değeri **bırakıyoruz**.
- **"Alan `null` olabilir mi?"** sorusunu türdeki `| None` cevaplıyor. Cevap "hayır" olmalı; bu yüzden `| None` kısmını **kaldırıyoruz**.

`server.py` dosyasında `BookUpdate` modelinin alanlarını şöyle değiştir:

| Eski satır | Yeni satır |
|---|---|
| `title: str \| None = Field(default=None, min_length=1)` | `title: str = Field(default=None, min_length=1)` |
| `author: Author \| None = None` | `author: Author = None` |
| `available: bool \| None = None` | `available: bool = None` |
| `tags: list[str] \| None = None` | `tags: list[str] = None` |
| `rating: float \| None = Field(default=None, ge=0, le=5)` | Değişmiyor. |

Modelin yeni hâli:

```python
class BookUpdate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    title: str = Field(default=None, min_length=1)
    author: Author = None
    available: bool = None
    tags: list[str] = None
    rating: float | None = Field(default=None, ge=0, le=5)
```

`title: str = None` yazımı ilk bakışta çelişkili görünüyor: Tür `str`, varsayılan değer ise `None`. Bu yazımın işe yaramasının nedeni şu: **Pydantic, varsayılan değeri kontrol etmez; yalnızca istemcinin gönderdiği değeri kontrol eder.**

| İstemci `title` için ne yaptı? | Ne olur? |
|---|---|
| Hiç göndermedi | Varsayılan değer `None` kullanılır ve kontrol edilmez. `exclude_unset=True` bu alanı zaten `changes` sözlüğüne koymaz; kitabın adı değişmez. |
| `null` gönderdi | Gönderilen değer kontrol edilir. `None` bir metin değildir; istek `422` ile reddedilir. |
| Bir metin gönderdi | Metin kontrol edilir; boş değilse kabul edilir. |

Editörün bu satırların altını çizdiğini görürsen nedenini [ek notta](07_Supplement_Default_None.md) bulabilirsin; kod doğru çalışır.

`rating` alanında `| None` kalıyor, çünkü puan için `null` anlamlı bir değer: "Bu kitabın puanı yok." `null` göndermek puanı silmek demektir; Hafta 4'teki ek notta da bunu yapmıştık.

### 4.2 İstemciyle dene

`client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"


# PATCH isteği gönderir, durum kodunu ve kitabın adını ya da hatayı yazar.
def send_patch(label, body):
    response = httpx.patch(base_url + "/books/42", json=body)

    if response.status_code == 200:
        book = response.json()
        print(label, response.status_code, "title:", repr(book["title"]), "rating:", book["rating"])
    else:
        print(label, response.status_code, response.json()["detail"][0]["msg"])


try:
    send_patch("Empty body:   ", {})
    send_patch("Rating 4:     ", {"rating": 4})
    send_patch("Rating null:  ", {"rating": None})
    send_patch("Title null:   ", {"title": None})
    send_patch("Author null:  ", {"author": None})

    # Kitabı yeniden oku: bozulmuş mu?
    response = httpx.get(base_url + "/books/42")
    print("Read book 42: ", response.status_code, "title:", repr(response.json()["title"]))
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Empty body:    200 title: 'API Yolculuğu' rating: None
Rating 4:      200 title: 'API Yolculuğu' rating: 4.0
Rating null:   200 title: 'API Yolculuğu' rating: None
Title null:    422 Input should be a valid string
Author null:   422 Input should be a valid dictionary or object to extract fields from
Read book 42:  200 title: 'API Yolculuğu'
```

| Çıktıdaki satır | İstek | Sonuç |
|---|---|---|
| `Empty body` | `{}` | `200`. Hiçbir alan gönderilmedi; kitap değişmedi. |
| `Rating 4` | `{"rating": 4}` | `200`. Puan `4.0` oldu. Sıkı modda da tam sayı, ondalıklı sayı alanına yazılabilir. JSON'da `4` ile `4.0` aynı sayıdır; bu çeviride bilgi kaybolmaz. |
| `Rating null` | `{"rating": null}` | `200`. Puan silindi; `rating` için `null` geçerli bir değer. |
| `Title null` | `{"title": null}` | `422`. Hafta 4'te `500` alan ve kitabı bozan istek artık kitaba dokunulmadan reddediliyor. |
| `Author null` | `{"author": null}` | `422`. Yazar da `null` olamaz. Mesajdaki *dictionary or object*, yazarın bir nesne olması gerektiğini söylüyor: `first_name` ve `last_name` alanları olan bir sözlük. |
| `Read book 42` | `GET /books/42` | `200`. Kitabın adı yerinde; kitap bozulmadı. |

> **Ana fikir:** Bir alanın isteğe bağlı olması ile `null` olabilmesi ayrı şeylerdir. `title: str = None` yazımında alan gönderilmeyebilir, ama gönderilirse metin olmalıdır. `| None` yalnızca `null` değerinin anlamlı olduğu alanlarda kalmalı; bizim kitaplarımızda bu alan `rating`.

---

## Deney 5 — Kuralın yeri: model mi, fonksiyon mu?

**Amaç:** Kitap kimliğini taşıyan yol parametresine bir kural eklemek ve kaydedilmiş veriye bakmayı gerektiren bir kuralı fonksiyonun içine yazmak.

Şu ana kadar yazdığımız kuralların hepsi, karar vermek için yalnızca istemcinin gönderdiği değere bakıyordu. Örneğin boş bir adı reddetmek için adın kendisine bakmak yetiyordu; sunucudaki kitaplara bakmak gerekmiyordu. Bölüm 0'da bunları "gelen değere bakmak yeter" diye ayırmıştık.

Bu deneyde iki yeni kural ekliyoruz:

- **Kitap kimliği 0'dan büyük olmalı (5.1).** Bu kural da yalnızca değere bakıyor: `-5` sayısının bir kitap kimliği olamayacağını anlamak için kitap listesine bakmak gerekmez. Yeni olan, kuralın gövdedeki bir alana değil, adresteki yol parametresine yazılması.
- **Bir okur bir kitaba yalnızca bir yorum yazabilir (5.2).** Bu kural değere bakarak karar veremez. `"Ece"` adında yanlış bir şey yok. Ece'nin bu kitaba daha önce yorum yazıp yazmadığını öğrenmek için sunucudaki `reviews` listesine bakmak gerekir.

Deneyin sonunda bu iki tür kuralın nereye yazıldığını bir tabloda toplayacağız.

### 5.1 Yol parametresine kural: `Path`

Kitap kimlikleri pozitif sayılar. `/books/-5` adresi hiçbir zaman bir kitap bulamaz. Bu kuralı, yolunda `book_id` olan **bütün** fonksiyonların parametresine yazıyoruz; yoksa `GET /books/-5` isteği `422`, `DELETE /books/-5` isteği `404` alır ve aynı adres işleme göre farklı davranır.

`server.py` dosyasında şu satırları değiştir:

| Eski satır | Yeni satır |
|---|---|
| `from fastapi import FastAPI, HTTPException, Response` | `from fastapi import FastAPI, HTTPException, Path, Response` |
| `def get_book(book_id: int):` | `def get_book(book_id: int = Path(gt=0)):` |
| `def delete_book(book_id: int):` | `def delete_book(book_id: int = Path(gt=0)):` |
| `def replace_book(book_id: int, book_data: BookCreate):` | `def replace_book(book_data: BookCreate, book_id: int = Path(gt=0)):` |
| `def update_book(book_id: int, book_data: BookUpdate):` | `def update_book(book_data: BookUpdate, book_id: int = Path(gt=0)):` |
| `def get_reviews(book_id: int):` | `def get_reviews(book_id: int = Path(gt=0)):` |
| `def create_review(book_id: int, review_data: ReviewCreate):` | `def create_review(review_data: ReviewCreate, book_id: int = Path(gt=0)):` |

`Path`, `Field` fonksiyonunun yol parametreleri için olanıdır. `gt=0` "0'dan büyük" (greater than) demektir; `ge` gibi, ama sınırın kendisi dahil değil.

İki parametreli fonksiyonlarda `book_id` sona geçti. Python'da varsayılan değeri olan parametreler, varsayılan değeri olmayanlardan sonra gelmelidir; `= Path(gt=0)` yazımı da bir varsayılan değer gibi yazılıyor. FastAPI parametreleri sırasına göre değil adına göre eşleştirdiği için sıra değişikliği istekleri etkilemez. Sırayı değiştirmeyi unutursan sunucu başlamaz ve terminalde şu hata görünür:

```text
SyntaxError: non-default argument follows default argument
```

Python'un yeni sürümlerinde mesajın metni farklı olabilir; önemli olan, hatanın `SyntaxError` olması ve sunucunun başlamaması.

FastAPI belgelerinde aynı kuralın başka bir yazımını göreceksin; o yazım [ek notta](08_Supplement_Annotated.md).

### 5.2 Veriye bağlı kural: aynı okurun ikinci yorumu

Bir okur bir kitaba yalnızca bir yorum yazabilsin. Bu kural modele yazılamaz: `ReviewCreate` modeli yalnızca gelen yorumu görür. Okurun daha önce yorum yazıp yazmadığını öğrenmek için `reviews` listesine bakmak gerekir; bunu yalnızca fonksiyon yapabilir.

`server.py` dosyasında `create_review` fonksiyonuna, kitabın var olup olmadığını kontrol eden satırlardan sonra şunu ekle:

```python
    for review in reviews:
        if review["book_id"] == book_id and review["reader"] == review_data.reader:
            raise HTTPException(status_code=409, detail="This reader has already reviewed this book")
```

Fonksiyonun üstündeki yorumu da güncelle:

```python
# Yeni yorum: kitaba ekler, 201 döner; kitap yoksa 404, okurun bu kitaba yorumu varsa 409.
```

Bu kural okuru adından tanıyor; `"Ece"` ile `"ece"` iki ayrı okur sayılır. Gerçek bir sistemde okur, oturum açmış kullanıcının kimliğinden tanınır; bunu 9. haftada göreceğiz.

**409 Conflict**, "istek, sunucudaki verinin şu anki hâliyle çakışıyor" demektir. Hafta 2'nin [durum kodları notunda](../Week_02/07_Supplement_Status_Codes.md) görmüştük. İstek kendi içinde doğru; sorun, sunucuda zaten var olan bir yorum.

### 5.3 İstemciyle dene

`client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"

try:
    # Kimlik: -5 hiçbir zaman kitap kimliği olamaz, 43 olabilir ama yok.
    response = httpx.get(base_url + "/books/-5")
    print("Book -5:   ", response.status_code, response.json())

    # Aynı kural silme işleminde de var mı?
    response = httpx.delete(base_url + "/books/-5")
    print("Delete -5: ", response.status_code, response.json())

    response = httpx.get(base_url + "/books/43")
    print("Book 43:   ", response.status_code, response.json())

    # Yorumlar: Ece'nin 42 numaralı kitaba yorumu zaten var.
    review = {"reader": "Ece", "comment": "Tekrar okudum.", "score": 4}
    response = httpx.post(base_url + "/books/42/reviews", json=review)
    print("Ece again: ", response.status_code, response.json())

    review = {"reader": "Can", "comment": "Örnekleri çalıştırdım.", "score": 4}
    response = httpx.post(base_url + "/books/42/reviews", json=review)
    print("Can first: ", response.status_code, response.json())

    response = httpx.post(base_url + "/books/42/reviews", json=review)
    print("Can again: ", response.status_code, response.json())
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Book -5:    422 {'detail': [{'type': 'greater_than', 'loc': ['path', 'book_id'], 'msg': 'Input should be greater than 0', 'input': '-5', 'ctx': {'gt': 0}}]}
Delete -5:  422 {'detail': [{'type': 'greater_than', 'loc': ['path', 'book_id'], 'msg': 'Input should be greater than 0', 'input': '-5', 'ctx': {'gt': 0}}]}
Book 43:    404 {'detail': 'Book not found'}
Ece again:  409 {'detail': 'This reader has already reviewed this book'}
Can first:  201 {'reader': 'Can', 'comment': 'Örnekleri çalıştırdım.', 'score': 4, 'id': 2, 'book_id': 42}
Can again:  409 {'detail': 'This reader has already reviewed this book'}
```

| Çıktıdaki satır | İstek | Yanıt | Kim reddetti? | Neden? |
|---|---|---|---|---|
| `Book -5` | `GET /books/-5` | `422` | FastAPI, `Path(gt=0)` kuralıyla | `-5` hiçbir zaman kitap kimliği olamaz. Bunu bilmek için kitaplara bakmak gerekmez; fonksiyon hiç çalışmadı. |
| `Delete -5` | `DELETE /books/-5` | `422` | FastAPI, `Path(gt=0)` kuralıyla | Aynı kural silme işleminde de var. Burada `404` görüyorsan `delete_book` fonksiyonuna `Path(gt=0)` eklemeyi unutmuşsundur. |
| `Book 43` | `GET /books/43` | `404` | `get_book` fonksiyonu | `43` bir kitap kimliği olabilir, ama listede böyle bir kitap yok. Bunu bilmek için kitaplara bakmak gerekti. |
| `Ece again` | Ece'nin ikinci yorumu | `409` | `create_review` fonksiyonu | Ece'nin 42 numaralı kitaba yorumu sunucu başlarken zaten var. |
| `Can first` | Can'ın ilk yorumu | `201` | Kimse | Can'ın bu kitaba yorumu yoktu. |
| `Can again` | Can'ın ikinci yorumu | `409` | `create_review` fonksiyonu | Az önce eklenen yorumla çakışıyor. |

Bölüm 0'daki soruya, "Bir kuralı nereye yazmalıyım?" sorusuna, şimdi bu haftanın kurallarıyla cevap verebiliriz. Bir istek üç ayrı kontrolden geçebilir:

| Kontrol | Bu haftanın örnekleri | Kim kontrol eder? | Nereye yazdık? | Yanıt |
|---|---|---|---|---|
| **Tür ve alanlar** | `"title": 123`, `"rating": "4.5"`, `"available": "yes"`, modelde olmayan `isbn` alanı | FastAPI (Pydantic ile), fonksiyondan önce | Alanın türüne (`title: str`) ve modelin ayarına (`strict=True`, `extra="forbid"`) | `422` |
| **Değer** | Boş ad, `9` puan, `/books/-5` | FastAPI (Pydantic ile), fonksiyondan önce | Alana: `Field(...)`; parametreye: `Path(...)` | `422` |
| **Veriye bağlı** | `/books/43`, aynı okurun ikinci yorumu | Bizim fonksiyonumuz | Fonksiyonun içine: `raise HTTPException(...)` | `404`, `409` |

İlk iki kontrolün kurallarına bakarak Pydantic karar verir; FastAPI onu istek fonksiyona ulaşmadan çağırır. Kurala uymayan istek fonksiyonu hiç çalıştırmaz.

> **Ana fikir:** Değerin kendisine bakarak karar verilebilen kurallar modele ya da parametreye yazılır; FastAPI bunları fonksiyondan önce kontrol eder ve `422` döndürür. Sunucudaki veriye bakmayı gerektiren kurallar fonksiyonun içine yazılır ve uygun durum koduyla (`404`, `409`) bildirilir.

---

## Deney 6 — İstemcide hata yanıtını göstermek

**Amaç:** İstemcinin, sunucudan gelen hata yanıtlarını kullanıcıya okunur biçimde göstermesini sağlamak.

Bu deney ödev: Derste zaman kalmazsa evde yap. Yalnızca istemciyi değiştirir; sunucuya dokunmaz.

Deney 5'in çıktısında iki farklı hata yanıtı biçimi var:

| Kim üretti? | `detail` alanı | Örnek |
|---|---|---|
| FastAPI (`422`) | Bir **liste**: her öğe bir hata | `[{'type': 'greater_than', 'loc': ['path', 'book_id'], ...}]` |
| Bizim fonksiyonumuz (`404`, `409`) | Bir **metin** | `'Book not found'` |

İstemci iki biçimi de okuyabilmeli. Hangisinin geldiğini durum kodundan anlayabilir: `422` ise `detail` bir liste, değilse bir metin.

### 6.1 İstemciyi yaz

`client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"


# Hata yanıtını okunur biçimde yazar.
def show_error(response):
    detail = response.json()["detail"]

    if response.status_code == 422:
        # FastAPI'nin 422 yanıtı: detail bir liste.
        for error in detail:
            place = error["loc"][0]
            field = error["loc"][1:]
            print(f"   {place} -> {field}: {error['msg']}")
    else:
        # Bizim yazdığımız hata: detail bir metin.
        print(f"   {detail}")


try:
    review = {"reader": "", "comment": "Güzel.", "score": 9}
    response = httpx.post(base_url + "/books/42/reviews", json=review)
    print("Review with two errors:", response.status_code)
    show_error(response)

    review = {"reader": "Ece", "comment": "Tekrar okudum.", "score": 4}
    response = httpx.post(base_url + "/books/42/reviews", json=review)
    print("Second review by Ece:", response.status_code)
    show_error(response)

    response = httpx.get(base_url + "/books/43")
    print("Book 43:", response.status_code)
    show_error(response)

    response = httpx.get(base_url + "/books/-5")
    print("Book -5:", response.status_code)
    show_error(response)

    # Etiket listesinin 2. öğesi metin değil.
    book = {
        "title": "Etiketleri Bozuk Kitap",
        "author": {"first_name": "Ada", "last_name": "Yıldız"},
        "available": True,
        "tags": ["http", 5]
    }
    response = httpx.post(base_url + "/books", json=book)
    print("Book with a bad tag:", response.status_code)
    show_error(response)
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

| Kod | Ne yapar? |
|---|---|
| `response.status_code == 422` | Hatayı FastAPI mi üretti? Bizim fonksiyonlarımız `404` ve `409` döndürüyor; `422` yalnızca FastAPI'den geliyor. |
| `error["loc"][0]` | `loc` listesinin ilk öğesi: `body`, `path` ya da `query`. |
| `error["loc"][1:]` | `loc` listesinin ilk öğesinden sonraki bütün öğeleri, yine bir liste olarak: hatalı alanın yeri. `['body', 'tags', 1]` için `['tags', 1]`. |
| `f"   {place} -> {field}: ..."` | Değerleri metnin içine yerleştirir. |

### 6.2 Çalıştır

Sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Review with two errors: 422
   body -> ['reader']: String should have at least 1 character
   body -> ['score']: Input should be less than or equal to 5
Second review by Ece: 409
   This reader has already reviewed this book
Book 43: 404
   Book not found
Book -5: 422
   path -> ['book_id']: Input should be greater than 0
Book with a bad tag: 422
   body -> ['tags', 1]: Input should be a valid string
```

İstemci her hatayı tek satırda gösteriyor. `422` yanıtlarında hatanın isteğin hangi bölümünde ve hangi alanda olduğu da görünüyor; kullanıcı neyi düzeltmesi gerektiğini buradan okuyabilir. Son satırdaki `['tags', 1]`, hatanın `tags` listesinin 1. sıradaki öğesinde olduğunu söylüyor; Python'da sıra 0'dan başladığı için bu, listenin ikinci öğesi olan `5`.

> **Ana fikir:** Hata yanıtı istemci için de bir veridir. FastAPI'nin `422` yanıtında `detail` bir liste, bizim `HTTPException` ile ürettiğimiz yanıtlarda bir metindir. İstemci ikisini ayırıp okunur bir mesaja çevirebilir.

---

## 7. Bu haftanın sonundaki `server.py`

Deney 5'ten sonra `server.py` dosyasının tamamı şöyle olmalı (Deney 6 yalnızca istemciyi değiştirdi). Hafta 6'ya bu dosyayla başlayacağız.

```python
from fastapi import FastAPI, HTTPException, Path, Response
from pydantic import BaseModel, ConfigDict, Field


class Author(BaseModel):
    first_name: str
    last_name: str


class BookCreate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    title: str = Field(min_length=1)
    author: Author
    available: bool
    tags: list[str]
    rating: float | None = Field(default=None, ge=0, le=5)


class BookPublic(BookCreate):
    model_config = ConfigDict(strict=False, extra="ignore")

    id: int


class BookUpdate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    title: str = Field(default=None, min_length=1)
    author: Author = None
    available: bool = None
    tags: list[str] = None
    rating: float | None = Field(default=None, ge=0, le=5)


class ReviewCreate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    reader: str = Field(min_length=1)
    comment: str = Field(min_length=1)
    score: int = Field(ge=1, le=5)


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
        "rating": None,
        "internal_note": "Kapağı yıpranmış, yenisi sipariş edildi."
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
@app.get("/books", response_model=list[BookPublic])
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
@app.get("/books/{book_id}", response_model=BookPublic)
def get_book(book_id: int = Path(gt=0)):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")


# Yeni kitap: listeye ekler, 201 ve Location döner.
@app.post("/books", status_code=201, response_model=BookPublic)
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


# Kitabı silme: listeden çıkarır, 204 döner; kitap yoksa 404.
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int = Path(gt=0)):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return

    raise HTTPException(status_code=404, detail="Book not found")


# Kitabı tümüyle değiştirme: bütün alanlar yenisiyle değişir; kitap yoksa 404.
@app.put("/books/{book_id}", response_model=BookPublic)
def replace_book(book_data: BookCreate, book_id: int = Path(gt=0)):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            new_book = book_data.model_dump()
            new_book["id"] = book_id
            books[index] = new_book
            return new_book

    raise HTTPException(status_code=404, detail="Book not found")


# Kitabın bir kısmını değiştirme: yalnızca gönderilen alanlar değişir; kitap yoksa 404.
@app.patch("/books/{book_id}", response_model=BookPublic)
def update_book(book_data: BookUpdate, book_id: int = Path(gt=0)):
    for book in books:
        if book["id"] == book_id:
            changes = book_data.model_dump(exclude_unset=True)
            book.update(changes)
            return book

    raise HTTPException(status_code=404, detail="Book not found")


# Kitabın yorumları: kitap yoksa 404.
@app.get("/books/{book_id}/reviews")
def get_reviews(book_id: int = Path(gt=0)):
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


# Yeni yorum: kitaba ekler, 201 döner; kitap yoksa 404, okurun bu kitaba yorumu varsa 409.
@app.post("/books/{book_id}/reviews", status_code=201)
def create_review(review_data: ReviewCreate, book_id: int = Path(gt=0)):
    book_exists = False
    for book in books:
        if book["id"] == book_id:
            book_exists = True

    if not book_exists:
        raise HTTPException(status_code=404, detail="Book not found")

    for review in reviews:
        if review["book_id"] == book_id and review["reader"] == review_data.reader:
            raise HTTPException(status_code=409, detail="This reader has already reviewed this book")

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

Hafta 3'teki 8.3 ya da Hafta 4'teki 5.3 alıştırmalarını yaptıysan, `get_review` ve `delete_review` fonksiyonların da dosyada kalır. Onların `book_id` ve `review_id` parametrelerine de `Path(gt=0)` ekleyebilirsin.

---

## 8. Ödev: belge ve kendi kuralını yazmak

Bu bölümü, Deney 6 ile birlikte evde tamamla.

### 8.1 Kuralları API'nin şemasında görmek

FastAPI, modellerden API'nin bir tarifini, yani **şemasını** kendiliğinden üretir; `/docs` sayfası da bu şemadan hazırlanır. Sunucu çalışırken şemayı görmek için tarayıcıda şu adresi aç:

```text
http://127.0.0.1:8000/openapi.json
```

Tarayıcı JSON'u düzenli gösterir; gerekirse sayfanın üstündeki **Pretty-print** kutusunu işaretle. `components` → `schemas` → `BookCreate` bölümünde yazdığımız kurallar var:

| Alan | Şemada görünen | Kodumuzdaki kural |
|---|---|---|
| `title` | `{"type":"string","minLength":1,...}` | `Field(min_length=1)` |
| `rating` | `{"type":"number","maximum":5.0,"minimum":0.0}` ya da `{"type":"null"}` | `float \| None = Field(default=None, ge=0, le=5)` |
| Modelin kendisi | `"additionalProperties":false` | `extra="forbid"` |

Aynı bilgiler `http://127.0.0.1:8000/docs` sayfasının altındaki **Schemas** bölümünde de görünür. Bu sayfada `POST /books` işleminde **Try it out** düğmesine bas, gövdedeki `rating` değerini `7` yap ve isteği gönder; `422` yanıtını ve `detail` listesini sayfada görürsün. Sayfa bu yanıtı `Validation Error`, yani doğrulama hatası olarak adlandırır.

### 8.2 `README.md` belgesine alan kurallarını eklemek

Hafta 3'te yazdığın `README.md` belgesini kullanan biri, bir isteğin neden reddedildiğini belgeden öğrenebilmeli. Belgenin sonuna şu bölümü ekle:

```markdown
## Alan kuralları

Kurala uymayan istekler `422 Unprocessable Entity` ile reddedilir. Yanıttaki `detail` listesi her hatanın yerini (`loc`) ve açıklamasını (`msg`) verir.

| Alan | Kural |
|---|---|
| Kitap: `title` | Boş olamaz. `PATCH` isteğinde gönderilmeyebilir, ama `null` olamaz. |
| Kitap: `rating` | 0 ile 5 arasında bir sayı ya da `null` |
| Yorum: `reader`, `comment` | Boş olamaz. |
| Yorum: `score` | 1 ile 5 arasında bir tam sayı |
| Bütün gövdeler | Değerler kendi türünde gönderilmeli: `"4.5"` metni sayı yerine geçmez. Tabloda olmayan alanlar kabul edilmez. |
| Yol: `book_id` | 0'dan büyük bir tam sayı olmalı. |

Aynı okur aynı kitaba ikinci kez yorum yazarsa yanıt `409 Conflict` olur.
```

### 8.3 Kendin yaz: yazarın adı boş olmasın

Şu an bir kitabın yazarı `{"first_name": "", "last_name": ""}` olabiliyor; yazara fazladan bir alan da gönderilebiliyor ve sessizce atılıyor.

**İstenenler:**

1. Yazarın adı (`first_name`) ve soyadı (`last_name`) boş olamasın.
2. Yazar nesnesinde modelde olmayan bir alan gönderilirse istek reddedilsin.

**İpucu:** Değiştirmen gereken tek model `Author`. Deney 2 ve Deney 3'te öteki modellere yaptığını bu modele uygula.

**Kontrol et:** Sunucuyu yeniden başlat ve istekleri gönder. Sonuçlar şöyle olmalı:

| İstek | Durum kodu | `loc` |
|---|---|---|
| `POST /books`, yazar `{"first_name": "", "last_name": "Yıldız"}` | `422` | `['body', 'author', 'first_name']` |
| `POST /books`, yazar `{"first_name": "Ada", "last_name": "Yıldız", "middle_name": "Su"}` | `422` | `['body', 'author', 'middle_name']` |
| `POST /books`, yazar `{"first_name": "Ada", "last_name": "Yıldız"}` | `201` | Yok |
| `GET /books` | `200` | Yok |

Son satır önemli: Kuralı ekledikten sonra kitapları okumak hâlâ çalışmalı.

Kodunu yazıp denedikten sonra [ek nottaki cevapla](09_Supplement_Exercise_8_3_Answer.md) karşılaştır.

### 8.4 Kendin yaz: üst sınırlar

Şimdiye kadar yalnızca alt sınır yazdık. Oysa bir kitabın adı on bin karakter olabiliyor, etiket listesine de yüzlerce etiket eklenebiliyor. Üst sınırları da `Field` yazar: Metin için `max_length` en fazla karakter sayısını, liste için de en fazla öğe sayısını belirler.

**İstenenler:**

1. Kitabın adı en fazla 100 karakter olsun.
2. Bir kitabın en fazla 5 etiketi olsun.
3. İki kural `PATCH` isteklerinde de geçerli olsun.

**İpucu:** `BookCreate` ve `BookUpdate` modellerini değiştirmen gerekiyor. Kuralları yazmadan önce [kuralların yanıt modeline geçtiği ek notun](05_Supplement_Inherited_Rules.md) sonundaki iki soruyu sor: Sunucudaki kitaplar bu kurallara uyuyor mu?

**Kontrol et:** Sunucuyu yeniden başlat ve istekleri gönder. Sonuçlar şöyle olmalı:

| İstek | Durum kodu | `loc` |
|---|---|---|
| `POST /books`, 101 karakterlik bir ad | `422` | `['body', 'title']` |
| `POST /books`, 6 etiket | `422` | `['body', 'tags']` |
| `POST /books`, 100 karakterlik bir ad ve 5 etiket | `201` | Yok |
| `PATCH /books/42`, 6 etiket | `422` | `['body', 'tags']` |
| `GET /books` | `200` | Yok |

Kodunu yazıp denedikten sonra [ek nottaki cevapla](10_Supplement_Exercise_8_4_Answer.md) karşılaştır.

---

## 9. Kendini kontrol et: Bu haftanın yedi sorusu

1. Bir istek hangi üç kontrolden geçebilir? Hangileri istek fonksiyona ulaşmadan yapılır?
2. `422` yanıtında `'loc': ['path', 'book_id']` ne söyler?
3. Kitap puanının alt sınırını `ge=1` yapsaydık 57 numaralı kitap neden okunamazdı?
4. `strict=True` eklenmeden önce `"available": "yes"` neden kabul ediliyordu?
5. `extra="forbid"` eklenince 42 numaralı kitabı okuyan istek neden `500` aldı? Nasıl düzelttik?
6. `BookUpdate` modelinde `title: str = None` yazımıyla `title: str | None = None` yazımı arasındaki fark nedir?
7. `/books/-5` neden `422`, `/books/43` neden `404` alıyor? Aynı okurun ikinci yorumunu reddeden kural neden modelde değil de fonksiyonda?

### 9.1 Soruların cevapları

1. Tür ve alanlar, değer ve veriye bağlı kontrol. Tür ve alan kontrolüyle değer kontrolünü FastAPI, Pydantic'i çağırarak, istek fonksiyona ulaşmadan yapar ve `422` döndürür. Veriye bağlı kontrolü fonksiyonun kendisi yapar ve `404` ya da `409` gibi bir durum koduyla bildirir.
2. Hatanın bir yol parametresinde (`path`), `book_id` parametresinde olduğunu söyler.
3. `BookPublic` modeli `BookCreate` modelinden türediği için kurallar yanıt modeline de geçer. 57 numaralı kitabın puanı `0`; yanıt hazırlanırken bu değer `ge=1` kuralına uymaz ve istemciye `500` gider.
4. Pydantic, varsayılan olarak bazı değerleri alanın türüne çevirir; `"yes"` metnini `True` yapar. `strict=True` bu çeviriyi kapatır; değer alanın türünde gönderilmelidir.
5. `BookPublic` modeli `BookCreate` modelinin `extra="forbid"` ayarını da aldı. 42 numaralı kitabın sözlüğünde modelde olmayan `internal_note` alanı vardı; yanıt modeli bu alanı süzmek yerine reddetti. `BookPublic` modeline `model_config = ConfigDict(strict=False, extra="ignore")` ekleyerek fazla alanların yine süzülmesini sağladık; sıkı modu da yanıt modelinde kapattık.
6. İkisinde de alan gönderilmeyebilir. `title: str | None = None` yazımında `null` da kabul edilir ve kitabın adı `None` olabilir. `title: str = None` yazımında gönderilen değer metin olmalıdır; `null` gönderilirse istek `422` ile reddedilir. Varsayılan değer kontrol edilmediği için alan gönderilmeyince bir sorun çıkmaz.
7. `-5` hiçbir zaman kitap kimliği olamaz; bunu bilmek için değere bakmak yeter, bu yüzden `Path(gt=0)` kuralı istek fonksiyona ulaşmadan `422` döndürür. `43` bir kitap kimliği olabilir ama listede yoktur; bunu ancak kitaplara bakan fonksiyon bilir ve `404` döndürür. İkinci yorum için de okurun daha önce yorum yazıp yazmadığına, yani `reviews` listesine bakmak gerekir; model yalnızca gelen yorumu gördüğü için bu kural fonksiyona yazılır.

---

## 10. Resmî belgeler

- [FastAPI — Body: Fields](https://fastapi.tiangolo.com/tutorial/body-fields/)
- [FastAPI — Path Parameters and Numeric Validations](https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/)
- [FastAPI — Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Pydantic — Fields](https://docs.pydantic.dev/latest/concepts/fields/): Bu sayfada alanlara yazdığımız kurallara *constraint* denir.
- [Pydantic — Strict Mode](https://docs.pydantic.dev/latest/concepts/strict_mode/): Bu sayfada varsayılan davranışa *lax mode*, değerlerin türe çevrilmesine *coerce* denir.
- [Pydantic — Configuration: `extra`](https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.extra)
- [MDN — 422 Unprocessable Content](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/422)
- [MDN — 409 Conflict](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/409)

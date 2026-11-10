# Hafta 05 — Ders Anlatımı

Bu dosya, [uygulama föyünü](02_Practice.md) bölüm bölüm, bir öğretmenin anlatacağı gibi anlatır. Kısa cümlelerle yazıldı; sesli okumaya uygundur. Her bölümü föydeki aynı bölümle birlikte oku.

---

## Bölüm 0: Kural kimin işi?

### Bugünkü durum

Hafta 2'den beri sunucumuz bazı hatalı istekleri reddediyor. Örneğin kitabın adını metin yerine sayı olarak gönderdiğini düşün: `"title": 123`. Sunucu bu isteği `422` ile reddeder. Kitap eklenmez.

Ama sunucu hâlâ bazı hatalı değerleri kabul ediyor. Adı boş olan bir kitap eklenebiliyor. Puanı 9 olan bir yorum da eklenebiliyor. Oysa puan 1 ile 5 arasında olmalı.

Bunun nedeni şu: Sunucu şimdilik yalnızca **türe** bakıyor. Boş bir ad da sonuçta bir metin. 9 da bir sayı. Türleri doğru olduğu için ikisi de geçiyor.

Bu hafta bu değerleri reddeden kurallar yazacağız.

### Haftanın sorusu

Haftanın sonunda şu soruya cevap verebileceksin: **Bir kuralı nereye yazmalıyım?**

Bunun için kuralları ikiye ayıracağız.

**Birinci grup:** Gelen değere bakmak yeten kurallar. Boş bir metin buna örnek. Beşten büyük bir puan da öyle. Bunlara karar vermek için sunucudaki verilere bakmak gerekmez.

**İkinci grup:** Sunucudaki veriye bakmayı gerektiren kurallar. Örneğin "43 numaralı kitap var mı?" sorusu. 43 sayısında bir sorun yok. Ama böyle bir kitabın olup olmadığını öğrenmek için kitap listesine bakmak gerekiyor.

Birinci gruptaki kuralları FastAPI, bizim fonksiyonumuz çalışmadan önce kontrol edebilir. İkinci gruptakileri ise yalnızca bizim fonksiyonumuz bilebilir.

Bu ayrımı Deney 5'in sonunda bir tabloda toplayacağız.

### Haftanın planı

Bu hafta altı deney yapacağız:

- **Deney 1:** Sunucunun bugün hangi hatalı değerleri kabul ettiğini göreceğiz. Hata yanıtını da okumayı öğreneceğiz.
- **Deney 2:** Boş metinleri ve aralık dışındaki puanları reddedeceğiz.
- **Deney 3:** Türleri sıkılaştıracağız. Modelde olmayan alanları da reddedeceğiz.
- **Deney 4:** `PATCH` isteğinde zorunlu bir alana `null` gönderilirse bunu reddedeceğiz.
- **Deney 5:** Bir kuralın modele mi, fonksiyona mı yazılacağına karar vereceğiz.
- **Deney 6:** Bu bir ödev. Hata yanıtını istemcide okunur biçimde göstereceğiz.

### 0.1 Başlangıç dosyaları

Hafta 4'ün sonundaki dosyalarla başlıyoruz.

`server.py` dosyası, Hafta 4'teki Deney 4'ün sonundaki hâliyle olmalı. Yani dekoratörlerinde `response_model` olan sunucu.

`client.py` dosyasını ise her deneyde baştan yazacağız.

Kendi `server.py` dosyandan emin değilsen, bu haftanın [başlangıç dosyasını](Starting_Code/server.py) kullan. Föydeki çıktılar o dosyayla alındı. Bu dosyada iki şey önemli: 42 numaralı kitapta `internal_note` diye bir alan var. Bir de Ece'nin yazdığı bir yorum var. Deney 3 ve Deney 5 bunlara dayanıyor.

Hafta 4'te `delete_review` fonksiyonunu yazdıysan, o da dosyada kalabilir. Bu haftanın değişiklikleriyle çakışmaz.

### Sunucuyu yeniden başlatmak

Sunucu her başlatıldığında dosyada yazılı üç kitapla ve bir yorumla başlar. İstemcinin eklediği kitaplar ve yorumlar bellekte durur. Sunucuyu yeniden başlatınca bunlar silinir.

Bu yüzden deneylerde sık sık "sunucuyu yeniden başlat" diyeceğiz. Bu adımı atlarsan, çıktıların föydekilerden farklı olabilir.

---

## Deney 1: Sunucu bugün neyi kabul ediyor?

Kural yazmadan önce sunucunun bugün ne yaptığını bilmemiz gerekiyor. Bir doktor da önce muayene eder, sonra ilaç yazar. Bu deneyde biz de sunucuyu muayene ediyoruz.

Deneyin iki parçası var. Önce sunucuya hatalı değerler göndereceğiz ve hangilerini kabul ettiğine bakacağız. Sonra reddettiği isteklerin hata yanıtını baştan sona okuyacağız.

### 1.1 Hatalı değerler göndermek

Yöntemimiz basit. Elimizde doğru bir kitap var. Her istekte bu kitabın yalnızca bir alanını bozuyoruz ve kitabı `POST /books` ile gönderiyoruz. Sunucu bir isteği reddederse, nedeninin hangi alan olduğunu böylece biliyoruz.

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

Kodda bizim için yeni olan birkaç parça var. Sırayla bakalım.

`send_book` fonksiyonu üç şey alır: ekranda görünecek bir etiket, bozacağımız alanın adı ve o alana koyacağımız değer.

`new_book.copy()`, kitap sözlüğünün bir kopyasını oluşturur. Değişikliği bu kopyada yapıyoruz. Böylece asıl `new_book` sözlüğü hiç bozulmuyor ve her istek temiz bir kitapla başlıyor.

`body[field] = value`, kopyada tek bir alanı değiştirir. Alan sözlükte yoksa yeni bir alan ekler. `isbn` satırında bunu kullanıyoruz.

İstek kabul edilirse, yani durum kodu `201` ise, sunucunun kaydettiği değeri yazdırıyoruz. Bunun için `response.json().get(field)` kullanıyoruz. `get`, alan yanıtta yoksa hata vermez, `None` verir.

`repr(...)`, değeri tırnaklarıyla birlikte yazar. Bu sayede boş metni ekranda `''` olarak görebiliyoruz. `repr` olmasaydı boş metin ekranda hiç görünmezdi.

İstek reddedilirse, hata yanıtındaki ilk açıklamayı yazdırıyoruz: `response.json()["detail"][0]["msg"]`. Bu yazımın ne demek olduğunu 1.2'de göreceğiz.

En sonda bir de yorum gönderiyoruz. Yorumun puanı 9; okuru ve yorum metni boş.

Sunucuyu yeniden başlat ve istemciyi çalıştır. Şu çıktıyı görmelisin:

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

Dokuz istek gönderdik. Yalnızca biri reddedildi. Satırlara gruplar hâlinde bakalım.

**Boş ad ve boşluklu ad.** İkisi de kabul edildi. Artık katalogda adı olmayan kitaplar var.

**Puan 7 ve puan -1.** İkisi de kabul edildi. Oysa kitap puanı 0 ile 5 arasında olmalı. Küçük bir ayrıntı: `7` gönderdik, sunucu `7.0` kaydetti. Çünkü modelde `rating` alanının türü `float`, yani ondalıklı sayı.

**Metin olarak puan: `"4.5"`.** Bu bir sayı değil, tırnak içinde bir metin. Sunucu bunu sayıya çevirdi ve `4.5` kaydetti. İlk bakışta yardımsever bir davranış gibi görünüyor. Ama sorun şu: İstemci yanlış türde değer gönderdiğini hiç fark etmiyor.

**`"yes"` metni.** Aynı durum. `available` alanı `true` ya da `false` bekliyor. Sunucu `"yes"` metnini `True` yaptı.

**Bilinmeyen alan: `isbn`.** Modelimizde böyle bir alan yok. Sunucu kitabı ekledi, ama `isbn` alanını sessizce attı. Çıktıda `stored: None` görmemizin nedeni bu: Kaydedilen kitapta bu alan yok, `get` de bu yüzden `None` verdi. İstemci alanın kaydedildiğini sanıyor ve hiçbir hata almıyor.

**Sayı olarak ad: `123`.** Reddedilen tek istek bu. Modelde `title: str` yazıyor, yani ad bir metin olmalı. Tür kontrolü çalıştı ve sunucu `422` döndü.

**Puanı 9 olan yorum.** Kabul edildi. Okur ve yorum metni de boş. Üç sorun birden var, ama sunucu hiçbirini fark etmedi.

Burada önemli bir not var. `"4.5"`, `"yes"` ve `isbn` satırlarındaki davranışlar bir hata değil. Bunlar Pydantic'in bilerek seçtiği varsayılan davranışlar ve birçok API böyle çalışır. Bizim API'mizde neden değiştireceğimizi Deney 3'te konuşacağız. Pydantic'in başka hangi değerleri çevirdiğini merak edersen [ek nota](03_Supplement_Lax_Type_Conversion.md) bakabilirsin.

### 1.2 Hata yanıtını okumak

Reddedilen tek istek `"title": 123` idi. Şimdi bu hata yanıtının tamamına bakalım.

Hata yalnızca gövdede olmaz. Yol parametresinde ve sorgu parametresinde de olabilir; bunları Hafta 1'de görmüştük. Bu yüzden üç ayrı yerde hata yapan üç istek gönderiyoruz:

- **Gövdede hata:** Kitabın adı yine `123`.
- **Yol parametresinde hata:** `/books/abc`. Kitap kimliği bir sayı olmalı, `abc` sayı değil.
- **Sorgu parametresinde hata:** `?available=maybe`. `available` için `true` ya da `false` bekleniyor, `maybe` ikisi de değil.

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

Üç yanıta dikkatle bak. Üçünün de durum kodu `422`. Gövdeleri de aynı biçimde.

Yanıtta `detail` adında bir alan var. Değeri köşeli parantezle başlıyor ve köşeli parantezle bitiyor. Bu, onun bir **liste** olduğunu gösterir. Listenin her öğesi bir hatayı anlatır. Bu isteklerin her birinde tek hata olduğu için listelerde tek öğe var. Bir istekte birden fazla hata olunca hepsi bu listede sıralanır. Bunu Deney 2'de göreceğiz.

Şimdi bir hatanın parçalarına `"title": 123` örneği üzerinden bakalım.

- **`type`:** Hatanın türünün kısa adı. Burada `string_type`, yani "metin bekleniyordu".
- **`loc`:** Hatanın nerede olduğu. Burada `['body', 'title']`. İlk öğe isteğin hangi bölümü olduğunu, son öğe hangi alan olduğunu söyler. Yani "gövdedeki `title` alanı".
- **`msg`:** Hatanın insanlar için yazılmış açıklaması. Burada `Input should be a valid string`. Bu metni biz yazmadık; Pydantic üretiyor.
- **`input`:** İstemcinin gönderdiği değer. Burada `123`.

Artık 1.1'deki `["detail"][0]["msg"]` yazımını da okuyabiliriz: `detail` listesini al, listenin ilk öğesini, yani ilk hatayı al, o hatanın `msg` parçasını al.

`loc` alanının ilk öğesine biraz daha yakından bakalım. Üç farklı değer alabiliyor:

- **`body`**, yani **gövde (body)**. `json=` ile gönderdiğimiz veri. İlk istekte hata buradaydı.
- **`path`**, yani **yol parametresi (path parameter)**. Adresin yolundaki değer: `/books/abc` içindeki `abc`.
- **`query`**, yani **sorgu parametresi (query parameter)**. `params=` ile gönderdiğimiz, adreste soru işaretinden sonra gelen değer: `?available=maybe`.

Bu kavramları daha önce görmüştük. Hafta 1'de adresin parçalarına ad verdik: `/books/abc` kısmı yol, soru işaretinden sonrası sorgu. Bu parçaların içindeki değerlere de parametre diyoruz. Hafta 3'te de sorgu ile gövde arasındaki farkı konuşmuştuk.

Son olarak durum kodunun adına bakalım. `422` kodunun adı sunucunun terminalinde `422 Unprocessable Entity` olarak görünür. HTTP standardının güncel sürümü bu koda `Unprocessable Content` diyor ve Python 3.13 ve sonrasıyla çalışan sunucular bu yeni adı yazar. İki ad da aynı kodu anlatır.

Bazı API'ler benzer hatalar için `400` kullanır. Aradaki farkı [ek notta](04_Supplement_400_vs_422.md) bulabilirsin.

### Ana fikir

Sunucu şu an yalnızca türü yanlış olan değerleri reddediyor. Türü doğru ama anlamsız olan değerler kabul ediliyor; boş ad ve 9 puan gibi. Modelde olmayan alanlar da sessizce atılıyor.

Reddedilen her istekte `422` yanıtı gelir. Bu yanıttaki `detail` listesi iki şey söyler: Hatanın ne olduğunu `msg` söyler, nerede olduğunu `loc` söyler.

---

## Deney 2: Değer sınırları: `Field`

Deney 1'de sunucunun yalnızca türe baktığını gördük. Şimdi türün yanına **değer kuralları** ekleyeceğiz.

Bu kuralları önceki haftalarda bu haftaya bırakmıştık. Hafta 2'de "kitabın adı boş olmasın" demiştik. Hafta 3'te de "yorumun puanı 1 ile 5 arasında olsun" demiştik. Bu tür kuralları Pydantic'in `Field` fonksiyonuyla yazıyoruz. Kural, modeldeki alanın hemen yanına yazılır.

### 2.1 Modellere kuralları ekle

`server.py` dosyasında önce import satırını değiştiriyoruz:

```python
from pydantic import BaseModel, Field
```

Böylece `Field` fonksiyonunu kullanabiliriz. Sonra üç modelin alanlarını değiştiriyoruz. Değişen modellerin yeni hâli şöyle:

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

Kuralların anlamına bakalım.

`Field(min_length=1)`, metnin en az 1 karakter olması gerektiğini söyler. Boş metin `""` artık reddedilir.

`Field(ge=0, le=5)`, sayının 0 ile 5 arasında olması gerektiğini söyler. `ge`, İngilizce *greater than or equal* sözlerinin kısaltması: "büyük ya da eşit". `le` ise *less than or equal*: "küçük ya da eşit". Sınırların kendisi de kabul edilir; yani 0 da 5 de geçerli.

`Field(default=None, ...)` ise alanın **varsayılan değeri (default value)**. Eskiden `= None` yazıyorduk. Şimdi eşittir işaretinin sağında `Field(...)` var ve oraya ikinci bir değer yazılamaz. Bu yüzden varsayılan değer `Field` içine, `default=None` olarak giriyor. Anlamı değişmedi: Alan gönderilmezse değeri `None` olur.

Şimdi üç soruya cevap verelim.

**Kitap puanının alt sınırı neden 0, neden 1 değil?** Çünkü sunucuda 57 numaralı kitabın puanı zaten 0. Alt sınırı 1 yapsaydık bu kitap okunamaz olurdu. Nedeni şu: Kurallar, `BookCreate` modelinden türeyen yanıt modeline, yani `BookPublic` modeline de geçiyor. Bunu [ek notta](05_Supplement_Inherited_Rules.md) deneyerek görebilirsin. Aynı "miras" konusuyla Deney 3'te bir kez daha karşılaşacağız.

Bu arada yorum puanının sınırı farklı: 1 ile 5 arası. Yorumlar için böyle eski bir veri yok; Ece'nin yorumu 5 puanlı.

**`BookUpdate` modeline neden aynı kuralları yazdık?** Çünkü `PATCH` istekleri bu modelle kontrol ediliyor. Kural eklemeseydik, `POST` ile boş ad gönderilemezdi ama `PATCH` ile gönderilebilirdi. Kapıyı bir yerden kapatıp öteki yerden açık bırakmış olurduk.

**`BookUpdate` modelindeki `| None` ne olacak?** Şimdilik kalıyor. Deney 4'te ele alacağız.

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

Önce yeni mesajlara bakalım. `String should have at least 1 character` gibi metinler ne sunucuda ne istemcide yazıyor. Biz sunucuya yalnızca `min_length=1` gibi bir kural yazdık. Değer kurala uymayınca mesajı Pydantic kendisi üretiyor. FastAPI bu mesajı yanıtın `msg` alanına koyuyor. İstemci de onu `["detail"][0]["msg"]` ile alıp yazdırıyor.

Şimdi satırlara bakalım.

**Boş ad.** Artık `422` alıyor. `min_length=1` kuralı çalıştı.

**Boşluklu ad.** Hâlâ `201` alıyor. Üç boşluk da bir metin ve uzunluğu 3. Yani en az 1 karakter kuralına uyuyor. Bunu reddetmenin yolu [ek notta](06_Supplement_Blank_Strings.md).

**Puan 7 ve puan -1.** İkisi de artık `422` alıyor. 7, `le=5` kuralına; -1 de `ge=0` kuralına takıldı.

**Metin olarak puan: `"4.5"`.** Hâlâ `201` alıyor. Burada önemli bir sıra var: Pydantic önce türe bakar, gerekirse değeri çevirir; sonra kurala bakar. `"4.5"` metni önce `4.5` sayısına çevrildi. Bu sayı 0 ile 5 arasında olduğu için kurala da uydu. Çeviriyi durdurmak Deney 3'ün işi.

**`"yes"` metni.** Hâlâ `201` alıyor. `available` alanına hiç kural eklemedik.

**Bilinmeyen alan: `isbn`.** Hâlâ `201` alıyor. Kuralları yalnızca modeldeki alanlara yazdık. Modelde olmayan bir alana kural yazamayız. Bu da Deney 3'ün işi.

**Sayı olarak ad.** Zaten Deney 1'de de `422` alıyordu. Yeni kural bunu değiştirmedi.

**Puanı 9 olan yorum.** Artık `422` alıyor. Ama dikkat: Bu yorumda üç alan birden kurala uymuyordu. Çıktıda yalnızca ilk hata görünüyor, çünkü istemci yalnızca listenin ilk öğesini yazdırıyor. Hepsine şimdi bakacağız.

### 2.3 Bir istekte birden fazla hata

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

Bu kez `detail` listesinin yalnızca ilk öğesini değil, bütün öğelerini yazdırıyoruz. `for` döngüsü listedeki her hatayı sırayla alıyor.

Sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Status: 422
{'type': 'string_too_short', 'loc': ['body', 'reader'], 'msg': 'String should have at least 1 character', 'input': '', 'ctx': {'min_length': 1}}
{'type': 'string_too_short', 'loc': ['body', 'comment'], 'msg': 'String should have at least 1 character', 'input': '', 'ctx': {'min_length': 1}}
{'type': 'less_than_equal', 'loc': ['body', 'score'], 'msg': 'Input should be less than or equal to 5', 'input': 9, 'ctx': {'le': 5}}
```

FastAPI üç hatayı tek bir yanıtta listeledi. Bu, istemci için çok kullanışlı. Bir formu düşün: Üç kutuyu yanlış doldurmuşsun. Sistem sana hatalarını tek tek, her seferinde bir tane söylese, formu üç kez göndermen gerekirdi. Burada ise hepsini tek seferde öğreniyorsun.

Hatalarda yeni bir parça da var: `ctx`. Bu, İngilizce *context* sözünün kısaltması; hatanın **bağlamı** demek. Hangi kuralın bozulduğunu söyler. `{'min_length': 1}` "en az 1 karakter" kuralı, `{'le': 5}` de "en fazla 5" kuralı.

Deney 1'deki hatalarda `ctx` yoktu. Çünkü onlar tür hatalarıydı ve tür hatalarında `min_length` ya da `le` gibi bir sınır yok.

### Ana fikir

`Field` ile modeldeki alana kural yazılır. Metin için `min_length`, sayı için `ge` ve `le` kullanılır.

Kurala uymayan değer, türü doğru olsa bile `422` ile reddedilir. Bir istekteki bütün hatalar aynı yanıtta listelenir.

---

## Deney 3: Türü ve alanları sıkılaştırmak

Deney 2'den sonra üç sorun kaldı. `"4.5"` metni puan olarak kabul ediliyor. `"yes"` metni `available` değeri olarak kabul ediliyor. `isbn` alanı da sessizce atılıyor.

Bu üç sorunun ortak bir yanı var: Hiçbiri tek bir alanla ilgili değil. Hepsi, modelin bütün alanlarına nasıl davrandığıyla ilgili. Bu yüzden kuralı tek tek alanların yanına değil, modelin kendisine yazıyoruz.

### 3.1 İstek modellerine ayar ekle

`server.py` dosyasında import satırını yine değiştiriyoruz:

```python
from pydantic import BaseModel, ConfigDict, Field
```

Sonra `BookCreate`, `BookUpdate` ve `ReviewCreate` modellerinin her birine, alanlardan önce aynı satırı ekliyoruz:

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

Bu satırı parça parça okuyalım.

`model_config`, **modelin ayarları (model configuration)**. Bu bir alan değil. Pydantic'e "bu model nasıl çalışsın?" sorusunun cevabını verir. Ayarlar `ConfigDict(...)` içine yazılır.

`strict=True`, **sıkı mod (strict mode)** demek. Bu modda değer, alanın kendi türünde gönderilmelidir. Pydantic başka bir türden çeviri yapmaz. `"4.5"` metni artık `float` alanına, `"yes"` metni de `bool` alanına giremez.

`extra="forbid"`, fazla alanları yasaklar. Modelde olmayan bir alana **fazla alan (extra field)** diyoruz. Böyle bir alan gönderilirse istek reddedilir. *Forbid*, İngilizcede "yasakla" demek. Varsayılan davranış ise bu alanları sessizce atmaktı.

Bu ayarlar yalnızca eklendikleri modelleri etkiler. `available` sorgu parametresi bir model alanı değil, fonksiyonun parametresi. Bu yüzden `?available=true` yazımı eskisi gibi çalışır. Zaten sorgu parametresinde sıkı mod işe yaramazdı. Deney 1.2'de gördüğümüz gibi, adresteki değerler her zaman metin olarak gelir. `true` da adreste bir metindir.

Bir not daha: Bu bir **tasarım seçimi**. Pydantic'in varsayılan davranışı yanlış değil. Değerleri çevirmek ve fazla alanları atmak, birçok API'nin bilerek seçtiği bir yol. Biz kitap kataloğunda başka bir şey seçtik: İstemci hatasını hemen öğrensin.

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

Üç satır değişti. `"4.5"` artık "geçerli bir sayı değil" hatası alıyor. `"yes"` "geçerli bir mantıksal değer değil" hatası alıyor. `isbn` de `Extra inputs are not permitted` hatası alıyor; yani "fazla alanlara izin verilmiyor".

Geriye yalnızca boşluklu ad kaldı. O da [ek nottaki](06_Supplement_Blank_Strings.md) ayarla düzelir.

### 3.3 Bir şey bozuldu

İstekler doğru reddediliyor. Peki kitapları okumak hâlâ çalışıyor mu? Deneyelim.

`client.py` dosyasının içeriğini şununla değiştir:

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

Hafta 4'te sorunsuz çalışan iki istek artık `500` alıyor. `500`, "sunucuda bir hata oldu" demek.

İstemci yalnızca `Internal Server Error` metnini görüyor. Bu yanıtta `detail` listesi yok. Neden? Çünkü sorun istemcinin isteğinde değil, sunucuda. FastAPI böyle bir hatanın ayrıntısını istemciye göndermez; yalnızca sunucunun terminaline yazar. Yanıtın gövdesi JSON olmadığı için de bu istemcide `response.json()` yerine `response.text` kullandık.

Nedenini görmek için sunucunun çalıştığı terminale bakıyoruz. Uzun hata çıktısının içinde şu satırlar var:

```text
INFO:     127.0.0.1:55002 - "GET /books/42 HTTP/1.1" 500 Internal Server Error
...
fastapi.exceptions.ResponseValidationError: 1 validation error:
  {'type': 'extra_forbidden', 'loc': ('response', 'internal_note'), 'msg': 'Extra inputs are not permitted', 'input': 'Kapağı yıpranmış, yenisi sipariş edildi.'}
```

Hatanın adı `ResponseValidationError`. *Validation*, **doğrulama (validation)** demek: Bir değeri modeldeki kurallara göre kontrol etmek. Yani bu ad "yanıt doğrulanamadı" diyor.

`loc` alanına bak: İlk öğe `response`. Bu kez hata istekte değil, yanıtta. Ne olduğunu adım adım görelim.

1. `get_book` fonksiyonu 42 numaralı kitabı döndürdü. Bu kitabın sözlüğünde `internal_note` alanı da var. Bu alanı Hafta 4'te eklemiştik.
2. FastAPI yanıtı göndermeden önce bu sözlüğü `BookPublic` modeline göre hazırlamak istedi.
3. `BookPublic` modeli, `BookCreate` modelinden türüyor. Türeyen model, atasının her şeyini alır: alanlarını, kurallarını ve ayarlarını. Yani `BookPublic` modelinde de artık `extra="forbid"` var.
4. `internal_note` alanı `BookPublic` modelinde yok. Model bu fazla alanı eskisi gibi atmak yerine reddetti. Yanıt hazırlanamadı ve istemciye `500` gitti.

Kitap listesi de aynı nedenle bozuldu. Listede 42 numaralı kitap da var. Tek bir kitap, bütün listeyi okunamaz hâle getirdi.

### 3.4 Yanıt modelinin ayarını düzelt

Buradan önemli bir sonuç çıkıyor: İstek modeli ile yanıt modeli fazla alanlara farklı davranmalı.

**İstek modeli** fazla alanı **reddetmeli**. İstemci yanlış bir alan gönderdiyse bunu öğrenmeli.

**Yanıt modeli** ise fazla alanı **süzmeli**. Sunucunun kendi verisinde fazladan alanlar olabilir. İstemciye yalnızca modeldeki alanlar gitmeli. Hafta 4'te `internal_note` alanını tam da bunun için gizlemiştik.

`server.py` dosyasında `BookPublic` modelini şöyle değiştir:

```python
class BookPublic(BookCreate):
    model_config = ConfigDict(strict=False, extra="ignore")

    id: int
```

Bu satır, `BookCreate` modelinden gelen iki ayarı değiştiriyor.

`extra="ignore"`, fazla alanları süzer. *Ignore*, İngilizcede "yok say" demek. Deney 1'de `isbn` alanına olan da buydu; Pydantic'in varsayılan davranışı budur.

`strict=False`, sıkı modu kapatır. Yanıt modeli istemcinin değil, sunucunun kendi verisini kontrol ediyor. Orada sıkı moda gerek yok.

Alanların kuralları ise yerinde kalıyor. `min_length`, `ge` ve `le` kuralları `BookPublic` modeline geçmeye devam ediyor. Yalnızca ayarları değiştirdik.

Sunucuyu yeniden başlat ve aynı istemciyi çalıştır:

```text
Book 42:   200 {"title":"API Yolculuğu","author":{"first_name":"Deniz","last_name":"Kaya"},"available":true,"tags":["software","education"],"rating":null,"id":42}
Book list: 200
```

Kitaplar yeniden okunuyor. Yanıtta `internal_note` alanı da yok.

### Ana fikir

`model_config`, modelin bütün alanlarına uygulanan ayarları taşır. `strict=True` türler arasında çeviri yapılmasını engeller. `extra="forbid"` modelde olmayan alanların kabul edilmesini engeller.

Türeyen model, bu ayarları da atasından alır. Yanıt modelinde fazla alanlar reddedilmemeli, süzülmeli. Sıkı moda da orada gerek yok.

---

## Deney 4: PATCH: gönderilmeyebilir, ama `null` olamaz

Hafta 4'te bir sorun görmüştük. `{"title": null}` gövdesiyle bir `PATCH` isteği gönderdik. İstek kabul edildi ve kitabın adı `None` oldu.

Sonra yanıt `500` döndü. Çünkü yanıt modelinde `title: str` yazıyor ve `None` bir metin değil. Ama iş işten geçmişti: Değişiklik, yanıt hazırlanmadan önce kitaba yazılmıştı. Kitap bozulmuştu.

Doğrusu şu: Böyle bir istek kitaba hiç dokunulmadan `422` ile reddedilmeli.

Deney 3'teki sıkı mod bu sorunu çözmedi. Çünkü `BookUpdate` modelinde `title: str | None` yazıyor. Bu yazım `None` değerine izin veriyor. Sıkı mod da yalnızca izin verilen türlere bakıyor.

### 4.1 `BookUpdate` modelinde `| None` yazımını kaldır

Önce bir yazımı adlandıralım. `str | None` yazımındaki `|` işaretine **dikey çizgi (pipe)** denir. Tür yazımında "ya da" anlamına gelir. `str | None`, "metin ya da `None`" demek. Python buna **birleşim türü (union type)** der.

İstediğimiz kural şu: `title` alanı **gönderilmeyebilir**. Ama **gönderilirse** `null` olamaz.

`server.py` dosyasında `BookUpdate` modelinin alanlarını şöyle değiştir:

```python
class BookUpdate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    title: str = Field(default=None, min_length=1)
    author: Author = None
    available: bool = None
    tags: list[str] = None
    rating: float | None = Field(default=None, ge=0, le=5)
```

`title`, `author`, `available` ve `tags` satırlarından `| None` kalktı. `rating` satırı değişmedi.

`title: str = None` yazımı ilk bakışta çelişkili görünüyor. Tür `str` diyor, varsayılan değer ise `None`. Bu nasıl çalışıyor?

Cevap şu cümlede: **Pydantic, varsayılan değeri kontrol etmez; yalnızca istemcinin gönderdiği değeri kontrol eder.**

Üç durumu düşünelim.

**İstemci `title` alanını hiç göndermedi.** Varsayılan değer `None` kullanılır ve kontrol edilmez. Ama bu `None` kitaba yazılmaz. Çünkü `update_book` fonksiyonu `exclude_unset=True` kullanıyor; gönderilmeyen alanlar `changes` sözlüğüne hiç girmiyor. Kitabın adı değişmez.

**İstemci `null` gönderdi.** Bu kez değer istemciden geldi, o yüzden kontrol edilir. `None` bir metin değildir. İstek `422` ile reddedilir.

**İstemci bir metin gönderdi.** Metin kontrol edilir. Boş değilse kabul edilir.

Editörün bu satırların altını çizdiğini görebilirsin. Nedenini [ek notta](07_Supplement_Default_None.md) bulabilirsin. Kod doğru çalışır.

Peki `rating` alanında `| None` neden kaldı? Çünkü puan için `null` anlamlı bir değer: "Bu kitabın puanı yok." Puana `null` göndermek, puanı silmek demek. Hafta 4'teki ek notta da bunu yapmıştık. Ama bir kitabın adının olmaması anlamlı değil.

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

`send_patch` fonksiyonu, Deney 1'deki `send_book` fonksiyonuna benziyor. 42 numaralı kitaba bir `PATCH` isteği gönderiyor. İstek kabul edilirse kitabın adını ve puanını, reddedilirse ilk hatanın açıklamasını yazdırıyor. En sonda kitabı yeniden okuyup bozulup bozulmadığına bakıyoruz.

Python'da `None` yazdığımız değer, JSON'a `null` olarak çevrilip gönderilir.

Sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Empty body:    200 title: 'API Yolculuğu' rating: None
Rating 4:      200 title: 'API Yolculuğu' rating: 4.0
Rating null:   200 title: 'API Yolculuğu' rating: None
Title null:    422 Input should be a valid string
Author null:   422 Input should be a valid dictionary or object to extract fields from
Read book 42:  200 title: 'API Yolculuğu'
```

Satırlara bakalım.

**Boş gövde.** `200` aldı. Hiçbir alan gönderilmedi, kitap değişmedi.

**Puan 4.** `200` aldı ve puan `4.0` oldu. Burada küçük bir soru akla gelebilir: Sıkı modda çeviri yapılmıyordu, `4` neden `4.0` oldu? Sıkı modda bile tam sayı, ondalıklı sayı alanına yazılabilir. JSON'da `4` ile `4.0` aynı sayıdır; bu çeviride bilgi kaybolmaz.

**Puan `null`.** `200` aldı ve puan silindi. `rating` için `null` geçerli bir değer.

**Ad `null`.** `422` aldı. Hafta 4'te `500` alan ve kitabı bozan istek, artık kitaba dokunulmadan reddediliyor.

**Yazar `null`.** `422` aldı. Yazar da `null` olamaz. Mesajdaki *dictionary or object*, yazarın bir nesne olması gerektiğini söylüyor: `first_name` ve `last_name` alanları olan bir sözlük.

**Kitabı yeniden okumak.** `200` aldı ve kitabın adı yerinde. Kitap bozulmadı.

### Ana fikir

Bir alanın isteğe bağlı olması ile `null` olabilmesi ayrı şeylerdir.

`title: str = None` yazımında alan gönderilmeyebilir; ama gönderilirse metin olmalıdır. `| None` yalnızca `null` değerinin anlamlı olduğu alanlarda kalmalı. Bizim kitaplarımızda bu alan `rating`.

---

## Deney 5: Kuralın yeri: model mi, fonksiyon mu?

Şimdiye kadar yazdığımız kuralların hepsi değerin kendisine bakıyordu. Bu deneyde iki yeni kural ekliyoruz. Biri yine değere bakıyor. Öteki ise sunucudaki veriye bakmak zorunda. Bölüm 0'daki soruya, "Bir kuralı nereye yazmalıyım?" sorusuna, bu deneyin sonunda cevap vereceğiz.

### 5.1 Yol parametresine kural: `Path`

Kitap kimlikleri pozitif sayılar. Yani `/books/-5` adresi hiçbir zaman bir kitap bulamaz. Bunu bilmek için kitap listesine bakmaya gerek yok; `-5` değerine bakmak yetiyor.

Bu kuralı, yolunda `book_id` olan **bütün** fonksiyonlara yazıyoruz. Bir tanesini unutursak aynı adres işleme göre farklı davranır. Örneğin `GET /books/-5` isteği `422`, `DELETE /books/-5` isteği ise `404` alır. Bu, istemciyi şaşırtır.

`server.py` dosyasında önce import satırına `Path` ekleniyor:

```python
from fastapi import FastAPI, HTTPException, Path, Response
```

Sonra altı fonksiyonun ilk satırı değişiyor. Yeni hâlleri şöyle:

```python
def get_book(book_id: int = Path(gt=0)):
def delete_book(book_id: int = Path(gt=0)):
def replace_book(book_data: BookCreate, book_id: int = Path(gt=0)):
def update_book(book_data: BookUpdate, book_id: int = Path(gt=0)):
def get_reviews(book_id: int = Path(gt=0)):
def create_review(review_data: ReviewCreate, book_id: int = Path(gt=0)):
```

`Path`, `Field` fonksiyonunun yol parametreleri için olan hâli. Modeldeki alana `Field` ile, yol parametresine `Path` ile kural yazıyoruz.

`gt=0`, "0'dan büyük" demek. İngilizce *greater than* sözlerinin kısaltması. `ge` gibi, ama bir farkla: Sınırın kendisi dahil değil. Yani 0 da reddedilir.

Bir şey daha dikkatini çekmiş olmalı. İki parametreli fonksiyonlarda `book_id` sona geçti. Neden?

Python'da bir kural var: Varsayılan değeri olan parametreler, varsayılan değeri olmayanlardan sonra gelmelidir. `= Path(gt=0)` yazımı da bir varsayılan değer gibi yazılıyor. Bu yüzden `book_id` sona geçmek zorunda.

Bu sıra değişikliği istekleri etkilemez. FastAPI parametreleri sıralarına göre değil, adlarına göre eşleştirir.

Sırayı değiştirmeyi unutursan sunucu hiç başlamaz. Terminalde şu hata görünür:

```text
SyntaxError: non-default argument follows default argument
```

Python'un yeni sürümlerinde bu mesajın metni farklı olabilir. Önemli olan, hatanın `SyntaxError` olması ve sunucunun başlamaması.

FastAPI belgelerinde aynı kuralın başka bir yazımını göreceksin: `Annotated`. O yazımda parametrelerin sırasını değiştirmek gerekmiyor. Ayrıntısı [ek notta](08_Supplement_Annotated.md).

### 5.2 Veriye bağlı kural: aynı okurun ikinci yorumu

Yeni kuralımız şu: Bir okur bir kitaba yalnızca bir yorum yazabilsin.

Bu kural modele yazılamaz. Neden? `ReviewCreate` modeli yalnızca gelen yorumu görür. Okurun adını görür, yorumu görür, puanı görür. Ama okurun daha önce yorum yazıp yazmadığını bilemez. Bunu öğrenmek için `reviews` listesine bakmak gerekir. Bu listeye de yalnızca bizim fonksiyonumuz bakabilir.

`server.py` dosyasında `create_review` fonksiyonuna, kitabın var olup olmadığını kontrol eden satırlardan sonra şunu ekle:

```python
    for review in reviews:
        if review["book_id"] == book_id and review["reader"] == review_data.reader:
            raise HTTPException(status_code=409, detail="This reader has already reviewed this book")
```

Bu döngü bütün yorumlara tek tek bakıyor. Hem aynı kitaba ait hem de aynı okurun yazdığı bir yorum bulursa, isteği `409` ile reddediyor.

Neden kitap kontrolünden sonra? Kitap yoksa önce `404` dönmeli. Var olmayan bir kitapta yorum çakışması diye bir şey de olamaz.

Fonksiyonun üstündeki yorum satırını da güncelle:

```python
# Yeni yorum: kitaba ekler, 201 döner; kitap yoksa 404, okurun bu kitaba yorumu varsa 409.
```

Bu kuralın bir sınırı var: Okuru adından tanıyor. `"Ece"` ile `"ece"` iki ayrı okur sayılır. Gerçek bir sistemde okur, oturum açmış kullanıcının kimliğinden tanınır. Bunu 9. haftada göreceğiz.

Peki neden `409`? **409 Conflict**, "istek, sunucudaki verinin şu anki hâliyle çakışıyor" demek. Bu kodu Hafta 2'nin [durum kodları notunda](../Week_02/07_Supplement_Status_Codes.md) görmüştük.

`422` ile farkı önemli. `422`, "isteğin içindeki değerler kurala uymuyor" der. Oysa buradaki istek kendi içinde tamamen doğru: Okurun adı dolu, yorum dolu, puan 1 ile 5 arasında. Sorun istekte değil, sunucuda zaten var olan bir yorumda. Aynı istek, Ece'nin eski yorumu olmasaydı kabul edilirdi.

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

Satırlara bakalım. Her satırda iki soru soracağız: Kim reddetti, neden?

**Kitap -5.** `422` aldı. Reddeden FastAPI, `Path(gt=0)` kuralıyla. `-5` hiçbir zaman kitap kimliği olamaz. Bunu bilmek için kitaplara bakmak gerekmedi. `get_book` fonksiyonu hiç çalışmadı. `input` değerinin tırnak içinde olduğuna dikkat et: `'-5'`. Adresteki değerler her zaman metin olarak gelir.

**Kitap -5'i silmek.** Yine `422` aldı. Aynı kural silme işleminde de var. Burada `404` görüyorsan, `delete_book` fonksiyonuna `Path(gt=0)` eklemeyi unutmuşsundur.

**Kitap 43.** `404` aldı. Reddeden `get_book` fonksiyonu. `43` bir kitap kimliği olabilir; ama listede böyle bir kitap yok. Bunu bilmek için kitaplara bakmak gerekti. Bunu da yalnızca fonksiyon yapabilir.

**Ece'nin ikinci yorumu.** `409` aldı. Reddeden `create_review` fonksiyonu. Ece'nin 42 numaralı kitaba yorumu, sunucu başlarken zaten var.

**Can'ın ilk yorumu.** `201` aldı. Kimse reddetmedi. Can'ın bu kitaba yorumu yoktu.

**Can'ın ikinci yorumu.** `409` aldı. Aynı istek, birkaç satır önce `201` almıştı. Değişen istek değil, sunucudaki veri. Az önce eklenen yorumla çakışıyor.

### Kural nereye yazılır?

Artık Bölüm 0'daki soruya cevap verebiliriz. Bir istek üç ayrı kontrolden geçebilir.

**Birinci kontrol: tür ve alanlar.** Örnekleri: `"title": 123`, `"rating": "4.5"`, `"available": "yes"` ve modelde olmayan `isbn` alanı. Bunu FastAPI, Pydantic ile, fonksiyondan önce kontrol eder. Kuralı alanın türüne, örneğin `title: str` yazımına, ve modelin ayarına, yani `strict=True` ile `extra="forbid"` yazımına yazdık. Yanıt `422` olur.

**İkinci kontrol: değer.** Örnekleri: boş ad, `9` puan ve `/books/-5`. Bunu da FastAPI, Pydantic ile, fonksiyondan önce kontrol eder. Kuralı alana `Field(...)` ile, parametreye `Path(...)` ile yazdık. Yanıt yine `422` olur.

**Üçüncü kontrol: veriye bağlı.** Örnekleri: `/books/43` ve aynı okurun ikinci yorumu. Bunu yalnızca bizim fonksiyonumuz kontrol edebilir. Kuralı fonksiyonun içine, `raise HTTPException(...)` ile yazdık. Yanıt `404` ya da `409` gibi, duruma uygun bir kod olur.

İlk iki kontrolde karar veren Pydantic. FastAPI onu, istek fonksiyona ulaşmadan çağırır. Kurala uymayan bir istek, fonksiyonu hiç çalıştırmaz.

### Ana fikir

Değerin kendisine bakarak karar verilebilen kurallar, modele ya da parametreye yazılır. FastAPI bunları fonksiyondan önce kontrol eder ve `422` döndürür.

Sunucudaki veriye bakmayı gerektiren kurallar ise fonksiyonun içine yazılır. Bunlar uygun bir durum koduyla, örneğin `404` ya da `409` ile bildirilir.

---

## Deney 6: İstemcide hata yanıtını göstermek

Bu deney bir ödev. Derste zaman kalmazsa evde yap. Yalnızca istemciyi değiştiriyoruz; sunucuya dokunmuyoruz.

Deney 5'in çıktısına tekrar bak. İki farklı hata yanıtı biçimi var.

**FastAPI'nin ürettiği `422` yanıtı.** Burada `detail` bir **liste**. Listenin her öğesi bir hata. Her hatanın `type`, `loc` ve `msg` gibi parçaları var.

**Bizim fonksiyonumuzun ürettiği `404` ve `409` yanıtları.** Burada `detail` bir **metin**. Örneğin `'Book not found'`. Bu metni `HTTPException` içinde biz yazmıştık.

İstemci iki biçimi de okuyabilmeli. Hangisinin geldiğini durum kodundan anlayabilir. Kod `422` ise `detail` bir liste; değilse bir metin.

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

`show_error` fonksiyonuna yakından bakalım.

Önce `detail` alanını alıyor. Sonra durum koduna bakıyor.

Kod `422` ise listedeki her hatayı tek tek yazdırıyor. `422` kodunun yalnızca FastAPI'den geldiğini biliyoruz; bizim fonksiyonlarımız `404` ve `409` döndürüyor.

`error["loc"][0]`, `loc` listesinin ilk öğesi: `body`, `path` ya da `query`. Yani hatanın isteğin hangi bölümünde olduğu.

`error["loc"][1:]` ise ilk öğeden sonraki bütün öğeler, yine bir liste olarak. Bu, hatalı alanın yeri. Örneğin `['body', 'tags', 1]` için sonuç `['tags', 1]` olur.

`f"..."` yazımı, değerleri metnin içine yerleştiriyor. Süslü parantez içindeki her şeyin yerine değeri geliyor.

Kod `422` değilse, `detail` bir metin. Fonksiyon onu olduğu gibi yazdırıyor.

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

İstemci her hatayı tek satırda gösteriyor. `422` yanıtlarında hatanın isteğin hangi bölümünde ve hangi alanda olduğu da görünüyor. Kullanıcı neyi düzeltmesi gerektiğini buradan okuyabilir.

İlk yorumda iki hata var, çünkü bu kez yorum metni dolu: `"Güzel."`. Yalnızca okur ve puan kurala uymuyor.

Son satıra dikkat: `['tags', 1]`. Bu, hatanın `tags` listesinin 1. sıradaki öğesinde olduğunu söylüyor. Python'da sıra 0'dan başlar. Yani 1. sıra, listenin ikinci öğesi: `5`. Etiketler metin olmalı, `5` ise bir sayı.

### Ana fikir

Hata yanıtı, istemci için de bir veridir.

FastAPI'nin `422` yanıtında `detail` bir listedir. Bizim `HTTPException` ile ürettiğimiz yanıtlarda ise bir metindir. İstemci ikisini ayırıp kullanıcıya okunur bir mesaj gösterebilir.

---

## Bölüm 7: Bu haftanın sonundaki `server.py`

Föyün 7. bölümünde, Deney 5'ten sonraki `server.py` dosyasının tamamı var. Deney 6 yalnızca istemciyi değiştirdiği için sunucu Deney 5'teki hâlinde kalıyor. Hafta 6'ya bu dosyayla başlayacağız.

Kendi dosyanı föydekiyle karşılaştırırken şu değişikliklere bak:

- **İmport satırları:** `fastapi` satırında `Path`, `pydantic` satırında `ConfigDict` ve `Field` var.
- **`BookCreate`, `BookUpdate` ve `ReviewCreate`:** Üçünde de `model_config = ConfigDict(strict=True, extra="forbid")` satırı ve `Field` kuralları var.
- **`BookPublic`:** `model_config = ConfigDict(strict=False, extra="ignore")` satırı var.
- **`BookUpdate`:** `title`, `author`, `available` ve `tags` alanlarında `| None` yok. `rating` alanında var.
- **`book_id` parametreleri:** Altı fonksiyonun hepsinde `Path(gt=0)` var. İki parametreli fonksiyonlarda `book_id` sonda.
- **`create_review`:** Aynı okurun ikinci yorumunu `409` ile reddeden döngü var.

Önceki haftalarda `get_review` ya da `delete_review` fonksiyonlarını yazdıysan, onlar da dosyada kalır. Onların `book_id` ve `review_id` parametrelerine de `Path(gt=0)` ekleyebilirsin.

---

## Bölüm 8: Ödev: belge ve kendi kuralını yazmak

Bu bölümü Deney 6 ile birlikte evde tamamla. Dört parçası var.

### 8.1 Kuralları API'nin şemasında görmek

FastAPI, modellerimizden API'nin bir tarifini kendiliğinden üretir. Bu tarife API'nin **şeması** diyoruz. `/docs` sayfası da bu şemadan hazırlanır.

Sunucu çalışırken şemayı görmek için tarayıcıda şu adresi aç:

```text
http://127.0.0.1:8000/openapi.json
```

Tarayıcı JSON'u düzenli gösterir. Gerekirse sayfanın üstündeki **Pretty-print** kutusunu işaretle.

`components`, sonra `schemas`, sonra `BookCreate` bölümüne in. Yazdığımız kurallar orada, ama başka adlarla:

- `title` alanında `"minLength":1` göreceksin. Bu, bizim `Field(min_length=1)` kuralımız.
- `rating` alanında `"maximum":5.0` ve `"minimum":0.0` göreceksin. Bunlar `le=5` ve `ge=0`. Yanında bir de `{"type":"null"}` seçeneği var; çünkü puan `null` olabilir.
- Modelin kendisinde `"additionalProperties":false` göreceksin. Bu, bizim `extra="forbid"` ayarımız: "Fazladan alan yok."

Aynı bilgileri `http://127.0.0.1:8000/docs` sayfasının altındaki **Schemas** bölümünde de görebilirsin.

Bir deneme de yap. Aynı sayfada `POST /books` işlemini aç ve **Try it out** düğmesine bas. Gövdedeki `rating` değerini `7` yap ve isteği gönder. `422` yanıtını ve `detail` listesini sayfada göreceksin. Sayfa bu yanıta `Validation Error`, yani doğrulama hatası diyor.

### 8.2 `README.md` belgesine alan kurallarını eklemek

Hafta 3'te bir `README.md` belgesi yazmıştın. API'yi kullanan biri, bir isteğin neden reddedildiğini bu belgeden öğrenebilmeli. Kod okumak zorunda kalmamalı.

Belgenin sonuna şu bölümü ekle:

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

Bu bölüm, haftanın bütün kurallarını kullanıcının diliyle özetliyor.

### 8.3 Kendin yaz: yazarın adı boş olmasın

Şu an bir kitabın yazarı `{"first_name": "", "last_name": ""}` olabiliyor. Yazara fazladan bir alan da gönderilebiliyor ve bu alan sessizce atılıyor.

Senden iki şey isteniyor:

1. Yazarın adı (`first_name`) ve soyadı (`last_name`) boş olamasın.
2. Yazar nesnesinde modelde olmayan bir alan gönderilirse istek reddedilsin.

İpucu: Değiştirmen gereken tek model `Author`. Deney 2'de ve Deney 3'te öteki modellere yaptığını bu modele uygula.

Kodunu yazdıktan sonra şunları kontrol et:

- Yazarın adı boş bir kitap gönderdiğinde `422` almalısın. `loc` değeri `['body', 'author', 'first_name']` olmalı.
- Yazara `middle_name` gibi fazla bir alan eklediğinde de `422` almalısın. `loc` değeri `['body', 'author', 'middle_name']` olmalı.
- Doğru bir yazarla gönderdiğinde `201` almalısın.
- Kuralı ekledikten sonra `GET /books` isteği hâlâ `200` almalı.

Son madde önemli. Kendine şunu sor: `Author` modeli başka nerelerde kullanılıyor? Deney 3'te `BookPublic` modelinde ne olmuştu?

Kodunu yazıp denedikten sonra [ek nottaki cevapla](09_Supplement_Exercise_8_3_Answer.md) karşılaştır. Önce kendin dene.

### 8.4 Kendin yaz: üst sınırlar

Şimdiye kadar hep alt sınır yazdık. Oysa bir kitabın adı şu an on bin karakter olabiliyor. Etiket listesine yüzlerce etiket de eklenebiliyor.

Üst sınırları da `Field` yazar. `max_length`, metin için en fazla karakter sayısını, liste için de en fazla öğe sayısını belirler.

Senden üç şey isteniyor:

1. Kitabın adı en fazla 100 karakter olsun.
2. Bir kitabın en fazla 5 etiketi olsun.
3. İki kural `PATCH` isteklerinde de geçerli olsun.

İpucu: `BookCreate` ve `BookUpdate` modellerini değiştirmen gerekiyor. Kuralları yazmadan önce [kuralların yanıt modeline geçtiği ek notun](05_Supplement_Inherited_Rules.md) sonundaki iki soruyu kendine sor. Sunucudaki kitaplar bu kurallara uyuyor mu?

Kodunu yazdıktan sonra şunları kontrol et:

- 101 karakterlik bir ad `422` almalı; `loc` değeri `['body', 'title']`.
- 6 etiketli bir kitap `422` almalı; `loc` değeri `['body', 'tags']`.
- 100 karakterlik bir ad ve 5 etiket `201` almalı. Sınırın kendisi kabul edilir.
- `PATCH /books/42` isteğiyle 6 etiket göndermek `422` almalı.
- `GET /books` isteği hâlâ `200` almalı.

Kodunu yazıp denedikten sonra [ek nottaki cevapla](10_Supplement_Exercise_8_4_Answer.md) karşılaştır.

---

## Bölüm 9: Kendini kontrol et

Haftayı yedi soruyla gözden geçirelim. Her soruyu önce kendin cevaplamaya çalış. Sonra föyün 9.1 bölümündeki cevaplarla karşılaştır.

1. Bir istek hangi üç kontrolden geçebilir? Bunlardan hangileri, istek fonksiyona ulaşmadan yapılır?
2. `422` yanıtında `'loc': ['path', 'book_id']` ne söyler?
3. Kitap puanının alt sınırını `ge=1` yapsaydık, 57 numaralı kitap neden okunamazdı?
4. `strict=True` eklenmeden önce `"available": "yes"` neden kabul ediliyordu?
5. `extra="forbid"` eklenince 42 numaralı kitabı okuyan istek neden `500` aldı? Bunu nasıl düzelttik?
6. `BookUpdate` modelinde `title: str = None` yazımı ile `title: str | None = None` yazımı arasındaki fark nedir?
7. `/books/-5` neden `422`, `/books/43` neden `404` alıyor? Aynı okurun ikinci yorumunu reddeden kural neden modelde değil de fonksiyonda?

Cevaplarken haftanın ana çizgisini hatırla: Tür bir şeydir, değer başka bir şey; değer de sunucudaki veriden ayrı bir şey.

---

## Bölüm 10: Resmî belgeler

Föyün 10. bölümünde bu haftanın konularına ait resmî belgelerin bağlantıları var. FastAPI belgeleri alan kurallarını, yol parametrelerini ve hata yanıtlarını anlatıyor. Pydantic belgeleri alanları, sıkı modu ve `extra` ayarını anlatıyor. MDN sayfaları da `422` ve `409` durum kodlarını anlatıyor.

Bu belgeleri okurken birkaç İngilizce terimle karşılaşacaksın:

- Pydantic, alanlara yazdığımız kurallara *constraint* der. Türkçesi "kısıt".
- Varsayılan, gevşek davranışa *lax mode* der.
- Değerin başka bir türe çevrilmesine *coerce* der.

---

## Haftanın özeti

Bu hafta tek bir soruya cevap aradık: Bir kuralı nereye yazmalıyım?

Cevap, kuralın neye baktığına bağlı.

Kural yalnızca **değerin türüne** bakıyorsa, alanın türüne ve modelin ayarına yazılır. `title: str`, `strict=True` ve `extra="forbid"` buna örnek.

Kural **değerin kendisine** bakıyorsa, alana `Field` ile ya da parametreye `Path` ile yazılır. `min_length=1`, `ge=1, le=5` ve `gt=0` buna örnek.

Bu iki türü FastAPI, fonksiyon çalışmadan önce kontrol eder ve `422` döndürür.

Kural **sunucudaki veriye** bakıyorsa, fonksiyonun içine yazılır. "43 numaralı kitap var mı?" ve "Bu okur daha önce yorum yazmış mı?" buna örnek. Bunları yalnızca fonksiyon bilebilir. Sonuç `404` ya da `409` gibi uygun bir kodla bildirilir.

Yolda iki önemli ders de öğrendik. Birincisi: Türeyen model, atasının kurallarını ve ayarlarını da alır; yanıt modeline bu yüzden dikkat etmek gerekir. İkincisi: Bir alanın gönderilmeyebilmesi ile `null` olabilmesi ayrı şeylerdir.

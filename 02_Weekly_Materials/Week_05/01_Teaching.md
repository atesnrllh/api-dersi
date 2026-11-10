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

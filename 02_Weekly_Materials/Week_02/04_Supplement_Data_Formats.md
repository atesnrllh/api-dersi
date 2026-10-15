# Ek Not — JSON'dan Başka Veri Biçimleri

Derste istemci ile sunucu arasındaki veriyi **JSON** biçiminde gönderiyoruz. JSON, bugün web API'lerinde istek ve yanıt gövdesinde veri taşımak için en çok kullanılan biçimdir, ama tek biçim değildir.

## 1. Aynı kitap, farklı biçimlerde

**JSON:**

```json
{"id": 74, "title": "HTTP ile Yeni Bir Kitap", "available": true}
```

**XML:**

```xml
<book>
  <id>74</id>
  <title>HTTP ile Yeni Bir Kitap</title>
  <available>true</available>
</book>
```

**YAML:**

```yaml
id: 74
title: HTTP ile Yeni Bir Kitap
available: true
```

**Form verisi** (web sayfalarındaki formlar veriyi çoğunlukla bu biçimle gönderir):

```text
id=74&title=HTTP+ile+Yeni+Bir+Kitap&available=true
```

Dördü de aynı kitabı anlatır, ama değerlerin türünü aynı şekilde göstermez:

| Biçim | `74` | `true` |
|---|---|---|
| JSON | Sayı | Mantıksal değer |
| YAML | Sayı | Mantıksal değer |
| XML | Metin | Metin |
| Form verisi | Metin | Metin |

XML'de ve form verisinde her değer metin olarak gelir; değerin sayı mı, mantıksal değer mi olduğuna veriyi okuyan program karar verir.

## 2. Hangi biçim nerede kullanılır?

| Biçim | `Content-Type` değeri | Nerede karşılaşılır? |
|---|---|---|
| **JSON** | `application/json` | Bugünkü web API'lerinin çoğu. Derste kullandığımız biçim. |
| **XML** | `application/xml` | Bankacılık gibi alanlardaki daha eski sistemler, **SOAP** servisleri |
| **YAML** | `application/yaml` | Daha çok ayar dosyaları; API'lerin tanım belgeleri (OpenAPI) |
| **Form verisi** | `application/x-www-form-urlencoded` | Web sayfalarındaki formların gönderilmesi |
| **Çok parçalı form** | `multipart/form-data` | Dosya yükleme; örneğin bir kitap kapağı resmi göndermek |
| **CSV** | `text/csv` | Tablo verisini dışa aktarma; örneğin kataloğu Excel'e almak |

Bunların yanında, açıldığında insanların okuyamadığı **ikili (binary)** biçimler de vardır. Aynı veriyi JSON'dan daha az yer kaplayarak taşırlar ve programlar onları daha hızlı işler. Bu derste kullanılmayacak.

## 3. Sunucu hangi biçimin geldiğini nereden anlar?

Gövdenin biçimini **`Content-Type`** başlığı bildirir. Birinci haftada gördüğümüz iki başlık bu iş içindir:

| Başlık | Kim gönderir? | Ne bildirir? |
|---|---|---|
| `Accept` | İstemci | "Yanıtı şu biçimde kabul ediyorum." |
| `Content-Type` | Gövdeyi gönderen taraf | "Gönderdiğim gövde şu biçimde." |

Bu hafta `json=new_book` yazdığımızda HTTPX isteğe `Content-Type: application/json` başlığını kendisi ekliyor. Aynı kitabı form verisi olarak göndermek isteseydik `json=` yerine `data=` kullanırdık. O zaman HTTPX başlığı `application/x-www-form-urlencoded` yapardı. Bizim sunucumuz ise gövdeyi JSON olarak beklediği için böyle bir isteği `422` ile reddederdi.

## 4. JSON neden bu kadar yaygın?

- İnsanlar için okuması ve yazması kolaydır.
- Aynı bilgiyi XML'den daha az karakterle yazar.
- Değerin türü yazılışından anlaşılır. Bunu bir sonraki bölümde açıklıyoruz.

## 5. JSON'da değerin türü nasıl anlaşılır?

JSON'da bir değerin **nasıl yazıldığına bakarak türü anlaşılır**. Veriyi okuyan programın tahmin etmesi gerekmez.

| JSON'da yazılışı | Türü | Nereden anlaşılıyor? |
|---|---|---|
| `74` veya `4.5` | Sayı | Tırnak yok, rakamlardan oluşuyor |
| `"74"` | Metin | Tırnak içinde yazılmış |
| `true` / `false` | Mantıksal değer | Tırnaksız `true` ya da `false` |
| `null` | Değer yok | Tırnaksız `null` |
| `{"first_name": "Ada"}` | Nesne | Süslü parantez içinde `"ad": değer` çiftleri |
| `["http", "python"]` | Dizi | Köşeli parantez içinde değerler |

### 5.1 `74` ile `"74"` aynı şey değildir

JSON'da tırnak işareti türü değiştirir: `74` bir sayıdır, `"74"` ise bir metindir. Birinci haftanın Deney 12'sinde bunu gördük. `"page_count": 240` geldiğinde kontrol geçti; `"page_count": "240"` geldiğinde program "sayfa sayısı tam sayı olmalı" diyerek kabul etmedi. İki değer ekranda benzer görünse de JSON'da farklı türdedir.

### 5.2 XML'de ve form verisinde tür yazılıştan anlaşılmaz

Aynı kimlik XML'de ve form verisinde şöyle yazılır:

```xml
<id>74</id>
```

```text
id=74
```

Burada `74` yalnızca bir yazıdır. Yazılışına bakarak sayı mı, metin mi olduğunu anlayamayız. Bu kararı veriyi okuyan program verir; bunun için ayrıca bir kural yazmak gerekir.

### 5.3 JSON okununca Python'da neye dönüşür?

`response.json()` veya `json.loads(...)` JSON'u okuduğunda her türü Python'daki karşılığına çevirir:

| JSON | Python |
|---|---|
| `74` | `int` (tam sayı) |
| `4.5` | `float` (ondalıklı sayı) |
| `"74"` | `str` (metin) |
| `true` / `false` | `True` / `False` |
| `null` | `None` |
| `{...}` (nesne) | `dict` (sözlük) |
| `[...]` (dizi) | `list` (liste) |

Ters yönde de aynı karşılıklar geçerlidir: Python'daki `True` JSON'a `true`, `None` ise `null` olarak yazılır. Bu hafta istemcide `"available": True` ve `"rating": None` yazdığımızda HTTPX'in gönderdiği JSON'da `true` ve `null` görünmesinin nedeni budur.

## 6. Dersin ilerleyen haftalarında

- **Hafta 3:** REST, SOAP ve GraphQL karşılaştırılırken biçim farkı da görünecek. SOAP mesajları XML ile yazılır; GraphQL yanıtları JSON olarak gelir.
- **Hafta 13:** FastAPI, API'nin tanımını (OpenAPI) kendisi üretir ve JSON olarak `/openapi.json` adresinde sunar. `/docs` sayfası bu tanımdan oluşur. Aynı tanım YAML ile de yazılabilir.

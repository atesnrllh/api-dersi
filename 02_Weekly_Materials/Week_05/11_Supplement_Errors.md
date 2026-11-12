# Ek Not — Bu haftanın hataları

Bu notta, Hafta 5 föyünde karşılaşacağın bütün hataları bir arada bulacaksın. Bazılarını önceki haftalarda gördük, bazıları bu hafta yeni. Föyde bir hatanın ne demek olduğunu unutursan buraya dön. Tablolardaki "Föyde nerede?" sütunu, hatayı föyün hangi bölümünde gördüğünü söyler.

---

## 1. Durum kodları

Yanıtın durum kodu, isteğin sonucunu bir sayıyla söyler. İstemcide `response.status_code` ile okunur.

| Kod | Adı | Ne demek? | Kim döndürür? | Föyde nerede? |
|---|---|---|---|---|
| `404` | Not Found | İstenen kaynak sunucuda yok. | Bizim fonksiyonumuz: `raise HTTPException(status_code=404, ...)` | 5.1: `Path` kuralından önce `/books/-5`; 5.3: `/books/43` |
| `409` | Conflict | İstek kendi içinde doğru, ama sunucudaki verinin şu anki hâliyle çakışıyor. | Bizim fonksiyonumuz: `raise HTTPException(status_code=409, ...)` | 5.2, 5.3: aynı okurun ikinci yorumu |
| `422` | Unprocessable Content (eski adı Unprocessable Entity) | İstekteki bir değer, modelin ya da parametrenin kuralına uymuyor. Gövdedeki `detail` listesi hatanın ne olduğunu ve nerede olduğunu söyler. | FastAPI, fonksiyonumuz çalışmadan önce | Her deneyde |
| `500` | Internal Server Error | Sorun istekte değil, sunucunun kendisinde. İstemci yalnızca `Internal Server Error` metnini görür; ayrıntı sunucunun terminalindedir. | FastAPI, sunucu kodu hata verince | 3.3: 42 numaralı kitabı okumak |

`400 Bad Request` kodunu bu föyde kullanmıyoruz. `422` ile farkı [ek notta](04_Supplement_400_vs_422.md) anlatılıyor.

---

## 2. `422` yanıtındaki hatalar

`422` yanıtının `detail` listesindeki her hatanın iki adı vardır, ikisini de Pydantic üretir:

- `type`: hatanın kısa adı
- `msg`: insanların okuyacağı açıklaması

Bu parçaları föyün 1.2 bölümünde ayrıntılı okuyoruz. İstemcimiz çoğu deneyde yalnızca `msg` metnini yazdırıyor. Bu yüzden tablonun ilk sütunu bu metin.

| Çıktıdaki `msg` | `type` | Ne demek? | Hangi kural ya da ayar? | Föyde nerede? |
|---|---|---|---|---|
| `Input should be a valid string` | `string_type` | Metin bekleniyordu, başka bir şey geldi. | `title: str` | 1.1, 1.2: `"title": 123`; 4.2: `"title": null` |
| `Input should be a valid integer, unable to parse string as an integer` | `int_parsing` | Adresteki metin tam sayıya çevrilemedi. | `book_id: int` | 1.2: `/books/abc` |
| `Input should be a valid boolean, unable to interpret input` | `bool_parsing` | Adresteki metin `true` ya da `false` olarak okunamadı. | `available: bool` (sorgu parametresi) | 1.2: `?available=maybe` |
| `String should have at least 1 character` | `string_too_short` | Metin, izin verilenden kısa. | `min_length=1` | 2.2, 2.3: boş ad, boş okur adı ve boş yorum |
| `Input should be less than or equal to 5` | `less_than_equal` | Sayı, üst sınırdan büyük. | `le=5` | 2.2: puan `7`; 2.3: yorum puanı `9` |
| `Input should be greater than or equal to 0` | `greater_than_equal` | Sayı, alt sınırdan küçük. | `ge=0` | 2.2: puan `-1` |
| `Input should be greater than 0` | `greater_than` | Sayı 0'dan büyük olmalıydı. | `Path(gt=0)` | 5.3: `/books/-5` |
| `Input should be a valid number` | `float_type` | Sayı bekleniyordu. Sıkı modda metin sayıya çevrilmez. | `strict=True` | 3.2: `"rating": "4.5"` |
| `Input should be a valid boolean` | `bool_type` | `true` ya da `false` bekleniyordu. Sıkı modda `"yes"` metni çevrilmez. | `strict=True` | 3.2: `"available": "yes"` |
| `Extra inputs are not permitted` | `extra_forbidden` | Modelde olmayan bir alan geldi. | `extra="forbid"` | 3.2: `isbn`. 3.3'te aynı hata yanıtta çıkar; istemci `422` değil `500` alır. |
| `Input should be a valid dictionary or object to extract fields from` | `model_attributes_type` | Alt alanları olan bir nesne bekleniyordu. | `author: Author` | 4.2: `"author": null` |

---

## 3. Terminalde görülen hatalar

Bunlar bir yanıtın içinde değil, sunucunun ya da istemcinin terminalinde görünür.

| Hata | Nerede görünür? | Ne demek? | Föyde nerede? |
|---|---|---|---|
| `httpx.ConnectError` | İstemcide. Föydeki istemciler bu hatayı yakalar ve `Connection failed: Check that the server is running.` yazar. | İstemci sunucuya bağlanamadı. Büyük olasılıkla sunucu çalışmıyor. | Her istemcide |
| `ResponseValidationError` | Sunucunun terminalinde | Fonksiyonun döndürdüğü veri, yanıt modeline (`response_model`) uymuyor. İstemci `500` alır. | 3.3 |
| `SyntaxError: non-default argument follows default argument` | Sunucuyu başlattığın terminalde | Varsayılan değeri olan bir parametre, varsayılan değeri olmayan bir parametreden önce yazıldı. Python dosyayı okuyamaz ve sunucu hiç başlamaz. | 5.1 |

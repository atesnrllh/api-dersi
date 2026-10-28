# Ek Not — Bir İstek Nereye Gider?

## URL'nin parçaları, yerel sunucu ve internetteki bir API

**Hafta:** 01 · **Kullanım:** Derste anlatım ve canlı deneme · **Gerekenler:** Föydeki sunucu (`server.py`), `httpx`, internet bağlantısı

Bu notta iki isteği yan yana inceleyeceğiz. Biri kendi bilgisayarımızda çalışan kitap API'sine, diğeri internetteki bir hava durumu API'sine gidiyor. Amaç, adresin her parçasının ne işe yaradığını görmek ve isteğin yerel ya da uzak bir sunucuya gitmesinin neyi değiştirip neyi değiştirmediğini anlamak.

### Bu notun sonunda

- Bir URL'yi şema, sunucu adresi, port, yol ve sorgu olarak parçalarına ayırabileceksin.
- Adresin hangi parçalarının bağlantı kurmak için, hangilerinin istek mesajı için kullanıldığını açıklayabileceksin.
- `127.0.0.1` ile bir alan adı arasındaki farkı ve DNS'in görevini açıklayabileceksin.
- Yerel ve internetteki bir sunucuya istek göndermenin farklarını ve benzerliklerini sayabileceksin.
- Bir bilginin yolda mı, sorguda mı gönderileceğine gerekçesiyle karar verebileceksin.

---

## 1. İki istek, aynı kalıp

**Yerel kitap API'si** (föydeki Deney 2):

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/book/42")
```

**İnternetteki hava durumu API'si** ([Open-Meteo](https://open-meteo.com/)):

```python
import httpx

response = httpx.get(
    "https://api.open-meteo.com/v1/forecast",
    params={
        "latitude": 41.27976,
        "longitude": 36.3361,
        "daily": "temperature_2m_max,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 1,
    },
    timeout=15,
)
```

İki istek de aynı fonksiyonla gönderiliyor: `httpx.get(...)`. Değişen, isteğin **nereye** gittiği.

---

## 2. Adresi okumak

HTTPX'in gerçekte gönderdiği adresler şunlar:

```text
http://127.0.0.1:8000/book/42
https://api.open-meteo.com/v1/forecast?latitude=41.27976&longitude=36.3361&daily=temperature_2m_max%2Cprecipitation_probability_max&timezone=auto&forecast_days=1
```

Bir adresi, bir binaya gidip içeriden bir şey istemeye benzetebiliriz:

```text
http://  127.0.0.1  :8000  /book/42
   │         │        │        │
   │         │        │        └─ İçeri girince ne istediğin
   │         │        └────────── Daire numarası: hangi kapı
   │         └─────────────────── Binanın adresi: hangi bilgisayar
   └───────────────────────────── Konuşma dili: hangi kurallar
```

### Parçalar

| Parça | Yerel istek | İnternet isteği | Görevi |
|---|---|---|---|
| Şema | `http` | `https` | Hangi kurallarla konuşulacağı. `https`, aynı kuralların şifreli bir bağlantı üzerinden kullanılmasıdır. |
| Sunucunun adresi (host) | `127.0.0.1` | `api.open-meteo.com` | Hangi bilgisayara gidileceği |
| Port | `8000` | Yazılmamış, `443` kullanılır | O bilgisayarda hangi kapıya gidileceği |
| Yol (path) | `/book/42` | `/v1/forecast` | Sunucudaki hangi kaynağın ya da işlemin istendiği |
| Sorgu (query) | Yok | `latitude=...&longitude=...` | İsteğin ayarları. `?` ile başlar, parçaları `&` ile ayrılır. |

Bu parçaları Python'da da ayırabiliriz. `url_parts.py`:

```python
import httpx

for address in [
    "http://127.0.0.1:8000/book/42",
    "https://api.open-meteo.com/v1/forecast?latitude=41.27976&longitude=36.3361",
]:
    url = httpx.URL(address)
    print("Scheme:", url.scheme)
    print("Host:  ", url.host)
    print("Port:  ", url.port)
    print("Path:  ", url.path)
    print("Query: ", url.query.decode())
    print()
```

```text
Scheme: http
Host:   127.0.0.1
Port:   8000
Path:   /book/42
Query:  

Scheme: https
Host:   api.open-meteo.com
Port:   None
Path:   /v1/forecast
Query:  latitude=41.27976&longitude=36.3361
```

İkinci adreste `Port` satırında `None` görünüyor: adreste port yazılmamış. Bu durumda şemanın varsayılan portu kullanılır.

### Port: numaralı kapı

Bir bilgisayarda aynı anda birçok program ağdan bağlantı bekleyebilir. Port, bunlardan hangisine ulaşılacağını seçer. Port bir program değildir; programın beklediği **kapının numarasıdır**. Föydeki sunucuda Uvicorn 8000 numaralı kapıda bekler.

| Şema | Port yazılmazsa kullanılan |
|---|---|
| `http` | `80` |
| `https` | `443` |

Web sitelerinin adresinde port görmememizin nedeni budur.

Yerel sunucuya portu yazmadan istek gönderirsek istek 80 numaralı kapıya gider. Orada bekleyen bir program olmadığı için bağlantı kurulamaz:

```python
httpx.get("http://127.0.0.1/book/42")
```

```text
httpx.ConnectError: [Errno 111] Connection refused
```

### Sunucunun adresi: IP adresi ve alan adı

`127.0.0.1` bir **IP adresidir** ve özel bir anlamı vardır: "bu bilgisayarın kendisi". Aynı anlama gelen ad `localhost`'tur.

`api.open-meteo.com` ise bir **alan adıdır**. Bilgisayar, bağlantı kurmadan önce bu adın IP adresini **DNS** adı verilen ad çözme sistemine sorar. `dns_lookup.py`:

```python
import socket

print("localhost          ->", socket.gethostbyname("localhost"))
print("api.open-meteo.com ->", socket.gethostbyname("api.open-meteo.com"))
```

```text
localhost          -> 127.0.0.1
api.open-meteo.com -> 94.130.142.35
```

> **Not:** Bir alan adının IP adresi zamanla değişebilir; senin denemende farklı bir adres görebilirsin. Alan adı kullanmanın kazancı da budur: sunucunun IP adresi değişse bile istemci kodu aynı kalır.

### Sorgu: `params` sözlüğü adrese nasıl dönüşüyor?

`params` sözlüğündeki her anahtar–değer çifti adrese `anahtar=değer` olarak eklenir; çiftler `&` ile ayrılır:

| `params` içinde | Adreste |
|---|---|
| `"latitude": 41.27976` | `latitude=41.27976` |
| `"daily": "temperature_2m_max,precipitation_probability_max"` | `daily=temperature_2m_max%2Cprecipitation_probability_max` |
| `"forecast_days": 1` | `forecast_days=1` |

Virgül adreste `%2C` olarak yazıldı. HTTPX, adreste özel anlamı olabilecek karakterleri bu şekilde güvenli hale getirir. Sunucu onları yeniden virgüle çevirir.

---

## 3. Adresin parçaları iki ayrı iş görür

İstemcinin gerçekte ne gönderdiğini `curl -v` komutuyla görebiliriz. Föydeki sunucu çalışırken şunu çalıştır:

```bash
curl -v http://127.0.0.1:8000/book/42
```

Çıktıda `>` ile başlayan satırlar istemcinin gönderdikleridir:

```text
> GET /book/42 HTTP/1.1
> Host: 127.0.0.1:8000
```

Aynısını Open-Meteo için de yapalım:

```bash
curl -v --http1.1 "https://api.open-meteo.com/v1/forecast?latitude=41.27976&longitude=36.3361&daily=temperature_2m_max"
```

```text
* Connected to api.open-meteo.com (94.130.142.35) port 443 (#0)
> GET /v1/forecast?latitude=41.27976&longitude=36.3361&daily=temperature_2m_max HTTP/1.1
> Host: api.open-meteo.com
```

`--http1.1` seçeneği, mesajın iki örnekte de aynı biçimde görünmesini sağlar.

| Parçalar | Ne için kullanılır? |
|---|---|
| Şema, sunucunun adresi, port | **Bağlantıyı kurmak için:** hangi bilgisayardaki hangi kapıya gidileceği. `Connected to ... port 443` satırı bu adımdır. |
| Yol ve sorgu | **İstek mesajının içinde gider:** bağlantı kurulduktan sonra sunucuya ne istendiği söylenir. |

Bu mesajdan iki şey daha öğreniyoruz:

- **`GET` adreste yazmıyor.** HTTP metodu, mesajın en başında ayrıca gönderilir. Bizim kodumuzda HTTP metodunu `httpx.get(...)` seçiyor. Yol **hangi kaynağın** istendiğini, HTTP metodu ise **onunla ne yapılmak istendiğini** söyler.
- **Sunucunun adresi `Host` satırında da gönderiliyor.** Aynı IP adresinde birden fazla site bulunabilir; sunucu hangisinin istendiğini bu satırdan anlar.

---

## 4. Yerel ile internet arasındaki farklar

|  | Yerel (`127.0.0.1`) | İnternet (`api.open-meteo.com`) |
|---|---|---|
| Sunucu nerede çalışıyor? | Aynı bilgisayarda; biz başlattık | Open-Meteo'nun bilgisayarlarında |
| Sunucu kodunu kim yazdı? | Biz | Başkası. Biz yalnızca belgelerindeki kuralları biliyoruz. |
| Adres nasıl bulunuyor? | `127.0.0.1` zaten bir IP adresi | Alan adı önce DNS ile IP adresine çevriliyor |
| İstek bilgisayardan çıkıyor mu? | Hayır | Evet, internete çıkıyor |
| Bağlantı | `http`: şifresiz. İstek bilgisayardan çıkmadığı için yeterli. | `https`: yol boyunca şifreli |
| Gecikme ve kopma | Neredeyse yok | Ağın durumuna bağlı; gecikebilir ya da kopabilir |
| Sunucu kapalıysa | Biz açarız | Elimizde değil |

### `timeout=15` neden var?

HTTPX, bağlantı kurmak ya da yanıt almak için varsayılan olarak **5 saniye** bekler; süre dolarsa hata verir. İnternetteki bir sunucunun yanıtı ağın durumuna göre gecikebileceği için bu örnekte bekleme süresi 15 saniyeye çıkarılmıştır. Yerel sunucuda buna gerek yoktur.

---

## 5. Değişmeyen şey: istemcinin işi

Hava durumu yanıtını, föydeki istemcide yaptığımız gibi okuyalım. `weather_client.py`:

```python
import httpx

try:
    response = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": 41.27976,
            "longitude": 36.3361,
            "daily": "temperature_2m_max,precipitation_probability_max",
            "timezone": "auto",
            "forecast_days": 1,
        },
        timeout=15,
    )
except httpx.RequestError:
    print("Request failed: Check your internet connection.")
else:
    print("Request URL:", response.request.url)
    print("Status code:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))

    if response.status_code == 200:
        forecast = response.json()
        daily = forecast["daily"]
        units = forecast["daily_units"]

        print("Date:", daily["time"][0])
        print("Max temperature:", daily["temperature_2m_max"][0], units["temperature_2m_max"])
        print("Rain probability:", daily["precipitation_probability_max"][0], units["precipitation_probability_max"])
    else:
        print("Forecast could not be retrieved.")
```

```text
Request URL: https://api.open-meteo.com/v1/forecast?latitude=41.27976&longitude=36.3361&daily=temperature_2m_max%2Cprecipitation_probability_max&timezone=auto&forecast_days=1
Status code: 200
Content-Type: application/json; charset=utf-8
Date: 2026-10-06
Max temperature: 18.2 °C
Rain probability: 48 %
```

Tarih ve hava durumu değerleri, programı çalıştırdığın güne göre değişir.

| | Kitap API'si | Open-Meteo |
|---|---|---|
| Durum kodu | `200` | `200` |
| `Content-Type` | `application/json` | `application/json; charset=utf-8` |
| `response.json()` sonucu | Sözlük | Sözlük |
| Bağlantı sorunu nasıl yakalanır? | `except httpx.ConnectError` | `except httpx.RequestError`: bağlantı hatasını ve zaman aşımını birlikte kapsar |

İstemci, sunucunun yan odada mı yoksa başka bir ülkede mi olduğunu bilmek zorunda değil. Bildiği tek şey adres ve üzerinde anlaşılan biçim. **API'nin anlamı da budur.**

Yanıtın gövdesi şöyle:

```json
{
  "latitude": 41.3125,
  "longitude": 36.3125,
  "generationtime_ms": 0.0871419906616211,
  "utc_offset_seconds": 10800,
  "timezone": "Europe/Istanbul",
  "timezone_abbreviation": "GMT+3",
  "elevation": 55.0,
  "daily_units": {
    "time": "iso8601",
    "temperature_2m_max": "°C",
    "precipitation_probability_max": "%"
  },
  "daily": {
    "time": ["2026-10-06"],
    "temperature_2m_max": [18.2],
    "precipitation_probability_max": [48]
  }
}
```

Föyün Deney 7'sinde gördüğümüz JSON türleri burada da var:

| Alan | JSON türü |
|---|---|
| `"timezone": "Europe/Istanbul"` | Metin |
| `"elevation": 55.0` | Sayı |
| `"daily": {...}` | İç içe nesne |
| `"temperature_2m_max": [18.2]` | Dizi |

> **Not:** İstekte `41.27976` enlemini gönderdik, ama yanıtta `41.3125` geldi. Open-Meteo, kendi hava durumu verisindeki en yakın ızgara noktasının konumunu döndürdü. Yanıtta hangi verinin hangi biçimde gönderileceğine sunucu karar verir.

---

## 6. Yol mu, sorgu mu?

|  | Yolda | Sorguda |
|---|---|---|
| Kitap API'si | Hangi kitap: `/book/42` | Arama ve filtre: `?search=API&available=true` |
| Open-Meteo | Hangi işlem: `/v1/forecast` | Ayarlar: konum, istenen veriler, gün sayısı |

Yaygın kural şudur:

- **Yol**, hangi kaynağın ya da işlemin istendiğini söyler.
- **Sorgu**, o isteğin ayarlarını, filtrelerini ve seçeneklerini taşır.

Bu bir zorunluluk değil, yaygın bir tasarım alışkanlığıdır. Hangi bilginin nerede gönderileceğine API'yi tasarlayan karar verir; istemci de API'nin belgelerine uyar.

Open-Meteo'nun yolundaki `v1`, API'nin **sürüm** numarasıdır. API ileride değişirse eski istemcilerin bozulmaması için yeni sürüm farklı bir yolla (örneğin `v2`) sunulabilir.

---

## 7. Dene

1. `url_parts.py` dosyasındaki listeye kendi seçtiğin bir web adresini ekle ve parçalarını incele.
2. `weather_client.py` içinde `forecast_days` değerini `3` yap ve `print(len(daily["time"]))` satırını ekle. Kaç gün geldi?
3. Koordinatları kendi şehrinin koordinatlarıyla değiştir.
4. `latitude` değerini `100` yap. Hangi durum kodu ve hangi gövde geldi? Föyün Deney 8'indeki `422` ile karşılaştır.
5. Föydeki sunucu çalışırken adresteki `127.0.0.1` yerine `localhost` yaz. Sonuç değişti mi?
6. Port yazmadan `http://127.0.0.1/book/42` adresine istek gönder. Hangi hata geldi? Neden?
7. İnternet bağlantını kapatıp `weather_client.py`'yi çalıştır. Hangi mesaj çıktı?

---

## 8. Tartışma soruları

1. `https://api.open-meteo.com/v1/forecast?latitude=41.27976` adresinde yol hangi kısımdır? Sorgu hangi kısımdır?
2. Open-Meteo adresinde port neden yazmıyor?
3. `127.0.0.1` ile `api.open-meteo.com` arasındaki fark nedir? DNS ne işe yarar?
4. Adresin hangi parçaları bağlantı kurmak için, hangileri istek mesajında kullanılır?
5. Kitap API'sine ve Open-Meteo'ya istek gönderen kodlarda ne değişti, ne aynı kaldı?
6. Kitap kimliği neden yolda, Open-Meteo'daki konum neden sorguda gönderiliyor?
7. Hava durumu isteğinde `timeout` neden artırıldı?

### Cevaplarda aranacak noktalar

**Dene:**

2. Üç gün gelir; `daily` içindeki her dizi üç eleman içerir.
4. `400` durum kodu ve `{"error":true,"reason":"Latitude must be in range of -90 to 90°. Given: 100.0."}` gövdesi gelir. Open-Meteo da gelen değeri kontrol ediyor; bu hata için `400` kullanıyor. FastAPI tür hatalarında `422` kullanır. Hangi durum kodunun kullanılacağına API'yi yazan karar verir; ortak nokta, hatanın istemcinin gönderdiği veriden kaynaklanmasıdır.
5. Değişmez; `localhost` ile `127.0.0.1` aynı bilgisayarı gösterir.
6. `ConnectError` gelir. Port yazılmadığı için istek 80 numaralı kapıya gider; orada bekleyen bir program yoktur.
7. `Request failed: Check your internet connection.` mesajı çıkar. Alan adı çözülemediği ya da bağlantı kurulamadığı için `httpx.RequestError` yakalanır.

**Tartışma soruları:**

1. Yol `/v1/forecast`, sorgu `latitude=41.27976` kısmıdır.
2. Şema `https` olduğu için varsayılan port `443` kullanılır.
3. `127.0.0.1` bu bilgisayarı gösteren bir IP adresidir. `api.open-meteo.com` bir alan adıdır; DNS bu adı bağlanılacak IP adresine çevirir.
4. Şema, sunucunun adresi ve port bağlantıyı kurmak için kullanılır. Yol ve sorgu istek mesajının içinde gider.
5. Değişen yalnızca adres, sorgu parametreleri ve bekleme süresidir. İstek yine `httpx.get(...)` ile gönderilir, yanıt yine durum kodu ve JSON gövdeden oluşur, `response.json()` yine sözlük verir.
6. Kitap kimliği hangi kaynağın istendiğini belirtir, bu yüzden yoldadır. Konum ise tahmin işleminin bir ayarıdır, bu yüzden sorgudadır. Bu bir tasarım tercihidir.
7. İnternetteki bir sunucunun yanıtı ağın durumuna göre gecikebilir; varsayılan 5 saniye yetmeyebilir.

---

## Resmî belgeler

- [Open-Meteo — API belgeleri](https://open-meteo.com/en/docs)
- [HTTPX — QuickStart](https://www.python-httpx.org/quickstart/)
- [HTTPX — Exceptions](https://www.python-httpx.org/exceptions/)
- [MDN — What is a URL?](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/What_is_a_URL)
- [MDN — What is a domain name?](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/What_is_a_domain_name)

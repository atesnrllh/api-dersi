# Ek Not — Kitabın Bilgileri Mesajın Neresinde Gider?

Föyün Deney 3'ündeki karşılaştırmada iki tasarım yan yana duruyor:

| İşlem | `bad_server.py` | REST'e uygun API'miz |
|---|---|---|
| Yeni kitap | `POST /createNewBook?title=Yeni%20Kitap` | `POST /books`, kitap bilgileri gövdede |

Bu notta "gövdede" sözünün ne demek olduğunu, sunucuya giden mesajın kendisine bakarak görüyoruz.

---

## 1. curl ile gönderilen mesajlar

İki komutu çalıştırıp sunucuya gerçekte ne gittiğini yakaladık.

**`bad_server.py` için:**

```bash
curl -X POST "http://127.0.0.1:8000/createNewBook?title=Yeni%20Kitap"
```

```http
POST /createNewBook?title=Yeni%20Kitap HTTP/1.1
Host: 127.0.0.1:8000
User-Agent: curl/7.81.0
Accept: */*

```

Kitabın adı **ilk satırda, adresin içinde**. Son boş satırdan sonra hiçbir şey yok.

**Bizim API'miz için:**

```bash
curl -X POST http://127.0.0.1:8000/books -H "Content-Type: application/json" -d '{"title": "HTTP ile Yeni Bir Kitap", "author": {"first_name": "Ada", "last_name": "Yıldız"}, "available": true, "tags": ["http", "python"], "rating": null}'
```

```http
POST /books HTTP/1.1
Host: 127.0.0.1:8000
User-Agent: curl/7.81.0
Accept: */*
Content-Type: application/json
Content-Length: 157

{"title": "HTTP ile Yeni Bir Kitap", "author": {"first_name": "Ada", "last_name": "Yıldız"}, "available": true, "tags": ["http", "python"], "rating": null}
```

İlk satırda yalnızca `/books` var. Kitabın bilgileri **boş satırdan sonra, mesajın en altında** duruyor. Mesajın bu alt kısmına **gövde** denir.

| | Kitabın bilgileri nerede? |
|---|---|
| `bad_server.py` | İlk satırda, adresin `?` işaretinden sonraki kısmında |
| Bizim API'miz | Boş satırdan sonra, gövdede |

Neden gövdede? Adrese yalnızca kısa bilgiler sığar: tek satırdır, boşluk bile `%20` olarak yazılmak zorundadır. Yazarı, etiket listesi olan bütün bir kitap gövdeye daha rahat sığar.

---

## 2. HTTPX ile gönderilen mesajlar

Aynı iki isteği `client.py` dosyasındaki gibi HTTPX ile gönderdik.

**`bad_server.py` için:**

```python
httpx.post(base_url + "/createNewBook", params={"title": "Yeni Kitap"})
```

```http
POST /createNewBook?title=Yeni+Kitap HTTP/1.1
Host: 127.0.0.1:8000
Content-Length: 0
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
User-Agent: python-httpx/0.28.1

```

Kitabın adı yine ilk satırda, adresin içinde. Gövde boş: `Content-Length: 0`.

**Bizim API'miz için:**

```python
httpx.post(base_url + "/books", json=new_book)
```

```http
POST /books HTTP/1.1
Host: 127.0.0.1:8000
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
User-Agent: python-httpx/0.28.1
Content-Length: 144
Content-Type: application/json

{"title":"HTTP ile Yeni Bir Kitap","author":{"first_name":"Ada","last_name":"Yıldız"},"available":true,"tags":["http","python"],"rating":null}
```

İlk satırda yalnızca `/books` var. Kitabın bilgileri boş satırdan sonra, gövdede.

Kodda bilginin nereye gideceğini `params=` ve `json=` belirler:

| Kod | Bilgi nereye gider? |
|---|---|
| `params={"title": "Yeni Kitap"}` | Adresin `?` işaretinden sonraki kısmına |
| `json=new_book` | Gövdeye; adreste görünmez |

---

## 3. curl ile HTTPX arasındaki küçük farklar

Mesajın yapısı ikisinde de aynı. Değişen birkaç küçük ayrıntı var:

| | curl | HTTPX |
|---|---|---|
| Adresteki boşluk | `%20` (biz yazdık) | `+` (HTTPX yazdı) |
| JSON'daki boşluklar | `"title": "..."`: biz nasıl yazdıysak öyle | `"title":"..."`: HTTPX boşluksuz yazar |
| `User-Agent` başlığı | `curl/7.81.0` | `python-httpx/0.28.1` |
| `Content-Type` başlığı | Biz `-H` ile ekledik | HTTPX `json=` görünce kendisi ekledi |

Adresteki `%20` ile `+` farkı [boşluk ek notunda](05_Supplement_Space_Encoding.md) anlatılıyor.

---

## 4. Kendi istemcinde görmek için

HTTPX'in gönderdiği isteğin adresini ve gövdesini, Hafta 2'de kullandığımız `response.request` ile ekrana yazdırabilirsin:

```python
print("URL:", response.request.url)
print("Body:", response.request.content.decode())
```

İki istek için çıktı:

```text
URL: http://127.0.0.1:8000/createNewBook?title=Yeni+Kitap
Body: 
```

```text
URL: http://127.0.0.1:8000/books
Body: {"title":"HTTP ile Yeni Bir Kitap","author":{"first_name":"Ada","last_name":"Yıldız"},"available":true,"tags":["http","python"],"rating":null}
```

`response.request.content` gövdeyi bayt olarak verir; `.decode()` onu metne çevirir. İlk istekte gövde boş olduğu için `Body:` satırının devamı boş kalır.

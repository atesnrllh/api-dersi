# Ek Not — Adreste Boşluk Nasıl Yazılır?

Föyün Deney 3'ünde kitabın adını adreste gönderdik:

```bash
curl -X POST "http://127.0.0.1:8000/createNewBook?title=Yeni%20Kitap"
```

Bu notta iki soruyu cevaplıyoruz: **`%20` nedir?** ve **Aynı isteği HTTPX ile gönderirsek sunucuya ne gider?**

---

## 1. `%20` nedir?

Adreste boşluk olamaz. HTTP mesajının ilk satırı boşluklarla üç parçaya ayrılır:

```http
POST /createNewBook?title=Yeni%20Kitap HTTP/1.1
```

Adreste boşluk olsaydı (`Yeni Kitap`), sunucu satırı yanlış yerden bölerdi. Bu yüzden boşluk adreste özel bir yazımla gönderilir.

Bilgisayar karakterleri sayı olarak saklar; her karakterin bir numarası vardır. Bu numaraları veren en temel tablo **ASCII**'dir. Adreste özel bir karakter yazmak için `%` işaretinden sonra o karakterin numarası 16'lık sayı sisteminde yazılır:

| Karakter | ASCII numarası | 16'lık sistemde | Adreste yazılışı |
|---|---|---|---|
| boşluk | 32 | `20` | `%20` |
| `+` | 43 | `2B` | `%2B` |
| `A` | 65 | `41` | `A` (harf olduğu için olduğu gibi yazılır) |

ASCII tablosunda Türkçe harfler yoktur. `ğ` gibi harfler **UTF-8** ile iki sayıyla yazılır: `C4` ve `9F`. Adreste `%C4%9F` olarak görünür.

---

## 2. HTTPX boşluğu nasıl gönderir?

Föydeki `bad_server.py` sunucusunu başlat:

```bash
python -m uvicorn bad_server:app
```

Proje klasöründe `space_client.py` adlı ayrı bir dosya oluştur. Kitabın adını bu kez `params=` ile gönderiyoruz; adresi kendimiz yazmıyoruz:

```python
import httpx

response = httpx.post(
    "http://127.0.0.1:8000/createNewBook",
    params={"title": "Yeni Kitap"}
)
print("Sent URL:", response.request.url)
print("Response body:", response.text)
```

Önce föydeki curl komutunu, sonra istemciyi çalıştır:

```text
Sent URL: http://127.0.0.1:8000/createNewBook?title=Yeni+Kitap
Response body: {"id":59,"title":"Yeni Kitap"}
```

HTTPX boşluğu `%20` değil, `+` olarak yazdı. Sunucunun terminalinde iki isteğin satırı şöyle görünür:

```text
INFO:     127.0.0.1:36948 - "POST /createNewBook?title=Yeni%20Kitap HTTP/1.1" 200 OK
INFO:     127.0.0.1:36964 - "POST /createNewBook?title=Yeni+Kitap HTTP/1.1" 200 OK
```

| İstemci | Sunucuya giden sorgu | Fonksiyonun aldığı `title` |
|---|---|---|
| curl (adresi biz yazdık) | `title=Yeni%20Kitap` | `"Yeni Kitap"` |
| HTTPX (`params=`) | `title=Yeni+Kitap` | `"Yeni Kitap"` |

Adresin sorgu bölümünde boşluk için iki yazım da geçerlidir: `%20` ve `+`. FastAPI ikisini de boşluğa çevirir. Bu yüzden `create_new_book` fonksiyonu `%20` ya da `+` görmez; ikisinde de `"Yeni Kitap"` alır. Bu yazımları yalnızca sunucunun terminalindeki istek satırında görürüz.

---

## 3. Kitabın adında gerçekten `+` varsa?

Sorgu bölümünde `+` boşluk demek olduğu için, gerçek bir `+` işareti `%2B` olarak yazılmalıdır. curl ile iki farklı yazımı deneyelim:

```bash
curl -X POST "http://127.0.0.1:8000/createNewBook?title=Yeni+Kitap"
```

```text
{"id":60,"title":"Yeni Kitap"}
```

```bash
curl -X POST "http://127.0.0.1:8000/createNewBook?title=Yeni%2BKitap"
```

```text
{"id":61,"title":"Yeni+Kitap"}
```

Adresi kendimiz yazarken bu ayrıma dikkat etmemiz gerekir. `params=` kullanınca HTTPX bunu kendisi yapar. `space_client.py` dosyasında kitabın adını `"Ağaç ve C++"` yaparsak:

```text
Sent URL: http://127.0.0.1:8000/createNewBook?title=A%C4%9Fa%C3%A7+ve+C%2B%2B
Response body: {"id":62,"title":"Ağaç ve C++"}
```

HTTPX boşlukları `+`, `+` işaretlerini `%2B`, Türkçe harfleri de UTF-8 numaralarıyla yazdı. Sunucu hepsini geri çevirdi ve kitabın adı doğru saklandı.

# Ek Not — Durum Kodunu Kendimiz Belirleyebilir miyiz?

Föyün Deney 2'sinde şu cümle geçiyor: "Başarı kodu belirtmediğimiz için FastAPI varsayılan `200` kodunu gönderdi." Yani `200`, yalnızca biz hiçbir şey belirtmediğimizde gönderilir. Durum kodunu kendimiz de belirleyebiliriz.

---

## 1. Durum kodunu belirlemenin yolları

| Yol | Kod | Gönderilen durum kodu | Derste nerede gördük? |
|---|---|---|---|
| Hiçbir şey belirtmemek | `@app.post("/book")` | `200` | Föy, Deney 2 |
| Dekoratörde belirtmek | `@app.post("/book", status_code=201)` | `201` | Föy, Deney 3 |
| Hata fırlatmak | `raise HTTPException(status_code=404, detail="...")` | `404` | Hafta 1, `get_book` |
| Fonksiyonun içinde değiştirmek | `response.status_code = 201` | `201` | Yeni. `response: Response` parametresini föyün Deney 4'ünde `Location` başlığı için kullandık. |

---

## 2. Hangisi ne zaman kullanılır?

| Yol | Ne zaman? |
|---|---|
| Dekoratörde `status_code` | Fonksiyon her başarılı çalıştığında **aynı** kod gönderilecekse. Örneğin kitap her eklendiğinde `201`. |
| `HTTPException` | Bir **hata** durumunda. Fonksiyon o satırda durur ve hata yanıtı gönderilir. |
| `response.status_code` | Başarılı sonucun koduna fonksiyonun içinde, **duruma göre** karar verilecekse. |

---

## 3. Dört yolu deneyen örnek

> **Not:** Bu örnekteki `server.py` ve `client.py`, föydeki dosyalardan ayrıdır. Föydeki dosyalarını bozmamak için örneği ayrı bir klasörde dene.

### 3.1 `server.py`

Her yol için ayrı bir işlem tanımladık:

```python
from fastapi import FastAPI, HTTPException, Response

app = FastAPI()

books = [{"id": 42, "title": "API Yolculuğu"}]


@app.post("/no-code")
def no_code():
    return {"message": "No status code was set"}


@app.post("/fixed-code", status_code=201)
def fixed_code():
    return {"message": "Status code set in the decorator"}


@app.post("/error-code")
def error_code():
    raise HTTPException(status_code=409, detail="Book already exists")


@app.post("/choose-code/{book_id}")
def choose_code(book_id: int, response: Response):
    for book in books:
        if book["id"] == book_id:
            response.status_code = 200
            return book

    created_book = {"id": book_id, "title": "Yeni Kitap"}
    books.append(created_book)
    response.status_code = 201
    return created_book
```

| Yol | Ne yapar? |
|---|---|
| `/no-code` | Durum kodu belirtilmedi; FastAPI varsayılan `200` kodunu gönderir. |
| `/fixed-code` | Dekoratörde `status_code=201` yazıldı; her başarılı yanıt `201` olur. |
| `/error-code` | `HTTPException` ile `409` hata yanıtı gönderilir. `409`, "çakışma" demektir; örneğin "bu kitap zaten var". |
| `/choose-code/{book_id}` | Kod, fonksiyonun içinde duruma göre seçilir: Kitap zaten listedeyse `200` ile mevcut kitabı döndürür; yoksa ekler ve `201` döndürür. |

### 3.2 `client.py`

İstemci beş yola sırayla POST isteği gönderip her yanıtın durum kodunu ve gövdesini yazdırır:

```python
import httpx

base_url = "http://127.0.0.1:8000"

for path in ["/no-code", "/fixed-code", "/error-code", "/choose-code/42", "/choose-code/74"]:
    response = httpx.post(base_url + path)
    print(path, "->", response.status_code, response.text)
```

### 3.3 Çalıştır

Sunucu terminalinde:

```bash
python -m uvicorn server:app
```

İstemci terminalinde:

```bash
python client.py
```

Çıktı:

```text
/no-code -> 200 {"message":"No status code was set"}
/fixed-code -> 201 {"message":"Status code set in the decorator"}
/error-code -> 409 {"detail":"Book already exists"}
/choose-code/42 -> 200 {"id":42,"title":"API Yolculuğu"}
/choose-code/74 -> 201 {"id":74,"title":"Yeni Kitap"}
```

`/choose-code/42` ile `/choose-code/74` aynı fonksiyonu çalıştırdı, ama farklı durum kodları aldı: `42` listede olduğu için `200`, `74` listede olmadığı için eklenip `201`.

---

## 4. Durum kodunu anlamına uygun seçmek

FastAPI hangi sayıyı yazdığımıza karışmaz; örneğin bir hata durumunda bile `200` gönderebiliriz. Ama istemci sonucu durum koduna bakarak anlar. Föydeki istemci de `if response.status_code == 201:` diye kontrol ediyor. Bu yüzden durum kodu, anlamına uygun seçilmelidir:

| Durum kodu | Anlamı | Örnek |
|---|---|---|
| `200` | Başarılı | Kitap okundu. |
| `201` | Oluşturuldu | Yeni kitap eklendi. |
| `404` | Bulunamadı | İstenen kimlikte kitap yok. |
| `409` | Çakışma | Eklenmek istenen kitap zaten var. |
| `422` | Gönderilen bilgi kurallara uymuyor | Kitabın adı gönderilmedi. Bu kodu FastAPI kendisi gönderir. |

Bunların dışında, fonksiyonun yanıtı tamamen kendisinin oluşturduğu bir yol daha vardır: `return JSONResponse(status_code=201, content={...})`. Bu yolu derste henüz kullanmıyoruz.

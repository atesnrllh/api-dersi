# Ek Not — Sunucunun Sakladığı Kayıt, Gönderdiğimizden Farklı Olabilir

Gerçek uygulamalarda sunucu, kaydı saklarken bazı bilgileri kendisi ekler ya da değiştirir. Bu yüzden bir kaydı ekledikten sonra GET ile okuduğumuzda, **istemcinin gönderdiğini değil, sunucunun sakladığını** görürüz.

Bu notta bunu küçük bir örnekle görüyoruz.

> **Not:** Bu örnekteki `server.py` ve `client.py`, föydeki dosyalardan ayrıdır. Föydeki dosyalarını bozmamak için örneği ayrı bir klasörde dene.

---

## 1. Bu örnekte sunucu kaydı saklarken ne yapıyor?

İstemci yalnızca kitabın adını gönderiyor. Sunucu kaydı saklarken şunları yapıyor:

| Sunucunun yaptığı | Bu örnekte |
|---|---|
| Kimlik ekler | `id` alanına `1` yazar. |
| Oluşturulma zamanını ekler | `created_at` alanına kaydın oluşturulduğu anı yazar. |
| Gönderilmeyen alanlara varsayılan değer koyar | `available` için `True`, `tags` için boş liste `[]` kullanır. |
| Gelen bir değeri düzeltir | Kitabın adının başındaki ve sonundaki boşlukları siler. |

---

## 2. `server.py`

```python
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel


class BookCreate(BaseModel):
    title: str
    available: bool = True
    tags: list[str] = []


app = FastAPI()

books = []


@app.post("/book", status_code=201)
def create_book(book_data: BookCreate, response: Response):
    new_id = 1
    for book in books:
        if book["id"] >= new_id:
            new_id = book["id"] + 1

    created_book = book_data.model_dump()
    created_book["id"] = new_id
    created_book["title"] = created_book["title"].strip()
    created_book["created_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    books.append(created_book)
    response.headers["Location"] = f"/book/{new_id}"
    return created_book


@app.get("/book/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

Föydeki sunucuya göre yeni olan satırlar:

| Kod | Ne yapar? |
|---|---|
| `available: bool = True` | İstemci `available` göndermezse değeri `True` olur. |
| `tags: list[str] = []` | İstemci `tags` göndermezse değeri boş liste olur. |
| `books = []` | Bu örnek boş bir listeyle başlar; bu yüzden ilk kitabın kimliği `1` olur. |
| `created_book["title"].strip()` | Kitabın adının başındaki ve sonundaki boşlukları siler. |
| `datetime.now(timezone.utc).isoformat(timespec="seconds")` | Kaydın oluşturulduğu anı, saniyeye kadar, metin olarak yazar. Sondaki `+00:00`, saatin UTC'ye göre yazıldığını gösterir; Türkiye saati UTC'den 3 saat ileridedir. |

Varsayılan değerleri sunucudaki kod değil, **Pydantic** yerleştirir: İstemci bir alanı göndermezse Pydantic, modelde o alan için yazılan değeri kullanır.

---

## 3. `client.py`

```python
import httpx

base_url = "http://127.0.0.1:8000"

new_book = {
    "title": "  HTTP ile Yeni Bir Kitap  "
}

response = httpx.post(base_url + "/book", json=new_book)
print("Status code:", response.status_code)

location = response.headers["Location"]
read_response = httpx.get(base_url + location)
saved_book = read_response.json()

print("Sent:  ", new_book)
print("Stored:", saved_book)
```

İstemci yalnızca `title` alanını gönderiyor. Adın başına ve sonuna bilerek boşluk koyduk; sunucunun bu boşlukları silip silmediğini göreceğiz.

İstemci kitabı ekledikten sonra `Location` başlığındaki yolla kitabı GET ile geri okuyor. Ekrana iki şey yazdırıyor:

| Satır | Gösterdiği |
|---|---|
| `Sent:` | İstemcinin gönderdiği sözlük (`new_book`) |
| `Stored:` | GET yanıtından okunan, sunucunun sakladığı kayıt (`saved_book`) |

---

## 4. Çalıştır

Sunucu terminalinde:

```bash
python -m uvicorn server:app
```

İstemci terminalinde:

```bash
python client.py
```

Çıktı (zaman sende farklı olur):

```text
Status code: 201
Sent:   {'title': '  HTTP ile Yeni Bir Kitap  '}
Stored: {'title': 'HTTP ile Yeni Bir Kitap', 'available': True, 'tags': [], 'id': 1, 'created_at': '2026-10-15T08:51:33+00:00'}
```

---

## 5. Gönderdiğimiz ile sunucunun sakladığı arasındaki fark

| Alan | Gönderdiğimiz | Sunucunun sakladığı | Farkı kim oluşturdu? |
|---|---|---|---|
| `title` | `'  HTTP ile Yeni Bir Kitap  '` | `'HTTP ile Yeni Bir Kitap'` | Sunucudaki kod: `strip()` boşlukları sildi. |
| `available` | Gönderilmedi | `True` | Pydantic: modeldeki varsayılan değer (`= True`). |
| `tags` | Gönderilmedi | `[]` | Pydantic: modeldeki varsayılan değer (`= []`). |
| `id` | Gönderilmedi | `1` | Sunucudaki kod: kimliği hesapladı. |
| `created_at` | Gönderilmedi | `'2026-10-15T08:51:33+00:00'` | Sunucudaki kod: o anın zamanını yazdı. |

İstemci tek bir alan gönderdi; sunucu kaydı beş alanla sakladı ve birinin değerini değiştirdi. İstemcinin kendi elindeki `new_book` sözlüğü ise hiç değişmedi.

Kaydın sunucudaki gerçek hâlini ancak sunucuya sorarak öğreniriz. Kaydı ekledikten sonra GET ile okumamızın nedeni budur.

Föydeki Deney 3'te sunucu yalnızca kimlik eklediği için gönderdiğimiz ile sakladığı arasındaki tek fark `id` alanıydı. Gerçek uygulamalarda bu fark çoğu zaman bu örnekteki gibi daha büyüktür.

# Ek Not — 8.3'ün Cevabı: Tek Bir Yorumu Okumak

Bu not, föyün 8.3 bölümündeki alıştırmanın cevabıdır. Önce kodu kendin yaz, sonra buradaki cevapla karşılaştır.

İki değişiklik gerekiyor. İkisi de föyün 5.4 bölümündeki `server.py` dosyasına yapılır.

---

## 1. `create_review` fonksiyonuna `Location` başlığını ekle

Fonksiyonun tamamı aşağıda. 5.4'tekinden farkı üç satırda: `def` satırına `response: Response` parametresi, `return` satırının hemen üstüne `Location` satırı eklendi; en üstteki yorum satırı da "201 ve Location döner" olarak güncellendi.

```python
# Yeni yorum: kitaba ekler, 201 ve Location döner.
@app.post("/books/{book_id}/reviews", status_code=201)
def create_review(book_id: int, review_data: ReviewCreate, response: Response):
    book_exists = False
    for book in books:
        if book["id"] == book_id:
            book_exists = True

    if not book_exists:
        raise HTTPException(status_code=404, detail="Book not found")

    new_id = 1
    for review in reviews:
        if review["id"] >= new_id:
            new_id = review["id"] + 1

    created_review = review_data.model_dump()
    created_review["id"] = new_id
    created_review["book_id"] = book_id
    reviews.append(created_review)
    response.headers["Location"] = f"/books/{book_id}/reviews/{new_id}"
    return created_review
```

Hafta 2'deki `create_book` ile aynı kalıp. Tek fark, yolda kitabın kimliğinin de bulunması: `/books/42/reviews/2`. `Response` zaten dosyanın ilk satırında içe aktarılıyor; ayrıca bir şey eklemen gerekmiyor.

---

## 2. Tek bir yorumu okuyan işlemi ekle

`create_review` fonksiyonundan sonra:

```python
# Tek yorum: kitap ve yorum kimliği eşleşmeli, yoksa 404.
@app.get("/books/{book_id}/reviews/{review_id}")
def get_review(book_id: int, review_id: int):
    for review in reviews:
        if review["book_id"] == book_id and review["id"] == review_id:
            return review

    raise HTTPException(status_code=404, detail="Review not found")
```

| Kod | Ne yapar? |
|---|---|
| `{book_id}` ve `{review_id}` | Yolda iki ad var. FastAPI, yoldaki iki sayıyı aynı adlı iki fonksiyon parametresine koyar. |
| `... == book_id and ... == review_id` | Yorum ancak iki koşul da doğruysa döndürülür: Hem doğru kitaba ait olmalı hem de kimliği doğru olmalı. |
| `raise HTTPException(...)` | Döngüde eşleşen yorum bulunmazsa `404` ve `{"detail":"Review not found"}` döner. |

---

## 3. Sonuçlar

Sunucu yeniden başlatıldıktan sonra 8.1'deki curl komutuyla bir yorum eklendi, ardından föydeki istekler gönderildi:

| İstek | Sonuç |
|---|---|
| `POST /books/42/reviews` | `201 Created` ve `location: /books/42/reviews/2` |
| `GET /books/42/reviews/1` | `200`: `{"id":1,"book_id":42,"reader":"Ece","comment":"Konuları örneklerle anlatıyor.","score":5}` |
| `GET /books/42/reviews/2` | `200`: `{"reader":"Can","comment":"İlk API projemi bu kitapla yazdım.","score":4,"id":2,"book_id":42}` |
| `GET /books/42/reviews/9` | `404`: `{"detail":"Review not found"}` |
| `GET /books/57/reviews/1` | `404`: `{"detail":"Review not found"}` |

Son satır `and` kullanımının nedenini gösteriyor. 1 numaralı yorum var, ama 42 numaralı kitaba ait. Yalnızca yorum kimliğine baksaydık, 57 numaralı kitabın yolundan da Ece'nin yorumu gelirdi.

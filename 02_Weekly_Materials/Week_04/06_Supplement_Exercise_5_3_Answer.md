# Ek Not — 5.3'ün Cevabı: Bir Yorumu Silmek

Bu not, föyün 5.3 bölümündeki alıştırmanın cevabıdır. Önce kodu kendin yaz, sonra buradaki cevapla karşılaştır.

---

## 1. Kod

`server.py` dosyasında yorumlarla ilgili fonksiyonlardan sonra şunu ekle:

```python
# Yorumu silme: kitap ve yorum kimliği eşleşmeli, yoksa 404.
@app.delete("/books/{book_id}/reviews/{review_id}", status_code=204)
def delete_review(book_id: int, review_id: int):
    for review in reviews:
        if review["book_id"] == book_id and review["id"] == review_id:
            reviews.remove(review)
            return

    raise HTTPException(status_code=404, detail="Review not found")
```

| Kod | Ne yapar? |
|---|---|
| `@app.delete(..., status_code=204)` | Föyün Deney 1'indeki `delete_book` gibi: Başarılı silmede yanıt `204`, gövde boş. |
| `{book_id}` ve `{review_id}` | Hafta 3'teki 8.3 alıştırması gibi: Yolda iki ad var, fonksiyonun da bu adlarla iki parametresi var. |
| `... == book_id and ... == review_id` | Yorum ancak iki koşul da doğruysa silinir: Hem doğru kitaba ait olmalı hem de kimliği doğru olmalı. |
| `reviews.remove(review)` | Yorumu `reviews` listesinden çıkarır. Hemen ardından gelen `return` döngüyü ve fonksiyonu bitirir. |
| `raise HTTPException(...)` | Eşleşen yorum bulunmazsa `404` ve `{"detail":"Review not found"}` döner. |

---

## 2. Sonuçlar

Sunucu yeniden başlatıldıktan sonra föydeki istekler sırayla gönderildi:

| İstek | Sonuç |
|---|---|
| `DELETE /books/57/reviews/1` | `404`: `{"detail":"Review not found"}` |
| `DELETE /books/42/reviews/1` | `204`, gövde boş |
| `GET /books/42/reviews` | `200`: `[]` |
| `DELETE /books/42/reviews/1` | `404`: `{"detail":"Review not found"}` |

İlk satır `and` kullanımının nedenini gösteriyor. 1 numaralı yorum var, ama 42 numaralı kitaba ait. Yalnızca yorum kimliğine baksaydık, 57 numaralı kitabın yolundan Ece'nin yorumu silinirdi.

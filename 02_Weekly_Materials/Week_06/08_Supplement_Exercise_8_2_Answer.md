# Ek Not — 8.2 Alıştırmasının Cevabı: Tek Yorumu Okumak ve Silmek

Bu not, föydeki 8.2 alıştırmasının bir cevabını veriyor. Kendi kodunu yazıp denedikten sonra karşılaştır.

---

## 1. İki fonksiyon

`server.py` dosyasının sonuna şu iki fonksiyon eklenir. Eski hâllerindeki `for` döngülerinin ve `reviews` listesinin yerini veritabanı alıyor:

```python
# Tek yorum: yoksa ya da yoldaki kitaba ait değilse 404.
@app.get("/books/{book_id}/reviews/{review_id}", response_model=ReviewPublic)
def get_review(book_id: int = Path(gt=0), review_id: int = Path(gt=0)):
    with Session(engine) as session:
        review = session.get(Review, review_id)

        if review is None or review.book_id != book_id:
            raise HTTPException(status_code=404, detail="Review not found")

        return review


# Yorumu silme: 204 döner; yorum yoksa ya da yoldaki kitaba ait değilse 404.
@app.delete("/books/{book_id}/reviews/{review_id}", status_code=204)
def delete_review(book_id: int = Path(gt=0), review_id: int = Path(gt=0)):
    with Session(engine) as session:
        review = session.get(Review, review_id)

        if review is None or review.book_id != book_id:
            raise HTTPException(status_code=404, detail="Review not found")

        session.delete(review)
        session.commit()
```

| Kod | Ne yapar? |
|---|---|
| `session.get(Review, review_id)` | Yorumu birincil anahtarına göre bulur; yoksa `None` verir. Föydeki `get_book` fonksiyonuyla aynı yol. |
| `review is None or review.book_id != book_id` | İki durumda `404`: Yorum yok **ya da** yorum var ama yoldaki kitaba ait değil. Eski koddaki `review["book_id"] == book_id and review["id"] == review_id` koşulunun karşılığı. |
| `response_model=ReviewPublic` | Yanıt, föyde Deney 5'te eklediğimiz modelle hazırlanır; alanlar öteki yorum yanıtlarıyla aynı sırada gelir. |
| `session.delete(review)` ve `session.commit()` | Yorumu veritabanından siler. Föydeki `delete_book` fonksiyonuyla aynı yol. |

`book_id` kontrolünü unutmak kolay: `session.get` yalnızca yorumun kimliğine bakar. Kontrol olmasaydı `GET /books/57/reviews/1` isteği, 42 numaralı kitabın yorumunu 57 numaralı kitabın yorumuymuş gibi döndürürdü; `DELETE /books/57/reviews/1` isteği de onu silerdi.

---

## 2. Sonuçlar

Veritabanı sıfırlandıktan ve sunucu yeniden başlatıldıktan sonra istekler sırayla gönderildi:

| İstek | Durum kodu | Yanıt |
|---|---|---|
| `GET /books/42/reviews/1` | `200` | `{'reader': 'Ece', 'comment': 'Konuları örneklerle anlatıyor.', 'score': 5, 'id': 1, 'book_id': 42}` |
| `GET /books/57/reviews/1` | `404` | `{'detail': 'Review not found'}` |
| `DELETE /books/57/reviews/1` | `404` | `{'detail': 'Review not found'}` |
| `DELETE /books/42/reviews/1` | `204` | Boş |
| `GET /books/42/reviews/1` | `404` | `{'detail': 'Review not found'}` |

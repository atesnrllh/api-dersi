# Ek Not — 7.3 Alıştırmasının Cevabı: Benim Yorumlarım

Bu not, föydeki 7.3 alıştırmasının bir cevabını veriyor. Kendi kodunu yazıp denedikten sonra karşılaştır.

---

## 1. İşlem

`server.py` dosyasının sonuna:

```python
# Giriş yapan kullanıcının yorumları: kimlik sırasıyla.
@app.get("/me/reviews", response_model=list[ReviewPublic])
def read_my_reviews(user: User = Depends(get_current_user)):
    with Session(engine) as session:
        statement = select(Review).where(Review.user_id == user.id).order_by(Review.id)
        return session.exec(statement).all()
```

`get_reviews` fonksiyonundaki sorgu yorumları kitaba göre (`Review.book_id == book_id`), bu sorgu kullanıcıya göre (`Review.user_id == user.id`) süzüyor. Kullanıcının kimliği adresten değil tokenden geliyor: Adreste bir kullanıcı kimliği olmadığı için başka birinin yorumlarını istemek mümkün değil.

---

## 2. Test

```python
# Kullanıcının yorumları: yalnızca kendi yorumları gelir.
def test_my_reviews():
    review = {"comment": "Kısa ve açık.", "score": 4}
    client.post("/books/73/reviews", json=review, headers=login_as("Can", "can-parola"))

    response = client.get("/me/reviews", headers=login_as("Ece", "ece-parola"))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["book_id"] == 42
```

Can'in yorumu testin hazırlığı: Veritabanında başka bir kullanıcının yorumu da olsun ki süzmenin işe yaradığı görülsün. Başlangıç veritabanında yalnızca Ece'nin yorumu var; süzme koşulunu unutan bir fonksiyon da Ece'ye tek yorum döndürürdü ve test bu hatayı yakalamazdı.

---

## 3. Sonuç

7.2 ile birlikte:

```text
============================== 18 passed in 4.91s ==============================
```

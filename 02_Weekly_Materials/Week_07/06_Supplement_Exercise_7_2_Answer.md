# Ek Not — 7.2 Alıştırmasının Cevabı: Yorum ve Arama Testleri

Bu not, föydeki 7.2 alıştırmasının bir cevabını veriyor. Kendi kodunu yazıp denedikten sonra karşılaştır.

---

## 1. Dört test

`test_server.py` dosyasının sonuna şu testler eklenir:

```python
# Yorumlar: 42 numaralı kitabın tek yorumu Ece'nin.
def test_get_reviews():
    response = client.get("/books/42/reviews")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["reader"] == "Ece"


# Yeni yorum: 201, yeni kimlik ve yorumun kitabı.
def test_create_review():
    review = {"reader": "Can", "comment": "Örnekleri çalıştırdım.", "score": 4}

    response = client.post("/books/42/reviews", json=review)

    assert response.status_code == 201
    assert response.json()["id"] == 2
    assert response.json()["book_id"] == 42


# Olmayan kitaba yorum: 404.
def test_review_for_missing_book():
    review = {"reader": "Can", "comment": "Örnekleri çalıştırdım.", "score": 4}

    response = client.post("/books/43/reviews", json=review)

    assert response.status_code == 404


# Türkçe harfle arama: "ilk", "Veriyle İlk Adımlar" kitabını bulur.
def test_search_turkish_letters():
    response = client.get("/books", params={"search": "ilk"})

    ids = []
    for book in response.json():
        ids.append(book["id"])
    assert ids == [57]
```

| Test | Dikkat edilecek nokta |
|---|---|
| `test_get_reviews` | `len(response.json()) == 1`, listede tam bir yorum olduğunu kontrol eder. `[0]`, listenin ilk öğesi. |
| `test_create_review` | Yorumun kimliğinin `2` olmasını, hazırlık fonksiyonunun her testten önce veritabanını sıfırlamasına borçluyuz: Sayaç her seferinde 1'den devam ediyor. |
| `test_review_for_missing_book` | Gövde kurallara uygun; yalnızca kitap yok. Gövdede de bir hata olsaydı `422` gelirdi, çünkü FastAPI gövdeyi fonksiyon çalışmadan önce kontrol eder (Hafta 5, Deney 5). |
| `test_search_turkish_letters` | Hafta 6'daki ek notta, Hafta 5'in sunucusunun bu aramada boş liste döndürdüğünü görmüştük. Bu test, aramayı yeniden Python'a taşıyan biri olursa farkın fark edilmesini sağlar. |

---

## 2. Sonuç

```text
============================== 14 passed in 2.07s ==============================
```

Föyün sonundaki on teste dört test eklendi.

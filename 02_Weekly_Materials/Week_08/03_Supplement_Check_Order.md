# Ek Not — Kontrollerin Sırası

Föyün Deney 1'inde, iki kuralı birden çiğneyen bir isteğe ilk sıradaki adımın yanıt verdiğini gördük. Bu notta aynı soruya üç istekle daha yakından bakıyoruz: Bir istekte birden fazla `422` hatası olursa ne olur, fonksiyonun içindeki kontroller hangi sırayla yapılır ve yol yanlışsa gövdeye bakılır mı?

---

## 1. Üç istek

Föyün başlangıç dosyalarıyla, `server.py` ile aynı klasörde `order.py` adlı bir dosya oluşturduk:

```python
from fastapi.testclient import TestClient

from database import reset_database
from server import app

client = TestClient(app)

reset_database()

response = client.patch("/books/-1", json={"rating": 9, "title": ""})
print(response.status_code)
for error in response.json()["detail"]:
    print(error["loc"], error["msg"])

response = client.post("/books/43/reviews", json={"reader": "Ece", "comment": "Yine güzel.", "score": 4})
print(response.status_code, response.json())

response = client.post("/book/42/reviews", json={"reader": "Ece", "comment": "", "score": 9})
print(response.status_code, response.json())
```

```text
422
['path', 'book_id'] Input should be greater than 0
['body', 'title'] String should have at least 1 character
['body', 'rating'] Input should be less than or equal to 5
404 {'detail': 'Book not found'}
404 {'detail': 'Not Found'}
```

---

## 2. Birden fazla `422` hatası: hepsi birden

İlk istekte üç sorun var: Kimlik negatif, ad boş, puan 5'ten büyük. Yanıt üçünü birden listeliyor.

FastAPI, 2. adımda yol parametresini, sorgu parametrelerini ve gövdeyi tek tek kontrol eder ve bulduğu bütün hataları toplar. İlk hatada durmaz. Böylece istemci bütün hatalarını tek bir yanıtta görür ve isteği bir kerede düzeltebilir. Föydeki `show` fonksiyonu yalnızca listenin ilk öğesini yazdığı için bunu Deney 1'de görmedik.

Hafta 5'in 2.3 bölümünde, üç alanı da hatalı bir yorumda aynı şeyi görmüştük: `detail` listesinde üç hata vardı. Burada hatalar iki ayrı yerden geliyor, yoldan ve gövdeden, ama yine tek listede.

---

## 3. Fonksiyonun içindeki sıra: önce kitap, sonra okur

İkinci istekte Ece, olmayan 43 numaralı kitaba yorum yazıyor. Gövde kurallara uygun, bu yüzden fonksiyon çalışıyor. `create_review` fonksiyonunda iki kontrol var:

```python
        if session.get(Book, book_id) is None:
            raise HTTPException(status_code=404, detail="Book not found")

        statement = select(Review).where(Review.book_id == book_id).where(Review.reader == review_data.reader)
        if session.exec(statement).first() is not None:
            raise HTTPException(status_code=409, detail="This reader has already reviewed this book")
```

İlk `raise` satırı fonksiyonu orada bitirir; ikinci kontrole hiç gelinmez. Fonksiyonun içindeki kontrollerin sırasını FastAPI değil, biz belirliyoruz: Kodda hangisi önce yazılmışsa o.

Bu sıra bir tercih ama keyfî değil. Olmayan bir kitap için "bu okur bu kitaba yorum yazmış mı?" sorusu anlamsız. Önce kaynağın var olup olmadığını sormak, istemciye daha doğru bilgiyi verir.

---

## 4. Yol yanlışsa gövdeye bakılmaz

Üçüncü istekte gövdede iki hata var (boş yorum, `9` puan), ama yanıt `422` değil `404 Not Found`. Yol (`/book/42/reviews`) hiçbir fonksiyonla eşleşmedi. Gövdenin hangi kurallara uyması gerektiğini fonksiyonun parametreleri söylüyor (`review_data: ReviewCreate`); eşleşen bir fonksiyon olmadığı için kontrol edilecek bir kural da yok.

---

## 5. Sıranın özeti

| Sıra | Adım | Bu adımın yanıtları | Sırayı kim belirliyor? |
|---|---|---|---|
| 1 | Yol ve metot eşleştirme | `404 Not Found`, `405 Method Not Allowed` | FastAPI |
| 2 | Parametreler ve gövde | `422`; bütün hatalar bir listede | FastAPI |
| 3 | Fonksiyonun kendisi | `404 Book not found`, `409` ve başarılı yanıtlar | Biz: kontrollerin koddaki sırası |

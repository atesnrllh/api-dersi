# Ek Not — 6.2 Alıştırmasının Cevabı: Bildirilen İkinci Hata

Bu not, föydeki 6.2 alıştırmasının bir cevabını veriyor. Kendi kodunu yazıp denedikten sonra karşılaştır.

---

## 1. Bildirimi teste çevirmek

`test_server.py` dosyasının sonuna şu test eklenir:

```python
# Yorum: bir okur farklı kitaplara yorum yazabilir.
def test_review_other_book():
    review = {"reader": "Ece", "comment": "Kısa ve açık.", "score": 4}

    response = client.post("/books/73/reviews", json=review)

    assert response.status_code == 201
    assert response.json()["book_id"] == 73
```

Hazırlık fonksiyonu veritabanını her testten önce sıfırladığı için Ece'nin 42 numaralı kitaba yazdığı yorum veritabanında hazır: Bildirimdeki durumu kurmak için ayrıca bir şey yapmaya gerek yok.

---

## 2. Testin kaldığını görmek

Ekip arkadaşının değişikliği koddayken testler:

```text
test_server.py ............F                                             [100%]

=================================== FAILURES ===================================
____________________________ test_review_other_book ____________________________

    def test_review_other_book():
        review = {"reader": "Ece", "comment": "Kısa ve açık.", "score": 4}

        response = client.post("/books/73/reviews", json=review)

>       assert response.status_code == 201
E       assert 409 == 201
E        +  where 409 = <Response [409 Conflict]>.status_code

test_server.py:147: AssertionError
=========================== short test summary info ============================
FAILED test_server.py::test_review_other_book - assert 409 == 201
========================= 1 failed, 12 passed in 2.15s =========================
```

`assert 409 == 201`: Ece'nin bildirdiği `409` testte de geldi. `where 409 = <Response [409 Conflict]>.status_code` satırı, soldaki `409` değerinin yanıtın durum kodundan geldiğini söylüyor. Hata tekrar üretildi.

---

## 3. Hatanın yeri

`409` yanıtını `create_review` fonksiyonundaki tek bir satır veriyor. O satıra şu sorgu bir yorum bulduğunda geliniyor:

```python
        statement = select(Review).where(Review.reader == review_data.reader)
```

Sorgu, okuru Ece olan **bütün** yorumları arıyor; hangi kitaba yazıldıklarına bakmıyor. Ece'nin 42 numaralı kitaba yazdığı yorum bu sorguya uyuyor, bu yüzden 73 numaralı kitaba yazdığı ilk yorum da `409` alıyor.

Kural "aynı okur **aynı kitaba** ikinci kez yorum yazamaz" idi. Sorgunun iki koşulu da sorması gerekir: kitap ve okur. Satır Hafta 6'daki hâline döner:

```python
        statement = select(Review).where(Review.book_id == book_id).where(Review.reader == review_data.reader)
```

Testler:

```text
============================== 13 passed in 1.74s ==============================
```

---

## 4. `test_create_review` neden yakalamadı?

Hafta 7'nin 7.2 alıştırmasındaki test, **Can**'in 42 numaralı kitaba yorumunu gönderiyordu. Başlangıç veritabanında Can'in hiç yorumu yok. Hatalı sorgu da Can için bir yorum bulamaz ve yorum `201` ile eklenir. Hata ancak daha önce **başka bir kitaba** yorum yazmış bir okurla görünür; o durumu kuran bir test yoktu.

Bir davranışı test ederken yalnızca "çalışıyor mu?" değil, "kural hangi durumları ayırıyor?" diye de sormak gerekir. Bu kural iki durumu ayırıyordu: aynı kitap (`409`) ve başka kitap (`201`). Hafta 7'de yalnızca birincinin testi vardı.

# Ek Not — 6.3 Alıştırmasının Cevabı: Deney 1'in Testleri

Bu not, föydeki 6.3 alıştırmasının bir cevabını veriyor. Kendi kodunu yazıp denedikten sonra karşılaştır.

---

## 1. Üç test

`test_server.py` dosyasının sonuna şu testler eklenir:

```python
# Yanlış yol: FastAPI'nin 404'ü; bizim fonksiyonumuz hiç çalışmaz.
def test_wrong_path():
    response = client.get("/book/42")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


# Yol var, metot yok: 405.
def test_method_not_allowed():
    response = client.delete("/books")

    assert response.status_code == 405


# Olmayan kitaba hatalı puan: gövde, kitap aranmadan önce reddedilir.
def test_invalid_body_before_missing_book():
    response = client.patch("/books/43", json={"rating": 9})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "rating"]
```

| Test | Dikkat edilecek nokta |
|---|---|
| `test_wrong_path` | Yalnızca `404` kontrolü yetmez: `GET /books/43` de `404` alır. Gövdenin tamamını karşılaştırmak, yanıtı bizim fonksiyonumuzun (`Book not found`) değil, FastAPI'nin verdiğini kanıtlar. |
| `test_method_not_allowed` | Bir gün `DELETE /books` için bir fonksiyon yazılırsa, örneğin bütün kataloğu silen bir işlem, bu test kalır. Böyle bir işlemin bilerek eklenip eklenmediği o zaman sorulur. |
| `test_invalid_body_before_missing_book` | `loc` kontrolü, `422` yanıtının yoldan değil gövdeden geldiğini gösterir. 43 numaralı kitap yok; test, buna rağmen yanıtın `404` olmadığını kontrol ediyor. |

---

## 2. Sonuç

`-v` ile:

```text
collecting ... collected 16 items

test_server.py::test_get_book PASSED                                     [  6%]
test_server.py::test_get_missing_book PASSED                             [ 12%]
test_server.py::test_create_book PASSED                                  [ 18%]
test_server.py::test_search_books PASSED                                 [ 25%]
test_server.py::test_rating_out_of_range PASSED                          [ 31%]
test_server.py::test_negative_book_id PASSED                             [ 37%]
test_server.py::test_patch_rating PASSED                                 [ 43%]
test_server.py::test_patch_null_title PASSED                             [ 50%]
test_server.py::test_second_review_conflict PASSED                       [ 56%]
test_server.py::test_delete_book_deletes_reviews PASSED                  [ 62%]
test_server.py::test_filter_not_available PASSED                         [ 68%]
test_server.py::test_replace_book PASSED                                 [ 75%]
test_server.py::test_review_other_book PASSED                            [ 81%]
test_server.py::test_wrong_path PASSED                                   [ 87%]
test_server.py::test_method_not_allowed PASSED                           [ 93%]
test_server.py::test_invalid_body_before_missing_book PASSED             [100%]

============================== 16 passed in 2.24s ==============================
```

Föyün on iki testine 6.2'nin bir ve bu alıştırmanın üç testi eklendi.

# Ek Not — 7.3 Alıştırmasının Cevabı: Hiçbir Testin Yakalamadığı Hata

Bu not, föydeki 7.3 alıştırmasının bir cevabını veriyor. Kendi kodunu yazıp denedikten sonra karşılaştır.

---

## 1. Satırı silince

`replace_book` fonksiyonundan `session.refresh(book)` satırını sildik ve föyün sonundaki on testi çalıştırdık:

```text
============================== 10 passed in 1.84s ==============================
```

Hiçbir test kalmadı. Ama `PUT /books/73` isteği artık `500` alıyor; Hafta 6'daki ek notta `PATCH` için gördüğümüz hatanın aynısı. Testlerin hiçbiri `PUT` isteği göndermediği için hatayı yakalayan da yok.

---

## 2. Test

`test_server.py` dosyasının sonuna şu test eklenir:

```python
# PUT: bütün alanlar yenisiyle değişir.
def test_replace_book():
    response = client.put("/books/73", json=new_book)

    assert response.status_code == 200
    assert response.json()["title"] == "Test Kitabı"

    response = client.get("/books/73")
    assert response.json()["title"] == "Test Kitabı"
```

Satır silinmişken testleri `--tb=short` ile çalıştırdık. Hata izinin sonundaki satırlar aşağıda; 7.2'deki testleri de eklediysen `test_server.py` satır numarası seninkinde farklı olur:

```text
test_server.py:124: in test_replace_book
...
E   fastapi.exceptions.ResponseValidationError: 6 validation errors:
E     {'type': 'get_attribute_error', 'loc': ('response', 'title'), 'msg': 'Error extracting attribute: DetachedInstanceError: ...
...
E     File ".../server.py", line 108, in replace_book
E       PUT /books/{book_id}
```

Hata, yanıtı hazırlarken çıktı (`loc` alanının ilk öğesi `response`; Hafta 5, Deney 3). FastAPI, hatanın hangi fonksiyonda ve hangi işlemde çıktığını da yazıyor: `server.py` dosyasının 108. satırı, `replace_book`, `PUT /books/{book_id}`.

Satırı geri koyunca:

```text
============================== 11 passed in 1.89s ==============================
```

---

## 3. Bundan ne öğreniyoruz?

Bütün testlerin geçmesi, yalnızca **test edilen** davranışların doğru olduğunu söyler. Hiç test edilmeyen bir işlem bozulursa testler sessiz kalır. Testlerin kodun ne kadarını kontrol ettiğine **kapsam (coverage)** denir.

Bu yüzden testlere yeni bir işlem eklendiğinde onun testi de eklenir; bir hata bulunduğunda da önce o hatayı yakalayan test yazılır, sonra hata düzeltilir. Böylece aynı hata bir daha sessizce geri gelemez.

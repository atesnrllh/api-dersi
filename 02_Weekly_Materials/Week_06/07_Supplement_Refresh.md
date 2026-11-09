# Ek Not — `session.refresh` Unutulursa

Föyün Deney 4'ünde `replace_book` ve `update_book` fonksiyonlarına, `commit` satırından sonra `session.refresh(book)` yazdık. Bu notta o satır olmasaydı ne olacağını görüyoruz.

---

## 1. Deney: `refresh` olmadan `PATCH`

`update_book` fonksiyonundan `session.refresh(book)` satırını sildik:

```python
        changes = book_data.model_dump(exclude_unset=True)
        book.sqlmodel_update(changes)
        session.commit()
        return book
```

Veritabanını sıfırladık, sunucuyu yeniden başlattık ve iki istek gönderdik:

| İstek | Sonuç |
|---|---|
| `PATCH /books/57`, `{"rating": 3}` | `500 Internal Server Error` |
| `GET /books/57` | `200`, puan `3.0` |

İstemci `500` aldı, ama değişiklik veritabanına yazılmış. İstemci "işlem başarısız oldu" diye düşünüp aynı isteği tekrar gönderebilir; oysa ilk istek zaten başarılıydı.

Sunucunun terminalinde hatanın içinde şu parça vardı:

```text
'loc': ('response', 'title'), 'msg': 'Error extracting attribute: DetachedInstanceError: Instance <Book at 0x...> is not bound to a Session; ...
```

`loc` alanının ilk öğesi `response`: Hata istekte değil, yanıtı hazırlarken çıktı (Hafta 5, Deney 3). *Detached* "ayrılmış" demek: `Book` nesnesi artık bir oturuma bağlı değil.

---

## 2. Neden?

Adım adım:

1. `session.commit()` değişikliği veritabanına yazdı. Ardından oturum, nesnedeki değerleri unuttu; bir sonraki kullanımda veritabanından yeniden okuyacaktı. Böylece nesne, başka bir programın veritabanında yapmış olabileceği değişikliklerle eski kalmaz.
2. Fonksiyon `book` nesnesini döndürdü; `with` bloğu bitti ve oturum kapandı.
3. FastAPI, yanıtı `BookPublic` modeline göre hazırlamak için `book.title` değerini okumak istedi. Değer unutulmuştu ve onu veritabanından getirecek oturum yoktu.

`session.refresh(book)`, değerleri oturum kapanmadan veritabanından yeniden okur; FastAPI yanıtı hazırlarken değerler nesnede durur.

---

## 3. `create_book` neden yine de çalışıyordu?

Aynı satırı `create_book` fonksiyonundan silince `POST /books` isteği `201` almaya devam etti. Çünkü o fonksiyonda `commit` satırından sonra `response.headers["Location"] = f"/books/{book.id}"` satırı var: `book.id` okunurken oturum henüz açık ve nesnenin bütün değerleri veritabanından yeniden okunuyor.

Bu bir rastlantı: `Location` satırı başka bir yere taşınırsa aynı hata ortaya çıkar. Föyde `refresh` satırını her yazma işleminde açıkça yazıyoruz; veritabanının verdiği değerleri, örneğin yeni kimliği, okumak istediğimizi böylece kod da söylüyor.

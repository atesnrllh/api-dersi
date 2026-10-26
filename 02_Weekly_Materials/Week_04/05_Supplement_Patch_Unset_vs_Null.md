# Ek Not — PATCH'te Gönderilmeyen Alan ile `null` Gönderilen Alan

Föyün Deney 3'ündeki `update_book` fonksiyonu, kitabı değiştirmeden önce şu satırla bir sözlük oluşturuyor:

```python
changes = book_data.model_dump(exclude_unset=True)
```

Bu notta `exclude_unset=True` yazılmazsa ne olduğuna ve bir alanın "gönderilmemesi" ile "`null` gönderilmesi" arasındaki farka bakıyoruz.

---

## 1. Üç gövde, üç sonuç

Föyün Deney 4 sonundaki sunucuya 73 numaralı kitap için üç `PATCH` isteği gönderdik. Kitabın başlangıçtaki puanı `4.5`.

| Gövde | Yanıttaki `rating` | Ne oldu? |
|---|---|---|
| `{}` | `4.5` | Hiçbir alan gönderilmedi; kitap değişmedi. |
| `{"rating": null}` | `null` | `rating` alanı **gönderildi** ve değeri `null`. Puan silindi. |
| `{"available": false}` | `4.5` | `rating` gönderilmedi; eski değerini korudu. Yalnızca `available` değişti. |

Pydantic modeli bu iki durumu ayırt edebilir: Bir alanın değeri `None` olabilir, ama o alan gövdede **gönderilmiş** ya da **gönderilmemiş** olabilir. `exclude_unset=True`, gönderilmemiş alanları sözlüğe almaz; gönderilmiş ama `null` olan alanları alır.

Yani bir istemci puanı silmek isterse `{"rating": null}` gönderir; puana dokunmak istemiyorsa `rating` alanını hiç yazmaz.

---

## 2. `exclude_unset=True` yazılmasaydı

`update_book` fonksiyonunda o satırı `book_data.model_dump()` olarak değiştirip aynı isteği gönderdik:

```bash
curl -X PATCH http://127.0.0.1:8000/books/42 -H "Content-Type: application/json" -d '{"available": false}'
```

```text
{"id":42,"title":null,"author":null,"available":false,"tags":null,"rating":null}
```

`BookUpdate` modelindeki bütün alanların varsayılan değeri `None`. `exclude_unset=True` olmadan, gönderilmeyen her alan `None` olarak sözlüğe girdi ve kitabın üzerine yazıldı. Kitabın adı, yazarı ve etiketleri silindi; `PATCH` istediğimiz gibi çalışmadı.

Bu denemeyi yanıt modeli olmayan sunucuyla (Deney 3 sonundaki) yaptık. Deney 4'teki yanıt modeliyle denersen sonuç daha da kötü olur; nedeni aşağıda.

---

## 3. Zorunlu bir alana `null` göndermek

`BookUpdate` modelinde bütün alanlar `None` olabildiği için, istemci `{"title": null}` da gönderebilir. Deney 4 sonundaki sunucuda bunu denedik:

```bash
curl -i -X PATCH http://127.0.0.1:8000/books/42 -H "Content-Type: application/json" -d '{"title": null}'
```

```text
HTTP/1.1 500 Internal Server Error
...
Internal Server Error
```

Sunucu kitabın adını `None` yaptı. Sonra yanıtı `Book` modeline göre hazırlamak istedi; ama `Book` modelinde `title` bir metin olmak zorunda. Yanıt hazırlanamadı ve sunucu `500` hatası verdi. Kitap da bozuk kaldı: Bundan sonra `GET /books/42` isteği de `500` alıyor.

**500 Internal Server Error**, "sunucuda bir hata oldu" demektir; sorunun istemcide değil, sunucuda olduğunu söyler.

Bunu önlemek için `BookUpdate` modelinde "`title` gönderilebilir ama `null` olamaz" gibi kurallar yazmak gerekir. Alanların kabul edeceği değerleri ve hata yanıtlarını 5. haftada göreceğiz.

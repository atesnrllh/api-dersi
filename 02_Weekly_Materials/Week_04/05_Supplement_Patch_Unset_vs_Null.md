# Ek Not — PATCH'te Gönderilmeyen Alan ile `null` Gönderilen Alan

Föyün Deney 3'ündeki `update_book` fonksiyonu kitabı şu iki satırla değiştiriyor:

```python
changes = book_data.model_dump(exclude_unset=True)
book.update(changes)
```

`exclude_unset=True`, `changes` sözlüğüne yalnızca istemcinin gövdede **gönderdiği** alanları koyar; gönderilmeyen alanları koymaz. Gövdede `null` değeriyle gönderilen bir alan ise gönderilmiş sayılır ve sözlüğe girer.

Bu notta üç soruyu cevaplıyoruz:

1. Bir alanı **hiç göndermemek** ile **`null` göndermek** sunucuda ne fark yaratıyor?
2. `exclude_unset=True` yazılmasaydı ne olurdu?
3. İstemci zorunlu bir alana `null` gönderirse ne olur?

---

## 1. Gönderilmeyen alan ile `null` gönderilen alan

Föyün Deney 4 sonundaki sunucuyu kullanıyoruz. 73 numaralı kitabın başlangıçtaki puanı `4.5`.

`client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"

try:
    # Kitabı oku: değiştirmeden önce.
    response = httpx.get(base_url + "/books/73")
    print("Before:   ", response.json())

    # Boş gövde: hiçbir alan gönderilmedi.
    response = httpx.patch(base_url + "/books/73", json={})
    print("Empty:    ", response.json())

    # Yalnızca available gönderildi; rating gönderilmedi.
    response = httpx.patch(base_url + "/books/73", json={"available": False})
    print("Available:", response.json())

    # rating gönderildi, değeri None (JSON'da null).
    response = httpx.patch(base_url + "/books/73", json={"rating": None})
    print("Rating:   ", response.json())
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Before:    {'title': 'Python ile Web API', 'author': {'first_name': 'Can', 'last_name': 'Demir'}, 'available': True, 'tags': ['python', 'api'], 'rating': 4.5, 'id': 73}
Empty:     {'title': 'Python ile Web API', 'author': {'first_name': 'Can', 'last_name': 'Demir'}, 'available': True, 'tags': ['python', 'api'], 'rating': 4.5, 'id': 73}
Available: {'title': 'Python ile Web API', 'author': {'first_name': 'Can', 'last_name': 'Demir'}, 'available': False, 'tags': ['python', 'api'], 'rating': 4.5, 'id': 73}
Rating:    {'title': 'Python ile Web API', 'author': {'first_name': 'Can', 'last_name': 'Demir'}, 'available': False, 'tags': ['python', 'api'], 'rating': None, 'id': 73}
```

| Gövde | `changes` sözlüğü | Kitapta ne değişti? |
|---|---|---|
| `{}` | `{}` | Hiçbir şey. Gönderilen alan yok. |
| `{"available": false}` | `{'available': False}` | Yalnızca `available`. Puan `4.5` olarak kaldı. |
| `{"rating": null}` | `{'rating': None}` | Yalnızca `rating`: Puan silindi, `None` oldu. |

Yani istemci için kural şu:

- Bir alana **dokunmak istemiyorsan**, o alanı gövdeye hiç yazma.
- Bir alanın değerini **silmek istiyorsan**, o alanı `null` değeriyle gönder.

---

## 2. `exclude_unset=True` yazılmasaydı

`update_book` fonksiyonunda o satırı şöyle değiştirdiğimizi düşünelim:

```python
changes = book_data.model_dump()
```

Föyün **Deney 3 sonundaki** sunucuda, yani yanıt modeli eklenmeden önce, bu değişiklikle aynı isteği gönderdik:

```bash
curl -X PATCH http://127.0.0.1:8000/books/42 -H "Content-Type: application/json" -d '{"available": false}'
```

```text
{"id":42,"title":null,"author":null,"available":false,"tags":null,"rating":null}
```

Ne oldu, adım adım:

1. Gövdede yalnızca `available` vardı.
2. `model_dump()` modeldeki bütün alanları sözlüğe koydu: `available` için `False`, gönderilmeyen öteki alanlar için varsayılan değerleri, yani `None`.
3. `book.update(changes)` bu sözlükteki **her** alanı kitabın üzerine yazdı.
4. Kitabın adı, yazarı ve etiketleri `None` oldu. Yalnızca ödünç durumunu değiştirmek istiyorduk; kitabın bilgilerinin çoğunu sildik.

Aynı denemeyi **Deney 4 sonundaki** sunucuda, yani yanıt modeliyle yaparsan, bu kez yanıt `500` olur. Nedeni 3. bölümde.

---

## 3. Zorunlu bir alana `null` göndermek

Sunucumuzda kitabı iki ayrı model denetliyor:

| Model | Ne zaman devreye giriyor? | `title` alanı `None` olabilir mi? |
|---|---|---|
| `BookUpdate` | İstek gelince, gövdeyi kontrol ederken (Deney 3) | **Evet.** PATCH'te her alan isteğe bağlı olsun diye `None` olabiliyor. |
| `Book` | Yanıt hazırlanırken; dekoratördeki `response_model=Book` (Deney 4) | **Hayır.** Yanıttaki kitabın adı bir metin (`str`) olmak zorunda. |

İki model `title` konusunda farklı şey söylüyor. İstemci `{"title": null}` gönderince bu fark sorun çıkarıyor. Deney 4 sonundaki sunucuda denedik:

```bash
curl -i -X PATCH http://127.0.0.1:8000/books/42 -H "Content-Type: application/json" -d '{"title": null}'
```

```text
HTTP/1.1 500 Internal Server Error
...
Internal Server Error
```

Sunucuda sırasıyla şunlar oldu:

1. **İstek kabul edildi.** `BookUpdate` modeli `{"title": null}` gövdesine izin verdi.
2. **Kitap değişti.** `changes` sözlüğü `{'title': None}` oldu; `book.update(changes)` listedeki kitabın adını `None` yaptı.
3. **Yanıt hazırlanamadı.** FastAPI, değişen kitabı `Book` modeline göre yanıta koymak istedi. `title` alanında metin yerine `None` buldu ve yanıtı hazırlayamadı.
4. **İstemciye `500` gitti.** **500 Internal Server Error**, "sunucuda bir hata oldu" demektir.

Burada iki sorun var:

- **İstemci yanlış bilgilendirildi.** Yanıt "hata oldu" diyor, ama kitap aslında değişti. İstemci isteğinin işe yarayıp yaramadığını yanıttan anlayamıyor.
- **Kitap bozuk kaldı.** Adı artık `None` olduğu için bundan sonra bu kitabı döndüren her istek de `500` alıyor; örneğin `GET /books/42`.

Asıl hata, sunucunun `null` değerli bir `title` alanını baştan kabul etmesi. Doğrusu, böyle bir isteği **kitaba dokunmadan önce** `422` ile reddetmek: "`title` gönderilmeyebilir, ama gönderilirse `null` olamaz." Modellere bu tür kurallar yazmayı, yani alanların kabul edeceği değerleri, 5. haftada göreceğiz.

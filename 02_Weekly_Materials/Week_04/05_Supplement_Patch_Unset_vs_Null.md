# Ek Not — PATCH'te Gönderilmeyen Alan ile `null` Gönderilen Alan

Föyün Deney 3'ündeki `update_book` fonksiyonu kitabı şu iki satırla değiştiriyor:

```python
changes = book_data.model_dump(exclude_unset=True)
book.update(changes)
```

Bu notta üç soruyu cevaplıyoruz:

1. `exclude_unset=True` tam olarak ne yapıyor?
2. Bir alanı **hiç göndermemek** ile **`null` göndermek** arasında ne fark var?
3. Bu satır yanlış yazılırsa ya da istemci beklenmedik bir değer gönderirse ne olur?

---

## 1. `exclude_unset=True` ne yapıyor?

Bunu görmek için sunucuya gerek yok; modeli doğrudan Python'da oluşturabiliriz. Proje klasöründe `model_dump_demo.py` adlı ayrı bir dosya oluştur:

```python
from pydantic import BaseModel


class Author(BaseModel):
    first_name: str
    last_name: str


class BookUpdate(BaseModel):
    title: str | None = None
    author: Author | None = None
    available: bool | None = None
    tags: list[str] | None = None
    rating: float | None = None


# Gövde {"available": false} gibi: yalnızca available gönderildi.
only_available = BookUpdate(available=False)

# Gövde {"rating": null} gibi: rating gönderildi, değeri null.
rating_null = BookUpdate(rating=None)

print("only_available, model_dump():")
print(only_available.model_dump())
print("only_available, model_dump(exclude_unset=True):")
print(only_available.model_dump(exclude_unset=True))
print("rating_null, model_dump(exclude_unset=True):")
print(rating_null.model_dump(exclude_unset=True))
```

`BookUpdate(available=False)` yazmak, FastAPI'nin `{"available": false}` gövdesinden oluşturduğu modelin aynısını oluşturur. Föyde bu işi FastAPI yapıyordu; burada kendimiz yapıyoruz.

Dosyayı çalıştır:

```bash
python model_dump_demo.py
```

```text
only_available, model_dump():
{'title': None, 'author': None, 'available': False, 'tags': None, 'rating': None}
only_available, model_dump(exclude_unset=True):
{'available': False}
rating_null, model_dump(exclude_unset=True):
{'rating': None}
```

| Çıktı | Ne gösteriyor? |
|---|---|
| `model_dump()` | Modeldeki **bütün** alanları sözlüğe koyar. Gönderilmeyen alanlar da varsayılan değerleriyle, yani `None` olarak gelir. |
| `model_dump(exclude_unset=True)` | Yalnızca **gönderilen** alanları sözlüğe koyar. Yalnızca `available` gönderildiği için sözlükte yalnızca o var. |
| `rating_null` ile `exclude_unset=True` | `rating` gönderildi, değeri `None`. Gönderildiği için sözlüğe girdi. |

Buradaki önemli nokta şu: `only_available` modelinde de `rating` alanının değeri `None`; `rating_null` modelinde de. Değerleri aynı. Ama Pydantic, alanın gönderilip gönderilmediğini ayrıca hatırlıyor. `exclude_unset=True` da bu bilgiye bakıyor:

| | `rating` alanının değeri | `rating` gönderildi mi? | `exclude_unset=True` sözlüğünde `rating` var mı? |
|---|---|---|---|
| `{"available": false}` | `None` | Hayır | Yok |
| `{"rating": null}` | `None` | Evet | Var: `'rating': None` |

---

## 2. Sunucuda ne oluyor?

Aynı farkı şimdi sunucuda görelim. Föyün Deney 4 sonundaki sunucuyu kullanıyoruz. 73 numaralı kitabın başlangıçtaki puanı `4.5`.

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

## 3. `exclude_unset=True` yazılmasaydı

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
2. `model_dump()` bütün alanları sözlüğe koydu: `available` için `False`, gönderilmeyen öteki alanlar için `None` (1. bölümdeki ilk çıktı).
3. `book.update(changes)` bu sözlükteki **her** alanı kitabın üzerine yazdı.
4. Kitabın adı, yazarı ve etiketleri `None` oldu. Yalnızca ödünç durumunu değiştirmek istiyorduk; kitabın bilgilerinin çoğunu sildik.

Aynı denemeyi **Deney 4 sonundaki** sunucuda, yani yanıt modeliyle yaparsan, bu kez yanıt `500` olur. Nedeni 4. bölümde.

---

## 4. Zorunlu bir alana `null` göndermek

`BookUpdate` modelinde bütün alanlar `None` olabilir. Bu yüzden istemci `{"title": null}` da gönderebilir; model bunu kabul eder. Deney 4 sonundaki sunucuda denedik:

```bash
curl -i -X PATCH http://127.0.0.1:8000/books/42 -H "Content-Type: application/json" -d '{"title": null}'
```

```text
HTTP/1.1 500 Internal Server Error
...
Internal Server Error
```

Ne oldu, adım adım:

1. `BookUpdate` modeli `{"title": null}` gövdesini kabul etti, çünkü modelde `title` alanı `None` olabiliyor.
2. `exclude_unset=True` sözlüğü `{'title': None}` oldu; `book.update` kitabın adını `None` yaptı.
3. FastAPI yanıtı `Book` yanıt modeline göre hazırlamak istedi. Ama `Book` modelinde `title` bir metin (`str`) olmak zorunda.
4. Yanıt hazırlanamadı ve sunucu `500` döndürdü.

Kitap da bozuk kaldı: Adı artık `None` olduğu için bundan sonra `GET /books/42` isteği de `500` alıyor.

**500 Internal Server Error**, "sunucuda bir hata oldu" demektir. Sorunun istemcide değil sunucuda olduğunu söyler. Burada asıl sorun, sunucunun `null` değerli bir `title` alanını baştan kabul etmesi.

Bunu önlemek için `BookUpdate` modelinde "`title` gönderilmeyebilir, ama gönderilirse `null` olamaz" gibi kurallar yazmak gerekir. Böylece istek daha kitaba dokunmadan `422` ile reddedilir. Alanların kabul edeceği değerleri 5. haftada göreceğiz.

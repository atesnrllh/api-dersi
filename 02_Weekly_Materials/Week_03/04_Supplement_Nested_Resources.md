# Ek Not — İç İçe Kaynak mı, Ayrı Koleksiyon mu?

Föyün Deney 5'inde yorumları kitabın yolunun altına koyduk: `/books/42/reviews`. Bu bir zorunluluk değil, bir tasarım tercihidir. Bu notta yorumları **ayrı bir koleksiyon** olarak tasarlamanın nasıl olacağını ve iki tasarımın ne zaman tercih edildiğini görüyoruz.

---

## 1. İki tasarım

| İstenen | İç içe kaynak (föydeki tasarım) | Ayrı koleksiyon |
|---|---|---|
| 42 numaralı kitabın yorumları | `GET /books/42/reviews` | `GET /reviews?book_id=42` |
| 42 numaralı kitaba yorum eklemek | `POST /books/42/reviews` | `POST /reviews` (gövdede `book_id` ile) |
| Ece'nin bütün kitaplara yaptığı yorumlar | Tek istekle alınamaz | `GET /reviews?reader=Ece` |

İki tasarımda da yorumların hangi kitaba ait olduğu bellidir. Fark, bu bilginin **nerede** durduğudur:

- **İç içe kaynakta** kitabın kimliği yoldadır: `/books/42/reviews`.
- **Ayrı koleksiyonda** kitabın kimliği, Hafta 1'de gördüğümüz gibi bir sorgu parametresidir: `?book_id=42`.

---

## 2. Ayrı koleksiyonla yazılmış bir örnek

> **Not:** Bu örnek föydeki sunucudan ayrıdır. Föydeki dosyalarını bozmamak için örneği ayrı bir klasörde dene.

`server.py`:

```python
from fastapi import FastAPI

app = FastAPI()

reviews = [
    {"id": 1, "book_id": 42, "reader": "Ece", "score": 5},
    {"id": 2, "book_id": 57, "reader": "Ece", "score": 3},
    {"id": 3, "book_id": 42, "reader": "Can", "score": 4}
]


@app.get("/reviews")
def get_reviews(book_id: int | None = None, reader: str | None = None):
    results = []

    for review in reviews:
        book_matches = book_id is None or review["book_id"] == book_id
        reader_matches = reader is None or review["reader"] == reader

        if book_matches and reader_matches:
            results.append(review)

    return results
```

Bu kod, Hafta 1'deki `get_books` fonksiyonuyla aynı kalıbı kullanıyor. İki sorgu parametresi var, ikisi de isteğe bağlı. Bir sorgu parametresi gönderilmezse fonksiyondaki karşılığının değeri `None` olur ve o koşul filtrelemede yok sayılır.

Sunucuyu başlat ve üç isteği gönder:

```bash
curl "http://127.0.0.1:8000/reviews?book_id=42"
```

```text
[{"id":1,"book_id":42,"reader":"Ece","score":5},{"id":3,"book_id":42,"reader":"Can","score":4}]
```

```bash
curl "http://127.0.0.1:8000/reviews?reader=Ece"
```

```text
[{"id":1,"book_id":42,"reader":"Ece","score":5},{"id":2,"book_id":57,"reader":"Ece","score":3}]
```

```bash
curl http://127.0.0.1:8000/reviews
```

```text
[{"id":1,"book_id":42,"reader":"Ece","score":5},{"id":2,"book_id":57,"reader":"Ece","score":3},{"id":3,"book_id":42,"reader":"Can","score":4}]
```

İkinci istek, iç içe tasarımda tek istekle yapılamayan işi yaptı: Ece'nin iki farklı kitaba yaptığı yorumları birlikte getirdi.

---

## 3. Hangisi ne zaman tercih edilir?

| Tasarım | Ne zaman uygun? |
|---|---|
| İç içe kaynak: `/books/42/reviews` | Yorumlara hemen her zaman bir kitap **üzerinden** ulaşılıyorsa. Yol, ilişkiyi açıkça gösterir: "Bu kitabın yorumları." |
| Ayrı koleksiyon: `/reviews?book_id=42` | Yorumları kitaptan bağımsız olarak da aramak gerekiyorsa. Örneğin bir okuyucunun bütün yorumları ya da en son yazılan yorumlar. |

İki tasarım birlikte de kullanılabilir. Bir API, hem `/books/42/reviews` hem de `/reviews?reader=Ece` yollarını sunabilir.

Bir uyarı: İç içe yollar derinleştikçe kullanımı zorlaşır. Örneğin bir yorumun yanıtlarını `/books/42/reviews/1/replies` gibi bir yolla sunmak mümkündür, ama yol uzadıkça istemcinin her seferinde bütün kimlikleri bilmesi gerekir. Bu yüzden iç içe yollar genellikle bir iki seviyeyle sınırlı tutulur.

---

## 4. Föyde neden iç içe kaynağı seçtik?

Kitap kataloğumuzda yorumlara her zaman bir kitabın sayfasından bakılıyor; bir okuyucunun bütün yorumlarını listelemek gibi bir ihtiyacımız yok. Bu yüzden `/books/42/reviews` yolu ilişkiyi daha açık gösteriyor. Ayrıca bu tasarım, yoldan alınan bir parametre ile gövdeden alınan bir modeli aynı fonksiyonda kullanmayı görmemizi sağladı.

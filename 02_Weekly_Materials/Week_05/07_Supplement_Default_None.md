# Ek Not — `title: str = None` Yazımının Bedeli

Föyün Deney 4'ünde `BookUpdate` modelinin alanlarını `title: str = Field(default=None, min_length=1)` ve `author: Author = None` gibi yazdık. Böylece alan gönderilmeyebiliyor, ama `null` gönderilemiyor. Bu notta bu kısayolun bir bedelini görüyoruz: Alan gönderilmediğinde değeri, türüyle uyuşmuyor.

---

## 1. Gönderilmeyen alanın değeri

FastAPI istek gövdesini modele çevirirken ne yapıyorsa, biz de burada elle yapıyoruz. Aşağıdaki kodu ayrı bir dosyaya, örneğin `default_none.py` dosyasına yaz ve çalıştır:

```python
from pydantic import BaseModel, ConfigDict, Field


class BookUpdate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    title: str = Field(default=None, min_length=1)
    available: bool = None


# İstemci yalnızca available gönderdi: {"available": false}
book_data = BookUpdate(available=False)

print("title:", repr(book_data.title))
print("model_dump():", book_data.model_dump())
print("model_dump(exclude_unset=True):", book_data.model_dump(exclude_unset=True))
```

Model kısaltıldı; yalnızca iki alanı var.

```text
title: None
model_dump(): {'title': None, 'available': False}
model_dump(exclude_unset=True): {'available': False}
```

| Satır | Ne görüyoruz? |
|---|---|
| `title: None` | Tür `str` diyor, ama değer `None`. Pydantic varsayılan değeri kontrol etmediği için bu değer modelde kaldı. |
| `model_dump()` | Gönderilmeyen `title` da sözlükte, değeri `None`. |
| `model_dump(exclude_unset=True)` | Yalnızca istemcinin gönderdiği alan var. |

---

## 2. Neden sorun çıkmıyor?

Bizim `update_book` fonksiyonumuz kitabı `model_dump(exclude_unset=True)` ile değiştiriyor (Hafta 4, Deney 3). Gönderilmeyen alanlar `changes` sözlüğüne hiç girmediği için `None` değerleri kitaba yazılmıyor.

`exclude_unset=True` olmasaydı `book.update(changes)` satırı kitabın adını `None` yapardı ve kitap bozulurdu. Yani bu kısayol, ancak yalnızca gönderilen alanları kullanan bir fonksiyonla birlikte güvenli.

---

## 3. Editör uyarısı

Bazı editörler, tür denetimi açıksa `author: Author = None` gibi satırların altını çizer. Uyarı kabaca şunu söyler: "`None`, `Author` türünde bir değer değil." Uyarı haklı: Yukarıda gördüğümüz gibi, alan gönderilmezse değer gerçekten `None` oluyor. Ama kod doğru çalışır; uyarı yalnızca tür bilgisiyle değerin uyuşmadığını söylüyor.

`title` satırında uyarı çıkmayabilir, çünkü değeri `Field(...)` veriyor ve editör bu değeri `str` türüyle karşılaştıramıyor. Satır yine aynı kısayolu kullanıyor.

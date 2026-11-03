# Ek Not — `Path` Kuralının Başka Bir Yazımı: `Annotated`

Föyün Deney 5'inde yol parametresine kuralı `book_id: int = Path(gt=0)` diye yazdık. FastAPI'nin [belgelerinde](https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/) aynı kural başka bir yazımla görünür. Bu notta o yazımı görüyoruz.

---

## 1. İki yazım yan yana

| Föydeki yazım | FastAPI belgelerindeki yazım |
|---|---|
| `def get_book(book_id: int = Path(gt=0)):` | `def get_book(book_id: Annotated[int, Path(gt=0)]):` |
| `def update_book(book_data: BookUpdate, book_id: int = Path(gt=0)):` | `def update_book(book_id: Annotated[int, Path(gt=0)], book_data: BookUpdate):` |

`Annotated[int, Path(gt=0)]` şunu söyler: "Bu parametrenin türü `int`; ayrıca şu kural da var: `Path(gt=0)`." Tür ve kural köşeli parantezin içinde birlikte yazılır.

`Annotated`, Python'un `typing` modülünden gelir; dosyanın başına şu satır eklenir:

```python
from typing import Annotated
```

---

## 2. Ne değişir?

Sunucunun bütün `book_id` parametrelerini `Annotated` ile yazıp föyün istekleri yeniden gönderdik. Bütün yanıtlar aynı çıktı: `/books/-5` adresi her işlemde yine `422` aldı.

Tek fark parametrelerin sırasında. Föydeki yazımda `= Path(gt=0)` bir varsayılan değer gibi yazılıyor; Python'da varsayılan değeri olan parametreler sona gelmek zorunda olduğu için `book_id` parametresini sona taşıdık. `Annotated` yazımında varsayılan değer yok, bu yüzden `book_id` yerinde kalabilir.

---

## 3. Hangisini kullanmalı?

İki yazım aynı işi yapar. Föyde, `Field` ile aynı görünen ilk yazımı kullanıyoruz. Belgelerde ya da başka projelerde `Annotated` gördüğünde aynı kuralın yazıldığını bilmen yeterli.

`Annotated`, modellerin alanlarında da kullanılabilir. 8.4 alıştırmasının [cevap notunda](10_Supplement_Exercise_8_4_Answer.md), listedeki her etikete kural yazmak için bu yazımı görebilirsin.

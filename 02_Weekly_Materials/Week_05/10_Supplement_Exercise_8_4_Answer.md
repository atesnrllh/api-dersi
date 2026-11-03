# Ek Not — 8.4'ün Cevabı: Üst Sınırlar

Bu not, föyün 8.4 bölümündeki alıştırmanın cevabıdır. Önce kodunu kendin yaz ve dene, sonra buradaki cevapla karşılaştır.

---

## 1. Kod

`server.py` dosyasında `BookCreate` ve `BookUpdate` modellerinin `title` ve `tags` satırlarını şöyle değiştir:

```python
class BookCreate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    title: str = Field(min_length=1, max_length=100)
    author: Author
    available: bool
    tags: list[str] = Field(max_length=5)
    rating: float | None = Field(default=None, ge=0, le=5)

...

class BookUpdate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    title: str = Field(default=None, min_length=1, max_length=100)
    author: Author = None
    available: bool = None
    tags: list[str] = Field(default=None, max_length=5)
    rating: float | None = Field(default=None, ge=0, le=5)
```

| Yazım | Anlamı |
|---|---|
| `Field(min_length=1, max_length=100)` | Metin en az 1, en fazla 100 karakter olmalı. Bir alana birden fazla kural yazılabilir. |
| `tags: list[str] = Field(max_length=5)` | Liste en fazla 5 öğe içermeli. `max_length` metinde karakter sayısını, listede öğe sayısını sınırlar. |
| `Field(default=None, max_length=5)` | `BookUpdate` modelinde aynı kural; alan gönderilmeyebilir. |

---

## 2. Sonuçlar

Sunucuyu yeniden başlatıp istekleri gönderdik:

| İstek | Durum kodu | `loc` | `msg` |
|---|---|---|---|
| `POST /books`, 101 karakterlik bir ad | `422` | `['body', 'title']` | `String should have at most 100 characters` |
| `POST /books`, 6 etiket | `422` | `['body', 'tags']` | `List should have at most 5 items after validation, not 6` |
| `POST /books`, 100 karakterlik bir ad ve 5 etiket | `201` | Yok | Yok |
| `PATCH /books/42`, 6 etiket | `422` | `['body', 'tags']` | `List should have at most 5 items after validation, not 6` |
| `GET /books` | `200` | Yok | Yok |

Sınırın kendisi kabul ediliyor: 100 karakterlik ad ve 5 etiket geçti. `max_length`, `le` gibi "küçük ya da eşit" demektir.

---

## 3. Sunucudaki kitaplar kurallara uyuyor mu?

İpucundaki soru önemliydi. Kurallar `BookCreate` modelinden `BookPublic` modeline de geçiyor ([kuralların yanıt modeline geçtiği ek not](05_Supplement_Inherited_Rules.md)). Sunucudaki üç kitabın adları 100 karakterden kısa, etiketleri de en fazla 2 tane; bu yüzden `GET /books` isteği `200` almaya devam etti. Sınırları daha dar seçseydik, örneğin en fazla 1 etiket, 42 ve 73 numaralı kitaplar okunamazdı ve yanıt `500` olurdu.

---

## 4. Bir adım ötesi: boş etiket

`tags` listesi artık en fazla 5 öğe alıyor, ama `["", ""]` gibi boş etiketler hâlâ kabul ediliyor. `max_length=5` listenin kendisine bakar; listenin içindeki metinlere bakmaz. Her etikete ayrı bir kural yazmak için Pydantic'in `Annotated` yazımı gerekir:

```python
from typing import Annotated

    tags: list[Annotated[str, Field(min_length=1)]] = Field(max_length=5)
```

Burada `Annotated[str, Field(min_length=1)]` "boş olmayan bir metin" demek; liste bu metinlerden oluşuyor. Bu yazımı ders kapsamında kullanmıyoruz; `Annotated` yazımını [ek notta](08_Supplement_Annotated.md) görmüştük.

# Ek Not — Kurallar Yanıt Modeline de Geçer

Föyün Deney 2'sinde kitap puanının kuralını `Field(default=None, ge=0, le=5)` olarak yazdık; alt sınır `0`. Puanlar genellikle 1 ile 5 arasında verilir; peki alt sınırı neden `1` yapmadık? Bu notta `ge=1` yazınca ne olduğunu deniyoruz.

---

## 1. Alt sınırı 1 yapmak

Föyün 7. bölümündeki son sunucuda `BookCreate` modelinin `rating` satırını şöyle değiştirdik:

```python
    rating: float | None = Field(default=None, ge=1, le=5)
```

Sunucuyu yeniden başlatıp kitapları okuduk:

| İstek | Yanıt |
|---|---|
| `GET /books/42` | `200` |
| `GET /books/57` | `500 Internal Server Error` |
| `GET /books` | `500 Internal Server Error` |

Sunucunun terminalinde nedeni görünüyor:

```text
fastapi.exceptions.ResponseValidationError: 1 validation error:
  {'type': 'greater_than_equal', 'loc': ('response', 'rating'), 'msg': 'Input should be greater than or equal to 1', 'input': 0, 'ctx': {'ge': 1.0}}
```

---

## 2. Ne oldu?

1. `BookPublic` modeli `BookCreate` modelinden türüyor (Hafta 4, Deney 4). Alanlarla birlikte alanların kurallarını da alıyor; yani `BookPublic` modelinde de `ge=1` var.
2. 57 numaralı kitabın puanı sunucu başlarken `0`. Bu değer, kural yazılmadan önce kaydedilmiş bir veri.
3. `GET /books/57` isteğinde FastAPI kitabı `BookPublic` modeline göre hazırlamak istedi. `0`, `ge=1` kuralına uymadı; yanıt hazırlanamadı ve istemciye `500` gitti.
4. `GET /books` isteği de `500` aldı, çünkü listede 57 numaralı kitap da var. **Tek bir kitap, bütün listeyi okunamaz hâle getirdi.**

Yeni kural, istemciden gelecek verileri korumak için yazılmıştı; ama sunucuda zaten duran eski veriye de uygulandı.

---

## 3. Çözüm seçenekleri

| Seçenek | Ne yapılır? | Sonucu |
|---|---|---|
| 1. Kuralı veriye uydurmak | Alt sınır `0` olur (föyde seçtiğimiz). | Eski veri geçerli kalır; `0` puan da kabul edilir. |
| 2. Veriyi kurala uydurmak | 57 numaralı kitabın puanı değiştirilir; örneğin `None` yapılır. | Kural `ge=1` olarak kalabilir. |
| 3. Kuralları yalnızca istek modeline yazmak | `BookPublic` modeli `BookCreate` modelinden türetilmez; alanları ayrıca yazılır. | Yanıt modeli eski veriyi kabul eder, ama alanlar iki yerde yazılır. |

2. seçeneği de denedik. `ge=1` kuralıyla `PATCH /books/57` isteğiyle `{"rating": 3}` gönderince yanıt `200` oldu; ardından `GET /books` isteği yeniden `200` aldı. Ama sunucuyu her yeniden başlattığımızda `books` listesi dosyadaki hâline döndüğü için 57 numaralı kitabın puanı yine `0` olur. Bu yüzden föyde 1. seçeneği kullandık.

---

## 4. Akılda tutulacak kural

Bir modele yeni bir kural eklemeden önce iki soruyu sor:

1. Bu model başka bir modelin, özellikle yanıt modelinin, atası mı?
2. Sunucuda bu kurala uymayan bir veri var mı?

İkisinin de cevabı "evet" ise, kural yalnızca yeni istekleri değil, eski verinin okunmasını da etkiler. 6. haftada verileri veritabanında saklamaya başladığımızda bu soru daha da önemli olacak: Veritabanındaki kayıtlar, sunucu yeniden başlayınca dosyadaki hâline dönmez.

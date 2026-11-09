# Ek Not — Yazarı ve Etiketleri Nasıl Saklamalı?

Föyün Deney 1'inde `Book` tablosunun `author` ve `tags` sütunlarını `JSONB` türünde tanımladık. Bu notta neden böyle yaptığımızı ve başka hangi seçeneklerin olduğunu görüyoruz.

---

## 1. Sorun: Bir hücreye tek değer

Tablonun her hücresine tek bir değer yazılır: bir metin, bir sayı, `true` ya da `false`. Bizim kitaplarımızda ise iki alan tek değer değil:

- `author` iki alanlı bir nesne: `{"first_name": "Deniz", "last_name": "Kaya"}`
- `tags` bir liste: `["software", "education"]`

Bunları tabloya yerleştirmenin üç yaygın yolu var.

---

## 2. Üç seçenek

| Seçenek | Tablolar | Artısı | Eksisi |
|---|---|---|---|
| 1. `JSONB` sütunu (föydeki yol) | `book` tablosunda `author` ve `tags` sütunları; değerleri JSON olarak saklanır. | API'deki kitapla tablodaki kayıt aynı biçimde. `model_dump()` ile gelen sözlük doğrudan tabloya yazılabiliyor. | Bir yazarın bütün kitaplarını bulmak ya da bir yazarın adını tek yerden düzeltmek zorlaşır: Yazar her kitabın içinde ayrı ayrı yazılıdır. |
| 2. Ayrı sütunlar | `book` tablosunda `author_first_name` ve `author_last_name` sütunları | Her değer kendi sütununda; yazarın adına göre arama kolay. | API iç içe bir `author` nesnesi beklediği için her fonksiyonda nesneyi iki sütuna ayırıp yeniden birleştiren kod gerekir. Etiket listesi bu yolla saklanamaz. |
| 3. Ayrı tablolar | `author` tablosu ve `book` tablosunda ona bağlı bir `author_id` sütunu; etiketler için `tag` tablosu ve kitapla etiketi eşleştiren üçüncü bir tablo | Bir yazar bir kez yazılır, birçok kitaba bağlanır. Veritabanları tam da bu tür ilişkiler için tasarlanmıştır. | Tablo ve kod sayısı artar; bir kitabı okumak için birkaç tabloyu birleştirmek gerekir. |

Föyde 1. seçeneği kullandık, çünkü bu haftanın konusu verinin kalıcı saklanması; API'nin dışı da hiç değişmeden kaldı. Ayrı tablolar ve aralarındaki ilişkiler için Deney 5'teki `review` tablosu ilk örneğimiz: Her yorum `book_id` sütunuyla bir kitaba bağlı. Gerçek bir kütüphane sisteminde yazarlar da büyük olasılıkla kendi tablolarında durur.

---

## 3. psql'de yazarın görünüşü

Yazarları psql ile okuyunca anahtarların sırası farklı görünür:

```bash
docker exec book-db psql -U student -d catalog -c "SELECT id, author FROM book;"
```

```text
 id |                    author
----+----------------------------------------------
 42 | {"last_name": "Kaya", "first_name": "Deniz"}
 57 | {"last_name": "Yılmaz", "first_name": "Ece"}
 73 | {"last_name": "Demir", "first_name": "Can"}
(3 rows)
```

`JSONB`, JSON'u PostgreSQL'in kendi biçimine çevirerek saklar ve anahtarları kendi düzenine göre sıralar. JSON'da bir nesnenin anahtarlarının sırası anlam taşımaz; değerler aynı. API yanıtında ise `first_name` yine önce gelir, çünkü yanıtı `Author` modeli hazırlıyor ve alanların sırasını model belirliyor.

PostgreSQL'de bir de `JSON` türü vardır; o, metni olduğu gibi saklar. `JSONB` içinde arama yapmak daha hızlı olduğu için genellikle o tercih edilir.

---

## 4. Listeyi yerinde değiştirmek

Bir kitaba etiket eklemek için akla ilk gelen yol, listeye `append` ile bir öğe eklemek olabilir. Bunu küçük bir programla denedik:

```python
from sqlmodel import Session

from database import Book, engine

with Session(engine) as session:
    book = session.get(Book, 42)
    book.tags.append("new")
    session.commit()

with Session(engine) as session:
    print("After append:  ", session.get(Book, 42).tags)

with Session(engine) as session:
    book = session.get(Book, 42)
    book.tags = book.tags + ["new"]
    session.commit()

with Session(engine) as session:
    print("After new list:", session.get(Book, 42).tags)
```

```text
After append:   ['software', 'education']
After new list: ['software', 'education', 'new']
```

`append` satırından sonra `commit` çalıştı, ama etiket veritabanına yazılmadı. Oturum, bir alana yeni bir değer verildiğinde değişikliği fark eder; var olan listenin içi değiştiğinde ise fark etmez. Yeni bir liste verince (`book.tags = book.tags + ["new"]`) değişiklik yazıldı.

Föyde bu sorun çıkmıyor, çünkü `sqlmodel_update` her alana istemciden gelen yeni değeri veriyor. Kendi kodunda `JSONB` sütunundaki bir listeyi ya da sözlüğü değiştireceksen ona yeni bir değer ver.

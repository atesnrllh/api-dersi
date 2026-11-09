# Ek Not — 8.3 Alıştırmasının Cevabı: Sayfa Sayısı

Bu not, föydeki 8.3 alıştırmasının bir cevabını veriyor. Kendi kodunu yazıp denedikten sonra karşılaştır.

---

## 1. Üç model

**`database.py` dosyasında `Book` tablo modeli:** Tabloda yeni bir sütun.

```python
    rating: float | None = None
    pages: int | None = None
    internal_note: str | None = None
```

**`server.py` dosyasında `BookCreate` ve `BookUpdate` modelleri:** İki modele de aynı satır, `rating` satırının altına.

```python
    rating: float | None = Field(default=None, ge=0, le=5)
    pages: int | None = Field(default=None, ge=1)
```

| Kod | Ne yapar? |
|---|---|
| `pages: int \| None = None` (`Book`) | Tabloda boş bırakılabilen bir tam sayı sütunu. Başlangıçtaki üç kitabın sayfa sayısı bilinmiyor; sütunları boş kalır. |
| `pages: int \| None = Field(default=None, ge=1)` (`BookCreate`) | Gönderilmezse `None`; gönderilirse en az 1. `None` burada anlamlı bir değer: "sayfa sayısı bilinmiyor" (Hafta 5, Deney 4'teki `rating` gibi). |
| Aynı satır (`BookUpdate`) | `PATCH` isteğinde de aynı kural. |

`BookPublic` modeline bir şey yazmaya gerek yok: `BookCreate` modelinden türediği için `pages` alanı yanıtlarda da görünür. `reset_db.py` dosyası da değişmiyor; başlangıçtaki kitaplara sayfa sayısı yazmadık.

---

## 2. Sunucu neden `500` aldı?

Modelleri değiştirip sunucuyu yeniden başlattıktan sonra ilk istek (`GET /books/42`) `500` aldı. Sunucunun terminalinde hatanın son satırlarından biri şuydu:

```text
psycopg.errors.UndefinedColumn: column book.pages does not exist
```

*Undefined column*, "tanımlanmamış sütun" demek. `Book` sınıfına `pages` alanını ekledik, ama veritabanındaki `book` tablosu Deney 1'de `create_all` ile oluşturulmuştu ve o zaman bu sütun yoktu. SQLModel her okumada `pages` sütununu istedi; veritabanı böyle bir sütun bulamadı.

Python sınıfını değiştirmek tabloyu değiştirmez. `create_all` de yalnızca **olmayan** tabloları oluşturur; var olan bir tabloya sütun eklemez. Bu yüzden `python reset_db.py` komutunu çalıştırdık: Tablolar silindi ve yeni `Book` sınıfına göre, `pages` sütunuyla yeniden oluşturuldu.

Bu yol bizim deneme veritabanımızda işe yarıyor, çünkü `reset_db.py` bütün kayıtları silip başlangıçtaki kitapları yeniden yazıyor. Gerçek bir uygulamada kayıtları silmek kabul edilemez. Orada tabloyu, içindeki kayıtları koruyarak değiştiren araçlar kullanılır; bu değişikliklere **taşıma (migration)** denir.

---

## 3. Sonuçlar

Veritabanı sıfırlandıktan ve sunucu yeniden başlatıldıktan sonra istekler sırayla gönderildi:

| İstek | Durum kodu | Yanıtta `pages` |
|---|---|---|
| `GET /books/42` | `200` | `None` |
| `POST /books`, `"pages": 320` | `201` | `320` |
| `POST /books`, `"pages": 0` | `422` | Yok; `loc`: `['body', 'pages']` |
| `PATCH /books/42`, `{"pages": 250}` | `200` | `250` |

Föydeki tabloda ilk satır `null` diyor; burada `None` görünüyor. İkisi aynı değer: JSON'daki `null`, Python'a `None` olarak gelir.

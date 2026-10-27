# Ek Not — Silinen Kitabın Yorumlarına Ne Olur?

Föyün Deney 1'inde yorumu olmayan 57 numaralı kitabı sildik. Bu notta yorumu olan 42 numaralı kitabı silip yorumlarına ne olduğuna bakıyoruz.

---

## 1. 42 numaralı kitabı silmek

Föyün Deney 4 sonundaki sunucuyu kullandık. Sunucuda Hafta 3'teki 8.3 alıştırmasının `get_review` fonksiyonu da vardı. Sunucuyu yeniden başlatıp istekleri sırayla gönderdik:

| İstek | Sonuç |
|---|---|
| `GET /books/42/reviews` | `200`: `[{"id":1,"book_id":42,"reader":"Ece",...}]` |
| `DELETE /books/42` | `204`: Kitap silindi. |
| `GET /books/42/reviews` | `404`: `{"detail":"Book not found"}` |
| `POST /books/42/reviews` | `404`: `{"detail":"Book not found"}` |
| `GET /books/42/reviews/1` | `200`: `{"id":1,"book_id":42,"reader":"Ece",...}` |

İlk üç sonuç beklediğimiz gibi: Kitap yok, yorumları listelenemiyor, yeni yorum da eklenemiyor.

Son satır ise bir sorun gösteriyor: Kitap silindi, ama 1 numaralı yorum hâlâ okunabiliyor. `delete_book` fonksiyonu yalnızca `books` listesinden kitabı çıkardı; `reviews` listesine hiç dokunmadı. Yorum, artık var olmayan bir kitaba ait olarak bellekte duruyor. `get_review` fonksiyonu da kitabın var olup olmadığını kontrol etmediği için yorumu döndürdü.

---

## 2. Üç seçenek

Bir kitap silinince yorumlarına ne olacağı bir **tasarım kararıdır**. Yaygın üç seçenek var:

| Seçenek | Kitap silinince | Ne zaman uygun? |
|---|---|---|
| 1. Yorumlara dokunmamak | Yorumlar kalır, ama kitabı olmadığı için anlamsızlaşır. Föydeki `delete_book` fonksiyonu şu an böyle çalışıyor. | Yorumların ayrıca saklanması gerekiyorsa; örneğin silinen kitapların yorumları sonra incelenecekse |
| 2. Yorumları da silmek | Kitapla birlikte yorumları da silinir. | Yorumlar kitap olmadan bir anlam taşımıyorsa |
| 3. Silmeyi reddetmek | Yorumu olan kitap silinemez; sunucu `409 Conflict` döndürür. Önce yorumların silinmesi gerekir. | Bir şeyin yanlışlıkla silinmesi büyük sorunsa |

`409` durum kodunu Hafta 2'nin [durum kodları notunda](../Week_02/07_Supplement_Status_Codes.md) "çakışma" olarak görmüştük.

Kitap kataloğu API'sinde 2. seçenek en mantıklısı: Kitabı olmayan bir yorumun okunmasının bir anlamı yok.

---

## 3. Veritabanında bu kural nasıl kurulur?

Şimdilik kitaplar ve yorumlar iki ayrı Python listesinde duruyor; aralarındaki ilişkiyi yalnızca `book_id` alanı kuruyor ve bu ilişkiyi korumak bize kalıyor. 6. haftada verileri veritabanında saklamaya başladığımızda, "bir kitap silinince yorumlarına ne olacak?" kuralını veritabanının kendisine tanımlayabileceğiz. Veritabanı bu kuralı her silmede kendisi uygular.

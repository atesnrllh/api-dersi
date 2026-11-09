# Ek Not — Kimlik Sayacı

Föyün Deney 1'inde `reset_db.py` dosyasına `setval` içeren bir satır yazdık ve "kimlik sayacını en büyük kimliğe getirir" dedik. Bu notta o satır olmasaydı ne olacağını ve sayacın Hafta 2'deki kimlik kuralımızdan nasıl ayrıldığını görüyoruz.

---

## 1. Sayaç nedir?

Föyün 1.3 bölümünde `\d book` çıktısında `id` sütununun varsayılan değeri şöyleydi:

```text
nextval('book_id_seq'::regclass)
```

`book_id_seq`, PostgreSQL'in bu tablo için tuttuğu bir **sayaçtır (sequence)**. Kimliği verilmeyen yeni bir kayıt eklendiğinde veritabanı `nextval` ile sayacı bir artırır ve çıkan sayıyı kimlik yapar.

Sayaç, tabloya bakmaz. Kimliği kendimiz yazdığımız kayıtlar (42, 57, 73) sayacı ilerletmez. Bu yüzden `reset_db.py` üç kitabı yazdıktan sonra sayaç hâlâ en baştadır.

---

## 2. `setval` satırı olmasaydı

`reset_db.py` dosyasından `setval` satırlarını silip veritabanını sıfırladık ve föyün sonundaki sunucuya yeni bir kitap gönderdik:

| İstek | Sonuç |
|---|---|
| `POST /books` | `201`, `Location: /books/1` |

Yeni kitabın kimliği `74` değil, `1` oldu. Bu bir hata vermedi, ama Hafta 2'den beri bildiğimiz "yeni kitap 74 olur" bilgisine uymuyor.

Asıl sorun daha sonra çıkar: Sayaç 41'e geldikten sonra eklenen kitap `42` kimliğini alır; ama 42 numaralı kitap zaten var. Bunu denemek için sayacı psql ile 41'e getirip bir kitap daha gönderdik:

| İstek | Sonuç |
|---|---|
| `POST /books` | `500 Internal Server Error` |

Sunucunun terminalinde şu satır vardı:

```text
psycopg.errors.UniqueViolation: duplicate key value violates unique constraint "book_pkey"
```

*Duplicate key*, "tekrarlanan anahtar" demek: Birincil anahtar her kayıtta farklı olmalı; veritabanı aynı kimlikle ikinci bir kaydı reddetti. `setval` satırı sayacı en büyük kimliğe getirerek bu çakışmayı baştan önlüyor.

---

## 3. Silinen kimlik tekrar kullanılmaz

Hafta 2'den beri sunucumuz yeni kimliği "en büyük kimlik + 1" kuralıyla buluyordu. Sayaç ise yalnızca ileri gider. Farkı görmek için iki sunucuya da aynı istekleri sırayla gönderdik:

| İstek | Hafta 5'in sonundaki sunucu | Bu haftanın sunucusu |
|---|---|---|
| `POST /books` | `201`, kimlik `74` | `201`, kimlik `74` |
| `DELETE /books/74` | `204` | `204` |
| `POST /books` | `201`, kimlik `74` | `201`, kimlik `75` |

Hafta 5'teki sunucu, silinen kitabın kimliğini yeni kitaba yeniden verdi. Veritabanı vermedi.

Kimliğin tekrar kullanılmaması bir güvencedir. Bir istemci silinen 74 numaralı kitabın adresini (`/books/74`) bir yerde saklamış olabilir. Kimlik yeniden kullanılırsa bu adres, istemcinin hiç bilmediği başka bir kitabı gösterir. Kimlik hiç tekrar kullanılmazsa eski adres yalnızca `404` alır.

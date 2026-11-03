# Ek Not — 8.3'ün Cevabı: Yazarın Adı Boş Olmasın

Bu not, föyün 8.3 bölümündeki alıştırmanın cevabıdır. Önce kodunu kendin yaz ve dene, sonra buradaki cevapla karşılaştır.

---

## 1. Kod

`server.py` dosyasında `Author` modelini şöyle değiştir:

```python
class Author(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
```

| Satır | Ne yapar? | Föydeki karşılığı |
|---|---|---|
| `model_config = ConfigDict(strict=True, extra="forbid")` | Yazar nesnesinde modelde olmayan alanları reddeder; değerlerin metin olarak gönderilmesini ister. | Deney 3 |
| `Field(min_length=1)` | Adın ve soyadın boş olmasını engeller. | Deney 2 |

`strict=True` bu alıştırmada istenmedi; öteki istek modelleriyle aynı davransın diye ekledik. Metin alanlarına sayı gönderilmesi zaten Pydantic'in varsayılan davranışında da reddediliyor ([tür dönüşümleri ek notu](03_Supplement_Lax_Type_Conversion.md)).

---

## 2. Sonuçlar

Sunucuyu yeniden başlatıp istekleri gönderdik:

| İstek | Durum kodu | `loc` |
|---|---|---|
| `POST /books`, yazar `{"first_name": "", "last_name": "Yıldız"}` | `422` | `['body', 'author', 'first_name']` |
| `POST /books`, yazar `{"first_name": "Ada", "last_name": "Yıldız", "middle_name": "Su"}` | `422` | `['body', 'author', 'middle_name']` |
| `POST /books`, yazar `{"first_name": "Ada", "last_name": "Yıldız"}` | `201` | Yok |
| `PATCH /books/42`, yazar `{"first_name": "", "last_name": "Kaya"}` | `422` | `['body', 'author', 'first_name']` |
| `GET /books` | `200` | Yok |

`loc` listesinde artık üç öğe var: Hata gövdede, `author` nesnesinin içindeki `first_name` alanında. Föyün Deney 6'sındaki `show_error` fonksiyonu bu hatayı `body -> ['author', 'first_name']` olarak gösterir.

`PATCH` isteği de reddedildi, çünkü `BookUpdate` modeli de yazar için aynı `Author` modelini kullanıyor. Kuralı tek bir yere yazdık; iki istek modeli de onu kullanıyor.

---

## 3. Son satır neden önemli?

`Author` modeli yalnızca isteklerde değil, yanıtlarda da kullanılıyor: `BookPublic` modelinin `author` alanı da bir `Author`. Yani `strict=True` ve `extra="forbid"` ayarları yanıttaki yazara da uygulanıyor. `BookPublic` modelindeki `strict=False, extra="ignore"` ayarı yalnızca kendi alanları için geçerli; içindeki `Author` modeli kendi ayarlarıyla kontrol ediliyor.

Föyün Deney 3'ünde `BookPublic` modelinde aynı ayar `500` hatasına yol açmıştı; çünkü sunucudaki 42 numaralı kitapta modelde olmayan `internal_note` alanı vardı. Burada sorun çıkmadı, çünkü sunucudaki yazarlarda yalnızca `first_name` ve `last_name` var. Yazarların sözlüğüne bir gün modelde olmayan bir alan eklenirse, aynı `500` hatası bu kez yazarlarda çıkar.

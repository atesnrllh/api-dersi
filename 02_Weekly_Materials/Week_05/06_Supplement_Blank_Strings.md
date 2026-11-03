# Ek Not — Yalnızca Boşluktan Oluşan Ad

Föyün Deney 2'sinde `Field(min_length=1)` kuralı boş adı (`""`) reddetti, ama `"   "` adı kabul edildi. Üç boşluk karakteri de bir metindir ve uzunluğu 3'tür; `min_length=1` kuralına uyar. Bu notta böyle adları da reddetmenin bir yolunu görüyoruz.

---

## 1. Boşlukları kırpmak

Pydantic, metinlerin başındaki ve sonundaki boşlukları kontrol etmeden önce **kırpabilir**. Bunun için modelin ayarına `str_strip_whitespace=True` eklenir. Föyün 7. bölümündeki son sunucuda `BookCreate` modelinin ayar satırını şöyle değiştirdik:

```python
class BookCreate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", str_strip_whitespace=True)
```

Sunucuyu yeniden başlatıp üç kitap gönderdik:

| Gönderilen `title` | Yanıt | Kaydedilen `title` |
|---|---|---|
| `"   "` | `422`: `String should have at least 1 character` | Yok |
| `"  Yeni Kitap  "` | `201` | `"Yeni Kitap"` |
| `""` | `422`: `String should have at least 1 character` | Yok |

İlk satırda üç boşluk kırpıldı, geriye `""` kaldı; `min_length=1` kuralı da onu reddetti.

---

## 2. Dikkat edilecek iki nokta

- **Kaydedilen değer değişir.** İkinci satırda istemci `"  Yeni Kitap  "` gönderdi, sunucu `"Yeni Kitap"` kaydetti. Çoğu zaman istenen budur; ama istemci gönderdiğinin aynen saklandığını varsayıyorsa şaşırabilir. Bu davranış API'nin belgesinde yazmalı.
- **Ayar modeldeki bütün metin alanlarına uygulanır.** `BookCreate` modelinde metin alanları `title` ve `tags` listesindeki etiketler. `" python "` etiketi de `"python"` olarak kaydedilir. `PATCH` isteklerinde de aynı davranışı istiyorsan ayarı `BookUpdate` modeline de eklemelisin.

`BookPublic` modeli bu ayarı da `BookCreate` modelinden alır (föyün Deney 3'ünde `extra` ayarında gördüğümüz gibi). Sunucudaki kitapların adlarında baştaki ya da sondaki boşluk olmadığı için yanıtlarda bir şey değişmez.

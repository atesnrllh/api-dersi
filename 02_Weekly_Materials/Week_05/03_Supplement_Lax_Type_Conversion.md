# Ek Not — Pydantic Hangi Değerleri Kendiliğinden Çevirir?

Föyün Deney 1'inde `"available": "yes"` gövdesi kabul edildi ve kitabın `available` alanı `True` oldu. Pydantic, varsayılan olarak bazı değerleri alanın türüne **çevirir (coerce)**; bu davranışa **gevşek mod (lax mode)** denir. Bu notta hangi değerlerin çevrildiğini ve Deney 3'teki `strict=True` ayarından sonra ne değiştiğini bir tabloda topluyoruz.

---

## 1. Deneme

Her satırda `POST /books` ya da `POST /books/42/reviews` isteğiyle tek bir alana farklı bir değer gönderdik. Sol sütundaki sonuçlar Hafta 4 sonundaki sunucudan, sağ sütundakiler föyün Deney 3 sonundaki sunucudan.

**Kitabın `available` alanı (`bool`):**

| Gönderilen | `strict=True` olmadan | `strict=True` ile |
|---|---|---|
| `true`, `false` | Kabul edilir. | Kabul edilir. |
| `"yes"`, `"true"`, `"on"`, `"1"` | `True` yapılır. | `422` |
| `"no"`, `"off"`, `"0"` | `False` yapılır. | `422` |
| `1` | `True` yapılır. | `422` |
| `0` | `False` yapılır. | `422` |
| `2`, `"maybe"` | `422` | `422` |

**Kitabın `rating` alanı (`float`):**

| Gönderilen | `strict=True` olmadan | `strict=True` ile |
|---|---|---|
| `4.5` | Kabul edilir. | Kabul edilir. |
| `4` | `4.0` yapılır. | `4.0` yapılır. |
| `"4.5"` | `4.5` yapılır. | `422` |
| `"4"` | `4.0` yapılır. | `422` |
| `true` | `1.0` yapılır. | `422` |
| `"abc"` | `422` | `422` |

**Yorumun `score` alanı (`int`):**

| Gönderilen | `strict=True` olmadan | `strict=True` ile |
|---|---|---|
| `4` | Kabul edilir. | Kabul edilir. |
| `"4"`, `"4.0"`, `4.0` | `4` yapılır. | `422` |
| `true` | `1` yapılır. | `422` |
| `4.5` | `422` | `422` |

**Kitabın `title` alanı (`str`):**

| Gönderilen | `strict=True` olmadan | `strict=True` ile |
|---|---|---|
| `123`, `4.5`, `true` | `422` | `422` |

---

## 2. Tablodan çıkanlar

- **Metne çeviri yapılmıyor.** `title` alanına gönderilen sayı, `strict=True` olmadan da reddedildi. Bu yüzden Deney 1'deki `"title": 123` isteği baştan `422` aldı.
- **Bilgi kaybeden çeviriler yapılmıyor.** `4.5` tam sayıya çevrilmedi; çevrilseydi `.5` kaybolurdu. `2` de mantıksal değere çevrilmedi.
- **En şaşırtıcı satır: `"rating": true`.** `strict=True` olmadan kitabın puanı `1.0` oldu. İstemci büyük olasılıkla yanlış alana değer yazmıştı; sunucu bunu fark etmedi.
- **`strict=True` ile yalnızca bir çeviri kalıyor:** Tam sayı (`4`), ondalıklı sayı alanına (`float`) yazılabiliyor. JSON'da `4` ile `4.0` aynı sayıdır; bu çeviride bilgi kaybolmaz.

---

## 3. Yol ve sorgu parametrelerinin değerleri

Yol ve sorgu parametrelerinin değerleri her zaman metin olarak gelir: `/books/42` içindeki `42` de, `?available=true` içindeki `true` da birer metindir. FastAPI bunları parametrenin türüne çevirmek zorundadır; çevirmeseydi `book_id: int` parametresi hiç çalışmazdı.

`strict=True` ayarını yalnızca istek modellerine (`BookCreate`, `BookUpdate`, `ReviewCreate`) yazdık. Fonksiyon parametreleri bu ayardan etkilenmez; `?available=true` sorgu parametresi föyün sonundaki sunucuda da çalışır.

---

## 4. Hangisini seçmeli?

İki davranışın da yeri var:

| Davranış | Ne zaman uygun? |
|---|---|
| Çeviri yapmak (varsayılan) | Değerlerin metin olarak geldiği yerler: yol ve sorgu parametreleri, form alanları |
| Sıkı mod (`strict=True`) | İstemcinin türleri ayırt edebildiği JSON gövdesi. Yanlış türde gönderilen değer büyük olasılıkla istemcideki bir hatadır; sessizce çevirmek bu hatayı gizler. |

Kitap kataloğu API'sinde gövdeyi JSON ile alıyoruz; bu yüzden istek modellerinde sıkı modu seçtik.

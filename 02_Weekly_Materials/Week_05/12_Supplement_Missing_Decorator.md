# Ek Not — `Delete -5` satırında `405` görürsen

Föyün 5.3 bölümünde `Delete -5` satırının `422` alması bekleniyor. Bazen şu çıktı görünür:

```text
Delete -5:  405 {'detail': 'Method Not Allowed'}
```

Bu notta bunun nedenini ve nasıl düzeltileceğini görüyoruz.

---

## 1. Neden: Dekoratör eksik

`server.py` dosyasında `delete_book` fonksiyonunun üstündeki dekoratör satırı unutulmuş:

```python
# Kitabı silme: listeden çıkarır, 204 döner; kitap yoksa 404.
def delete_book(book_id: int = Path(gt=0)):
```

Olması gereken:

```python
# Kitabı silme: listeden çıkarır, 204 döner; kitap yoksa 404.
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int = Path(gt=0)):
```

**Dekoratör (decorator)**, fonksiyonu bir HTTP yöntemi ve bir yolla ilişkilendirir. Bunu Hafta 1'de [görmüştük](../Week_01/02_Practice.md). `@app.delete(...)` satırı olmayınca `delete_book` dosyada sıradan bir Python fonksiyonu olarak durur. FastAPI onu tanımaz ve hiçbir istek ona ulaşmaz.

Bu hatayı fark etmek zor. Dekoratörü olmayan bir fonksiyon da geçerli bir Python kodu, bu yüzden Python hata vermez ve sunucu normal başlar. Fonksiyonun üstündeki `#` ile başlayan açıklama satırı da dekoratör değildir. O satır yalnızca bizim için yazılmış bir nottur ve FastAPI'ye bir şey söylemez.

---

## 2. Neden `405`, neden `404` ya da `422` değil?

FastAPI isteği karşılarken önce yola, sonra yönteme bakar:

1. `/books/-5` adresi `/books/{book_id}` yoluna uyuyor. Bu yol sunucuda var, çünkü `GET`, `PUT` ve `PATCH` dekoratörleri bu yolu kullanıyor.
2. Bu yol için `DELETE` yöntemine bağlı bir fonksiyon yok.
3. FastAPI bu yüzden **`405 Method Not Allowed`** ile cevap verir. Anlamı: "Bu adres var, ama bu yöntemle kullanılamaz." Bu kodu Hafta 2'nin [7.4 bölümünde](../Week_02/02_Practice.md) görmüştük.

`Path(gt=0)` kuralı fonksiyonun parametresine yazılı. Fonksiyon hiçbir isteğe bağlı olmadığı için FastAPI bu kuralı hiç görmez, bu yüzden `422` de gelmez. Aynı sebeple silme işlemi hiçbir kitap için çalışmaz: `DELETE /books/42` isteği de `405` alır ve kitap silinmez.

Aynı istek, sunucudaki koda göre üç farklı yanıt alabilir:

| `server.py` dosyasında | `DELETE /books/-5` yanıtı | Neden? |
|---|---|---|
| Dekoratör var, `Path(gt=0)` var | `422` | FastAPI kuralı fonksiyondan önce kontrol eder. |
| Dekoratör var, `Path(gt=0)` yok | `404` | Fonksiyon çalışır, listede `-5` numaralı kitap bulamaz. |
| Dekoratör yok | `405` | İstek hiçbir fonksiyona ulaşmaz. |

---

## 3. Düzeltmek

Dekoratörü ekle, sunucuyu yeniden başlat ve 5.3'teki istemciyi tekrar çalıştır. İkinci satır föydeki gibi olur:

```text
Delete -5:  422 {'detail': [{'type': 'greater_than', 'loc': ['path', 'book_id'], 'msg': 'Input should be greater than 0', 'input': '-5', 'ctx': {'gt': 0}}]}
```

Bir istek beklenmedik biçimde `405` alıyorsa, önce o yöntemin fonksiyonunun üstünde dekoratör olup olmadığına bak.

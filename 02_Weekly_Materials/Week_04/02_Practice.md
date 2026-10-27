# Hafta 04 — Uygulama Föyü

## 0. CRUD nedir?

Bir veriyle yapılabilecek dört temel iş vardır: oluşturmak, okumak, güncellemek ve silmek. Bu dört işe İngilizce adlarının baş harfleriyle **CRUD** denir: *Create, Read, Update, Delete*. CRUD bir program ya da standart değildir; bu dört işin kısa adıdır.

Hafta 1'den beri yazdığımız kitap kataloğu API'sinde, yani `server.py` dosyasındaki sunucuda, bu dört iş şu isteklerle yapılır:

| İş | İngilizcesi | HTTP metodu | Kitap kataloğu API'sinde | Ne zaman yazdık? |
|---|---|---|---|---|
| Oluşturmak | Create | `POST` | `POST /books` | Hafta 2 |
| Okumak | Read | `GET` | `GET /books`, `GET /books/42` | Hafta 1 |
| Güncellemek | Update | `PUT` ya da `PATCH` | `PUT /books/42`, `PATCH /books/42` | **Bu hafta** |
| Silmek | Delete | `DELETE` | `DELETE /books/42` | **Bu hafta** |

HTTP metotlarının anlamı HTTP standardından gelir: `DELETE` "sil", `PUT` "bu yoldakini gönderdiğimle değiştir", `PATCH` "bu yoldakinin bir kısmını değiştir" demektir. CRUD'un dört işini bu metotlarla eşleştirmek ise REST API'lerinde yaygın bir alışkanlıktır.

Bu hafta kitap kataloğu API'sine güncelleme ve silmeyi ekleyeceğiz:

- **Deney 1:** Kitabı silmek (`DELETE`)
- **Deney 2:** Kitabı tümüyle değiştirmek (`PUT`)
- **Deney 3:** Kitabın bir kısmını değiştirmek (`PATCH`)
- **Deney 4:** Yanıtta hangi alanların döneceğini belirlemek (yanıt modelleri)

Her işlemde kitabı önce okuyacak, sonra isteği gönderecek, sonra tekrar okuyacağız. Böylece her isteğin kitapta neyi değiştirdiğini göreceğiz.

### 0.1 Başlangıç dosyaları

Hafta 3'ün sonundaki dosyalarla başla:

| Dosya | Hafta 3 föyündeki yeri |
|---|---|
| `server.py` | 5.4: Hafta 3'ün son `server.py` dosyası |
| `client.py` | Her deneyde içeriğini baştan yazacağız. |

Hafta 3'teki 8.3 alıştırmasını yaptıysan, eklediğin `get_review` fonksiyonu ve `Location` satırı da dosyada kalabilir; bu haftanın değişiklikleriyle çakışmaz.

> **Kitap sayılarını izlemek için:** Sunucu her başlatıldığında dosyada yazılı üç kitapla ve bir yorumla başlar. İstekle yapılan değişiklikler yalnızca sunucu çalıştığı sürece bellekte durur. Deneylerdeki "sunucuyu yeniden başlat" adımlarını izlersen çıktıların föydekilerle aynı olur.

---

## Deney 1 — Kitabı silmek: DELETE

**Amaç:** Sunucuya kitap silen bir işlem eklemek ve silmeden önce ve sonra kitap listesine bakmak.

Hafta 2 föyünün 7.4 bölümünde `DELETE` isteği göndermiş ve `405` almıştık. Yol vardı, ama o HTTP metodunu karşılayan bir fonksiyon yoktu. Bu deneyde o fonksiyonu yazıyoruz.

### 1.1 Fonksiyon yokken: 405

`server.py` dosyasında henüz bir şey değiştirme. Sunucuyu başlat ve 57 numaralı kitabı silmeyi dene:

```bash
curl -i -X DELETE http://127.0.0.1:8000/books/57
```

```text
HTTP/1.1 405 Method Not Allowed
date: Mon, 26 Oct 2026 18:59:59 GMT
server: uvicorn
allow: GET
content-length: 31
content-type: application/json

{"detail":"Method Not Allowed"}
```

`/books/57` yolu var, ama yalnızca `GET` için bir fonksiyon tanımlı. `allow: GET` başlığı da bunu söylüyor: "Bu yolda yalnızca `GET` kabul ediliyor."

### 1.2 Sunucuya silme işlemini ekle

`server.py` dosyasında `create_book` fonksiyonundan sonra, yorumlarla ilgili fonksiyonlardan önce şunu ekle:

```python
# Kitabı silme: listeden çıkarır, 204 döner; kitap yoksa 404.
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return

    raise HTTPException(status_code=404, detail="Book not found")
```

| Kod | Ne yapar? |
|---|---|
| `@app.delete("/books/{book_id}", status_code=204)` | FastAPI'ye şunu bildirir: "`DELETE /books/...` isteği gelirse `delete_book` fonksiyonunu çalıştır ve başarılı yanıtın durum kodunu `204` yap." |
| `books.remove(book)` | Bulunan kitabı listeden çıkarır. |
| `return` | Fonksiyonu bitirir ve bir şey döndürmez. Döngü de burada biter; listeden kitap çıkardıktan sonra aramaya devam etmeyiz. |
| `raise HTTPException(status_code=404, ...)` | Döngüde kitap bulunmazsa `404` yanıtı gönderilir. |

**204 No Content**, "işlem başarılı, ama yanıtın gövdesi yok" demektir. Silinen kitap artık olmadığı için istemciye geri gönderecek bir şey de yok. Fonksiyonun hiçbir şey döndürmemesi bu yüzden.

### 1.3 İstemciyle dene

`client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"

try:
    # Kitap listesi: silmeden önce say.
    response = httpx.get(base_url + "/books")
    print("Books before:", len(response.json()))

    # Kitabı sil: 57 numaralı kitap.
    response = httpx.delete(base_url + "/books/57")
    print("Delete status:", response.status_code)
    print("Delete body is empty:", response.text == "")

    # Silinen kitap: artık bulunamamalı.
    response = httpx.get(base_url + "/books/57")
    print("Read deleted:", response.status_code, response.text)

    # Kitap listesi: sildikten sonra say.
    response = httpx.get(base_url + "/books")
    print("Books after:", len(response.json()))

    # Aynı silme isteği: kitap artık yok.
    response = httpx.delete(base_url + "/books/57")
    print("Delete again:", response.status_code, response.text)
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Sunucuyu yeniden başlat ve istemciyi **bir kez** çalıştır:

```text
Books before: 3
Delete status: 204
Delete body is empty: True
Read deleted: 404 {"detail":"Book not found"}
Books after: 2
Delete again: 404 {"detail":"Book not found"}
```

| Satır | Anlamı |
|---|---|
| `Books before: 3` | Silmeden önce listede üç kitap var. |
| `Delete status: 204` | Kitap silindi. |
| `Delete body is empty: True` | `204` yanıtının gövdesi boş. |
| `Read deleted: 404` | 57 numaralı kitap artık yok. |
| `Books after: 2` | Listede iki kitap kaldı. |
| `Delete again: 404` | Aynı kitabı ikinci kez silmeye çalıştık. Silinecek kitap kalmadığı için `404` geldi. |

Son satır önemli: Aynı `DELETE` isteğini iki kez gönderdik. Yanıtlar farklı (`204`, sonra `404`), ama sunucudaki veri ikisinden sonra da aynı: 57 numaralı kitap yok. Aynı isteği tekrar göndermenin her HTTP metodunda ne yaptığı [ek notta](03_Supplement_Repeating_Requests.md).

57 numaralı kitabı seçtik, çünkü yorumu yok. Yorumu olan 42 numaralı kitabı silseydik yorumlarına ne olacağı [ayrı bir ek notta](04_Supplement_Deleted_Book_Reviews.md).

> **Ana fikir:** `DELETE` isteği bir kaynağı siler. Silme başarılıysa yanıt genellikle `204 No Content` olur ve gövdesi boştur. Hafta 2'de `405` alan aynı istek, sunucuya o HTTP metodunu karşılayan bir fonksiyon eklenince karşılandı.

---

## Deney 2 — Kitabı tümüyle değiştirmek: PUT

**Amaç:** Bir kitabın bütün bilgilerini yenisiyle değiştiren bir işlem eklemek ve gönderilmeyen bir alana ne olduğunu görmek.

`PUT` isteği "bu yoldaki kitabı, gönderdiğim kitapla değiştir" demektir. Bu yüzden gövdede kitabın **bütün** bilgileri gider; Hafta 2'de `POST` ile kitap eklerken gönderdiğimiz bilgilerin aynısı. Kitabın kimliği ise yoldan gelir ve değişmez.

### 2.1 Sunucuya PUT işlemini ekle

`server.py` dosyasında `delete_book` fonksiyonundan sonra şunu ekle:

```python
# Kitabı tümüyle değiştirme: bütün alanlar yenisiyle değişir; kitap yoksa 404.
@app.put("/books/{book_id}")
def replace_book(book_id: int, book_data: BookCreate):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            new_book = book_data.model_dump()
            new_book["id"] = book_id
            books[index] = new_book
            return new_book

    raise HTTPException(status_code=404, detail="Book not found")
```

| Kod | Ne yapar? |
|---|---|
| `@app.put("/books/{book_id}")` | FastAPI'ye şunu bildirir: "`PUT /books/...` isteği gelirse `replace_book` fonksiyonunu çalıştır." |
| `book_data: BookCreate` | Gövde, Hafta 2'deki `BookCreate` modeline uymalı. Kitap eklerken hangi alanlar gerekiyorsa değiştirirken de onlar gerekiyor. |
| `enumerate(books)` | Döngünün her turunda iki şey verir: kitabın listedeki sırası (`index`) ve kitabın kendisi (`book`). Sıraya, kitabın yerine yenisini koymak için ihtiyacımız var. |
| `new_book["id"] = book_id` | Yeni kitaba kimliğini yoldan verir. Kimlik değişmez. |
| `books[index] = new_book` | Listede eski kitabın yerine yenisini koyar. |
| `return new_book` | Yanıtın gövdesinde kitabın yeni hâli gider. Durum kodu varsayılan `200`. |

`replace_book` fonksiyonu, olmayan bir kitaba `PUT` gönderilirse `404` döndürür. HTTP standardı, böyle bir istekle yeni bir kayıt oluşturulmasına da izin verir; biz bunu yapmıyoruz, çünkü kitap eklemek için `POST /books` var.

### 2.2 İstemciyle dene

73 numaralı kitabın etiketlerine `fastapi` ekleyeceğiz. Gövdede bütün alanları gönderiyoruz; yalnızca `rating` alanını göndermiyoruz.

`client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"

new_version = {
    "title": "Python ile Web API",
    "author": {
        "first_name": "Can",
        "last_name": "Demir"
    },
    "available": True,
    "tags": ["python", "api", "fastapi"]
}

try:
    # Kitabı oku: değiştirmeden önce.
    response = httpx.get(base_url + "/books/73")
    print("Before:", response.json())

    # Kitabı tümüyle değiştir: rating gönderilmedi.
    response = httpx.put(base_url + "/books/73", json=new_version)
    print("Put status:", response.status_code)

    # Kitabı oku: değiştirdikten sonra.
    response = httpx.get(base_url + "/books/73")
    print("After:", response.json())

    # Eksik gövde: yalnızca available gönderildi.
    response = httpx.put(base_url + "/books/73", json={"available": False})
    print("Only available:", response.status_code)

    # Olmayan kitap: 404 beklenir.
    response = httpx.put(base_url + "/books/99", json=new_version)
    print("Book 99:", response.status_code, response.text)
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Before: {'id': 73, 'title': 'Python ile Web API', 'author': {'first_name': 'Can', 'last_name': 'Demir'}, 'available': True, 'tags': ['python', 'api'], 'rating': 4.5}
Put status: 200
After: {'title': 'Python ile Web API', 'author': {'first_name': 'Can', 'last_name': 'Demir'}, 'available': True, 'tags': ['python', 'api', 'fastapi'], 'rating': None, 'id': 73}
Only available: 422
Book 99: 404 {"detail":"Book not found"}
```

`response.json()` bir Python sözlüğü verdiği için çıktıda `true` yerine `True`, `null` yerine `None` görünüyor.

| Satır | Anlamı |
|---|---|
| `Before` | Kitabın etiketleri `["python", "api"]`, puanı `4.5`. |
| `Put status: 200` | Kitap değiştirildi. |
| `After` | Etiketlere `fastapi` eklendi. **Puan ise `None` oldu**, çünkü `rating` alanını göndermedik. `id` alanı da sona geçti, çünkü sunucu kitabı yeni bir sözlük olarak oluşturdu. |
| `Only available: 422` | Gövdede `title`, `author` ve `tags` yok. `BookCreate` modelinde bu alanlar zorunlu olduğu için istek reddedildi. |
| `Book 99: 404` | 99 numaralı kitap yok. |

**422 Unprocessable Entity:** İstemcinin gönderdiği gövde, sunucunun beklediği modele uymuyor. Bir alan eksik ya da yanlış türde olabilir. Bu yanıtı FastAPI kendisi üretir ve fonksiyonu hiç çalıştırmaz; bu yüzden kitap değişmez.

Puanın kaybolması `PUT` isteğinin nasıl çalıştığını gösteriyor. `PUT` kitabın bir kısmını değil, tamamını değiştirir. `rating` alanının `BookCreate` modelinde varsayılan değeri (`None`) olduğu için, göndermeyince hata almadık; ama eski puan da korunmadı, varsayılan değer yazıldı.

> **Ana fikir:** `PUT` isteği kaynağın tamamını, gövdede gönderilen hâliyle değiştirir. Gönderilmeyen alan eski değerini korumaz: Zorunluysa istek reddedilir (`422`), varsayılan değeri varsa o değer yazılır.

---

## Deney 3 — Kitabın bir kısmını değiştirmek: PATCH

**Amaç:** Bir kitabın yalnızca istenen alanlarını değiştiren bir işlem eklemek ve aynı gövdeyi `PUT` ve `PATCH` ile gönderip farkı görmek.

Deney 2'de bir kitabın tek bir etiketini değiştirmek için bile bütün bilgilerini göndermek zorunda kaldık. Oysa çoğu zaman yalnızca bir alan değişir: Kitap ödünç verildiğinde değişen tek şey `available` alanıdır. `PATCH` isteği "bu yoldaki kitapta yalnızca şunları değiştir" demektir. Gövdede yalnızca değişecek alanlar gider.

### 3.1 Bütün alanları isteğe bağlı bir model

`BookCreate` modeli bütün zorunlu alanları istiyor; `PATCH` için bu uygun değil. `server.py` dosyasında `BookCreate` modelinden sonra yeni bir model ekle:

```python
class BookUpdate(BaseModel):
    title: str | None = None
    author: Author | None = None
    available: bool | None = None
    tags: list[str] | None = None
    rating: float | None = None
```

Her alanın sonundaki `= None`, o alanın gönderilmeyebileceğini söyler. Böylece gövdede yalnızca `available` gönderilse de model hata vermez.

### 3.2 Sunucuya PATCH işlemini ekle

`server.py` dosyasında `replace_book` fonksiyonundan sonra şunu ekle:

```python
# Kitabın bir kısmını değiştirme: yalnızca gönderilen alanlar değişir; kitap yoksa 404.
@app.patch("/books/{book_id}")
def update_book(book_id: int, book_data: BookUpdate):
    for book in books:
        if book["id"] == book_id:
            changes = book_data.model_dump(exclude_unset=True)
            book.update(changes)
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

| Kod | Ne yapar? |
|---|---|
| `@app.patch("/books/{book_id}")` | FastAPI'ye şunu bildirir: "`PATCH /books/...` isteği gelirse `update_book` fonksiyonunu çalıştır." |
| `book_data: BookUpdate` | Gövde, bütün alanları isteğe bağlı olan `BookUpdate` modeline uymalı. |
| `model_dump(exclude_unset=True)` | Modelden bir sözlük oluşturur, ama **yalnızca istemcinin gövdede gönderdiği alanlarla**. `{"available": false}` gönderildiyse sözlük `{"available": False}` olur. |
| `book.update(changes)` | Kitabın sözlüğünde yalnızca `changes` içindeki alanları değiştirir; öteki alanlara dokunmaz. Kitap listedeki yerinde kalır. |
| `return book` | Yanıtın gövdesinde kitabın yeni hâli gider. Durum kodu varsayılan `200`. |

`exclude_unset=True` yazılmasaydı, gönderilmeyen alanların hepsi `None` olarak sözlüğe girer ve kitabın bütün bilgilerini silerdi. Bunun denemesi ve "gönderilmeyen alan" ile "`null` gönderilen alan" arasındaki fark [ek notta](05_Supplement_Patch_Unset_vs_Null.md).

### 3.3 İstemciyle dene

42 numaralı kitabı ödünç verilmiş olarak işaretleyeceğiz. `client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"

try:
    # Kitabı oku: değiştirmeden önce.
    response = httpx.get(base_url + "/books/42")
    print("Before:", response.json())

    # Kitabın bir kısmını değiştir: yalnızca available.
    response = httpx.patch(base_url + "/books/42", json={"available": False})
    print("Patch status:", response.status_code)

    # Kitabı oku: değiştirdikten sonra.
    response = httpx.get(base_url + "/books/42")
    print("After:", response.json())

    # Aynı gövde PUT ile: bütün alanlar beklenir.
    response = httpx.put(base_url + "/books/42", json={"available": False})
    print("Same body with PUT:", response.status_code)

    # Olmayan kitap: 404 beklenir.
    response = httpx.patch(base_url + "/books/99", json={"available": False})
    print("Book 99:", response.status_code, response.text)
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Before: {'id': 42, 'title': 'API Yolculuğu', 'author': {'first_name': 'Deniz', 'last_name': 'Kaya'}, 'available': True, 'tags': ['software', 'education'], 'rating': None}
Patch status: 200
After: {'id': 42, 'title': 'API Yolculuğu', 'author': {'first_name': 'Deniz', 'last_name': 'Kaya'}, 'available': False, 'tags': ['software', 'education'], 'rating': None}
Same body with PUT: 422
Book 99: 404 {"detail":"Book not found"}
```

| Satır | Anlamı |
|---|---|
| `Before` | Kitap ödünç verilebilir durumda: `'available': True`. |
| `Patch status: 200` | Kitap değiştirildi. |
| `After` | Yalnızca `available` değişti: `False`. Öteki alanlar aynı kaldı; `id` de yerinde duruyor, çünkü sunucu kitabın sözlüğünü yeniden oluşturmadı, yalnızca bir alanını değiştirdi. |
| `Same body with PUT: 422` | Aynı gövde `PUT` ile reddedildi; `PUT` kitabın bütün alanlarını istiyor. |
| `Book 99: 404` | 99 numaralı kitap yok. |

### 3.4 PUT ile PATCH yan yana

| | `PUT` | `PATCH` |
|---|---|---|
| Gövdede ne gider? | Kitabın bütün bilgileri | Yalnızca değişecek alanlar |
| Gönderilmeyen alana ne olur? | Zorunluysa `422`; varsayılan değeri varsa o değer yazılır | Eski değerini korur |
| `{"available": false}` gövdesiyle | `422` | `200`, yalnızca `available` değişir |
| `server.py` dosyasında kullandığı model | `BookCreate` | `BookUpdate` |
| Ne zaman kullanılır? | Kaynağın tamamı yeniden gönderilecekse | Bir ya da birkaç alan değişecekse |

> **Ana fikir:** `PATCH` isteği kaynağın yalnızca gövdede gönderilen alanlarını değiştirir. Bunun için sunucuda bütün alanları isteğe bağlı bir model ve yalnızca gönderilen alanları alan `exclude_unset=True` gerekir.

---

## Deney 4 — Yanıtta hangi alanlar dönsün? Yanıt modelleri

**Amaç:** Sunucunun sakladığı ama istemciye göstermemesi gereken bir bilgiyi yanıt modeliyle yanıttan çıkarmak.

Şimdiye kadar fonksiyonun döndürdüğü sözlük, olduğu gibi yanıtın gövdesine gidiyordu. Sözlükte ne varsa istemci onu görüyordu. Ama sunucuda saklanan her bilgi istemciye gösterilmemeli. Örneğin kütüphane görevlisinin bir kitap için yazdığı not, okuyucuya gitmemeli.

### 4.1 Sunucuya görevli notu ekle

`server.py` dosyasında `books` listesindeki 42 numaralı kitaba bir alan ekle. Değişen kısım: `rating` satırının sonuna virgül ve altına `internal_note` satırı.

```python
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": {
            "first_name": "Deniz",
            "last_name": "Kaya"
        },
        "available": True,
        "tags": ["software", "education"],
        "rating": None,
        "internal_note": "Kapağı yıpranmış, yenisi sipariş edildi."
    },
```

`client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"

try:
    # Tek kitap: yanıtta hangi alanlar var?
    response = httpx.get(base_url + "/books/42")
    print("Book 42:", response.json())

    # Kitap listesi: ilk kitabın alanları.
    response = httpx.get(base_url + "/books")
    print("First in list:", response.json()[0])
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Book 42: {'id': 42, 'title': 'API Yolculuğu', 'author': {'first_name': 'Deniz', 'last_name': 'Kaya'}, 'available': True, 'tags': ['software', 'education'], 'rating': None, 'internal_note': 'Kapağı yıpranmış, yenisi sipariş edildi.'}
First in list: {'id': 42, 'title': 'API Yolculuğu', 'author': {'first_name': 'Deniz', 'last_name': 'Kaya'}, 'available': True, 'tags': ['software', 'education'], 'rating': None, 'internal_note': 'Kapağı yıpranmış, yenisi sipariş edildi.'}
```

Görevlinin notu istemciye gitti. Sunucu sözlüğü olduğu gibi gönderdiği için, sözlüğe eklenen her alan yanıtta da görünüyor.

### 4.2 Yanıt modeli tanımla

**Yanıt modeli**, yanıtın gövdesinde hangi alanların bulunacağını söyleyen bir Pydantic modelidir. `server.py` dosyasında `BookCreate` modelinden sonra şunu ekle:

```python
class BookPublic(BookCreate):
    id: int
```

Bu iki satır şunu söylüyor:

- **`class BookPublic(BookCreate)`:** `BookPublic` modeli, `BookCreate` modelindeki bütün alanları alır. Bu alanları yeniden yazmamıza gerek kalmaz.
- **`id: int`:** O alanlara bir alan daha ekler: kitabın kimliği.

Yani bu iki satır, aşağıdaki modelin kısa yazılışıdır:

```python
class BookPublic(BaseModel):
    title: str
    author: Author
    available: bool
    tags: list[str]
    rating: float | None = None
    id: int
```

Adındaki `Public`, bu modelin kitabın **istemciye gösterilen** hâli olduğunu söyler. Ad, `BookCreate` ve `BookUpdate` ile aynı düzende; ayrıca `books` listesi ve döngüdeki `book` değişkeniyle de karışmaz.

İlk beş alan `BookCreate` modelinden geliyor, son alan bizim eklediğimiz. İki yazılış da aynı modeli tanımlar; kısa yazılışı seçiyoruz, çünkü `BookCreate` modeline ileride bir alan eklersek `BookPublic` modeli de onu kendiliğinden alır.

`internal_note` bu modelde yok. 4.3'te yanıtı bu modele göre hazırlattığımızda, not bu yüzden yanıta girmeyecek.

**Neden ayrı bir model?** `BookCreate` modelinde `id` yok, çünkü kitabı ekleyen istemci kimliği göndermiyor; kimliği sunucu veriyor (Hafta 2). Yanıttaki kitabın ise kimliği de görünmeli. Sunucumuzda artık her biri başka bir iş için kullanılan üç kitap modeli var:

| Model | Nerede kullanılıyor? | Alanlar |
|---|---|---|
| `BookCreate` | İstekte: `POST` ile kitap eklerken ve `PUT` ile kitabı tümüyle değiştirirken | Kitabın bilgileri, `id` yok. `title`, `author`, `available` ve `tags` zorunlu. |
| `BookUpdate` | İstekte: `PATCH` ile kitabın bir kısmını değiştirirken (Deney 3) | Aynı alanlar, ama hepsi isteğe bağlı. `id` yok. |
| `BookPublic` | Yanıtta: sunucu kitabı döndürürken | `BookCreate` modelinin bütün alanları ve `id`. |

İlk iki model istemcinin **gönderdiğini**, üçüncüsü sunucunun **döndürdüğünü** tarif ediyor.

### 4.3 İşlemlere yanıt modelini ekle

`server.py` dosyasında kitap döndüren beş işlemin dekoratörünü değiştir:

| Eski satır | Yeni satır |
|---|---|
| `@app.get("/books")` | `@app.get("/books", response_model=list[BookPublic])` |
| `@app.get("/books/{book_id}")` | `@app.get("/books/{book_id}", response_model=BookPublic)` |
| `@app.post("/books", status_code=201)` | `@app.post("/books", status_code=201, response_model=BookPublic)` |
| `@app.put("/books/{book_id}")` | `@app.put("/books/{book_id}", response_model=BookPublic)` |
| `@app.patch("/books/{book_id}")` | `@app.patch("/books/{book_id}", response_model=BookPublic)` |

| Kod | Ne yapar? |
|---|---|
| `response_model=BookPublic` | FastAPI'ye şunu bildirir: "Fonksiyon ne döndürürse döndürsün, yanıtın gövdesine yalnızca `BookPublic` modelindeki alanları koy." Modelde olmayan alanlar yanıta girmez. |
| `response_model=list[BookPublic]` | Kitap listesi için: Listedeki her kitap `BookPublic` modeline göre süzülür. |

Fonksiyonların içi değişmiyor. `internal_note` sunucudaki listede durmaya devam ediyor; yalnızca yanıta girmiyor.

`delete_book` fonksiyonuna yanıt modeli eklemiyoruz, çünkü `204` yanıtının gövdesi yok.

### 4.4 Tekrar dene

Sunucuyu yeniden başlat ve aynı istemciyi çalıştır:

```text
Book 42: {'title': 'API Yolculuğu', 'author': {'first_name': 'Deniz', 'last_name': 'Kaya'}, 'available': True, 'tags': ['software', 'education'], 'rating': None, 'id': 42}
First in list: {'title': 'API Yolculuğu', 'author': {'first_name': 'Deniz', 'last_name': 'Kaya'}, 'available': True, 'tags': ['software', 'education'], 'rating': None, 'id': 42}
```

`internal_note` iki yanıtta da yok. Alanların sırası da değişti: Artık `BookPublic` modelindeki sırayla geliyor, `id` sonda.

Yanıt modelinin bir yararı daha var: `http://127.0.0.1:8000/docs` sayfasında her işlemin yanıtında hangi alanların döneceği artık görünür. Hafta 3'te elle yazdığımız `README.md` belgesindeki bilginin bir kısmını FastAPI bu modelden kendisi üretir.

> **Ana fikir:** Yanıt modeli, yanıtın gövdesinde hangi alanların bulunacağını belirler. Fonksiyon daha fazla alan içeren bir sözlük döndürse bile, istemciye yalnızca modeldeki alanlar gider.

---

## 5. Ek çalışmalar: curl, belge ve kendi kodunu yazmak

### 5.1 DELETE, PUT ve PATCH isteklerini curl ile göndermek

Sunucuyu yeniden başlat ve üç isteği sırayla gönder.

**Kitabı silmek:**

```bash
curl -i -X DELETE http://127.0.0.1:8000/books/57
```

```text
HTTP/1.1 204 No Content
date: Mon, 26 Oct 2026 18:58:23 GMT
server: uvicorn
content-type: application/json

```

Boş satırdan sonra hiçbir şey yok; yanıtın gövdesi boş.

**Kitabı tümüyle değiştirmek:**

```bash
curl -i -X PUT http://127.0.0.1:8000/books/73 -H "Content-Type: application/json" -d '{"title": "Python ile Web API", "author": {"first_name": "Can", "last_name": "Demir"}, "available": true, "tags": ["python", "api", "fastapi"]}'
```

```text
HTTP/1.1 200 OK
date: Mon, 26 Oct 2026 18:58:23 GMT
server: uvicorn
content-length: 153
content-type: application/json

{"title":"Python ile Web API","author":{"first_name":"Can","last_name":"Demir"},"available":true,"tags":["python","api","fastapi"],"rating":null,"id":73}
```

**Kitabın bir kısmını değiştirmek:**

```bash
curl -i -X PATCH http://127.0.0.1:8000/books/42 -H "Content-Type: application/json" -d '{"available": false}'
```

```text
HTTP/1.1 200 OK
date: Mon, 26 Oct 2026 18:58:23 GMT
server: uvicorn
content-length: 149
content-type: application/json

{"title":"API Yolculuğu","author":{"first_name":"Deniz","last_name":"Kaya"},"available":false,"tags":["software","education"],"rating":null,"id":42}
```

PATCH yanıtında `internal_note` yok; Deney 4'teki yanıt modeli burada da çalışıyor.

PowerShell kullanıyorsan Hafta 2 föyündeki 7.2.4 bölümüne bak: `curl.exe` kullan ve gövdeyi bir dosyadan gönder.

### 5.2 `README.md` belgesine yeni işlemleri eklemek

Hafta 3'te yazdığın `README.md` belgesinin işlemler tablosuna şu üç satırı ekle:

```markdown
| `PUT` | `/books/{book_id}` | Kitabın bütün bilgilerini gönderilenlerle değiştirir. |
| `PATCH` | `/books/{book_id}` | Kitabın yalnızca gönderilen alanlarını değiştirir. |
| `DELETE` | `/books/{book_id}` | Kitabı siler. Yanıt `204 No Content` olur. |
```

Sonra her biri için 5.1'deki komutu ve yanıtı, Hafta 3'teki örnekler gibi belgeye ekle. Hata durumlarını da yaz: Kitap yoksa üçünde de `404`; `PUT` isteğinde zorunlu bir alan eksikse `422`.

### 5.3 Kendin yaz: bir yorumu silmek

Bu alıştırmada bir kitabın tek bir yorumunu silen işlemi sen yazacaksın.

**İstenenler:**

1. `DELETE /books/{book_id}/reviews/{review_id}` işlemini ekle. Hem kitap kimliği hem yorum kimliği eşleşen yorumu silsin ve `204` döndürsün.
2. Böyle bir yorum yoksa `404` ve `{"detail":"Review not found"}` döndürsün.

**İpuçları:**

- Deney 1'deki `delete_book` fonksiyonu ile Hafta 3'teki 8.3 alıştırmasını birleştir.
- Yorumlar `reviews` listesinde duruyor; listeden çıkarmak için yine `remove` kullanılır.
- İki koşulu birlikte kontrol etmek için `and` kullan.

**Kontrol et:** Sunucuyu yeniden başlat ve istekleri bu sırayla gönder. Sonuçlar şöyle olmalı:

| İstek | Durum kodu | Neden? |
|---|---|---|
| `DELETE /books/57/reviews/1` | `404` | 1 numaralı yorum var, ama 57 numaralı kitaba değil 42'ye ait. |
| `DELETE /books/42/reviews/1` | `204` | Yorum silindi. |
| `GET /books/42/reviews` | `200` ve `[]` | Kitabın yorumu kalmadı. |
| `DELETE /books/42/reviews/1` | `404` | Yorum zaten silinmiş. |

Kodunu yazıp denedikten sonra [ek nottaki cevapla](06_Supplement_Exercise_5_3_Answer.md) karşılaştır.

---

## 6. Kendini kontrol et: Bu haftanın altı sorusu

1. CRUD'un dört işi kitap kataloğu API'sinde hangi isteklerle yapılır?
2. `DELETE` isteğinin yanıtı neden `204` ve gövdesi neden boş? Aynı isteği ikinci kez gönderince neden `404` gelir?
3. 73 numaralı kitabı `PUT` ile `rating` göndermeden değiştirince puanı neden `None` oldu?
4. `{"available": false}` gövdesi `PUT` ile `422`, `PATCH` ile `200` alıyor. Neden?
5. `update_book` fonksiyonunda `exclude_unset=True` ne işe yarar?
6. `response_model=BookPublic` eklenince `internal_note` yanıttan kayboldu. Bu not sunucudaki listeden de silindi mi?

### 6.1 Soruların cevapları

1. Oluşturmak `POST /books`, okumak `GET /books` ve `GET /books/42`, güncellemek `PUT /books/42` ya da `PATCH /books/42`, silmek `DELETE /books/42` ile yapılır.
2. `204 No Content`, işlemin başarılı olduğunu ama gövdenin boş olduğunu söyler; silinen kitap artık olmadığı için gönderilecek bir şey yoktur. İkinci istekte silinecek kitap kalmadığı için `404` gelir. Sunucudaki veri iki istekten sonra da aynıdır.
3. `PUT` kitabın tamamını gövdede gönderilen hâliyle değiştirir. `rating` gönderilmediği için modeldeki varsayılan değeri, yani `None` yazıldı; eski puan korunmadı.
4. `PUT` için kullanılan `BookCreate` modelinde `title`, `author` ve `tags` zorunludur, bu yüzden istek reddedilir. `PATCH` için kullanılan `BookUpdate` modelinde bütün alanlar isteğe bağlıdır; yalnızca `available` değişir.
5. Modelden oluşturulan sözlüğe yalnızca istemcinin gövdede gönderdiği alanları koyar. Böylece gönderilmeyen alanlar `None` olarak kitabın üzerine yazılmaz.
6. Hayır. Yanıt modeli yalnızca yanıtın gövdesini süzer; `internal_note` sunucudaki `books` listesinde durmaya devam eder.

---

## 7. Resmî belgeler

- [FastAPI — Body: Updates](https://fastapi.tiangolo.com/tutorial/body-updates/)
- [FastAPI — Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)
- [MDN — PUT](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/PUT)
- [MDN — PATCH](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/PATCH)
- [MDN — DELETE](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/DELETE)
- [MDN — 204 No Content](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/204)
- [HTTP standardı (RFC 9110) — PUT ve DELETE](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3.4)
- [PATCH standardı (RFC 5789)](https://www.rfc-editor.org/rfc/rfc5789)

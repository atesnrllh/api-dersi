# Ek Not — Aynı İsteği Tekrar Göndermek

Föyün Deney 1'inde aynı `DELETE` isteğini iki kez gönderdik. İlkinde `204`, ikincisinde `404` geldi; ama 57 numaralı kitap iki seferden sonra da yoktu. Bu notta aynı denemeyi beş HTTP metodunun hepsiyle yapıyoruz.

---

## 1. Beş isteği ikişer kez göndermek

Yapacağımız şey şu: Beş HTTP metodunun her biriyle bir istek hazırlıyoruz ve **aynı isteği arka arkaya iki kez** gönderiyoruz. Her gönderimden sonra yanıtın durum koduna ve sunucudaki kitaplara bakıyoruz. Soru şu: İkinci gönderim, sunucudaki veriyi ilk gönderimden sonra bir kez daha değiştiriyor mu?

Föyün Deney 4 sonundaki sunucuyu kullanıyoruz. Proje klasöründe `repeat_client.py` adlı ayrı bir dosya oluştur:

```python
import httpx

base_url = "http://127.0.0.1:8000"

new_book = {
    "title": "HTTP ile Yeni Bir Kitap",
    "author": {
        "first_name": "Ada",
        "last_name": "Yıldız"
    },
    "available": True,
    "tags": ["http", "python"],
    "rating": None
}

new_version = {
    "title": "Python ile Web API",
    "author": {
        "first_name": "Can",
        "last_name": "Demir"
    },
    "available": True,
    "tags": ["python", "api", "fastapi"]
}


def count_books():
    return len(httpx.get(base_url + "/books").json())


try:
    print("Start:", count_books(), "books")

    # GET: 42 numaralı kitabı iki kez oku.
    for attempt in [1, 2]:
        response = httpx.get(base_url + "/books/42")
        print(f"GET    #{attempt}: {response.status_code}, books: {count_books()}")

    # POST: aynı kitabı iki kez ekle.
    for attempt in [1, 2]:
        response = httpx.post(base_url + "/books", json=new_book)
        print(f"POST   #{attempt}: {response.status_code}, new id: {response.json()['id']}, books: {count_books()}")

    # PUT: 73 numaralı kitabı aynı gövdeyle iki kez değiştir.
    for attempt in [1, 2]:
        response = httpx.put(base_url + "/books/73", json=new_version)
        print(f"PUT    #{attempt}: {response.status_code}, tags: {response.json()['tags']}")

    # PATCH: 42 numaralı kitabı aynı gövdeyle iki kez değiştir.
    for attempt in [1, 2]:
        response = httpx.patch(base_url + "/books/42", json={"available": False})
        print(f"PATCH  #{attempt}: {response.status_code}, available: {response.json()['available']}")

    # DELETE: 57 numaralı kitabı iki kez sil.
    for attempt in [1, 2]:
        response = httpx.delete(base_url + "/books/57")
        print(f"DELETE #{attempt}: {response.status_code}, books: {count_books()}")
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

| Kod | Ne yapar? |
|---|---|
| `count_books()` | Kitap listesini isteyip kaç kitap olduğunu döndüren küçük bir yardımcı fonksiyon. Her gönderimden sonra kitap sayısına bakmak için. |
| `for attempt in [1, 2]:` | İçindeki isteği iki kez gönderir. `attempt`, kaçıncı gönderim olduğunu tutar. |

İstekler bu sırayla, aynı sunucuya gönderiliyor. Bu yüzden kitap sayısı bir istekten ötekine taşınıyor: POST'tan sonra 5 olan sayı, DELETE'ten sonra 4'e iniyor.

Sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Start: 3 books
GET    #1: 200, books: 3
GET    #2: 200, books: 3
POST   #1: 201, new id: 74, books: 4
POST   #2: 201, new id: 75, books: 5
PUT    #1: 200, tags: ['python', 'api', 'fastapi']
PUT    #2: 200, tags: ['python', 'api', 'fastapi']
PATCH  #1: 200, available: False
PATCH  #2: 200, available: False
DELETE #1: 204, books: 4
DELETE #2: 404, books: 4
```

| İstek | Ne yapmak istiyor? | 1. gönderimde ne oldu? | 2. gönderimde ne oldu? | İkinci gönderim veriyi değiştirdi mi? |
|---|---|---|---|---|
| `GET /books/42` | 42 numaralı kitabı okumak | `200`; kitap okundu, kitap sayısı 3 | `200`; aynı kitap yine okundu, kitap sayısı 3 | **Hayır.** Okumak veriyi değiştirmez. |
| `POST /books` | Yeni bir kitap eklemek | `201`; kitap `74` kimliğiyle eklendi, kitap sayısı 4 | `201`; aynı kitap bu kez `75` kimliğiyle **bir daha** eklendi, kitap sayısı 5 | **Evet.** Her gönderim yeni bir kitap ekledi. |
| `PUT /books/73` | 73 numaralı kitabın etiketlerini `python`, `api`, `fastapi` yapmak | `200`; etiketler değişti | `200`; etiketler zaten öyleydi, aynı kaldı | **Hayır.** Kitap zaten gönderilen hâldeydi. |
| `PATCH /books/42` | 42 numaralı kitabı ödünç verilmiş yapmak | `200`; `available` `False` oldu | `200`; `available` zaten `False` idi | **Hayır.** Aynı değer bir daha yazıldı. |
| `DELETE /books/57` | 57 numaralı kitabı silmek | `204`; kitap silindi, kitap sayısı 4 | `404`; silinecek kitap yoktu, kitap sayısı 4 | **Hayır.** Kitap zaten silinmişti. |

`DELETE` satırında iki ayrı soruya bakıyoruz, karıştırmayalım:

- **Yanıt aynı mı?** Hayır: önce `204`, sonra `404`.
- **Sunucudaki veri aynı mı?** Evet: İki istekten sonra da kitap yok, kitap sayısı 4.

Bu notta önemli olan ikinci soru. Beş istekten yalnızca `POST`, ikinci gönderimde veriyi bir kez daha değiştirdi.

---

## 2. HTTP standardı ne söylüyor?

Bir isteği birkaç kez göndermek, sunucudaki veriyi bir kez göndermekle aynı hâlde bırakıyorsa, HTTP standardı bu isteğe **idempotent** der. Türkçede yerleşmiş bir karşılığı yok; "tekrarlanınca sonucu değişmeyen" diye düşünebilirsin.

Tablodaki iki soru farklı şeyleri soruyor:

- **İlk gönderimde veriyi değiştirir mi?** İstek bir kez gönderildiğinde sunucudaki kitaplarda bir şey değişiyor mu? 1. bölümde `GET /books/42` kitabı yalnızca okudu, kitaplarda hiçbir şey değişmedi: **Hayır.** `DELETE /books/57` ise kitabı listeden çıkardı: **Evet.**
- **İdempotent mi?** Aynı istek ikinci kez gönderildiğinde kitaplar, ilk gönderimden sonraki hâliyle mi kalıyor? `DELETE /books/57` ikinci kez gönderilince kitap zaten yoktu, hiçbir şey değişmedi: **Evet.** `POST /books` ikinci kez gönderilince bir kitap daha eklendi: **Hayır.**

| HTTP metodu | İlk gönderimde veriyi değiştirir mi? | İdempotent mi? |
|---|---|---|
| `GET` | Hayır (Hafta 3, Deney 4: güvenli) | Evet |
| `PUT` | Evet | Evet: Aynı kitabı iki kez göndermek, bir kez göndermekle aynı sonucu bırakır. |
| `DELETE` | Evet | Evet: Silinmiş kitap ikinci istekte de silinmiş kalır. |
| `POST` | Evet | **Hayır:** Her istek yeni bir kayıt oluşturabilir. |
| `PATCH` | Evet | **Garanti edilmez.** |

`PATCH` 1. bölümdeki denemede tekrarlanınca bir şey değiştirmedi, çünkü `available` alanına aynı değeri yazdı. Ama bir `PATCH` isteği "stok sayısını bir artır" gibi bir iş de yapabilir; o zaman her tekrar veriyi yeniden değiştirir. Standart bu yüzden `PATCH` için bir şey garanti etmez; bu, API'yi yazan kişinin isteği nasıl tasarladığına bağlıdır.

---

## 3. Bu neden önemli?

İstemci bir istek gönderdiğinde bazen yanıt gelmez: Bağlantı kopmuş, sunucu geç kalmış olabilir. İstemci isteğin sunucuya ulaşıp ulaşmadığını bilemez.

- İstek `GET`, `PUT` ya da `DELETE` ise istemci aynı isteği gönül rahatlığıyla tekrar gönderebilir. İstek ilk seferde ulaşmış olsa bile tekrar veriyi bozmaz.
- İstek `POST` ise tekrar göndermek, Hafta 2'de gördüğümüz gibi aynı kitabın iki kez eklenmesine yol açabilir.

Hafta 3'te tarayıcıların GET isteğini kendiliğinden tekrar gönderebildiğini görmüştük. Tarayıcılar ve öteki programlar, metotların bu özelliklerine güvenerek davranır; bu yüzden her işi kendi anlamına uygun HTTP metoduyla yazmak önemlidir.

# Ek Not — `Location` Başlığı Ne İşe Yarar?

Deney 4'te sunucu yeni kitabı ekledi ve yanıta `Location: /book/74` başlığını koydu. İstemci de bu başlığı okuyup kitabı geri istedi.

Bu notta şu soruyu cevaplıyoruz: **Kitabın yolunu zaten kendimiz kurabiliyorsak, `Location` başlığına neden gerek var?**

---

## 1. İstemci neyi önceden bilir, neyi sonradan öğrenir?

| Bilgi | Örnek | İstemci ne zaman öğrenir? |
|---|---|---|
| Kitabı ekleyen istek | `POST /book` | **Önceden.** Bunu bilmeden kitap eklenemez. |
| Yeni kitabın kimliği | `74` | **Sonradan.** Kimliği sunucu verir; istemci onu yanıttan öğrenir. |

Kimliği istemci önceden bilemez. Bizim sunucumuzda ilk eklenen kitap `74`, ikincisi `75` olur. Sunucu yeniden başlatılırsa sayılar yine `74`'ten başlar.

---

## 2. Bizim örneğimizde istemci kitabın yolunu nasıl bulur?

Sunucunun yanıtı hem gövdede kimliği hem de `Location` başlığını içeriyor:

```http
HTTP/1.1 201 Created
location: /book/74

{"title":"HTTP ile Yeni Bir Kitap", ... ,"id":74}
```

İstemci yeni kitabın yolunu iki şekilde bulabilir:

| Seçenek | İstemci ne yapar? | Sonuç |
|---|---|---|
| Gövdedeki kimliği kullanmak | `/book/` ile `74`'ü kendisi birleştirir. | `/book/74` |
| `Location` başlığını okumak | Sunucunun verdiği yolu doğrudan alır. | `/book/74` |

**Önemli:** `Location` başlığındaki yol, POST isteğini gönderdiğimiz yoldan türetilmez. Sunucuyu yazan kişi oraya, yeni kitabın **GET ile okunacağı yolu** yazar. Bizim sunucumuzda bu başlığı yazan satır şudur:

```python
response.headers["Location"] = f"/book/{new_id}"
```

Buraya `/book/...` yazdık, çünkü bizim GET yolumuz `@app.get("/book/{book_id}")`. Bizim API'mizde okuma yolu ile ekleme yolu aynı kelimeyle başladığı için `Location`, "ekleme yolu + kimlik" gibi görünür. Bu, API'mizi böyle yazdığımız içindir.

**İkisi de aynı sonucu verir.** Bu yüzden bizim örneğimizde `Location` başlığı zorunlu değildir; yolu kendimiz de kurabiliriz.

Deney 4'te `Location` başlığını kullanmamızın nedeni, sunucuda bir **yanıt başlığı eklemeyi** ve istemcide bu başlığı **okumayı** öğrenmektir.

---

## 3. `Location` başlığı ne zaman gerçekten gerekir?

İstemcinin yolu kendisi kuramadığı iki durumda:

**3.1 Sunucu gövdede kimliği göndermiyorsa.** Bazı API'ler kayıt oluşturduğunda yanıtın gövdesini boş bırakır, yalnızca `Location` başlığını gönderir. Kimlik gövdede olmadığı için yolu kurmak mümkün değildir. İstemci yeni kaydın yolunu yalnızca bu başlıktan öğrenebilir.

**3.2 Tek kitabın yolu bizimki gibi kurulmuyorsa.** Tek bir kitabın hangi yoldan okunacağına, API'yi yazan kişi karar verir. Bu yol, sunucudaki dekoratöre ne yazıldığına bağlıdır. Bizim sunucumuzda tek kitabı okuyan fonksiyon şöyle tanımlı:

```python
@app.get("/book/{book_id}")
def get_book(book_id: int):
```

Bu yüzden 74 numaralı kitabın yolu `/book/74` olur ve istemci kimliği öğrenince yolu kendisi kurabilir. Ama başka biri aynı işi yapan bir API'yi farklı yazabilirdi:

| Sunucudaki tanım | 74 numaralı kitabın yolu |
|---|---|
| `@app.get("/book/{book_id}")` (bizim API'miz) | `/book/74` |
| `@app.get("/book-detail")` ve kimlik sorgu parametresiyle | `/book-detail?id=74` |
| `@app.get("/book/{title_slug}")` ve kimlik yerine kitabın adı | `/book/http-ile-yeni-bir-kitap` |

İstemcinin elinde yalnızca `"id": 74` olduğunu düşünelim. İkinci API'de `/book/` + `74` diye birleştirirse tanımlı olmayan bir yola gider ve `404` alır. Üçüncü API'de kimliği bilmek hiç işe yaramaz, çünkü yolda kitabın adı kullanılır. Bu API'lerde istemci doğru yolu tahmin edemez. Sunucu ise yolu bilir, çünkü onu kendisi tanımladı; doğru yolu `Location` başlığıyla istemciye söyler.

Bunu denemek için ekleme yolu yine `POST /book`, ama tek kitabı okuma yolu `/book-detail?id=...` olan küçük bir sunucu yazdık. Bu sunucu `Location` başlığına okuma yolunu yazıyor:

```python
response.headers["Location"] = f"/book-detail?id={created_book['id']}"
```

İstemci önce yolu kendisi kurdu, sonra `Location` başlığındaki yolu kullandı:

```text
POST status: 201
Body id: 74
Location: /book-detail?id=74
Kendi kurduğumuz yol: /book/74 -> 404
Location yolu: /book-detail?id=74 -> 200 {'title': 'HTTP ile Yeni Bir Kitap', 'id': 74}
```

Kendi kurduğumuz `/book/74` yolu bu sunucuda yok. `Location` başlığındaki yol ise kitabı getirdi, çünkü o yolu sunucu kendi okuma yoluna göre yazdı.

Kısacası, yolu kimlikten kurabilmemizin nedeni API'mizi böyle yazmış olmamızdır. Her API böyle değildir.

---

## 4. Kitabı ekledikten sonra neden GET ile tekrar okuyoruz?

Deney 4'teki istemci, kitabı ekledikten sonra aynı kitabı bir de GET ile istiyor:

```python
location = response.headers["Location"]
read_response = httpx.get(base_url + location)
```

POST yanıtında kitap zaten geldiği hâlde neden tekrar okuyoruz? Çünkü GET yanıtı, kitabın sunucuda **gerçekten saklandığını** ve **hangi haliyle saklandığını** gösterir.

Gerçek uygulamalarda sunucu, kaydı saklarken bazı bilgileri kendisi ekler: kimlik, oluşturulma zamanı ya da gönderilmeyen alanlar için varsayılan değerler. GET ile okuyunca istemcinin gönderdiğini değil, **sunucunun sakladığını** görürüz.

6. haftada kayıtları veritabanında saklamaya başladığımızda bu adım daha da anlamlı olacak.

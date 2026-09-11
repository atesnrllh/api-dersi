# Hafta 02 — Teorik Ders Notu

## HTTP İstek–Yanıt Yapısı, Metotlar, Başlıklar ve Durum Kodları

**Ders:** Uygulama Programı Arayüzü (API)

**Düzey:** API konusunda başlangıç

**Ön koşul:** Birinci haftanın teori notu ve kitap kataloğu uygulaması

**Sürüm:** 1.0 — 11 Eylül 2026

> Bu hafta yeni ve ilgisiz bir örneğe geçmiyoruz. [Birinci hafta uygulamasında](../Hafta_01/02_Uygulama_Foyu.md) yazdığımız kitap kataloğundaki istekleri açıp HTTP mesajının parçalarını inceliyoruz. [İkinci hafta uygulama föyünde](02_Uygulama_Foyu.md) önce aynı işlemleri Postman ile elle kuracak, ardından kitap ekleyen küçük bir Python istemcisi yazacağız.

## 1. Birinci haftadan ikinci haftaya geçiş

Birinci haftada şu ilişkiyi kurduk:

```text
client.py  ── HTTP isteği ──►  server.py
client.py  ◄─ HTTP yanıtı ───  server.py
```

Şu isteğin çalıştığını gördük:

```http
GET /api/books?search=Python&available=true
```

Bu gösterimde bazı parçaları kullandık; fakat hepsini sistemli biçimde incelemedik. İkinci haftanın ana soruları şunlardır:

1. İstemci, sunucuya **ne yapmak istediğini** nasıl bildirir?
2. Yol, sorgu parametresi, başlık ve gövde hangi bilgileri taşır?
3. Sunucu işlemin sonucunu istemciye nasıl açıklar?
4. Aynı yola farklı HTTP metotları gönderildiğinde neden farklı işlemler seçilir?

Bu haftanın sonunda şunları yapabilmelisin:

- Bir HTTP isteğinde metodu, hedefi, başlıkları ve varsa gövdeyi ayırmak.
- Yol parametresi, sorgu parametresi ve istek gövdesinin rollerini karşılaştırmak.
- `GET`, `POST`, `PUT`, `PATCH` ve `DELETE` metotlarının amaçlarını açıklamak.
- Güvenli metot ile idempotent metot kavramlarını birbirine karıştırmamak.
- Bir HTTP yanıtında durum kodunu, başlıkları ve gövdeyi ayrı okumak.
- `200`, `201`, `204`, `400`, `404`, `405`, `409`, `415`, `422` ve `500` kodlarını bağlama göre yorumlamak.
- `Accept`, `Content-Type`, `Location` ve `Allow` başlıklarının görevlerini açıklamak.
- Postman’ın API veya sunucu olmadığını, istemci rolünde bir araç olduğunu göstermek.

## 2. HTTP neyi düzenler?

**HTTP**, istemci ile sunucu arasındaki istek–yanıt iletişiminin kurallarını tanımlayan uygulama katmanı protokolüdür. API, yazılımın sunduğu işlemler ve bunların kullanım arayüzüdür; HTTP ise web API’mizde bu işlemlere ait mesajları taşıyan iletişim düzenidir.

```text
API sözleşmesi: “Kitapları listelemek ve kitap eklemek için şu işlemler sunulur.”
HTTP mesajı:     “POST /api/books yoluna bu başlıklarla şu gövde gönderildi.”
```

API ile HTTP aynı kavram değildir. Her API ağ üzerinden HTTP kullanmak zorunda değildir. Bizim dersimizin ana uygulaması bir web API olduğu için HTTP üzerinde çalışır.

### 2.1. Her istek ayrı değerlendirilir

İstemci bir istek gönderir, sunucu bu isteği değerlendirir ve yanıt üretir. Sonra başka bir istek gelebilir:

```text
İstek 1: GET  /api/books       → Yanıt 1: 200 + kitap listesi
İstek 2: POST /api/books       → Yanıt 2: 201 + oluşturulan kitap
İstek 3: GET  /api/books/74    → Yanıt 3: 200 + 74 numaralı kitap
```

Birinci isteğin `200` olması, sonraki isteğin de başarılı olacağını garanti etmez. Her yanıt kendi isteğinin sonucunu anlatır.

## 3. HTTP isteğinin parçaları

Öğretim amacıyla sadeleştirilmiş bir istek:

```http
POST /api/books HTTP/1.1
Host: 127.0.0.1:8000
Accept: application/json
Content-Type: application/json

{
  "title": "HTTP'yi Anlamak",
  "author": {
    "first_name": "Selin",
    "last_name": "Aras"
  },
  "available": true,
  "tags": ["http", "web"],
  "rating": null
}
```

| Parça | Örnekteki değer | Görevi |
|---|---|---|
| Metot | `POST` | İstemcinin amaçladığı işlem türünü bildirir. |
| Hedef yol | `/api/books` | İşlemin yöneldiği kaynağı belirtir. |
| HTTP sürümü | `HTTP/1.1` | Mesajın kullandığı HTTP sürümünü gösterir. |
| Başlıklar | `Host`, `Accept`, `Content-Type` | Mesaj ve gövdenin işlenmesi için ek bilgi taşır. |
| Boş satır | Başlıklarla gövde arasında | Başlık bölümünün bittiğini gösterir. |
| Gövde | Kitap JSON’u | Sunucuya gönderilen asıl veriyi taşır. |

Postman ve HTTPX bazı başlıkları bizim yerimize ekleyebilir. Ekranda yalnızca yazdığımız alanları görmek, ağ üzerinden yalnızca bunların gönderildiği anlamına gelmez.

## 4. Girdi nerede taşınır?

Bir API işleminin girdileri aynı yere yazılmak zorunda değildir. Yer seçimi, girdinin işlemdeki anlamına göre yapılır.

### 4.1. Yol parametresi: hangi kaynak?

```http
GET /api/books/57
```

Buradaki `57`, istenen tek kitabı seçer. FastAPI tanımındaki karşılığı şöyledir:

```python
@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    ...
```

### 4.2. Sorgu parametresi: sonuç nasıl daraltılsın?

```http
GET /api/books?search=API&available=true
```

`search` ve `available`, kitap koleksiyonundan dönecek sonuçları süzer. `?` sorgu bölümünü başlatır, `&` parametreleri ayırır. Parametre adlarının anlamını HTTP değil, API sözleşmemiz belirler.

### 4.3. Gövde: işlenecek temsil nedir?

```http
POST /api/books
Content-Type: application/json

{"title": "HTTP'yi Anlamak", ...}
```

Yeni kitabın alanları gövdede taşınır. Kimliği bu örnekte istemci seçmez; sunucu oluşturur. Gövde kullanımı yalnızca `POST` metoduna özgü değildir, ancak `GET` istek gövdesi normal API tasarımında kullanılmamalıdır.

### 4.4. Aynı bilgi her yere yazılabilir mi?

Teknik olarak çok farklı tasarımlar yapılabilir; fakat anlaşılır bir sözleşmede girdinin yeri anlamıyla uyumlu olmalıdır:

| Soru | Uygun yer | Kitap örneği |
|---|---|---|
| Hangi tek kaynak? | Yol | `/api/books/57` |
| Koleksiyon nasıl süzülsün? | Sorgu | `?available=true` |
| Oluşturulacak kaydın alanları neler? | Gövde | Kitap JSON’u |
| Gövdenin biçimi nedir? | Başlık | `Content-Type: application/json` |

Bu bir doğa kanunu değil, okunabilir ve tutarlı API tasarımı için kullandığımız yaklaşımdır.

## 5. Metot ile yol birlikte işlemi seçer

Yalnızca `/api/books` yoluna bakmak yeterli değildir:

```text
GET  /api/books   → kitap listesini getir
POST /api/books   → yeni kitap oluştur
```

Yol aynıdır; metot değiştiği için amaçlanan işlem değişir. FastAPI’de iki ayrı dekoratör ve iki ayrı fonksiyon bulunur:

```python
@app.get("/api/books")
def get_books():
    ...


@app.post("/api/books")
def create_book():
    ...
```

Sunucuda yalnızca GET tanımlıyken aynı yola POST gönderilirse yol vardır, fakat o metot için işlem yoktur. Bu durumda `405 Method Not Allowed` beklenir.

## 6. Sık kullanılan HTTP metotları

| Metot | Temel amaç | Kitap örneği |
|---|---|---|
| `GET` | Kaynağın temsilini istemek | Kitapları veya bir kitabı getir. |
| `POST` | Hedef kaynağa veri göndererek işlem başlatmak; çoğu zaman yeni alt kaynak oluşturmak | Koleksiyona yeni kitap ekle. |
| `PUT` | Hedef kaynağın mevcut temsilini gönderilen içerikle değiştirmek | Kitabın bütün düzenlenebilir alanlarını yeni temsil ile değiştir. |
| `PATCH` | Kaynağa kısmi değişiklik uygulamak | Yalnızca `available` alanını değiştir. |
| `DELETE` | Hedef kaynağı silmek | Kimliği verilen kitabı sil. |

Bu eşleştirme yaygındır; “her POST mutlaka veritabanına kayıt ekler” gibi evrensel bir kural değildir. API, metodun o işlemdeki kesin anlamını belgelemelidir.

Bu hafta çalışan kodda `GET` ve `POST` kullanacağız. `PUT`, `PATCH` ve `DELETE` işlemlerini dördüncü haftada kitap kataloğunun gerçek güncelleme ve silme davranışlarıyla yazacağız.

### 6.1. CRUD ile HTTP metodu aynı şey değildir

CRUD, uygulama verisi üzerinde **Create, Read, Update, Delete** işlemlerini sınıflandırır. HTTP metotları ise isteklerin amaçlanan anlamını bildirir. Sık kullanılan eşleştirme şöyledir:

| CRUD | Yaygın HTTP metodu |
|---|---|
| Create | `POST` |
| Read | `GET` |
| Update | `PUT` veya `PATCH` |
| Delete | `DELETE` |

Bu tablo öğrenmeyi kolaylaştırır; HTTP’yi yalnızca veritabanı işlemlerine indirgememeliyiz.

## 7. Güvenli ve idempotent metotlar

### 7.1. Güvenli metot

İstemci, güvenli bir metotla sunucu durumunu değiştiren bir işlem istemez. `GET`, `HEAD` ve `OPTIONS` güvenli metotlardır. Sunucu günlük kaydı tutabilir; burada önemli olan istemcinin GET ile kitap oluşturma veya silme talep etmemesidir.

### 7.2. Idempotent metot

Aynı istek bir veya birden fazla kez uygulandığında sunucuda amaçlanan son etkinin aynı kalmasına **idempotent** denir.

```text
PUT /api/books/57   aynı tam temsil ile iki kez → hedefin son hâli aynı
DELETE /api/books/57 iki kez                   → hedef sonunda silinmiş
POST /api/books      aynı gövdeyle iki kez      → iki yeni kayıt oluşabilir
```

`GET`, `PUT` ve `DELETE` idempotent kabul edilir. `POST` genel olarak idempotent değildir. `DELETE` idempotent olduğu hâlde güvenli değildir; çünkü ilk başarılı istek kaynağı siler. Böylece **güvenli** ile **idempotent** kavramlarının aynı olmadığını görürüz.

İdempotentlik “iki isteğin durum kodu ve gövdesi mutlaka aynıdır” demek değildir. İlk DELETE `204`, ikincisi `404` dönebilir; amaçlanan son durumda kaynak yine yoktur.

## 8. HTTP yanıtının parçaları

Kitap oluşturma işleminin sadeleştirilmiş yanıtı:

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/books/74

{
  "id": 74,
  "title": "HTTP'yi Anlamak",
  "author": {
    "first_name": "Selin",
    "last_name": "Aras"
  },
  "available": true,
  "tags": ["http", "web"],
  "rating": null
}
```

| Parça | Ne anlatır? |
|---|---|
| `HTTP/1.1 201 Created` | Bu isteğin sonucunu bildirir. |
| `Content-Type` | Yanıt gövdesinin JSON olduğunu bildirir. |
| `Location` | Oluşturulan kaynağın yolunu gösterir. |
| Gövde | Oluşturulan kitabın sunucu tarafından üretilen kimlikle temsilini taşır. |

Durum kodu, başlık ve gövde birbirinin yerine geçmez. `201` işlemin türünü; `Location` yeni kaynağın yerini; JSON gövdesi kaynağın verisini açıklar.

## 9. Durum kodu sınıfları

İlk rakam, yanıtın geniş sınıfını gösterir:

| Aralık | Sınıf | Genel anlam |
|---:|---|---|
| `100–199` | Bilgilendirme | İletişimin ara durumu hakkında bilgi verir. |
| `200–299` | Başarı | İstek başarıyla tamamlanmıştır. |
| `300–399` | Yönlendirme | İstemcinin başka bir konum veya önbellek kuralıyla devam etmesini anlatır. |
| `400–499` | İstemci hatası | İstek hedef işleme uygun değildir veya gerekli koşulu sağlamaz. |
| `500–599` | Sunucu hatası | Sunucu isteği tamamlarken kendi tarafında sorun yaşamıştır. |

“4xx gördüm; istemci programında kesin yazılım hatası var” demek fazla geniştir. Örneğin kullanıcı var olmayan bir kitap kimliği seçtiğinde istemci kodu teknik olarak doğru çalışmış olabilir; sunucu yine `404` döndürür.

### 9.1. Bu derste kullanacağımız kodlar

| Kod | Adı | Kitap kataloğundaki örnek |
|---:|---|---|
| `200` | OK | Liste veya tek kitap başarıyla döndü. |
| `201` | Created | Yeni kitap oluşturuldu. |
| `204` | No Content | İşlem başarılı, dönecek gövde yok; silmede ileride kullanabiliriz. |
| `400` | Bad Request | Sunucu isteği kendi genel kurallarına göre geçersiz buldu. |
| `404` | Not Found | Kimliği verilen kitap bulunamadı. |
| `405` | Method Not Allowed | Yol var, gönderilen metot için işlem tanımlı değil. |
| `409` | Conflict | İstek mevcut durumla çatışıyor; örneğin benzersiz olması gereken değer zaten var. |
| `415` | Unsupported Media Type | Sunucu, gövdenin bildirilen biçimini desteklemiyor. |
| `422` | Unprocessable Content | Mesajın biçimi işlenebilir olsa da içerik beklenen yapıya veya türe uymuyor. |
| `500` | Internal Server Error | Sunucu kodunda beklenmeyen hata oluştu. |

Aynı sorun her API’de mutlaka aynı ayrıntı gövdesiyle dönmez. API sözleşmesi durum kodunun yanında hata gövdesinin alanlarını da tanımlamalıdır.

Güncel HTTP adlandırmasında `422` için **Unprocessable Content** kullanılır. Bazı sunucular ve araçlar geçmişteki **Unprocessable Entity** adını gösterebilir; karar verirken üç basamaklı durum kodunu esas alırız.

### 9.2. `400`, `415` ve `422` neden karışır?

- `400`, isteğin genel olarak hatalı olduğunu bildiren geniş bir koddur.
- `415`, sunucunun gövde için bildirilen medya türünü desteklemediğini anlatır.
- `422`, içerik türü anlaşılmış olsa bile verinin beklenen yapı veya değerlere dönüştürülemediği durumlarda kullanılabilir.

FastAPI, Pydantic modeline uymayan istek gövdelerinde varsayılan olarak ayrıntılı `422` yanıtı üretir. Beşinci haftada hangi doğrulama hatasına hangi yanıtı vereceğimizi daha ayrıntılı tasarlayacağız.

## 10. Başlıklar: mesaj hakkındaki bilgi

HTTP başlıkları ad–değer çiftleridir. Alan adları büyük/küçük harfe duyarlı değildir; araçlar görünümü değiştirebilir.

### 10.1. `Accept`

```http
Accept: application/json
```

İstemci, kabul ettiği yanıt biçimini bildirir. Bu bir talep veya tercih bilgisidir. Sunucunun içerik uzlaşmasını destekleyip desteklemediğini sözleşmeden öğreniriz. FastAPI örneğimiz `Accept: text/plain` gönderilse bile varsayılan olarak JSON dönebilir; `Accept` tek başına sunucuya zorunlu biçim değişikliği yaptırmaz.

### 10.2. `Content-Type`

```http
Content-Type: application/json
```

Bu başlık, bulunduğu mesajın gövde biçimini bildirir:

- İstekteyse istemci gönderdiği gövdenin türünü açıklar.
- Yanıttaysa sunucu döndürdüğü gövdenin türünü açıklar.

`Content-Type: application/json` işlemin başarılı olduğunu göstermez. JSON biçiminde bir hata gövdesi de gelebilir.

### 10.3. `Location`

```http
Location: /api/books/74
```

`201 Created` yanıtında yeni kaynağın nerede bulunduğunu göstermek için kullanılabilir. İstemci daha sonra bu yolu GET isteğinde kullanabilir.

### 10.4. `Allow`

```http
Allow: GET
```

`405 Method Not Allowed` yanıtında hedef kaynağın desteklediği metotları bildirmek için kullanılır. Değer sunucu çatısının yönlendirme davranışına göre görülebilir.

## 11. Gövde ile JSON aynı şey değildir

**Gövde**, HTTP mesajının veri taşıyan bölümüdür. **JSON** ise gövdede kullanılabilecek veri biçimlerinden biridir. Bir gövde metin, HTML, XML, görsel baytları veya başka bir biçim taşıyabilir.

```text
HTTP gövdesi  → mesajın bölümü
JSON          → o bölümde kullanılabilen veri biçimi
```

Birinci haftada çoğunlukla yanıt gövdesini okuduk. İkinci haftada istemci de POST isteğinin gövdesinde JSON gönderecek.

## 12. FastAPI isteği nasıl ilgili koda ulaştırır?

Sadeleştirilmiş süreç şöyledir:

```text
1. Uvicorn bağlantıyı kabul eder.
2. FastAPI metot ve yolu birlikte eşleştirir.
3. Yol ve sorgu değerlerini tanımlanan Python türlerine dönüştürür.
4. Varsa gövdeyi Content-Type bilgisine göre okur.
5. JSON verisini beklenen modele dönüştürür ve doğrular.
6. İlgili Python fonksiyonunu çalıştırır.
7. Dönüş değerini yanıt gövdesine serileştirir.
8. Durum kodu ve başlıklarla HTTP yanıtını gönderir.
```

Hata hangi aşamada oluşursa gözlediğimiz yanıt da değişir:

- Metot+yol işlemi yoksa `404` veya `405`.
- `book_id: int` dönüşümü yapılamazsa `422`.
- JSON yazımı veya model alanları uygun değilse `422`.
- Fonksiyon içinde kitap bulunamazsa bizim kodumuz `404` üretir.
- Fonksiyonda yakalanmayan beklenmedik hata oluşursa `500` görülebilir.

## 13. Postman bu ilişkide ne yapar?

Postman bir API oluşturmaz ve sunucunun yerine geçmez. İstemci rolünde istek hazırlayıp gönderir ve yanıtı bölümleriyle gösterir.

```text
Postman  ── HTTP isteği ──► FastAPI uygulaması
Postman  ◄─ HTTP yanıtı ─── FastAPI uygulaması
```

Birinci haftadaki `client.py` de aynı istemci rolündeydi. Aralarındaki fark amaç ve kullanım biçimidir:

| İstemci | Güçlü olduğu kullanım |
|---|---|
| Postman | Metodu, yolu, parametreyi, başlığı ve gövdeyi elle değiştirerek keşfetmek. |
| HTTPX kullanan Python dosyası | İsteği program akışının parçası olarak tekrar üretmek ve yanıtı kodla işlemek. |

Postman’da **Params**, **Headers** ve **Body** sekmelerinin bulunması, bunların HTTP’de aynı yer olduğu anlamına gelmez. Araç yalnızca ayrı mesaj parçalarını düzenlemeyi kolaylaştırır.

## 14. Kitap ekleme işleminin uçtan uca yolculuğu

Kullanıcı veya geliştirici yeni kitabın bilgilerini hazırlar:

```json
{
  "title": "HTTP'yi Anlamak",
  "author": {
    "first_name": "Selin",
    "last_name": "Aras"
  },
  "available": true,
  "tags": ["http", "web"],
  "rating": null
}
```

Ardından süreç şöyle ilerler:

1. İstemci `POST /api/books` isteğini hazırlar.
2. `Content-Type: application/json`, gönderilen gövdenin biçimini bildirir.
3. FastAPI metot ve yolu `create_book` işlemine eşler.
4. İstek gövdesi JSON’dan Python/Pydantic verisine dönüştürülür.
5. Sunucu yeni kimliği üretir ve kitabı bellekteki listeye ekler.
6. Sunucu `201 Created`, `Location` başlığı ve kitap gövdesi döndürür.
7. İstemci durum kodunu, başlıkları ve gövdeyi ayrı ayrı yorumlar.

Bu örnekte kitap sunucu belleğinde tutulur. Uvicorn yeniden başlatıldığında eklenen kayıt kaybolur. Bu, POST isteğinin başarısız olduğu anlamına gelmez; kalıcılığın henüz uygulanmadığını gösterir.

## 15. Sık karıştırılan noktalar

| Yanılgı | Doğru açıklama |
|---|---|
| “URL işlemi tek başına belirler.” | FastAPI’de işlem seçilirken metot ve yol birlikte değerlendirilir. `GET /api/books` ile `POST /api/books` farklı işlemlerdir. |
| “POST, GET’in daha güçlü hâlidir.” | Metotlar güç sırası oluşturmaz; farklı amaçlanan anlamları vardır. |
| “POST gönderirsem kitap kesin eklenir.” | Yol tanımlı olmayabilir, gövde geçersiz olabilir veya sunucu işlemi reddedebilir. Yanıtı incelemek gerekir. |
| “`Content-Type` hangi yanıtı istediğimi söyler.” | İstekte `Content-Type`, gönderdiğin gövdenin biçimini; `Accept`, kabul ettiğin yanıt biçimini bildirir. |
| “201 geldiyse yeni kimliği istemci seçmiştir.” | Bu örnekte kimliği sunucu üretir; yanıt gövdesi ve `Location` ile istemciye bildirir. |
| “4xx, sunucu hiç çalışmadı demektir.” | 4xx bir HTTP yanıtıdır. Sunucu isteği almış ve belirli nedenle karşılayamamıştır. |
| “500 kullanıcının yanlış kitap adı yazmasıdır.” | 500 sunucu tarafındaki beklenmedik tamamlanma sorunlarını anlatır; geçersiz kullanıcı girdisi için 4xx sınıfı daha uygundur. |
| “Aynı POST’u iki kez göndermek tek kitap oluşturur.” | POST genel olarak idempotent değildir; örneğimiz her başarılı tekrarda yeni kimlikle kitap oluşturur. |
| “Gövde demek JSON demektir.” | Gövde HTTP mesajının bölümüdür; JSON bu bölümde taşınabilecek biçimlerden biridir. |
| “Postman isteği başarılı yapar.” | Postman yalnızca istemcidir. Sonucu sunucunun sözleşmesi, istek ve mevcut durum belirler. |

## 16. Kendini değerlendir

1. `POST /api/books` gösteriminde metot ve yol ayrı ayrı neyi anlatır?
2. Aynı `/api/books` yoluna GET ve POST gönderildiğinde neden farklı fonksiyonlar çalışabilir?
3. Yol parametresi, sorgu parametresi ve gövde için birer kitap örneği ver.
4. `Accept` ile `Content-Type` arasındaki fark nedir?
5. `201` ile `200` arasındaki anlam farkını kitap örneğiyle açıkla.
6. `405` ile `404` arasındaki fark nedir?
7. `422` hangi aşamada, `500` hangi aşamada oluşabilir?
8. Güvenli metot ve idempotent metot aynı şey midir?
9. DELETE neden idempotent olabildiği hâlde güvenli değildir?
10. Aynı POST gövdesini iki kez göndermek neden iki kitap oluşturabilir?
11. `Location: /api/books/74` başlığı ne anlatır?
12. Postman ile `client.py` aynı rolü hangi açıdan paylaşır?
13. POST başarılı olduktan sonra sunucuyu yeniden başlatınca kitap neden kaybolabilir?
14. `Content-Type: application/json` neden işlemin başarılı olduğunu kanıtlamaz?
15. Kitabın kimliğini neden istek gövdesine koymadığımızı bu örneğin sözleşmesine göre açıkla.

## 17. Gerekçeli cevaplar

**1.** `POST` istemcinin hedefe veri göndererek bir işlem başlatma niyetini, `/api/books` kitap koleksiyonu kaynağını belirtir.

**2.** Sunucu yönlendirmeyi metot ve yol çiftiyle yapar. Aynı yol için GET listeleme, POST oluşturma işlemine bağlanabilir.

**3.** Yol: `/api/books/57`; sorgu: `?available=true`; gövde: oluşturulacak kitabın `title`, `author`, `tags` gibi alanları.

**4.** `Accept` istemcinin kabul ettiği yanıt biçimini, `Content-Type` bulunduğu mesajın gövde biçimini bildirir.

**5.** `200`, mevcut kitap listesinin başarıyla okunmasında; `201`, yeni kitap kaynağının oluşturulmasında kullanılır.

**6.** `404` hedef yolun veya kaynağın bulunmadığını; `405` yol bulunduğu hâlde o metot için işlem tanımlanmadığını anlatır.

**7.** Gövde modele dönüştürülemezse `422`; fonksiyon içinde beklenmedik ve yakalanmayan hata oluşursa `500` görülebilir.

**8.** Hayır. Güvenli metot sunucu durumunu değiştiren talep taşımaz. Idempotent metot tekrarlandığında amaçlanan son etkiyi değiştirmez.

**9.** DELETE kaynağı değiştirir, dolayısıyla güvenli değildir. Aynı silme isteği tekrarlandığında hedef sonunda yine silinmiş kalır.

**10.** POST genel olarak idempotent değildir. Sunucu her başarılı istekte yeni kimlik üretip yeni kayıt ekleyebilir.

**11.** Oluşturulan yeni kaynağın erişim yolunu bildirir.

**12.** İkisi de HTTP isteğini başlatan ve yanıtı alan istemci yazılımlardır. Biri elle, diğeri kodla çalıştırılır.

**13.** Bu aşamada veri yalnızca Python listesindedir. Uygulama süreci yeniden başlayınca liste kaynak kodundaki başlangıç değerleriyle kurulur.

**14.** Başlık yalnızca gövdenin JSON olduğunu bildirir. Hata gövdesi de JSON olabilir.

**15.** Bu sözleşmede istemci yeni kitabın verisini gönderir, benzersiz kimliği sunucu üretir. Böylece kimlik üretme sorumluluğu tek tarafta kalır.

## 18. Üç ders saati için anlatım akışı

| Blok | Süre | İçerik ve etkinlik |
|---|---:|---|
| 1. ders | 0–10 dk | Birinci haftanın son GET isteğini öğrencinin kendi cümlesiyle anlatması. |
| 1. ders | 10–25 dk | HTTP isteğinin metot, hedef, başlık ve gövde parçaları. |
| 1. ders | 25–35 dk | Yol, sorgu ve gövde karşılaştırması. |
| 1. ders | 35–45 dk | Aynı yolda GET ile POST’un neden farklı işlem olduğu. |
| 2. ders | 0–20 dk | GET, POST, PUT, PATCH ve DELETE anlamları. |
| 2. ders | 20–35 dk | Güvenli ve idempotent metot tartışması. |
| 2. ders | 35–45 dk | Aynı POST’un iki kez gönderilmesi düşünce deneyi. |
| 3. ders | 0–15 dk | Yanıt satırı, başlıklar, gövde ve durum kodu sınıfları. |
| 3. ders | 15–30 dk | `200`, `201`, `404`, `405`, `422`, `500` karşılaştırması. |
| 3. ders | 30–40 dk | `Accept`, `Content-Type`, `Location`, `Allow`. |
| 3. ders | 40–45 dk | Kitap POST akışını yedi adımda sözlü anlatma. |

## 19. Kaynaklar

- [MDN — HTTP’ye genel bakış](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [MDN — HTTP istek metotları](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)
- [MDN — Güvenli HTTP metotları](https://developer.mozilla.org/en-US/docs/Glossary/Safe/HTTP)
- [MDN — Idempotent HTTP metotları](https://developer.mozilla.org/en-US/docs/Glossary/Idempotent)
- [MDN — HTTP yanıt durum kodları](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)
- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [FastAPI — Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI — Response Status Code](https://fastapi.tiangolo.com/tutorial/response-status-code/)
- [FastAPI — Response Headers](https://fastapi.tiangolo.com/advanced/response-headers/)
- [Postman — İstek parametreleri ve gövde](https://learning.postman.com/docs/send-requests/create-requests/parameters/)
- [Postman — İstek başlıkları](https://learning.postman.com/docs/use/send-requests/create-requests/headers/)

Bu kaynaklar teknik başvuru içindir. İkinci hafta için ana çalışma sırası bu not ve ardından uygulama föyüdür.

# Ek Not — SOAP ve GraphQL Mesajları Nasıl Okunur?

Föyün Deney 7'sinde "42 numaralı kitabın adını ve yazarını getir" isteğini REST, SOAP ve GraphQL ile yazan kodları yan yana gördük. Bu notta SOAP ve GraphQL mesajlarını parça parça okuyoruz. Föydeki gibi burada da üç yaklaşımın yolu `/books`; gerçek uygulamalarda bu tek yola genellikle `/BookService` ya da `/graphql` gibi adlar verilir.

> **Not:** Buradaki mesajlar örnektir. Derste SOAP ya da GraphQL sunucusu kurmuyoruz; amaç mesajların yapısını tanımaktır.

---

## 1. SOAP isteği

```http
POST /books HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: text/xml; charset=utf-8
SOAPAction: "GetBook"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetBook>
      <id>42</id>
    </GetBook>
  </soap:Body>
</soap:Envelope>
```

| Parça | Anlamı |
|---|---|
| `POST /books` | SOAP'ta bütün istekler aynı yola, POST ile gönderilir. Yol hangi işlemin istendiğini söylemez. |
| `Host: 127.0.0.1:8000` | Sunucunun adresi. Her HTTP isteğinde bulunur. |
| `Content-Type: text/xml` | Gövdenin XML olduğunu bildirir. |
| `SOAPAction: "GetBook"` | İstenen işlemin adı. SOAP'ın bu örnekteki 1.1 sürümünde işlem adı, mesajın içinin yanında bu başlıkta da yazılır. |
| `<?xml ... ?>` | Bunun bir XML belgesi olduğunu ve hangi karakter kodlamasıyla yazıldığını söyler. |
| `<soap:Envelope>` | **Zarf.** Mesajın tamamını sarar. `xmlns:soap="..."` kısmı, mesajın hangi SOAP kurallarına göre yazıldığını gösteren bir addır; bir web sayfası değildir. |
| `<soap:Body>` | Mesajın asıl içeriği bu öğenin içindedir. |
| `<GetBook>` | İstenen işlem: "kitabı getir". REST'te bunu HTTP metodu ve yol söylüyordu (`GET /books/42`). |
| `<id>42</id>` | İşlemin parametresi: kitabın kimliği. REST'te bu bilgi yoldaydı. |

REST'te `GET /books/42` yazdığımız tek satırın karşılığı, SOAP'ta XML ile yazılmış bir mesajdır.

## 2. SOAP yanıtı

```xml
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetBookResponse>
      <book>
        <id>42</id>
        <title>API Yolculuğu</title>
        <author>
          <first_name>Deniz</first_name>
          <last_name>Kaya</last_name>
        </author>
      </book>
    </GetBookResponse>
  </soap:Body>
</soap:Envelope>
```

| Parça | Anlamı |
|---|---|
| `<soap:Envelope>`, `<soap:Body>` | Yanıt da aynı zarfın içinde gelir. |
| `<GetBookResponse>` | `GetBook` işleminin yanıtı olduğunu söyler. |
| `<book>` ve içindekiler | Kitabın bilgileri. Her alan bir XML öğesidir; yazarın bilgileri `<author>` öğesinin içinde durur. |

XML'de değerlerin türü yazılıştan anlaşılmaz: `<id>42</id>` içindeki `42` yalnızca bir yazıdır. Sayı olduğunu, veriyi okuyan program bilir. Bu farkı Hafta 2'nin [veri biçimleri notunda](../Week_02/04_Supplement_Data_Formats.md) görmüştük.

Bir hata olduğunda SOAP yanıtının gövdesinde `<soap:Fault>` adlı bir öğe bulunur; hatanın açıklaması bu öğenin içinde yazar. SOAP 1.1'de böyle bir yanıtın HTTP durum kodu `500` olur.

SOAP servisleri, hangi işlemleri sunduklarını ve hangi parametreleri beklediklerini genellikle **WSDL** adlı bir XML belgesinde tanımlar. İstemciyi yazan kişi işlem adlarını bu belgeden öğrenir.

---

## 3. GraphQL isteği

```http
POST /books HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{"query": "{ book(id: 42) { title author { first_name last_name } } }"}
```

İstek bir JSON gövdesidir. Asıl içerik, `query` alanındaki metindir. Bu metne **sorgu** denir. Tek satırda okunması zor olduğu için aynı sorguyu satırlara bölerek yazalım:

```graphql
{
  book(id: 42) {
    title
    author {
      first_name
      last_name
    }
  }
}
```

| Parça | Anlamı |
|---|---|
| `book(id: 42)` | Hangi veri isteniyor: kimliği 42 olan kitap. Parantez içindeki `id: 42`, isteğin parametresidir. |
| `{ title ... }` | Kitabın **hangi alanlarının** istendiği. Burada yalnızca `title` ve `author` istendi. |
| `author { first_name last_name }` | `author` bir nesne olduğu için onun da hangi alanlarının istendiği yazılır. |

GraphQL sunucusu, hangi verilerin ve alanların istenebileceğini bir **şemada** tanımlar. İstemci yalnızca şemada bulunan alanları isteyebilir.

## 4. GraphQL yanıtı

```json
{"data": {"book": {"title": "API Yolculuğu", "author": {"first_name": "Deniz", "last_name": "Kaya"}}}}
```

| Parça | Anlamı |
|---|---|
| `"data"` | İstenen veriler bu alanın içinde gelir. |
| `"book": {...}` | Sorgudaki `book` kısmının cevabı. |
| `"title"`, `"author"` | Yalnızca sorguda istenen alanlar. `tags`, `rating` gibi istenmeyen alanlar gelmez. |

Yanıtın biçimi sorgunun biçimini izler: Sorguda `book` içinde `title` ve `author` istendiyse, yanıtta da `book` içinde `title` ve `author` bulunur.

Bir hata olduğunda yanıtta `"errors"` adlı bir alan bulunur ve hata orada açıklanır. Birçok GraphQL sunucusu bu durumda da `200` durum kodu döndürür. Yani REST'te durum koduna bakarak anladığımız sonucu, GraphQL'de yanıtın gövdesindeki `errors` alanına bakarak anlarız.

---

## 5. Aynı bilginin üç yaklaşımda yeri

| Bilgi | REST | SOAP | GraphQL |
|---|---|---|---|
| İstenen işlem | HTTP metodu: `GET` | `<GetBook>` öğesi ve `SOAPAction` başlığı | Sorgudaki `book` |
| Kitabın kimliği | Yolda: `/books/42` | `<id>42</id>` | Sorgudaki `id: 42` |
| İstenen alanlar | Seçilemez; sunucu belirler | Seçilemez; sunucu belirler | Sorguda istemci seçer |
| Sonucun başarılı olup olmadığı | Durum kodu | Gövdedeki `<soap:Fault>` öğesi (durum kodu `500`) | Gövdedeki `"errors"` alanı (durum kodu çoğu zaman `200`) |

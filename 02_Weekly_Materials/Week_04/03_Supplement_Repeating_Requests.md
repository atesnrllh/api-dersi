# Ek Not — Aynı İsteği Tekrar Göndermek

Föyün Deney 1'inde aynı `DELETE` isteğini iki kez gönderdik. İlkinde `204`, ikincisinde `404` geldi; ama 57 numaralı kitap iki seferden sonra da yoktu. Bu notta aynı denemeyi beş HTTP metodunun hepsiyle yapıyoruz.

---

## 1. Beş isteği ikişer kez göndermek

Föyün Deney 4 sonundaki sunucuyu yeniden başlattık ve her isteği arka arkaya iki kez gönderdik:

| İstek | 1. gönderim | 2. gönderim | İkinci gönderim veriyi değiştirdi mi? |
|---|---|---|---|
| `GET /books/42` | `200` | `200` | Hayır. Kitap sayısı 3 kaldı. |
| `POST /books` (aynı kitap) | `201`, kimlik `74` | `201`, kimlik `75` | **Evet.** Aynı kitap ikinci kez eklendi; kitap sayısı 4'ten 5'e çıktı. |
| `PUT /books/73` (aynı gövde) | `200` | `200`, aynı yanıt | Hayır. Kitap zaten gönderilen hâldeydi. |
| `PATCH /books/42` `{"available": false}` | `200` | `200`, aynı yanıt | Hayır. `available` zaten `false` idi. |
| `DELETE /books/57` | `204` | `404` | Hayır. Kitap zaten silinmişti; kitap sayısı 4 kaldı. |

Burada iki ayrı soruya bakıyoruz, karıştırmayalım:

- **Yanıt aynı mı?** `DELETE` için hayır: önce `204`, sonra `404`.
- **Sunucudaki veri aynı mı?** `DELETE` için evet: İki istekten sonra da kitap yok.

Bu notta önemli olan ikinci soru.

---

## 2. HTTP standardı ne söylüyor?

Bir isteği birkaç kez göndermek, sunucudaki veriyi bir kez göndermekle aynı hâlde bırakıyorsa, HTTP standardı bu isteğe **idempotent** der. Türkçede yerleşmiş bir karşılığı yok; "tekrarlanınca sonucu değişmeyen" diye düşünebilirsin.

| HTTP metodu | Veriyi değiştirir mi? | Standarda göre idempotent mi? |
|---|---|---|
| `GET` | Hayır (Hafta 3, Deney 4: güvenli) | Evet |
| `PUT` | Evet | Evet: Aynı kitabı iki kez göndermek, bir kez göndermekle aynı sonucu bırakır. |
| `DELETE` | Evet | Evet: Silinmiş kitap ikinci istekte de silinmiş kalır. |
| `POST` | Evet | **Hayır:** Her istek yeni bir kayıt oluşturabilir. |
| `PATCH` | Evet | **Garanti edilmez.** |

`PATCH` bizim denememizde tekrarlanınca bir şey değiştirmedi, çünkü `available` alanına aynı değeri yazdı. Ama bir `PATCH` isteği "stok sayısını bir artır" gibi bir iş de yapabilir; o zaman her tekrar veriyi yeniden değiştirir. Standart bu yüzden `PATCH` için bir şey garanti etmez; bu, API'yi yazan kişinin isteği nasıl tasarladığına bağlıdır.

---

## 3. Bu neden önemli?

İstemci bir istek gönderdiğinde bazen yanıt gelmez: Bağlantı kopmuş, sunucu geç kalmış olabilir. İstemci isteğin sunucuya ulaşıp ulaşmadığını bilemez.

- İstek `GET`, `PUT` ya da `DELETE` ise istemci aynı isteği gönül rahatlığıyla tekrar gönderebilir. İstek ilk seferde ulaşmış olsa bile tekrar veriyi bozmaz.
- İstek `POST` ise tekrar göndermek, Hafta 2'de gördüğümüz gibi aynı kitabın iki kez eklenmesine yol açabilir.

Hafta 3'te tarayıcıların GET isteğini kendiliğinden tekrar gönderebildiğini görmüştük. Tarayıcılar ve öteki programlar, metotların bu özelliklerine güvenerek davranır; bu yüzden her işi kendi anlamına uygun HTTP metoduyla yazmak önemlidir.

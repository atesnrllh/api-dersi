# Ek Not — REST'in Altı Kısıtı

Föyün 0. bölümünde, günlük kullanımda "REST API" denince kastedilen beş maddeyi gördük. Bu notta REST'in asıl tanımına bakıyoruz.

Roy Fielding, 2000 yılındaki doktora tezinde REST'i **altı kısıtla** tanımladı. Kısıt (constraint), bir sistemi REST yapan şarttır. Föydeki "kural" sözü ile aynı anlamdadır.

---

## 1. Altı kısıt

| # | Kısıt | Ne demek? | Bizim derste |
|---|---|---|---|
| 1 | İstemci–sunucu | İstek gönderen ile cevap veren ayrı programlardır. | `client.py` ve `server.py`, ilk haftadan beri |
| 2 | Durumsuzluk (stateless) | Sunucu önceki isteği hatırlamaz; her istek kendi başına yeterlidir. | Föyün 0. bölümü, 4. madde |
| 3 | Önbelleğe alınabilirlik (cache) | Yanıt, saklanıp tekrar kullanılıp kullanılamayacağını söyleyebilir. | Henüz kullanmıyoruz. |
| 4 | Tek biçimli arayüz (uniform interface) | Her kaynakla aynı biçimde konuşulur. Dört alt maddesi var (2. bölüm). | Föyün 0. bölümü, 1., 2. ve 3. madde |
| 5 | Katmanlı sistem (layered system) | İstemci ile sunucu arasında başka sunucular olabilir; istemcinin bunu bilmesi gerekmez. | Kullanmıyoruz. |
| 6 | İstek üzerine kod (code on demand) | Sunucu istemciye çalıştırması için kod gönderebilir. **İsteğe bağlı** olan tek kısıt budur. | Kullanmıyoruz. |

**3. kısıt için örnek:** Sunucu yanıta `Cache-Control: max-age=60` başlığını eklerse, "bu yanıtı 60 saniye boyunca yeniden kullanabilirsin" demiş olur. Tarayıcı bu sürede aynı GET isteğini sunucuya göndermeden saklanan yanıtı gösterebilir. Bu, GET'in veriyi değiştirmemesi sayesinde mümkündür (föyün Deney 4'ü).

**5. kısıt için örnek:** Büyük sitelerde istek önce aradaki bir sunucuya gider; o sunucu isteği arkadaki sunuculardan birine iletir. İstemci yine tek bir adrese istek gönderir ve aradaki sunucuyu görmez.

**6. kısıt için örnek:** Bir web sayfası açılırken sunucu tarayıcıya JavaScript kodu gönderir; tarayıcı bu kodu çalıştırır.

---

## 2. Tek biçimli arayüzün dört alt maddesi

| Alt madde | Ne demek? | Bizim derste |
|---|---|---|
| Kaynakların adlandırılması | Her kaynağın kendi adresi vardır. | `http://127.0.0.1:8000/books/42` |
| Temsiller üzerinden işlem | İstemci kaynağın kendisini değil, bir temsilini alır ve gönderir. | Kitap sunucuda Python sözlüğüdür; istemciye JSON hâli gider. |
| Kendini anlatan mesajlar | Mesaj nasıl okunacağını kendisi söyler. | HTTP metodu (`GET`, `POST`) ve `Content-Type: application/json` başlığı |
| Bağlantılarla ilerleme (HATEOAS) | Yanıt, istemcinin sonra gidebileceği adresleri de içerir. | Kullanmıyoruz. |

**HATEOAS için örnek:** Bizim API'miz 42 numaralı kitabı yalnızca kitabın bilgileriyle döndürüyor. HATEOAS'a uyan bir API, yanıtın içine kitabın yorumlarının yolunu da koyardı:

```json
{
  "id": 42,
  "title": "API Yolculuğu",
  "links": {
    "reviews": "/books/42/reviews"
  }
}
```

Bu örnekteki `links` alanı **örnektir**; bizim sunucumuz böyle bir alan göndermiyor. İstemci yorumların yolunu tahmin etmek yerine yanıttan okur. Hafta 2'deki `Location` başlığı da benzer bir iş görüyordu: Yeni kitabın yolunu sunucu söylüyordu.

---

## 3. Föydeki beş madde ile altı kısıt

| Föydeki madde | Fielding'in tanımında karşılığı |
|---|---|
| 1. Her kaynağın bir yolu vardır | 4. kısıt: Kaynakların adlandırılması |
| 2. Ne yapılacağını HTTP metodu söyler | 4. kısıt: Kendini anlatan mesajlar |
| 3. Sunucu kaynağın temsilini gönderir | 4. kısıt: Temsiller üzerinden işlem |
| 4. Her istek kendi başına yeterlidir | 2. kısıt: Durumsuzluk |
| 5. Sonucu durum kodu söyler | Karşılığı yok. Durum kodları HTTP'nin özelliğidir; REST API'leri onları kullanır. |

Kendine "REST API" diyen API'lerin çoğu, bizimki de dahil, HATEOAS'u uygulamaz. Fielding buna itiraz eder: Ona göre bu API'ler tam anlamıyla REST değildir. Günlük kullanımda ise "REST API" denince genellikle şunlar kastedilir: kaynaklar ve yolları, HTTP metotları, JSON temsiller, durumsuz istekler ve HTTP'nin durum kodları. Föyün 0. bölümündeki beş madde bu günlük kullanımı özetler.

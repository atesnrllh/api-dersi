# Ek Not — Bu Haftanın Açıklarının Adları

Föyde üç açık bulduk ve düzelttik. Üçü de API güvenliğinde iyi bilinen açıklar. **OWASP** (Open Worldwide Application Security Project), web uygulamalarının güvenliği üzerine çalışan, kâr amacı gütmeyen bir topluluk. API'ler için en sık görülen on güvenlik riskini bir listede topluyor: **OWASP API Security Top 10**. Bu not, föydeki açıkları o listedeki adlarıyla eşleştiriyor ve föyde ele almadığımız birkaç riske kısaca bakıyor.

---

## 1. Föyde bulduğumuz üç açık

| Föyde | OWASP API Security Top 10 (2023) | Kısaca |
|---|---|---|
| Deney 3: Can, Ece'nin yorumunu değiştirebiliyordu. | **API1: Broken Object Level Authorization** (nesne düzeyinde yetki hatası) | Kullanıcı bir işlemi yapabiliyor, ama işlem **hangi kayıt** üzerinde yapıldığına bakmıyor. Adresteki kimliği değiştirmek, başkasının kaydına ulaşmak için yetiyor. |
| Deney 4: Kullanıcı listesinde parola özetleri vardı. | **API3: Broken Object Property Level Authorization** (alan düzeyinde yetki hatası) | Kullanıcı kaydı görebiliyor, ama kaydın **bütün alanlarını** görmemeli. Aynı risk, istemcinin değiştirmemesi gereken bir alanı gönderebilmesini de kapsar. |
| Deney 1 ve 2: Okurlar ve tokensiz istekler kitapları silebiliyordu. | **API5: Broken Function Level Authorization** (işlem düzeyinde yetki hatası) | Kullanıcı, rolünün yapmaması gereken **bir işlemi** yapabiliyor: Okurun kitap silmesi gibi. |

Listenin ilk sırasındaki açık, Deney 3'teki: API'lerde en sık bulunan ve en kolay sömürülen açık bu.

---

## 2. Alan düzeyinde yetki: istek tarafı

Deney 4'te yanıtın fazla alan taşımasını gördük. Aynı risk istekte de var. Hafta 9'da `reader` alanını `ReviewCreate` modelinden çıkarmıştık: İstemci okurun adını gönderebilseydi, başkasının adıyla yorum yazabilirdi. Hafta 10'da `User` tablosuna `is_librarian` alanını ekledik. Bir gün kullanıcıların kendi bilgilerini değiştirebildiği bir işlem yazarsak ve istek modelinde `is_librarian` olursa, her kullanıcı kendini kütüphaneci yapabilir.

İki yönde de yol aynı: İstek modeli, istemcinin **değiştirebileceği** alanları; yanıt modeli, istemcinin **görebileceği** alanları listeler. Tablo modelini doğrudan istek ya da yanıt modeli olarak kullanmak, bu iki listeyi tablonun bütün alanlarına eşitler.

---

## 3. Föyde ele almadığımız birkaç risk

| Risk | Kataloğumuzda nasıl görünürdü? |
|---|---|
| **API2: Broken Authentication** (kimlik doğrulama hatası) | Hafta 9'daki tokenlerin süresi dolmuyor; 6.3 alıştırması bunu düzeltiyor. Giriş işlemi, aynı kullanıcı adı için arka arkaya yapılan yanlış denemeleri sınırlamıyor. |
| **API4: Unrestricted Resource Consumption** (sınırsız kaynak kullanımı) | `GET /books` bütün kitapları tek yanıtta döndürüyor. Katalogda bir milyon kitap olsaydı, tek bir istek sunucuyu uzun süre meşgul ederdi. Gerçek API'ler listeleri sayfalara böler ve bir istemcinin belli bir sürede gönderebileceği istek sayısını sınırlar. |

Listenin geri kalanını [OWASP'ın sayfasında](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) bulabilirsin. Her riskin sayfasında bir saldırı örneği ve korunma yolları var.

---

## 4. `404` mü, `403` mü?

Deney 3'te Can, Ece'nin yorumunu değiştirmek istediğinde `403` aldı. Bu yanıt Can'e bir bilgi veriyor: "1 numaralı yorum var, ama senin değil." Bazı API'ler, kullanıcının erişemediği kayıtlar için de `404` döndürür: "Senin için böyle bir kayıt yok." Böylece istemci, başkalarına ait kayıtların var olup olmadığını öğrenemez.

Bizim kataloğumuzda yorumlar zaten herkese açık (`GET /books/42/reviews`); bir yorumun var olduğunu gizlemenin anlamı yok, bu yüzden daha açıklayıcı olan `403` yanıtını seçtik. Kayıtların kendisi gizli olsaydı, örneğin kullanıcıların özel notları, `404` daha doğru bir seçim olurdu.

# Ek Not — 400 mü, 422 mi?

Föyün Deney 1'inde sunucumuz hatalı değerleri `422` ile reddetti. Hafta 1'deki [URL ek notunda](../Week_01/03_Supplement_URL.md) ise Open-Meteo, `latitude=100` değerini `400` ile reddetmişti. İki durum kodu da "hata istemcinin gönderdiği istekte" der. Bu notta aralarındaki farkı ve FastAPI'nin neden `422` seçtiğini görüyoruz.

---

## 1. İki durum kodunun anlamı

| Durum kodu | Adı | HTTP standardındaki anlamı |
|---|---|---|
| `400` | Bad Request | İstek bozuk ya da sunucunun işleyemeyeceği biçimde. Genel bir "istemci hatası" kodu. |
| `422` | Unprocessable Entity | İsteğin biçimi doğru, sunucu onu okuyabildi; ama içindeki değerler işlenemiyor. |

Yani `422`, `400` kodunun daha belirli bir hâlidir: "Mesajını okuyabildim, ama içindekiler kurallarıma uymuyor."

`422` kodunun adı HTTP standardının güncel sürümünde (RFC 9110) **Unprocessable Content** olarak değişti; eski adı **Unprocessable Entity**. İkisi aynı kodu anlatır. Sunucu terminalinde hangisini göreceğin Python sürümüne bağlı: Python 3.12 ve öncesi eski adı, Python 3.13 ve sonrası yeni adı yazar. Ders materyallerinde, kendi ortamımızda görünen eski adı kullanıyoruz.

---

## 2. FastAPI bozuk JSON için de 422 döndürür

Gövdesi yarım kalmış, yani JSON olarak okunamayan bir istek gönderdik:

```bash
curl -s -X POST http://127.0.0.1:8000/books -H "Content-Type: application/json" -d '{"title": "T",'
```

```text
{"detail":[{"type":"json_invalid","loc":["body",14],"msg":"JSON decode error","input":{},"ctx":{"error":"Expecting property name enclosed in double quotes"}}]}
```

Durum kodu yine `422`. HTTP standardına göre bu istek için `400` daha uygun olurdu, çünkü sunucu gövdeyi okuyamadı bile. FastAPI ise bütün doğrulama hatalarını tek biçimde bildirmeyi seçiyor: Hata ister bozuk JSON'da ister bir alanın değerinde olsun, yanıt `422` ve aynı `detail` listesi. `loc` alanındaki `14`, gövdede hatanın bulunduğu karakterin sırası.

---

## 3. Hangisini kullanmalı?

Bu bir tasarım kararı; standart iki kodu da istemci hataları için ayırmış:

| API | Değer kurala uymayınca |
|---|---|
| Kitap kataloğu API'si (FastAPI) | `422` |
| Open-Meteo | `400`, gövdede `{"error": true, "reason": "..."}` |

İstemci için önemli olan iki şey var:

1. **Durum kodunun `4` ile başlaması:** Sorun istemcinin gönderdiğinde; aynı isteği değiştirmeden tekrar göndermek işe yaramaz.
2. **Gövdedeki açıklama:** Neyin yanlış olduğunu söyler. Her API'nin hata gövdesi farklıdır; FastAPI'de `detail` listesi, Open-Meteo'da `reason` metni.

Bu yüzden bir API'nin hangi durum kodunu ve hangi hata gövdesini kullandığı belgesinde yazmalı. Föyün 8.2 bölümünde `README.md` belgesine eklediğimiz "Alan kuralları" bölümü bunu yapıyor.

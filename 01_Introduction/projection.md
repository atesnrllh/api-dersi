# Introduction — Projection

## Hava durumunu kendi programımıza alalım

**Bugün Samsun'da hava ne kadar sıcak olacak? Yanımıza şemsiye almalı mıyız?**

Önce sitede tahmine bakacağız. Sonra aynı bilgileri Python programımıza alıp bir öneri göstereceğiz.

---

## 1. Sitede konumu seçelim

[Open-Meteo hava tahmini sayfasını aç](https://open-meteo.com/en/docs).

**Location and Time — Konum ve zaman** bölümünü dolduralım:

| Alan | Değer |
|---|---|
| Latitude — Enlem | `41.27976` |
| Longitude — Boylam | `36.3361` |
| Timezone — Saat dilimi | **Automatically detect time zone** |
| Forecast days — Gün sayısı | **7 days** |

**Enlem ve boylam birlikte haritadaki tek bir noktayı belirtir.** Samsun içindeki bu noktanın tahminini istiyoruz.

Saat dilimi, konuma göre otomatik belirlenecek.

---

## 2. Sıcaklık ve yağış olasılığını görelim

**Hourly Weather Variables — Saatlik bilgiler** bölümünde yalnızca şu iki kutuyu seçelim:

- **Temperature (2 m):** Yerden iki metre yükseklikteki hava sıcaklığı.
- **Precipitation Probability:** Yağış olasılığı.

**API Response → Chart & URL** bölümüne inelim. Grafik, yedi günlük saatlik tahminleri gösterir. Alt eksende tarihler ve saatler vardır.

| Bilgi | Birim | Ne anlatır? |
|---|---|---|
| Sıcaklık | **°C** | Havanın ne kadar sıcak olacağı. |
| Yağış olasılığı | **%** | Yağışın gerçekleşme ihtimali. |

**Yağış olasılığı, yağmur miktarı değildir.** `Rain` miktarı **mm** ile gösterir; bu örnekte o kutuyu seçmiyoruz. `%80` olasılık, şiddetli yağmur demek değildir.

---

## 3. Bugünün iki değerini seçelim

Programımızda saatlik grafik yerine şu iki bilgiyi göstereceğiz:

- **Bugünün en yüksek sıcaklığı.**
- **Bugün için verilen en yüksek yağış olasılığı.**

Sitedeki seçimleri değiştirelim:

1. **Forecast days → 1 day** seçelim.
2. **Hourly Weather Variables** bölümündeki iki işareti kaldıralım.
3. **Daily Weather Variables — Günlük bilgiler** bölümünde **Maximum Temperature (2 m)** ve **Precipitation Probability Max** kutularını seçelim.

**Günün en yüksek olasılığı:** Saatlik değerler `%10`, `%30`, `%20` ise en yüksek değer `%30` olur. Bu, bütün günün tek bir yağış olasılığı değildir.

---

## 4. Grafiğin verisini açalım

**API Response** bölümüne dönelim. **API URL** alanının yanındaki **Open in new tab — Yeni sekmede aç** bağlantısına tıklayalım.

**URL**, internet adresidir. Açılan adreste grafiği değil, programların okuyabileceği veriyi görüyoruz. Bu yazım biçimine **JSON** denir.

Yanıtın günlük bilgiler bölümü şöyle görünür:

```json
{
  "daily": {
    "time": ["2026-09-22"],
    "temperature_2m_max": [24.1],
    "precipitation_probability_max": [30]
  }
}
```

**Tarih ve sayılar örnektir.** Sırayla tarih, en yüksek sıcaklık ve en yüksek yağış olasılığı verilmiştir.

`[...]` bir listeyi gösterir. Bir gün istediğimiz için her listede bir değer vardır.

---

## 5. API bize ne sağlıyor?

**Sitedeki bilgiyi kendi programımızın kullanmasını sağlıyor.**

Open-Meteo'nun API'si, başka programların hava tahmini istemesine imkân veren arayüzdür. Hangi adrese, hangi bilgileri göndererek tahmin isteyeceğimizi ve nasıl bir yanıt alacağımızı belirler.

Bu örnekte:

- **İstemci:** Tahmini isteyen Python programımız.
- **Sunucu:** İsteğimizi karşılayıp tahmini gönderen Open-Meteo sistemi.

Sunucu Open-Meteo tarafında çalışıyor. Biz yalnızca istemciyi yazacağız.

---

## 6. Python ile isteği gönderelim

**HTTPX**, Python'dan istek gönderip yanıt almamızı sağlayan bir kütüphanedir.

`client.py` dosyasını aşağıdaki kodla başlatalım. Sonraki bölümde devamını ekleyeceğiz.

```python
import httpx

response = httpx.get(
    "https://api.open-meteo.com/v1/forecast",
    params={
        "latitude": 41.27976,
        "longitude": 36.3361,
        "daily": "temperature_2m_max,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 1,
    },
    timeout=15,
)
```

- `httpx.get(...)`, belirttiğimiz adresten bilgi ister; gelen yanıt `response` içinde tutulur.
- `params`, sitede yaptığımız seçimleri taşır: **konum, istenen bilgiler, saat dilimi ve gün sayısı**.
- `timeout=15`, ağ işlemlerinde bağlantı veya veri beklemek için zaman aşımı sınırı koyar.

---

## 7. Yanıttaki bilgileri ekrana yazdıralım

`client.py` dosyasında önceki kodun altına ekleyelim:

```python
response.raise_for_status()
weather = response.json()["daily"]

print("Şehir: Samsun")
print("Tarih:", weather["time"][0])
print("En yüksek sıcaklık:", weather["temperature_2m_max"][0], "°C")
print(
    "Günün en yüksek yağış olasılığı:",
    weather["precipitation_probability_max"][0], "%"
)
```

| Kod | Görevi |
|---|---|
| `raise_for_status()` | Başarısız bir HTTP yanıtı geldiyse hata verir. |
| `response.json()` | JSON yanıtını Python sözlük ve listelerine dönüştürür. |
| `["daily"]` | Günlük bilgilerin bulunduğu bölümü seçer. |
| `[0]` | Listedeki ilk değeri seçer: burada bugünün değeri. |
| `print(...)` | Bilgiyi terminale yazdırır. |

---

## 8. Çalıştıralım

Python ve HTTPX'in hazır olduğu ortamda, dosyayı kaydedip terminalde çalıştıralım:

```bash
python client.py
```

Örnek çıktı:

```text
Şehir: Samsun
Tarih: 2026-09-22
En yüksek sıcaklık: 24.1 °C
Günün en yüksek yağış olasılığı: 30 %
```

**Program, çalıştırıldığı günün tahminini getirir; sonuçlar değişebilir.** Sıcaklık, şu anki ölçüm değil, gün için tahmin edilen en yüksek değerdir.

---

## 9. Şemsiye önerisi gösterelim

Dosyanın sonuna ekleyelim:

```python
if weather["precipitation_probability_max"][0] >= 50:
    print("Dışarı çıkarken yanına şemsiye al.")
else:
    print("Bugün için en yüksek yağış olasılığı %50'nin altında.")
```

Programı yeniden çalıştıralım.

**Open-Meteo yağış olasılığını gönderir. Şemsiye önerisini bizim programımız üretir.**

`50` sınırını biz seçtik. `%50`'nin altında olması, kesinlikle yağış olmayacağı anlamına gelmez.

API sayesinde başka bir hizmetten aldığımız bilgiyi **kendi uygulamamızda kullanabiliyoruz.**

---

[Kısa kavram notları](01_Lecture_Notes.md) · [HTTPX](https://www.python-httpx.org/quickstart/) · Hava tahmini verisi: [Open-Meteo](https://open-meteo.com/en/docs), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

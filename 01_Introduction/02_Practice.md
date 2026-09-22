# Introduction — Practice

## Hava durumunu kendi programımıza alalım

Bugün Samsun'da dışarı çıkacağımızı düşünelim. Hava ne kadar sıcak olacak? Yağış ihtimali var mı? Önce bu bilgileri bir web sitesinde göreceğiz. Ardından küçük bir Python programıyla aynı hizmetten bilgi alıp kendi ekranımıza yazdıracağız.

Bu başlangıç dersinin amacı, **API öğrenerek ne yapabileceğimizi çalışan bir örnekte görmek.** Kodun kurulumu eğitmenin hazır Python ortamında gösterilebilir; öğrenciler ilk bölüme yalnızca tarayıcıyla katılabilir. Python ortamını hazırlamayı Week 1'de ele alacağız.

## 1. Sitede Samsun'un hava tahminini aç

[Open-Meteo hava tahmini sayfasını](https://open-meteo.com/en/docs) aç. Bu sayfada konumu ve görmek istediğimiz bilgileri seçip bir grafik oluşturabiliyoruz. Sayfanın adı **Weather Forecast API**; birazdan önce grafiğini kullanacağız.

**Location and Time (Konum ve zaman)** bölümünü şu şekilde doldur:

| Alan | Seçilecek veya yazılacak değer | Ne belirliyoruz? |
|---|---|---|
| Latitude — Enlem | `41.27976` | Samsun'da kullanacağımız noktanın enlemi. |
| Longitude — Boylam | `36.3361` | Aynı noktanın boylamı. |
| Timezone — Saat dilimi | **Automatically detect time zone** | Saat dilimini girdiğimiz konuma göre otomatik belirlemesini istiyoruz. |
| Forecast days — Tahmin gün sayısı | **7 days** | Önümüzdeki yedi günlük tahmini görmek istiyoruz. |

Ondalık sayılarda nokta kullan. Saat dilimi listesinde İstanbul aramana gerek yok; otomatik seçim Samsun için de uygundur.

**Enlem ve boylam birlikte, haritadaki tek bir noktayı belirtir.** Burada Samsun içindeki bir konum için tahmin istiyoruz.

**Hourly Weather Variables (Saatlik hava durumu değişkenleri)** bölümünde şu iki kutuyu işaretle:

- **Temperature (2 m):** Sıcaklık.
- **Precipitation Probability:** Yağış olasılığı.

Başka kutular işaretliyse şimdilik kaldır. Aşağıdaki **API Response (API Yanıtı)** bölümüne git ve **Chart & URL (Grafik ve adres)** görünümüne bak. Bu bölüm, seçtiğimiz bilgileri grafik olarak gösterir.

## 2. Grafikte ne görüyoruz?

| Grafikteki bilgi | Nasıl okunur? |
|---|---|
| Tarihler ve saatler | Tahminin hangi zamana ait olduğunu gösterir. |
| `temperature_2m` | Sıcaklık tahminidir; birimi **°C**'dir. `2 m`, yerden iki metre yükseklikteki hava sıcaklığını belirtir. |
| `precipitation_probability` | Yağış olasılığıdır; birimi **%**'dir. |

Sıcaklık ile yağış olasılığı farklı birimlerle gösterilir. Örneğin `20 °C` ile `%20` aynı şey değildir; her değerin birimine bak.

**Grafikte yalnızca sıcaklık görünüyorsa:** Yağış olasılığı kutusunun da seçili olduğunu kontrol et. `Rain` kutusunu seçmek, yağış olasılığını seçmek değildir.

### Yağış olasılığı ile yağmur miktarı aynı mı?

| Bilgi | Cevapladığı soru | Örnek |
|---|---|---|
| Precipitation Probability — Yağış olasılığı | Bu zaman aralığında yağış olma ihtimali nedir? | `%80` |
| Rain — Yağmur | Bu zaman aralığında ne kadar yağmur bekleniyor? | `2 mm` |

`%80`, yağmurun şiddetli olacağı veya zamanın %80'inde yağacağı anlamına gelmez. Yağışın gerçekleşme ihtimalini anlatır. Yağış ihtimali yüksekken beklenen miktar az olabilir. **Yağış**, yağmur ve kar gibi türleri kapsayan genel addır.

Bu çalışmada sıcaklık ve **yağış olasılığını** izleyeceğiz. Yağmur miktarını ayrıca seçmemiz gerekmiyor. Alanların açıklamaları [Open-Meteo belgelerinde](https://open-meteo.com/en/docs#hourly_parameter_definition) bulunur.

## 3. Python'da göstereceğimiz iki bilgiyi seç

Yedi günlük grafik genel durumu görmemizi sağladı. Şimdi programımızın ekranda göstereceği bilgileri belirleyelim:

> Samsun için **bugünün en yüksek sıcaklığını** ve **bugün için verilen en yüksek yağış olasılığını** göster.

Sitedeki seçimleri buna göre değiştir:

1. **Forecast days** alanını **1 day** yap. Bu seçim bugünü getirir.
2. **Hourly Weather Variables** bölümünde seçtiğimiz iki kutunun işaretini kaldır.
3. **Daily Weather Variables (Günlük hava durumu değişkenleri)** bölümünde **Maximum Temperature (2 m)** ve **Precipitation Probability Max** kutularını işaretle.
4. **API Response → Chart & URL** bölümüne dön.

Artık saat saat değişen değerler yerine, bugün için her bilgiden bir değer istiyoruz. Tek gün seçtiğimiz için önceki gibi yedi güne yayılan bir çizgi görmeyi beklemeyiz.

**“En yüksek yağış olasılığı” ne demek?** Örneğin gün içindeki bazı saatler için `%10`, `%30` ve `%20` verildiyse, bunların en yükseği `%30`'dur. Bu değer bir yağmur miktarı değildir; bütün günün tek bir yağış olasılığı olarak da yorumlanmamalıdır.

## 4. Grafiğin arkasındaki veriyi aç

Grafiğin altında **API URL** adlı bir adres alanı var. **URL**, internet adresi demektir. Seçimleri değiştirdiğimizde bu adresin de değiştiğini görebiliriz.

**Open in new tab (Yeni sekmede aç)** bağlantısına tıkla. Bu kez bir hava durumu grafiği yerine, alan adları ve değerlerden oluşan bir yanıt göreceksin. Tarayıcıya göre tek satırda veya girintili gösterilebilir.

Bu yazım biçimine **JSON** denir. Programlar JSON içindeki alanları adlarıyla bulup değerlerini okuyabilir. Yanıtın yalnızca `daily` bölümünü örnek olarak gösterelim; aşağıdaki sayılar temsildir:

```json
{
  "daily": {
    "time": ["2026-09-22"],
    "temperature_2m_max": [24.1],
    "precipitation_probability_max": [30]
  }
}
```

| Alan | Bu örnekteki anlamı |
|---|---|
| `time` | Tahminin ait olduğu tarih. |
| `temperature_2m_max` | O günün tahmin edilen en yüksek sıcaklığı: `24.1 °C`. |
| `precipitation_probability_max` | O günün tahminlerindeki en yüksek yağış olasılığı: `%30`. |

Köşeli parantezlerin içindeki değerler birer listedir. Bir gün istediğimiz için her listede bir değer var. Birkaç gün isteseydik aynı sıradaki tarih, sıcaklık ve olasılık değerleri aynı güne ait olacaktı.

### API burada ne işe yarıyor?

Sitedeki grafiği biz okuyabiliyoruz. Kendi Python programımızın da bu bilgileri kullanmasını istiyorsak, programın veriyi alabileceği bir yol gerekir.

**Open-Meteo'nun API'si, başka programların hava tahmini istemesine imkân veren arayüzdür.** Hangi adrese ne bilgi gönderileceğini ve karşılığında nasıl bir yanıt alınacağını tanımlar. Az önce açtığımız adres, bu API üzerinden tahmin istemek için kullanılıyor.

Birazdan Python programımız konumu ve istediğimiz bilgileri gönderecek. Open-Meteo yanıt verecek. Biz de yanıttaki değerleri kendi seçtiğimiz başlıklarla ekrana yazdıracağız.

## 5. Aynı bilgileri Python ile al

Bu örnekte **istemci**, bilgi isteyen `client.py` programımızdır. İsteği karşılayan **sunucu**, Open-Meteo tarafında zaten çalışır. Bu nedenle bu gösterim için kendi bilgisayarımızda bir `server.py` çalıştırmamız gerekmiyor.

### `client.py` — dosyanın tamamı

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
response.raise_for_status()
weather = response.json()["daily"]

print("Şehir: Samsun")
print("Tarih:", weather["time"][0])
print("En yüksek sıcaklık:", weather["temperature_2m_max"][0], "°C")
print("Günün en yüksek yağış olasılığı:", weather["precipitation_probability_max"][0], "%")
```

**HTTPX**, Python programının internet üzerinden istek gönderip yanıt almasını sağlayan bir kütüphanedir; Python ortamına paket olarak kurulur. Burada hava tahminini üreten Open-Meteo'dur; HTTPX onunla iletişim kurmamıza yardım eder.

Python ve HTTPX'in hazır olduğu ortamda, bu dosyanın bulunduğu klasörde çalıştır:

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

**Tarih ve sayılar örnektir.** Program çalıştığı günün tahminini alır. Sıcaklık, o anda termometreyle ölçülen değer değil, gün için beklenen en yüksek değerdir.

### Kodun hangi kısmı ne yapıyor?

Önce sitedeki seçimlerle kodu eşleştirelim. `params`, isteğe eklediğimiz seçimleri tutan Python sözlüğüdür:

| Sitedeki seçim | Koddaki karşılığı |
|---|---|
| Latitude ve Longitude | `latitude` ve `longitude` |
| `Daily Weather Variables` bölümündeki iki kutu | `daily` içindeki virgülle ayrılmış iki alan adı |
| Automatically detect time zone | `"timezone": "auto"` |
| 1 day | `"forecast_days": 1` |

Diğer satırların görevleri:

| Kod | Açıklama |
|---|---|
| `import httpx` | HTTPX'i bu dosyada kullanmamızı sağlar. |
| `httpx.get(...)` | Belirttiğimiz adresten bilgi ister. Buradaki `GET`, bilgi istemek için kullandığımız HTTP yöntemidir. HTTP, istemci ve sunucunun mesajlaşırken kullandığı kurallardır. |
| `response = ...` | Gelen yanıtı `response` adlı değişkende tutar. |
| `timeout=15` | Ağ işlemlerinde bağlantı veya yeni veri beklemek için 15 saniyelik zaman aşımı sınırı koyar. |
| `response.raise_for_status()` | Başarısız bir HTTP yanıtı geldiyse hata verir; başarılı yanıtta sonraki satıra geçilir. |
| `response.json()` | Yanıttaki JSON'u Python'un okuyabileceği sözlük ve listelere dönüştürür. Yeni bir istek göndermez. |
| `["daily"]` | Dönüştürülen yanıttan günlük bilgilerin bulunduğu bölümü seçer. Bu bölüm `weather` değişkenine atanır. |
| `weather["time"][0]` | Tarihler listesindeki ilk değeri alır. Python'da ilk elemanın sıra numarası `0`'dır. Diğer iki satır da kendi listesindeki ilk değeri alır. |
| `print(...)` | Seçtiğimiz bilgiyi terminale yazdırır. `Şehir: Samsun` yazısı kodda bizim yazdığımız etikettir; konumu belirleyen ise gönderdiğimiz koordinatlardır. |

İstek gönderme ve yanıt okuma işlemleri [HTTPX'in başlangıç belgesinde](https://www.python-httpx.org/quickstart/) de örneklenir.

## 6. Yağış olasılığına göre şemsiye önerisi göster

Şimdi `client.py` dosyasının sonuna şu satırları ekle:

```python
if weather["precipitation_probability_max"][0] >= 50:
    print("Dışarı çıkarken yanına şemsiye al.")
else:
    print("Bugün için en yüksek yağış olasılığı %50'nin altında.")
```

Programı yeniden çalıştır. **Open-Meteo yağış olasılığını gönderiyor; bizim programımız bu değere bakarak kullanıcıya bir mesaj gösteriyor.** Şemsiye önerisini Open-Meteo'dan almıyoruz; öneriyi üretmek için **`50` sınırını biz belirliyoruz.** `%50`'nin altında olması, yağışın kesinlikle olmayacağı anlamına gelmez.

API öğrenmenin bize kazandırdığı şey burada görünür: dışarıdaki bir hizmetten bilgi alıp **kendi uygulamamızın bir parçası hâline getirebiliriz.** Bu örnekte programımız, aldığı yağış olasılığını ekrana yazdırmanın yanında, belirlediğimiz koşula göre şemsiye önerisi de gösterebiliyor.

## 7. Gözlemini kontrol et

- Yağış olasılığı kutusunu kaldırınca grafikte hangi bilgi kayboluyor?
- Sitede seçtiğimiz konumun kodda hangi iki satırla belirlendiğini gösterebilir misin?
- Şemsiye önerisini Open-Meteo mu gönderdi, bizim kodumuz mu üretti?

Bu örnekte hazır bir API'yi kullandık. Week 1'de kendi küçük sunucumuzu yazıp bir istemcinin ona nasıl istek gönderdiğini inceleyeceğiz. Bu gösterimde gördüğümüz kavramları kısaca toparlamak için [Lecture Notes](01_Lecture_Notes.md) dosyasını okuyabilirsin.

## Konum ve veri hakkında kısa sorular

### Şehir adını yazarak tahmin alamaz mıyız?

Alabiliriz; program önce şehir adının koordinatlarını bulur, sonra bu koordinatlarla tahmin ister. Open-Meteo'nun [konum arama sayfası](https://open-meteo.com/en/docs/geocoding-api), yer adlarını koordinatlarla eşleştirir. İlk programımızı kısa tutmak için bildiğimiz koordinatları doğrudan yazdık.

**Aynı adla iki sonuç çıkarsa** ülkeye ve ile de bak. Örneğin Samsun aramasında Samsun ilindeki kaydın yanında Trabzon/Çarşıbaşı içinde “Samsun” adlı başka bir kayıt da görülebilir. Bu ders için **ili Samsun olan kaydı** kullanıyoruz.

### Başka kaynakta koordinatlar neden farklı?

Şehir geniş bir alanı kaplar; okulun ve meydanın koordinatları farklıdır. Kaynaklar şehri temsil etmek için farklı noktalar seçebilir. Örneğin [DB-City'deki Samsun kaydı](https://tr.db-city.com/T%C3%BCrkiye--Samsun--Samsun) `41.2903, 36.3336` verir. Bu nokta kullandığımız noktadan yaklaşık **1,2 km** uzaktadır. Bu fark tek başına birinin yanlış olduğunu göstermez.

Grafikte görünen koordinatlar ise hava tahmini modelinin kullandığı yakın noktaya ait olabilir; girdiğimiz sayılarla birebir aynı olmak zorunda değildir. [Open-Meteo'nun konum açıklaması](https://open-meteo.com/en/docs#json_return_object)

### Open-Meteo'nun verilerine güvenebilir miyiz?

Open-Meteo, ECMWF (Avrupa), DWD (Almanya) ve NOAA (ABD) gibi meteoroloji kuruluşlarının tahminlerinden yararlanır. Kaynaklarını açıkça belirtir; bu nedenle dersimiz için uygun bir gerçek veri hizmetidir. Bununla birlikte tahminin kesin gerçekleşeceği söylenemez. [Veri kaynakları](https://open-meteo.com/en/docs#data_sources)

Hava tahmini verisi: [Open-Meteo](https://open-meteo.com/) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Tahminler güncellendikçe sonuçlar değişebilir.

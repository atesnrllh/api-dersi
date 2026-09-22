# Introduction — Lecture Notes

[Practice](02_Practice.md) bölümünde önce Samsun için hava tahminini sitede gördük, sonra Python programımızla aldık. Bu kısa not, yaptığımız işteki kavramları birbirinden ayırmak içindir.

## API bize ne kazandırdı?

Bir okulun gezi duyurusunda bugünün sıcaklığını göstermek istediğimizi düşünelim. Sitedeki değeri okuyup duyuruya elle yazabiliriz. Programımız ise Open-Meteo'dan tahmini isteyip gelen değeri doğrudan duyuruda kullanabilir. Böylece hava tahmini üreten sistemi kendimiz kurmadan, o hizmetin sunduğu bilgiyi kendi uygulamamıza katmış oluruz.

**API**, bir yazılımın başka programların kullanımına sunduğu işlemleri ve bu işlemlerin nasıl kullanılacağını belirleyen arayüzdür. Buradaki somut işlem, seçtiğimiz konumun hava tahminini istemektir. Kullanım kuralları arasında isteği hangi adrese göndereceğimiz, konumu nasıl belirteceğimiz ve yanıtın nasıl düzenleneceği bulunur.

## Bu örnekte istemci ve sunucu hangisi?

`client.py` çalıştığında Open-Meteo'ya istek gönderen bir program olur; bu nedenle **istemci** rolündedir. İnternetteki Open-Meteo sunucusu isteği karşılar ve tahmin bilgilerini geri gönderir. Bizim bilgisayarımızda ayrıca bir hava durumu sunucusu çalıştırmadık.

```text
Python programımız → Open-Meteo: Bu konumun bugünkü tahminini istiyorum.
Open-Meteo → Python programımız: İstediğin bilgiler bunlar.
```

Programımızdaki **HTTPX**, bu iletişimi Python koduyla yapmamızı sağlayan kütüphanedir. `httpx.get(...)` isteği gönderir; dönen `response` üzerinden yanıtı okuruz. `params` ile konum ve istediğimiz bilgiler gibi seçimleri göndeririz. Bu adları hizmetin kabul ettiği biçimde yazmamız gerekir. [HTTPX: İstek gönderme ve parametreler](https://www.python-httpx.org/quickstart/#passing-parameters-in-urls)

## JSON burada ne işe yaradı?

Tarayıcıda API adresini açtığımızda grafik yerine alan adları ve değerler gördük. Aşağıdaki parça yalnızca yapıyı göstermek için kısaltılmıştır; `24.1` güncel tahmin değildir:

```json
{"daily": {"temperature_2m_max": [24.1]}}
```

**JSON**, bilgilerin metin içinde düzenli biçimde yazılmasını sağlayan bir veri biçimidir. Bu örnekte `daily` günlük bilgileri, `temperature_2m_max` ise günlük en yüksek sıcaklıkları içerir. Köşeli parantez bir listeyi gösterir; bir gün istediğimiz için listede tek değer vardır.

`response.json()` bu yanıtı Python'da okuyabileceğimiz sözlük ve listelere dönüştürür. Program böylece istediği değeri seçip terminale yazdırabilir. JSON, API'nin bu örnekte yanıtı yazmak için kullandığı biçimdir. [HTTPX: JSON yanıtını okuma](https://www.python-httpx.org/quickstart/#json-response-content)

## Gelen değerleri doğru yorumlamak

Enlem ve boylam, Samsun'un tamamını değil, harita üzerindeki bir noktayı belirtir. Hizmetten o konum için tahmin isteriz. Farklı kaynakların şehir adına verdiği koordinatlar, seçtikleri temsil noktası nedeniyle farklı olabilir.

Sitede saatlik sıcaklıkları inceleyebiliriz; programımızda ise bir günlük özeti istedik:

| Bilgi | Anlamı |
| --- | --- |
| En yüksek sıcaklık | O gün için tahmin edilen en yüksek sıcaklık; şu anda ölçülen sıcaklık değildir. |
| Günün en yüksek yağış olasılığı | Gün içindeki saatlik yağış olasılıklarının en büyüğü. |

Yağış olasılığı **yüzde (%)**, yağmur miktarı **milimetre (mm)** ile belirtilir. Örneğin yüksek olasılık, mutlaka çok miktarda yağmur beklendiğini söylemez. Programımız miktarı istemedi; olasılığı istedi. Bunlar tahmin verileridir ve yeni tahminlerle değişebilir. [Open-Meteo: Saatlik bilgiler](https://open-meteo.com/en/docs#hourly_parameter_definition), [günlük bilgiler](https://open-meteo.com/en/docs#daily_parameter_definition)

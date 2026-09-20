# API Dersi

Uygulama Programı Arayüzü (API) dersi için planlama ve ders materyalleri.

**Süre:** 14 hafta; haftada 3 ders saati teori + 2 ders saati uygulama.

## Planlama belgeleri

- [Haftalık ders planı](00_Planlama/01_Haftalik_Ders_Plani.md): Haftalık teorik konu ve uygulama başlıkları.
- [Teknolojiler ve araçlar](00_Planlama/02_Teknolojiler_ve_Araclar.md): Seçilen araçlar ve dersteki kullanım amaçları.
- [Ders işleme yaklaşımı](00_Planlama/03_Ders_Isleme_Yaklasimi.md): Birinci haftanın uygulamasından çıkarılan tempo, örnek seçimi ve teori–uygulama karşılaştırma ölçütleri.

Haftalık plan ile teknoloji tablosu ayrı tutulur. Haftalık plana araç sütunu eklenmez.

## Haftalık materyaller

| Hafta | Teorik ders notu | Uygulama föyü |
|---|---|---|
| 01 | [API temelleri, istemci–sunucu mimarisi ve JSON](02_Haftalik_Materyaller/Hafta_01/01_Teorik_Ders_Notu.md) — üzerinde çalışılıyor | [İlk kitap kataloğu API'si](02_Haftalik_Materyaller/Hafta_01/02_Practice.md) — üzerinde çalışılıyor; VS Code'da Python sunucusu ve istemcisiyle yönlendirilmiş çalışma |
| 02 | [HTTP istek–yanıt yapısı, metotlar, başlıklar ve durum kodları](02_Haftalik_Materyaller/Hafta_02/01_Teorik_Ders_Notu.md) — üzerinde çalışılıyor | [Kitap kataloğunda HTTP deneyleri](02_Haftalik_Materyaller/Hafta_02/02_Uygulama_Foyu.md) — üzerinde çalışılıyor; Postman ve HTTPX ile GET/POST çalışması |

İlk haftanın teorik notu açıklamalar, beş şema, örnekler ve cevaplı değerlendirme soruları içerir. Görseller notun yanındaki `Gorseller` klasöründe saklanır; Markdown belgeleri ve görseller birlikte sürüm takibine alınır.

İkinci hafta birinci haftanın üç kitaplı son sürümünü sürdürür. Teori, “yeni kitabı istemciden nasıl ekleriz?” ihtiyacından hareket eder. Uygulamada gövdeyi almak, kaydetmek ve yanıtı istemcide yorumlamak ayrı gözlemlerle ilerler. POST ve `Location`, tekrar gönderim ve hatalı gövde deneyleri aynı kitapla çalışılır. Föy, her kod değişikliğinde tam dosyayı; her deneyde amaç, teori bağlantısı, başlangıç durumu, beklenen sonuç ve gerekçeli kontrol sorusu verir. PUT/PATCH/DELETE teorinin başvuru bölümündedir; uygulanmaları dördüncü haftadadır.

## Çalışma düzeni

Ana belgeler Markdown (`.md`) biçiminde tutulur. Güncellemeler bu kaynaklarda yapılır; PDF ve gerektiğinde Word dosyaları paylaşım için üretilir.

Üçüncü haftadan itibaren tek dönem projesi geliştirilir. Proje kodu haftalara kopyalanarak çoğaltılmaz; gelişimi Git üzerinden takip edilir.

İhtiyaç oldukça aşağıdaki klasörler eklenecektir:

```text
API/
├── README.md
├── 00_Planlama/
│   ├── 01_Haftalik_Ders_Plani.md
│   ├── 02_Teknolojiler_ve_Araclar.md
│   └── 03_Ders_Isleme_Yaklasimi.md
├── 01_Kurulum_Rehberleri/
├── 02_Haftalik_Materyaller/
│   └── Hafta_01/ ... Hafta_14/
│       ├── 01_Teorik_Ders_Notu.md
│       ├── 02_Uygulama_Foyu.md
│       └── Gorseller/
├── 03_Donem_Projesi/
└── 04_Paylasim_Ciktilari/
```

Haftalık teorik ders notları ve uygulama föyleri ayrı belgelerde hazırlanır. Kurulum ve araç kullanım yönergeleri kurulum rehberlerinde tutulur.

## Devam edilecek işler

- Öğrencilerin programlama önbilgisini ve laboratuvar koşullarını netleştirmek.
- Kesin sınav takvimini plana işlemek.
- Dönem projesinin konusunu kesinleştirmek; önceki görüşmede Kitap Takip API’si önerilmiştir.
- Kurulum rehberlerini ve haftalık materyalleri hazırlamak.

Bu başlangıç belgeleri, “API Konuşmasını Bulma” sohbetindeki son plan ve Markdown tercihi esas alınarak 6 Eylül 2026 tarihinde hazırlanmıştır.

## Sürüm takibi

Bu klasör Git ile takip edilecek şekilde düzenlenmiştir. GitHub’a gönderilen sürümler, ders materyallerinin değişiklik geçmişini tutar. Dosyayı VS Code’da kaydetmek GitHub’a otomatik gönderim yapmaz; ilgili değişiklikler kaydedilip (`commit`) gönderilmelidir (`push`).

`.gitignore`, yerel ortam dosyalarını ve geçici dosyaları kapsam dışında bırakır. Ders notları, görseller ve ileride eklenecek proje kaynakları depoda tutulur.

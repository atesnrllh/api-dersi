# Hafta 05 — Ders Anlatımı

Bu dosya, [uygulama föyünü](02_Practice.md) bölüm bölüm, bir öğretmenin anlatacağı gibi anlatır. Kısa cümlelerle yazıldı; sesli okumaya uygundur. Her bölümü föydeki aynı bölümle birlikte oku.

---

## Bölüm 0: Kural kimin işi?

### Bugünkü durum

Hafta 2'den beri sunucumuz bazı hatalı istekleri reddediyor. Örneğin kitabın adını metin yerine sayı olarak gönderdiğini düşün: `"title": 123`. Sunucu bu isteği `422` ile reddeder. Kitap eklenmez.

Ama sunucu hâlâ bazı hatalı değerleri kabul ediyor. Adı boş olan bir kitap eklenebiliyor. Puanı 9 olan bir yorum da eklenebiliyor. Oysa puan 1 ile 5 arasında olmalı.

Bunun nedeni şu: Sunucu şimdilik yalnızca **türe** bakıyor. Boş bir ad da sonuçta bir metin. 9 da bir sayı. Türleri doğru olduğu için ikisi de geçiyor.

Bu hafta bu değerleri reddeden kurallar yazacağız.

### Haftanın sorusu

Haftanın sonunda şu soruya cevap verebileceksin: **Bir kuralı nereye yazmalıyım?**

Bunun için kuralları ikiye ayıracağız.

**Birinci grup:** Gelen değere bakmak yeten kurallar. Boş bir metin buna örnek. Beşten büyük bir puan da öyle. Bunlara karar vermek için sunucudaki verilere bakmak gerekmez.

**İkinci grup:** Sunucudaki veriye bakmayı gerektiren kurallar. Örneğin "43 numaralı kitap var mı?" sorusu. 43 sayısında bir sorun yok. Ama böyle bir kitabın olup olmadığını öğrenmek için kitap listesine bakmak gerekiyor.

Birinci gruptaki kuralları FastAPI, bizim fonksiyonumuz çalışmadan önce kontrol edebilir. İkinci gruptakileri ise yalnızca bizim fonksiyonumuz bilebilir.

Bu ayrımı Deney 5'in sonunda bir tabloda toplayacağız.

### Haftanın planı

Bu hafta altı deney yapacağız:

- **Deney 1:** Sunucunun bugün hangi hatalı değerleri kabul ettiğini göreceğiz. Hata yanıtını da okumayı öğreneceğiz.
- **Deney 2:** Boş metinleri ve aralık dışındaki puanları reddedeceğiz.
- **Deney 3:** Türleri sıkılaştıracağız. Modelde olmayan alanları da reddedeceğiz.
- **Deney 4:** `PATCH` isteğinde zorunlu bir alana `null` gönderilirse bunu reddedeceğiz.
- **Deney 5:** Bir kuralın modele mi, fonksiyona mı yazılacağına karar vereceğiz.
- **Deney 6:** Bu bir ödev. Hata yanıtını istemcide okunur biçimde göstereceğiz.

### 0.1 Başlangıç dosyaları

Hafta 4'ün sonundaki dosyalarla başlıyoruz.

`server.py` dosyası, Hafta 4'teki Deney 4'ün sonundaki hâliyle olmalı. Yani dekoratörlerinde `response_model` olan sunucu.

`client.py` dosyasını ise her deneyde baştan yazacağız.

Kendi `server.py` dosyandan emin değilsen, bu haftanın [başlangıç dosyasını](Starting_Code/server.py) kullan. Föydeki çıktılar o dosyayla alındı. Bu dosyada iki şey önemli: 42 numaralı kitapta `internal_note` diye bir alan var. Bir de Ece'nin yazdığı bir yorum var. Deney 3 ve Deney 5 bunlara dayanıyor.

Hafta 4'te `delete_review` fonksiyonunu yazdıysan, o da dosyada kalabilir. Bu haftanın değişiklikleriyle çakışmaz.

### Sunucuyu yeniden başlatmak

Sunucu her başlatıldığında dosyada yazılı üç kitapla ve bir yorumla başlar. İstemcinin eklediği kitaplar ve yorumlar bellekte durur. Sunucuyu yeniden başlatınca bunlar silinir.

Bu yüzden deneylerde sık sık "sunucuyu yeniden başlat" diyeceğiz. Bu adımı atlarsan, çıktıların föydekilerden farklı olabilir.

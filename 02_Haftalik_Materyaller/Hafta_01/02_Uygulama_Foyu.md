# Hafta 01 — Uygulama Föyü

**Ders:** Uygulama Programı Arayüzü (API)

**Süre:** 2 ders saati — toplam 90 dakika; her ders saati 45 dakika kabul edilmiştir.

**Konu:** İlk API İsteği ve JSON Yanıtlarını Okuma

**Sürüm:** 1.0 — 7 Eylül 2026

## 1. Uygulamanın amacı

Bu çalışmanın sonunda bir GET isteği gönderebilecek; durum kodunu, içerik türünü ve JSON gövdesini ayırt edebileceksin. Tek kayıt ile listeyi, başarılı yanıt ile hata yanıtını ve HTTP yanıtı almak ile bağlantı kuramamak arasındaki farkı açıklayabileceksin. Bu hafta API sunucusu yazmıyoruz.

## 2. Ön hazırlık ve gerekli araçlar

- İnternet bağlantısı ve **Postman masaüstü uygulaması** gerekir. Terminalde `curl` varsa aşağıdaki eşdeğer komutlarla da çalışabilirsin. İki yöntemi birden uygulaman gerekmiyor.
- Postman kullanıyorsan uygulamayı aç; terminal kullanıyorsan `curl --version` ile aracın kullanılabilirliğini kontrol et. Araç eksikse kurulumu ders öncesinde eğitmenle tamamla. Ayrıntılı kurulum yönergeleri bu föyün kapsamı dışındadır.
- Teori notunun 5–7 ve 10–12. bölümlerini yanında bulundur. Kod yazma veya Python bilgisi gerekmez.

**Örnek hizmet:** [JSONPlaceholder](https://jsonplaceholder.typicode.com/), öğretim ve deneme amaçlı örnek veriler sunar. Burada kitap yerine görev (`todo`) kayıtlarını okuyacağız. Kitap örneğindeki istemci–sunucu ve JSON kavramları aynen geçerlidir.

Bu uç noktalar için hesap veya API anahtarı gerekmiyor. Postman'de yetkilendirmeyi **No Auth** olarak bırak. Teorideki `kutuphane.example` çalışan bir adres değildir; bu föyde aşağıdaki gerçek adresleri kullan.

## 3. Çalışma akışı

| Süre | Görev | Beklenen çıktı |
|---|---|---|
| 0–10 dk | Araç kontrolü ve iletişim rollerini belirleme | İstemci, sunucu, istek ve yanıtın kısa açıklaması |
| 10–25 dk | İlk GET isteği | Durum kodu, içerik türü ve gövde |
| 25–45 dk | JSON alanlarını okuma | Alan–değer–tür tablosu |
| 45–60 dk | Başka bir kayıt ve liste isteme | Yanıtların karşılaştırması |
| 60–75 dk | Bulunmayan kaydı inceleme | Başarı ve hata yanıtlarının açıklaması |
| 75–90 dk | Bağımsız çalışma ve değerlendirme | Kısa teslim metni |

## 4. İlk isteğini gönder

### Postman ile

1. Yeni bir HTTP isteği aç.
2. Metot olarak **GET** seç.
3. Adres alanına `https://jsonplaceholder.typicode.com/todos/1` yaz.
4. İstek gövdesini boş bırak; Authorization bölümünde **No Auth** seç.
5. **Send** düğmesine bas.
6. Yanıtın durum kodunu, yanıt **Headers** bölümündeki `Content-Type` değerini ve **Body** bölümündeki veriyi incele. Arayüz etiketleri sürüme göre biraz farklı olabilir.

### Terminal ile eşdeğer istek

```bash
curl --include --max-time 20 'https://jsonplaceholder.typicode.com/todos/1'
```

`--include`, yanıt başlıklarını da gösterir. `--max-time 20`, isteğin toplam bekleme süresini 20 saniyeyle sınırlar. Bu komutta curl varsayılan olarak GET kullanır. Tek tırnaklar adresi kabuğa tek parça olarak iletir.

Başarı durumunda `200` ve `Content-Type: application/json; charset=utf-8` beklenir. Başlık adlarının büyük/küçük harfle görünmesi fark yaratmaz. HTTP sürümü ve ek başlıklar kullandığın araca ve bağlantıya göre değişebilir.

7 Eylül 2026 tarihinde gözlenen gövde:

```json
{
  "userId": 1,
  "id": 1,
  "title": "delectus aut autem",
  "completed": false
}
```

Örnek başlığın metnini ezberleme; alanlara ve türlerine odaklan. `userId` görevin ilişkili olduğu kullanıcıyı, `id` görevin kendisini belirtir. `title` görev başlığı, `completed` tamamlanma durumudur.

**Dur ve düşün:** İsteği yapan yazılım hangisi? Yanıtı veren hizmet hangisi? Sen bu ilişkide istemci yazılımını kullanan insansın.

## 5. JSON'u oku

Aşağıdaki tabloyu kendi aldığın yanıta göre doldur:

| Alan | Gözlediğin değer | JSON türü | Anlamı |
|---|---|---|---|
| `userId` | … | … | … |
| `id` | … | … | … |
| `title` | … | … | … |
| `completed` | … | … | … |

Ardından cevapla:

1. En dış yapı nesne mi, dizi mi? Hangi işaretten anladın?
2. `completed: false`, alanın eksik olduğu anlamına mı gelir?
3. Sunucu `"completed": "false"` gönderseydi veri türü aynı kalır mıydı?
4. `userId` ile `id` bu örnekte aynı sayı. Bunların aynı kavram olduğunu söyleyebilir miyiz?

## 6. Kaynağı ve yanıt yapısını değiştir

Önce adresin sonundaki `1` yerine `2` yazarak yeni bir GET isteği gönder. Metot ve yetkilendirme ayarlarını değiştirme.

```bash
curl --include --max-time 20 'https://jsonplaceholder.typicode.com/todos/2'
```

İlk yanıtla karşılaştır: durum kodu, alan adları ve alan değerlerinden hangileri değişti? Özellikle `id` ve `title` değerlerini incele.

Şimdi aşağıdaki liste adresine GET isteği gönder:

```bash
curl --include --max-time 20 'https://jsonplaceholder.typicode.com/todos?userId=1'
```

Bu hizmette `userId=1`, kullanıcı kimliği 1 olan görevleri süzer. `?` sorgu bileşenini başlatır. Burada JSON gövdesi göndermiyorsun; filtreyi URL ile belirtiyorsun.

- Gövdenin ilk anlamlı karakteri `{` mı, `[` mı?
- Liste elemanlarının türü ne?
- İlk elemanın `id` ve `completed` değerlerini bul.
- Teori notundaki yardımcı yol gösterimini kullanarak ilk elemanın başlığını `[0].title` şeklinde tarif edebiliriz. Bu, çalıştırılacak JSON veya Python kodu değildir.

Kontrol tarihinde liste 20 görev içeriyordu. Bu sayı JSON'un bir kuralı değildir; hizmetin örnek verisine bağlıdır. Tüm listeyi teslimine kopyalaman gerekmiyor.

## 7. Bulunmayan bir kayıt iste

Şu adrese GET isteği gönder:

```bash
curl --include --max-time 20 'https://jsonplaceholder.typicode.com/todos/999999'
```

Kontrol tarihinde bu adres **404** ve aşağıdaki gövdeyi döndürdü:

```json
{}
```

`{}` boş bir JSON nesnesidir; boş dizi `[]` ile aynı değildir. Bu hizmetin hata gövdesinde açıklama metni bulunmuyor. Teorik kitap örneğindeki `hata` alanı bütün API'lerde zorunlu değildir.

Şu iki soruyu yazılı cevapla:

1. Gövde geçerli JSON olduğu hâlde neden başarılı bir kayıt okuma işlemi saymıyoruz?
2. 404 aldığına göre bir HTTP yanıtı geldi mi?

**Terminal ayrıntısı:** Bu komutlarda curl, HTTP 404 almasına rağmen sıfır çıkış koduyla bitebilir. Aracın aktarımı tamamlaması ile HTTP işleminin başarılı olması farklıdır. Bu çalışmada yanıtın HTTP durum kodunu incele.

### Bağlantı sorunu olursa

`Could not resolve host`, bağlantı kurulamaması veya zaman aşımı mesajı alırsan bunu `404` diye kaydetme. Bu durumda kullanılabilir bir HTTP yanıtı alınmamış veya aktarım tamamlanmamış olabilir. Adresi ve internet bağlantısını kontrol et; hata mesajını aynen not al.

Hizmet erişilemiyorsa yukarıdaki örnek gövdelerle JSON okuma görevlerini yapabilirsin. Tesliminde bunların **föydeki örnekler** olduğunu belirt; canlı istek bölümünü bağlantı sağlanınca tamamla. Beklenenlerden farklı bir yanıt alırsan kendi gözlemini kaydet ve eğitmenle değerlendir.

## 8. Bağımsız çalışma

`https://jsonplaceholder.typicode.com/todos/3` adresini kullanarak aşağıdaki kısa raporu hazırla:

```text
Kullandığım araç:
İstek metodu ve tam adresi:
Gözlediğim HTTP durum kodu:
Yanıtın Content-Type değeri:
JSON'un en dış yapısı:
Üç alanın adı, değeri ve türü:
İstemci ve sunucu rolleri:
Bulunmayan kayıt isteğiyle karşılaştırmam:
```

Ardından şu cümleyi tamamla: “JSON gelmesi tek başına başarıyı göstermez, çünkü …”

## 9. Teslim ve değerlendirme

Tabloyu, bağımsız çalışma raporunu ve 7. bölümdeki iki cevabını kısa bir Markdown metni olarak teslim et. Ekran görüntüsü zorunlu değildir; kullanılan adresler ve gözlenen sonuçlar yeterlidir. Bire bir çalışmada cevaplarını sohbet içinde paylaşabilirsin.

| Ölçüt | Puan |
|---|---:|
| Metodu, adresi ve istemci–sunucu rollerini doğru belirtme | 2 |
| Durum kodunu, içerik türünü ve gövdeyi ayırt etme | 2 |
| Alanları ve JSON türlerini doğru okuma | 2 |
| Tek nesne ile listeyi ayırt etme | 2 |
| 404 ile bağlantı sorununu gerekçeli ayırma | 2 |
| **Toplam** | **10** |

### Çalışmayı bitirdikten sonra kısa kontrol

- İlk yanıt nesnedir. `userId` ve `id` sayı, `title` metin, `completed` mantıksal değerdir.
- `false`, tamamlanmamış olmayı bildirir; eksik alan değildir. `"false"` ise metindir.
- Liste yanıtı dizidir ve görev nesneleri içerir.
- 404 bir HTTP yanıtıdır. Bu örnekte istenen görev bulunamamıştır. Bağlantı hatasıyla aynı durum değildir.

## 10. Kaynak ve doğrulama

[JSONPlaceholder resmî rehberi](https://jsonplaceholder.typicode.com/guide/) kaynak okuma ve filtreleme işlemlerini açıklar. Bu föydeki `/todos/1`, `/todos/2`, `/todos/3`, `/todos?userId=1` ve `/todos/999999` adresleri 7 Eylül 2026 tarihinde canlı GET istekleriyle kontrol edilmiştir. Dış hizmetin verileri ve erişilebilirliği zamanla değişebilir.

Postman adımları için: [Postman resmî başlangıç rehberi](https://learning.postman.com/docs/getting-started/quick-start/).

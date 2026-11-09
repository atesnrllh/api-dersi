# Ek Not — Veritabanında Arama: Python'dan İki Fark

Föyün Deney 3'ünde kitap aramasını Python'dan veritabanına taşıdık: `casefold()` karşılaştırmasının yerini `icontains` aldı. Föydeki aramalarda iki yol aynı sonucu verdi. Bu notta sonucun ayrışabildiği iki durumu görüyoruz: Türkçe harfler ve `%`, `_` işaretleri.

---

## 1. Türkçe harfler

Aynı aramaları Hafta 5'in sonundaki sunucuya ve bu haftanın sunucusuna gönderdik. Tabloda bulunan kitapların kimlikleri var; 57 numaralı kitabın adı "Veriyle İlk Adımlar", 42 numaralınınki "API Yolculuğu".

| `search` | Hafta 5 (`casefold()`) | Hafta 6 (`icontains`) |
|---|---|---|
| `ilk` | `[]` | `[57]` |
| `İlk` | `[57]` | `[57]` |
| `İLK` | `[57]` | `[57]` |
| `adım` | `[57]` | `[57]` |
| `ADIM` | `[]` | `[]` |
| `yolculuğu` | `[42]` | `[42]` |
| `YOLCULUĞU` | `[42]` | `[42]` |

Yalnızca ilk satırda sonuçlar farklı.

İki yol da büyük-küçük harf farkını ortadan kaldırmak için harfleri küçültür, ama `İ` harfini farklı küçültür:

- Python'un `casefold()` metodu `İ` harfini iki karaktere çevirir: `i` ve onun üstündeki noktayı gösteren ayrı bir işaret. Bu yüzden "İlk" küçültülünce "i" ile "lk" arasında bir işaret kalır ve "ilk" araması onu bulamaz.
- PostgreSQL ise `İ` harfini doğrudan `i` yapar; "ilk" araması kitabı bulur.

`ADIM` aramasında iki yol da başarısız, çünkü ikisi de `I` harfini Türkçedeki gibi `ı` değil, İngilizcedeki gibi `i` yapar: "ADIM" küçültülünce "adim" olur, kitabın adında ise "Adım" yazıyor.

---

## 2. `%` ve `_` işaretleri

`icontains`, veritabanına bir `ILIKE` komutu gönderir: "Adında şu metin geçen kayıtlar." Bu komutta iki işaretin özel bir anlamı vardır:

| İşaret | `ILIKE` komutundaki anlamı |
|---|---|
| `%` | Herhangi bir metin, boş metin de olabilir |
| `_` | Herhangi tek bir karakter |

Föydeki `get_books` fonksiyonunda `autoescape=True` yazdık; bu ayar, aranan metindeki `%` ve `_` işaretlerini sıradan harf gibi aratır. Ayarı silip aynı aramaları üç sunucuya gönderdik:

| `search` | Hafta 5 | Hafta 6, föydeki gibi | Hafta 6, `autoescape=True` olmadan |
|---|---|---|---|
| `_` | `[]` | `[]` | `[42, 57, 73]` |
| `%` | `[]` | `[]` | `[42, 57, 73]` |
| `a_i` | `[]` | `[]` | `[42, 73]` |
| `api` | `[42, 73]` | `[42, 73]` | `[42, 73]` |

Ayar olmadan `_` araması bütün kitapları getirdi: Adında en az bir karakter olan her kitap "herhangi tek bir karakter" koşuluna uyuyor. `a_i` araması da "API" geçen iki kitabı buldu, çünkü `_` işareti `P` harfinin yerini tuttu. Hiçbir kitabın adında `_` yok; Hafta 5'teki sunucu bu yüzden boş liste döndürüyordu.

`autoescape=True` ile veritabanı bu iki işareti, adında gerçekten `%` ya da `_` geçen kitaplar için arar; sonuçlar Hafta 5'tekiyle aynı oldu.

---

## 3. Bundan ne öğreniyoruz?

Bir işi koddan veritabanına taşıdığımızda sonucun her durumda aynı kalacağını varsayamayız. Föydeki istemciler aynı çıktıyı verdi, çünkü aramalar sıradan İngilizce kelimelerdi. Türkçe metinlerle çalışan gerçek bir uygulamada bu tür aramalar ayrıca denenmeli; veritabanına Türkçe harf kurallarını kullanmasını söyleyen ayarlar da vardır. Aramaları otomatik testlerle tekrar tekrar denemeyi Hafta 7'de göreceğiz.

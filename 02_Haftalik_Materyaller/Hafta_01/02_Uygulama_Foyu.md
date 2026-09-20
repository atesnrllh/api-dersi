# Hafta 01 — Uygulama Föyü

## Çalışan İlk Kitap Kataloğu API'si: Sunucu, İstemci, HTTP ve JSON

**Ders:** Uygulama Programı Arayüzü (API)

**Düzey:** API konusunda başlangıç

**Ana araçlar:** VS Code, Python 3.10+, FastAPI, Uvicorn, HTTPX ve uv

**Sürüm:** 2.0 — 11 Eylül 2026

> Bu föy yalnızca çalışacak kodu vermez. Her deneyde önce **neyi ve neden yaptığımızı**, sonra değişen satırları, dosyanın tam hâlini, beklenen gözlemi ve çıkarılacak sonucu gösterir. Kodu bir defada kopyalayıp geçmek yerine her deneyin sorusunu cevaplayarak ilerle.

> **Kod renkleri:** “Değişen satırlar” başlıklı `diff` kutularında silinen satırlar `-`, eklenen satırlar `+` ile gösterilir. GitHub ve destekleyen editörler bunları genellikle kırmızı ve yeşil renklendirir. Hemen altındaki Python kutusu ise değişiklikten sonra dosyada bulunması gereken kodun tamamıdır.

## Uygulamanın amacı ve kapsamı

Bu çalışmada iki Python dosyası yazacağız: `client.py` ve `server.py`. `.py` uzantısı, dosyanın Python kodu içerdiğini gösterir. Bu dosyalardaki kodlar çalıştırıldığında iki ayrı program aynı bilgisayarda farklı roller üstlenecek:

- **İstemci (client) — `client.py`:** Bilgi isteyen programdır. Örneğin, sunucudan 42 numaralı kitabın bilgilerini ister.
- **Sunucu (server) — `server.py`:** İsteği karşılayan API uygulamasını içerir. Bu uygulamayı Uvicorn ile çalıştıracağız. Uygulama, istenen kitabı bulur ve bilgilerini istemciye gönderir.

Bu iki program **HTTP** adı verilen iletişim kurallarına göre mesajlaşır. İstemcinin gönderdiği mesaja **istek (request)**, sunucunun bu isteğe verdiği cevaba **yanıt (response)** denir.

Çalışmanın sonunda şunları yapabilmelisin:

- VS Code'da proje klasörü, dosya ve terminal düzenini kurmak.
- Projeye özel Python sanal ortamı oluşturup paketleri bu ortama kurmak.
- FastAPI ile GET isteği karşılayan küçük bir sunucu yazmak.
- HTTPX ile bu sunucuya istek gönderen istemci yazmak.
- Yol parametresiyle tek kitap, koleksiyon yolu ile kitap listesi istemek.
- `200`, `404`, `422` ve bağlantı hatasını birbirinden ayırmak.
- JSON nesnesi, dizisi, metni, sayısı, mantıksal değeri ve `null` değerini uygulamada okumak.
- Sorgu parametreleriyle başlık araması ve ödünç alınabilirlik filtresi yapmak.
- `Accept` ile `Content-Type` başlıklarının farklı görevlerini açıklamak.
- Geçersiz JSON, yanlış veri türü ve iş kuralına aykırı değeri ayırmak.

## VS Code'da başlangıç düzenini kur

### Ne yapıyoruz, neden yapıyoruz?

Kodlarımızı ve Python ortamımızı tek bir proje klasöründe düzenliyoruz. VS Code'da doğru klasörü açmak, terminal komutlarının ve dosya yollarının aynı proje üzerinde çalışmasını sağlar.

API tek bir ekran değildir; arkasında çalışan istemci ve sunucu kodları vardır. Bu bölüm o kodların çalışma ortamını hazırlar.

### Proje klasörünü aç

1. Masaüstünde `book-catalog-api` adlı klasör oluştur.
2. VS Code'da **File → Open Folder** ile bu klasörü aç.
3. **Terminal → New Terminal** ile terminal aç.
4. Linux veya WSL terminalinde bulunduğun yeri kontrol et:

```bash
pwd
```

Örnek sonuç:

```text
/home/nuri/Desktop/book-catalog-api
```

Windows klasörünü WSL üzerinden açtıysan yol `/mnt/c/Users/.../book-catalog-api` biçiminde de olabilir. Önemli olan son bölümün proje klasörünü göstermesidir.

Klasörü daha önce `API` adıyla oluşturduysan yeniden oluşturman gerekmez; terminaldeki yolun o klasörü göstermesi yeterlidir. Projeye özel `book-catalog-api` adı, klasörün ne içerdiğini daha açık anlatır.

VS Code'un solundaki **Explorer** bölümünde **New File** düğmesini kullanarak `server.py` ve `client.py` dosyalarını oluştur. Kodu değiştirdikten sonra **Ctrl+S** ile dosyayı kaydet; terminal, diske kaydedilmiş sürümü çalıştırır.

### Python'u kontrol et

```bash
python3 --version
```

Bu föydeki `bool | None` tür gösterimi için Python 3.10 veya daha yeni bir sürüm kullan.

### Sanal ortamı oluştur

```bash
python3 -m venv api-env
```

Sanal ortam, bu projenin Python paketlerini diğer projelerden ayırır. Ayrı bir bilgisayar veya sanal makine değildir; proje için Python çalıştırıcısı ve paket klasörleri sağlar.

Oluşacak düzen:

```text
book-catalog-api/
├── api-env/      ← sanal ortam; uygulama kodunu buraya yazma
├── server.py     ← birazdan oluşturulacak
└── client.py     ← birazdan oluşturulacak
```

Ortamı etkinleştir:

```bash
source api-env/bin/activate
```

Terminal satırının başında `(api-env)` görünmelidir. Sunucu ve istemci aynı projenin parçaları olduğu için aynı ortamı kullanabilir.

### uv aracını kur ve doğrula

Önce kontrol et:

```bash
uv --version
```

Komut bulunamazsa Linux veya WSL üzerinde uv'nin resmî kurucusunu çalıştır:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Mevcut terminal uv'yi bulamazsa:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Ardından yeniden kontrol et:

```bash
uv --version
```

> Bazı kurulum çıktıları `source "$HOME/.local/bin/env"` önerebilir. Bu dosya sisteminde yoksa yukarıdaki `export PATH=...` komutunu kullan. Bu komut yalnızca açık terminalin komut arama yolunu günceller.

### Paketleri proje ortamına kur

```bash
uv pip install --python api-env/bin/python fastapi uvicorn httpx
```

**Paket nedir?** Python projemize kurup kullanabildiğimiz hazır yazılımdır. Başka geliştiricilerin hazırladığı araçları kullanarak her işlemi sıfırdan yazmak zorunda kalmayız. Yukarıdaki komutta `uv`, kurulum işlemini yapan araçtır; `fastapi`, `uvicorn` ve `httpx` ise kurduğumuz üç pakettir. Aşağıdaki tabloda bu dört aracın görevleri açıklanmıştır:

| Araç / paket | Nedir? | Bu uygulamadaki görevi |
|---|---|---|
| **[uv](https://docs.astral.sh/uv/)** | Python projelerinin ihtiyaç duyduğu paketleri kurmak, güncellemek ve yönetmek için terminalden kullanılan bir **paket ve proje yönetim aracıdır**. Bir paketin çalışması için gereken diğer paketlere **bağımlılık (dependency)** denir; uv kurulum sırasında bunları da belirler ve kurar. Ayrıca projeye özel sanal ortamlar oluşturabilir. | Bu föyde `api-env` adlı sanal ortamı Python'un `venv` aracıyla oluşturduk. uv'yi, FastAPI, Uvicorn ve HTTPX paketlerini bu ortama kurmak için kullanıyoruz. Komuttaki `--python api-env/bin/python`, paketlerin hangi Python ortamına kurulacağını belirtir. uv bu aşamada geliştirme ortamımızı hazırlar; kitap isteğini karşılayan uygulamayı çalıştırma görevini Uvicorn üstlenir. |
| **[FastAPI](https://fastapi.tiangolo.com/tutorial/first-steps/)** | Python ile web API'leri geliştirmek için kullanılan bir **uygulama çatısıdır (framework)**. Uygulama çatısı, kodumuzu belirli bir düzen içinde yazmamızı sağlayan hazır bir yapı ve araçlar sunar. FastAPI ile hangi adrese gelen isteğin hangi Python fonksiyonunu çalıştıracağını tanımlarız. | `server.py` içindeki API uygulamasını FastAPI ile yazacağız. Kitap bilgisini isteyen bir istek geldiğinde, FastAPI tanımladığımız uygun fonksiyonu çalıştıracak. Kitabı bulma işlemini bu fonksiyonun içinde biz yazacağız. FastAPI, fonksiyonun döndürdüğü kitap sözlüğünü JSON biçiminde bir yanıta dönüştürecek. |
| **[Uvicorn](https://uvicorn.dev/)** | Python ile yazılmış web uygulamalarının HTTP üzerinden erişilebilir olmasını sağlayan bir **sunucu programıdır**. Belirli bir adres ve bağlantı noktasında (**port**) istemcilerin bağlantı kurmasını bekler. “Bağlantıları dinlemek” ifadesi bu bekleme ve gelen bağlantıları kabul etme işini anlatır. | `server.py` içinde yazdığımız FastAPI uygulamasını Uvicorn ile çalıştıracağız. Uvicorn, istemciden gelen HTTP isteğini uygulamaya aktaracak ve uygulamanın hazırladığı yanıtı istemciye gönderecek. Çalışmaya devam ettiği sürece yeni istekleri kabul edebilecek; bu nedenle sunucu terminalini açık tutacağız. |
| **[HTTPX](https://www.python-httpx.org/quickstart/)** | Python programından HTTP istekleri göndermek ve yanıtları almak için kullanılan bir **istemci kütüphanesidir (client library)**. Kütüphane, kendi kodumuzdan çağırabildiğimiz hazır işlevler sunar. HTTPX ile isteğin gönderileceği adresi belirtir ve gelen yanıtı programımızda inceleyebiliriz. | `client.py` içinde HTTPX kullanarak kitap bilgisi isteyeceğiz. HTTPX, isteği sunucuya gönderecek ve gelen yanıtı kodumuzda kullanabileceğimiz bir nesne olarak verecek. Bu nesne üzerinden işlemin sonucunu belirten durum kodunu okuyabilecek, JSON biçimindeki kitap bilgilerini Python verisine dönüştürebileceğiz. Kitap başlığını terminale yazdıran kodu biz yazacağız. |

**Bu araçlar birlikte nasıl kullanılır?** uv ile gerekli paketleri projenin sanal ortamına kurarız. Sunucu tarafında FastAPI ile isteğe verilecek cevabın nasıl hazırlanacağını tanımlarız; Uvicorn bu uygulamanın istemcilerden istek alıp yanıt göndermesini sağlar. İstemci tarafında ise HTTPX kullanarak bu uygulamaya ulaşırız. Böylece sunucu uygulamasını yazma, uygulamayı erişime açma ve istemciden istek gönderme görevleri için ayrı araçlar kullanmış oluruz.

`Failed to hardlink files; falling back to full copy` uyarısı görülürse kurulum başarısız olmuş sayılmaz. Önbellek ve proje farklı dosya sistemlerindeyse uv dosyaları kopyalayarak devam edebilir.

### İki terminal kullan

- **Sunucu terminali:** Uvicorn çalışır ve istek bekler. Bu terminal komut satırına dönmeden açık kalır.
- **İstemci terminali:** `client.py` çalıştırılır ve yeni istekler gönderilir.

Yeni terminal açıldığında sanal ortamı yeniden etkinleştir:

```bash
source api-env/bin/activate
```

Python dosyalarını klasik anlamda ayrıca derlemeyeceğiz. Python yorumlayıcısıyla çalıştıracağız.

VS Code'un terminal listesinde sunucu terminalinin adı çalışırken `python`, istemci terminalinin adı ise `bash` görünebilir. İki terminal de Bash veya WSL kabuğuyla açılmıştır. Uvicorn önde çalışmaya devam ettiği için ilk terminal o anki işlemin adını gösterir; `client.py` bitip komut satırına döndüğü için ikinci terminal yeniden kabuğun adını gösterir.

<a id="sunucu-surec-yonetimi"></a>

#### Sunucuyu kapatma, PID bulma ve dolu portu boşaltma

Sunucuyu çalıştırdıktan sonra durdurup yeniden başlatman gerekebilir. Bu işlemleri WSL/Bash terminalinde yapıyoruz. Sunucu terminali komut almıyorsa kontrol komutlarını ikinci terminalde çalıştırabilirsin.

| İşlem veya kavram | Anlamı |
|---|---|
| **Süreç (process)** | İşletim sisteminde çalışan program örneğidir. Uvicorn sunucusu bir süreç olarak çalışır. |
| **PID — süreç kimliği** | İşletim sisteminin süreci tanımak için verdiği numaradır. Sunucu yeniden başlatıldığında değişebilir. |
| **Port** | İstemcinin sunucuya bağlanmak için kullandığı numaralı bağlantı noktasıdır. Bu derste `8000` portunu kullanıyoruz. |
| **Ctrl+C** | Bu örnekte ön planda çalışan Uvicorn'a kapanma isteği gönderir. Normal kapatma için sunucu terminalinde bunu kullanırız. |
| **Ctrl+Z** | Ön plandaki süreci duraklatır. Süreç sona ermez; açık bağlantı noktası üzerinde sahipliği devam edebilir. |

**Terminalde yeniden `$` görünmesi tek başına sunucunun kapandığını kanıtlamaz.** Ctrl+Z ile duraklatılan bir sunucu da terminali komut almaya bırakabilir. Normal kapatmada Ctrl+C'ye basıp kapanış mesajlarının tamamlanmasını bekle.

##### `address already in use` hatası ne demek?

Örneğin yeniden başlatırken şöyle bir çıktı görülebilir:

```text
INFO:     Started server process [2237]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
ERROR:    [Errno 98] error while attempting to bind on address ('127.0.0.1', 8000): address already in use
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
```

Yeni süreç başlamış, fakat `127.0.0.1:8000` adresinde bağlantı kabul etmeye geçememiştir; portu başka bir süreç kullanmaktadır. Buradaki `2237`, yeni başlatma denemesinin PID'sidir. Portu elinde tutan eski sürecin PID'sini ayrıca bulmalıyız. `Application startup complete` mesajından sonra hata geldiği için yalnızca bu başlangıç mesajına bakarak sunucunun erişilebilir olduğunu düşünmemeliyiz.

##### Portu kullanan PID'yi bul ve komutunu doğrula

```bash
ss -ltnp 'sport = :8000'
```

Bu komut `8000` portundaki dinleyen TCP soketlerini ve görülebilen süreç bilgilerini listeler. Örnek çıktı:

```text
State  Recv-Q  Send-Q  Local Address:Port  Peer Address:Port  Process
LISTEN 0       2048    127.0.0.1:8000      0.0.0.0:*          users:(("python",pid=2106,fd=6))
```

| Çıktıdaki bölüm | Anlamı |
|---|---|
| `LISTEN` | Bu portta bağlantı kabul etmek üzere açılmış bir soket var. Sahibi olan sürecin duraklatılmamış olduğunu tek başına garanti etmez. |
| `127.0.0.1:8000` | Kullanımda olan yerel adres ve port. |
| `"python"` | Soketi tutan süreç için gösterilen program adı. Uvicorn'u Python üzerinden başlattığımız için bu adı görebiliriz. |
| `pid=2106` | Portu kullanan sürecin kimlik numarası: **2106**. PID, satırın sağ tarafındaki `Process` sütunundadır. |
| `fd=6` | Sürecin bu açık soket için kullandığı dosya tanıtıcısıdır. Kapatma komutunda kullanacağımız sayı PID'dir. |

`ss` komutundaki `-l` dinleyen soketleri, `-t` TCP'yi, `-n` sayısal adres ve port gösterimini, `-p` süreç bilgisini seçer. [Linux `ss` belgesi](https://man7.org/linux/man-pages/man8/ss.8.html).

**Aşağıdaki komutlardaki `2106` yalnızca bu çıktının örnek PID'sidir. Kendi güncel çıktındaki numarayı kullan.** Önce bu sürecin gerçekten bizim sunucumuz olduğunu kontrol et:

```bash
ps -p 2106 -o pid,stat,args
```

| Sütun | Ne gösterir? |
|---|---|
| `PID` | Seçtiğimiz süreç numarasını. |
| `STAT` | Sürecin durumunu. `T`, iş denetimiyle duraklatılmış süreci belirtir. `Tl` gibi bir gösterimde `T` aynı anlama gelir; küçük `l` ek bir süreç özelliğidir. |
| `COMMAND` | Sürecin çalıştırıldığı komutu ve argümanlarını. Burada `python -m uvicorn server:app` gibi bizim sunucu komutumuzu görmeliyiz. |

`-p` PID'yi seçer; `-o pid,stat,args` görmek istediğimiz sütunları belirler. [Linux `ps` belgesi](https://man7.org/linux/man-pages/man1/ps.1.html).

##### Doğru sürece kapanma isteği gönder

Portu kullanan sürecin bizim Uvicorn sunucumuz olduğunu doğruladıktan sonra:

```bash
kill -TERM 2106
```

`kill`, bir sürece sinyal gönderir; `TERM`, kapanma isteğidir. Komutun sessizce bitmesi, sürecin kapanışını tamamladığını tek başına göstermez.

**`STAT` değeri `T` veya `Tl` ise:** Duraklatılmış Uvicorn, kapanma isteğini işleyebilmek için yeniden çalışmaya devam etmelidir. Önce kapanma isteğini gönderip sonra duraklamayı kaldırırız:

```bash
kill -TERM 2106
kill -CONT 2106
```

`CONT`, duraklatılmış süreci devam ettirir; yeni bir sunucu başlatmaz. Böylece süreç bekleyen kapanma isteğini işleyebilir. Bu adım duraklatılmış süreç içindir; `address already in use` hatasının her zaman Ctrl+Z'den kaynaklandığını varsaymayız. [Linux sinyalleri](https://man7.org/linux/man-pages/man7/signal.7.html).

##### Portun boşaldığını doğrula, sonra yeniden başlat

```bash
ss -ltnp 'sport = :8000'
```

Başlığın altında `LISTEN` satırı kalmadığında portu dinleyen süreç görünmüyor demektir. Satır hâlâ varsa kapanışın tamamlanmasını bekleyip yeniden kontrol et; PID değişmişse yeni sürecin komutunu da doğrula.

Proje klasöründe, `api-env` etkin durumdayken sunucuyu yeniden başlat:

```bash
python -m uvicorn server:app
```

Başarılı başlangıçta `Uvicorn running on http://127.0.0.1:8000` mesajını görürsün. Sunucu terminalini açık bırakıp istemciyi ikinci terminalden çalıştır.

## Deney 1 — İlk API sunucusunu yaz

### Ne yapıyoruz?

Sunucunun belleğinde bir kitap sözlüğü tutuyor ve yalnızca `/api/books/42` adresindeki GET isteğine cevap veren bir işlem tanımlıyoruz.

### Neden yapıyoruz?

API tanımındaki **işlem, girdi ve sonuç** kavramlarını çalışan bir programda görmek istiyoruz. İlk örneği küçük tutarak istemci–sunucu iletişimine odaklanıyoruz.

Bu aşamada veritabanı yoktur. Kitap bilgisi `server.py` içindeki Python sözlüğünde tutulur. Sunucu yeniden başladığında veri koddan yeniden yüklenir.

### Yeni dosya — değişen satırlar

```diff
+ from fastapi import FastAPI
+
+ app = FastAPI()
+
+ book = {
+     "id": 42,
+     "title": "API Yolculuğu",
+     "author": "Deniz Kaya"
+ }
+
+
+ @app.get("/api/books/42")
+ def get_book():
+     return book
```

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI

app = FastAPI()

book = {
    "id": 42,
    "title": "API Yolculuğu",
    "author": "Deniz Kaya"
}


@app.get("/api/books/42")
def get_book():
    return book
```

### Sunucuyu çalıştır

`server.py` dosyasının bulunduğu proje klasöründe, sanal ortam etkin durumdayken şu komutu yaz:

```bash
python -m uvicorn server:app
```

#### Komutun parçaları ne anlama geliyor?

| Parça | Anlamı | Bu komuttaki görevi |
|---|---|---|
| `python` | Python kodunu çalıştıran yorumlayıcıyı başlatır. | Önceki adımda `api-env` sanal ortamını etkinleştirdiğimiz için bu ortamın Python yorumlayıcısını kullanırız. |
| `-m` | Python'a, adı verilen modülü veya paketi bulup program olarak çalıştırmasını söyler. | Burada çalıştırılacak paket `uvicorn`dur. Böylece Uvicorn'u seçtiğimiz Python ortamı üzerinden başlatırız. |
| `uvicorn` | HTTP bağlantılarını kabul eden ve web uygulamamızı çalıştıran sunucu programıdır. | FastAPI ile yazdığımız uygulamanın istemcilerden istek almasını sağlar. |
| `server` | Uygulamanın bulunduğu Python modülünün adıdır. Bu örnekte `server.py` dosyasına karşılık gelir. | Uvicorn, içinde bulunduğumuz klasördeki `server.py` dosyasını Python üzerinden yükler. Komutta `.py` uzantısını yazmayız. |
| `:` | Modül adı ile o modüldeki uygulamanın adını ayırır. | `server:app`, “`server` modülünün içindeki `app` adlı uygulamayı kullan” demektir. |
| `app` | `server.py` içinde `app = FastAPI()` satırıyla oluşturduğumuz uygulama nesnesinin adıdır. | Uvicorn hangi uygulamayı çalıştıracağını bu addan anlar. |

Komutun tamamını şöyle okuyabiliriz: **“Bu Python ortamındaki Uvicorn'u başlat ve `server.py` dosyasındaki `app` uygulamasını çalıştır.”**

`app`, kendi kodumuzda verdiğimiz bir değişken adıdır. `app = FastAPI()` satırı, FastAPI uygulamasını oluşturur ve ona `app` adıyla ulaşmamızı sağlar. Komuttaki adın dosyadaki adla eşleşmesi gerekir. [Python'da `-m` kullanımı](https://docs.python.org/3/using/cmdline.html#cmdoption-m) ve [Uvicorn uygulama seçimi](https://uvicorn.dev/settings/#application) bu yazımın başvuru kaynaklarıdır.

#### Komuttan sonra terminalde görünen satırlar

Aşağıdaki örnekte ilk satır, terminalin komut satırı ve yazdığımız komuttur. `INFO:` ile başlayan dört satırı ise Uvicorn üretir:

```text
(api-env) nuri@Esra:/mnt/c/Users/MONSTER/Desktop/book-catalog-api$ python -m uvicorn server:app
INFO:     Started server process [13821]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

| Terminaldeki satır | Türkçe anlamı | Bu aşamada ne oluyor? |
|---|---|---|
| `(api-env) nuri@Esra:/mnt/c/Users/MONSTER/Desktop/book-catalog-api$ python -m uvicorn server:app` | Etkin sanal ortam ve bulunduğumuz klasör gösteriliyor; ardından sunucuyu başlatma komutunu çalıştırıyoruz. | `$` işaretinin solundaki bölümü terminal kendisi gösterir. Biz yalnızca `python -m uvicorn server:app` kısmını yazar ve Enter'a basarız. |
| `INFO: Started server process [13821]` | “Sunucu süreci başlatıldı. Süreç numarası: 13821.” | İşletim sistemi, çalışan programı **süreç (process)** olarak takip eder. `13821`, bu çalıştırmadaki sürecin kimlik numarasıdır (**PID**). Başka bir çalıştırmada farklı olabilir. |
| `INFO: Waiting for application startup.` | “Uygulamanın başlangıç işlemlerinin tamamlanması bekleniyor.” | Uvicorn, FastAPI uygulamasının başlangıç aşamasını tamamlamasını bekler. Buradaki bekleme, uygulamanın hazırlanmasıyla ilgilidir. |
| `INFO: Application startup complete.` | “Uygulamanın başlangıç işlemleri tamamlandı.” | Uygulama başlangıç aşamasını başarıyla geçmiştir. Ardından sunucu belirtilen adreste bağlantı kabul etmeye başlar. |
| `INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)` | “Uvicorn bu adreste çalışıyor. Çıkmak için Ctrl+C'ye basın.” | Sunucu `127.0.0.1` adresindeki `8000` numaralı portta bağlantı bekliyor. Sunucuyu durdurmak istediğimizde bu terminalde Ctrl+C'ye basarız. |

**`INFO` ne demek?** “Information” sözcüğünün kısaltmasıdır ve mesajın bilgilendirme düzeyinde olduğunu gösterir. Programın çalışırken ürettiği bu kayıtlara **günlük kaydı (log)** denir. Yukarıdaki dört kayıt, sunucunun normal başlangıç adımlarını bildirir.

**Başlangıçta ne hazırlanıyor?** Uygulamalar, isteklere cevap vermeden önce bazı hazırlıklar yapabilir. Örneğin başka bir uygulamada başlangıç sırasında bir veritabanına bağlantı kurulabilir. Bizim ilk örneğimizde ayrıca böyle bir hazırlık kodu yazmadık; yine de FastAPI uygulamasının başlangıç aşaması vardır ve bu iki mesaj görülebilir. Bu aşama, henüz bir kitap isteği gönderildiği veya bir kitabın bulunduğu anlamına gelmez. [Uvicorn başlangıç ve kapanış süreci](https://uvicorn.dev/concepts/lifespan/).

#### İlk satırdaki terminal bilgilerinin ayrıntısı

| Görünen bölüm | Anlamı |
|---|---|
| `(api-env)` | `api-env` adlı Python sanal ortamının bu terminalde etkin olduğunu gösterir. |
| `nuri` | Bu örnekte Linux/WSL oturumundaki kullanıcı adıdır. Sende farklı olabilir. |
| `@Esra` | `@` işaretinden sonraki `Esra`, bu oturumda gösterilen sistem adıdır. Sende farklı olabilir. |
| `:` | Kullanıcı ve sistem bilgisini, bulunulan klasör yolundan ayırır. |
| `/mnt/c/Users/MONSTER/Desktop/book-catalog-api` | Terminalin o anda içinde bulunduğu proje klasörüdür. WSL'deki `/mnt/c`, Windows'un `C:` sürücüsüne erişim yoludur. Bu örnek Windows tarafında `C:\Users\MONSTER\Desktop\book-catalog-api` klasörüne karşılık gelir. |
| `$` | Bu örnekte komut yazılacak yerin başladığını gösteren kabuk istemi işaretidir. Komutun parçası olarak yazılmaz. |

Kullanıcı adı, sistem adı ve klasör yolu kendi bilgisayarına göre değişebilir. Komutu bu uygulamanın `server.py` dosyasının bulunduğu klasörde çalıştırmalısın.

#### Sunucu adresinin ayrıntısı

| Adresin bölümü | Anlamı |
|---|---|
| `http://` | İletişimde HTTP protokolünün kullanılacağını belirtir. |
| `127.0.0.1` | Yerel geri dönüş (**loopback**) adresidir. Bu adresi kullanan programın kendi çalıştığı ağ ortamını gösterir. Bu derste sunucu ve istemci aynı WSL ortamında çalışır. |
| `:8000` | Bağlanılacak portun `8000` olduğunu belirtir. **Port**, aynı ağ adresindeki hizmetlere ulaşmak için kullanılan numaralı bağlantı noktasıdır. İstemci bu numarayla bizim sunucumuza ulaşır. |

Bu komutta adres ve port için ayrı seçenek vermedik. Uvicorn, varsayılan olarak `127.0.0.1` ve `8000` değerlerini kullanır. `13821` işletim sisteminin çalışan süreci tanıdığı numaradır; `8000` ise istemcinin bağlantı kurarken kullandığı port numarasıdır. [Uvicorn adres ve port ayarları](https://uvicorn.dev/settings/#socket-binding).

**Terminal neden yeni komut istemiyor?** Sunucu çalışmaya devam ederek istek bekler; bu nedenle terminal hemen yeniden `$` işaretini göstermez. Bu, programın takıldığı anlamına gelmez. Sunucu terminalini açık bırak ve bir sonraki bölümde istemciyi ikinci terminalden çalıştır. Ctrl+C ile sunucuyu durdurduğunda bu terminal tekrar komut almaya döner.

### Deneyin sonucu

API ayrı bir makine değildir. Bu örnekte API, istemci programın kitap bilgisi isteyebilmesini sağlayan arayüzdür; `server.py` içindeki FastAPI uygulamasında bu isteğin hangi adrese, hangi HTTP metoduyla gönderileceğini ve karşılığında hangi bilgilerin döneceğini tanımlarız. Uvicorn bu uygulamayı çalıştırır.

## Deney 2 — İlk istemciyi yaz

### Ne yapıyoruz?

İkinci Python programından sunucuya GET isteği gönderiyor ve dönen JSON içindeki kitap başlığını gösteriyoruz.

### Neden yapıyoruz?

API'yi başka bir yazılımın kullandığını görmek istiyoruz. İnsan `client.py` programını çalıştırır; HTTP isteğini oluşturan taraf istemci yazılımıdır.

### Yeni dosya — değişen satırlar

```diff
+ import httpx
+
+ response = httpx.get("http://127.0.0.1:8000/api/books/42")
+ book = response.json()
+ print(book["title"])
```

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books/42")
book = response.json()
print(book["title"])
```

#### İstemci kodunun satır satır açıklaması

| Satır | Kod | Açıklaması |
|---|---|---|
| 1 | `import httpx` | Önceden kurduğumuz HTTPX kütüphanesini bu dosyada kullanıma açar. Bundan sonra kütüphanenin sunduğu işlevlere `httpx` adı üzerinden ulaşabiliriz. |
| 2 | Boş satır | Kütüphaneyi içeri aktardığımız satır ile işlemleri yapan satırları görsel olarak ayırır. Python bu satırda bir işlem yapmaz. |
| 3 | `response = httpx.get("http://127.0.0.1:8000/api/books/42")` | Belirtilen adrese HTTP GET isteği gönderir. Bu örnekte 42 numaralı kitabın bilgilerini isteriz. Yanıt geldiğinde HTTPX'in döndürdüğü yanıt nesnesini `response` adlı değişkene atarız. |
| 4 | `book = response.json()` | Alınmış yanıtın gövdesindeki JSON verisini Python'un kullanabileceği bir veri yapısına dönüştürür. Bu örnekte tek bir kitap nesnesi geldiği için sonuç bir Python sözlüğüdür (`dict`). Bu sözlüğü `book` adlı değişkene atarız. |
| 5 | `print(book["title"])` | `book` sözlüğündeki `title` anahtarının karşılığı olan kitap başlığını alır ve terminale yazdırır. |

#### Üçüncü satırdaki adres ve atama işlemi

`httpx.get(...)`, HTTPX'in GET isteği gönderen fonksiyonunu çağırır. Parantez içindeki, tırnaklar arasında yazılmış metin isteğin gönderileceği adrestir:

| Adresin bölümü | Bu örnekteki anlamı |
|---|---|
| `http://` | İstek HTTP protokolüyle gönderilir. |
| `127.0.0.1` | İstemcinin kendi çalıştığı ağ ortamını gösterir. Sunucuyu da aynı WSL ortamında çalıştırdığımız için bu adresi kullanırız. |
| `:8000` | İstemci, sunucunun bağlantı beklediği `8000` numaralı porta bağlanır. |
| `/api/books/42` | Sunucu uygulamasında tanımladığımız yoldur. Biz bu yolu 42 numaralı kitabın bilgilerini vermek için tanımladık. |

`=` işareti **atama** yapar: önce sağ taraftaki işlem gerçekleştirilir, ardından sonucu soldaki değişken adıyla kullanılabilir hâle gelir. Burada önce istek gönderilir ve yanıt alınır; sonra bu yanıt `response` adıyla kullanılabilir. Bu basit örnekte program, bu işlem tamamlandıktan sonra bir sonraki satıra geçer.

#### `response` ile `book` arasındaki fark

| İfade | Neyi temsil eder? |
|---|---|
| `response` | HTTP yanıtını temsil eden nesnedir. Yanıtın durum kodunu, başlıklarını ve gövdesini incelememizi sağlar. |
| `response.json()` | Yanıtın gövdesindeki JSON'u ayrıştıran, yani Python verisine dönüştüren metot çağrısıdır. Yeni bir HTTP isteği göndermez; alınmış yanıt üzerinde çalışır. |
| `book` | Bu örnekte JSON'dan elde ettiğimiz kitap sözlüğüdür. İçinde `id`, `title` ve `author` anahtarları vardır. |

Sunucumuzun gönderdiği JSON gövdesi şu bilgileri içerir:

```json
{
  "id": 42,
  "title": "API Yolculuğu",
  "author": "Deniz Kaya"
}
```

`response.json()` bu veriyi ayrıştırdıktan sonra istemcideki `book` sözlüğünde de bu üç alan bulunur. `response` ve `book`, bizim seçtiğimiz değişken adlarıdır; sunucudaki değişkenlerle aynı adı taşımaları gerekmez. `server.py` ve `client.py` içindeki `book` değişkenleri, ayrı programların belleğinde bulunur. Kitap bilgisi HTTP yanıtıyla istemciye ulaşır.

#### Son satır başlığı nasıl seçiyor?

`book["title"]` ifadesindeki köşeli parantezler, sözlükten bir anahtarın değerini almamızı sağlar. `"title"` anahtardır; bu örnekte karşılığı `"API Yolculuğu"` metnidir. `print(...)`, bu değeri terminale yazar:

```text
API Yolculuğu
```

Kodun sonunda yalnızca başlığı yazdırmayı seçtik. Sunucudan gelen `id` ve `author` bilgileri de `book` içinde bulunur, fakat bu satır onları ekrana yazdırmaz.

Bu ilk örnek, sunucunun açık olduğu ve beklenen kitap verisini döndürdüğü durum içindir. Bağlantı kurulamazsa veya yanıt beklediğimiz yapıda değilse kod hata verebilir; bu durumları sonraki deneylerde ele alacağız. HTTPX kullanımı için başvuru: [İstek gönderme ve JSON yanıtını okuma](https://www.python-httpx.org/quickstart/).

Sunucu terminalini açık bırak. İkinci terminalde:

```bash
source api-env/bin/activate
python client.py
```

Beklenen çıktı:

```text
API Yolculuğu
```

### Deneyin sonucu

`server.py` üç alan gönderdi; `client.py` yalnızca `title` alanını gösterdi. Sunucu veriyi üretir, istemci aldığı veriyi nasıl kullanacağına karar verir.

## Deney 3 — HTTP yanıtını görünür hâle getir

### Ne yapıyoruz?

İstemcide durum kodunu, ham yanıt gövdesini ve seçilen alanları ayrı ayrı gösteriyoruz.

### Neden yapıyoruz?

Bir HTTP yanıtının yalnızca kitap verisinden oluşmadığını görmek istiyoruz. İşlemin sonucunu belirten durum kodu ile gövde farklı bilgilerdir.

### Değişen satırlar

```diff
  response = httpx.get("http://127.0.0.1:8000/api/books/42")
+ print("Status code:", response.status_code)
+ print("Response body:", response.text)
  book = response.json()
- print(book["title"])
+ print("Book title:", book["title"])
+ print("Book author:", book["author"])
```

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books/42")

print("Status code:", response.status_code)
print("Response body:", response.text)

book = response.json()

print("Book title:", book["title"])
print("Book author:", book["author"])
```

Beklenen temel çıktı:

```text
Status code: 200
Response body: {"id":42,"title":"API Yolculuğu","author":"Deniz Kaya"}
Book title: API Yolculuğu
Book author: Deniz Kaya
```

### Deneyin sonucu

`200` isteğin başarıyla karşılandığını, JSON gövdesi ise kaynağın temsilini gösterir. `response.json()` bu JSON'u istemcinin kullanacağı Python sözlüğüne dönüştürür.

## Deney 4 — JSON gelmesi başarı demek midir?

### Ne yapıyoruz?

Henüz tanımlamadığımız `/api/books/99` adresini istiyoruz. Sonra istemcinin her JSON yanıtını kitap sanmasının neden hata olduğunu gözlemliyoruz.

### Neden yapıyoruz?

Başarısız bir işlemde de JSON gövdesi gelebileceğini ve istemcinin durum koduna bakması gerektiğini göstermek istiyoruz.

### Değişen satırlar

```diff
- response = httpx.get("http://127.0.0.1:8000/api/books/42")
+ response = httpx.get("http://127.0.0.1:8000/api/books/99")
```

### `client.py` dosyasının tamamı — hatayı gözlemleme sürümü

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books/99")

print("Status code:", response.status_code)
print("Response body:", response.text)

book = response.json()

print("Book title:", book["title"])
print("Book author:", book["author"])
```

Beklenen sonuç — hata ayrıntılarıyla birlikte örnek terminal çıktısı:

```text
Status code: 404
Response body: {"detail":"Not Found"}
Traceback (most recent call last):
  File "/mnt/c/Users/MONSTER/Desktop/book-catalog-api/client.py", line 12, in <module>
    print("Book title:", book["title"])
                        ~~~~^^^^^^^^^
KeyError: 'title'
```

| Çıktıdaki satır veya bölüm | Ne anlama geliyor? |
|---|---|
| `Status code: 404` | Sunucu isteğe yanıt verdi, fakat istediğimiz yol bulunamadı. Deneyin bu aşamasında sunucuda yalnızca `/api/books/42` yolu tanımlı; istemci ise `/api/books/99` yolunu istiyor. |
| `Response body: {"detail":"Not Found"}` | Sunucu kitap bilgisi yerine JSON biçiminde bir hata açıklaması gönderdi. Bu JSON'da yalnızca `detail` alanı var. `Not Found`, “Bulunamadı” demektir. |
| `Traceback (most recent call last):` | Python, programın hangi noktada hatayla durduğunu gösteren hata izini yazdırmaya başlıyor. “Most recent call last”, en son çağrının en altta gösterildiğini belirtir. Bu bölüm istemci programında oluşan hatanın ayrıntısıdır. |
| `File ".../client.py", line 12, in <module>` | Hatanın `client.py` dosyasının bu örnekteki 12. satırında oluştuğunu gösterir. `<module>`, bu satırın dosyanın doğrudan çalıştırılan ana bölümünde bulunduğunu belirtir. |
| `print("Book title:", book["title"])` | Python hataya yol açan kod satırını gösterir. `print` yazdırmadan önce `book["title"]` değerini bulmaya çalışır. |
| `~~~~^^^^^^^^^` | Python'un bazı sürümlerinde sorunlu ifadeyi vurgulamak için kullandığı işaretlerdir. Burada `book["title"]` erişimine dikkat çeker. |
| `KeyError: 'title'` | Sözlükte `title` adlı anahtar bulunmadığını söyler. Program yakalanmayan bu hata nedeniyle durur. |

**Neden `KeyError` oluştu?** `response.json()` bu örnekte başarılıdır: hata yanıtı da geçerli bir JSON'dur ve `book` değişkenine `{"detail": "Not Found"}` sözlüğü atanır. Ancak bu sözlükte `title` bulunmaz. Değişkene `book` adını vermemiz, gelen verinin mutlaka bir kitap olduğu anlamına gelmez. `book["title"]` erişimi başarısız olduğu için kitap başlığı yazdırılamaz; ardından gelen yazar yazdırma satırına da geçilmez.

**Çıktı neden bilgisayarımda farklı uzunlukta?** `Traceback`, dosya yolu, satır numarası ve işaretleme satırı aynı hatanın ayrıntılarıdır. Dosyadaki boş satırlar nedeniyle hata sende 10., 12. veya başka bir satırda görünebilir. Python sürümüne göre vurgulama işaretleri de değişebilir. Karşılaştırırken temel sıra şudur: sunucudan `404` yanıtı gelir, gövdede `Not Found` açıklaması vardır, istemci olmayan `title` alanını okumaya çalıştığı için `KeyError` oluşur.

Bu hata `client.py` programının çalışmasını sonlandırır ve istemci terminali yeniden `(api-env) ... $` komut istemini gösterir. Uvicorn ile çalışan sunucu ise yeni istekleri beklemeye devam eder. Bu deneyde hatayı bilerek gözlemliyoruz; sonraki adımda yanıtın durum kodunu kontrol ederek istemciyi düzelteceğiz.

### İstemciyi durum koduna göre düzelt

```diff
  print("Response body:", response.text)
- book = response.json()
- print("Book title:", book["title"])
- print("Book author:", book["author"])
+ if response.status_code == 200:
+     book = response.json()
+     print("Book title:", book["title"])
+     print("Book author:", book["author"])
+ else:
+     print("Book information could not be retrieved.")
```

### `client.py` dosyasının tamamı — kontrollü sürüm

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books/99")

print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    book = response.json()
    print("Book title:", book["title"])
    print("Book author:", book["author"])
else:
    print("Book information could not be retrieved.")
```

### Deneyin sonucu

`404`, sunucunun hiç cevap vermediğini göstermez. Sunucu bir HTTP hata yanıtı vermiştir. İstemci başarılı kitap yanıtıyla hata yanıtını farklı işlemelidir.

### Yol parametresine geçmeden önce: istemci isteği sunucudaki fonksiyona nasıl ulaşır?

Şimdiye kadar sunucuda bir fonksiyon yazdık, istemciden bir adrese istek gönderdik ve yanıt aldık. Bu bölümde mevcut kodu değiştirmeden bu iki tarafın nasıl bağlandığını açıklıyoruz.

#### Sunucudaki kodun parçaları

Bu aşamadaki `server.py` dosyamız şöyledir:

```python
from fastapi import FastAPI

app = FastAPI()

book = {
    "id": 42,
    "title": "API Yolculuğu",
    "author": "Deniz Kaya"
}


@app.get("/api/books/42")
def get_book():
    return book
```

| Kod veya ad | Nedir? | Burada ne yapar? |
|---|---|---|
| `fastapi` | Kurduğumuz Python paketinin kodda kullandığımız adıdır. | API uygulamasını yazmak için gereken sınıfı bu paketten alırız. |
| `FastAPI` | Bu paketin sunduğu bir **sınıftır (class)**. Sınıf, belirli özelliklere ve davranışlara sahip nesneler oluşturmak için kullanılan tanımdır. | Kendi API uygulama nesnemizi oluşturmak için kullanırız. |
| `from fastapi import FastAPI` | Bir paketten belirli bir adı içeri aktaran Python ifadesidir. | `FastAPI` sınıfını bu dosyada kullanıma açar. |
| `app = FastAPI()` | Sınıftan bir **nesne (object / instance)** oluşturur ve onu `app` değişkenine atar. | `app`, bizim API uygulamamızı temsil eder; hangi isteklerin hangi fonksiyonlarla karşılanacağı bu uygulamaya kaydedilir. |
| `book = {...}` | Kitap bilgilerini içeren Python sözlüğünü oluşturur. | Bu ilk örnekte sunucunun döndüreceği tek kitabı bellekte tutar. |
| `@app.get("/api/books/42")` | Altındaki fonksiyonu belirli bir HTTP metodu ve yolla ilişkilendiren **dekoratör (decorator)** ifadesidir. | `GET /api/books/42` isteğini `get_book` fonksiyonuna bağlar. |
| `def get_book():` | `get_book` adlı Python fonksiyonunu tanımlar. | Uygun istek geldiğinde FastAPI'nin çalıştıracağı kodu tanımlar. |
| `return book` | Fonksiyonun sonucunu döndürür. | Kitap sözlüğünü FastAPI'ye verir. FastAPI bu örnekte sözlüğü JSON yanıt gövdesine dönüştürür. |

Burada `FastAPI` sınıfın, `app` ise o sınıftan oluşturduğumuz uygulama nesnesinin adıdır. `python -m uvicorn server:app` komutundaki `app`, bu nesneyi gösterir. [FastAPI sınıfı ve uygulama nesnesi](https://fastapi.tiangolo.com/reference/fastapi/).

#### `book` global bir değişken mi? Fonksiyon ona nasıl erişiyor?

**Evet.** Yukarıdaki `book = {...}` satırı bir fonksiyonun veya sınıfın içinde değildir; dosyanın en dış düzeyindedir. Bu yüzden `book`, `server.py` modülünün **global değişkenidir (global variable)**. Python'da bir `.py` dosyası modül olarak kullanılabilir. Buradaki “global”, bu modülün kapsamını ifade eder.

**Kapsam (scope)**, bir değişken adına kodun hangi bölümünden erişebildiğimizi belirler. `get_book` içinde yerel bir `book` tanımı veya bu adda bir parametre yoktur. Bu nedenle `return book`, fonksiyonun tanımlandığı modüldeki `book` değişkenini kullanır.

| Kodun bulunduğu yer | Ne olur? |
|---|---|
| Dosyanın en dış düzeyindeki `book = {...}` | Sunucu modülü yüklenirken kitap sözlüğü oluşturulur ve `book` adına bağlanır. |
| `def get_book():` | Fonksiyon tanımlanır. Parantezlerin boş olması, bu fonksiyonun parametre almadığını gösterir. |
| Fonksiyonun içindeki `return book` | Fonksiyon çağrıldığında modüldeki mevcut `book` sözlüğüne erişir ve onu döndürür. Her çağrıda bu satırla yeni bir sözlük oluşturulmaz. |

Bu erişimi sağlayan Python'un kapsam kurallarıdır. `@app.get(...)` ise uygun HTTP isteğiyle fonksiyon arasında bağlantı kurar; fonksiyonun `book` değişkenine erişmesi için gerekli değildir. [Python'da kapsam ve ad alanları](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces).

#### Neden fonksiyonun içine `global book` yazmadık?

`return book`, mevcut değişkeni okur; ona yeni bir değer atamaz. **Bir global değişkeni fonksiyon içinde yalnızca okumak için `global` bildirimi gerekmez.** Okuma ile atama arasındaki fark şöyledir:

| Fonksiyon içinde yapılan işlem | `global book` gerekir mi? | Açıklama |
|---|---|---|
| `return book` | Hayır. | Modüldeki sözlüğü okuyup döndürür. Bizim fonksiyonumuzun yaptığı budur. |
| `book = {...}` ile modüldeki `book` değişkenine yeni bir sözlük atamak | Evet. | Fonksiyon içinde aynı ada normal atama yapılırsa yerel bir `book` oluşur. Atamanın modüldeki değişkene yapılmasını istiyorsak fonksiyonda önce `global book` bildirimi kullanırız. |
| `book["title"] = "Yeni başlık"` | Hayır. | Mevcut sözlüğün içeriğini değiştirir; `book` adını başka bir sözlüğe bağlamaz. Bu değişiklik sunucudaki aynı sözlüğe yansır. |

Son iki satır kapsam farkını açıklamak içindir; bu aşamada sunucu kodumuza bunları eklemiyoruz. [Python'da `global` bildirimi](https://docs.python.org/3/reference/simple_stmts.html#the-global-statement).

**İstemcideki `book` aynı değişken mi?** Hayır. `server.py` içindeki `book`, sunucu programının belleğindedir. `client.py` içindeki `book = response.json()` ise gelen JSON'dan istemci programının belleğinde ayrı bir sözlük oluşturur. Aynı adı kullanmaları, aynı değişkeni paylaştıkları anlamına gelmez; bilgi HTTP yanıtıyla aktarılır.

#### Dekoratör, Python'ın bir özelliğidir

**Dekoratör (decorator)**, bir fonksiyonu alıp onu kaydetmek veya davranışını değiştirmek için kullanılan bir yapıdır. Python'daki `@` sözdizimi dekoratörü altındaki fonksiyona uygular; web veya API uygulamalarına özel değildir.

Aşağıdaki bağımsız Python örneğinde dekoratör, fonksiyon çalışmadan önce bir mesaj yazdırır:

```python
def haber_ver(fonksiyon):
    def yeni_fonksiyon():
        print("Fonksiyon çalışacak.")
        fonksiyon()
    return yeni_fonksiyon

@haber_ver
def selamla():
    print("Merhaba!")

selamla()
```

Çıktı:

```text
Fonksiyon çalışacak.
Merhaba!
```

`@haber_ver`, fonksiyon tanımından sonra `selamla = haber_ver(selamla)` yazmanın kısa biçimidir. `haber_ver`, asıl `selamla` fonksiyonunu alır ve `yeni_fonksiyon` adlı sarmalayıcı fonksiyonu döndürür. Böylece `selamla()` çağrıldığında önce mesaj yazılır, ardından asıl fonksiyon çalışır. `fonksiyon()` çağırır; `return yeni_fonksiyon` ise parantezsiz olduğu için fonksiyonu çalıştırmadan geri verir.

FastAPI'deki `@app.get(...)` de aynı Python özelliğini kullanır. Onun buradaki görevi, altındaki fonksiyonu belirli bir HTTP metodu ve yol için kaydetmektir; fonksiyonun gövdesi daha sonra uygun istek geldiğinde çalışır.

#### `@app.get(...)` fonksiyonun çalışmasıyla nasıl ilişkili?

Bir Python fonksiyonunu `def` ile tanımlamak, gövdesindeki kodu hemen çalıştırmaz. Fonksiyonun daha sonra çağrılması gerekir. Bizim örneğimizde bu çağrıyı, uygun HTTP isteği geldiğinde FastAPI yapar.

`@` işareti, Python'da bir dekoratörün altındaki fonksiyona uygulanmasını sağlar. Bu örnekte `@app.get("/api/books/42")`, `get_book` fonksiyonunu uygulamanın istek yönlendirme kayıtlarına ekler. **Yönlendirme (routing)**, gelen isteği uygun fonksiyonla eşleştirme işidir. [Python'da dekoratör](https://docs.python.org/3/glossary.html#term-decorator) ve [FastAPI'de yol işlemi tanımlama](https://fastapi.tiangolo.com/tutorial/first-steps/#define-a-path-operation-decorator).

Bu kaydı şöyle okuyabiliriz:

| HTTP metodu | Yol | Çalıştırılacak fonksiyon |
|---|---|---|
| `GET` | `/api/books/42` | `get_book` |

İki farklı zamanı ayıralım:

1. **Sunucu başlatılırken:** Uvicorn `server.py` modülünü yükler. `app` oluşturulur; fonksiyon tanımlanır ve dekoratör bu eşleştirmeyi kaydeder. Bu kayıt sırasında `get_book` fonksiyonunun gövdesindeki `return book` henüz çalışmaz.
2. **İstek geldiğinde:** FastAPI gelen isteğin metodunu ve yolunu kontrol eder. `GET` ve `/api/books/42` eşleştiğinde kayıtlı `get_book` fonksiyonunu çağırır. İşte bu anda `return book` çalışır.

Bu örnekte dekoratörü kaldırıp sunucuyu yeniden başlatsaydık, `get_book` normal bir Python fonksiyonu olarak tanımlı kalırdı; fakat bu yol için kaydedilmiş bir eşleştirme olmazdı. Başka bir kayıt da yapmadığımız için `/api/books/42` isteği onu çalıştırmazdı. Sunucu kodunun içinde açıkça `get_book()` yazarak fonksiyonu çağırmak mümkün olurdu; bu, program içindeki sıradan bir fonksiyon çağrısıdır.

#### İstemcideki `httpx.get(...)` ile sunucudaki `app.get(...)` arasındaki ilişki

| İfade | Nerede kullanılır? | Görevi |
|---|---|---|
| `httpx.get("http://127.0.0.1:8000/api/books/42")` | İstemcide, `client.py` içinde | Verilen adrese HTTP `GET` isteği gönderir ve yanıtı alır. |
| `@app.get("/api/books/42")` | Sunucuda, `server.py` içinde | Sunucuya `/api/books/42` yolu için bir HTTP `GET` isteği geldiğinde `get_book` fonksiyonunun çalıştırılacağını uygulamaya kaydeder. |

İki taraftaki `get` adının ortak noktası **HTTP'nin GET metodudur**. İstemci GET isteğini gönderir; sunucudaki kayıt GET isteğini karşılayacak fonksiyonu belirtir. HTTPX, FastAPI'deki `app.get` metodunu doğrudan çağırmaz; aralarında HTTP iletişimi vardır. [HTTPX ile GET isteği gönderme](https://www.python-httpx.org/quickstart/).

İstemci `get_book` adını bilmez; sunucuya HTTP metodunu ve adresi gönderir. Fonksiyonun adını `find_book` olarak değiştirip aynı dekoratörü korusaydık istemci kodunu değiştirmemiz gerekmezdi. Fonksiyon adındaki `get` sözcüğü onu kendiliğinden HTTP GET isteklerine bağlamaz; bağlantıyı kuran dekoratörle yaptığımız kayıttır.

#### `/42` isteğinde kim, hangi sırayla çalışır?

Aşağıdaki satır, daha önce başarıyla çalıştırdığımız istemci isteğidir:

```python
response = httpx.get("http://127.0.0.1:8000/api/books/42")
```

| Adım | Ne olur? |
|---|---|
| 1 | İstemci, HTTPX aracılığıyla `127.0.0.1:8000` adresine `GET /api/books/42` isteğini gönderir. |
| 2 | Uvicorn bağlantıyı kabul eder ve isteği çalıştırdığı `app` uygulamasına aktarır. |
| 3 | FastAPI, metodun `GET`, yolun `/api/books/42` olduğunu görür ve eşleşen kayıttan `get_book` fonksiyonunu bulur. |
| 4 | FastAPI fonksiyonu çağırır. Fonksiyonun içindeki `return book` kitap sözlüğünü döndürür. |
| 5 | FastAPI bu sözlükten JSON içeren başarılı yanıtı hazırlar. Uvicorn yanıtı istemciye iletir. |
| 6 | HTTPX yanıtı alır ve bir yanıt nesnesi döndürür. İstemcideki `response` değişkeni bu nesneyi tutar. |

Uvicorn bağlantı ve HTTP iletişimini yürütür; FastAPI uygulaması isteğin hangi kodla işleneceğini belirler. [Sunucu ile uygulamanın iletişimi](https://uvicorn.dev/concepts/asgi/).

#### Aynı kodda `/99` neden fonksiyonu çalıştırmıyor?

Son deneyde istemcide şu satırı kullandık:

```python
response = httpx.get("http://127.0.0.1:8000/api/books/99")
```

Sunucudaki kayıt ise hâlâ `@app.get("/api/books/42")` şeklindedir. GET metodu eşleşse de yol eşleşmez:

| İstemcinin isteği | Sunucuda kayıtlı yol | `get_book` çalışır mı? | Sonuç |
|---|---|---|---|
| `GET /api/books/42` | `/api/books/42` | Evet | `200` ve kitap bilgileri döner. |
| `GET /api/books/99` | `/api/books/42` | Hayır | `404` ve `{"detail":"Not Found"}` döner. |

**Bu aşamadaki `404`, fonksiyonun kitaplar arasında arama yapıp 99 numaralı kitabı bulamamasından kaynaklanmaz. İstenen yola karşılık gelen fonksiyon kaydı bulunamadığı için oluşur.** `get_book` hiç çağrılmadığından içindeki `return book` satırına da ulaşılmaz.

Ayrıca `/api/books/42` içindeki `42`, şu anda sabit yol metninin bir parçasıdır. FastAPI bunu kendiliğinden `book` sözlüğünün `id` alanına bağlamaz. Yol eşleşince fonksiyon mevcut `book` sözlüğünü doğrudan döndürür; henüz bir kimlik karşılaştırması yazmadık.

Bir sonraki deneyde `/api/books/{book_id}` yazarak bu sabit parçayı **yol parametresine (path parameter)** dönüştüreceğiz. Böylece hem `/42` hem `/99` aynı fonksiyona ulaşabilecek; gelen kimliğe ait kitabın bulunup bulunmadığına fonksiyonun içinde yazacağımız kod karar verecek. [FastAPI yol parametreleri](https://fastapi.tiangolo.com/tutorial/path-params/).

## Deney 5 — Yol parametresiyle farklı kitap kimliklerini karşıla

### Ne yapıyoruz?

Sabit `/api/books/42` yolunu `/api/books/{book_id}` biçimine getiriyoruz. Aynı fonksiyon farklı kitap kimliklerini alabilecek.

### Neden yapıyoruz?

Her kitap için ayrı fonksiyon yazmak yerine, istemcinin istediği kaynak kimliğini adres üzerinden sunucuya iletmesini istiyoruz.

### Değişen satırlar

```diff
- from fastapi import FastAPI
+ from fastapi import FastAPI, HTTPException
...
- @app.get("/api/books/42")
- def get_book():
-     return book
+ @app.get("/api/books/{book_id}")
+ def get_book(book_id: int):
+     if book_id == book["id"]:
+         return book
+
+     raise HTTPException(status_code=404, detail="Book not found")
```

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

book = {
    "id": 42,
    "title": "API Yolculuğu",
    "author": "Deniz Kaya"
}


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    if book_id == book["id"]:
        return book

    raise HTTPException(status_code=404, detail="Book not found")
```

### Dekoratör ile fonksiyonun arasına başka kod yazılabilir mi?

| Dekoratör ile `def` arasına gelen içerik | Geçerli mi? | Neden? |
|---|---|---|
| Boş satırlar | Evet. | Python, dosyadaki bu boş satırları atlar; dekoratör yine altındaki fonksiyona uygulanır. Okumayı kolaylaştırmak için dekoratörü fonksiyonun hemen üstüne yazarız. |
| Yalnızca `#` ile başlayan yorum satırları | Evet. | Yorumlar çalıştırılan bir Python ifadesi değildir; dekoratörün fonksiyonla bağını kesmez. |
| `book = {...}` gibi bir atama | Hayır. | Dekoratör ile süsleyeceği fonksiyon tanımı arasına bağımsız bir atama ifadesi konulamaz. Python dosyayı okurken `SyntaxError` verir. |

Örneğin aşağıdaki yerleşim **geçersizdir**:

```python
@app.get("/api/books/{book_id}")

book = {
    "id": 42,
    "title": "API Yolculuğu",
    "author": "Deniz Kaya"
}

def get_book(book_id: int):
    if book_id == book["id"]:
        return book
    raise HTTPException(status_code=404, detail="Book not found")
```

Burada Python, `@app.get(...)` ifadesinden sonra `book = ...` atamasıyla karşılaşır ve sözdizimi hatası verir. Dekoratör bu atamayı atlayıp aşağıdaki fonksiyonu aramaz; sunucu yeni kodla başlayamaz.

Doğru sıralama, yukarıdaki tam `server.py` örneğinde olduğu gibidir: önce `book` sözlüğünü tanımla, ardından `@app.get(...)` ve `def get_book(...)` satırlarını birlikte yaz.

**Boş satır ile girinti farklıdır.** Boş satırlar bu örnekte sorun oluşturmaz; satır başındaki boşluklar ise hangi kodun hangi bloğa ait olduğunu belirler. `if` ve `raise` fonksiyonun içinde, `return book` ise `if` bloğunun içinde olmalıdır. Bu nedenle örnekte `if` ve `raise` dört, `return book` sekiz boşluk içeridedir. Koşul doğruysa `return` fonksiyonu bitirir; yanlışsa `raise` satırına geçilir. [Python'da fonksiyon tanımları ve dekoratörler](https://docs.python.org/3/reference/compound_stmts.html#function-definitions).

Sunucuyu değiştirdiğimiz için sunucu terminalinde **Ctrl+C** ile kapat ve yeniden çalıştır:

Ctrl+C'ye bastığında terminalde şu kapanış mesajlarını görebilirsin:

```text
^CINFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [13821]
```

| Görünen satır veya bölüm | Türkçe anlamı | Ne oluyor? |
|---|---|---|
| `^C` | Ctrl+C tuşlarına basıldığını gösterir. | Terminal, çalışan Uvicorn sürecine durdurma isteği iletir. `^C` terminalin gösterdiği işarettir; ardından gelen `INFO` ile aynı satırda görünebilir. |
| `INFO: Shutting down` | “Kapanıyor.” | Uvicorn kapanış sürecini başlatır. Yeni bağlantıları kabul etmeyi bırakır ve varsa devam eden isteklerin tamamlanmasına fırsat verir. |
| `INFO: Waiting for application shutdown.` | “Uygulamanın kapanış işlemlerinin tamamlanması bekleniyor.” | Uvicorn, FastAPI uygulamasına kapanacağını bildirir ve uygulamanın kapanış aşamasını tamamlamasını bekler. |
| `INFO: Application shutdown complete.` | “Uygulamanın kapanış işlemleri tamamlandı.” | FastAPI uygulamasının kapanış aşaması tamamlanmıştır. Uvicorn artık sunucu sürecini sonlandırma aşamasına geçer. |
| `INFO: Finished server process [13821]` | “13821 numaralı sunucu sürecinin çalışması tamamlandı.” | Uvicorn sunucu çalışmasını bitirmiştir. Köşeli parantezdeki sayı süreç kimliğidir (**PID**); başlangıçta gördüğümüz `Started server process [13821]` satırındaki süreçle aynıdır. Sende farklı bir sayı olabilir. |

**Bunlar hata mesajı mı?** Hayır. `INFO`, bilgilendirme kaydı olduğunu belirtir. Bu satırlar, Ctrl+C ile istediğimiz normal kapanışın aşamalarını gösterir. Uvicorn, çalışan işleri mümkün olduğunca tamamlayarak düzenli biçimde kapanır. [Uvicorn'un düzenli kapanış davranışı](https://uvicorn.dev/server-behavior/#graceful-process-shutdown).

**Uygulamanın kapanış aşamasında ne yapılır?** Uygulamada böyle işlemler tanımlanmışsa, örneğin açık bir veritabanı bağlantısı kapatılabilir. Biz bu örnekte özel bir kapanış işlemi yazmadık; yine de FastAPI'nin kapanış aşaması gerçekleşir ve bu mesajlar görülebilir. [Uygulamanın başlangıç ve kapanış aşamaları](https://uvicorn.dev/concepts/lifespan/).

Kapanış tamamlandığında aynı terminal yeniden `(api-env) ... $` komut istemini gösterir. Terminal ve sanal ortam açık kalır; sunucu programı durmuştur. `server.py` dosyasını kaydettiğinden emin ol ve aşağıdaki komutla yeniden başlat. Böylece dosyadaki yeni kod yüklenir:

```bash
python -m uvicorn server:app
```

`/api/books/99` artık tanımlı yol kalıbıyla eşleşir; fonksiyon çalışır ve kitabı bulamadığı için bilinçli olarak şu gövdeyi döndürür:

```json
{"detail": "Book not found"}
```

`/api/books/42` isteğinde ise `book_id` değeri `42` olur ve kitap `200` ile döner.

### Deneyin sonucu

`404` bu kodda beklenmedik sunucu arızası değildir. Kitabın bulunamayacağı olasılığı API davranışında açıkça tanımlanmıştır.

### Koleksiyona geçmeden önce: aynı işi HTTP API kullanmadan yapabilir miyiz?

**Evet. Bir kitabın bilgilerini bulup ekrana yazdırmak için HTTP API kurmak zorunda değiliz.** Aynı işi normal bir Python fonksiyonunu doğrudan çağırarak yapabiliriz. Şimdiye kadar yazdığımız FastAPI ve HTTPX kodları da Python programlarıdır. API kullanmak farklı bir programlama diline geçmek değildir; programların birbirinin sunduğu işlemlere nasıl erişeceğini düzenlemektir.

#### İki yaklaşımın farkı

| Soru | Doğrudan Python fonksiyonu çağırırsak | Bu dersteki HTTP API'yi kullanırsak |
|---|---|---|
| Kitap nasıl istenir? | `get_book(42)` çağrısıyla. | Sunucuya `GET /api/books/42` isteği gönderilerek. |
| İşlemi yapan kod nerede çalışır? | Fonksiyonu çağıran programın Python sürecinde. | Bağımsız çalışan sunucu sürecinde. |
| Çağıran kod neyi bilmelidir? | Hangi Python fonksiyonunu, hangi parametrelerle çağıracağını. | Sunucu adresini, HTTP metodunu, adres yolunu ve yanıt biçimini. |
| Sonuç nasıl alınır? | Fonksiyonun `return` ettiği Python değeri doğrudan alınır. | HTTP yanıtı alınır; bu örnekte JSON gövdesi Python verisine dönüştürülür. |
| FastAPI, Uvicorn ve HTTPX gerekli mi? | Bu basit doğrudan çağrı örneği için gerekli değildir. | Bu derste sunucu ve istemci taraflarını bu araçlarla oluşturuyoruz. |

#### HTTP kullanmadan çalışan küçük bir Python örneği

Karşılaştırma için `direct-call-demo` adlı ayrı bir klasörde şu iki dosyanın bulunduğunu düşünelim. Bu örnek, aynı kitap bulma işleminin doğrudan fonksiyon çağrısıyla nasıl yapıldığını gösterir.

**`catalog.py` — kitap bilgisi ve onu bulan fonksiyon:**

```python
book = {
    "id": 42,
    "title": "API Yolculuğu",
    "author": "Deniz Kaya"
}


def get_book(book_id):
    if book_id == book["id"]:
        return book
    return None
```

**`main.py` — fonksiyonu çağırıp sonucu gösteren kod:**

```python
from catalog import get_book

book = get_book(42)

if book is not None:
    print("Book title:", book["title"])
else:
    print("Book not found")
```

İki dosyanın bulunduğu klasörde şu komut çalıştırılır:

```bash
python main.py
```

Beklenen çıktı:

```text
Book title: API Yolculuğu
```

| Satır veya işlem | Ne yapar? |
|---|---|
| `from catalog import get_book` | `catalog.py` modülündeki fonksiyonu aynı Python sürecinde kullanıma açar. Ayrı bir sunucuya bağlantı kurmaz. |
| `book = get_book(42)` | Fonksiyonu doğrudan çağırır ve dönen sözlüğü `book` değişkenine atar. |
| `return None` | Kimlik eşleşmezse kitap bulunamadığını belirtmek için Python'un `None` değerini döndürür. Bu örnek için seçtiğimiz davranıştır. |
| `if book is not None:` | Sonucun bir kitap olup olmadığını kontrol eder; kitap varsa başlığını yazdırır. |

`get_book(42)` yerine `get_book(99)` yazarsak çıktı `Book not found` olur. Burada HTTP kullanılmadığı için `200` veya `404` durum kodları da yoktur; sonucu Python değerleriyle ifade ederiz.

**İki dosya olması, iki ayrı program süreci çalıştığı anlamına gelmez.** Bu örnekte yalnızca `python main.py` çalıştırılır. `catalog.py`, bu programın içine modül olarak yüklenir. Dolayısıyla burada bağımsız çalışan bir sunucuya istek göndermiyoruz. [Python modülleri ve `import`](https://docs.python.org/3/tutorial/modules.html).

#### O zaman HTTP API bize ne kazandırıyor?

Kitap kataloğunu yalnızca kendi Python programımız kullanacaksa yukarıdaki doğrudan çağrı yeterli olabilir. Şimdi ihtiyacın değiştiğini düşünelim: aynı kataloğu bir web arayüzü, bir telefon uygulaması ve başka bir Python programı da kullanacak.

HTTP API ile kitapları bulma işlemi sunucuda kalır. Her istemci sunucuya üzerinde anlaşılmış bir istek gönderir ve yanıtı kendi ihtiyacına göre kullanır. Örneğin web arayüzü başlığı sayfada gösterirken Python istemcimiz terminale yazdırabilir. İstemcilerin sunucudaki `get_book` fonksiyonunu içeri aktarması veya aynı programlama diliyle yazılması gerekmez.

Bu derste bu anlaşmayı şu şekilde kurduk:

| API'nin belirlediği bilgi | Kitap örneğimizdeki karşılığı |
|---|---|
| Hangi işlem istenebilir? | Kimliği verilen kitabın bilgisini almak. |
| İstek nasıl gönderilir? | `GET /api/books/{book_id}` yoluyla. |
| Hangi girdi verilir? | Adres yolundaki kitap kimliği. |
| Başarılı sonuç nasıl bildirilir? | `200` durum kodu ve kitap bilgilerini içeren JSON gövdesiyle. |
| Kitap bulunamazsa ne olur? | `404` durum kodu ve hata açıklamasını içeren JSON gövdesiyle. |

**API'nin bu örnekteki yeri, istemcinin sunucudaki kitap bulma işlevini hangi kurallarla kullanacağını tanımlayan arayüzdür.** Kitabı bulan kodu biz Python ile yazıyoruz. FastAPI, dışarıdan gelen HTTP isteğini bu koda bağlamamızı ve sonucu bir HTTP yanıtı olarak sunmamızı kolaylaştırıyor. [FastAPI ile HTTP işlemleri tanımlama](https://fastapi.tiangolo.com/tutorial/first-steps/).

İstemciyle sunucuyu öğrenme kolaylığı için aynı bilgisayarda çalıştırıyoruz. Aynı iletişim yaklaşımı, uygun ağ erişimi sağlandığında farklı bilgisayarlarda da kullanılabilir. Bunun için istemci, yerel `127.0.0.1` yerine erişilebilir sunucu adresini kullanır. HTTP API kullanmak, mutlaka genel internete bağlanmak anlamına gelmez.

#### `from server import get_book` yazsak çalışan sunucuya ulaşmış olmaz mıyız?

Bu ifade, `server.py` kodunu istemcinin Python sürecine yükler. Çağrı bu süreçte çalışır; Uvicorn ile zaten çalıştırdığımız sunucu sürecine bir istek gönderilmez. Böylece sunucunun belleğindeki kitap sözlüğüne uzaktan erişmiş olmayız. Ayrı süreçlerin iletişimi için HTTP gibi bir iletişim yolu gerekir.

Ayrıca bu dersteki `server.py`, FastAPI ve `HTTPException` kullanır. Doğrudan çağrı örneğinde `catalog.py` adında küçük bir modül göstermemizin nedeni, kitap bulma mantığını HTTP yanıtı hazırlama görevinden ayrı görebilmektir.

#### İki ayrı Python programı HTTP kullanmadan konuşabilir mi?

**Evet. İstemci–sunucu yapısı kurmak için HTTP API kullanmak zorunda değiliz.** Önceki `catalog.py` ve `main.py` örneği tek bir Python sürecinde çalışıyordu. İki bağımsız programın haberleşmesi ise farklı bir durumdur.

Örneğin Python'un **TCP soketleri (sockets)** üzerinden iki ayrı program arasında bağlantı kurabiliriz. Soket, programın bağlantı üzerinden veri gönderip alabildiği iletişim ucudur. Kitap örneğimizde şöyle bir iletişim tasarlayabiliriz:

| Taraf | Yaptığı iş |
|---|---|
| Sunucu | Ayrı bir program olarak çalışır ve bağlantı bekler. |
| İstemci | Sunucuya bağlanıp `KITAP 42` mesajını gönderir. |
| Sunucu | Mesajı okuyup kitabı bulur ve `API Yolculuğu` cevabını gönderir. |
| İstemci | Gelen cevabı ekrana yazdırır. |

Bu tasarımda FastAPI, HTTP, GET, adres yolu veya JSON kullanmak zorunda değiliz. Sunucu ve istemci ayrı süreçlerde çalışır; aralarında gerçek bir bağlantı vardır. [Python ile soket iletişimi](https://docs.python.org/3/howto/sockets.html).

Bununla birlikte, iki programın anlaşabilmesi için kurallar belirlememiz gerekir: `KITAP 42` ne anlama geliyor, mesaj nerede bitiyor, kitap bulunamazsa hangi cevap gönderiliyor? Bunlar **iletişim protokolünün** kurallarıdır. HTTP, istek ve yanıtların yapısı için hazır bir standart sunar; HTTP kullanmazsak mesajların biçimini başka bir protokolle belirlememiz gerekir.

#### İstemci–sunucu, protokol ve API arasındaki fark

| Kavram | Neyi anlatır? | Kitap örneğindeki karşılığı |
|---|---|---|
| **İstemci–sunucu (client–server)** | Programların iletişimde üstlendiği rolleri anlatır. | İstemci kitap bilgisi ister; sunucu isteği karşılar. |
| **Protokol (protocol)** | Mesajların nasıl oluşturulacağını ve karşılıklı iletişimin hangi kurallarla yürütüleceğini belirler. | HTTP kullanabiliriz veya TCP üzerinde `KITAP 42` gibi mesajların biçimini kendimiz tanımlayabiliriz. |
| **API — uygulama programlama arayüzü** | Bir yazılımın sunduğu işlemlerin başka kodlar tarafından nasıl kullanılacağını tanımlar. | “Kitap kimliğini vererek kitap bilgisi isteyebilirsin; başarılı sonuç ve bulunamadı sonucu şu biçimde döner.” |
| **FastAPI** | HTTP üzerinden API sunan uygulamalar yazmamızı kolaylaştıran Python aracıdır. | İsteğin adres yolunu ve metodunu Python fonksiyonuna bağlarız. |

#### “API kullanmadan” ifadesini nasıl anlamalıyız?

**API, HTTP'den daha geniş bir kavramdır.** Bir Python kütüphanesinin dışarıya sunduğu fonksiyonlar da o kütüphanenin API'sini oluşturabilir. Benzer şekilde, TCP üzerinden çalışan sunucunun kabul ettiği komutlar ve ürettiği cevaplar da onun kullanım arayüzü olarak tanımlanabilir. Ayrıca “API” adlı bir araç kurmak zorunda değiliz; API, sunduğumuz arayüzün adıdır. [API kavramı](https://developer.mozilla.org/en-US/docs/Glossary/API).

Bu nedenle üç durumu ayırmalıyız: **aynı program içinde doğrudan fonksiyon çağrısı**, **HTTP kullanmadan iki ayrı programın haberleşmesi** ve **HTTP API üzerinden iki ayrı programın haberleşmesi**. Bu derste üçüncü yaklaşımı öğreniyoruz.

Bu çalışmada HTTP API kurmamızın amacı, yalnızca bir kitap başlığı yazdırmak değil; bir programın sunduğu kitap işlemini başka bir programdan kullanmayı öğrenmektir. Bir sonraki deneyde bu arayüzü birden fazla kitabı sunacak şekilde genişleteceğiz.

## Deney 6 — Bir kitap koleksiyonu oluştur

### Ne yapıyoruz?

Tek sözlük yerine kitap sözlüklerinden oluşan liste tutuyoruz. Bütün kitapları ve kimliği verilen tek kitabı sunan iki işlem oluşturuyoruz.

### Neden yapıyoruz?

Tek kaynak yanıtıyla koleksiyon yanıtının farklı JSON yapılarına sahip olduğunu görmek istiyoruz.

### Değişen satırlar

```diff
- book = { ... }
+ books = [
+     {"id": 42, ...},
+     {"id": 57, ...}
+ ]
+
+ @app.get("/api/books")
+ def get_books():
+     return books
...
+     for book in books:
+         if book["id"] == book_id:
+             return book
```

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": "Deniz Kaya"
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": "Ece Yılmaz"
    }
]


@app.get("/api/books")
def get_books():
    return books


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

Sunucuyu yeniden başlat. İstemcinin adresini `/api/books` olarak değiştir ve gelen listeyi döngüyle işle.

### Değişen satırlar

```diff
- response = httpx.get("http://127.0.0.1:8000/api/books/99")
+ response = httpx.get("http://127.0.0.1:8000/api/books")
...
-     book = response.json()
-     print("Book title:", book["title"])
+     books = response.json()
+     print("Book count:", len(books))
+     for book in books:
+         print("Book title:", book["title"])
+         print("Book author:", book["author"])
```

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books")

print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

    for book in books:
        print("Book title:", book["title"])
        print("Book author:", book["author"])
        print()
else:
    print("Book information could not be retrieved.")
```

### Gözlem ve sonuç

| İstek | JSON gövdesi | Python karşılığı |
|---|---|---|
| `GET /api/books/57` | `{...}` | Sözlük |
| `GET /api/books` | `[{...}, {...}]` | Sözlüklerden oluşan liste |

Sunucu listeyi gönderir; `len(books)` ile kitap sayısını istemci hesaplar.

## Deney 7 — JSON türlerini çalışan API'de gör

### Ne yapıyoruz, neden yapıyoruz?

Kitap temsilini adım adım genişletip mantıksal değer, dizi, `null`, sayı ve iç içe nesneyi hem sunucuda üretiyor hem istemcide anlamına göre işliyoruz. Böylece JSON türlerinin yalnızca yazım biçimi olmadığını, istemcinin davranışını etkilediğini görüyoruz.

### Mantıksal değer: `available`

**Amaç:** Sunucunun yalnızca metin göndermediğini, istemcinin mantıksal değere göre farklı davranabildiğini görmek.

Python'daki `True` ve `False`, FastAPI tarafından JSON'daki `true` ve `false` değerlerine dönüştürülür.

#### Değişen satırlar

```diff
      "author": "Deniz Kaya",
+     "available": True
...
      "author": "Ece Yılmaz",
+     "available": False
```

#### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": "Deniz Kaya",
        "available": True
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": "Ece Yılmaz",
        "available": False
    }
]


@app.get("/api/books")
def get_books():
    return books


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

Sunucuyu yeniden başlat. Ardından istemciye görünüm kuralını ekle.

#### Değişen satırlar

```diff
          print("Book author:", book["author"])
+
+         if book["available"]:
+             print("Availability: Available to borrow")
+         else:
+             print("Availability: Not available to borrow")
```

#### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books")

print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

    for book in books:
        print("Book title:", book["title"])
        print("Book author:", book["author"])

        if book["available"]:
            print("Availability: Available to borrow")
        else:
            print("Availability: Not available to borrow")

        print()
else:
    print("Book information could not be retrieved.")
```

**Sonuç:** `false`, alanın eksik olduğunu söylemez. “Ödünç alınamaz” şeklinde anlamlı bir cevaptır.

### Dizi ve boş dizi: `tags`

**Amaç:** Tek kitap nesnesinin içinde birden fazla değerin diziyle taşınmasını ve `[]` değerinin hata olmadığını görmek.

#### Değişen satırlar

```diff
      "available": True,
+     "tags": ["software", "education"]
...
      "available": False,
+     "tags": []
```

#### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": "Deniz Kaya",
        "available": True,
        "tags": ["software", "education"]
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": "Ece Yılmaz",
        "available": False,
        "tags": []
    }
]


@app.get("/api/books")
def get_books():
    return books


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

#### Değişen satırlar

```diff
          else:
              print("Availability: Not available to borrow")
+
+         if book["tags"]:
+             print("Tags:")
+             for tag in book["tags"]:
+                 print("-", tag)
+         else:
+             print("Tags: No tags")
```

#### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books")

print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

    for book in books:
        print("Book title:", book["title"])
        print("Book author:", book["author"])

        if book["available"]:
            print("Availability: Available to borrow")
        else:
            print("Availability: Not available to borrow")

        if book["tags"]:
            print("Tags:")
            for tag in book["tags"]:
                print("-", tag)
        else:
            print("Tags: No tags")

        print()
else:
    print("Book information could not be retrieved.")
```

**Sonuç:** `tags: []`, etiket alanının bulunduğunu fakat dizide sıfır eleman olduğunu anlatır. Bu durum tek başına HTTP hatası değildir.

### `null` ile `0`: `rating`

**Amaç:** “Henüz puan verilmemiş” ile “puanı sıfır” bilgisini ayırmak.

Bizim API sözleşmemizde `None` henüz puan verilmediğini, `0` ise verilmiş sayısal puanı anlatır. FastAPI, Python `None` değerini JSON `null` değerine dönüştürür.

#### Değişen satırlar

```diff
      "tags": ["software", "education"],
+     "rating": None
...
      "tags": [],
+     "rating": 0
```

#### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": "Deniz Kaya",
        "available": True,
        "tags": ["software", "education"],
        "rating": None
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": "Ece Yılmaz",
        "available": False,
        "tags": [],
        "rating": 0
    }
]


@app.get("/api/books")
def get_books():
    return books


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

#### Değişen satırlar

```diff
          else:
              print("Tags: No tags")
+
+         if book["rating"] is None:
+             print("Rating: Not rated yet")
+         else:
+             print("Rating:", book["rating"])
```

#### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books")

print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

    for book in books:
        print("Book title:", book["title"])
        print("Book author:", book["author"])

        if book["available"]:
            print("Availability: Available to borrow")
        else:
            print("Availability: Not available to borrow")

        if book["tags"]:
            print("Tags:")
            for tag in book["tags"]:
                print("-", tag)
        else:
            print("Tags: No tags")

        if book["rating"] is None:
            print("Rating: Not rated yet")
        else:
            print("Rating:", book["rating"])

        print()
else:
    print("Book information could not be retrieved.")
```

`if not book["rating"]` kullanılsaydı hem `None` hem `0` yanlış kabul edilirdi. `is None` yalnızca `null` karşılığını ayırır. Bu kontrol genel bir istemci koruması değildir; alan eksikse, tür yanlışsa veya JSON bozuksa ayrıca kontrol gerekir.

### İç içe nesne: `author`

**Amaç:** Bir alanın değerinin kendi alanları bulunan başka bir nesne olabileceğini görmek.

Önceden `author` alanında ad ve soyadı içeren tek bir metin tutuyorduk. Şimdi bu alanın içine `first_name` ve `last_name` alanlarından oluşan bir JSON nesnesi koyuyoruz. Bu nedenle istemcinin yazar bilgisini okuma biçimini de değiştiriyoruz.

Burada `author` alanının değeri artık kendi alanları bulunan **bir JSON nesnesidir**. Bu nesnenin içindeki `first_name` ve `last_name` değerleri ise yine metindir.

#### Değişen satırlar

```diff
-     "author": "Deniz Kaya",
+     "author": {
+         "first_name": "Deniz",
+         "last_name": "Kaya"
+     },
...
-     "author": "Ece Yılmaz",
+     "author": {
+         "first_name": "Ece",
+         "last_name": "Yılmaz"
+     },
```

#### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": {
            "first_name": "Deniz",
            "last_name": "Kaya"
        },
        "available": True,
        "tags": ["software", "education"],
        "rating": None
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": {
            "first_name": "Ece",
            "last_name": "Yılmaz"
        },
        "available": False,
        "tags": [],
        "rating": 0
    }
]


@app.get("/api/books")
def get_books():
    return books


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

#### Değişen satırlar

```diff
-         print("Book author:", book["author"])
+         print(
+             "Book author:",
+             book["author"]["first_name"],
+             book["author"]["last_name"]
+         )
```

#### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get("http://127.0.0.1:8000/api/books")

print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

    for book in books:
        print("Book title:", book["title"])
        print(
            "Book author:",
            book["author"]["first_name"],
            book["author"]["last_name"]
        )

        if book["available"]:
            print("Availability: Available to borrow")
        else:
            print("Availability: Not available to borrow")

        if book["tags"]:
            print("Tags:")
            for tag in book["tags"]:
                print("-", tag)
        else:
            print("Tags: No tags")

        if book["rating"] is None:
            print("Rating: Not rated yet")
        else:
            print("Rating:", book["rating"])

        print()
else:
    print("Book information could not be retrieved.")
```

`book["author"]` yazar sözlüğünün tamamını; `book["author"]["last_name"]` yalnızca soyadını verir. Sunucudaki yapı değişse bile istemci ad ve soyadı birleştirerek kullanıcıya aynı görünümü sunabilir.

## Deney 8 — Başlıkta arama yapmak için sorgu parametresi kullan

### Ne yapıyoruz?

İstemci `/api/books?search=API` isteğini gönderiyor. Sunucu `search` değerini kitapların yalnızca `title` alanında arıyor.

### Neden yapıyoruz?

İstemcinin istediği sonucu sorgu parametresiyle daraltabildiğini ve parametrenin anlamını sunucu sözleşmesinin belirlediğini görmek istiyoruz.

### Sunucudaki değişen satırlar

```diff
  @app.get("/api/books")
- def get_books():
-     return books
+ def get_books(search: str = ""):
+     results = []
+     for book in books:
+         if search.casefold() in book["title"].casefold():
+             results.append(book)
+     return results
```

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": {"first_name": "Deniz", "last_name": "Kaya"},
        "available": True,
        "tags": ["software", "education"],
        "rating": None
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": {"first_name": "Ece", "last_name": "Yılmaz"},
        "available": False,
        "tags": [],
        "rating": 0
    }
]


@app.get("/api/books")
def get_books(search: str = ""):
    results = []

    for book in books:
        if search.casefold() in book["title"].casefold():
            results.append(book)

    return results


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

### İstemcideki değişen satırlar

```diff
- response = httpx.get("http://127.0.0.1:8000/api/books")
+ response = httpx.get(
+     "http://127.0.0.1:8000/api/books",
+     params={"search": "API"}
+ )
+ print("Request URL:", response.request.url)
```

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get(
    "http://127.0.0.1:8000/api/books",
    params={"search": "API"}
)

print("Request URL:", response.request.url)
print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

    for book in books:
        print("Book title:", book["title"])
        print(
            "Book author:",
            book["author"]["first_name"],
            book["author"]["last_name"]
        )

        if book["available"]:
            print("Availability: Available to borrow")
        else:
            print("Availability: Not available to borrow")

        if book["tags"]:
            print("Tags:")
            for tag in book["tags"]:
                print("-", tag)
        else:
            print("Tags: No tags")

        if book["rating"] is None:
            print("Rating: Not rated yet")
        else:
            print("Rating:", book["rating"])

        print()
else:
    print("Book information could not be retrieved.")
```

### Gözlem ve tartışma

- `search=API`, yalnızca `title` alanında aranır. Etikette `python` bulunması, başlık eşleşmiyorsa bu kodda sonuç üretmez.
- `search` HTTP veya FastAPI'nin özel kelimesi değildir; adını ve anlamını biz seçtik.
- `casefold()` sayesinde `API` ile `api` büyük ölçüde aynı arama sonucunu verir.
- Boş metin `""` sıfır karakter içerir ve Python'da her metnin içinde bulunur. Bu nedenle parametre verilmezse bütün kitaplar döner.
- Bir boşluk içeren `" "` ise boş metin değildir; yalnızca başlığında boşluk bulunan kitaplarla eşleşebilir.

### Soru–cevap: FastAPI `search` parametresini nasıl buluyor?

**Soru: Parametreyi yalnızca `search` olarak yazarsak ne değişir?**

Çalışır; ancak `= ""` varsayılan değeri kaldırıldığı için istemcinin `search` göndermesi zorunlu olur. `: str` ise beklenen türün metin olduğunu belirtir.

| Tanım | `search` gönderilmezse |
|---|---|
| `search: str = ""` | Boş metin kullanılır; mevcut kod bütün kitapları döndürür. |
| `search: str` veya `search` | FastAPI **422** yanıtı verir. 422, sunucunun isteği aldığı ancak gönderilen bilgiler beklenen koşulları karşılamadığı için işleyemediği anlamına gelen HTTP durum kodudur. |

**Soru: `search`, `@app.get("/api/books")` içinde yok. FastAPI onu nasıl görüyor?**

Dekoratör, altındaki fonksiyonu FastAPI'ye kaydeder. FastAPI hem yolu hem de fonksiyonun parametrelerini inceler; bunun için fonksiyonun gövdesini çalıştırması gerekmez.

```python
@app.get("/api/books")       # İsteğin yolu
def get_books(search):     # Fonksiyonun istediği parametre
```

Bu örnekte `search` yolda tanımlanmadığı için `?search=API` biçiminde sorgudan alınır. Değer bulunduğunda FastAPI, kavramsal olarak `get_books(search="API")` çağrısını yapar.

**Soru: Zorunlu `search` gönderilmezse hangi satırdan yanıt döner?**

FastAPI eksik parametreyi **fonksiyonu çağırmadan önce** fark eder ve 422 yanıtını kendisi oluşturur. `results = []`, `for` ve `return` satırlarının hiçbirine ulaşılmaz. İstemcide `response.status_code` değeri 422 olur.

## Deney 9 — Başarılı boş sonuç ile 404'ü ayır

### Ne yapıyoruz?

`search=astronomy` ile eşleşmeyen bir arama yapıyor ve istemcide boş listeyi açıklıyoruz.

### Neden yapıyoruz?

Koleksiyonda sıfır eşleşmenin, belirli bir kitabın bulunamamasından farklı olduğunu görmek istiyoruz.

### Değişen satırlar

```diff
-     params={"search": "API"}
+     params={"search": "astronomy"}
...
      print()
+     if not books:
+         print("No books matched your search.")
```

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get(
    "http://127.0.0.1:8000/api/books",
    params={"search": "astronomy"}
)

print("Request URL:", response.request.url)
print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

    if not books:
        print("No books matched your search.")

    for book in books:
        print("Book title:", book["title"])
        print(
            "Book author:",
            book["author"]["first_name"],
            book["author"]["last_name"]
        )

        if book["available"]:
            print("Availability: Available to borrow")
        else:
            print("Availability: Not available to borrow")

        if book["tags"]:
            print("Tags:")
            for tag in book["tags"]:
                print("-", tag)
        else:
            print("Tags: No tags")

        if book["rating"] is None:
            print("Rating: Not rated yet")
        else:
            print("Rating:", book["rating"])

        print()
else:
    print("Book information could not be retrieved.")
```

Beklenen sonuç:

```text
Status code: 200
Response body: []
Book count: 0
No books matched your search.
```

**Sonuç:** Arama başarıyla tamamlanmıştır; yalnızca eşleşen kayıt yoktur. Tek kitap işleminde `/api/books/999` belirli bir kaynağı hedefler ve kaynak yoksa `404` döner.

- **“Başlığında şu kelime geçen kitapları bul.”** → Hiç eşleşme olmasa da **200 + boş liste**.
- **“Kimliği 999 olan kitabı getir.”** → O kitap yoksa **404**; varsa **200 + kitabın bilgileri**.

## Deney 10 — İstek ve yanıt başlıklarını incele

### Ne yapıyoruz?

İstemci `Accept: application/json` gönderiyor; sunucunun `Content-Type` yanıt başlığını okuyoruz.

### Neden yapıyoruz?

İletişimde adres, durum kodu ve gövde dışında başlıkların da bulunduğunu; `Accept` ile `Content-Type` değerlerinin farklı taraflardan gönderildiğini görmek istiyoruz.

### Değişen satırlar

```diff
-     params={"search": "astronomy"}
+     params={"search": "API"},
+     headers={"Accept": "application/json"}
 )
  print("Request URL:", response.request.url)
+ print("Request Accept:", response.request.headers.get("Accept"))
  print("Status code:", response.status_code)
+ print("Response Content-Type:", response.headers.get("Content-Type"))
```

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get(
    "http://127.0.0.1:8000/api/books",
    params={"search": "API"},
    headers={"Accept": "application/json"}
)

print("Request URL:", response.request.url)
print("Request Accept:", response.request.headers.get("Accept"))
print("Status code:", response.status_code)
print("Response Content-Type:", response.headers.get("Content-Type"))
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

    if not books:
        print("No books matched your search.")

    for book in books:
        print("Book title:", book["title"])
        print(
            "Book author:",
            book["author"]["first_name"],
            book["author"]["last_name"]
        )

        if book["available"]:
            print("Availability: Available to borrow")
        else:
            print("Availability: Not available to borrow")

        if book["tags"]:
            print("Tags:")
            for tag in book["tags"]:
                print("-", tag)
        else:
            print("Tags: No tags")

        if book["rating"] is None:
            print("Rating: Not rated yet")
        else:
            print("Rating:", book["rating"])

        print()
else:
    print("Book information could not be retrieved.")
```

| Başlık | Gönderen | Anlamı |
|---|---|---|
| `Accept: application/json` | İstemci | “JSON yanıt kabul ediyorum.” |
| `Content-Type: application/json` | Sunucu | “Bu yanıt gövdesi JSON'dur.” |

`Accept` başlığı sunucunun mutlaka istenen biçimde başarıyla yanıt vereceğini garanti etmez. `Content-Type` da tek başına işlemin başarılı olduğunu göstermez; hata gövdesi de JSON olabilir.

### Bu deneyde neyi gözlemliyoruz?

Sunucu istemciye nasıl yanıt vereceğini sormaz. İstemci, isteği gönderirken `Accept: application/json` başlığıyla **“JSON biçiminde yanıt kabul ediyorum.”** bilgisini baştan iletir. Bu başlık, isteğin biçimini değil, istemcinin kabul ettiği **yanıt biçimini** belirtir.

Sunucunun yanıtındaki `Content-Type: application/json` ise **“Gönderdiğim yanıtın gövdesi JSON biçimindedir.”** demektir. Başlıklar mesajla ilgili ek bilgileri taşır; kitap bilgileri yanıtın gövdesindedir.

**Bizim sunucumuz zaten JSON döndürüyor.** `Accept` eklediğimiz için JSON'a geçmiyor. Sunucu kodumuzda bu başlığı okuyup farklı yanıt biçimleri arasında seçim yapan bir işlem de yazmadık. Bu deneyin amacı, istemcinin gönderdiği `Accept` başlığı ile sunucunun döndürdüğü `Content-Type` başlığını ayrı ayrı görmektir.

## Deney 11 — İki sorgu parametresini birlikte uygula

### Ne yapıyoruz?

Başlık aramasıyla ödünç alınabilirlik filtresini birlikte sunuyoruz:

```text
/api/books?search=API&available=true
```

### Neden yapıyoruz?

İstemcinin birden fazla koşulu iletebildiğini ve sunucunun bu koşulları birlikte değerlendirdiğini görmek istiyoruz.

### Sunucudaki değişen satırlar

```diff
- def get_books(search: str = ""):
+ def get_books(search: str = "", available: bool | None = None):
      results = []
      for book in books:
-         if search.casefold() in book["title"].casefold():
+         title_matches = search.casefold() in book["title"].casefold()
+         availability_matches = (
+             available is None or book["available"] == available
+         )
+         if title_matches and availability_matches:
              results.append(book)
```

### `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": {"first_name": "Deniz", "last_name": "Kaya"},
        "available": True,
        "tags": ["software", "education"],
        "rating": None
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": {"first_name": "Ece", "last_name": "Yılmaz"},
        "available": False,
        "tags": [],
        "rating": 0
    }
]


@app.get("/api/books")
def get_books(search: str = "", available: bool | None = None):
    results = []

    for book in books:
        title_matches = search.casefold() in book["title"].casefold()
        availability_matches = (
            available is None or book["available"] == available
        )

        if title_matches and availability_matches:
            results.append(book)

    return results


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

### İstemcideki değişen satırlar

```diff
-     params={"search": "API"},
+     params={
+         "search": "API",
+         "available": "true"
+     },
```

### `client.py` dosyasının tamamı

```python
import httpx

response = httpx.get(
    "http://127.0.0.1:8000/api/books",
    params={
        "search": "API",
        "available": "true"
    },
    headers={"Accept": "application/json"}
)

print("Request URL:", response.request.url)
print("Request Accept:", response.request.headers.get("Accept"))
print("Status code:", response.status_code)
print("Response Content-Type:", response.headers.get("Content-Type"))
print("Response body:", response.text)

if response.status_code == 200:
    books = response.json()

    print("Book count:", len(books))
    print()

    if not books:
        print("No books matched your search.")

    for book in books:
        print("Book title:", book["title"])
        print(
            "Book author:",
            book["author"]["first_name"],
            book["author"]["last_name"]
        )

        if book["available"]:
            print("Availability: Available to borrow")
        else:
            print("Availability: Not available to borrow")

        if book["tags"]:
            print("Tags:")
            for tag in book["tags"]:
                print("-", tag)
        else:
            print("Tags: No tags")

        if book["rating"] is None:
            print("Rating: Not rated yet")
        else:
            print("Rating:", book["rating"])

        print()
else:
    print("Book information could not be retrieved.")
```

### Gözlem ve tartışma

- URL'deki `&`, iki sorgu parametresini ayırır.
- Sunucu kodundaki `and`, kitabın iki koşulu da sağlamasını ister.
- Parametrelerin URL'deki veya fonksiyondaki yazım sırası bu bağımsız filtrelerin sonucunu değiştirmez.
- `available: bool | None = None`, filtre için üç durumu ayırır: `True`, `False` ve parametrenin gönderilmemesi.
- URL'deki `true` JSON gövdesi değildir. HTTPX bunu URL metni içinde taşır; FastAPI tür bildirimine göre Python `True` değerine dönüştürür.

## Deney 12 — JSON'u okumak ile kitap bilgisini kontrol etmek

### Bu deneyin amacı

**Bu deneyde, istemcinin aldığı veriyi kullanmadan önce yaptığı iki ayrı işlemi inceleyeceğiz: JSON metnini okumak ve içindeki bilgilerin uygulamanın beklentisine uyup uymadığını kontrol etmek.**

Önceki deneylerde istemci, sunucunun yanıtını şu satırla okuyordu:

```python
book = response.json()
```

Bu işlem, yanıtın JSON biçimindeki metnini Python'da kullanılabilir veriye dönüştürür. Ancak **kitabın sayfa sayısının doğru veya bizim istediğimiz türde olduğunu kontrol etmez.**

Bu farkı görmek için `page_count` adlı bir sayfa sayısı alanı kullanacağız:

| Örnek JSON metni | JSON olarak okunabilir mi? | Bizim programımız ne yapacak? |
|---|---|---|
| `{"page_count": 240,}` | Hayır. Sondaki fazladan virgül JSON yazımına aykırıdır. | Metin okunamadığı için sayfa sayısını kontrol etme aşamasına geçemeyecek. |
| `{"page_count": "240"}` | Evet. `"240"` bir metin değeridir. | “Sayfa sayısını tam sayı olarak bekliyorum.” diyerek kabul etmeyecek. |
| `{"page_count": -20}` | Evet. `-20` bir tam sayıdır. | “Sayfa sayısı sıfırdan büyük olmalı.” diyerek kabul etmeyecek. |
| `{"page_count": 240}` | Evet. `240` bir tam sayıdır. | Hem tür hem değer beklentisini karşıladığı için kabul edecek. |

**İlk satırdaki sorun JSON'un yazımıyla ilgilidir. Diğer satırlarda JSON okunmuştur; bundan sonra kararı bizim kontrol kodumuz verir.** Örneğin isteseydik `"240"` metnini sayıya dönüştürüp kabul eden bir program da yazabilirdik. Bu deneyde ise sayfa sayısının baştan pozitif tam sayı olarak gelmesini istiyoruz. Bu, JSON'un zorunlu tuttuğu bir kural değildir.

Bu örnekleri denemek için sunucu kodunu her seferinde değiştirmek yerine, JSON metinlerini ayrı bir `book_validation.py` dosyasına kendimiz yazacağız. Burada gerçek bir HTTP yanıtı almayacağız (yani programımız sunucuya istek gönderip ondan bir cevap beklemeyecek); **yanıtta gelebilecek metinleri yerelde deneyeceğiz.** Bu yüzden `response.json()` yerine, doğrudan bir metni okuyan `json.loads(response_body)` kullanacağız.

`client.py` dosyasının görevi devam ediyor. Bu alıştırma, istemcinin sunucudan aldığı veriyi neden yalnızca okuyup kullanmakla yetinmeyebileceğini göstermek için ayrı yapılmaktadır.

### Programı oluştur ve çalıştır

VS Code'da `server.py` ve `client.py` ile aynı klasörde **`book_validation.py`** oluştur ve aşağıdaki kodu kaydet. `json`, Python ile birlikte gelir; ek paket kurmana gerek yok.

```python
import json

response_body = '{"title": "API Yolculuğu", "page_count": 240}'

try:
    book = json.loads(response_body)
except json.JSONDecodeError:
    print("JSON yazımı hatalı; metin okunamadı.")
else:
    page_count = book["page_count"]

    if type(page_count) is not int:
        print("Sayfa sayısı tam sayı olmalı.")
    elif page_count <= 0:
        print("Sayfa sayısı sıfırdan büyük olmalı.")
    else:
        print("Kitap bilgisi kontrolleri geçti.")
```

İstemciyi çalıştırdığın terminalde şu komutu çalıştır:

```bash
python book_validation.py
```

İlk çıktı:

```text
Kitap bilgisi kontrolleri geçti.
```

### Kod nasıl çalışıyor?

| Kod | Anlamı |
|---|---|
| `response_body = '...'` | Örnek JSON'u bir Python metni olarak tutar. Burada gerçek bir HTTP yanıtı alınmaz; değişkenin adını biz verdik. Dıştaki tek tırnaklar Python metnini sınırlar; içteki çift tırnaklar JSON'un parçasıdır. |
| `json.loads(response_body)` | JSON metnini okur ve bu örnekte bir Python sözlüğüne dönüştürür. Bu işleme **ayrıştırma (parsing)** denir. Sunucudan alınan yanıtı `response.json()` ile okumaya benzer; burada doğrudan elimizdeki metni okuyoruz. |
| `try` / `except json.JSONDecodeError` | JSON'u okumayı dener. Yazım hatası varsa `except` altındaki mesajı yazdırır. |
| İlk `else` | Yalnızca JSON başarıyla okunursa çalışır; kitap bilgisinin kontrolleri burada başlar. |
| `book["page_count"]` | Okunan sözlükten sayfa sayısını alır. Bu deneydeki bütün örneklerde bu alan vardır. |
| `type(page_count) is not int` | Değer tam sayı değilse tür hatasını bildirir. `int`, Python'da tam sayı türüdür. |
| `elif page_count <= 0` | Değer tam sayıysa, sıfır veya negatif olup olmadığını kontrol eder. |
| Son `else` | Sayfa sayısı hem tam sayı hem sıfırdan büyükse başarı mesajını yazdırır. |

Türü önce kontrol ediyoruz; böylece `"240"` gibi bir metni `0` sayısıyla karşılaştırmaya çalışmıyoruz. Bu koşulların yazdırdığı mesajlar bizim programımıza aittir; HTTP isteği göndermediğimiz için burada 200, 404 veya 422 durum kodu yoktur.

### Yalnızca örnek metni değiştirerek dene

Her denemede dosyadaki **`response_body = ...` satırını** tablodaki satırla değiştir. **Ctrl+S** ile kaydet ve tekrar `python book_validation.py` çalıştır. Diğer kodlar aynı kalacak.

| Kullanılacak satır | Terminal çıktısı | Nedeni |
|---|---|---|
| `response_body = '{"title": "API Yolculuğu", "page_count": 240,}'` | `JSON yazımı hatalı; metin okunamadı.` | `240` sonrasındaki fazladan virgül JSON kuralına aykırıdır. Tür ve değer kontrollerine geçilemez. |
| `response_body = '{"title": "API Yolculuğu", "page_count": "240"}'` | `Sayfa sayısı tam sayı olmalı.` | JSON okunur; ancak tırnak içindeki `"240"`, tam sayı değil metindir. |
| `response_body = '{"title": "API Yolculuğu", "page_count": -20}'` | `Sayfa sayısı sıfırdan büyük olmalı.` | JSON okunur, tür de tam sayıdır; ancak değer belirlediğimiz kurala uymaz. |
| `response_body = '{"title": "API Yolculuğu", "page_count": 240}'` | `Kitap bilgisi kontrolleri geçti.` | JSON okunur ve sayfa sayısı pozitif tam sayıdır. |

Deney tamamlandığında sonraki bölüm için yeniden mevcut `client.py` dosyasına döneceğiz.

## Deney 13 — 404 ile bağlantı kuramamayı ayır

### Ne yapıyoruz?

Önce sunucuyu kapatıp mevcut istemcinin bağlantı hatasını gözlemliyor, sonra bu hatayı kontrollü biçimde yakalıyoruz.

### Neden yapıyoruz?

`404` durumunda sunucudan HTTP yanıtı gelir. Sunucu kapalıyken ise HTTP durum kodu alınmaz. Bu iki durumu aynı hata mesajıyla açıklamamak gerekir.

Sunucu terminalinde **Ctrl+C** ile sunucuyu kapat. İstemciyi çalıştırdığında `httpx.ConnectError: [Errno 111] Connection refused` benzeri bir hata beklenir.

Buradaki **111, HTTP durum kodu değil**, işletim sisteminin bağlantı hatası numarasıdır.

### Değişen satırlar

```diff
- response = httpx.get(...)
+ try:
+     response = httpx.get(...)
+ except httpx.ConnectError:
+     print("Connection failed: Could not connect to the server.")
+     print("Check that the server is running at http://127.0.0.1:8000.")
+ else:
+     # Yanıt ancak bağlantı kurulursa burada işlenir.
```

### `client.py` dosyasının tamamı

```python
import httpx

try:
    response = httpx.get(
        "http://127.0.0.1:8000/api/books",
        params={
            "search": "API",
            "available": "true"
        },
        headers={"Accept": "application/json"}
    )
except httpx.ConnectError:
    print("Connection failed: Could not connect to the server.")
    print("Check that the server is running at http://127.0.0.1:8000.")
else:
    print("Request URL:", response.request.url)
    print("Request Accept:", response.request.headers.get("Accept"))
    print("Status code:", response.status_code)
    print("Response Content-Type:", response.headers.get("Content-Type"))
    print("Response body:", response.text)

    if response.status_code == 200:
        books = response.json()

        print("Book count:", len(books))
        print()

        if not books:
            print("No books matched your search.")

        for book in books:
            print("Book title:", book["title"])
            print(
                "Book author:",
                book["author"]["first_name"],
                book["author"]["last_name"]
            )

            if book["available"]:
                print("Availability: Available to borrow")
            else:
                print("Availability: Not available to borrow")

            if book["tags"]:
                print("Tags:")
                for tag in book["tags"]:
                    print("-", tag)
            else:
                print("Tags: No tags")

            if book["rating"] is None:
                print("Rating: Not rated yet")
            else:
                print("Rating:", book["rating"])

            print()
    else:
        print("Book information could not be retrieved.")
```

Sunucu kapalıyken beklenen kısa çıktı:

```text
Connection failed: Could not connect to the server.
Check that the server is running at http://127.0.0.1:8000.
```

Bu mesaj bağlantıyı düzeltmez; istemcinin sorunu anlaşılır biçimde bildirmesini sağlar.

## Deney 14 — Yol doğrulaması ve yönlendirme sırasını dene

### Ne yapacağız?

Önce aynı sunucuya dört farklı adresle istek göndereceğiz. Ardından iki fonksiyonun dosyadaki yerini değiştirip bunun sonucu nasıl etkilediğini göreceğiz.

| İstek | Ne istiyoruz? |
|---|---|
| `/api/books/57` | Kimliği 57 olan kitabı getir. |
| `/api/books/999` | Kimliği 999 olan kitabı getir; listemizde böyle bir kitap yok. |
| `/api/books/abc` | Kitap kimliği yerine `abc` gönderiyoruz; sunucu tam sayı bekliyor. |
| `/api/books/latest` | Bu deneyde ekleyeceğimiz fonksiyonla listedeki son kitabı getir. |

`latest`, İngilizcede “en son” demektir. Bu örnekte listedeki son kaydı döndüreceğiz; tarihe göre bir sıralama yapmayacağız.

### 1. `server.py` dosyasını hazırla

`server.py` dosyasının içeriğini aşağıdaki kodla değiştir ve **Ctrl+S** ile kaydet. Önceki kitap bilgileri ve arama fonksiyonu burada da var. Eklediğimiz yeni işlem `/api/books/latest` yoludur.

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": {"first_name": "Deniz", "last_name": "Kaya"},
        "available": True,
        "tags": ["software", "education"],
        "rating": None
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": {"first_name": "Ece", "last_name": "Yılmaz"},
        "available": False,
        "tags": [],
        "rating": 0
    }
]


@app.get("/api/books")
def get_books(search: str = "", available: bool | None = None):
    results = []

    for book in books:
        title_matches = search.casefold() in book["title"].casefold()
        availability_matches = (
            available is None or book["available"] == available
        )

        if title_matches and availability_matches:
            results.append(book)

    return results


@app.get("/api/books/latest")
def get_latest_book():
    return books[-1]


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

`books[-1]`, Python'da listenin son elemanını alır. Yukarıdaki listede bu, kimliği 57 olan kitaptır.

Sunucu önceki deneyde kapatılmıştı. Sunucu terminalinde aşağıdaki komutla başlat. Hâlâ çalışıyorsa önce **Ctrl+C** ile kapat, ardından yeniden başlat:

```bash
python -m uvicorn server:app
```

### 2. `client.py` dosyasını hazırla

Bu deneyde durum kodunu ve yanıt gövdesini görmek yeterli. `client.py` dosyasının içeriğini aşağıdaki kısa kodla değiştir ve kaydet. İstekleri bu dosyadan göndereceğiz; `book_validation.py` dosyasını çalıştırmayacağız.

```python
import httpx

path = "/api/books/57"

try:
    response = httpx.get("http://127.0.0.1:8000" + path)
except httpx.ConnectError:
    print("Sunucuya bağlanılamadı. Sunucunun çalıştığını kontrol et.")
else:
    print("Request URL:", response.request.url)
    print("Status code:", response.status_code)
    print("Response body:", response.text)
```

`path`, adresin değiştirerek deneyeceğimiz yol kısmıdır. `+` ile sunucu adresinin sonuna eklenir. `response.text` yanıt gövdesini doğrudan yazdırdığı için hem kitap bilgisini hem hata mesajını görebiliriz.

İkinci terminalde çalıştır:

```bash
python client.py
```

İlk çalıştırmada `Status code: 200` ve kimliği 57 olan kitabın bilgileri görünmelidir.

### 3. Dört adresi sırayla dene

Her denemede `client.py` içindeki **`path = ...` satırını** aşağıdaki satırla değiştir, **Ctrl+S** ile kaydet ve `python client.py` komutunu tekrar çalıştır. Yalnızca istemci değiştiği için sunucuyu yeniden başlatmana gerek yok.

| İstemcide kullanılacak satır | Durum kodu | Yanıt ve nedeni |
|---|---|---|
| `path = "/api/books/57"` | `200` | 57 numaralı kitabın bilgileri gelir. `get_book` çalışır ve kitabı bulur. |
| `path = "/api/books/999"` | `404` | `{"detail":"Book not found"}` gelir. `get_book` çalışır; kitap bulunamadığı için `raise HTTPException(...)` satırına ulaşır. |
| `path = "/api/books/abc"` | `422` | Yanıt, `book_id` değerinin tam sayıya çevrilemediğini bildirir. FastAPI `get_book` fonksiyonunu çağırmadan yanıt verir. |
| `path = "/api/books/latest"` | `200` | `get_latest_book` çalışır; listedeki son kitabın, yani 57 numaralı kitabın bilgileri gelir. |

`abc` isteğinin hata gövdesinde `"loc":["path","book_id"]` ve `"input":"abc"` gibi bilgiler görürsün. Bunlar sorunun URL yolundaki `book_id` değerinde olduğunu gösterir. Hata metninin ayrıntıları sürüme göre değişebilir.

### 4. Fonksiyonların sırasını değiştir ve sonucu gözlemle

Şimdi yalnızca `server.py` dosyasının sonundaki **`get_latest_book` ve `get_book` fonksiyonlarını, üstlerindeki dekoratörlerle birlikte** aşağıdaki blokla değiştir. Aynı fonksiyonları dosyaya ikinci kez ekleme. `books` listesi ve `get_books` fonksiyonu aynı kalacak.

```python
@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")


@app.get("/api/books/latest")
def get_latest_book():
    return books[-1]
```

Dosyayı kaydet. **Sunucu kodu değiştiği için** sunucu terminalinde **Ctrl+C** ile kapat ve yeniden başlat:

```bash
python -m uvicorn server:app
```

İstemcide şu satırın bulunduğundan emin ol:

```python
path = "/api/books/latest"
```

İstemci dosyasını kaydet ve ikinci terminalde yeniden çalıştır:

```bash
python client.py
```

Bu kez **`Status code: 422`** görmelisin. Hata gövdesi `latest` değerinin tam sayıya çevrilemediğini bildirir.

| Adım | Ne oluyor? |
|---|---|
| Yol seçiliyor. | FastAPI yolları kayıt sırasıyla kontrol eder. Önce gelen `/api/books/{book_id}`, `/api/books/latest` isteğiyle eşleşir; `latest`, `book_id` için aday değer olur. |
| Parametre kontrol ediliyor. | Fonksiyon `book_id: int` istediği için FastAPI `latest` metnini tam sayıya çevirmeyi dener. |
| Dönüşüm başarısız oluyor. | 422 yanıtı verilir. `get_book` gövdesi çalışmaz; daha aşağıdaki `get_latest_book` fonksiyonuna da geçilmez. |

**Yol eşleşmesi ile parametrenin tür kontrolü ayrı adımlardır.** `book_id: int` yazmak, yönlendirmenin `latest` sözcüğünü atlayıp sonraki yolu denemesini sağlamaz. Bu nedenle sabit `/api/books/latest` yolunu, onu da yakalayabilen `/api/books/{book_id}` yolundan önce tanımlarız. [FastAPI: yol sırası](https://fastapi.tiangolo.com/tutorial/path-params/#order-matters)

### 5. Doğru sıraya geri dön

`get_latest_book` fonksiyonunu dekoratörüyle birlikte yeniden `get_book` fonksiyonunun üstüne taşı; ilk verdiğimiz tam `server.py` kodundaki sırayı kullan. Kaydet, sunucuyu **Ctrl+C** ile kapatıp aynı komutla yeniden başlat ve istemciyi tekrar çalıştır. `/api/books/latest` yeniden **200** döndürmelidir.

Mevcut `/api/books` ve `/api/books/{book_id}` yolları ise bu şekilde çakışmaz: ilkinin sonunda kitap kimliği için ek bir parça yoktur. `/api/books?search=API&available=true` isteğinde de yol `/api/books` olarak kalır; `?` sonrasındaki sorgu parametreleri `get_books` fonksiyonuna aktarılır.

## Son uygulama — Üçüncü kitabı ekle ve filtrele

### Ne yapıyoruz?

Öğrendiğimiz veri yapılarıyla üçüncü kitabı koleksiyona ekliyor; istemciden başlık ve ödünç durumu koşullarını birlikte gönderiyoruz.

### Neden yapıyoruz?

Haftanın veri türleri, sorgu parametreleri, koşulları ve istemci görünümü çalışmalarını tek çalışan örnekte birleştiriyoruz.

### Sunucudaki değişen satırlar

```diff
      {
          "id": 57,
          ...
          "rating": 0
+     },
+     {
+         "id": 73,
+         "title": "Python ile Web API",
+         "author": {
+             "first_name": "Can",
+             "last_name": "Demir"
+         },
+         "available": True,
+         "tags": ["python", "api"],
+         "rating": 4.5
      }
```

### Son `server.py` dosyasının tamamı

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": {
            "first_name": "Deniz",
            "last_name": "Kaya"
        },
        "available": True,
        "tags": ["software", "education"],
        "rating": None
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": {
            "first_name": "Ece",
            "last_name": "Yılmaz"
        },
        "available": False,
        "tags": [],
        "rating": 0
    },
    {
        "id": 73,
        "title": "Python ile Web API",
        "author": {
            "first_name": "Can",
            "last_name": "Demir"
        },
        "available": True,
        "tags": ["python", "api"],
        "rating": 4.5
    }
]


@app.get("/api/books")
def get_books(search: str = "", available: bool | None = None):
    results = []

    for book in books:
        title_matches = search.casefold() in book["title"].casefold()
        availability_matches = (
            available is None or book["available"] == available
        )

        if title_matches and availability_matches:
            results.append(book)

    return results


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

### İstemcideki değişen satırlar

```diff
      params={
-         "search": "API",
+         "search": "Python",
          "available": "true"
      },
```

### Son `client.py` dosyasının tamamı

```python
import httpx

try:
    response = httpx.get(
        "http://127.0.0.1:8000/api/books",
        params={
            "search": "Python",
            "available": "true"
        },
        headers={"Accept": "application/json"}
    )
except httpx.ConnectError:
    print("Connection failed: Could not connect to the server.")
    print("Check that the server is running at http://127.0.0.1:8000.")
else:
    print("Request URL:", response.request.url)
    print("Request Accept:", response.request.headers.get("Accept"))
    print("Status code:", response.status_code)
    print("Response Content-Type:", response.headers.get("Content-Type"))
    print("Response body:", response.text)

    if response.status_code == 200:
        books = response.json()

        print("Book count:", len(books))
        print()

        if not books:
            print("No books matched your search.")

        for book in books:
            print("Book title:", book["title"])
            print(
                "Book author:",
                book["author"]["first_name"],
                book["author"]["last_name"]
            )

            if book["available"]:
                print("Availability: Available to borrow")
            else:
                print("Availability: Not available to borrow")

            if book["tags"]:
                print("Tags:")
                for tag in book["tags"]:
                    print("-", tag)
            else:
                print("Tags: No tags")

            if book["rating"] is None:
                print("Rating: Not rated yet")
            else:
                print("Rating:", book["rating"])

            print()
    else:
        print("Book information could not be retrieved.")
```

Beklenen temel sonuç:

```text
Book count: 1
Book title: Python ile Web API
Book author: Can Demir
Availability: Available to borrow
Tags:
- python
- api
Rating: 4.5
```

## Çalışırken karşılaşılan sorunlar

### `python: command not found`

Sanal ortam etkin değilse Linux veya WSL'de `python3` kullan. Sanal ortam etkinleştirildiğinde `python` komutu ortamın çalıştırıcısını göstermelidir:

```bash
source api-env/bin/activate
```

### `uv: command not found`

uv kurulduğu hâlde mevcut terminal bulamıyorsa:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### `address already in use`

PID bulma, süreç durumunu kontrol etme ve duraklatılmış sunucuyu kapatma adımları için belgenin başındaki [Sunucuyu kapatma, PID bulma ve dolu portu boşaltma](#sunucu-surec-yonetimi) açıklamasını kullan.

8000 portunda eski sunucu çalışıyor olabilir:

```bash
ss -ltnp 'sport = :8000'
```

Sunucu terminalinde **Ctrl+C** işlemi kapatır. **Ctrl+Z** işlemi kapatmak yerine duraklatabilir; duraklatılan işlem portu tutmaya devam eder. Süreç numarası biliniyorsa önce ne olduğunu kontrol et:

```bash
ps -p 4225 -o pid,ppid,stat,args
```

Buradaki `4225` yalnızca örnektir; kendi çıktındaki PID değerini kullan.

### Kod değişti ama eski sonuç geliyor

Uvicorn'u otomatik yenileme seçeneği olmadan başlattık. `server.py` değişince sunucuyu Ctrl+C ile kapatıp yeniden çalıştır:

```bash
python -m uvicorn server:app
```

Yalnızca `client.py` değiştiyse sunucuyu yeniden başlatmaya gerek yoktur.

### Web sitesindeki 404 ile API'deki 404

İkisi de HTTP durum kodudur. Bir web sitesi genellikle insan için HTML hata sayfası, API ise istemci program için JSON hata gövdesi döndürür. Her iki durumda da HTTP yanıtı alınmıştır.

## Haftalık değerlendirme

### Sorular

1. `client.py` ve `server.py` hangi rolleri üstlenir? Uvicorn'un görevi nedir?
2. `GET /api/books/57` içinde `GET` ve `57` ayrı ayrı neyi belirtir?
3. `404` ile `httpx.ConnectError` arasındaki temel fark nedir?
4. `false`, `null` ve `0` neden aynı kabul edilmemelidir?
5. `search=Python` parametresi mevcut sunucu kodunda hangi alanda aranır? Yalnızca `tags` içinde `python` bulunması yeterli midir?
6. URL'deki `&` ile Python kodundaki `and` ne iş yapar?
7. `/api/books?search=astronomy` neden `200` ve `[]`; `/api/books/999` neden `404` döndürür?
8. `/api/books/abc` neden `404` yerine `422` döndürebilir?
9. `Accept` ile `Content-Type` başlıklarını hangi taraf gönderir ve ne anlatırlar?
10. `GET /api/books?search=Python&available=true` isteğinden kitabın terminalde görünmesine kadar süreci altı kısa adımda anlat.

### Cevapları değerlendirirken aranacak noktalar

- İstemci isteği başlatır; sunucu isteği karşılar; Uvicorn uygulamayı çalıştırıp bağlantıları dinler.
- `GET` bilgi alma niyetini, `/57` hedef kitap kimliğini belirtir.
- `404` alınmış HTTP yanıtıdır; bağlantı hatasında kullanılabilir HTTP yanıtı yoktur.
- `false` mantıksal cevap, `null` sözleşmeye göre yorumlanan özel boş/yok değeri, `0` sayıdır.
- `search` yalnızca `title` alanında aranır; parametrenin anlamını sunucu kodu belirler.
- `&` URL parametrelerini ayırır; `and` iki koşulun birlikte doğru olmasını ister.
- Koleksiyon araması sıfır sonuçla tamamlanabilir; tek kaynak isteğinde hedef yoksa `404` verilir.
- `abc`, `book_id: int` tür doğrulamasını geçemez.
- `Accept` istemcinin kabul ettiği biçimi, `Content-Type` sunucunun gönderdiği gövde biçimini bildirir.
- Yol eşleşmesi, parametre dönüşümü, filtreleme, serileştirme, HTTP yanıtı, ayrıştırma ve istemci görünümü birbirinden ayrılmalıdır.

## Kaynaklar

- [FastAPI — First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [FastAPI — Path Parameters](https://fastapi.tiangolo.com/tutorial/path-params/)
- [HTTPX — QuickStart](https://www.python-httpx.org/quickstart/)
- [HTTPX — Exceptions](https://www.python-httpx.org/exceptions/)
- [uv — Installation](https://docs.astral.sh/uv/getting-started/installation/)
- [Python — `json` modülü](https://docs.python.org/3/library/json.html)

Bu föydeki uygulama `localhost` üzerinde çalışır; genel internet bağlantısı API iletişimi için gerekli değildir. İnternet yalnızca araçların ilk kurulumu sırasında gerekebilir.

# Hafta 06 — Uygulama Föyü

## 0. Veri nerede duruyor?

Hafta 2'den beri sunucumuzun kitapları `server.py` dosyasındaki `books` listesinde duruyor. Bu listenin üç sonucunu gördük:

- Hafta 2'nin Deney 6'sında yeni bir kitap ekledik, sunucuyu yeniden başlattık ve kitap kayboldu: Liste yalnızca çalışan sunucunun belleğinde duruyordu.
- Hafta 4'teki [ek notta](../Week_04/04_Supplement_Deleted_Book_Reviews.md) bir kitabı sildik, ama yorumları `reviews` listesinde kaldı. Kitapla yorumları arasındaki ilişkiyi korumak bize kalmıştı.
- Hafta 5'teki [ek notta](../Week_05/05_Supplement_Inherited_Rules.md) 57 numaralı kitabın puanını değiştirdik, ama sunucu her başladığında puan yine `0` oldu.

Bu hafta kitapları ve yorumları bir **veritabanında (database)** saklayacağız. Veritabanı, veriyi kendi dosyalarında tutan ayrı bir programdır: Bizim sunucumuz kapansa da veri orada durur. Biz **PostgreSQL** veritabanını kullanacağız; Python kodumuzla veritabanı arasındaki işi de **SQLModel** kütüphanesi yapacak.

API'nin dışı değişmeyecek: Aynı istekler aynı yanıtları alacak. Değişen, verinin durduğu yer.

Haftanın sonunda şu soruya cevap verebileceksin: **Bir kitap Python kodunda, veritabanında ve API yanıtında nasıl görünür; sunucu kapanınca neden kaybolmaz?**

Bu hafta sırasıyla şunları yapacağız:

- **Deney 1:** Bir Python sınıfından veritabanı tablosu oluşturmak ve kitapları tabloya yazmak
- **Deney 2:** Python programından kayıt eklemek ve okumak
- **Deney 3:** Sunucunun okuma işlemlerini veritabanına taşımak
- **Deney 4:** Yazma işlemlerini taşımak ve sunucu yeniden başlayınca kayıtların durduğunu görmek
- **Deney 5:** Yorumları ikinci bir tabloya taşımak ve iki tabloyu birbirine bağlamak
- **Deney 6** (ödev): SQLModel'in veritabanına gönderdiği komutları görmek

### 0.1 Başlangıç dosyaları

Hafta 5'in sonundaki dosyalarla başla:

| Dosya | Hafta 5 föyündeki yeri |
|---|---|
| `server.py` | 7. bölümdeki son hâli: alan kuralları ve `Path(gt=0)` eklenmiş sunucu |
| `client.py` | Her deneyde içeriğini baştan yazacağız. |

Kendi `server.py` dosyandan emin değilsen, bu haftanın [başlangıç dosyasını](Starting_Code/server.py) kullan; föydeki çıktılar bu dosyayla alındı.

Bu hafta aynı klasöre üç yeni dosya ekleyeceğiz: `database.py`, `reset_db.py` ve yalnızca Deney 2'de kullanacağımız `try_db.py`.

### 0.2 PostgreSQL'i başlat

PostgreSQL'i bilgisayarına kurmak yerine **Docker** ile çalıştıracağız. Docker, bir programı gerekli her şeyiyle birlikte paketlenmiş hâlde çalıştırır; böylece herkesin veritabanı aynı ayarlarla çalışır. Önce Docker'ın hazır olduğunu kontrol et:

```bash
docker --version
```

Çıktı `Docker version` ile başlamalı. `docker: command not found` gibi bir hata alırsan Docker kurulu değildir: [Docker'ın kurulum sayfasındaki](https://docs.docker.com/get-started/get-docker/) adımları izle. Windows'ta WSL terminalini kullanıyorsan Docker Desktop'ı Windows'a kur; WSL terminalinden kullanabilmek için [WSL desteğinin](https://docs.docker.com/desktop/features/wsl/) açık olması gerekir.

Ardından PostgreSQL'i başlat. Bu komutu yalnızca **bir kez** çalıştıracaksın:

```bash
docker run --name book-db -e POSTGRES_USER=student -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=catalog -p 5432:5432 -d postgres:16
```

| Parça | Anlamı |
|---|---|
| `docker run` | Bir **imajdan (image)** yeni bir **kapsayıcı (container)** oluşturup başlatır. İmaj programın paketlenmiş hâli, kapsayıcı ise o paketten başlatılmış, çalışan kopyasıdır. |
| `--name book-db` | Kapsayıcının adı. Sonraki komutlarda kapsayıcıyı bu adla çağıracağız. |
| `-e POSTGRES_USER=student` | Veritabanına bağlanacak kullanıcının adı. `-e`, kapsayıcıya bir ayar verir. |
| `-e POSTGRES_PASSWORD=secret` | Bu kullanıcının parolası |
| `-e POSTGRES_DB=catalog` | Oluşturulacak veritabanının adı |
| `-p 5432:5432` | Bilgisayarın 5432 numaralı portuna gelen bağlantıları kapsayıcının 5432 numaralı portuna iletir. Sunucumuz 8000 numaralı portu dinliyor; PostgreSQL de 5432'yi dinler (Hafta 1). |
| `-d` | Kapsayıcıyı arka planda çalıştırır; terminal serbest kalır. |
| `postgres:16` | Kullanılacak imaj: PostgreSQL'in 16. sürümü. İlk seferde internetten indirilir. |

Kapsayıcının çalıştığını kontrol et:

```bash
docker ps
```

Listede `book-db` adını ve `STATUS` sütununda `Up` ile başlayan bir yazı görmelisin.

Bilgisayarını kapatıp açtığında kapsayıcı da durur. O zaman yukarıdaki uzun komutu değil, şunu çalıştır:

```bash
docker start book-db
```

`docker run` her çalıştığında yeni bir kapsayıcı oluşturmaya çalışır; `docker start` ise var olanı, içindeki veriyle birlikte yeniden başlatır. Docker'la ilgili diğer komutları ve "port is already allocated" gibi hataların çözümünü [ek notta](03_Supplement_Docker.md) bulabilirsin.

> **Parola kodun içinde:** `student` ve `secret`, yalnızca kendi bilgisayarındaki bu deneme veritabanı için. Gerçek bir uygulamada parola kodun içine yazılmaz; çalışma ayarlarını koddan ayırmayı Hafta 11'de göreceğiz.

### 0.3 Paketleri kur

Sanal ortam etkinken iki paket kur:

```bash
uv pip install sqlmodel "psycopg[binary]"
```

| Paket | Görevi |
|---|---|
| **SQLModel** | Python sınıflarımızı veritabanı tablolarına bağlar; kayıt eklemeyi, okumayı, değiştirmeyi ve silmeyi Python koduyla yapmamızı sağlar. Pydantic ve SQLAlchemy adlı iki kütüphanenin üzerine kuruludur. |
| **psycopg** | Python ile PostgreSQL arasındaki bağlantıyı kuran **sürücü (driver)**. SQLModel veritabanıyla bu sürücü üzerinden konuşur. `[binary]`, sürücünün kurulmaya hazır hâlinin indirilmesini sağlar. |

Kurulumu kontrol et:

```bash
python -c "import sqlmodel; print(sqlmodel.__version__)"
```

Çıktı `0.0.21` ya da daha yeni bir sürüm olmalı, örneğin `0.0.48`. Föydeki çıktılar SQLModel 0.0.48 ve PostgreSQL 16 ile alındı.

> **Çıktıları föydekilerle aynı görmek için:** Sunucuyu yeniden başlatmak artık kitapları başlangıç hâline döndürmez; bu haftanın konusu da bu. Deneylerde "veritabanını sıfırla" adımını gördüğünde Deney 1'de yazacağımız `python reset_db.py` komutunu çalıştır.

---

## Deney 1 — İlk tablo: Python sınıfından veritabanına

**Amaç:** Kitapları saklayacak tabloyu bir Python sınıfıyla tanımlamak, tabloyu oluşturmak ve başlangıçtaki üç kitabı tabloya yazmak.

Bu deneyde `server.py` dosyasına dokunmuyoruz. Veritabanıyla ilgili kodu ayrı bir dosyada topluyoruz.

### 1.1 `database.py`: tablonun modeli

`server.py` ile aynı klasörde `database.py` adlı yeni bir dosya oluştur:

```python
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, create_engine

DATABASE_URL = "postgresql+psycopg://student:secret@localhost:5432/catalog"

engine = create_engine(DATABASE_URL)


# Kitap tablosu: her Book nesnesi tabloda bir kayıttır.
class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author: dict = Field(sa_column=Column(JSONB, nullable=False))
    available: bool
    tags: list[str] = Field(sa_column=Column(JSONB, nullable=False))
    rating: float | None = None
    internal_note: str | None = None
```

İlk iki satırdaki `sqlalchemy` paketini ayrıca kurmadık: SQLModel'in üzerine kurulduğu kütüphane, 0.3'te SQLModel'le birlikte kuruldu.

`DATABASE_URL`, veritabanının adresidir. Parçaları 0.2'deki `docker run` komutundan geliyor:

| Parça | Anlamı |
|---|---|
| `postgresql+psycopg` | Veritabanının türü (PostgreSQL) ve bağlanırken kullanılacak sürücü (psycopg) |
| `student:secret` | Kullanıcı adı ve parola: `POSTGRES_USER` ve `POSTGRES_PASSWORD` |
| `localhost:5432` | Veritabanının çalıştığı bilgisayar ve port: `-p 5432:5432` |
| `catalog` | Veritabanının adı: `POSTGRES_DB` |

Kodun geri kalanı:

| Kod | Ne yapar? |
|---|---|
| `engine = create_engine(DATABASE_URL)` | Veritabanına bağlantıları yöneten **motoru (engine)** oluşturur. Bağlantıyı hemen kurmaz; veritabanıyla ilk işlemde kurar. |
| `class Book(SQLModel, table=True)` | `table=True`, bu sınıfın bir **tablo (table)** tanımladığını söyler. Tablonun adı sınıfın adından gelir: `book`. |
| `id: int \| None = Field(default=None, primary_key=True)` | `id` bu tablonun **birincil anahtarı (primary key)**: her kaydı tek başına tanıtan sütun. Tabloda iki kaydın kimliği aynı olamaz. Varsayılan değerin `None` olmasının nedenini Deney 2'de göreceğiz. |
| `author: dict = Field(sa_column=Column(JSONB, nullable=False))` | Yazar bir sözlük. Tablonun bir hücresine tek bir değer yazılır; PostgreSQL'in `JSONB` türü bir hücrede JSON saklamamızı sağlar. `sa_column`, sütunu doğrudan SQLAlchemy'nin `Column` sınıfıyla tanımlamamızı sağlar (*sa*: SQLAlchemy); SQLModel'in kendisi `JSONB` türünü bilmiyor. `nullable=False`, bu hücrenin boş bırakılamayacağını söyler. |
| `tags: list[str] = Field(sa_column=Column(JSONB, nullable=False))` | Etiket listesi de aynı yolla bir hücrede saklanır. |
| `rating: float \| None = None` | Puan boş olabilir. |
| `internal_note: str \| None = None` | Hafta 4'teki iç not da tabloda duruyor. İstemciye gitmemesini yine yanıt modeli sağlayacak. |

`author` ve `tags` alanlarını başka yollarla da saklayabilirdik; seçeneklerini [ek notta](04_Supplement_JSONB_Columns.md) görebilirsin.

İki not:

- **Bu dosyadaki `Field`, SQLModel'in `Field` fonksiyonu.** `server.py` dosyasındaki `Field` ise Pydantic'in. Adları aynı, görevleri farklı: Pydantic'in `Field` fonksiyonu gelen değere kural koyar, SQLModel'inki tablonun sütununu tanımlar. Veritabanı kodunu ayrı bir dosyaya koymamızın bir nedeni de bu.
- **`Book` modelinde `min_length` ya da `ge` gibi kurallar yok.** İstemciden gelen değeri yine `BookCreate` ve `BookUpdate` kontrol edecek. `Book` yalnızca verinin tabloda nasıl saklanacağını anlatıyor.

### 1.2 `reset_db.py`: tabloyu oluştur ve kitapları yaz

Aynı klasörde `reset_db.py` adlı bir dosya daha oluştur:

```python
from sqlalchemy import text
from sqlmodel import Session, SQLModel

from database import Book, engine

# Tabloları sil ve modellere göre yeniden oluştur.
SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    session.add(Book(
        id=42,
        title="API Yolculuğu",
        author={"first_name": "Deniz", "last_name": "Kaya"},
        available=True,
        tags=["software", "education"],
        rating=None,
        internal_note="Kapağı yıpranmış, yenisi sipariş edildi.",
    ))
    session.add(Book(
        id=57,
        title="Veriyle İlk Adımlar",
        author={"first_name": "Ece", "last_name": "Yılmaz"},
        available=False,
        tags=[],
        rating=0,
    ))
    session.add(Book(
        id=73,
        title="Python ile Web API",
        author={"first_name": "Can", "last_name": "Demir"},
        available=True,
        tags=["python", "api"],
        rating=4.5,
    ))
    session.commit()

    # Kimlik sayacını en büyük kimliğe getir: yeni kitabın kimliği 74 olsun.
    session.execute(text("SELECT setval(pg_get_serial_sequence('book', 'id'), (SELECT MAX(id) FROM book))"))
    session.commit()

print("Database reset: 3 books")
```

| Kod | Ne yapar? |
|---|---|
| `from database import Book, engine` | Kendi `database.py` dosyamızdaki `Book` sınıfını ve `engine` nesnesini alır. Bunun için iki dosya aynı klasörde olmalı. |
| `SQLModel.metadata.drop_all(engine)` | `table=True` ile tanımlanmış tabloları, içindeki bütün kayıtlarla birlikte siler. |
| `SQLModel.metadata.create_all(engine)` | Bu tabloları modellere göre yeniden oluşturur. |
| `with Session(engine) as session:` | Veritabanıyla bir çalışma oturumu açar. Ayrıntısını Deney 2'de göreceğiz. |
| `session.add(Book(id=42, ...))` | Bir `Book` nesnesi oluşturur ve kaydedilmek üzere oturuma ekler. Kimlikleri kendimiz veriyoruz, çünkü önceki haftalardaki kimliklerin aynı kalmasını istiyoruz. |
| `session.commit()` | Eklenenleri veritabanına yazar. |
| `session.execute(text("SELECT setval(...)"))` | Veritabanı yeni kayıtlara kimliği bir **sayaçtan (sequence)** verir. Biz kimlikleri kendimiz yazdığımız için sayaç hâlâ en baştaydı; bu satır onu 73'e getirir, böylece ilk yeni kitap `74` olur. Bu satır olmasaydı ne olacağını [ek notta](05_Supplement_Id_Sequence.md) görebilirsin. |

`reset_db.py` dosyasını şimdiye kadar yazdığımız programlardan ayıran bir şey var: Veritabanındaki bütün kitapları siler. Yalnızca bu deneme veritabanında, föyü izlerken çalıştır.

Programı çalıştır:

```bash
python reset_db.py
```

```text
Database reset: 3 books
```

### 1.3 Tabloya bakmak

Kitaplar artık `server.py` dosyasında değil, veritabanında. Onları görmek için PostgreSQL'in kendi terminal programı **psql**'i kapsayıcının içinde çalıştıralım:

```bash
docker exec book-db psql -U student -d catalog -c "SELECT id, title, available, rating FROM book;"
```

| Parça | Anlamı |
|---|---|
| `docker exec book-db` | `book-db` kapsayıcısının içinde bir komut çalıştırır. |
| `psql -U student -d catalog` | `student` kullanıcısıyla `catalog` veritabanına bağlanır. |
| `-c "..."` | Tırnak içindeki komutu çalıştırır ve çıkar. |
| `SELECT id, title, available, rating FROM book;` | **SQL** komutu: "`book` tablosundaki kayıtların bu dört sütununu getir." SQL, veritabanlarıyla konuşmak için kullanılan dildir. |

```text
 id |        title        | available | rating
----+---------------------+-----------+--------
 42 | API Yolculuğu       | t         |
 57 | Veriyle İlk Adımlar | f         |      0
 73 | Python ile Web API  | t         |    4.5
(3 rows)
```

Tablodaki her satır bir **kayıt (record)**, her sütun bir alan. `t` ve `f`, psql'in `true` ve `false` yazımıdır. 42 numaralı kitabın puanı boş görünüyor: Veritabanında bu boş değere `NULL` denir; Python'da `None`, JSON'da `null` olarak gördüğümüz değerin karşılığıdır.

Veritabanından veri isteyen `SELECT` gibi komutlara **sorgu (query)** da denir. Hafta 1'deki sorgu parametresiyle karıştırma: İkisinin İngilizcesi de *query*, ama sorgu parametresi adresin içinde, SQL sorgusu ise veritabanına gönderilen bir komut. Bu föyde karışmasın diye "SQL komutu" diyeceğiz.

Tablonun yapısını da görebiliriz. `\d`, SQL değil, psql'in kendi komutudur (*describe*: tanımla); ardından yazılan tablonun sütunlarını gösterir:

```bash
docker exec book-db psql -U student -d catalog -c "\d book"
```

```text
                                     Table "public.book"
    Column     |       Type        | Collation | Nullable |             Default
---------------+-------------------+-----------+----------+----------------------------------
 id            | integer           |           | not null | nextval('book_id_seq'::regclass)
 title         | character varying |           | not null |
 author        | jsonb             |           | not null |
 available     | boolean           |           | not null |
 tags          | jsonb             |           | not null |
 rating        | double precision  |           |          |
 internal_note | character varying |           |          |
Indexes:
    "book_pkey" PRIMARY KEY, btree (id)
```

Bu tabloyu biz SQL ile yazmadık; `create_all` onu `Book` sınıfından oluşturdu. Python tarafıyla veritabanı tarafı şöyle eşleşiyor:

| Python'da | Veritabanında | Örnek |
|---|---|---|
| `table=True` olan sınıf: `Book` | Tablo: `book` | |
| Sınıftaki alan: `title: str` | **Sütun (column)**: `title`, türü `character varying` (metin) | `bool` → `boolean`, `float` → `double precision`, `dict` → `jsonb` |
| `\| None` olmayan alan | `not null`: Sütun boş bırakılamaz. | `title`, `author`, `available`, `tags` |
| `\| None` olan alan | `Nullable` sütunu boş: Değer `NULL` olabilir. | `rating`, `internal_note` |
| `primary_key=True` | `PRIMARY KEY` | `id` |
| Bir `Book(...)` nesnesi | Tabloda bir kayıt | 42 numaralı kitap |

`id` sütununun `Default` değerindeki `book_id_seq`, 1.2'deki `setval` satırının ayarladığı sayaçtır: Kimliği verilmeyen yeni bir kayda kimliği bu sayaç verir.

> **Ana fikir:** `table=True` ile yazılan bir SQLModel sınıfı bir tabloyu tanımlar: Sınıfın alanları tablonun sütunları, sınıftan oluşturulan her nesne tablonun bir kaydıdır. Tabloları ve başlangıç kayıtlarını `reset_db.py` oluşturuyor; kayıtlar artık `server.py` dosyasında değil, veritabanında duruyor.

---

## Deney 2 — Kayıt eklemek ve okumak

**Amaç:** Python'dan veritabanına bir kayıt eklemek, kayıtları okumak ve program bittikten sonra kaydın durduğunu görmek.

Sunucuya geçmeden önce aynı işi küçük bir programla deneyelim.

### 2.1 Bir kitap ekle ve oku

`try_db.py` adlı bir dosya oluştur:

```python
from sqlmodel import Session, select

from database import Book, engine

# Kaydetmek: yeni bir Book nesnesi oluştur ve veritabanına yaz.
with Session(engine) as session:
    book = Book(
        title="Deneme Kitabı",
        author={"first_name": "Ada", "last_name": "Yıldız"},
        available=True,
        tags=[],
    )
    print("Before saving:", book.id)
    session.add(book)
    session.commit()
    session.refresh(book)
    print("After saving: ", book.id)

# Okumak: tablodaki bütün kitapları kimlik sırasıyla al.
with Session(engine) as session:
    statement = select(Book).order_by(Book.id)
    for book in session.exec(statement).all():
        print(book.id, book.title)
```

| Kod | Ne yapar? |
|---|---|
| `with Session(engine) as session:` | Veritabanıyla bir **oturum (session)** açar. Oturum, veritabanıyla yapılan bir işin sınırlarını çizer: Eklemeler ve değişiklikler önce oturumda toplanır. `with` bloğu bitince oturum kendiliğinden kapanır. |
| `book = Book(...)` | Yeni bir kitap nesnesi oluşturur. Kimlik vermedik; `id` alanı varsayılan değeri olan `None` olarak kalır. |
| `session.add(book)` | Oturuma "bu kitap kaydedilecek" der. Kitap henüz veritabanına yazılmadı. |
| `session.commit()` | Oturumdaki değişiklikleri veritabanına yazar ve onları **kalıcı hâle getirir (commit)**. Veritabanı bu sırada sayaçtan kitaba bir kimlik verir. |
| `session.refresh(book)` | Kitabı veritabanından yeniden okur. Veritabanının verdiği kimlik böylece `book` nesnesine gelir. |
| `select(Book).order_by(Book.id)` | Bir SQL komutu hazırlar: "`book` tablosundaki kayıtları getir, kimliğe göre sırala." Bu, 1.3'te psql ile yazdığımız `SELECT` komutunun Python'daki hâlidir. |
| `session.exec(statement).all()` | Komutu veritabanına gönderir ve gelen kayıtları bir liste olarak verir. Listenin her öğesi bir `Book` nesnesidir. |

Programı çalıştır:

```bash
python try_db.py
```

```text
Before saving: None
After saving:  74
42 API Yolculuğu
57 Veriyle İlk Adımlar
73 Python ile Web API
74 Deneme Kitabı
```

Kitabın kimliği kaydetmeden önce `None`, kaydettikten sonra `74`. Kimliği biz vermedik, veritabanı verdi. `Book` modelinde `id` alanının `int | None` olmasının nedeni bu: Nesne Python'da oluşturulduğu anda henüz bir kimliği yok.

Programı **bir kez daha** çalıştır:

```text
Before saving: None
After saving:  75
42 API Yolculuğu
57 Veriyle İlk Adımlar
73 Python ile Web API
74 Deneme Kitabı
75 Deneme Kitabı
```

İlk çalıştırmada eklenen 74 numaralı kitap hâlâ listede. Program bitti, ama kayıt veritabanında kaldı. Hafta 2'deki sunucuda böyle olmuyordu: Liste programın belleğindeydi ve program kapanınca kayboluyordu.

### 2.2 `commit` yazılmazsa

`try_db.py` dosyasından şu iki satırı sil:

```python
    session.commit()
    session.refresh(book)
```

Önce veritabanını sıfırla, sonra programı çalıştır:

```bash
python reset_db.py
python try_db.py
```

```text
Database reset: 3 books
Before saving: None
After saving:  None
42 API Yolculuğu
57 Veriyle İlk Adımlar
73 Python ile Web API
```

Kitap kaydedilmedi. `session.add` kitabı yalnızca oturuma ekledi; `commit` olmadan oturum kapanınca bu ekleme geri alındı. Veritabanına yazmak istediğimiz her değişiklikten sonra `commit` gerekir.

Silinen iki satırı geri koy ve veritabanını sıfırla:

```bash
python reset_db.py
```

`try_db.py` yalnızca bu deney içindi; istersen dosyayı silebilirsin.

> **Ana fikir:** Veritabanıyla her iş bir oturumda yapılır: `session.add` kaydı oturuma ekler, `session.commit` veritabanına yazar, `select` ile hazırlanan komut da kayıtları okur. Yeni kaydın kimliğini veritabanı verir. Veritabanına yazılan kayıt, onu yazan program kapandıktan sonra da durur.

---

## Deney 3 — Okuma işlemlerini veritabanına taşımak

**Amaç:** Kitap listesini ve tek kitabı `books` listesinden değil, veritabanından okumak.

İşlemleri sırayla taşıyoruz. Bu deneyde yalnızca iki okuma işlemini değiştiriyoruz; `books` listesi şimdilik duruyor, çünkü ekleme, değiştirme ve silme işlemleri hâlâ onu kullanıyor.

### 3.1 `get_books` ve `get_book`

`server.py` dosyasının başındaki import satırlarına iki satır ekle. Satırlar şöyle olmalı:

```python
from fastapi import FastAPI, HTTPException, Path, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import Session, select

from database import Book, engine
```

`get_books` ve `get_book` fonksiyonlarını şöyle değiştir:

```python
# Kitap listesi: ada ve ödünç durumuna göre süzülebilir.
@app.get("/books", response_model=list[BookPublic])
def get_books(search: str = "", available: bool | None = None):
    with Session(engine) as session:
        statement = select(Book).where(Book.title.icontains(search, autoescape=True))
        if available is not None:
            statement = statement.where(Book.available == available)
        statement = statement.order_by(Book.id)

        return session.exec(statement).all()


# Tek kitap: kimliğe göre bulur, yoksa 404.
@app.get("/books/{book_id}", response_model=BookPublic)
def get_book(book_id: int = Path(gt=0)):
    with Session(engine) as session:
        book = session.get(Book, book_id)

        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")

        return book
```

| Kod | Ne yapar? |
|---|---|
| `with Session(engine) as session:` | Her istek kendi oturumunu açar; fonksiyon bitince oturum kapanır. |
| `.where(Book.title.icontains(search, autoescape=True))` | Komuta bir koşul ekler: "Adında `search` metni geçen kitaplar." `Book.title` burada bir kitabın adı değil, `title` sütununun kendisi: Veritabanı koşulu her kayıt için bu sütuna bakarak dener. `icontains`, büyük ve küçük harfi ayırmaz; Hafta 1'deki `casefold()` karşılaştırmasının yerini alıyor. `search` boşsa her ad boş metni içerir, yani bütün kitaplar gelir. |
| `autoescape=True` | Aranan metindeki `%` ve `_` işaretlerini de sıradan harf gibi arar. SQL'de bu iki işaretin özel bir anlamı var; bu ayar olmasaydı `?search=_` bütün kitapları getirirdi. Ayrıntısı [ek notta](06_Supplement_Search_Differences.md). |
| `statement = statement.where(Book.available == available)` | `available` gönderildiyse ikinci bir koşul ekler. `Book.available == available` burada `True` ya da `False` vermez, veritabanına gidecek bir koşul hazırlar. İki `where` birlikte "ikisi birden" demektir. |
| `statement = statement.order_by(Book.id)` | Kitapları kimliğe göre sıralar. Neden gerektiğini 3.3'te göreceğiz. |
| `return session.exec(statement).all()` | `Book` nesnelerinden oluşan bir liste döndürür. `response_model` yine `BookPublic`; yanıt bu modele göre hazırlanır ve `internal_note` istemciye gitmez. |
| `session.get(Book, book_id)` | Birincil anahtarı `book_id` olan kaydı getirir; böyle bir kayıt yoksa `None` verir. Listede tek tek arayan `for` döngüsünün yerini alıyor. |

Döngülerin yerine artık SQL komutları var: Kitapları aramak ve süzmek veritabanının işi.

> **Dikkat:** Bu deneyin sonunda sunucu yarı yarıya taşınmış durumda. `POST /books` ile bir kitap eklersen kitap `books` listesine eklenir, ama `GET /books` onu göstermez; çünkü okuma artık veritabanından yapılıyor. Deney 4'te yazma işlemlerini de taşıyınca bu düzelecek.

### 3.2 İstemciyle dene

`client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"


# Kitap listesini ister, her kitabın kimliğini ve adını yazar.
def show_books(label, params):
    response = httpx.get(base_url + "/books", params=params)
    titles = []
    for book in response.json():
        titles.append(f"{book['id']} {book['title']}")
    print(label, response.status_code, titles)


try:
    show_books("All books:    ", {})
    show_books("Search 'api': ", {"search": "api"})
    show_books("Not available:", {"available": False})

    response = httpx.get(base_url + "/books/42")
    print("Book 42:      ", response.status_code, response.json())

    response = httpx.get(base_url + "/books/43")
    print("Book 43:      ", response.status_code, response.json())
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Veritabanını sıfırla, sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
All books:     200 ['42 API Yolculuğu', '57 Veriyle İlk Adımlar', '73 Python ile Web API']
Search 'api':  200 ['42 API Yolculuğu', '73 Python ile Web API']
Not available: 200 ['57 Veriyle İlk Adımlar']
Book 42:       200 {'title': 'API Yolculuğu', 'author': {'first_name': 'Deniz', 'last_name': 'Kaya'}, 'available': True, 'tags': ['software', 'education'], 'rating': None, 'id': 42}
Book 43:       404 {'detail': 'Book not found'}
```

Bu çıktı, aynı istemciyi Hafta 5'in sonundaki sunucuyla çalıştırınca alınan çıktıyla tıpatıp aynı. Tablonun her satırı, çıktının aynı sıradaki satırını açıklıyor:

| Çıktıdaki satır | İstek | Sunucu ne yaptı? |
|---|---|---|
| `All books` | `GET /books` | `search` boş; bütün kitaplar kimlik sırasıyla geldi. |
| `Search 'api'` | `GET /books?search=api` | Adında büyük ya da küçük harfle `api` geçen iki kitap |
| `Not available` | `GET /books?available=false` | Ödünç verilmiş tek kitap |
| `Book 42` | `GET /books/42` | Kitap veritabanından geldi; `internal_note` tabloda var, ama yanıtta yok. `BookPublic` onu yine süzdü. |
| `Book 43` | `GET /books/43` | `session.get` `None` verdi; fonksiyon `404` döndürdü. |

Bazı aramalarda veritabanının sonucu Python'unkinden ayrışabiliyor: Türkçe harfler içeren aramalarda ve `%`, `_` işaretlerinde. İkisini de [ek notta](06_Supplement_Search_Differences.md) görebilirsin.

### 3.3 Veri gerçekten veritabanından mı geliyor?

Sunucu çalışırken kaydı sunucunun dışından, psql ile değiştirelim. Önce `client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"

try:
    response = httpx.get(base_url + "/books/57")
    print("Book 57:", response.status_code, "rating:", response.json()["rating"])
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Sunucuyu yeniden başlatmadan şu üç adımı sırayla yap:

1. İstemciyi çalıştır.
2. psql ile 57 numaralı kitabın puanını değiştir:

   ```bash
   docker exec book-db psql -U student -d catalog -c "UPDATE book SET rating = 3 WHERE id = 57;"
   ```

3. İstemciyi tekrar çalıştır.

```text
Book 57: 200 rating: 0.0
UPDATE 1
Book 57: 200 rating: 3.0
```

| Çıktıdaki satır | Ne oldu? |
|---|---|
| `Book 57: 200 rating: 0.0` | Kitap, `reset_db.py` dosyasının yazdığı puanla geldi. |
| `UPDATE 1` | psql'in cevabı: `UPDATE` komutu bir kaydı değiştirdi. |
| `Book 57: 200 rating: 3.0` | Sunucuya dokunmadık, ama yanıt değişti. Sunucu her istekte veritabanına soruyor. |

Bir şey daha değişti. Kitapları psql ile sıralamadan listeleyelim:

```bash
docker exec book-db psql -U student -d catalog -c "SELECT id, title, rating FROM book;"
```

```text
 id |        title        | rating
----+---------------------+--------
 42 | API Yolculuğu       |
 73 | Python ile Web API  |    4.5
 57 | Veriyle İlk Adımlar |      3
(3 rows)
```

57 numaralı kitap sona geçti. `SELECT` komutunda sıralama istemezsek veritabanı kayıtları kendi uygun bulduğu sırayla verir; değiştirilen kayıt bu örnekte sona geçti. `get_books` fonksiyonundaki `order_by` satırı bu yüzden var: O satırı silip sunucuyu yeniden başlatır ve istemciyi 3.2'deki hâliyle çalıştırırsan kitap listesinde de 57 sona geçer; denediysen satırı geri koy. Listedeki bir `for` döngüsü kitapları hep aynı sırayla verirdi; veritabanında sıra istiyorsak bunu söylememiz gerekir.

Veritabanını sıfırla:

```bash
python reset_db.py
```

> **Ana fikir:** Okuma işlemleri artık her istekte veritabanına bir SQL komutu gönderiyor: `session.get` kimliğe göre tek kaydı, `select` ve `where` koşula uyan kayıtları getiriyor. Veritabanı sıra garantisi vermez; sıra gerekiyorsa `order_by` yazılır. Yanıtı yine `response_model` hazırladığı için istemci farkı görmüyor.

---

## Deney 4 — Yazma işlemlerini taşımak

**Amaç:** Kitap ekleme, değiştirme ve silme işlemlerini veritabanına taşımak, `books` listesini kaldırmak ve sunucu yeniden başlayınca değişikliklerin durduğunu görmek.

### 4.1 Dört fonksiyonu değiştir

`server.py` dosyasında `books = [...]` listesinin tamamını sil. Kitaplar artık yalnızca veritabanında.

`create_book`, `delete_book`, `replace_book` ve `update_book` fonksiyonlarını şöyle değiştir:

```python
# Yeni kitap: veritabanına ekler, 201 ve Location döner.
@app.post("/books", status_code=201, response_model=BookPublic)
def create_book(book_data: BookCreate, response: Response):
    with Session(engine) as session:
        book = Book.model_validate(book_data.model_dump())
        session.add(book)
        session.commit()
        session.refresh(book)

        response.headers["Location"] = f"/books/{book.id}"
        return book


# Kitabı silme: veritabanından siler, 204 döner; kitap yoksa 404.
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int = Path(gt=0)):
    with Session(engine) as session:
        book = session.get(Book, book_id)

        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")

        session.delete(book)
        session.commit()


# Kitabı tümüyle değiştirme: bütün alanlar yenisiyle değişir; kitap yoksa 404.
@app.put("/books/{book_id}", response_model=BookPublic)
def replace_book(book_data: BookCreate, book_id: int = Path(gt=0)):
    with Session(engine) as session:
        book = session.get(Book, book_id)

        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")

        book.sqlmodel_update(book_data.model_dump())
        session.commit()
        session.refresh(book)
        return book


# Kitabın bir kısmını değiştirme: yalnızca gönderilen alanlar değişir; kitap yoksa 404.
@app.patch("/books/{book_id}", response_model=BookPublic)
def update_book(book_data: BookUpdate, book_id: int = Path(gt=0)):
    with Session(engine) as session:
        book = session.get(Book, book_id)

        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")

        changes = book_data.model_dump(exclude_unset=True)
        book.sqlmodel_update(changes)
        session.commit()
        session.refresh(book)
        return book
```

| Kod | Ne yapar? |
|---|---|
| `Book.model_validate(book_data.model_dump())` | `BookCreate` modelinden gelen sözlükten bir `Book` nesnesi oluşturur. İstemcinin gönderdiği değerler bu satıra gelmeden önce `BookCreate` ile kontrol edildi. |
| `session.add(book)` ve `session.commit()` | Kitabı veritabanına yazar. Hafta 2'den beri kullandığımız "en büyük kimlik + 1" döngüsü yok: Kimliği veritabanının sayacı veriyor. |
| `session.refresh(book)` | Kitabı veritabanından yeniden okur; veritabanının verdiği kimlik nesneye gelir. `Location` başlığı bu kimlikle yazılıyor. |
| `session.delete(book)` | Kitabı silinecek olarak işaretler; `commit` ile silinir. |
| `book.sqlmodel_update(changes)` | Sözlükteki her alanı kitaba yazar. Hafta 4'te sözlük olan kitabı `book.update(changes)` ile değiştiriyorduk; kitap artık bir `Book` nesnesi ve aynı işi `sqlmodel_update` yapıyor. |
| `replace_book` içindeki `book_data.model_dump()` | `PUT` isteğinde bütün alanlar gönderildiği için hepsi yazılır. |
| `update_book` içindeki `exclude_unset=True` | `PATCH` isteğinde yalnızca gönderilen alanlar yazılır (Hafta 4). |
| `replace_book` ve `update_book` içindeki `session.refresh(book)` | Değişikliği veritabanına yazdıktan sonra kitabı yeniden okur. `commit` sonrasında oturum nesnedeki değerleri unutur; FastAPI ise yanıtı fonksiyon bittikten, oturum kapandıktan sonra hazırlar. Değerleri oturum kapanmadan yeniden okumazsak yanıt hazırlanamaz. Bu satır unutulunca ne olduğunu [ek notta](07_Supplement_Refresh.md) görebilirsin. |

Yorum fonksiyonları, kitabın var olup olmadığını hâlâ silinen `books` listesinde arıyor. `get_reviews` ve `create_review` fonksiyonlarının ikisinde de şu satırları:

```python
    book_exists = False
    for book in books:
        if book["id"] == book_id:
            book_exists = True

    if not book_exists:
        raise HTTPException(status_code=404, detail="Book not found")
```

şu satırlarla değiştir:

```python
    with Session(engine) as session:
        if session.get(Book, book_id) is None:
            raise HTTPException(status_code=404, detail="Book not found")
```

Yorumların kendisi şimdilik `reviews` listesinde kalıyor; onları Deney 5'te taşıyacağız.

### 4.2 Yazma isteklerini gönder

`client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"

new_book = {
    "title": "Veritabanı Defteri",
    "author": {
        "first_name": "Ada",
        "last_name": "Yıldız"
    },
    "available": True,
    "tags": ["database"],
    "rating": None
}

try:
    # Yeni kitap: kimliğini artık veritabanı veriyor.
    response = httpx.post(base_url + "/books", json=new_book)
    print("Create:   ", response.status_code, response.headers["Location"])

    # 57 numaralı kitabın puanını değiştir.
    response = httpx.patch(base_url + "/books/57", json={"rating": 3})
    print("Patch 57: ", response.status_code, "rating:", response.json()["rating"])

    # 73 numaralı kitabı sil.
    response = httpx.delete(base_url + "/books/73")
    print("Delete 73:", response.status_code)
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Veritabanını sıfırla, sunucuyu yeniden başlat ve istemciyi **bir kez** çalıştır:

```text
Create:    201 /books/74
Patch 57:  200 rating: 3.0
Delete 73: 204
```

| Çıktıdaki satır | İstek | Sonuç |
|---|---|---|
| `Create` | `POST /books` | Kitap eklendi; veritabanının sayacı `74` kimliğini verdi. |
| `Patch 57` | `PATCH /books/57`, `{"rating": 3}` | Puan `3.0` oldu. |
| `Delete 73` | `DELETE /books/73` | Kitap silindi. |

Yanıtlar Hafta 5'teki sunucuyla aynı. Asıl fark bir sonraki adımda.

### 4.3 Sunucuyu yeniden başlat

Sunucuyu durdur (`Ctrl+C`) ve yeniden başlat. Veritabanını sıfırlama. Ardından `client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"

try:
    response = httpx.get(base_url + "/books")
    print("Status:", response.status_code)

    for book in response.json():
        print(book["id"], book["title"], "- rating:", book["rating"])
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

İstemciyi çalıştır:

```text
Status: 200
42 API Yolculuğu - rating: None
57 Veriyle İlk Adımlar - rating: 3.0
74 Veritabanı Defteri - rating: None
```

Üç değişiklik de duruyor: 74 numaralı kitap listede, 57'nin puanı `3.0`, 73 numaralı kitap yok. Sunucu kapandı ve yeniden başladı, ama kitaplar sunucunun belleğinde değil, veritabanında.

Aynı iki istemciyi Hafta 5'in sonundaki sunucuyla, arada sunucuyu yeniden başlatarak çalıştırsaydık şunu görürdük:

```text
Status: 200
42 API Yolculuğu - rating: None
57 Veriyle İlk Adımlar - rating: 0.0
73 Python ile Web API - rating: 4.5
```

Hafta 2'nin Deney 6'sındaki gibi: Sunucu yeniden başlayınca liste `server.py` dosyasındaki hâline dönerdi.

### 4.4 Başlangıç hâline dönmek

Kayıtlar artık kalıcı. Föydeki başlangıç hâline dönmek için veritabanını sıfırla ve aynı istemciyi tekrar çalıştır:

```bash
python reset_db.py
```

```text
Status: 200
42 API Yolculuğu - rating: None
57 Veriyle İlk Adımlar - rating: 0.0
73 Python ile Web API - rating: 4.5
```

Önceki haftalarda başlangıç hâline sunucuyu yeniden başlatarak dönüyorduk. Artık bunu ayrı bir program yapıyor ve bilerek çalıştırmamız gerekiyor. Sunucuyu yeniden başlatmak gerekmedi: Sunucu her istekte veritabanına sorduğu için sıfırlanmış kayıtları hemen gördü.

Hafta 5'in istemcilerini de bu sunucuyla çalıştırabilirsin: Her birinden önce veritabanını sıfırlarsan Hafta 5 föyündeki çıktıların aynısını alırsın.

> **Ana fikir:** Yazma işlemleri de artık veritabanında: `session.add`, `sqlmodel_update` ve `session.delete` değişikliği oturumda hazırlar, `session.commit` veritabanına yazar. Kayıtlar sunucu yeniden başlayınca kaybolmaz; başlangıç hâline dönmek için veritabanını bilerek sıfırlamak gerekir.

---

## Deney 5 — Yorumlar: iki tablo arasındaki ilişki

**Amaç:** Yorumları ikinci bir tabloya taşımak, her yorumu bir kitaba bağlamak ve bir kitap silinince yorumlarının da silinmesini veritabanına bırakmak.

Hafta 4'teki [ek notta](../Week_04/04_Supplement_Deleted_Book_Reviews.md) üç seçenek tartışmıştık; kitap kataloğu için en uygunu, kitap silinince yorumlarının da silinmesiydi. O notun sonunda bu kuralı veritabanının kendisine tanımlayabileceğimizi söylemiştik. Şimdi bunu yapıyoruz.

### 5.1 Yorum tablosu

`database.py` dosyasının sonuna şu sınıfı ekle:

```python
# Yorum tablosu: her yorum bir kitaba bağlı; kitap silinince yorumları da silinir.
class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id", ondelete="CASCADE")
    reader: str
    comment: str
    score: int
```

| Kod | Ne yapar? |
|---|---|
| `foreign_key="book.id"` | `book_id` sütununu bir **yabancı anahtar (foreign key)** yapar: Bu sütundaki her değer, `book` tablosunun `id` sütununda bulunmalıdır. Veritabanı, var olmayan bir kitaba bağlı yorum yazılmasına izin vermez. |
| `ondelete="CASCADE"` | Bir kitap silinince, ona bağlı yorumları da siler. *Cascade*, İngilizcede "zincirleme" demek: Silme işlemi kitaptan yorumlarına geçer. |

`reset_db.py` dosyasında şu değişiklikleri yap:

| Eski satır | Yeni satır |
|---|---|
| `from database import Book, engine` | `from database import Book, Review, engine` |
| `# Kimlik sayacını en büyük kimliğe getir: yeni kitabın kimliği 74 olsun.` | `# Kimlik sayaçlarını en büyük kimliğe getir: yeni kitabın kimliği 74, yeni yorumunki 2 olsun.` |
| `print("Database reset: 3 books")` | `print("Database reset: 3 books, 1 review")` |

73 numaralı kitabı ekleyen `session.add(...)` bloğundan sonra, ilk `session.commit()` satırından önce Ece'nin yorumunu ekle:

```python
    session.add(Review(
        id=1,
        book_id=42,
        reader="Ece",
        comment="Konuları örneklerle anlatıyor.",
        score=5,
    ))
```

Kitap sayacını ayarlayan `session.execute(...)` satırının altına yorum sayacı için aynı satırı ekle:

```python
    session.execute(text("SELECT setval(pg_get_serial_sequence('review', 'id'), (SELECT MAX(id) FROM review))"))
```

Veritabanını sıfırla:

```bash
python reset_db.py
```

```text
Database reset: 3 books, 1 review
```

`drop_all` ve `create_all` artık iki tabloyu birlikte siliyor ve oluşturuyor. Yorum tablosunun yapısına bakalım:

```bash
docker exec book-db psql -U student -d catalog -c "\d review"
```

```text
                                  Table "public.review"
 Column  |       Type        | Collation | Nullable |              Default
---------+-------------------+-----------+----------+------------------------------------
 id      | integer           |           | not null | nextval('review_id_seq'::regclass)
 book_id | integer           |           | not null |
 reader  | character varying |           | not null |
 comment | character varying |           | not null |
 score   | integer           |           | not null |
Indexes:
    "review_pkey" PRIMARY KEY, btree (id)
Foreign-key constraints:
    "review_book_id_fkey" FOREIGN KEY (book_id) REFERENCES book(id) ON DELETE CASCADE
```

Son satır, `Review` sınıfında yazdığımız kuralın veritabanındaki hâli: `book_id` sütunu `book` tablosunun `id` sütununa bağlı ve kitap silinince yorum da silinir.

### 5.2 Yorum işlemlerini taşı

`server.py` dosyasında şu değişiklikleri yap:

| Eski satır | Yeni satır |
|---|---|
| `from database import Book, engine` | `from database import Book, Review, engine` |

`reviews = [...]` listesinin tamamını sil. `ReviewCreate` modelinin altına bir yanıt modeli ekle:

```python
class ReviewPublic(ReviewCreate):
    model_config = ConfigDict(strict=False, extra="ignore")

    id: int
    book_id: int
```

Hafta 5'teki kural burada da geçerli: `ReviewPublic`, `ReviewCreate` modelinden türediği için onun sıkı modunu ve fazla alanları reddetme ayarını da alır. Yanıt modelinde ikisine de gerek yok.

`get_reviews` ve `create_review` fonksiyonlarını şöyle değiştir:

```python
# Kitabın yorumları: kitap yoksa 404.
@app.get("/books/{book_id}/reviews", response_model=list[ReviewPublic])
def get_reviews(book_id: int = Path(gt=0)):
    with Session(engine) as session:
        if session.get(Book, book_id) is None:
            raise HTTPException(status_code=404, detail="Book not found")

        statement = select(Review).where(Review.book_id == book_id).order_by(Review.id)
        return session.exec(statement).all()


# Yeni yorum: kitaba ekler, 201 döner; kitap yoksa 404, okurun bu kitaba yorumu varsa 409.
@app.post("/books/{book_id}/reviews", status_code=201, response_model=ReviewPublic)
def create_review(review_data: ReviewCreate, book_id: int = Path(gt=0)):
    with Session(engine) as session:
        if session.get(Book, book_id) is None:
            raise HTTPException(status_code=404, detail="Book not found")

        statement = select(Review).where(Review.book_id == book_id).where(Review.reader == review_data.reader)
        if session.exec(statement).first() is not None:
            raise HTTPException(status_code=409, detail="This reader has already reviewed this book")

        new_review = review_data.model_dump()
        new_review["book_id"] = book_id
        review = Review.model_validate(new_review)
        session.add(review)
        session.commit()
        session.refresh(review)
        return review
```

| Kod | Ne yapar? |
|---|---|
| `response_model=list[ReviewPublic]` ve `response_model=ReviewPublic` | Yorum yanıtları artık bir modelle hazırlanıyor. Böylece her yorumun alanları aynı sırayla gelir. Hafta 5'teki sunucuda başlangıçtaki yorumla sonradan eklenen yorumun alanları farklı sırayla geliyordu. |
| `.where(Review.book_id == book_id)` | Yalnızca bu kitaba ait yorumlar. Hafta 5'teki `for` döngüsünün ve `if` koşulunun yerini alıyor. |
| `.where(...).where(Review.reader == review_data.reader)` | İki koşul: Bu kitaba ait **ve** okuru aynı olan yorumlar. |
| `session.exec(statement).first()` | Komutun ilk sonucunu verir; sonuç yoksa `None` verir. Okurun bu kitaba yorumu varsa `None` gelmez ve `409` döner. |
| `new_review["book_id"] = book_id` | Hafta 5'teki `created_review["book_id"] = book_id` satırı gibi: Yorumun hangi kitaba ait olduğunu yoldan alır. Kimliği ise artık veritabanı veriyor. |

Fonksiyonun başındaki `404` kontrolünü kaldırma: Kontrol olmasaydı veritabanı, olmayan bir kitaba bağlı yorumu yine reddederdi. Ama istemci anlamlı bir `404` yerine `500 Internal Server Error` alırdı.

### 5.3 İstemciyle dene

`client.py` dosyasının içeriğini şununla değiştir:

```python
import httpx

base_url = "http://127.0.0.1:8000"

review = {"reader": "Can", "comment": "Örnekleri çalıştırdım.", "score": 4}

try:
    response = httpx.post(base_url + "/books/42/reviews", json=review)
    print("Can's review: ", response.status_code, response.json())

    response = httpx.post(base_url + "/books/42/reviews", json=review)
    print("Can again:    ", response.status_code, response.json())

    response = httpx.get(base_url + "/books/42/reviews")
    print("Reviews of 42:", response.status_code, response.json())

    # Kitabı sil: yorumlarına ne olacak?
    response = httpx.delete(base_url + "/books/42")
    print("Delete 42:    ", response.status_code)

    response = httpx.get(base_url + "/books/42/reviews")
    print("Reviews of 42:", response.status_code, response.json())
except httpx.ConnectError:
    print("Connection failed: Check that the server is running.")
```

Veritabanını sıfırla, sunucuyu yeniden başlat ve istemciyi çalıştır:

```text
Can's review:  201 {'reader': 'Can', 'comment': 'Örnekleri çalıştırdım.', 'score': 4, 'id': 2, 'book_id': 42}
Can again:     409 {'detail': 'This reader has already reviewed this book'}
Reviews of 42: 200 [{'reader': 'Ece', 'comment': 'Konuları örneklerle anlatıyor.', 'score': 5, 'id': 1, 'book_id': 42}, {'reader': 'Can', 'comment': 'Örnekleri çalıştırdım.', 'score': 4, 'id': 2, 'book_id': 42}]
Delete 42:     204
Reviews of 42: 404 {'detail': 'Book not found'}
```

| Çıktıdaki satır | İstek | Sonuç |
|---|---|---|
| `Can's review` | `POST /books/42/reviews` | Yorum eklendi; yorum sayacı `2` kimliğini verdi. |
| `Can again` | Aynı yorum tekrar | `409`: Fonksiyondaki `select` komutu Can'in yorumunu buldu. |
| `Reviews of 42` | `GET /books/42/reviews` | Ece'nin ve Can'in yorumları, kimlik sırasıyla. İki yorumun alanları aynı sırada. |
| `Delete 42` | `DELETE /books/42` | Kitap silindi. |
| `Reviews of 42` | `GET /books/42/reviews` | `404`: Kitap yok. Yorumlara ne olduğunu bu yanıt söylemiyor. |

### 5.4 Yorumlara ne oldu?

Son yanıt yalnızca kitabın olmadığını söylüyor. Yorum tablosuna psql ile bakalım:

```bash
docker exec book-db psql -U student -d catalog -c "SELECT id, book_id, reader FROM review;"
```

```text
 id | book_id | reader
----+---------+--------
(0 rows)
```

İki yorum da silinmiş. `delete_book` fonksiyonumuz yalnızca kitabı siliyor; yorumlara hiç dokunmuyor. Yorumları, `ondelete="CASCADE"` kuralıyla veritabanı kendisi sildi. Hafta 4'teki ek notta gördüğümüz sorun, yani kitabı silinmiş ama hâlâ okunabilen yorum, artık oluşamaz.

Veritabanı ters yöndeki hatayı da engelliyor. Olmayan bir kitaba psql ile yorum eklemeyi dene:

```bash
docker exec book-db psql -U student -d catalog -c "INSERT INTO review (book_id, reader, comment, score) VALUES (999, 'Ali', 'Güzel.', 4);"
```

```text
ERROR:  insert or update on table "review" violates foreign key constraint "review_book_id_fkey"
DETAIL:  Key (book_id)=(999) is not present in table "book".
```

Yabancı anahtar kuralı ihlal edildi: `book` tablosunda kimliği `999` olan bir kayıt yok.

Hafta 5'te "Bir kuralı nereye yazmalıyım?" diye sormuştuk. Artık üçüncü bir yer var:

| Kural | Nereye yazdık? | Kim kontrol ediyor? | İhlal edilirse |
|---|---|---|---|
| Kitabın adı boş olamaz, puan 0 ile 5 arasında | İstek modeline: `BookCreate`, `BookUpdate` | FastAPI (Pydantic ile), fonksiyondan önce | `422` |
| Kitap yoksa yorum eklenemez, aynı okur ikinci yorumu yazamaz | Fonksiyonun içine | Bizim fonksiyonumuz | `404`, `409` |
| İki kaydın kimliği aynı olamaz, her yorumun kitabı olmalı, kitap silinince yorumları silinir | Tablo modeline: `primary_key`, `foreign_key`, `ondelete` | Veritabanı, her yazma işleminde | Kayıt yazılmaz; sunucuda yakalanmazsa `500` |

Veritabanındaki kurallar son güvencedir: psql gibi sunucumuzu kullanmayan bir program bile onları aşamaz. Ama istemciye anlamlı bir yanıt vermek için aynı durumu fonksiyonda da kontrol ediyoruz.

Veritabanını sıfırla:

```bash
python reset_db.py
```

> **Ana fikir:** Yabancı anahtar, bir tablodaki kaydı başka bir tablodaki kayda bağlar. Veritabanı bu bağı her yazma işleminde korur: Olmayan bir kitaba yorum yazdırmaz ve `ondelete="CASCADE"` ile kitap silinince yorumlarını da siler. Bu kuralı bir kez tabloya yazdık; her silmede kodumuzun hatırlaması gerekmiyor.

---

## Deney 6 — SQLModel'in yazdığı SQL komutlarını görmek

**Amaç:** Her HTTP isteğinin veritabanına hangi SQL komutlarını gönderdiğini görmek.

Bu deney ödev: Derste zaman kalmazsa evde yap.

Python kodumuzda yalnızca `reset_db.py` dosyasında bir SQL komutu yazdık. Geri kalan her şeyi SQLModel bizim yerimize SQL'e çeviriyor. `database.py` dosyasında motoru oluşturan satırı şöyle değiştir:

| Eski satır | Yeni satır |
|---|---|
| `engine = create_engine(DATABASE_URL)` | `engine = create_engine(DATABASE_URL, echo=True)` |

`echo=True`, motorun veritabanına gönderdiği her komutu terminale yazmasını sağlar.

Veritabanını sıfırla, sunucuyu yeniden başlat ve Deney 4.2'deki istemciyi çalıştır. İstemcinin çıktısı aynı:

```text
Create:    201 /books/74
Patch 57:  200 rating: 3.0
Delete 73: 204
```

Sunucunun terminalinde ise her isteğin komutları görünür. Aşağıda satırların başındaki tarih ve saat kısaltıldı, yalnızca `POST` isteğinin komutları alındı. Köşeli parantezdeki süreler senin terminalinde farklı olacak:

```text
BEGIN (implicit)
INSERT INTO book (title, author, available, tags, rating, internal_note) VALUES (%(title)s::VARCHAR, %(author)s::JSONB, %(available)s, %(tags)s::JSONB, %(rating)s, %(internal_note)s::VARCHAR) RETURNING book.id
[generated in 0.00017s] {'title': 'Veritabanı Defteri', 'author': Jsonb({'first_name': 'Ada', 'last_name':  ... (44 chars)), 'available': True, 'tags': Jsonb(['database']), 'rating': None, 'internal_note': None}
COMMIT
BEGIN (implicit)
SELECT book.id, book.title, book.author, book.available, book.tags, book.rating, book.internal_note
FROM book
WHERE book.id = %(pk_1)s::INTEGER
[generated in 0.00010s] {'pk_1': 74}
ROLLBACK
```

| Satır | Python'daki karşılığı |
|---|---|
| `BEGIN (implicit)` | Oturum veritabanıyla bir iş başlattı. |
| `INSERT INTO book (...) VALUES (...) RETURNING book.id` | `session.add(book)` ve `session.commit()`: Kaydı ekle ve veritabanının verdiği kimliği geri gönder. |
| `{'title': 'Veritabanı Defteri', ...}` | Komuttaki `%(title)s` gibi yerlerin değerleri. Değerler komutun içine yazılmıyor, ayrı gönderiliyor. |
| `COMMIT` | `session.commit()` |
| `SELECT ... FROM book WHERE book.id = ...` | `session.refresh(book)`: Kaydı yeniden oku. |
| `ROLLBACK` | Oturum kapandı. Okumadan sonra kaydedilecek bir değişiklik yoktu; açık iş geri alınarak kapatıldı. Veritabanında bir şey değişmedi. |

Terminalde `PATCH` ve `DELETE` isteklerinin komutlarını kendin bul ve şu tabloyu tamamla:

| İstemcideki satır | HTTP isteği | Değişikliği yapan SQL komutu |
|---|---|---|
| `Create` | `POST /books` | `INSERT INTO book ...` |
| `Patch 57` | `PATCH /books/57` | ? |
| `Delete 73` | `DELETE /books/73` | ? |

İpucu: `PATCH` isteğinin komutunda yalnızca bir sütun değişiyor. Hangisi, neden?

Bitirince `echo=True` ayarını kaldır; föyün geri kalanında terminal bu komutlarla dolmasın. Cevaplar 9.1'in sonunda.

> **Ana fikir:** SQLModel, oturumda yaptığımız her işi SQL komutlarına çevirir: ekleme `INSERT`, okuma `SELECT`, değiştirme `UPDATE`, silme `DELETE` olur. HTTP metotlarıyla SQL komutları arasında böyle bir eşleşme vardır, ama bire bir değildir: Tek bir `PATCH` isteği önce bir `SELECT`, sonra bir `UPDATE` gönderir.

---

## 7. Bu haftanın sonundaki dosyalar

Deney 5'ten sonra üç dosya şöyle olmalı (Deney 6'daki `echo=True` ayarını kaldırdıysan). Hafta 7'ye bu dosyalarla başlayacağız.

### 7.1 `database.py`

```python
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, create_engine

DATABASE_URL = "postgresql+psycopg://student:secret@localhost:5432/catalog"

engine = create_engine(DATABASE_URL)


# Kitap tablosu: her Book nesnesi tabloda bir kayıttır.
class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author: dict = Field(sa_column=Column(JSONB, nullable=False))
    available: bool
    tags: list[str] = Field(sa_column=Column(JSONB, nullable=False))
    rating: float | None = None
    internal_note: str | None = None


# Yorum tablosu: her yorum bir kitaba bağlı; kitap silinince yorumları da silinir.
class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id", ondelete="CASCADE")
    reader: str
    comment: str
    score: int
```

### 7.2 `reset_db.py`

```python
from sqlalchemy import text
from sqlmodel import Session, SQLModel

from database import Book, Review, engine

# Tabloları sil ve modellere göre yeniden oluştur.
SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    session.add(Book(
        id=42,
        title="API Yolculuğu",
        author={"first_name": "Deniz", "last_name": "Kaya"},
        available=True,
        tags=["software", "education"],
        rating=None,
        internal_note="Kapağı yıpranmış, yenisi sipariş edildi.",
    ))
    session.add(Book(
        id=57,
        title="Veriyle İlk Adımlar",
        author={"first_name": "Ece", "last_name": "Yılmaz"},
        available=False,
        tags=[],
        rating=0,
    ))
    session.add(Book(
        id=73,
        title="Python ile Web API",
        author={"first_name": "Can", "last_name": "Demir"},
        available=True,
        tags=["python", "api"],
        rating=4.5,
    ))
    session.add(Review(
        id=1,
        book_id=42,
        reader="Ece",
        comment="Konuları örneklerle anlatıyor.",
        score=5,
    ))
    session.commit()

    # Kimlik sayaçlarını en büyük kimliğe getir: yeni kitabın kimliği 74, yeni yorumunki 2 olsun.
    session.execute(text("SELECT setval(pg_get_serial_sequence('book', 'id'), (SELECT MAX(id) FROM book))"))
    session.execute(text("SELECT setval(pg_get_serial_sequence('review', 'id'), (SELECT MAX(id) FROM review))"))
    session.commit()

print("Database reset: 3 books, 1 review")
```

### 7.3 `server.py`

```python
from fastapi import FastAPI, HTTPException, Path, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import Session, select

from database import Book, Review, engine


class Author(BaseModel):
    first_name: str
    last_name: str


class BookCreate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    title: str = Field(min_length=1)
    author: Author
    available: bool
    tags: list[str]
    rating: float | None = Field(default=None, ge=0, le=5)


class BookPublic(BookCreate):
    model_config = ConfigDict(strict=False, extra="ignore")

    id: int


class BookUpdate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    title: str = Field(default=None, min_length=1)
    author: Author = None
    available: bool = None
    tags: list[str] = None
    rating: float | None = Field(default=None, ge=0, le=5)


class ReviewCreate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    reader: str = Field(min_length=1)
    comment: str = Field(min_length=1)
    score: int = Field(ge=1, le=5)


class ReviewPublic(ReviewCreate):
    model_config = ConfigDict(strict=False, extra="ignore")

    id: int
    book_id: int


app = FastAPI()


# Kitap listesi: ada ve ödünç durumuna göre süzülebilir.
@app.get("/books", response_model=list[BookPublic])
def get_books(search: str = "", available: bool | None = None):
    with Session(engine) as session:
        statement = select(Book).where(Book.title.icontains(search, autoescape=True))
        if available is not None:
            statement = statement.where(Book.available == available)
        statement = statement.order_by(Book.id)

        return session.exec(statement).all()


# Tek kitap: kimliğe göre bulur, yoksa 404.
@app.get("/books/{book_id}", response_model=BookPublic)
def get_book(book_id: int = Path(gt=0)):
    with Session(engine) as session:
        book = session.get(Book, book_id)

        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")

        return book


# Yeni kitap: veritabanına ekler, 201 ve Location döner.
@app.post("/books", status_code=201, response_model=BookPublic)
def create_book(book_data: BookCreate, response: Response):
    with Session(engine) as session:
        book = Book.model_validate(book_data.model_dump())
        session.add(book)
        session.commit()
        session.refresh(book)

        response.headers["Location"] = f"/books/{book.id}"
        return book


# Kitabı silme: veritabanından siler, 204 döner; kitap yoksa 404.
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int = Path(gt=0)):
    with Session(engine) as session:
        book = session.get(Book, book_id)

        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")

        session.delete(book)
        session.commit()


# Kitabı tümüyle değiştirme: bütün alanlar yenisiyle değişir; kitap yoksa 404.
@app.put("/books/{book_id}", response_model=BookPublic)
def replace_book(book_data: BookCreate, book_id: int = Path(gt=0)):
    with Session(engine) as session:
        book = session.get(Book, book_id)

        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")

        book.sqlmodel_update(book_data.model_dump())
        session.commit()
        session.refresh(book)
        return book


# Kitabın bir kısmını değiştirme: yalnızca gönderilen alanlar değişir; kitap yoksa 404.
@app.patch("/books/{book_id}", response_model=BookPublic)
def update_book(book_data: BookUpdate, book_id: int = Path(gt=0)):
    with Session(engine) as session:
        book = session.get(Book, book_id)

        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")

        changes = book_data.model_dump(exclude_unset=True)
        book.sqlmodel_update(changes)
        session.commit()
        session.refresh(book)
        return book


# Kitabın yorumları: kitap yoksa 404.
@app.get("/books/{book_id}/reviews", response_model=list[ReviewPublic])
def get_reviews(book_id: int = Path(gt=0)):
    with Session(engine) as session:
        if session.get(Book, book_id) is None:
            raise HTTPException(status_code=404, detail="Book not found")

        statement = select(Review).where(Review.book_id == book_id).order_by(Review.id)
        return session.exec(statement).all()


# Yeni yorum: kitaba ekler, 201 döner; kitap yoksa 404, okurun bu kitaba yorumu varsa 409.
@app.post("/books/{book_id}/reviews", status_code=201, response_model=ReviewPublic)
def create_review(review_data: ReviewCreate, book_id: int = Path(gt=0)):
    with Session(engine) as session:
        if session.get(Book, book_id) is None:
            raise HTTPException(status_code=404, detail="Book not found")

        statement = select(Review).where(Review.book_id == book_id).where(Review.reader == review_data.reader)
        if session.exec(statement).first() is not None:
            raise HTTPException(status_code=409, detail="This reader has already reviewed this book")

        new_review = review_data.model_dump()
        new_review["book_id"] = book_id
        review = Review.model_validate(new_review)
        session.add(review)
        session.commit()
        session.refresh(review)
        return review
```

Hafta 3'teki 8.3 ya da Hafta 4'teki 5.3 alıştırmalarını yaptıysan, `get_review` ve `delete_review` fonksiyonların hâlâ silinen `reviews` listesini kullanıyor; onları 8.2'de taşıyacaksın.

---

## 8. Ödev: belge ve kendi kodunu taşımak

Bu bölümü, Deney 6 ile birlikte evde tamamla.

### 8.1 `README.md` belgesine çalıştırma adımlarını eklemek

Projeni yeni bir bilgisayarda çalıştıracak biri artık yalnızca sunucuyu başlatamaz; önce veritabanını hazırlaması gerekir. Hafta 3'te yazdığın `README.md` belgesinin sonuna şu bölümü ekle:

````markdown
## Veritabanı

Kitaplar ve yorumlar PostgreSQL veritabanında saklanır. İlk kez çalıştırırken:

```bash
docker run --name book-db -e POSTGRES_USER=student -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=catalog -p 5432:5432 -d postgres:16
python reset_db.py
python -m uvicorn server:app
```

Sonraki seferlerde `docker start book-db` ile veritabanını, ardından sunucuyu başlat.

`python reset_db.py` veritabanını başlangıç hâline getirir: Bütün kitapları ve yorumları siler, üç kitabı ve bir yorumu yeniden yazar.
````

### 8.2 Kendin yaz: tek yorumu okumak ve silmek

Hafta 3'teki 8.3 alıştırmasında tek bir yorumu okuyan `get_review` fonksiyonunu, Hafta 4'teki 5.3 alıştırmasında da bir yorumu silen `delete_review` fonksiyonunu yazmıştık. İkisi de silinen `reviews` listesini kullanıyor. Yazmadıysan, iki fonksiyonu Hafta 3'teki [cevap notundan](../Week_03/09_Supplement_Exercise_8_3_Answer.md) ve Hafta 4'teki [cevap notundan](../Week_04/06_Supplement_Exercise_5_3_Answer.md) alabilirsin.

**İstenenler:**

1. `GET /books/{book_id}/reviews/{review_id}` yorumu veritabanından okusun; yorum yoksa ya da başka bir kitaba aitse `404` ve `{"detail": "Review not found"}` dönsün.
2. `DELETE /books/{book_id}/reviews/{review_id}` yorumu veritabanından silsin ve `204` dönsün; aynı durumlarda `404` dönsün.
3. `GET` yanıtı `ReviewPublic` modeliyle hazırlansın. İki fonksiyonun `book_id` ve `review_id` parametrelerine de `Path(gt=0)` ekle.

**İpucu:** Yorumu `session.get(Review, review_id)` ile bulabilirsin. Ama bu yalnızca kimliğe bakar; yorumun yoldaki kitaba ait olup olmadığını ayrıca kontrol etmen gerekir.

**Kontrol et:** Veritabanını sıfırla, sunucuyu yeniden başlat ve istekleri sırayla gönder. Sonuçlar şöyle olmalı:

| İstek | Durum kodu | Yanıt |
|---|---|---|
| `GET /books/42/reviews/1` | `200` | Ece'nin yorumu |
| `GET /books/57/reviews/1` | `404` | `{"detail": "Review not found"}`: 1 numaralı yorum 57'ye değil, 42'ye ait. |
| `DELETE /books/57/reviews/1` | `404` | `{"detail": "Review not found"}`: Yorum silinmedi. |
| `DELETE /books/42/reviews/1` | `204` | Boş |
| `GET /books/42/reviews/1` | `404` | `{"detail": "Review not found"}` |

Kodunu yazıp denedikten sonra [ek nottaki cevapla](08_Supplement_Exercise_8_2_Answer.md) karşılaştır.

### 8.3 Kendin yaz: sayfa sayısı

Kitaplara isteğe bağlı bir alan ekle: sayfa sayısı (`pages`).

**İstenenler:**

1. Kitabın `pages` alanı bir tam sayı ya da `null` olsun; gönderilmezse `null` olsun.
2. Gönderilirse en az 1 olsun.
3. `PATCH` ile değiştirilebilsin ve kitap yanıtlarında görünsün.

**İpucu:** Değiştirmen gereken üç model var: biri `database.py` dosyasında, ikisi `server.py` dosyasında. Kodu yazıp sunucuyu yeniden başlattıktan sonra bir istek gönder. `500` alırsan sunucunun terminalindeki hatanın son satırını oku: Python sınıfını değiştirdin, peki tablo değişti mi?

**Kontrol et:** Sonuçlar şöyle olmalı:

| İstek | Durum kodu | Yanıtta `pages` |
|---|---|---|
| `GET /books/42` | `200` | `null` |
| `POST /books`, `"pages": 320` | `201` | `320` |
| `POST /books`, `"pages": 0` | `422` | Yok; `loc`: `['body', 'pages']` |
| `PATCH /books/42`, `{"pages": 250}` | `200` | `250` |

Kodunu yazıp denedikten sonra [ek nottaki cevapla](09_Supplement_Exercise_8_3_Answer.md) karşılaştır.

---

## 9. Kendini kontrol et: Bu haftanın yedi sorusu

1. Hafta 5'in sonundaki sunucuda eklenen bir kitap, sunucu yeniden başlayınca neden kayboluyordu? Bu hafta neden kaybolmuyor?
2. `Book` sınıfı, `book` tablosu ve `Book(...)` ile oluşturulan bir nesne arasındaki ilişki nedir?
3. `Book` modelinde `id` alanı neden `int | None` ve varsayılan değeri neden `None`?
4. `session.add(book)` satırından sonra `session.commit()` yazılmazsa ne olur?
5. `Book` tablo modeli varken `BookCreate` ve `BookPublic` modellerine neden hâlâ ihtiyacımız var?
6. 42 numaralı kitap silinince yorumlarını kim siliyor? Hafta 4'teki sunucudan farkı ne?
7. Föydeki başlangıç hâline nasıl dönüyoruz? Sunucuyu yeniden başlatmak bu hafta neden yetmiyor?

### 9.1 Soruların cevapları

1. Kitaplar `server.py` dosyasındaki `books` listesindeydi; liste yalnızca çalışan sunucunun belleğinde duruyordu ve sunucu yeniden başlayınca dosyadaki hâliyle yeniden oluşturuluyordu. Bu hafta kitaplar PostgreSQL veritabanında. Veritabanı sunucumuzdan ayrı çalışan bir program ve veriyi kendi dosyalarında saklıyor; sunucumuz her istekte ona soruyor.
2. `table=True` ile yazılan `Book` sınıfı `book` tablosunu tanımlar: Sınıfın her alanı tablonun bir sütunudur. `Book(...)` ile oluşturulan her nesne, oturuma eklenip `commit` edilince tabloda bir kayıt olur. Tabloyu `create_all` bu sınıftan oluşturdu.
3. Python'da yeni bir `Book` nesnesi oluşturduğumuzda henüz bir kimliği yoktur; kimliği kayıt veritabanına yazılırken veritabanının sayacı verir. Nesne bu arada `None` kimlikle durur. Deney 2'de kimliğin kaydetmeden önce `None`, kaydettikten sonra `74` olduğunu gördük.
4. Kayıt veritabanına yazılmaz. `session.add` kaydı yalnızca oturuma ekler; `commit` olmadan oturum kapanınca ekleme geri alınır. Deney 2.2'de kitap kaydedilmedi ve kimliği `None` kaldı.
5. Görevleri farklı. `BookCreate` istemcinin gönderdiği gövdeyi kontrol eder: kuralları (`min_length`, `ge`, `le`), sıkı modu ve fazla alanları reddetmeyi o taşır. `Book` bu kontrolleri yapmaz, yalnızca verinin tabloda nasıl saklanacağını anlatır. `BookPublic` ise istemciye neyin gideceğini belirler: Tabloda `internal_note` var, ama yanıtta yok.
6. Veritabanı. `Review` tablosundaki `book_id` sütunu `book` tablosuna bir yabancı anahtarla bağlı ve `ondelete="CASCADE"` kuralı var; kitap silinince veritabanı yorumlarını da siler. Hafta 4'teki sunucuda `delete_book` yalnızca `books` listesinden kitabı çıkarıyordu, yorumlar `reviews` listesinde kalıyordu.
7. `python reset_db.py` ile: Program tabloları silip yeniden oluşturur ve başlangıçtaki kitapları ve yorumu yazar. Sunucuyu yeniden başlatmak yetmez, çünkü kayıtlar artık sunucunun belleğinde değil, veritabanında; sunucu yeniden başlayınca veritabanındaki kayıtları olduğu gibi okur.

**Deney 6'daki tablonun cevapları:**

| İstemcideki satır | HTTP isteği | Değişikliği yapan SQL komutu |
|---|---|---|
| `Create` | `POST /books` | `INSERT INTO book ...` |
| `Patch 57` | `PATCH /books/57` | `UPDATE book SET rating=%(rating)s WHERE book.id = ...` |
| `Delete 73` | `DELETE /books/73` | `DELETE FROM book WHERE book.id = ...` |

`UPDATE` komutunda yalnızca `rating` sütunu var, çünkü `exclude_unset=True` ile yalnızca gönderilen alan kitaba yazıldı; SQLModel de yalnızca değişen sütunu güncelledi. İki istekte de değişiklikten önce bir `SELECT` var: `session.get` kitabı kimliğine göre okuyor.

---

## 10. Resmî belgeler

- [SQLModel — Create a Table with SQLModel](https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/)
- [SQLModel — Create Rows](https://sqlmodel.tiangolo.com/tutorial/insert/): Bu belgelerde kayda *row*, yani satır denir.
- [SQLModel — Automatic IDs, None Defaults, and Refreshing Data](https://sqlmodel.tiangolo.com/tutorial/automatic-id-none-refresh/)
- [SQLModel — Read Data, Filter Data](https://sqlmodel.tiangolo.com/tutorial/select/), [Where](https://sqlmodel.tiangolo.com/tutorial/where/), [Read One Row](https://sqlmodel.tiangolo.com/tutorial/one/)
- [SQLModel — Update Data](https://sqlmodel.tiangolo.com/tutorial/update/), [Delete Data](https://sqlmodel.tiangolo.com/tutorial/delete/)
- [SQLModel — Cascade Delete Relationships](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/cascade-delete-relationships/): `ondelete="CASCADE"` bu sayfada.
- [FastAPI — SQL (Relational) Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/): Bu sayfada oturum, fonksiyona bir parametre olarak verilir (`SessionDep`). Biz her fonksiyonda oturumu `with Session(engine)` ile kendimiz açtık; iki yol da aynı işi yapar.
- [PostgreSQL — Constraints](https://www.postgresql.org/docs/16/ddl-constraints.html): Birincil ve yabancı anahtarlar
- [PostgreSQL — JSON Types](https://www.postgresql.org/docs/16/datatype-json.html)
- [PostgreSQL — psql](https://www.postgresql.org/docs/16/app-psql.html)
- [Docker Hub — postgres](https://hub.docker.com/_/postgres): `POSTGRES_USER`, `POSTGRES_PASSWORD` ve `POSTGRES_DB` ayarları bu sayfada.

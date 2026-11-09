# Ek Not — Docker ile Veritabanını Yönetmek

Föyün 0.2 bölümünde PostgreSQL'i tek bir `docker run` komutuyla başlattık. Bu notta kapsayıcıyı durdurmayı, yeniden başlatmayı ve silmeyi, ayrıca en sık karşılaşılan iki hatayı görüyoruz.

---

## 1. İmaj ve kapsayıcı

| Kavram | Ne demek? | Bizim örneğimizde |
|---|---|---|
| **İmaj (image)** | Bir programın, çalışması için gereken her şeyle birlikte paketlenmiş hâli. Değişmez; bir kalıp gibidir. | `postgres:16` |
| **Kapsayıcı (container)** | Bir imajdan başlatılmış, çalışan kopya. Kendi dosyaları vardır; veritabanının kayıtları da bu dosyalarda durur. | `book-db` |

Aynı imajdan birden fazla kapsayıcı başlatılabilir; her birinin verisi ayrıdır.

---

## 2. Sık kullanılan komutlar

| Komut | Ne yapar? | Veriye ne olur? |
|---|---|---|
| `docker ps` | Çalışan kapsayıcıları listeler. | Değişmez. |
| `docker ps -a` | Durmuş olanlar dahil bütün kapsayıcıları listeler. | Değişmez. |
| `docker stop book-db` | Kapsayıcıyı durdurur. | Kalır. |
| `docker start book-db` | Durmuş kapsayıcıyı yeniden başlatır. | Durdurulduğu hâliyle geri gelir. |
| `docker logs book-db` | PostgreSQL'in kendi çıktısını gösterir. Veritabanı başlamıyorsa buraya bak. | Değişmez. |
| `docker rm -f book-db` | Kapsayıcıyı siler. | **Kaybolur.** Aynı `docker run` komutuyla yeniden oluşturursan veritabanı boş başlar; `python reset_db.py` ile tabloları ve kitapları yeniden yazman gerekir. |

Kapsayıcıyı durdurup başlattıktan sonra kayıtların durduğunu denedik: `docker stop` ve `docker start` komutlarından sonra `book` tablosunda yine üç kitap vardı.

---

## 3. Sık karşılaşılan iki hata

### `docker run` komutunu ikinci kez çalıştırmak

```text
docker: Error response from daemon: Conflict. The container name "/book-db" is already in use by container "...". You have to remove (or rename) that container to be able to reuse that name.
```

`book-db` adında bir kapsayıcı zaten var. `docker run` her seferinde yeni bir kapsayıcı oluşturmaya çalışır. Var olan kapsayıcıyı başlatmak için `docker start book-db` yeterli.

### 5432 numaralı port dolu

```text
docker: Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint book-db (...): Bind for 0.0.0.0:5432 failed: port is already allocated
```

Bilgisayarında 5432 numaralı portu kullanan başka bir program var; örneğin daha önce kurulmuş bir PostgreSQL. Hafta 1'de 8000 numaralı port dolu olduğunda sunucumuzun başlamadığını görmüştük; bu da aynı durum. Önce yarım kalan kapsayıcıyı sil, sonra başka bir port seçerek yeniden oluştur:

```bash
docker rm -f book-db
docker run --name book-db -e POSTGRES_USER=student -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=catalog -p 5433:5432 -d postgres:16
```

`-p 5433:5432`, bilgisayarın 5433 numaralı portunu kapsayıcının 5432 numaralı portuna bağlar. Bu durumda `database.py` dosyasındaki adreste de portu değiştir:

```python
DATABASE_URL = "postgresql+psycopg://student:secret@localhost:5433/catalog"
```

---

## 4. Veritabanı çalışmıyorsa sunucu ne yapar?

Sunucu yine başlar, çünkü `create_engine` bağlantıyı hemen kurmaz. Ama veritabanına giden ilk istek `500 Internal Server Error` alır. Sunucunun terminalinde uzun bir hata çıktısı görünür; içinde şuna benzeyen bir satır vardır:

```text
psycopg.OperationalError: connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
```

*Connection refused*, "bağlantı reddedildi" demek: O portta bağlantı bekleyen bir program yok. `docker ps` ile `book-db` kapsayıcısının çalıştığını kontrol et; çalışmıyorsa `docker start book-db` komutunu çalıştır.

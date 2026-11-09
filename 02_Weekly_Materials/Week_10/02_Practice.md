# Hafta 10 — Uygulama Föyü

## 0. Kim neyi yapabilir?

Hafta 9'da sunucu, bir isteği kimin gönderdiğini öğrendi. Ama bu bilgiyi yalnızca yorumlarda kullanıyoruz. Kitap ekleme, değiştirme ve silme işlemleri hâlâ herkese açık: Token göndermeyen biri bile kataloğun bütün kitaplarını silebilir.

Bir API'nin hangi kullanıcıya hangi işlemi yaptıracağını belirlemeye **erişim denetimi (access control)** denir. Kataloğumuz için istediğimiz kurallar şunlar:

| İşlem | Herkes | Okur (Ece, Can) | Kütüphaneci (Selin) |
|---|---|---|---|
| Kitapları ve yorumları okumak | Evet | Evet | Evet |
| Kitap eklemek, değiştirmek, silmek | Hayır | Hayır | Evet |
| Yorum yazmak | Hayır | Evet | Evet |
| Yorumu değiştirmek ve silmek | Hayır | Yalnızca kendi yorumunu | Yalnızca kendi yorumunu |
| Kullanıcıları listelemek | Hayır | Hayır | Evet |

Bu tablodaki her "Hayır" bir **başarısız olması gereken istek**. Şimdiye kadar testlerimizin çoğu bir işlemin çalıştığını kontrol ediyordu. Bu hafta testlerin önemli bir kısmı bir işlemin **çalışmadığını** kontrol edecek. Güvenlik açıkları genellikle tam burada saklanır: Kimse "çalışmaması gereken" isteği denemediği için.

Haftanın sonunda şu soruya cevap verebileceksin: **API'min yalnızca izin verdiğim istekleri yaptığından nasıl emin olurum?**

Bu hafta sırasıyla şunları yapacağız:

- **Deney 1:** Başarısız olması gereken istekleri test olarak yazmak ve bugün başarılı olduklarını görmek
- **Deney 2:** Kütüphaneci rolünü eklemek ve kitap işlemlerini korumak
- **Deney 3:** Giriş gerektiren, ama yine de başkasının kaydını değiştirmeye izin veren bir işlemi bulmak ve düzeltmek
- **Deney 4:** Yalnızca kütüphanecinin görebildiği bir yanıtın, görmemesi gereken bir bilgiyi taşıdığını bulmak

### 0.1 Başlangıç dosyaları

Hafta 9'un sonundaki dosyalarla başla: `server.py`, `database.py`, `reset_db.py`, `passwords.py`, `auth.py` ve on altı testli `test_server.py`. Kendi dosyalarından emin değilsen bu haftanın başlangıç dosyalarını kullan: [Starting_Code](Starting_Code/). Föydeki çıktılar bu dosyalarla alındı.

> **Hafta 9'un ödevini yaptıysan:** `/logout` ve `/me/reviews` işlemleri ve testleri dosyalarında kalabilir. Test sayıların föydekinden fazla olur.

### 0.2 Veritabanını başlat

```bash
docker start book-db
```

Bu hafta yeni paket kurmuyoruz.

---

## Deney 1 — Başarısız olması gereken istekler

**Amaç:** Erişim tablosundaki kuralları önce test olarak yazmak ve bugünkü sunucunun bu kuralların hiçbirine uymadığını görmek.

### 1.1 Üç test

Hafta 8'de bir hata bildirimini önce teste çevirmiş, sonra düzeltmiştik. Burada henüz bir bildirim yok; ama kuralı biliyoruz. `test_server.py` dosyasının sonuna üç test ekle:

```python
# Erişim: tokensiz kitap silinemez.
def test_delete_book_requires_login():
    response = client.delete("/books/57")
    assert response.status_code == 401

    response = client.get("/books/57")
    assert response.status_code == 200


# Erişim: okur kitap silemez.
def test_reader_cannot_delete_book():
    response = client.delete("/books/57", headers=login_as("Can", "can-parola"))
    assert response.status_code == 403

    response = client.get("/books/57")
    assert response.status_code == 200


# Erişim: okur kitabı değiştiremez.
def test_reader_cannot_patch_book():
    response = client.patch("/books/57", json={"title": "Değişti"}, headers=login_as("Can", "can-parola"))
    assert response.status_code == 403

    response = client.get("/books/57")
    assert response.json()["title"] == "Veriyle İlk Adımlar"
```

Hafta 9'daki `test_delete_other_users_review` testi gibi, her test iki şeyi kontrol ediyor: İsteğin reddedildiğini ve kitabın gerçekten değişmediğini.

### 1.2 Çalıştır

```bash
python -m pytest --tb=short
```

```text
test_server.py ................FFF                                       [100%]

=================================== FAILURES ===================================
_______________________ test_delete_book_requires_login ________________________
test_server.py:186: in test_delete_book_requires_login
    assert response.status_code == 401
E   assert 204 == 401
E    +  where 204 = <Response [204 No Content]>.status_code
________________________ test_reader_cannot_delete_book ________________________
test_server.py:195: in test_reader_cannot_delete_book
    assert response.status_code == 403
E   assert 204 == 403
E    +  where 204 = <Response [204 No Content]>.status_code
________________________ test_reader_cannot_patch_book _________________________
test_server.py:204: in test_reader_cannot_patch_book
    assert response.status_code == 403
E   assert 200 == 403
E    +  where 200 = <Response [200 OK]>.status_code
=========================== short test summary info ============================
FAILED test_server.py::test_delete_book_requires_login - assert 204 == 401
FAILED test_server.py::test_reader_cannot_delete_book - assert 204 == 403
FAILED test_server.py::test_reader_cannot_patch_book - assert 200 == 403
========================= 3 failed, 16 passed in 5.34s =========================
```

Üç test de kaldı. Tokensiz bir istek 57 numaralı kitabı sildi (`204`); Can da sildi ve kitabın adını değiştirdi. Kod bir hata vermedi; yalnızca yapmaması gereken bir şeyi yaptı.

Bu testlerin kalması iyi bir haber: Açığı biz bulduk, testler de onu görüyor. Deney 2'de kuralları ekledikten sonra aynı testler geçmeli.

> **Ana fikir:** Erişim kuralları da birer davranıştır ve test edilir. "Bu istek başarısız olmalı" diyen testler, ancak biri o isteği denediğinde ortaya çıkan açıkları önceden gösterir. Bir yetki testi hem isteğin reddedildiğini hem de verinin değişmediğini kontrol etmelidir.

---

## Deney 2 — Kütüphaneci rolü

**Amaç:** Kullanıcılara bir rol eklemek ve kitap işlemlerini yalnızca kütüphanecilere açmak.

### 2.1 Rol bir alan

Kimin kütüphaneci olduğunu kullanıcının kaydında tutacağız. `database.py` dosyasında `User` modeline bir alan ekle ve açıklama satırını güncelle:

```python
# Kullanıcı tablosu: parolanın kendisi değil, özeti saklanır; kütüphaneciler kitapları değiştirebilir.
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    password_hash: str
    is_librarian: bool = False
```

Varsayılan değer `False`: Yeni bir kullanıcı, açıkça kütüphaneci yapılmadıkça okurdur. İzinlerde varsayılan "hayır" olmalı; bir kullanıcıya fazladan bir hak vermek, onu bir haktan yoksun bırakmaktan daha tehlikelidir.

`reset_database` fonksiyonunda Can'in satırının altına bir kütüphaneci ekle:

```python
        session.add(User(username="Selin", password_hash=hash_password("selin-parola"), is_librarian=True))
```

`reset_db.py` dosyasının son satırını güncelle:

```python
print("Database reset: 3 books, 1 review, 3 users")
```

```bash
python reset_db.py
```

```text
Database reset: 3 books, 1 review, 3 users
```

### 2.2 "Bu kullanıcı kütüphaneci mi?"

Hafta 9'da `auth.py` dosyasını hazır kullanmıştık. Bu kez ona kendimiz bir fonksiyon ekliyoruz. `auth.py` dosyasının sonuna:

```python
# İsteği gönderen kullanıcı kütüphaneci değilse 403.
def get_current_librarian(user: User = Depends(get_current_user)):
    if not user.is_librarian:
        raise HTTPException(status_code=403, detail="Only librarians can do this")

    return user
```

Bu fonksiyon da bir bağımlılık ve kendisi de bir bağımlılık kullanıyor: Önce `get_current_user` çalışır ve kullanıcıyı bulur; token yoksa ya da geçersizse istek orada `401` alır. Kullanıcı bulunursa `get_current_librarian` onun kütüphaneci olup olmadığına bakar; değilse `403`. Sıra, Hafta 9'daki ayrımın aynısı: Önce "kim?", sonra "yapabilir mi?".

### 2.3 Kitap işlemlerini koru

`server.py` dosyasında import satırını değiştir:

| Eski satır | Yeni satır |
|---|---|
| `from auth import get_current_user` | `from auth import get_current_librarian, get_current_user` |

Kitap ekleyen, silen, tümüyle ve kısmen değiştiren dört işlemin dekoratörlerine aynı ayarı ekle:

| İşlem | Yeni dekoratör |
|---|---|
| `create_book` | `@app.post("/books", status_code=201, response_model=BookPublic, dependencies=[Depends(get_current_librarian)])` |
| `delete_book` | `@app.delete("/books/{book_id}", status_code=204, dependencies=[Depends(get_current_librarian)])` |
| `replace_book` | `@app.put("/books/{book_id}", response_model=BookPublic, dependencies=[Depends(get_current_librarian)])` |
| `update_book` | `@app.patch("/books/{book_id}", response_model=BookPublic, dependencies=[Depends(get_current_librarian)])` |

`dependencies=[...]`, Hafta 9'daki `user: User = Depends(...)` parametresinin başka bir yazımı. Fark şu: Bu işlemlerin fonksiyonları kullanıcıyı kullanmıyor; yalnızca isteğin bir kütüphaneciden gelip gelmediğinin kontrol edilmesini istiyoruz. Bağımlılığı dekoratöre yazınca FastAPI onu yine fonksiyondan önce çalıştırır, ama sonucunu fonksiyona vermez. Fonksiyonların kendisi değişmiyor.

### 2.4 Testler

```bash
python -m pytest --tb=no
```

`--tb=no` seçeneği hata izlerini hiç göstermez; yalnızca kalan testlerin kısa listesi kalır. Çok sayıda test kaldığında önce hangilerinin kaldığına bakmak için kullanışlı:

```text
test_server.py ..F.F.FF.F.F.......                                       [100%]

=========================== short test summary info ============================
FAILED test_server.py::test_create_book - assert 401 == 201
FAILED test_server.py::test_rating_out_of_range - assert 401 == 422
FAILED test_server.py::test_patch_rating - assert 401 == 200
FAILED test_server.py::test_patch_null_title - assert 401 == 422
FAILED test_server.py::test_delete_book_deletes_reviews - assert 401 == 204
FAILED test_server.py::test_replace_book - assert 401 == 200
========================= 6 failed, 13 passed in 6.04s =========================
```

Deney 1'in üç testi artık geçiyor. Ama altı eski test kaldı ve hepsi aynı nedenle: `401`. Bu testler kitap ekliyor, değiştiriyor ya da siliyor ve token göndermiyor. Hafta 9'un Deney 5'indeki durum: Kural bilerek değişti, testler eski kuralı kontrol ediyor.

`test_rating_out_of_range` ve `test_patch_null_title` testlerinin `422` yerine `401` aldığına dikkat et: Gövdedeki hatalı puana ve `null` ada bakılmadı. Bağımlılıklar, Hafta 8'deki 2. adımda gövdeden önce kontrol edilir; kimliği belirsiz bir isteğin gövdesine bakılmaz.

Altı testte kitap isteğine Selin'in başlığını ekle. Her testte değişen tek satır:

| Test | Yeni satır |
|---|---|
| `test_create_book` | `response = client.post("/books", json=new_book, headers=login_as("Selin", "selin-parola"))` |
| `test_rating_out_of_range` | `response = client.post("/books", json=book, headers=login_as("Selin", "selin-parola"))` |
| `test_patch_rating` | `response = client.patch("/books/57", json={"rating": 3}, headers=login_as("Selin", "selin-parola"))` |
| `test_patch_null_title` | `response = client.patch("/books/42", json={"title": None}, headers=login_as("Selin", "selin-parola"))` |
| `test_delete_book_deletes_reviews` | `response = client.delete("/books/42", headers=login_as("Selin", "selin-parola"))` |
| `test_replace_book` | `response = client.put("/books/73", json=new_book, headers=login_as("Selin", "selin-parola"))` |

Testleri yeniden çalıştır:

```text
============================== 19 passed in 6.42s ==============================
```

> **Ana fikir:** Rol, kullanıcının kaydındaki bir alandır ve varsayılan değeri en az yetkili olandır. Bir bağımlılık başka bir bağımlılığı kullanabilir: `get_current_librarian`, önce `get_current_user` ile kimliği doğrular (`401`), sonra rolü kontrol eder (`403`). Fonksiyonun kullanıcıya ihtiyacı yoksa bağımlılık dekoratöre `dependencies=[...]` ile yazılır.

---

## Deney 3 — Giriş yapmak yetmez

**Amaç:** Giriş gerektiren bir işlemin, yine de başkasının kaydını değiştirmeye izin verebildiğini görmek ve düzeltmek.

### 3.1 Yorumu değiştirme işlemi

Ekip arkadaşın, okurların yorumlarını düzeltebilmesi için bir işlem yazdı. `server.py` dosyasında `ReviewPublic` modelinin altına onun modelini ekle:

```python
class ReviewUpdate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    comment: str = Field(default=None, min_length=1)
    score: int = Field(default=None, ge=1, le=5)
```

`delete_review` fonksiyonunun altına onun işlemini ekle:

```python
# Yorumu değiştirme: yalnızca gönderilen alanlar değişir; yorum yoksa 404.
@app.patch("/books/{book_id}/reviews/{review_id}", response_model=ReviewPublic)
def update_review(review_data: ReviewUpdate, book_id: int = Path(gt=0), review_id: int = Path(gt=0), user: User = Depends(get_current_user)):
    with Session(engine) as session:
        review = session.get(Review, review_id)

        if review is None or review.book_id != book_id:
            raise HTTPException(status_code=404, detail="Review not found")

        review.sqlmodel_update(review_data.model_dump(exclude_unset=True))
        session.commit()
        session.refresh(review)
        return review
```

İşlem, Hafta 4'teki `update_book` ile Hafta 9'daki `delete_review` fonksiyonlarının birleşimi. `ReviewUpdate` modeli, Hafta 5'teki `BookUpdate` gibi: Alanlar gönderilmeyebilir, ama gönderilirse `null` olamaz. Ekip arkadaşın "Giriş gerektiriyor, yani güvenli." diyor.

### 3.2 Erişim tablosunu teste çevir

Tablodaki kural: Yorumu yalnızca sahibi değiştirebilir. Bu kuralın başarısız olması gereken isteği, Can'in Ece'nin yorumunu değiştirmesi. Dosyanın sonuna ekle:

```python
# Erişim: okur başkasının yorumunu değiştiremez.
def test_reader_cannot_edit_other_review():
    response = client.patch("/books/42/reviews/1", json={"score": 1}, headers=login_as("Can", "can-parola"))
    assert response.status_code == 403

    response = client.get("/books/42/reviews")
    assert response.json()[0]["score"] == 5
```

```bash
python -m pytest --tb=short
```

```text
test_server.py ...................F                                      [100%]

=================================== FAILURES ===================================
_____________________ test_reader_cannot_edit_other_review _____________________
test_server.py:213: in test_reader_cannot_edit_other_review
    assert response.status_code == 403
E   assert 200 == 403
E    +  where 200 = <Response [200 OK]>.status_code
=========================== short test summary info ============================
FAILED test_server.py::test_reader_cannot_edit_other_review - assert 200 == 403
========================= 1 failed, 19 passed in 7.09s =========================
```

Can, Ece'nin yorumunun puanını `5` yerine `1` yaptı ve `200` aldı. İşlem gerçekten giriş gerektiriyor: Tokensiz istek `401` alır. Ama giriş yapan **her** kullanıcı, **her** yorumu değiştirebiliyor. Fonksiyon "kim?" sorusunu soruyor, "bu yorum onun mu?" sorusunu sormuyor.

Bu, API'lerde en sık bulunan açık. Adı **nesne düzeyinde yetki hatası (broken object level authorization)**: Kullanıcı, adresteki kimliği değiştirerek (`/reviews/1`, `/reviews/2`, ...) başkalarının kayıtlarına ulaşabiliyor. Açığı bulmak için özel bir araç gerekmiyor; adresteki sayıyı değiştirmek yetiyor.

### 3.3 Düzelt

Hafta 9'da `delete_review` fonksiyonuna yazdığımız kontrolü buraya da ekle. `404` kontrolünün altına:

```python
        if review.user_id != user.id:
            raise HTTPException(status_code=403, detail="You can only change your own reviews")
```

Açıklama satırını da güncelle:

```python
# Yorumu değiştirme: yalnızca yorumu yazan kullanıcı değiştirebilir; yalnızca gönderilen alanlar değişir; yorum yoksa 404, başkasının yorumuysa 403.
```

Testleri çalıştır:

```text
============================== 20 passed in 6.74s ==============================
```

Bir kaydı değiştiren ya da silen her işlemde aynı iki soruyu sormak gerekir: "Kayıt var mı?" (`404`) ve "Kayıt bu kullanıcının mı?" (`403`). İkinci soru unutulduğunda kod hata vermez ve sahibinin kendi istekleriyle yapılan testler geçer; açığı yalnızca **başka** bir kullanıcının isteğini gönderen bir test görür.

> **Ana fikir:** Kimlik doğrulama (`401`), kaydın sahibini kontrol etmenin yerini tutmaz. Bir kaydı adresteki kimliğiyle bulan her işlem, kaydın isteği gönderen kullanıcıya ait olup olmadığını ayrıca kontrol etmelidir. Bu kontrolü, başka bir kullanıcının isteğini gönderen bir test korur.

---

## Deney 4 — Yanıtta ne var?

**Amaç:** Doğru kullanıcıya açık bir işlemin, yanıtında gizli kalması gereken bir bilgiyi taşıyıp taşımadığını kontrol etmek.

### 4.1 Kullanıcı listesi

Ekip arkadaşın, kütüphanecilerin kullanıcıları görebilmesi için bir işlem daha yazdı. Dosyanın sonuna ekle:

```python
# Kullanıcı listesi: yalnızca kütüphaneciler görebilir.
@app.get("/users", dependencies=[Depends(get_current_librarian)])
def get_users():
    with Session(engine) as session:
        statement = select(User).order_by(User.id)
        return session.exec(statement).all()
```

Erişim kuralı doğru: Okurlar ve tokensiz istekler bu listeyi göremez. Ama bir şey eksik. Okumadan önce kendin bulmaya çalış: Hafta 4'ten beri her işlemin dekoratöründe olan ve burada olmayan ne?

### 4.2 Yanıtı teste çevir

Kütüphaneci kullanıcı listesini görebilir; ama listede parolaların özetleri olmamalı. Bir kütüphanecinin hesabı ele geçirilirse, özetler bütün kullanıcıların parolalarını tahmin etmeye çalışmak için kullanılabilir (Hafta 9, 1.1). Dosyanın sonuna ekle:

```python
# Kullanıcı listesi: parola özetleri yanıtta görünmez.
def test_users_hide_password_hash():
    response = client.get("/users", headers=login_as("Selin", "selin-parola"))
    assert response.status_code == 200

    for user in response.json():
        assert "password_hash" not in user
```

`"password_hash" not in user`, sözlükte bu adla bir alan **olmadığını** kontrol eder. Test, listedeki her kullanıcı için bunu soruyor.

```bash
python -m pytest --tb=short
```

```text
test_server.py ....................F                                     [100%]

=================================== FAILURES ===================================
________________________ test_users_hide_password_hash _________________________
test_server.py:225: in test_users_hide_password_hash
    assert "password_hash" not in user
E   AssertionError: assert 'password_hash' not in {'username': 'Ece', 'password_hash': 'ca9c1a7f9c479ff4950955f3db161986$fcbe950876cdde20bd9576145f6ceb1850b5710978aba9fde51905529392a9d1', 'is_librarian': False, 'id': 1}
=========================== short test summary info ============================
FAILED test_server.py::test_users_hide_password_hash - AssertionError: assert...
========================= 1 failed, 20 passed in 7.25s =========================
```

Senin çıktındaki özet farklı olur. pytest, kalan karşılaştırmada sözlüğün tamamını gösterdi; yani yanıtın içinde ne olduğunu da: Ece'nin parolasının özeti ve kütüphaneci olup olmadığı.

İşlemin dekoratöründe `response_model` yok. Yanıt modeli olmadan FastAPI, fonksiyonun döndürdüğü nesnenin **bütün** alanlarını JSON'a çevirir. Hafta 4'te `internal_note` alanını yanıtlardan gizlemek için yanıt modeli yazmıştık; Hafta 9'da da `/me` işlemi `UserPublic` modelini kullanıyor. Bu işlem kullanmıyor.

### 4.3 Düzelt

Dekoratöre yanıt modelini ekle:

```python
@app.get("/users", response_model=list[UserPublic], dependencies=[Depends(get_current_librarian)])
```

Testleri çalıştır:

```text
============================== 21 passed in 6.96s ==============================
```

Bu açık, Deney 3'tekinden farklı bir yerde: Kimin istek gönderebileceği doğruydu; yanlış olan, yanıtın içindekiydi. Erişim denetimi yalnızca "kim hangi işlemi yapabilir?" değil, "kim hangi alanı görebilir?" sorusunu da kapsar. Yanıt modeli, gösterilecek alanların listesidir; listede olmayan bir alan, ne kadar yetkili biri isterse istesin yanıta girmez.

> **Ana fikir:** Bir yanıtın hangi alanları taşıyacağı da bir erişim kararıdır. Yanıt modeli olmayan bir işlem, tablo modelinin bütün alanlarını, gizli olanlar dahil, istemciye gönderir. Bir testte bir alanın yanıtta **olmadığını** kontrol etmek, böyle bir sızıntıyı yakalar.

---

## 5. Bu haftanın sonundaki dosyalar

| Dosya | Bu hafta |
|---|---|
| `database.py` | `User` modelindeki `is_librarian` (2.1), Selin (2.1) |
| `reset_db.py` | Son satır (2.1) |
| `auth.py` | `get_current_librarian` (2.2) |
| `server.py` | Import satırı ve dört kitap işleminin dekoratörü (2.3); `ReviewUpdate` ve `update_review` (3.1, 3.3); `get_users` (4.1, 4.3) |
| `test_server.py` | Deney 1'in üç testi; altı testin güncellenen satırı (2.4); iki yeni test (3.2, 4.2) |

Dosyaların tamamını [ek notta](04_Supplement_Final_Files.md) bulabilirsin. Bu hafta karşılaştığımız açıkların, API güvenliğinde bilinen adlarını ve föyde ele almadığımız birkaç açığı da [başka bir ek notta](03_Supplement_API_Security_Risks.md) bulabilirsin.

---

## 6. Ödev: belge ve iki kural

### 6.1 `README.md` belgesini güncellemek

Hafta 9'da yazdığın `## Kimlik doğrulama` bölümündeki tabloyu, bu haftanın 0. bölümündeki erişim tablosuyla değiştir. Başlangıç kullanıcılarının satırına Selin'i ekle: `Selin` (`selin-parola`), kütüphaneci. `## Hata yanıtları` bölümündeki `403` satırına bu haftanın iki açıklamasını ekle: `Only librarians can do this` ve `You can only change your own reviews`.

### 6.2 Kendin yaz: kütüphaneci yorum silebilsin

Kütüphanecinin, kurallara aykırı bir yorumu silebilmesi gerekiyor. Ama yorumları değiştirememeli: Bir okurun yorumunu onun adıyla değiştirmek, okurun söylemediği bir şeyi ona söyletmek olur.

**İstenenler:**

1. `delete_review` fonksiyonunu değiştir: Yorumu, sahibinin yanında bir kütüphaneci de silebilsin. Okurlar için kural aynı kalsın.
2. `test_librarian_can_delete_any_review` testini yaz: Selin, Ece'nin yorumunu silsin (`204`); 42 numaralı kitabın yorum listesi boş olsun.
3. Deney 3'teki `update_review` fonksiyonuna dokunma. Can için yazdığın `test_delete_other_users_review` ve `test_reader_cannot_edit_other_review` testleri hâlâ geçmeli.

**İpucu:** Değişen tek satır, `403` yanıtını veren `if` satırı. Koşul "sahibi değil" yerine "sahibi değil **ve** kütüphaneci de değil" olmalı.

**Kontrol et:** Sonuç `22 passed` olmalı (önceki haftaların ödev testleri varsa daha fazla).

Kodunu yazıp denedikten sonra [ek nottaki cevapla](05_Supplement_Exercise_6_2_Answer.md) karşılaştır.

### 6.3 Kendin yaz: tokenin süresi dolsun

Hafta 9'daki tokenler hiç geçersiz olmuyor. Çalınan ya da unutulan bir token, silinene kadar kullanılabilir.

**İstenenler:**

1. `Token` modeline tokenin üretildiği zamanı gösteren bir `created_at` alanı ekle.
2. `get_current_user` fonksiyonu, bir saatten eski tokenleri `401` ve `{"detail": "Token expired"}` ile reddetsin.
3. `test_expired_token` testini yaz: Ece olarak giriş yap; tokenin `created_at` değerini veritabanında iki saat geriye al; aynı tokenle `/me` iste ve `401` al.

**İpucu:** Python'un `datetime` modülündeki `datetime.now(timezone.utc)` şu anki zamanı verir; `timedelta(hours=1)` bir saatlik süreyi gösterir. İki zamanın farkı da bir `timedelta` olur ve öteki süreyle karşılaştırılabilir. Testte zamanın geçmesini beklemek yerine, kaydı Hafta 7'nin Deney 5'indeki gibi `Session(engine)` ile doğrudan değiştirebilirsin.

**Kontrol et:** 6.2 ile birlikte sonuç `23 passed` olmalı.

Kodunu yazıp denedikten sonra [ek nottaki cevapla](06_Supplement_Exercise_6_3_Answer.md) karşılaştır.

---

## 7. Kendini kontrol et: Bu haftanın yedi sorusu

1. Erişim denetimi hangi soruya cevap verir? Kimlik doğrulamadan farkı nedir?
2. "Başarısız olması gereken istek" testleri neden gerekli? Bir yetki testi hangi iki şeyi kontrol etmeli?
3. `is_librarian` alanının varsayılan değeri neden `False`?
4. Tokensiz bir `POST /books` isteği, gövdesinde hatalı bir puan olsa da neden `422` değil `401` alıyor?
5. Deney 3'teki işlem giriş gerektiriyordu. Açık neydi; neden yalnızca Ece'nin isteğini gönderen bir test onu yakalamazdı?
6. `dependencies=[Depends(get_current_librarian)]` ile `user: User = Depends(get_current_user)` yazımları arasındaki fark nedir?
7. Deney 4'teki işlemin erişim kuralı doğruydu. Yine de neyi yanlıştı ve hangi satır düzeltti?

### 7.1 Soruların cevapları

1. Erişim denetimi, "bu kullanıcı bu işlemi, bu kayıt üzerinde yapabilir mi; bu alanı görebilir mi?" sorusuna cevap verir. Kimlik doğrulama yalnızca isteği kimin gönderdiğini bulur; erişim denetimi bu bilgiyi kullanarak izin verir ya da reddeder.
2. Bir işlemin çalıştığını gösteren testler, yapmaması gereken bir şeyi yapıp yapmadığını göstermez. Açıklar, kimsenin denemediği isteklerde saklanır. Bir yetki testi hem isteğin reddedildiğini (`401` ya da `403`) hem de verinin değişmediğini kontrol etmelidir; yalnızca durum koduna bakan bir test, isteği reddettiği hâlde veriyi değiştiren bir kodu yakalamaz.
3. İzinlerde varsayılan "hayır" olmalı. Yeni bir kullanıcının kütüphaneci olması için bunun açıkça yazılması gerekir. Varsayılan `True` olsaydı, bir kullanıcıyı eklerken alanı yazmayı unutmak ona kitapları silme hakkı verirdi.
4. `get_current_librarian` bir bağımlılık ve bağımlılıklar gövdeden önce kontrol edilir. Kimliği belirsiz bir isteğin gövdesine bakılmaz; istek `401` ile reddedilir.
5. İşlem kimliği doğruluyordu, ama yorumun isteği gönderen kullanıcıya ait olup olmadığına bakmıyordu: Giriş yapan her kullanıcı her yorumu değiştirebiliyordu. Ece'nin kendi yorumunu değiştiren bir test, kural olsa da olmasa da geçer. Açığı yalnızca başka bir kullanıcının, Can'in isteğini gönderen bir test görür.
6. İkisi de FastAPI'nin bağımlılığı fonksiyondan önce çalıştırmasını sağlar. Parametre olarak yazılan bağımlılığın sonucu, yani kullanıcı, fonksiyona verilir. Dekoratöre yazılanın sonucu fonksiyona verilmez; fonksiyonun kullanıcıya ihtiyacı olmadığında kullanılır.
7. Yanıt modeli yoktu. FastAPI kullanıcıların bütün alanlarını, parola özetleri dahil, yanıta koydu. `response_model=list[UserPublic]` satırı yanıtı yalnızca `id` ve `username` alanlarıyla sınırladı.

---

## 8. Resmî belgeler

- [FastAPI — Dependencies in path operation decorators](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/): `dependencies=[...]` bu sayfada.
- [FastAPI — Sub-dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/): Bir bağımlılığın başka bir bağımlılığı kullanması.
- [FastAPI — Response Model](https://fastapi.tiangolo.com/tutorial/response-model/): Yanıt modelinin veriyi süzmesi bu sayfada.
- [OWASP — API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/): Bu haftanın üç açığı listenin ilk beş sırasında ([ek not](03_Supplement_API_Security_Risks.md)).
- [OWASP — Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html): "Varsayılan olarak reddet" ilkesi bu sayfada.
- [Python — datetime](https://docs.python.org/3/library/datetime.html): 6.3 alıştırması için `datetime` ve `timedelta`.

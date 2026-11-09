# Hafta 09 — Uygulama Föyü

## 0. Bu isteği kim gönderdi?

Şu an kataloğumuza herkes, herkesin adıyla yorum yazabiliyor. Hafta 8'in sonundaki sunucuyla şu isteği gönderelim:

```python
from fastapi.testclient import TestClient

from database import reset_database
from server import app

client = TestClient(app)

reset_database()

review = {"reader": "Ece", "comment": "Hiç beğenmedim.", "score": 1}
response = client.post("/books/73/reviews", json=review)
print(response.status_code, response.json())
```

```text
201 {'reader': 'Ece', 'comment': 'Hiç beğenmedim.', 'score': 1, 'id': 2, 'book_id': 73}
```

Bu isteği Ece göndermemiş olabilir. Sunucu bunu bilemez: İstekte gönderenin kim olduğunu kanıtlayan hiçbir şey yok; okurun adı gövdede, ve gövdeye herkes istediğini yazabilir.

Bu hafta iki soruyu birbirinden ayıracağız:

| Soru | Adı | Cevap verilmezse |
|---|---|---|
| "Bu isteği gönderen kim?" | **Kimlik doğrulama (authentication)** | `401 Unauthorized`: Sunucu seni tanımıyor. |
| "Bu kişi bu işlemi yapabilir mi?" | **Yetkilendirme (authorization)** | `403 Forbidden`: Sunucu seni tanıyor, ama bu işlemi yapamazsın. |

Kimliği kanıtlamanın bilinen yolu parola. Ama parolayı her isteğe eklemek istemeyiz. Bunun yerine istemci bir kez **giriş (login)** yapar: Kullanıcı adını ve parolasını gönderir. Sunucu parolayı doğrularsa istemciye rastgele üretilmiş uzun bir metin verir: **token**. İstemci sonraki her isteğe bu tokeni ekler. Token, "giriş yapmış olan bu kullanıcıyım" demenin kanıtıdır; bir tür geçici anahtar.

Haftanın sonunda şu soruya cevap verebileceksin: **Sunucu, bir isteği kimin gönderdiğini nasıl bilir; bir kaydı yalnızca sahibinin değiştirmesini nasıl sağlar?**

Bu hafta sırasıyla şunları yapacağız:

- **Deney 1:** Kullanıcı tablosunu eklemek; parolanın kendisini değil özetini saklamak
- **Deney 2:** Giriş yapıp token almak; tokenle "ben kimim?" sorusunu sormak
- **Deney 3:** Yorum yazmayı korumak; okurun adını gövdeden değil tokenden almak
- **Deney 4:** Yorum silme işlemi: yalnızca yorumu yazan silebilsin
- **Deney 5:** Testleri yeni kurallara göre güncellemek

### 0.1 Başlangıç dosyaları

Hafta 8'in sonundaki dosyalarla başla: `server.py`, `database.py`, `reset_db.py` ve on iki testli `test_server.py`.

Bu hafta iki **hazır dosya** ekliyoruz. Bunları sıfırdan yazmayacağız; ne yaptıklarını okuyup kullanacağız:

| Dosya | Görevi |
|---|---|
| [passwords.py](Starting_Code/passwords.py) | Parolanın özetini üretir ve gönderilen parolayı kayıtlı özetle karşılaştırır. |
| [auth.py](Starting_Code/auth.py) | Bir isteğin tokeninden, isteği gönderen kullanıcıyı bulur. |

İki dosyayı [başlangıç klasöründen](Starting_Code/) alıp `server.py` ile aynı klasöre koy. Kendi dosyalarından emin değilsen öteki dosyaları da oradan al: [server.py](Starting_Code/server.py), [database.py](Starting_Code/database.py), [reset_db.py](Starting_Code/reset_db.py), [test_server.py](Starting_Code/test_server.py). Föydeki çıktılar bu dosyalarla alındı.

> **Hafta 8'in ödevini yaptıysan:** 6.2 ve 6.3 alıştırmalarının testleri dosyanda kalabilir. Yorum gönderen testleri Deney 5'te ötekilerle birlikte güncelleyeceğiz.

### 0.2 Veritabanını başlat

```bash
docker start book-db
```

Yeni paket kurmuyoruz: Parola özeti ve token için Python'un kendi `hashlib` ve `secrets` modüllerini, tokeni istekten okumak için FastAPI'nin kendi parçalarını kullanacağız.

---

## Deney 1 — Kullanıcılar: parolanın kendisi değil, özeti

**Amaç:** Kullanıcıları veritabanına eklemek ve parolanın neden olduğu gibi saklanmadığını görmek.

### 1.1 Parolayı neden olduğu gibi saklamıyoruz?

Veritabanı bir gün başkasının eline geçebilir: Bir yedek dosyası yanlış yere konur, bir sunucuya izinsiz girilir. Parolalar tabloda olduğu gibi duruyorsa, o kişi bütün kullanıcıların parolalarını okur. İnsanlar aynı parolayı birçok yerde kullandığı için zarar yalnızca bizim kataloğumuzla da sınırlı kalmaz.

Bu yüzden parolanın kendisini değil, **özetini (hash)** saklarız. Özet, bir metinden hesaplanan ve şu özellikleri olan bir değerdir:

- Aynı metin her seferinde aynı özeti verir. Bu sayede girişte gönderilen parolanın özetini hesaplayıp kayıtlı özetle karşılaştırabiliriz.
- Özetten metne geri dönülemez. Tabloyu okuyan biri parolaları göremez.

### 1.2 `passwords.py`

Hazır dosyayı aç:

```python
import hashlib
import secrets


# Parolanın özetini üretir. Tuz her parola için rastgele seçilir ve özetin başına yazılır.
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return salt + "$" + digest.hex()


# Gönderilen parolayı, kayıtlı özetteki tuzla yeniden özetler ve iki özeti karşılaştırır.
def verify_password(password, password_hash):
    salt = password_hash.split("$")[0]
    return secrets.compare_digest(hash_password(password, salt), password_hash)
```

| Kod | Ne yapar? |
|---|---|
| `secrets.token_hex(16)` | Rastgele, 32 karakterlik bir metin üretir. `secrets` modülü, tahmin edilmesi zor olması gereken değerler için yazılmıştır. |
| `salt` | **Tuz (salt):** Parolaya özetlenmeden önce eklenen rastgele metin. İki kullanıcının parolası aynı olsa bile tuzları farklı olduğu için özetleri farklı olur. |
| `hashlib.pbkdf2_hmac("sha256", ..., 100_000)` | Parolayı ve tuzu birlikte özetler. Son sayı, özetleme işleminin kaç kez tekrarlanacağı: Özetlemeyi **bilerek yavaşlatır**. Doğru parolayı bilen biri için bu yavaşlık fark edilmez; milyonlarca parolayı deneyerek özeti tutturmaya çalışan biri için iş çok uzar. |
| `salt + "$" + digest.hex()` | Kaydedilecek değer: tuz, ayırıcı `$` ve özet. Tuzun gizli olması gerekmez; doğrulama için tuzu bilmemiz gerekir. |
| `password_hash.split("$")[0]` | Kayıtlı değerden tuzu, yani `$` işaretinden önceki kısmı alır. |
| `secrets.compare_digest(a, b)` | İki metni karşılaştırır. `a == b` ile aynı sonucu verir, ama karşılaştırmanın süresi metinlerin nerede farklılaştığını ele vermez. |

Gerçek projelerde bu iş için hazır paketler kullanılır; [ek notta](03_Supplement_Password_Hashing.md) bu dosyanın neyi basit tuttuğunu ve hazır paketlerin neden tercih edildiğini görebilirsin.

### 1.3 Kullanıcı tablosu

`database.py` dosyasında import satırlarının altına şu satırı ekle:

```python
from passwords import hash_password
```

`Book` sınıfı ile `Review` sınıfının arasına iki tablo modeli ekle:

```python
# Kullanıcı tablosu: parolanın kendisi değil, özeti saklanır.
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    password_hash: str


# Token tablosu: her token bir kullanıcıya aittir; kullanıcı silinince tokenleri de silinir.
class Token(SQLModel, table=True):
    value: str = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
```

| Kod | Ne yapar? |
|---|---|
| `__tablename__ = "users"` | Tablonun adını belirler. SQLModel, tabloya sınıfın adını küçük harfle verir: `book`, `review`. Ama `user`, PostgreSQL'de ayrılmış bir kelime: `SELECT * FROM user` komutu tabloyu değil, veritabanına bağlı olan kullanıcıyı gösterir. Karışıklığı önlemek için tabloya `users` adını veriyoruz. |
| `username: str = Field(unique=True)` | Kullanıcı adları **tekil (unique)** olmalı: Veritabanı, aynı kullanıcı adıyla ikinci bir kaydı reddeder. |
| `class Token` | Verilen tokenleri saklar. Tokenin kendisi tablonun birincil anahtarı (`value`); her token bir kullanıcıya bağlı (`user_id`). Hafta 6'da yorumları kitaplara bağladığımız yabancı anahtarın aynısı. |

`Review` modeline, yorumu yazan kullanıcıyı gösteren bir alan ekle. Açıklama satırını da güncelle:

```python
# Yorum tablosu: her yorum bir kitaba ve onu yazan kullanıcıya bağlı; kitap silinince yorumları da silinir.
class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id", ondelete="CASCADE")
    user_id: int = Field(foreign_key="users.id")
    reader: str
    comment: str
    score: int
```

`reader` alanı kalıyor: Yanıtlarda okurun adını göstermeye devam edeceğiz. Ama yorumun **sahibi** artık `user_id`. Ad değişebilir ya da iki kişi aynı adı kullanabilir; kimlik değişmez.

### 1.4 Başlangıç kullanıcıları

`database.py` dosyasındaki `reset_database` fonksiyonunda `session.add(Review(` ile başlayan bloğu, yani Ece'nin yorumunu ekleyen satırları, şunlarla değiştir. Önce iki kullanıcı ekleniyor, sonra Ece'nin yorumu `user_id=1` ile yazılıyor:

```python
        session.add(User(username="Ece", password_hash=hash_password("ece-parola")))
        session.add(User(username="Can", password_hash=hash_password("can-parola")))
        session.commit()

        session.add(Review(
            id=1,
            book_id=42,
            user_id=1,
            reader="Ece",
            comment="Konuları örneklerle anlatıyor.",
            score=5,
        ))
```

Kullanıcılara kimlik vermedik: Veritabanı onları sırayla `1` ve `2` olarak numaralandırır. Ece'nin yorumu `user_id=1` ile ona bağlanabilsin diye kullanıcıları yorumdan önce ayrı bir `commit` ile yazıyoruz.

`reset_db.py` dosyasının son satırını güncelle:

```python
print("Database reset: 3 books, 1 review, 2 users")
```

Çalıştır:

```bash
python reset_db.py
```

```text
Database reset: 3 books, 1 review, 2 users
```

### 1.5 Tabloya bak

```bash
docker exec book-db psql -U student -d catalog -c "SELECT * FROM users;"
```

```text
 id | username |                                           password_hash
----+----------+---------------------------------------------------------------------------------------------------
  1 | Ece      | 0cfb564b094c5e7e81519b0fb4897b4a$01abfbd39e31a87b2d127526b85fb87af4951b08d3c6a3272c8f0c1675b44288
  2 | Can      | 2a211fd450971c741c3f139fdbe12b6e$52715424c84aacd5464a78cd489b9a9f415c618ba31b459a0d9823d05093ca1f
(2 rows)
```

Tabloda parolalar yok. `$` işaretinden önceki 32 karakter tuz, sonraki 64 karakter özet. Senin tablonda bu değerler farklı olur: Tuz her sıfırlamada yeniden, rastgele seçiliyor. `python reset_db.py` komutunu bir kez daha çalıştırıp tabloya yeniden bakarsan, parolalar değişmediği hâlde özetlerin değiştiğini görürsün.

> **Ana fikir:** Parolanın kendisi değil, tuzla birlikte hesaplanmış özeti saklanır. Özetten parolaya geri dönülemez; girişte gönderilen parola aynı tuzla yeniden özetlenir ve kayıtlı özetle karşılaştırılır. Kayıtların sahibini adıyla değil, değişmeyen kimliğiyle (`user_id`) tutarız.

---

## Deney 2 — Giriş ve token

**Amaç:** Kullanıcı adı ve parolayla giriş yapıp token almak; tokenle gönderilen bir istekten kullanıcıyı bulmak.

### 2.1 Giriş işlemi

`server.py` dosyasının import satırlarını şöyle değiştir:

```python
import secrets

from fastapi import Depends, FastAPI, HTTPException, Path, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import Session, select

from auth import get_current_user
from database import Book, Review, Token, User, engine
from passwords import verify_password
```

`ReviewPublic` modelinin altına iki model ekle:

```python
class LoginData(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    username: str
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
```

`LoginData` giriş isteğinin gövdesi; `UserPublic` ise bir kullanıcıyı yanıtta gösterirken kullanacağımız yanıt modeli. `UserPublic` modelinde `password_hash` alanı yok: Hafta 4'te `internal_note` alanını yanıtlardan gizlediğimiz gibi, parolanın özeti de hiçbir yanıtta görünmemeli.

Dosyanın sonuna giriş işlemini ekle:

```python
# Giriş: kullanıcı adı ve parola doğruysa yeni bir token üretir; değilse 401.
@app.post("/login")
def login(login_data: LoginData):
    with Session(engine) as session:
        statement = select(User).where(User.username == login_data.username)
        user = session.exec(statement).first()

        if user is None or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Wrong username or password")

        token = Token(value=secrets.token_hex(16), user_id=user.id)
        session.add(token)
        session.commit()
        return {"access_token": token.value, "token_type": "bearer"}
```

| Kod | Ne yapar? |
|---|---|
| `select(User).where(User.username == ...)` | Kullanıcıyı adıyla bulur. Hafta 6'da yorumları okurun adıyla bulduğumuz sorgunun aynısı. |
| `if user is None or not verify_password(...)` | Kullanıcı yoksa ya da parola yanlışsa aynı yanıtı verir. İki durum için ayrı açıklamalar yazsaydık, istemci hangi kullanıcı adlarının kayıtlı olduğunu öğrenebilirdi. |
| `Token(value=secrets.token_hex(16), ...)` | Rastgele bir token üretir ve kullanıcıya bağlar. Tahmin edilemez olması gerekir: Tokeni tahmin eden biri o kullanıcı olur. |
| `{"access_token": ..., "token_type": "bearer"}` | Yanıt. `bearer` "taşıyıcı" demek: Bu tokeni taşıyan, kullanıcı sayılır. Alan adları, token veren servislerin ortak kullandığı adlar. |

### 2.2 "Ben kimim?" işlemi

Giriş yapan kullanıcının kendisini görebileceği bir işlem ekleyelim. Önce hazır `auth.py` dosyasını oku:

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from database import Token, User, engine

bearer = HTTPBearer()


# İsteği gönderen kullanıcıyı bulur: Authorization başlığındaki tokeni veritabanında arar; yoksa 401.
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    with Session(engine) as session:
        token = session.get(Token, credentials.credentials)

        if token is None:
            raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})

        return session.get(User, token.user_id)
```

| Kod | Ne yapar? |
|---|---|
| `HTTPBearer()` | İsteğin `Authorization` başlığını okuyan bir FastAPI parçası. Başlık `Bearer <token>` biçiminde olmalı. Başlık yoksa ya da biçimi yanlışsa isteği kendisi `401` ile reddeder. |
| `Depends(bearer)` | **Bağımlılık (dependency):** "Bu parametrenin değerini `bearer` üretsin." FastAPI, fonksiyonu çağırmadan önce `bearer` parçasını çalıştırır ve sonucunu `credentials` parametresine verir. |
| `credentials.credentials` | Başlıktaki tokenin kendisi: `Bearer ` kısmından sonrası. |
| `session.get(Token, ...)` | Tokeni veritabanında arar. Böyle bir token hiç verilmediyse `None` gelir ve istek `401` alır. |
| `headers={"WWW-Authenticate": "Bearer"}` | `401` yanıtının başlığı: İstemciye "kimliğini `Bearer` tokeniyle kanıtla" der. HTTP, `401` yanıtlarında bu başlığı ister. |
| `return session.get(User, token.user_id)` | Tokenin sahibi olan kullanıcıyı döndürür. |

`server.py` dosyasının sonuna şu işlemi ekle:

```python
# Giriş yapan kullanıcı: tokenin sahibini döner; token yoksa ya da geçersizse 401.
@app.get("/me", response_model=UserPublic)
def read_me(user: User = Depends(get_current_user)):
    return user
```

`user: User = Depends(get_current_user)`, Hafta 8'deki sırayla şu demek: FastAPI, 2. adımda, yani parametreleri hazırlarken `get_current_user` fonksiyonunu çalıştırır. O da önce `bearer` parçasını çalıştırır. Token yoksa ya da geçersizse istek orada `401` alır ve `read_me` hiç çalışmaz. Token geçerliyse `read_me`, kullanıcıyı `user` parametresinde hazır bulur.

### 2.3 curl ile dene

Bu deneyde tokeni kendi gözümüzle görmek için gerçek sunucuyu kullanacağız. Sunucuyu başlat:

```bash
python -m uvicorn server:app
```

İkinci bir terminalde Ece olarak giriş yap. `-i` seçeneği yanıtın başlıklarını da gösterir (Hafta 4, 5.1):

```bash
curl -i -X POST http://127.0.0.1:8000/login -H "Content-Type: application/json" -d '{"username": "Ece", "password": "ece-parola"}'
```

```text
HTTP/1.1 200 OK
date: Mon, 09 Nov 2026 15:10:10 GMT
server: uvicorn
content-length: 73
content-type: application/json

{"access_token":"e50df99d83cc2434ceff3dab9e318691","token_type":"bearer"}
```

Senin tokenin farklı olacak: Her giriş yeni, rastgele bir token üretir. Aşağıdaki komutlarda `TOKEN` yazan yere kendi tokenini koy.

Yanlış parolayla:

```bash
curl -i -X POST http://127.0.0.1:8000/login -H "Content-Type: application/json" -d '{"username": "Ece", "password": "yanlis"}'
```

```text
HTTP/1.1 401 Unauthorized
date: Mon, 09 Nov 2026 15:10:10 GMT
server: uvicorn
content-length: 39
content-type: application/json

{"detail":"Wrong username or password"}
```

Şimdi `/me` adresini üç kez iste: tokensiz, kendi tokeninle ve uydurma bir tokenle.

```bash
curl -i http://127.0.0.1:8000/me
```

```text
HTTP/1.1 401 Unauthorized
date: Mon, 09 Nov 2026 15:10:10 GMT
server: uvicorn
www-authenticate: Bearer
content-length: 30
content-type: application/json

{"detail":"Not authenticated"}
```

```bash
curl -i http://127.0.0.1:8000/me -H "Authorization: Bearer TOKEN"
```

```text
HTTP/1.1 200 OK
date: Mon, 09 Nov 2026 15:10:10 GMT
server: uvicorn
content-length: 25
content-type: application/json

{"id":1,"username":"Ece"}
```

```bash
curl -i http://127.0.0.1:8000/me -H "Authorization: Bearer 1234"
```

```text
HTTP/1.1 401 Unauthorized
date: Mon, 09 Nov 2026 15:10:10 GMT
server: uvicorn
www-authenticate: Bearer
content-length: 26
content-type: application/json

{"detail":"Invalid token"}
```

| İstek | Yanıt | Kim reddetti? |
|---|---|---|
| Tokensiz | `401`, `Not authenticated` | `HTTPBearer`: `Authorization` başlığı yok. |
| Ece'nin tokeniyle | `200`, Ece'nin kimliği ve adı | Reddedilmedi. Sunucu, kullanıcıyı gövdeden ya da adresten değil, yalnızca tokenden buldu. |
| `1234` tokeniyle | `401`, `Invalid token` | `get_current_user`: Başlığın biçimi doğru, ama böyle bir token verilmemiş. |

Verilen tokenler veritabanında duruyor:

```bash
docker exec book-db psql -U student -d catalog -c "SELECT * FROM token;"
```

```text
              value               | user_id
----------------------------------+---------
 e50df99d83cc2434ceff3dab9e318691 |       1
(1 row)
```

Tabloda tek token var: Ece'nin başarılı girişinde üretilen token. Yanlış parolalı deneme token üretmedi. Ece bir kez daha giriş yapsaydı tabloya ikinci bir satır eklenirdi; iki token da ayrı ayrı geçerli olurdu.

`http://127.0.0.1:8000/docs` sayfasında sağ üstte **Authorize** adlı bir düğme belirdi. Tokenini oraya yapıştırırsan, sayfadan gönderdiğin isteklere `Authorization` başlığı eklenir. Sunucuyu **Ctrl+C** ile durdur.

> **Ana fikir:** İstemci kullanıcı adı ve parolayı yalnızca girişte gönderir ve karşılığında bir token alır. Sonraki isteklerde tokeni `Authorization: Bearer <token>` başlığıyla gönderir. Sunucu, bağımlılık (`Depends`) olarak yazılan `get_current_user` ile tokenden kullanıcıyı bulur; token yoksa ya da tanınmıyorsa istek, işlemin fonksiyonu çalışmadan `401` alır.

---

## Deney 3 — Yorumu kim yazdı?

**Amaç:** Yorum yazma işlemini giriş yapmış kullanıcılara açmak ve okurun adını tokenden almak.

### 3.1 Okur artık gövdede değil

`ReviewCreate` ve `ReviewPublic` modellerini şöyle değiştir:

```python
class ReviewCreate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    comment: str = Field(min_length=1)
    score: int = Field(ge=1, le=5)


class ReviewPublic(ReviewCreate):
    model_config = ConfigDict(strict=False, extra="ignore")

    id: int
    book_id: int
    reader: str
```

`reader` alanı istek modelinden çıktı ve yalnızca yanıt modelinde kaldı. İstemci okurun adını artık gönderemez: `extra="forbid"` olduğu için `reader` gönderen istek `422` alır. Okurun adını sunucu, tokenden bulduğu kullanıcıdan yazacak.

### 3.2 `create_review` fonksiyonu

`create_review` fonksiyonunu şöyle değiştir:

```python
# Yeni yorum: giriş yapan kullanıcının adıyla ekler, 201 döner; kitap yoksa 404, kullanıcının bu kitaba yorumu varsa 409.
@app.post("/books/{book_id}/reviews", status_code=201, response_model=ReviewPublic)
def create_review(review_data: ReviewCreate, book_id: int = Path(gt=0), user: User = Depends(get_current_user)):
    with Session(engine) as session:
        if session.get(Book, book_id) is None:
            raise HTTPException(status_code=404, detail="Book not found")

        statement = select(Review).where(Review.book_id == book_id).where(Review.user_id == user.id)
        if session.exec(statement).first() is not None:
            raise HTTPException(status_code=409, detail="This reader has already reviewed this book")

        new_review = review_data.model_dump()
        new_review["book_id"] = book_id
        new_review["user_id"] = user.id
        new_review["reader"] = user.username
        review = Review.model_validate(new_review)
        session.add(review)
        session.commit()
        session.refresh(review)
        return review
```

| Değişen | Neden? |
|---|---|
| `user: User = Depends(get_current_user)` | Yorum yazmak artık giriş gerektiriyor. `/me` işlemindeki parametrenin aynısı. |
| `.where(Review.user_id == user.id)` | "Bu okur bu kitaba yorum yazmış mı?" sorusu artık ada değil, kimliğe bakıyor. |
| `new_review["user_id"] = user.id` ve `new_review["reader"] = user.username` | Yorumun sahibi ve okurun adı, gövdeden değil tokenden bulunan kullanıcıdan geliyor. |

### 3.3 Dene

`server.py` ile aynı klasörde `review_client.py` dosyasını oluştur. Giriş yapıp `Authorization` başlığını hazırlayan küçük bir fonksiyon, istekleri kısaltıyor:

```python
from fastapi.testclient import TestClient

from database import reset_database
from server import app

client = TestClient(app)


# Kullanıcı adına giriş yapar ve isteklere eklenecek Authorization başlığını döner.
def login_as(username, password):
    response = client.post("/login", json={"username": username, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": "Bearer " + token}


reset_database()

ece = login_as("Ece", "ece-parola")
can = login_as("Can", "can-parola")
review = {"comment": "Örnekleri çalıştırdım.", "score": 4}

response = client.post("/books/73/reviews", json=review)
print("1: no token:   ", response.status_code, response.json())

response = client.post("/books/73/reviews", json=review, headers=can)
print("2: Can:        ", response.status_code, response.json())

response = client.post("/books/73/reviews", json=review, headers=ece)
print("3: Ece:        ", response.status_code, response.json())

response = client.post("/books/73/reviews", json=review, headers=ece)
print("4: Ece again:  ", response.status_code, response.json())

fake = {"reader": "Ece", "comment": "Hiç beğenmedim.", "score": 1}
response = client.post("/books/57/reviews", json=fake, headers=can)
print("5: Can as Ece: ", response.status_code, response.json()["detail"][0]["msg"])
```

| Kod | Ne yapar? |
|---|---|
| `login_as("Ece", "ece-parola")` | Ece olarak giriş yapar ve `{"Authorization": "Bearer <token>"}` sözlüğünü döner. |
| `headers=can` | İsteğe Can'in `Authorization` başlığını ekler. Hafta 2'den beri yanıtın başlıklarını okuyorduk; bu kez isteğe biz başlık ekliyoruz. |

Çalıştır:

```bash
python review_client.py
```

```text
1: no token:    401 {'detail': 'Not authenticated'}
2: Can:         201 {'comment': 'Örnekleri çalıştırdım.', 'score': 4, 'id': 2, 'book_id': 73, 'reader': 'Can'}
3: Ece:         201 {'comment': 'Örnekleri çalıştırdım.', 'score': 4, 'id': 3, 'book_id': 73, 'reader': 'Ece'}
4: Ece again:   409 {'detail': 'This reader has already reviewed this book'}
5: Can as Ece:  422 Extra inputs are not permitted
```

| No | Ne oldu? |
|---|---|
| 1 | Tokensiz yorum reddedildi. Gövde ve kitap doğru; ama gönderen bilinmiyor. |
| 2 ve 3 | İki istek aynı gövdeyi gönderdi, ama yorumların okurları farklı: Okurun adı gövdeden değil, tokenden geldi. |
| 4 | Ece'nin bu kitaba ikinci yorumu `409` aldı. Kontrol artık Ece'nin kimliğine (`user_id`) bakıyor. |
| 5 | Can, gövdeye `"reader": "Ece"` yazarak Ece'nin adıyla yorum yazmaya çalıştı. `reader` artık istek modelinde olmadığı için istek reddedildi. 0. bölümdeki sorun kapandı. |

> **Ana fikir:** Kimlik bilgisi, istemcinin istediğini yazabildiği gövdeden alınmaz; sunucunun doğruladığı tokenden alınır. Bir işlemi korumak için fonksiyona `Depends(get_current_user)` parametresi eklemek yeter: Tokensiz istek `401` alır ve fonksiyon, isteği gönderen kullanıcıyı parametrede hazır bulur.

---

## Deney 4 — Kaydın sahibi

**Amaç:** Bir yorumu yalnızca onu yazan kullanıcının silebilmesini sağlamak; `401` ile `403` yanıtlarını ayırmak.

### 4.1 Yorum silme işlemi

Tek bir yorumu silen `delete_review` fonksiyonunu Hafta 4'ün 5.3 alıştırmasında yazmış, Hafta 6'nın 8.2 alıştırmasında veritabanına taşımıştık. Ana koda eklemediğimiz için başlangıç dosyalarında yok. `server.py` dosyasında `create_review` fonksiyonunun altına şu işlemi ekle; alıştırmadan kalan bir `delete_review` fonksiyonun varsa onu bununla değiştir:

```python
# Yorumu silme: yalnızca yorumu yazan kullanıcı silebilir; yorum yoksa 404, başkasının yorumuysa 403.
@app.delete("/books/{book_id}/reviews/{review_id}", status_code=204)
def delete_review(book_id: int = Path(gt=0), review_id: int = Path(gt=0), user: User = Depends(get_current_user)):
    with Session(engine) as session:
        review = session.get(Review, review_id)

        if review is None or review.book_id != book_id:
            raise HTTPException(status_code=404, detail="Review not found")

        if review.user_id != user.id:
            raise HTTPException(status_code=403, detail="You can only delete your own reviews")

        session.delete(review)
        session.commit()
```

| Kod | Ne yapar? |
|---|---|
| `/books/{book_id}/reviews/{review_id}` | Tek bir yorumun adresi: Hafta 3'teki iç içe kaynak adresi. |
| `review.book_id != book_id` | Yorum var, ama adresteki kitabın yorumu değilse de `404`: `/books/57/reviews/1` adresinde bir yorum yok, çünkü 1 numaralı yorum 42 numaralı kitabın. Alıştırmadaki fonksiyonun bu kısmı aynı. |
| `user: User = Depends(get_current_user)` ve `review.user_id != user.id` | Yeni olan kısım. Yorumun sahibi, isteği gönderen kullanıcı değilse `403`. Bu, bu haftanın ilk **yetkilendirme** kuralı: Kullanıcı tanınıyor, ama bu işlemi yapamaz. |

Kontrollerin sırasına dikkat: Önce yorumun var olup olmadığına, sonra sahibine bakıyoruz. Olmayan bir yorumun sahibi sorulamaz (Hafta 8, kontrollerin sırası).

### 4.2 Dene

`delete_client.py` dosyasını oluştur. Baştaki satırlar ve `login_as` fonksiyonu `review_client.py` dosyasındakiyle aynı:

```python
from fastapi.testclient import TestClient

from database import reset_database
from server import app

client = TestClient(app)


# Kullanıcı adına giriş yapar ve isteklere eklenecek Authorization başlığını döner.
def login_as(username, password):
    response = client.post("/login", json={"username": username, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": "Bearer " + token}


reset_database()

ece = login_as("Ece", "ece-parola")
can = login_as("Can", "can-parola")

response = client.delete("/books/42/reviews/1")
print("1: no token:  ", response.status_code, response.json())

response = client.delete("/books/42/reviews/1", headers=can)
print("2: Can:       ", response.status_code, response.json())

response = client.delete("/books/42/reviews/9", headers=ece)
print("3: no review: ", response.status_code, response.json())

response = client.delete("/books/42/reviews/1", headers=ece)
print("4: Ece:       ", response.status_code)

response = client.get("/books/42/reviews")
print("5: reviews:   ", response.status_code, response.json())
```

```bash
python delete_client.py
```

```text
1: no token:   401 {'detail': 'Not authenticated'}
2: Can:        403 {'detail': 'You can only delete your own reviews'}
3: no review:  404 {'detail': 'Review not found'}
4: Ece:        204
5: reviews:    200 []
```

| No | Yanıt | Sunucunun cevabı |
|---|---|---|
| 1 | `401` | "Seni tanımıyorum." Gönderen kim, bilinmiyor. |
| 2 | `403` | "Seni tanıyorum, Can; ama bu yorum senin değil." |
| 3 | `404` | "Böyle bir yorum yok." |
| 4 | `204` | Yorum, sahibi Ece tarafından silindi. |
| 5 | `200`, `[]` | 42 numaralı kitabın yorumu kalmadı. Yorumları okumak giriş gerektirmiyor: Herkes okuyabilir. |

`401` ile `403` arasındaki fark, ilk adı yanıltıcı olsa da şöyle: `401 Unauthorized` aslında "kimliğin doğrulanmadı" demek; `403 Forbidden` ise "kimliğin belli, ama izin yok". `401` alan bir istemci giriş yapıp tekrar deneyebilir; `403` alan istemcinin tekrar denemesi bir şey değiştirmez.

> **Ana fikir:** Kimlik doğrulama "kim?" sorusuna, yetkilendirme "yapabilir mi?" sorusuna cevap verir. Kimliği belirsiz istek `401`, kimliği belli ama izni olmayan istek `403` alır. Bir kaydın sahibi olup olmadığını, kayıttaki `user_id` ile tokenden bulunan kullanıcının kimliğini karşılaştırarak anlarız.

---

## Deney 5 — Testleri güncelle

**Amaç:** API'deki bir değişikliğin hangi testleri bozduğunu görmek; testleri yeni kurallara göre güncellemek ve yeni kurallar için test yazmak.

### 5.1 Hangi test kaldı?

`review_client.py` ve `delete_client.py` dosyalarını sil; bundan sonra aynı istekleri testler gönderecek. Testleri `--tb=short` ile çalıştır:

```bash
python -m pytest --tb=short
```

```text
test_server.py ........F...                                              [100%]

=================================== FAILURES ===================================
_________________________ test_second_review_conflict __________________________
test_server.py:107: in test_second_review_conflict
    assert response.status_code == 409
E   assert 401 == 409
E    +  where 401 = <Response [401 Unauthorized]>.status_code
=========================== short test summary info ============================
FAILED test_server.py::test_second_review_conflict - assert 401 == 409
========================= 1 failed, 11 passed in 3.51s =========================
```

Bu sefer test bir hata yakalamadı; API bilerek değişti. Test, eski kuralı ("herkes yorum yazabilir") kontrol ediyordu. Hafta 7'deki iki olasılıktan ikincisi: Beklenti yanlış, yani test güncellenmeli.

Testin gövdesinde hâlâ `"reader": "Ece"` var, ama yanıt `422` değil `401` oldu. Token kontrolü bir bağımlılık olduğu için gövdeden önce yapıldı: Kimliği belirsiz bir isteğin gövdesine bakılmadı.

Testlerin süresi de uzadı: Hafta 8'de iki saniyenin altındaydı, şimdi üç buçuk saniye. Her testten önce çalışan `reset_database()` artık iki parolayı özetliyor ve özetleme bilerek yavaş (1.2).

### 5.2 `login_as` fonksiyonunu teste taşı

`test_server.py` dosyasında `new_book` sözlüğünün altına, `fresh_database` fonksiyonunun üstüne `login_as` fonksiyonunu ekle. `review_client.py` dosyasındakinin aynısı:

```python
# Kullanıcı adına giriş yapar ve isteklere eklenecek Authorization başlığını döner.
def login_as(username, password):
    response = client.post("/login", json={"username": username, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": "Bearer " + token}
```

Adı `test_` ile başlamadığı için pytest onu bir test olarak çalıştırmaz; testler onu çağırır.

`test_second_review_conflict` testini şöyle değiştir:

```python
# Yorum: aynı okur aynı kitaba ikinci kez yorum yazamaz.
def test_second_review_conflict():
    review = {"comment": "Tekrar okudum.", "score": 4}

    response = client.post("/books/42/reviews", json=review, headers=login_as("Ece", "ece-parola"))

    assert response.status_code == 409
```

> **Hafta 7 ve Hafta 8 ödevlerinin testleri:** Yorum gönderen başka testlerin varsa (`test_create_review`, `test_review_for_missing_book`, `test_review_other_book`), onları da aynı şekilde değiştir: Gövdeden `reader` alanını çıkar, isteğe okurun `login_as` başlığını ekle. Can için parola `can-parola`.

### 5.3 Yeni kurallar için testler

Dosyanın sonuna dört test ekle:

```python
# Giriş: yanlış parola 401 alır.
def test_login_wrong_password():
    response = client.post("/login", json={"username": "Ece", "password": "yanlis"})

    assert response.status_code == 401


# Yorum: token olmadan yazılamaz.
def test_review_requires_login():
    review = {"comment": "Kısa ve açık.", "score": 4}

    response = client.post("/books/73/reviews", json=review)

    assert response.status_code == 401


# Yorum: okurun adı tokenden gelir.
def test_reader_comes_from_token():
    review = {"comment": "Kısa ve açık.", "score": 4}

    response = client.post("/books/73/reviews", json=review, headers=login_as("Can", "can-parola"))

    assert response.status_code == 201
    assert response.json()["reader"] == "Can"


# Yorum silme: başkasının yorumu silinemez; yorum yerinde kalır.
def test_delete_other_users_review():
    response = client.delete("/books/42/reviews/1", headers=login_as("Can", "can-parola"))
    assert response.status_code == 403

    response = client.get("/books/42/reviews")
    assert len(response.json()) == 1
```

Son test, Hafta 7'deki `test_patch_null_title` gibi iki şeyi kontrol ediyor: Yanıt `403` ve yorum gerçekten silinmemiş. Bir yetki kontrolünün yalnızca doğru durum kodunu vermesi yetmez; işlemin yapılmadığından da emin olmalıyız.

Testleri `-v` ile çalıştır:

```text
collecting ... collected 16 items

test_server.py::test_get_book PASSED                                     [  6%]
test_server.py::test_get_missing_book PASSED                             [ 12%]
test_server.py::test_create_book PASSED                                  [ 18%]
test_server.py::test_search_books PASSED                                 [ 25%]
test_server.py::test_rating_out_of_range PASSED                          [ 31%]
test_server.py::test_negative_book_id PASSED                             [ 37%]
test_server.py::test_patch_rating PASSED                                 [ 43%]
test_server.py::test_patch_null_title PASSED                             [ 50%]
test_server.py::test_second_review_conflict PASSED                       [ 56%]
test_server.py::test_delete_book_deletes_reviews PASSED                  [ 62%]
test_server.py::test_filter_not_available PASSED                         [ 68%]
test_server.py::test_replace_book PASSED                                 [ 75%]
test_server.py::test_login_wrong_password PASSED                         [ 81%]
test_server.py::test_review_requires_login PASSED                        [ 87%]
test_server.py::test_reader_comes_from_token PASSED                      [ 93%]
test_server.py::test_delete_other_users_review PASSED                    [100%]

============================== 16 passed in 4.55s ==============================
```

> **Ana fikir:** API bilerek değiştiğinde eski kuralı kontrol eden testler kalır; bu bir hata değil, testlerin güncellenmesi gerektiğinin işaretidir. Yetki kurallarını test ederken hem durum koduna hem de işlemin gerçekten yapılmadığına bakarız.

---

## 6. Bu haftanın sonundaki dosyalar

Hafta 10'a bu dosyalarla başlayacağız.

| Dosya | Bu hafta |
|---|---|
| `passwords.py` | Hazır dosya, değişmedi (1.2). |
| `auth.py` | Hazır dosya, değişmedi (2.2). |
| `database.py` | Import satırı (1.3), `User` ve `Token` modelleri (1.3), `Review` modelindeki `user_id` (1.3), başlangıç kullanıcıları (1.4) |
| `reset_db.py` | Son satır (1.4) |
| `server.py` | Import satırları (2.1); `ReviewCreate`, `ReviewPublic`, `LoginData` ve `UserPublic` modelleri (2.1, 3.1); `create_review` (3.2); `delete_review` (4.1); `login` (2.1); `read_me` (2.2) |
| `test_server.py` | `login_as` (5.2), `test_second_review_conflict` (5.2), dört yeni test (5.3) |

Dosyaların tamamını [ek notta](04_Supplement_Final_Files.md) bulabilirsin.

---

## 7. Ödev: belge ve iki işlem

### 7.1 `README.md` belgesine kimlik doğrulamayı eklemek

API'yi kullanan biri yorum yazmak için ne yapması gerektiğini belgeden öğrenebilmeli. `## Hata yanıtları` bölümünün üstüne şu bölümü ekle:

````markdown
## Kimlik doğrulama

Yorum yazmak ve silmek için giriş yapmak gerekir. Önce token al:

```bash
curl -X POST http://127.0.0.1:8000/login -H "Content-Type: application/json" -d '{"username": "Ece", "password": "ece-parola"}'
```

Yanıttaki `access_token` değerini sonraki isteklerin `Authorization` başlığına ekle:

```bash
curl http://127.0.0.1:8000/me -H "Authorization: Bearer <token>"
```

| İşlem | Giriş gerekir mi? | Kimin için? |
|---|---|---|
| Kitapları ve yorumları okumak | Hayır | Herkes |
| `POST /books/{book_id}/reviews` | Evet | Giriş yapan kullanıcı; okurun adı tokenden gelir. |
| `DELETE /books/{book_id}/reviews/{review_id}` | Evet | Yalnızca yorumu yazan kullanıcı |
| `GET /me` | Evet | Giriş yapan kullanıcı |

Başlangıç kullanıcıları: `Ece` (`ece-parola`) ve `Can` (`can-parola`).
````

`## Hata yanıtları` bölümündeki tabloya iki satır da ekle:

```markdown
| `401` | `Not authenticated`, `Invalid token`, `Wrong username or password` | Kimlik doğrulanamadı: Token yok, geçersiz ya da giriş bilgileri yanlış. |
| `403` | `You can only delete your own reviews` | Kimlik belli, ama bu işlem için izin yok. |
```

### 7.2 Kendin yaz: çıkış

Şu an bir token hiç geçersiz olmuyor. Kullanıcı ortak bir bilgisayardan çıkmak istese bile tokeni çalışmaya devam ediyor.

**İstenenler:**

1. `POST /logout` işlemini yaz. İsteğin `Authorization` başlığındaki token veritabanından silinsin; yanıt `204` olsun. Token yoksa ya da geçersizse yanıt `401` olsun.
2. `test_logout` testini yaz: Ece olarak giriş yap, çıkış yap (`204`), aynı tokenle `/me` iste (`401`).

**İpucu:** Bu işlem kullanıcıya değil, tokenin kendisine ihtiyaç duyuyor. `auth.py` dosyasındaki `get_current_user` fonksiyonunun ilk yarısı işine yarar: `bearer` nesnesini `server.py` dosyasına import edebilirsin.

**Kontrol et:** Sonuç `17 passed` olmalı (önceki haftaların ödev testleri varsa daha fazla).

Kodunu yazıp denedikten sonra [ek nottaki cevapla](05_Supplement_Exercise_7_2_Answer.md) karşılaştır.

### 7.3 Kendin yaz: benim yorumlarım

**İstenenler:**

1. `GET /me/reviews` işlemini yaz: Giriş yapan kullanıcının bütün yorumlarını, kimlik sırasıyla döndürsün. Yanıt modeli `list[ReviewPublic]` olsun.
2. `test_my_reviews` testini yaz: Can 73 numaralı kitaba bir yorum yazsın; sonra Ece `/me/reviews` istesin. Ece'nin listesinde tek yorum olmalı ve kitabı `42` olmalı.

**İpucu:** Sorgu, `get_reviews` fonksiyonundaki sorguya benziyor; yalnızca süzme koşulu farklı.

**Kontrol et:** 7.2 ile birlikte sonuç `18 passed` olmalı.

Kodunu yazıp denedikten sonra [ek nottaki cevapla](06_Supplement_Exercise_7_3_Answer.md) karşılaştır.

---

## 8. Kendini kontrol et: Bu haftanın yedi sorusu

1. Kimlik doğrulama ile yetkilendirme arasındaki fark nedir? Hangisi başarısız olunca `401`, hangisi başarısız olunca `403` döner?
2. Parolaların kendisini değil özetini saklamanın nedeni nedir? Tuz ne işe yarar?
3. Giriş yanıtında kullanıcı yoksa da, parola yanlışsa da aynı açıklama (`Wrong username or password`) dönüyor. Neden ayrı açıklamalar yazmadık?
4. `user: User = Depends(get_current_user)` parametresi bir işleme ne kazandırır? Token yoksa işlemin fonksiyonu çalışır mı?
5. 0. bölümdeki sorun neydi? Deney 3'ten sonra Can, Ece'nin adıyla neden yorum yazamıyor?
6. Can'in, Ece'nin yorumunu silme isteği neden `401` değil `403` aldı?
7. Deney 5'te `test_second_review_conflict` kaldı. Bu bir hatanın işareti miydi? Test neden `422` değil `401` ile kaldı?

### 8.1 Soruların cevapları

1. Kimlik doğrulama, isteği kimin gönderdiğini bulur; yetkilendirme, o kişinin bu işlemi yapıp yapamayacağına karar verir. Kimlik doğrulanamazsa `401`, kimlik belli ama izin yoksa `403` döner.
2. Veritabanı başkasının eline geçerse parolalar okunmasın diye. Özetten parolaya geri dönülemez; doğrulama, gönderilen parolanın aynı tuzla özetlenip kayıtlı özetle karşılaştırılmasıyla yapılır. Tuz, aynı parolaların farklı özetler vermesini sağlar: İki kullanıcının parolası aynıysa bile tabloda bu görünmez ve önceden hesaplanmış özet listeleriyle parola bulmak işe yaramaz.
3. Ayrı açıklamalar, bir kullanıcı adının kayıtlı olup olmadığını ele verirdi. Parola tahmin etmeye çalışan biri önce hangi adların var olduğunu öğrenir, sonra yalnızca onları denerdi.
4. İşlemi giriş yapmış kullanıcılara açar ve isteği gönderen kullanıcıyı fonksiyona hazır verir. FastAPI `get_current_user` fonksiyonunu işlemin fonksiyonundan önce çalıştırır; token yoksa ya da geçersizse istek `401` alır ve işlemin fonksiyonu hiç çalışmaz.
5. Okurun adı gövdeden geliyordu ve gövdeye herkes istediği adı yazabiliyordu. Deney 3'ten sonra `reader` istek modelinde yok; gönderilirse istek `422` alır. Okurun adı, sunucunun doğruladığı tokenin sahibinden geliyor; Can'in tokeni ise Can'e ait.
6. Can tokenini gönderdi, yani kimliği doğrulandı. Ama yorumun sahibi Ece (`user_id=1`); Can'in kimliği `2`. Kimlik belli, izin yok: `403`.
7. Hayır. API bilerek değişti: Yorum yazmak artık giriş gerektiriyor ve okur gövdede gönderilmiyor. Test eski kuralı kontrol ettiği için kaldı ve güncellenmesi gerekti. `401` geldi, çünkü token kontrolü bir bağımlılık olarak gövdenin kontrolünden önce yapıldı.

---

## 9. Resmî belgeler

- [FastAPI — Security](https://fastapi.tiangolo.com/tutorial/security/): FastAPI'nin güvenlik bölümünün girişi. Belgeler token için JWT kullanıyor; biz tokeni veritabanında saklayarak daha basit bir yol izledik ([ek not](03_Supplement_Password_Hashing.md)).
- [FastAPI — Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/): `Depends` bu sayfada.
- [FastAPI — Security Tools](https://fastapi.tiangolo.com/reference/security/): `HTTPBearer` ve `HTTPAuthorizationCredentials` bu sayfada.
- [MDN — HTTP authentication](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Authentication): `Authorization` ve `WWW-Authenticate` başlıkları.
- [MDN — 401 Unauthorized](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/401) ve [403 Forbidden](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/403)
- [Python — hashlib.pbkdf2_hmac](https://docs.python.org/3/library/hashlib.html#hashlib.pbkdf2_hmac)
- [Python — secrets](https://docs.python.org/3/library/secrets.html)
- [OWASP — Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

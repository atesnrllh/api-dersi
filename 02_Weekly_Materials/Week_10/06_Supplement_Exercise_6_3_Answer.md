# Ek Not — 6.3 Alıştırmasının Cevabı: Tokenin Süresi Dolsun

Bu not, föydeki 6.3 alıştırmasının bir cevabını veriyor. Kendi kodunu yazıp denedikten sonra karşılaştır.

---

## 1. `database.py`: tokenin üretildiği zaman

Dosyanın en başına:

```python
from datetime import datetime, timezone
```

`engine` satırının altına, şu anki zamanı veren küçük bir fonksiyon:

```python
# Şu anki zaman, saat dilimiyle birlikte: UTC.
def utc_now():
    return datetime.now(timezone.utc)
```

`Token` modeline yeni alan:

```python
    created_at: datetime = Field(default_factory=utc_now)
```

| Kod | Ne yapar? |
|---|---|
| `datetime.now(timezone.utc)` | Şu anki zamanı, saat dilimi bilgisiyle (UTC) verir. PostgreSQL bu alanı saat dilimiyle birlikte saklar ve okurken de saat dilimiyle verir. Saat dilimi olmayan `datetime.now()` ile saat dilimli bir zaman karşılaştırılamaz; Python `TypeError` verir. |
| `default_factory=utc_now` | Yeni bir token oluşturulurken `utc_now` fonksiyonunu çağırır ve sonucunu alana yazar. `default=utc_now()` yazsaydık, fonksiyon yalnızca bir kez, dosya yüklenirken çalışırdı ve bütün tokenler aynı zamanı alırdı. |

Tablo modeli değiştiği için veritabanını sıfırla: `python reset_db.py` (Hafta 6, 8.3). Testler bunu zaten her testten önce yapıyor.

---

## 2. `auth.py`: süresi dolan token

Dosyanın başına:

```python
from datetime import timedelta
```

`database.py` dosyasından gelen import satırına `utc_now` eklenir:

```python
from database import Token, User, engine, utc_now
```

`bearer` satırının altına tokenin ömrü:

```python
TOKEN_LIFETIME = timedelta(hours=1)
```

`get_current_user` fonksiyonunda, tokenin bulunamadığı durumun altına:

```python
        if utc_now() - token.created_at > TOKEN_LIFETIME:
            raise HTTPException(status_code=401, detail="Token expired", headers={"WWW-Authenticate": "Bearer"})
```

İki zamanın farkı bir `timedelta`; bir saatlik `TOKEN_LIFETIME` ile karşılaştırılabiliyor. Ömrü dosyanın başında adlandırılmış bir değer olarak yazmak, onu değiştirmek gerektiğinde aranacak yeri belli eder. Yanıt yine `401`: İstemci yeniden giriş yapıp yeni bir token alabilir.

---

## 3. Test

`test_server.py` dosyasının başına `from datetime import timedelta` satırı eklenir; `database.py` dosyasından gelen import satırına da `Token`:

```python
from database import Review, Token, engine, reset_database
```

```python
# Token: süresi dolan token 401 alır.
def test_expired_token():
    headers = login_as("Ece", "ece-parola")

    with Session(engine) as session:
        token = session.get(Token, headers["Authorization"].removeprefix("Bearer "))
        token.created_at = token.created_at - timedelta(hours=2)
        session.commit()

    response = client.get("/me", headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "Token expired"}
```

| Kod | Ne yapar? |
|---|---|
| `headers["Authorization"].removeprefix("Bearer ")` | `login_as` fonksiyonunun döndürdüğü başlıktan tokenin kendisini alır. |
| `token.created_at - timedelta(hours=2)` | Tokeni iki saat önce üretilmiş gibi gösterir. Testin iki saat beklemesi yerine zamanı biz geri alıyoruz. |
| `assert response.json() == {"detail": "Token expired"}` | Yanıtın `Invalid token` değil `Token expired` olduğunu kontrol eder: Token var, ama süresi dolmuş. |

---

## 4. Sonuç

6.2 ile birlikte:

```text
============================== 23 passed in 7.72s ==============================
```

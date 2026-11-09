# Ek Not — 7.2 Alıştırmasının Cevabı: Çıkış

Bu not, föydeki 7.2 alıştırmasının bir cevabını veriyor. Kendi kodunu yazıp denedikten sonra karşılaştır.

---

## 1. İşlem

`server.py` dosyasında import satırlarına iki ad eklenir: FastAPI'den `HTTPAuthorizationCredentials`, `auth.py` dosyasından `bearer`.

```python
import secrets

from fastapi import Depends, FastAPI, HTTPException, Path, Response
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import Session, select

from auth import bearer, get_current_user
from database import Book, Review, Token, User, engine
from passwords import verify_password
```

Dosyanın sonuna:

```python
# Çıkış: isteği gönderen tokeni siler; token bundan sonra geçersizdir.
@app.post("/logout", status_code=204)
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    with Session(engine) as session:
        token = session.get(Token, credentials.credentials)

        if token is None:
            raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})

        session.delete(token)
        session.commit()
```

| Kod | Dikkat edilecek nokta |
|---|---|
| `Depends(bearer)` | İşlem kullanıcıyı değil, tokenin kendisini istiyor. `get_current_user` yalnızca kullanıcıyı döndürdüğü için bir adım geriye, `bearer` parçasına gidiyoruz. Başlık yoksa `bearer` isteği yine kendisi `401` ile reddeder. |
| `session.get(Token, ...)` ve `401` | `get_current_user` fonksiyonunun ilk yarısının aynısı. Geçersiz bir tokenle çıkış yapmak istemek de `401` alır. |
| `session.delete(token)` | Yalnızca bu istekteki token silinir. Kullanıcı başka bir cihazdan aldığı tokenle giriş yapmış olarak kalır. |

`get_current_user` ile aynı satırları ikinci kez yazdık. İkinci bir yerde daha gerekirse, `auth.py` dosyasına tokeni döndüren ayrı bir fonksiyon yazmak daha iyi olur.

---

## 2. Test

```python
# Çıkış: 204; aynı token artık geçersiz.
def test_logout():
    headers = login_as("Ece", "ece-parola")

    response = client.post("/logout", headers=headers)
    assert response.status_code == 204

    response = client.get("/me", headers=headers)
    assert response.status_code == 401
```

Test, aynı `headers` sözlüğünü iki istekte kullanıyor: Önce çıkış için, sonra tokenin artık işe yaramadığını görmek için. `login_as` fonksiyonunu ikinci kez çağırsaydık yeni bir token alırdık ve `/me` isteği `200` dönerdi.

---

## 3. Sonuç

```text
============================== 17 passed in 4.67s ==============================
```

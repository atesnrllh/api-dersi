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

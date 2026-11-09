# Ek Not — Hafta 9'un Sonundaki Dosyalar

Föyün 6. bölümü bu haftanın değişikliklerini listeliyor. Bu notta dosyaların tamamı var. `passwords.py` ve `auth.py` hazır dosyalar; föyün 1.2 ve 2.2 bölümlerindeki hâlleriyle kalıyor.

---

## 1. `database.py`

```python
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Session, SQLModel, create_engine

from passwords import hash_password

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


# Yorum tablosu: her yorum bir kitaba ve onu yazan kullanıcıya bağlı; kitap silinince yorumları da silinir.
class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id", ondelete="CASCADE")
    user_id: int = Field(foreign_key="users.id")
    reader: str
    comment: str
    score: int


# Veritabanını başlangıç hâline getirir: tabloları siler, yeniden oluşturur ve başlangıç kayıtlarını yazar.
def reset_database():
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
        session.commit()

        # Kimlik sayaçlarını en büyük kimliğe getir: yeni kitabın kimliği 74, yeni yorumunki 2 olsun.
        session.execute(text("SELECT setval(pg_get_serial_sequence('book', 'id'), (SELECT MAX(id) FROM book))"))
        session.execute(text("SELECT setval(pg_get_serial_sequence('review', 'id'), (SELECT MAX(id) FROM review))"))
        session.commit()
```

---

## 2. `reset_db.py`

```python
from database import reset_database

reset_database()
print("Database reset: 3 books, 1 review, 2 users")
```

---

## 3. `server.py`

```python
import secrets

from fastapi import Depends, FastAPI, HTTPException, Path, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import Session, select

from auth import get_current_user
from database import Book, Review, Token, User, engine
from passwords import verify_password


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

    comment: str = Field(min_length=1)
    score: int = Field(ge=1, le=5)


class ReviewPublic(ReviewCreate):
    model_config = ConfigDict(strict=False, extra="ignore")

    id: int
    book_id: int
    reader: str


class LoginData(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    username: str
    password: str


class UserPublic(BaseModel):
    id: int
    username: str


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


# Giriş yapan kullanıcı: tokenin sahibini döner; token yoksa ya da geçersizse 401.
@app.get("/me", response_model=UserPublic)
def read_me(user: User = Depends(get_current_user)):
    return user
```

---

## 4. `test_server.py`

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from database import Review, engine, reset_database
from server import app

client = TestClient(app)

new_book = {
    "title": "Test Kitabı",
    "author": {
        "first_name": "Ada",
        "last_name": "Yıldız"
    },
    "available": True,
    "tags": []
}


# Kullanıcı adına giriş yapar ve isteklere eklenecek Authorization başlığını döner.
def login_as(username, password):
    response = client.post("/login", json={"username": username, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": "Bearer " + token}


# Her testten önce çalışır: her test, veritabanının başlangıç hâliyle başlar.
@pytest.fixture(autouse=True)
def fresh_database():
    reset_database()


# Tek kitap: 42 numaralı kitap okunabilmeli.
def test_get_book():
    response = client.get("/books/42")

    assert response.status_code == 200
    assert response.json()["title"] == "API Yolculuğu"


# Olmayan kitap: 404 ve açıklaması.
def test_get_missing_book():
    response = client.get("/books/43")

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}


# Yeni kitap: 201, Location başlığı ve o adresten okunabilen kitap.
def test_create_book():
    response = client.post("/books", json=new_book)

    assert response.status_code == 201
    assert response.headers["Location"] == "/books/74"

    response = client.get("/books/74")
    assert response.json()["title"] == "Test Kitabı"


# Arama: büyük ve küçük harfi ayırmaz, sonuçlar kimlik sırasıyla gelir.
def test_search_books():
    response = client.get("/books", params={"search": "api"})

    ids = []
    for book in response.json():
        ids.append(book["id"])
    assert ids == [42, 73]


# Hatalı puan: 422 ve hatanın yeri.
def test_rating_out_of_range():
    book = new_book.copy()
    book["rating"] = 7

    response = client.post("/books", json=book)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "rating"]


# Negatif kimlik: yol parametresinin kuralı.
def test_negative_book_id():
    response = client.get("/books/-5")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "book_id"]


# PATCH: yalnızca gönderilen alan değişir.
def test_patch_rating():
    response = client.patch("/books/57", json={"rating": 3})

    assert response.status_code == 200
    assert response.json()["rating"] == 3
    assert response.json()["title"] == "Veriyle İlk Adımlar"


# PATCH: ad null olamaz; istek reddedilir ve kitap değişmez.
def test_patch_null_title():
    response = client.patch("/books/42", json={"title": None})
    assert response.status_code == 422

    response = client.get("/books/42")
    assert response.json()["title"] == "API Yolculuğu"


# Yorum: aynı okur aynı kitaba ikinci kez yorum yazamaz.
def test_second_review_conflict():
    review = {"comment": "Tekrar okudum.", "score": 4}

    response = client.post("/books/42/reviews", json=review, headers=login_as("Ece", "ece-parola"))

    assert response.status_code == 409


# Kitap silme: kitabın yorumlarını veritabanı da siler.
def test_delete_book_deletes_reviews():
    response = client.delete("/books/42")
    assert response.status_code == 204

    with Session(engine) as session:
        statement = select(Review).where(Review.book_id == 42)
        reviews = session.exec(statement).all()

    assert reviews == []


# Süzme: available=false yalnızca ödünç verilmiş kitapları getirir.
def test_filter_not_available():
    response = client.get("/books", params={"available": False})

    ids = []
    for book in response.json():
        ids.append(book["id"])
    assert ids == [57]


# PUT: kitabın tamamı değişir; gönderilmeyen puan None olur.
def test_replace_book():
    response = client.put("/books/73", json=new_book)

    assert response.status_code == 200
    assert response.json()["title"] == "Test Kitabı"
    assert response.json()["rating"] is None


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

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

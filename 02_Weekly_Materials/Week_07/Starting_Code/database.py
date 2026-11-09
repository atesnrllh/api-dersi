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

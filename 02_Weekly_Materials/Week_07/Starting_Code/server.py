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

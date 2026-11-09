from fastapi import FastAPI, HTTPException, Path, Response
from pydantic import BaseModel, ConfigDict, Field


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


app = FastAPI()

books = [
    {
        "id": 42,
        "title": "API Yolculuğu",
        "author": {
            "first_name": "Deniz",
            "last_name": "Kaya"
        },
        "available": True,
        "tags": ["software", "education"],
        "rating": None,
        "internal_note": "Kapağı yıpranmış, yenisi sipariş edildi."
    },
    {
        "id": 57,
        "title": "Veriyle İlk Adımlar",
        "author": {
            "first_name": "Ece",
            "last_name": "Yılmaz"
        },
        "available": False,
        "tags": [],
        "rating": 0
    },
    {
        "id": 73,
        "title": "Python ile Web API",
        "author": {
            "first_name": "Can",
            "last_name": "Demir"
        },
        "available": True,
        "tags": ["python", "api"],
        "rating": 4.5
    }
]

reviews = [
    {
        "id": 1,
        "book_id": 42,
        "reader": "Ece",
        "comment": "Konuları örneklerle anlatıyor.",
        "score": 5
    }
]


# Kitap listesi: ada ve ödünç durumuna göre süzülebilir.
@app.get("/books", response_model=list[BookPublic])
def get_books(search: str = "", available: bool | None = None):
    results = []

    for book in books:
        title_matches = search.casefold() in book["title"].casefold()
        availability_matches = (
            available is None or book["available"] == available
        )

        if title_matches and availability_matches:
            results.append(book)

    return results


# Tek kitap: kimliğe göre bulur, yoksa 404.
@app.get("/books/{book_id}", response_model=BookPublic)
def get_book(book_id: int = Path(gt=0)):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")


# Yeni kitap: listeye ekler, 201 ve Location döner.
@app.post("/books", status_code=201, response_model=BookPublic)
def create_book(book_data: BookCreate, response: Response):
    new_id = 1
    for book in books:
        if book["id"] >= new_id:
            new_id = book["id"] + 1

    created_book = book_data.model_dump()
    created_book["id"] = new_id
    books.append(created_book)
    response.headers["Location"] = f"/books/{new_id}"
    return created_book


# Kitabı silme: listeden çıkarır, 204 döner; kitap yoksa 404.
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int = Path(gt=0)):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return

    raise HTTPException(status_code=404, detail="Book not found")


# Kitabı tümüyle değiştirme: bütün alanlar yenisiyle değişir; kitap yoksa 404.
@app.put("/books/{book_id}", response_model=BookPublic)
def replace_book(book_data: BookCreate, book_id: int = Path(gt=0)):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            new_book = book_data.model_dump()
            new_book["id"] = book_id
            books[index] = new_book
            return new_book

    raise HTTPException(status_code=404, detail="Book not found")


# Kitabın bir kısmını değiştirme: yalnızca gönderilen alanlar değişir; kitap yoksa 404.
@app.patch("/books/{book_id}", response_model=BookPublic)
def update_book(book_data: BookUpdate, book_id: int = Path(gt=0)):
    for book in books:
        if book["id"] == book_id:
            changes = book_data.model_dump(exclude_unset=True)
            book.update(changes)
            return book

    raise HTTPException(status_code=404, detail="Book not found")


# Kitabın yorumları: kitap yoksa 404.
@app.get("/books/{book_id}/reviews")
def get_reviews(book_id: int = Path(gt=0)):
    book_exists = False
    for book in books:
        if book["id"] == book_id:
            book_exists = True

    if not book_exists:
        raise HTTPException(status_code=404, detail="Book not found")

    results = []
    for review in reviews:
        if review["book_id"] == book_id:
            results.append(review)

    return results


# Yeni yorum: kitaba ekler, 201 döner; kitap yoksa 404, okurun bu kitaba yorumu varsa 409.
@app.post("/books/{book_id}/reviews", status_code=201)
def create_review(review_data: ReviewCreate, book_id: int = Path(gt=0)):
    book_exists = False
    for book in books:
        if book["id"] == book_id:
            book_exists = True

    if not book_exists:
        raise HTTPException(status_code=404, detail="Book not found")

    for review in reviews:
        if review["book_id"] == book_id and review["reader"] == review_data.reader:
            raise HTTPException(status_code=409, detail="This reader has already reviewed this book")

    new_id = 1
    for review in reviews:
        if review["id"] >= new_id:
            new_id = review["id"] + 1

    created_review = review_data.model_dump()
    created_review["id"] = new_id
    created_review["book_id"] = book_id
    reviews.append(created_review)
    return created_review

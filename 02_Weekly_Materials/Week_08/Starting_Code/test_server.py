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
    review = {"reader": "Ece", "comment": "Tekrar okudum.", "score": 4}

    response = client.post("/books/42/reviews", json=review)

    assert response.status_code == 409


# Kitap silme: kitabın yorumlarını veritabanı da siler.
def test_delete_book_deletes_reviews():
    response = client.delete("/books/42")
    assert response.status_code == 204

    with Session(engine) as session:
        statement = select(Review).where(Review.book_id == 42)
        reviews = session.exec(statement).all()

    assert reviews == []

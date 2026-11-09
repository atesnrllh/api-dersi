from sqlalchemy import text
from sqlmodel import Session, SQLModel

from database import Book, Review, engine

# Tabloları sil ve modellere göre yeniden oluştur.
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
    session.add(Review(
        id=1,
        book_id=42,
        reader="Ece",
        comment="Konuları örneklerle anlatıyor.",
        score=5,
    ))
    session.commit()

    # Kimlik sayaçlarını en büyük kimliğe getir: yeni kitabın kimliği 74, yeni yorumunki 2 olsun.
    session.execute(text("SELECT setval(pg_get_serial_sequence('book', 'id'), (SELECT MAX(id) FROM book))"))
    session.execute(text("SELECT setval(pg_get_serial_sequence('review', 'id'), (SELECT MAX(id) FROM review))"))
    session.commit()

print("Database reset: 3 books, 1 review")

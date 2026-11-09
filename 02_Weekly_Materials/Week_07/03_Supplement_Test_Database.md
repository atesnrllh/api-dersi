# Ek Not — Testler İçin Ayrı Bir Veritabanı

Föyün Deney 2'sinde her testten önce `reset_database()` çalıştırdık. Bu, testlerin `catalog` veritabanını, yani sunucunun da kullandığı veritabanını her seferinde sıfırladığı anlamına geliyor. Bu notta testleri ayrı bir veritabanında çalıştırmanın bir yolunu görüyoruz.

---

## 1. Sorun

Sunucuyu çalıştırıp elle birkaç kitap eklediğini düşün. Ardından testleri çalıştırırsan bu kitaplar silinir: Testler `catalog` veritabanını başlangıç hâline getirir. Föyde bu bir sorun değil, çünkü her deneyden önce veritabanını zaten sıfırlıyoruz. Gerçek bir projede ise geliştiricinin üzerinde çalıştığı veri ile testlerin sildiği veri ayrı olmalı.

---

## 2. İkinci bir veritabanı oluştur

Aynı PostgreSQL kapsayıcısında `catalog_test` adlı ikinci bir veritabanı oluştur:

```bash
docker exec book-db createdb -U student catalog_test
```

`createdb`, PostgreSQL ile birlikte gelen ve yeni bir veritabanı oluşturan bir programdır.

---

## 3. Testlerde motoru değiştir

`test_server.py` dosyasında import satırları ve hazırlık fonksiyonu şöyle değişir:

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, select

import database
import server
from database import Review, reset_database
from server import app

test_engine = create_engine("postgresql+psycopg://student:secret@localhost:5432/catalog_test")
```

```python
# Her testten önce çalışır: testler catalog_test veritabanını kullanır ve onu sıfırlar.
@pytest.fixture(autouse=True)
def fresh_database(monkeypatch):
    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(server, "engine", test_engine)
    reset_database()
```

| Kod | Ne yapar? |
|---|---|
| `test_engine = create_engine(...)` | `catalog_test` veritabanına bağlanan ikinci bir motor. Adresin yalnızca son parçası farklı. |
| `monkeypatch` | pytest'in hazır bir hazırlık fonksiyonu. Hazırlık fonksiyonumuzun parametresine bu adı yazınca pytest onu bize verir. Bir değeri yalnızca test süresince değiştirmeyi sağlar; test bitince eski değer geri gelir. |
| `monkeypatch.setattr(server, "engine", test_engine)` | `server.py` dosyasındaki `engine` adını test süresince `test_engine` yapar. Sunucunun fonksiyonları `with Session(engine)` satırında artık test veritabanına bağlanır. |
| `monkeypatch.setattr(database, "engine", test_engine)` | Aynısını `database.py` için yapar; `reset_database()` test veritabanını sıfırlar. |

Föyün Deney 5'teki testi de veritabanına kendisi bakıyordu. O testte `Session(engine)` yerine `Session(test_engine)` yazmak gerekir; çünkü testin başında `from database import engine` ile alınan ad, `monkeypatch` ile değişmez.

---

## 4. Deneme

Önce `catalog` veritabanını sıfırladık ve psql ile bir kitap ekledik. Ardından testleri çalıştırdık ve iki veritabanına baktık:

| Ne yaptık? | Sonuç |
|---|---|
| `python -m pytest -q` | `10 passed` |
| `catalog` veritabanındaki kitaplar | 42, 57, 73 ve elle eklenen 74. Testler bu veritabanına dokunmadı. |
| `catalog_test` veritabanındaki kitaplar | 57 ve 73. Son test 42 numaralı kitabı silmişti; bir sonraki test çalıştırması onu yeniden yazar. |

---

## 5. Daha temiz bir yol

Bu yolda veritabanının adresi iki yerde yazılı: `database.py` dosyasında ve testte. Gerçek projelerde adres koddan ayrı bir ayar olarak verilir; uygulama hangi ortamda çalışıyorsa o ortamın veritabanına bağlanır. Çalışma ayarlarını koddan ayırmayı Hafta 11'de göreceğiz.

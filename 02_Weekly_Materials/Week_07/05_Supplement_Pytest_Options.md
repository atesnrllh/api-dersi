# Ek Not — pytest Seçenekleri

Föyde pytest'i birkaç seçenekle çalıştırdık. Bu not, onları ve iki yenisini bir arada veriyor. Seçenekler birlikte de yazılabilir: `python -m pytest -k search -v`.

---

## 1. Çıktının ayrıntısı

| Seçenek | Ne yapar? | Örnek çıktı |
|---|---|---|
| Seçeneksiz | Her test için bir işaret: `.` geçti, `F` kaldı. | `test_server.py .........` |
| `-v` | Her testin adı ve sonucu ayrı satırda (*verbose*: ayrıntılı). | `test_server.py::test_get_book PASSED` |
| `-q` | Başlık satırları olmadan, kısa çıktı (*quiet*: sessiz). | `9 passed in 1.83s` |
| `--tb=short` | Kalan testlerin hata izini kısaltır. Varsayılanı `--tb=long`; `--tb=no` hata izini hiç göstermez. | Föyün Deney 3'ü |

`-q` ile, bütün testler geçtiğinde çıktının tamamı iki satır:

```text
.........                                                                [100%]
9 passed in 1.83s
```

---

## 2. Hangi testler çalışsın?

| Seçenek | Ne yapar? |
|---|---|
| `-k search` | Adında `search` geçen testleri çalıştırır. Föyün Deney 4'ü |
| `-k "patch and not null"` | Adında `patch` geçen, `null` geçmeyen testleri çalıştırır: `test_patch_rating` çalışır, `test_patch_null_title` çalışmaz. |
| `test_server.py::test_get_book` | Yalnızca bu testi çalıştırır: dosyanın adı, iki iki nokta üst üste ve testin adı. |
| `-x` | İlk kalan testte durur. |

`-x` seçeneğini, Deney 3 ve Deney 4'teki iki değişiklik birlikte yapılmışken denedik. Normalde iki test kalırdı; `-x` ile pytest ilkinde durdu:

```text
test_server.py ...F

=========================== short test summary info ============================
FAILED test_server.py::test_search_books - assert [] == [42, 73]
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
========================= 1 failed, 3 passed in 1.63s ==========================
```

Dördüncü test kaldı ve sonraki beş test hiç çalışmadı. Çok sayıda test bir arada kaldığında bir hatayla uğraşmaya başlamak için kullanışlıdır.

---

## 3. `print` çıktısını hemen görmek

Föyün Deney 4.3'ünde `print` çıktısını pytest yalnızca test kalınca, `Captured stdout call` bölümünde gösterdi. `-s` seçeneği yakalamayı kapatır; `print` çıktısı test çalışırken hemen görünür:

```bash
python -m pytest -k search -s
```

```text
test_server.py Response: 200 []
F
```

Çıktı, testin işaretinden (`F`) önce, satırın ortasında görünür. Test geçse de görünür.

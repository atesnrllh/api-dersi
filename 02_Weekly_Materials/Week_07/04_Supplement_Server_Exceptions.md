# Ek Not — Test, Sunucudaki Hatayı Neden Görüyor?

Föyün Deney 3'ünde `update_book` fonksiyonu bozulunca test çıktısında veritabanının hatası göründü. Bu notta aynı hatanın gerçek bir istemciden nasıl göründüğünü ve `TestClient` aracının bu davranışının nasıl değiştirileceğini görüyoruz.

---

## 1. Aynı hata, iki istemci

Deney 3.1'deki bozuk `update_book` fonksiyonuyla, aynı `PATCH` isteğini iki yoldan gönderdik:

| İstemci | Ne gördü? |
|---|---|
| `uvicorn` ile çalışan sunucuya `httpx.patch(...)` | `500 Internal Server Error`. Yanıtın gövdesinde yalnızca `Internal Server Error` yazıyor; hatanın ayrıntısı sunucunun terminalinde. |
| `TestClient` ile `client.patch(...)` | Durum kodu yok; sunucudaki `IntegrityError` hatası testin içinde ortaya çıktı ve hata izi test çıktısında göründü. |

Gerçek bir istemcinin hatanın ayrıntısını görmemesi doğru: Hata izinde veritabanının yapısı, SQL komutları ve dosya yolları var. Bunlar istemciye gitmemeli. Test yazarken ise tam tersini istiyoruz: Hatanın nerede olduğunu hemen görmek.

---

## 2. `raise_server_exceptions=False`

`TestClient`, sunucuda yakalanmayan bir hata çıktığında onu varsayılan olarak teste taşır. Bu davranış istemciyi oluştururken değiştirilebilir:

```python
client = TestClient(app, raise_server_exceptions=False)
```

Bu ayarla aynı test şöyle kaldı:

```text
    def test_patch_rating():
        response = client.patch("/books/57", json={"rating": 3})

>       assert response.status_code == 200
E       assert 500 == 200
E        +  where 500 = <Response [500 Internal Server Error]>.status_code

test_server.py:86: AssertionError
```

Test artık gerçek bir istemcinin göreceğini görüyor: `500`. Ama hatanın nedeni çıktıda yok; onu bulmak için yine sunucunun hata izine bakmak gerekir.

Föyde varsayılan ayarı kullandık, çünkü hata ayıklarken hatanın kendisini görmek işimizi kolaylaştırıyor. `raise_server_exceptions=False`, "sunucu beklenmedik bir hatada `500` döndürüyor mu?" gibi bir şeyi test etmek istediğinde işe yarar.

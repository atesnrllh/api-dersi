# Ek Not — 6.2 Alıştırmasının Cevabı: Kütüphaneci Yorum Silebilsin

Bu not, föydeki 6.2 alıştırmasının bir cevabını veriyor. Kendi kodunu yazıp denedikten sonra karşılaştır.

---

## 1. Değişen satırlar

`delete_review` fonksiyonunda `403` yanıtını veren koşul ve açıklama satırı değişir:

```python
# Yorumu silme: yorumu yazan kullanıcı ya da bir kütüphaneci silebilir; yorum yoksa 404, başkasının yorumuysa 403.
```

```python
        if review.user_id != user.id and not user.is_librarian:
            raise HTTPException(status_code=403, detail="You can only delete your own reviews")
```

Koşul iki durumda da doğru olmalı ki istek reddedilsin: Yorum isteği gönderenin değil **ve** isteği gönderen kütüphaneci değil. Selin için ikinci kısım yanlış olduğu için koşulun tamamı yanlış olur ve silme yapılır. Can için iki kısım da doğru: `403`.

`update_review` fonksiyonundaki koşul olduğu gibi kalıyor. Aynı rol, bir kayıt üzerinde bir işlemi yapabilir, ötekini yapamaz: Erişim kuralları işlem işlem yazılır.

---

## 2. Test

```python
# Yorum silme: kütüphaneci her yorumu silebilir.
def test_librarian_can_delete_any_review():
    response = client.delete("/books/42/reviews/1", headers=login_as("Selin", "selin-parola"))
    assert response.status_code == 204

    response = client.get("/books/42/reviews")
    assert response.json() == []
```

Kuralı değiştirdikten sonra `test_delete_other_users_review` testinin de geçtiğini kontrol etmek önemli. O test, kuralı gevşetirken okurlar için kapıyı açmadığımızı gösteriyor.

`and` yerine yanlışlıkla `or` yazılsaydı ne olurdu? Koşul "sahibi değil **ya da** kütüphaneci değil" olurdu ve yalnızca hem sahibi hem kütüphaneci olan biri silebilirdi. Selin, Ece'nin yorumunu silemezdi; yeni test bunu yakalardı. Ama Ece de kendi yorumunu silemezdi, ve bunu hiçbir test göstermezdi: Dosyada bir okurun kendi yorumunu sildiği bir test yok. Hafta 9'da bu durumu yalnızca `delete_client.py` ile, gözle denemiştik. Erişim tablosundaki her "Evet" de bir testle korunmalı; yoksa bir kuralı sıkılaştırırken izin verilmesi gereken bir isteği kapattığımızı fark etmeyiz.

---

## 3. Sonuç

```text
============================== 22 passed in 6.99s ==============================
```

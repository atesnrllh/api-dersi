# Ek Not — Hazır Dosyalar Neyi Basit Tutuyor?

Föyde `passwords.py` ve `auth.py` dosyalarını hazır kullandık. İkisi de çalışıyor ve fikri açıkça gösteriyor, ama gerçek bir projede birkaç noktada farklı yazılırdı. Bu not o noktaları topluyor.

---

## 1. Parola özeti: hazır paketler

`passwords.py`, Python'un kendi `hashlib.pbkdf2_hmac` fonksiyonunu kullanıyor. Yöntem güvenilir ve yeni bir paket gerektirmiyor. Gerçek projelerde ise genellikle hazır bir paket kullanılır. FastAPI'nin belgeleri `pwdlib` paketini ve **Argon2** yöntemini öneriyor.

Hazır paketlerin üç yararı var:

| Konu | `passwords.py` | Hazır paket |
|---|---|---|
| Yöntem | PBKDF2. Hâlâ kabul gören bir yöntem. | Argon2 ya da bcrypt. Özel donanımla hızlandırılması daha zor yöntemler. |
| Tekrar sayısı | `100_000`, kodun içinde sabit | Güncel öneriyle gelir. OWASP'ın 2023'ten beri PBKDF2-SHA256 için önerdiği sayı 600 000. |
| Yöntemi değiştirmek | Özetin içinde yöntemin adı yok. Yöntemi değiştirirsek eski özetleri ayıramayız. | Özetin başına yöntemi ve ayarlarını yazar. Eski özetler okunabilir, kullanıcı giriş yaptıkça yeni yöntemle yenilenebilir. |

Tekrar sayısını bilerek düşük tuttuk: Testler her testten önce iki parolayı özetliyor. 600 000 tekrarla testlerin süresi birkaç kat uzardı. Gerçek bir projede testler için ayrı, düşük bir ayar kullanmak yaygın bir yoldur.

Bu ayrıntıların hiçbiri föydeki fikri değiştirmez: Parolanın kendisi değil, tuzlu ve yavaş bir özeti saklanır.

---

## 2. Token: veritabanında mı, kendi içinde mi?

Föyde token, rastgele bir metin ve sunucu onu `token` tablosunda arıyor. Bu yönteme **opak token (opaque token)** denir: Tokenin içinde bir bilgi yok; anlamını yalnızca sunucu, kendi tablosuna bakarak bilir.

FastAPI'nin belgelerinde ise **JWT (JSON Web Token)** kullanılıyor. Bir JWT'nin içinde kullanıcının adı ve tokenin geçerlilik süresi yazılıdır; sunucu bu bilgiyi gizli bir anahtarla imzalar. Sunucu, imzayı kontrol ederek tokenin kendisinin ürettiği ve değiştirilmemiş bir token olduğunu anlar; veritabanına bakması gerekmez.

| | Opak token (föyde) | JWT |
|---|---|---|
| Her istekte veritabanına bakılır mı? | Evet | Hayır |
| Token iptal edilebilir mi? | Evet: Satırı silmek yeter (7.2 alıştırması). | Zor: Süresi dolana kadar geçerlidir; iptal için yine bir liste tutmak gerekir. |
| Ek paket | Yok | `pyjwt` gibi bir paket ve gizli bir anahtar |

Föyde opak tokeni seçtik, çünkü tokenin ne olduğu tabloya bakınca görünüyor ve çıkış işlemi tek satırla yazılabiliyor.

---

## 3. Eksik kalanlar

Föydeki tokenlerin süresi hiç dolmuyor: Bir token, silinene kadar geçerli. Gerçek bir projede her tokenin bir geçerlilik süresi olur. Ayrıca giriş işlemi, aynı kullanıcı adı için arka arkaya yapılan yanlış denemeleri sınırlamıyor; bir saldırgan istediği kadar parola deneyebilir. Bir ayrıntı daha: Giriş işlemi, kullanıcı adı yoksa parolayı hiç özetlemeden yanıt veriyor. Açıklamalar aynı olsa da bu yanıt daha hızlı geliyor; yanıt sürelerini ölçen biri hangi adların kayıtlı olduğunu yine çıkarabilir. Gerçek projelerde kullanıcı bulunamadığında da bir özet hesaplanır. Bu iki konuya Hafta 10'da, erişim denetimi ve API güvenliği konusunda döneceğiz.

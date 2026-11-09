import hashlib
import secrets


# Parolanın özetini üretir. Tuz her parola için rastgele seçilir ve özetin başına yazılır.
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return salt + "$" + digest.hex()


# Gönderilen parolayı, kayıtlı özetteki tuzla yeniden özetler ve iki özeti karşılaştırır.
def verify_password(password, password_hash):
    salt = password_hash.split("$")[0]
    return secrets.compare_digest(hash_password(password, salt), password_hash)

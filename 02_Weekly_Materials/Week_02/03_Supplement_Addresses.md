# Ek Not — İstemcinin ve Sunucunun Adresi

Derste istemci (`client.py`) ve sunucu (`server.py`) **aynı bilgisayarda** çalışır.

## Bilgisayarın kendi adresi: `127.0.0.1`

Programlar birbiriyle konuşurken karşı tarafı bir adresle bulur. İki program aynı bilgisayarda olsa bile bu böyledir.

`127.0.0.1`, **bilgisayarın kendi adresidir**. Bu adrese giden istek bilgisayardan dışarı çıkmaz; aynı bilgisayardaki sunucuya gider. İnternet bağlantısı gerekmez. Bu adresin yerine `localhost` da yazılabilir.

## İstemcinin ve sunucunun adresi

| | Adres | Kapı numarası (port) |
|---|---|---|
| **Sunucu** | `127.0.0.1` | `8000`: her zaman aynı |
| **İstemci** | `127.0.0.1` | Her çalıştırmada farklı, örneğin `51678` |

**Adres ikisinde de aynı.** İki program da aynı bilgisayarda çalıştığı için ikisi de `127.0.0.1` adresini kullanır.

**Sunucunun kapı numarası sabit.** Sunucu `8000` numaralı kapıda bekler. Bu numarayı biz seçtik ve değişmez. İstemcinin sunucuyu bulabilmesi için bu numarayı önceden bilmesi gerekir. Bu yüzden `client.py` içine şunu yazıyoruz:

```python
response = httpx.get("http://127.0.0.1:8000/book")
```

**İstemcinin kapı numarası her seferinde değişir.** İstemci de bağlanmak için bir kapı numarasına ihtiyaç duyar. Bu numarayı biz seçmeyiz; bilgisayar her çalıştırmada boş bir numara verir. Sunucu cevabı bu numaraya gönderir.

## Sunucu terminalindeki satır

İstemci her istek gönderdiğinde sunucu terminalinde şöyle bir satır görünür:

```text
INFO:     127.0.0.1:51678 - "GET /book HTTP/1.1" 200 OK
```

Bu satır şöyle okunur:

> "Bu bilgisayardaki `51678` numaralı kapıdan bir istemci `GET /book` istedi, ben de `200` ile cevap verdim."

`client.py`'yi tekrar çalıştırırsan bu satırda `127.0.0.1` aynı kalır, yalnızca kapı numarası değişir.

## İstek bilgisayardan dışarı çıkarsa

`127.0.0.1` yalnızca bilgisayarın **içinde** geçerli bir adrestir. İstemci Open-Meteo gibi dışarıdaki bir sunucuya istek gönderdiğinde bu adresi kullanamaz; bilgisayar o istek için **ağdaki adresini** kullanır (örneğin `10.140.1.110`).

| İstek nereye gidiyor? | İstemcinin adresi |
|---|---|
| Kendi sunucumuza | `127.0.0.1` |
| Open-Meteo'ya | Bilgisayarın ağdaki adresi |

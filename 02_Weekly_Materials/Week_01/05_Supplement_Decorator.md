# Ek Not — Dekoratör: `@app.get` Satırı Ne Yapıyor?

Föyün Deney 1'inde yazdığımız `server.py` şöyleydi:

```python
from fastapi import FastAPI

app = FastAPI()

book = {
    "id": 42,
    "title": "API Yolculuğu",
    "author": "Deniz Kaya"
}


@app.get("/book/42")
def get_book():
    return book
```

Tarayıcıda `http://127.0.0.1:8000/book/42` adresine gidince kitabın bilgileri gelir; yani `get_book` fonksiyonu çalışır. Ama kodun hiçbir yerinde `get_book()` diye bir çağrı yok.

> **Merak sorusu:** `get_book` fonksiyonunu kim çalıştırıyor? Tarayıcının istediği yol bu fonksiyona nasıl ulaşıyor?

Cevabın anahtarı `@app.get("/book/42")` satırında. Bu satıra **dekoratör (decorator)** denir. Föyde dekoratörü kısaca gördük; bu notta önce sade Python ile adım adım kuruyoruz, sonra bu soruya dönüyoruz.

Nottaki her örnek için proje klasöründe adı verilen dosyayı oluştur ve sanal ortam etkinken çalıştır; örneğin:

```bash
python function_basics.py
```

---

## 1. Önce üç temel fikir

Dekoratörü anlamak için fonksiyonlarla ilgili üç fikre ihtiyacımız var. Bu bölümdeki üç örneği `function_basics.py` dosyasına alt alta yazabilirsin; çıktılar aynı sırayla gelir.

### 1.1 Fonksiyonu tanımlamak, onu çalıştırmak demek değildir

```python
def greet():
    print("Hello!")
```

`def` satırı bir tarif yazmaya benzer. Tarifi yazmakla yemek pişmez: Bu kod çalışınca ekrana hiçbir şey yazılmaz.

Fonksiyonu çalıştırmak için adının sonuna parantez koyarız:

```python
greet()
```

```text
Hello!
```

| Yazım | Anlamı |
|---|---|
| `greet` | Fonksiyonun kendisi (tarif kâğıdı) |
| `greet()` | Fonksiyonu çalıştır (yemeği pişir) |

### 1.2 Fonksiyon başka bir fonksiyona verilebilir

Bir fonksiyona sayı ya da metin verebildiğimiz gibi başka bir fonksiyonu da verebiliriz:

```python
def run_twice(function):
    function()
    function()


run_twice(greet)
```

```text
Hello!
Hello!
```

`run_twice(greet)` yazdık, `run_twice(greet())` değil. Yani fonksiyonu çalıştırmadan kendisini verdik. Onu ne zaman çalıştıracağına `run_twice` karar verdi.

### 1.3 Bir fonksiyon yeni bir fonksiyon üretip geri verebilir

```python
def make_greeter(name):
    def greet_person():
        print("Hello,", name)
    return greet_person


greet_ali = make_greeter("Ali")
greet_ali()
```

```text
Hello, Ali
```

`make_greeter` bir fonksiyon fabrikası gibi çalışır: İçeride yeni bir fonksiyon (`greet_person`) üretir ve onu çalıştırmadan dışarı verir. `return greet_person` satırında parantez olmadığına dikkat et.

Üretilen fonksiyon, kendisine verilen `name` bilgisini hatırlar. Bu özellik 4. bölümde işimize yarayacak.

> **İpucu:** Dekoratör bu fikirlerin birleşimidir: Bir fonksiyonu alır (1.2) ve geriye yeni bir fonksiyon verir (1.3).

---

## 2. Dekoratör nedir?

**Dekoratör**, bir fonksiyonu alıp geriye bir fonksiyon veren fonksiyondur. Amacı, bir fonksiyonun içine dokunmadan ona yeni bir davranış eklemektir.

### 2.1 `@` işareti ne yapar?

`@` bir kısaltmadır. Aşağıdaki iki yazım aynı işi yapar:

<table>
<tr>
<th><code>@</code> ile</th>
<th><code>@</code> olmadan</th>
</tr>
<tr>
<td>

```python
@wrap
def greet():
    print("Hello!")
```

</td>
<td>

```python
def greet():
    print("Hello!")

greet = wrap(greet)
```

</td>
</tr>
</table>

`@wrap` satırı Python'a şunu söyler: "`greet` fonksiyonunu tanımladıktan hemen sonra onu `wrap` fonksiyonuna ver. Geri gelen fonksiyonu yine `greet` adıyla sakla."

### 2.2 Çalışma sırasını gösteren örnek

Bu örnekteki `print` satırları numaralı. Numaralar, satırların hangi sırayla çalıştığını gösteriyor. Dosyanın adı `what_is_decorator.py`.

Önce dekoratörü yazıyoruz:

```python
print("[1] Program started.")


def wrap(original_function):
    print("[3] wrap() is running. Received:", original_function.__name__)

    def wrapped():
        print("    >> The wrapper runs first.")
        original_function()
        print("    >> The original function finished.")

    print("[4] The wrapper is ready, returning it.")
    return wrapped
```

`wrap` bir fonksiyon alır (`original_function`). Onu saran yeni bir fonksiyon üretir (`wrapped`) ve bu yeni fonksiyonu geri verir. `__name__`, bir fonksiyonun adını veren Python özelliğidir.

Sonra dekoratörü kullanıyoruz:

```python
print("[2] wrap is defined. Next comes @wrap.")


@wrap
def greet():
    print("    ** Hello! (original function)")


print("[5] The name 'greet' now points to:", greet.__name__)

print("[6] Calling greet():")
greet()

print("[7] Calling it once more:")
greet()
```

Çıktı:

```text
[1] Program started.
[2] wrap is defined. Next comes @wrap.
[3] wrap() is running. Received: greet
[4] The wrapper is ready, returning it.
[5] The name 'greet' now points to: wrapped
[6] Calling greet():
    >> The wrapper runs first.
    ** Hello! (original function)
    >> The original function finished.
[7] Calling it once more:
    >> The wrapper runs first.
    ** Hello! (original function)
    >> The original function finished.
```

Koddaki numaraları yukarıdan aşağıya okuyunca sıra 1, 3, 4, 2, 5, 6, 7 olur; çıktıda ise sıra düzgündür. Çünkü Python bir fonksiyonun içini, o fonksiyon çağrılınca çalıştırır.

| Çıktı | Ne oldu? |
|---|---|
| `[1]`, `[2]` | `wrap` yalnızca tanımlandı, içi çalışmadı. |
| `[3]` | `@wrap` satırı `wrap(greet)` çağrısını yaptı. |
| `[4]` | `wrapped` üretildi ama çalışmadı; `wrap` onu geri verdi. |
| `[5]` | `greet` adı artık `wrapped` fonksiyonunu gösteriyor. Asıl fonksiyon, `wrapped` fonksiyonunun içinde `original_function` adıyla duruyor. |
| `[6]`, `[7]` | `greet()` çağrılınca `wrapped` çalıştı; o da arada asıl fonksiyonu çağırdı. |

> **En çok karıştırılan nokta:** Dekoratör, fonksiyon tanımlanırken **bir kez** çalışır. Bu yüzden `[3]` ve `[4]` yalnızca bir kez yazıldı. Sarmalayıcı fonksiyonun (`wrapped`) içindeki kod ise fonksiyon **her çağrıldığında** çalışır.

> **İpucu:** VS Code'da `wrap` fonksiyonunun ilk satırına kesme noktası (breakpoint) koyup dosyayı **Run and Debug** ile çalıştır. Programın `@wrap` satırından `wrap` fonksiyonunun içine atladığını adım adım görebilirsin.

---

## 3. Dekoratör neden kullanılır?

Dekoratör, birçok fonksiyonda tekrar eden bir işi tek bir yere yazmayı sağlar.

### 3.1 Sorun: tekrar eden kod

Bir uygulamada bazı işlemleri yalnızca giriş yapmış kullanıcılar yapabilsin. Dekoratör kullanmadan şöyle yazarız:

```python
logged_in = False


def show_profile():
    if not logged_in:
        print("You must log in first!")
        return
    print("Showing the profile page.")


def send_message():
    if not logged_in:
        print("You must log in first!")
        return
    print("Message sent.")
```

Bu kodun sorunları:

- Aynı kontrol her fonksiyonda tekrar ediyor.
- Uyarı mesajını değiştirmek için her fonksiyonu tek tek düzeltmek gerekiyor.
- Bir fonksiyonda kontrolü unutmak kolay. Unutulursa giriş yapmamış biri o işlemi yapabilir.
- Fonksiyonun asıl işi, kontrol kodunun arasında kayboluyor.

### 3.2 Çözüm: kontrolü bir dekoratöre taşımak

Dosyanın adı `why_decorator.py`. Kontrolü bir kez, dekoratörün içine yazıyoruz:

```python
logged_in = False


def login_required(original_function):
    def checked():
        if not logged_in:
            print("You must log in first!")
            return
        original_function()
    return checked
```

Her fonksiyona yalnızca `@login_required` satırını ekliyoruz:

```python
@login_required
def show_profile():
    print("Showing the profile page.")


@login_required
def send_message():
    print("Message sent.")
```

Deneyelim:

```python
print("--- Before logging in ---")
show_profile()
send_message()

print("--- After logging in ---")
logged_in = True
show_profile()
send_message()
```

```text
--- Before logging in ---
You must log in first!
You must log in first!
--- After logging in ---
Showing the profile page.
Message sent.
```

Kontrol artık tek yerde duruyor ve her fonksiyon yalnızca kendi işini yapıyor.

Bu örnekte sarmalayıcı fonksiyon (`checked`) yeni bir şey yapıyor: Asıl fonksiyonu çağırıp çağırmamaya kendisi karar veriyor. Giriş yoksa `return` ile çıkıyor ve asıl fonksiyon hiç çalışmıyor.

### 3.3 Yardımcı bir fonksiyon çağırsak yetmez mi?

Akla gelen ilk seçenek, kontrolü bir fonksiyona koyup her fonksiyonun başında çağırmaktır. Dosyanın adı `helper_function_trap.py`:

```python
logged_in = False


def check_login():
    if not logged_in:
        print("You must log in first!")
        return


def delete_account():
    check_login()
    print("Account deleted.")


delete_account()
```

```text
You must log in first!
Account deleted.
```

Giriş yapılmadığı hâlde hesap silindi. Çünkü `check_login` içindeki `return` yalnızca `check_login` fonksiyonundan çıkar; `delete_account` çalışmaya devam eder.

Bunu düzeltmek için her fonksiyona `if not check_login(): return` gibi bir satır eklemek gerekir. Bu da tekrarı ve unutma riskini geri getirir.

| Yardımcı fonksiyon | Dekoratör |
|---|---|
| Fonksiyonun içinden çağrılır. | Fonksiyonu dışarıdan sarar. |
| Yalnızca uyarı verebilir. | Asıl fonksiyonun çalışıp çalışmayacağına kendisi karar verir. |

Bir iki fonksiyonluk basit işlerde yardımcı fonksiyon yeterlidir. Aynı kural birçok fonksiyona uygulanacaksa dekoratör daha güvenlidir.

### 3.4 Yaygın kullanım alanları

| Kullanım | Dekoratör ne yapar? |
|---|---|
| Yetki kontrolü | "Bu kişi bu işlemi yapabilir mi?" diye bakar. |
| Süre ölçme | Fonksiyonun ne kadar sürdüğünü hesaplar. |
| Günlük tutma (log) | Hangi fonksiyonun ne zaman çalıştığını not eder. |
| Önbellek (cache) | Aynı hesaplama tekrar istenirse sonucu hafızadan verir. |
| Yol kaydı (API) | "Bu yola istek gelince bu fonksiyon çalışsın" diye not eder. |

Tablonun son satırı, FastAPI'nin yaptığı iştir.

---

## 4. FastAPI'nin dekoratörü nasıl çalışır?

### 4.1 Restoran benzetmesi

```text
Müşteri (tarayıcı) ──── GET /book/42 ────►  Garson (FastAPI)
                                                 │
                                                 │ 1. Yol defterine bakar:
                                                 │    /book/42 → get_book
                                                 ▼
                                            Aşçı (get_book)
                                                 │
                                                 │ 2. Yemeği hazırlar:
                                                 │    return book
                                                 ▼
Müşteri (tarayıcı) ◄──── JSON yanıtı ─────  Garson (FastAPI)
```

`@app.get("/book/42")` satırı garsonun yol defterine şu notu yazar: "`/book/42` için `GET` isteği gelirse onu `get_book` hazırlasın."

Aşçıyı müşteri çağırmaz, garson çağırır.

### 4.2 `wrap` ile `app.get` arasındaki iki fark

FastAPI'nin dekoratörü, 2. bölümdeki `wrap` dekoratöründen iki noktada farklıdır.

**Fark 1: Parantez var, çünkü dekoratöre bir yol veriliyor.**

Dekoratöre yalnızca fonksiyon verilir. Yolu da verebilmek için önce yolu alıp bir dekoratör üreten fonksiyon çalışır. Bu, 1.3'teki `make_greeter` fonksiyonunun yaptığı işin aynısıdır: Bir bilgi alır, onu hatırlayan yeni bir fonksiyon üretir.

```python
# @wrap tek adımdır:
greet = wrap(greet)

# @app.get("/book/42") iki adımdır:
register = app.get("/book/42")   # 1. Yolu ver, bir dekoratör al.
get_book = register(get_book)    # 2. Fonksiyonu o dekoratöre ver.
```

**Fark 2: Fonksiyonu sarmaz, yol defterine yazar.**

| | `@wrap` | `@app.get("/book/42")` |
|---|---|---|
| Fonksiyona ne yapar? | Yeni bir fonksiyonla sarar. | Yol defterine yazar. |
| Geri ne verir? | Yeni bir fonksiyon (`wrapped`) | Aynı fonksiyonu, hiç değiştirmeden |

### 4.3 `mini_fastapi`: girişteki sorunun cevabı

Aşağıdaki kod, FastAPI'nin yaptığı işi sade Python ile taklit ediyor. Numaralı `print` satırları yine çalışma sırasını gösteriyor. Dosyanın adı `mini_fastapi.py`.

Yol defteri ve dekoratör:

```python
import json

print("[1] Program started.")

routes = {}  # Yol defteri: hangi yola hangi fonksiyon yanıt verecek?


def get(path):
    print("[3] get() is running. Received path:", path)

    def register(function):
        print("[4] register() is running. Saving in routes:", path, "->", function.__name__)
        routes[path] = function
        return function  # Sarmadan, olduğu gibi geri veriyoruz.

    return register
```

`get`, yolu alır ve bir dekoratör (`register`) üretir. `register`, yolu hatırlar ve fonksiyonu `routes` sözlüğüne, yani yol defterine yazar.

Buradaki `get`, bizim yazdığımız sıradan bir Python fonksiyonu; adını FastAPI'deki `app.get` ile benzesin diye seçtik. HTTP metoduna bakmıyor, yalnızca yolu deftere yazıyor.

Garson:

```python
def handle_request(path):
    print()
    print("[Request] The browser asked for:", path)
    if path in routes:
        function = routes[path]
        result = function()
        print("[Response] 200 OK:", json.dumps(result, ensure_ascii=False))
    else:
        print("[Response] 404 Not Found: No such path.")
```

`handle_request` garsonun işini yapar: Deftere bakar, fonksiyonu bulursa çağırır ve sonucu JSON metnine çevirir.

`server.py` dosyasının sade Python hâli:

```python
print("[2] get and handle_request are defined. Next comes @get.")

book = {
    "id": 42,
    "title": "API Yolculuğu",
    "author": "Deniz Kaya"
}


@get("/book/42")
def get_book():
    print("           get_book() is running, returning the book.")
    return book


print("[5] Paths in routes:", list(routes))
print("[6] Note: we never called get_book() ourselves!")

handle_request("/book/42")
handle_request("/book/99")
```

Son iki satır, tarayıcıdan gelen iki isteği taklit ediyor.

Çıktı:

```text
[1] Program started.
[2] get and handle_request are defined. Next comes @get.
[3] get() is running. Received path: /book/42
[4] register() is running. Saving in routes: /book/42 -> get_book
[5] Paths in routes: ['/book/42']
[6] Note: we never called get_book() ourselves!

[Request] The browser asked for: /book/42
           get_book() is running, returning the book.
[Response] 200 OK: {"id": 42, "title": "API Yolculuğu", "author": "Deniz Kaya"}

[Request] The browser asked for: /book/99
[Response] 404 Not Found: No such path.
```

> **Girişteki sorunun cevabı:** `get_book` fonksiyonunu biz çalıştırmıyoruz, garson çalıştırıyor. `@get("/book/42")` satırı, program başlarken fonksiyonu deftere yazdı (`[3]` ve `[4]`). İstek gelince garson deftere baktı ve fonksiyonu kendisi çağırdı. Defterde olmayan `/book/99` için yanıt `404` oldu.

---

## 5. Gerçek FastAPI'de aynı parçalar

### 5.1 `server.py` ile `mini_fastapi.py` karşılaştırması

Sunucuyu ve istemciyi föyün Deney 1 ve 2'sindeki gibi çalıştırıyoruz. `server.py` dosyasının parçalarının `mini_fastapi.py` dosyasındaki karşılıkları:

| `server.py` | `mini_fastapi.py` |
|---|---|
| `app = FastAPI()` | `routes = {}` defteri ve `handle_request` garsonu |
| `@app.get("/book/42")` | `@get("/book/42")` |
| FastAPI'nin içindeki kayıt dekoratörü | `register` |
| Sözlüğün kendiliğinden JSON'a çevrilmesi | `json.dumps(result)` |
| Deftere yazılmamış yola `404` yanıtı | `else` bloğundaki `404` |
| `client.py` dosyasının gönderdiği gerçek istek | `handle_request("/book/42")` çağrısı |

`app` nesnesi defteri ve garsonu içinde taşır. Bu yüzden `get` yerine `app.get` yazarız.

FastAPI'nin defteri, bizim defterimizden bir bilgi fazla tutar: HTTP metodunu. `app.get(...)` deftere "`GET` isteği gelirse" diye yazar; Hafta 2'de göreceğimiz `app.post(...)` da aynı şekilde "`POST` isteği gelirse" diye yazar.

### 5.2 Dekoratörsüz kayıt

FastAPI'de aynı kaydı dekoratör kullanmadan da yapabiliriz. Aşağıdaki `server.py`, `@app.get("/book/42")` ile aynı kaydı yapar:

```python
from fastapi import FastAPI

app = FastAPI()

book = {
    "id": 42,
    "title": "API Yolculuğu",
    "author": "Deniz Kaya"
}


def get_book():
    return book


app.add_api_route("/book/42", get_book, methods=["GET"])
```

Bu sunucuyla `/book/42` isteği yine `200` ve kitabın bilgilerini, `/book/99` isteği yine `404` ve `{"detail":"Not Found"}` döndürür. Demek ki `@app.get(...)` satırı, bu kaydın kısa yazımıdır.

### 5.3 Defteri tarayıcıda görmek

Sunucu açıkken tarayıcıda `http://127.0.0.1:8000/docs` adresini aç. FastAPI'nin kendiliğinden hazırladığı bu sayfada `GET /book/42` satırı listelenir. Bu liste, dekoratörün deftere yazdığı yollardır. **Try it out** düğmesiyle sayfadan istek de gönderebilirsin.

---

## 6. Pekiştirme

### 6.1 Sık yapılan hatalar

| Hata | Belirti | Çözüm |
|---|---|---|
| Dekoratörün sonunda `return wrapped` satırını unutmak | `greet()` çağrılınca `TypeError: 'NoneType' object is not callable` | Dekoratörün sonunda ürettiği fonksiyonu `return` ile geri ver. |
| Fonksiyonu verirken parantez koymak: `wrap(greet())` | `greet` hemen çalışır; `wrap` fonksiyona değil, `greet` fonksiyonunun döndürdüğü `None` değerine sahip olur. | Fonksiyonu parantezsiz ver: `wrap(greet)` |
| İstekteki yolu farklı yazmak: `/books/42` | `404 Not Found` | İstekteki yolun dekoratördeki yolla birebir aynı olduğunu kontrol et. |

### 6.2 Alıştırmalar

1. `what_is_decorator.py` dosyasında `@wrap` satırını silip çalıştır. Çıktıda ne değişti? Neden?
2. Fonksiyonun kaç saniye sürdüğünü yazan `@measure_time` adında bir dekoratör yaz. İpucu: `import time` ve `time.time()`.
3. `server.py` dosyasına ikinci bir kitap ve `/book/7` yolu ekle. `/docs` sayfasında yeni yolun göründüğünü kontrol et. İpucu: Yeni yol için farklı adda bir fonksiyon yaz.
4. `client.py` dosyasını `/book/99` yoluna istek gönderecek şekilde değiştir. Durum kodu ve gelen veri ne oldu?
5. `mini_fastapi.py` dosyasına `post` adında ikinci bir dekoratör ekle. İpucu: Defterde yolla birlikte HTTP metodu da tutulmalı: `routes[("POST", path)]`.

### 6.3 Sıradaki adım: değişen yollar

Şu an her kitap için ayrı bir yol ve ayrı bir fonksiyon yazmamız gerekiyor. Föyün Deney 5'inde dekoratörü `@app.get("/book/{book_id}")` biçiminde yazıyoruz; yolun bir kısmı değişken oluyor.

Bu yapıda `/book/42` ve `/book/7` istekleri aynı fonksiyona gelir; `book_id` değeri yoldan okunur. Defterde artık tek bir kalıp durur: `/book/{book_id}`.

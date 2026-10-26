# Ek Not — 6.3'ün Cevabı: Belgenin Eksik İki Bölümü

Bu not, föyün 6.3 bölümündeki alıştırmanın cevabıdır. Önce belgeni kendin tamamla, sonra buradaki cevapla karşılaştır.

Aşağıdaki iki bölüm `README.md` dosyasının sonuna eklenir. Yanıtlar, sunucu yeniden başlatıldıktan sonra gönderilen isteklerden alındı. Sunucu dosyada yazılı bir yorumla başladığı için, eklenen ilk yorumun kimliği `2` olur.

````markdown
### Bütün kitapları listelemek

```bash
curl http://127.0.0.1:8000/books
```

Yanıt: `200 OK`

```json
[{"id":42,"title":"API Yolculuğu","author":{"first_name":"Deniz","last_name":"Kaya"},"available":true,"tags":["software","education"],"rating":null},{"id":57,"title":"Veriyle İlk Adımlar","author":{"first_name":"Ece","last_name":"Yılmaz"},"available":false,"tags":[],"rating":0},{"id":73,"title":"Python ile Web API","author":{"first_name":"Can","last_name":"Demir"},"available":true,"tags":["python","api"],"rating":4.5}]
```

Kitapları adına göre aramak ve ödünç durumuna göre süzmek için `search` ve `available` sorgu parametreleri kullanılır:

```bash
curl "http://127.0.0.1:8000/books?search=Python&available=true"
```

```json
[{"id":73,"title":"Python ile Web API","author":{"first_name":"Can","last_name":"Demir"},"available":true,"tags":["python","api"],"rating":4.5}]
```

Aramaya uyan kitap yoksa yanıt yine `200 OK` olur; gövde boş bir liste olur: `[]`

### Bir kitaba yorum eklemek

```bash
curl -X POST http://127.0.0.1:8000/books/42/reviews -H "Content-Type: application/json" -d '{"reader": "Can", "comment": "İlk API projemi bu kitapla yazdım.", "score": 4}'
```

Yanıt: `201 Created`

```json
{"reader":"Can","comment":"İlk API projemi bu kitapla yazdım.","score":4,"id":2,"book_id":42}
```

`reader`, `comment` ve `score` alanları zorunludur. Eksik ya da yanlış türde bir alan gönderilirse yanıt `422 Unprocessable Entity` olur.

Kitap yoksa yanıt `404 Not Found` olur: `{"detail":"Book not found"}`
````

Listelemede hata durumu yoktur: Aramaya uyan kitap olmasa bile yanıt `200` olur. Boş liste "bulunamadı" demek değil, "sonuç yok" demektir. Yorum eklemede ise iki hata durumu vardır: kitap yoksa `404`, gövde modele uymuyorsa `422`.

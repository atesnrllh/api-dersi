# Ek Not — URL Notundaki Soruların Cevapları

Bu not, [URL ek notunun](03_Supplement_URL.md) 7. ve 8. bölümlerindeki soruların cevaplarıdır. Önce kendin dene ve cevaplarını yaz, sonra buradakilerle karşılaştır.

---

## 7. Dene

1. ve 3. denemelerin sonucu, seçtiğin adrese ve şehre göre değişir; bu yüzden burada cevapları yok.

| Deneme | Ne olur? |
|---|---|
| **2.** `forecast_days` değeri `3` | Üç gün gelir; `daily` içindeki her dizi üç eleman içerir. |
| **4.** `latitude` değeri `100` | `400` durum kodu ve `{"reason":"Latitude must be in range of -90 to 90°. Given: 100.0.","error":true}` gövdesi gelir. Open-Meteo da gelen değeri kontrol ediyor ve bu hata için `400` kullanıyor; FastAPI ise tür hatalarında `422` kullanır. Hangi durum kodunun kullanılacağına API'yi yazan karar verir. Ortak nokta, hatanın istemcinin gönderdiği veriden kaynaklanmasıdır. |
| **5.** `127.0.0.1` yerine `localhost` | Sonuç değişmez; `localhost` ile `127.0.0.1` aynı bilgisayarı gösterir. |
| **6.** Port yazmadan istek | `httpx.ConnectError: [Errno 111] Connection refused` gelir. Port yazılmadığı için istek 80 numaralı kapıya gider; orada bekleyen bir program yoktur. |
| **7.** İnternet bağlantısı kapalıyken | `Request failed: Check your internet connection.` mesajı çıkar. Alan adı çözülemediği ya da bağlantı kurulamadığı için `httpx.RequestError` yakalanır. |

---

## 8. Tartışma soruları

| Soru | Cevap |
|---|---|
| **1.** Yol ve sorgu hangi kısımdır? | Yol `/v1/forecast`, sorgu `latitude=41.27976` kısmıdır. |
| **2.** Open-Meteo adresinde port neden yazmıyor? | Şema `https` olduğu için varsayılan port `443` kullanılır. |
| **3.** `127.0.0.1` ile `api.open-meteo.com` arasındaki fark nedir? DNS ne işe yarar? | `127.0.0.1` bu bilgisayarı gösteren bir IP adresidir. `api.open-meteo.com` bir alan adıdır; DNS bu adı bağlanılacak IP adresine çevirir. |
| **4.** Adresin hangi parçaları bağlantı için, hangileri istek mesajında kullanılır? | Şema, sunucunun adresi ve port bağlantıyı kurmak için kullanılır. Yol ve sorgu istek mesajının içinde gider. |
| **5.** İki istemci kodunda ne değişti, ne aynı kaldı? | Değişen yalnızca adres, sorgu parametreleri ve bekleme süresidir. İstek yine `httpx.get(...)` ile gönderilir, yanıt yine durum kodu ve JSON gövdeden oluşur, `response.json()` yine sözlük verir. |
| **6.** Kitap kimliği neden yolda, konum neden sorguda? | Kitap kimliği hangi kaynağın istendiğini belirtir, bu yüzden yoldadır. Konum ise tahmin işleminin bir ayarıdır, bu yüzden sorgudadır. Bu bir tasarım tercihidir. |
| **7.** `timeout` neden artırıldı? | İnternetteki bir sunucunun yanıtı ağın durumuna göre gecikebilir; HTTPX'in varsayılan 5 saniyesi yetmeyebilir. |

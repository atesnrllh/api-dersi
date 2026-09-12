# Ders İçeriğini Hazırlama ve Gözden Geçirme Yaklaşımı

**Çıkış noktası:** Birinci haftanın uygulaması ve ders sırasında konuşulan sorular.  
**Durum:** Üzerinde çalışılıyor — 12 Eylül 2026

Birinci hafta yalnızca öğrenilmiş konuların listesi değildir; öğrencinin bu konulara hangi örneklerle ve hangi büyüklükte adımlarla ulaştığını gösterir. Yeni haftaların temposu bu çalışma üzerinden belirlenir.

## 1. Birinci haftadan alınan ölçüt

| Birinci haftada yaptığımız | Sonraki haftalar için anlamı |
|---|---|
| Önce tek kitabın başlığını aldık; sonra yanıt kodunu ve gövdesini görünür yaptık. | Tanımdan önce öğrencinin inceleyebileceği somut bir sonuç ver. |
| Sunucuya `available`, `tags`, `rating` alanlarını ayrı ayrı ekledik. | Bir adımın merkezinde tek bir yeni kavram olsun; kod satırı sayısı tek ölçüt değildir. |
| Yeni alanın gelmesiyle istemcide gösterilmesini ayrı ele aldık. | Verinin taşınması ile yazılımın veriyi kullanmasını ayır. |
| `null`, `0`, `false` ve boş listeyi karşılaştırdık. | Benzer görünen sonuçların anlam farkını örnek üzerinden kur. |
| Bir filtreyi değiştirip sonucu yeniden okuduk. | Mümkün olduğunda bir seferde tek koşulu değiştir; sonucu hangi değişikliğin doğurduğu belli olsun. |
| `404`, `422` ve bağlantı kurulamamasını konuştuk. | Hata çıktısını bir öğrenme örneği yap; sadece düzeltme komutunu verme. |
| Takıldığımız soruları yeniden açıkladık. | Açıklamaları gerçek öğrenci sorularına göre geliştir; soru sayısını artırmayı öğrenme kanıtı sayma. |

## 2. Yeni bir hafta hazırlanırken izlenecek sıra

1. Önce önceki haftanın **uygulamasını** incele: öğrenci ne yaptı, hangi kavramı açıklayabildi, nerede yardıma ihtiyaç duydu?
2. Yeni haftanın ihtiyacını aynı örnek üzerinden belirle. İkinci hafta için: “Okuyabildiğimiz kataloğa, istemciden yeni kitap nasıl göndeririz?”
3. **Önce teoriyi hazırla:** Somut ihtiyaç, örnek istek, sunucunun yaptığı iş, örnek sonuç ve bunlardan çıkarılan kavram birbirini izlesin. Teori, henüz uygulamayı çalıştırmamış öğrenci tarafından da izlenebilsin.
4. Bu teoriyi uygulamaya dönüştür: her deneyin amacı, teori bağlantısı, başlangıç durumu, küçük değişikliği ve beklenen gözlemi belli olsun.
5. **Sonra uygulamadan teoriye geri dön:** Uygulamada ortaya çıkan her yeni düşünme adımı teoride açıklanmış mı? Teorideki somut örnekler uygulamada aynı sonuçlara ulaşıyor mu?
6. Eksik bağlantıları düzelt; ardından kodları ve belge düzenini doğrula. Çalışan kod, anlatımın öğrenciye yeterli geldiğinin tek başına kanıtı değildir.

Bu sıra, birinci haftanın teorisinin uygulama ve konuşmalar üzerinden düzenlenmesini; sonraki haftalarda ise önce teori, sonra uygulama yazılıp ikisinin tekrar karşılaştırılmasını birlikte kapsar.

## 3. Her bölüm için yazım ölçütü

- Kavramın adını vermeden önce ihtiyaç veya gözlenebilir bir örnek sun.
- “Başlık mesaj bilgisidir” gibi bir tanımı tek başına bırakma; kimin hangi başlığı gönderdiğini ve öğrencinin nerede okuyacağını göster.
- Bir çıktı için hem ne olduğunu hem API iletişiminde ne anlama geldiğini açıkla.
- İstek, sunucu işlemi, yanıt ve istemcinin gösterimi arasındaki bağı koru.
- Değişen `.py` dosyasını her seferinde tam ver; önceki sürümle farkını ayrı `diff` kutusunda göster.
- Başarılı POST gibi veri değiştiren adımlarda başlangıç verisini ve tekrar çalıştırmanın etkisini yaz.
- Açıklamalar kısa ve yeterli olsun; belgenin uzunluğunu azaltmak için anlamayı sağlayan ara adımı kaldırma.
- Öğrenilen, bu hafta yeni öğretilen ve sonraki haftaya bırakılan konuları açıkça belirt.

## 4. İkinci hafta için yapılan geri karşılaştırma

| Uygulamadaki öğrenme adımı | Teorideki karşılığı | Öğrencinin açıklayabilmesi gereken fark |
|---|---|---|
| Deney 1–5 | Bölüm 1–6 | İstemci, HTTP mesajı, API işlemi, filtre ve yanıt parçaları. |
| Deney 6 ve 7A | Bölüm 7 ve 8.1 | Modelin veri beklentisi; gövdenin alınması ile kaydın oluşturulması. |
| Deney 7B ve 8 | Bölüm 8.2–8.3 | Listeye ekleme, `201`, yeni kimlik ve `Location`. |
| Deney 9 | Bölüm 9 | Aynı isteğin tekrarlanmasının kaynak üzerindeki etkisi. |
| Deney 10–12 | Bölüm 7.3 ve 10 | Eksik alan, `null`, dönüştürülemeyen değer ve JSON yazım hatası. |
| Deney 13A–13B | Bölüm 11.1 | Ham yanıtın gelmesi ile istemcinin alanları yorumlaması. |
| Deney 14–15 | Bölüm 11.2–11.4 | Aynı sunucuyu kullanan istemciler; istemcinin kapanması ile sunucunun yeniden başlaması. |

PUT/PATCH/DELETE ve ileride kullanılacak durum kodları teorinin başvuru bölümündedir; bu hafta uygulanmış veya öğrenme kontrolü tamamlanmış kabul edilmez. Öğrenciyle çalışırken görülen yeni takılmalar, teoriye ve uygulamaya birlikte işlenir.

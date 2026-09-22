# Introduction — API ile gerçek bir hizmeti kullanalım

Bu giriş dersinde önce Open-Meteo sitesinde Samsun'un sıcaklık ve yağış olasılığını inceliyoruz. Ardından aynı hizmetin verilerini küçük bir Python programına alıyoruz.

- [Practice](02_Practice.md): Siteden başlayıp API yanıtına ve çalışan koda ilerleyen ders akışı.
- [Lecture Notes](01_Lecture_Notes.md): Uygulamada gördüğümüz kavramların kısa açıklaması.
- [client.py](client.py): Bugünün tahminini alan örnek program.

## Kodu çalıştırma

Bu gösterim için internet bağlantısı, Python ve HTTPX gerekir. Python ve HTTPX'in hazır olduğu ortamda bu klasörden çalıştır:

```bash
python client.py
```

HTTPX kurulu değilse kullandığın Python ortamına kur:

```bash
python -m pip install -r requirements.txt
```

### Mevcut WSL ortamını kullanıyorsan

Masaüstündeki `book-catalog-api/api-env` ortamı bilgisayarında zaten varsa, `introduction` klasöründeyken etkinleştirebilirsin:

```bash
source ../book-catalog-api/api-env/bin/activate
python client.py
```

`../`, bulunduğun klasörün bir üstünü gösterir. Python ortamının `introduction` klasörünün içinde olması zorunlu değildir. `source api-env/bin/activate` ise doğrudan bu klasörün içinde bir ortam arar; burada oluşturulmamışsa “No such file or directory” hatası verir.

Sınıfta ilk kez başlayan öğrencinin bu eski proje klasörüne sahip olması beklenmez. Introduction gösterimi eğitmenin hazır ortamında yapılabilir; öğrencinin Python ortamı Week 1'de hazırlanır.

Veri: [Open-Meteo](https://open-meteo.com/) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

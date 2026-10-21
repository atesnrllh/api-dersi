# Hafta 5 — Ruby ile Merhaba Dünya

Ruby kodu iki işletim sisteminde de aynıdır. Dosya oluşturma komutu ve masaüstü yolu farklıdır. Ruby'nin yüklü olduğunu `ruby --version` ile kontrol edebilirsiniz.

## Ubuntu

1. Terminalde masaüstünde boş dosya oluşturun:

```bash
touch ~/Masaüstü/Hello.rb
```

Masaüstü klasörünüzün adı İngilizceyse `Masaüstü` yerine `Desktop` yazın.

2. `Hello.rb` dosyasını bir metin düzenleyicide açın, aşağıdaki kodu yazıp kaydedin:

```ruby
puts "Merhaba dünya"
```

3. Terminalden çalıştırın:

```bash
ruby ~/Masaüstü/Hello.rb
```

## Windows (PowerShell)

Windows Terminal içinde PowerShell sekmesini açın. Aşağıdaki masaüstü yolu, OneDrive'a taşınmış masaüstünü de bulur.

1. Masaüstünde boş dosya oluşturun:

```powershell
$masaustu = [Environment]::GetFolderPath('Desktop')
New-Item -Path "$masaustu\Hello.rb" -ItemType File
```

2. Dosyayı Not Defteri ile açın:

```powershell
notepad "$masaustu\Hello.rb"
```

Aşağıdaki kodu yazıp UTF-8 kodlamasıyla kaydedin:

```ruby
puts "Merhaba dünya"
```

3. Aynı PowerShell penceresinde çalıştırın:

```powershell
ruby "$masaustu\Hello.rb"
```

`ruby` komutu tanınmıyorsa Ruby kurulu olmayabilir veya PATH'e eklenmemiş olabilir.

## Beklenen çıktı

```text
Merhaba dünya
```

Bu örnek metni terminale yazdırır. Örnek kod bu klasördeki [Hello.rb](Hello.rb) dosyasında da bulunur.

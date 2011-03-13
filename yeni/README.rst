
Arsiv duzenleyici gelistirme deposu
-----------------------------------

Lisans eklendi(lisanslar hakkında hiçbir fikrim yok, MIT kısa diye onu ekledim 
yardımcı olursanız sevinirim hehe).

Klasor dinleme ozelligi eklendi. Son kullanici icin birkac duzenleme yapilacak.


## Kullanım

* Klasör izleme seçeneği, zaten düzenli olan arşivi izleyerek(düzenli değilse 
ilk önce alttaki seçeneği kullanın) yeni dosya eklenme durumunda gerekli
düzenlemeleri yapar, albüm kapaklarını indirir, çakışmaları düzenler. Testlerime
göre oldukça stabil :) python watcher.py [izlenecek_klasor]
* Direkt düzenleme seçeneği, gösterdiğiniz klasörü düzenler, albüm kapaklarını
indirir, çakışmaları düzenler. Hiçbir dosya kaybolmaz, ID3 etiketlerini
okuyamadığı dosyaları farklı bir klasöre atar. python yeniduzenleyici.py [klasor].


Önceki sürümün sahip olduğu, düzenli hali farklı bir klasöre atma ve arayüz
özellikleri şimdilik yok. Klasör izleme özelliği için tüm yapıyı değiştirmek 
zorunda kaldım. Şimdilik bu kadar.

Bu arada, bir üst klasördeki eski hali çalışıyor. Klasör dinleme özelliği yok ama
onun dışında yukarıda saydığım özellikler var. Nautilus scriptiyle beraber
kullanılabilir.


Eklenecekler:

    * Deamon olarak calisma(yok bu olmadı, system tray'e otursa daha iyi olacak)
    * Arayuz(system tray'den tek tıklamayla ayar ekranına ulaşım)
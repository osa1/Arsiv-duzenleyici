Arsiv duzenleyici
=================

MP3, OGG ve FLAC formatlı dosyalarınızdan oluşan müzik arşivinizi ID3 etiketlerine düzenleyen basit bir python programı.

ID3 etiketlerini okumak için mutagen kullandım: http://code.google.com/p/mutagen/

Etiketi bulunmayan veya formata(mp3, ogg, flac) uymayan dosyaları ayrı bir klasöre taşır veya kopyalar.

mechanize(http://wwwsearch.sourceforge.net/mechanize/) kütüphanesinin bulunması durumunda albüm kapaklarını indirebilir.


Icindekiler
-----------

 * gui.py - Arayuzlu duzenleyici, kapak indirme ozelligi eklendi.
 * osa1.py - Nautilus scripti icin, arayuzsuz. Kurulum yapilmasi lazim.
 * Arsiv Duzenle - Nautilus scriptleri, ~/.gnome2/nautilus-scripts altina atilmalilar. Once programin kurulu olmasi lazim.

Diger
-----

An itibariyle yeni klasorundeki yeni(?!) hali calisiyor. watcher.py, kaynak kodda belirtilen(duzeltilecek) klasoru izleyip, ekleme halinde otomatik duzenleme yapar, duzenleme sonrasi bos klasorleri temizler, album kapaklarini indirir(kucuk bir istisna disinda, duzeltilecek).

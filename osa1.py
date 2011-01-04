#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Osa1 Arsiv duzenleme scripti!

Scriptin amacı basitce mp3, flac ve ogg formatli muzik
arsivinizi duzenlemektir. Iki farkli yol izleyebilir:

* Arsivinize dokunmadan, yeni bir klasor olusturur ve
duzenlemeleri oraya yapar.

* Arsivinizdeki dosyalari tasiyarak duzenler.

Kopyalama ve tasima islemleri icin shutil kullanilmistir.

Oneri, tavsiye, elestiri ve hatalari lutfen
omeragacan@gmail.com adresine yazin.

KULLANIM:
osa1.py arsiv_konumu, duzenli_arsivin_kopyalanacagi_konum

Detayli bilgi icin http://www.osa1.net
"""
import os
from shutil import copy, move
from sys import argv, exit, stderr
from mutagen.easyid3 import EasyID3 as id3
from mutagen.flac import Open as flac
from mutagen.oggvorbis import Open as ogg

def _help():
    print __doc__

def kontrol(b):
    """
    Dosya cakismalarini onler.
    Eger ayni dosyadan varsa isminin basina '_' ekler.
    """
    if os.path.isfile(b):
        _b = b.split(os.path.sep)
        b = os.sep.join(_b[:-1]) + os.path.sep + "_" + _b[-1]
    return b

def cp(a, b):
    "Shutil.copy kullanarak kopyalama yapar. Once cakisma icin konrol eder."
    copy(a, kontrol(b))

def yurut(a, b):
    "Shutil.move kullanarak kopyalama yapar. Once cakisma icin kontrol eder."
    move(a, kontrol(b))

def duzenle(yer, hedef, yontem=cp):
    """
    Ana fonksiyon. Yer'deki tum dosyalari os.walk yardimi ile gezer.
    Formata uyan dosyalarin bilgilerini Mutagen yardimiyla okur.
    Gerekli klasorleri olusturur, belirtilen yonteme gore tasir veya kopyalar.
    """
    if not os.path.isdir(yer):
        print u"Arsiv konumu hatali."
        exit()
    if not os.path.isdir(hedef):
        os.mkdir(hedef)
        print u"Hedef klasor olusturuluyor.."
    errors = []
    songs = 0
    supported_formats = ["mp3", "flac", "ogg"]
    for ana_dizin, dizinler, dosyalar in os.walk(yer):
        for dosya in dosyalar:
            Format = dosya.split(".")[-1]
            if Format in supported_formats:
                _dosya = os.path.join(ana_dizin, dosya)
                print _dosya,
                try:
                    if Format == "mp3": dosya = id3(_dosya)
                    elif Format == "flac": dosya = flac(_dosya)
                    elif Format == "ogg": dosya = ogg(_dosya)
                    songs += 1
                    artist = dosya["artist"][0].replace("/", "-")
                    album = dosya["album"][0].replace("/", "-")
                    title = dosya["title"][0].replace("/", "-")
                    try:
                        os.makedirs(os.path.join(hedef, artist, album))
                    except OSError:
                        pass
                    yontem(_dosya, "%s.%s" % (os.path.join(hedef, artist, album, title),
                                              Format))
                    print "tamam.."
                except:
                    errors.append(_dosya)
                    print "hata.."
            else:
                errors.append(os.path.join(ana_dizin, dosya))

    print "digerleri..",
    for dosya in errors:
        try:
            os.mkdir(os.path.join(hedef, "_DIGER"))
        except:
            pass
        _hedef = os.path.join(hedef, "_DIGER")
        yeni = dosya.split(os.path.sep)[-1]
        yontem(dosya, os.path.join(_hedef, yeni))
        songs += 1
    print "tamam.."

    print "log dosyasi..",
    log = open(os.path.join(hedef, "log.txt") , "w")
    log.write("%s kopyalandi.\n\n" % songs)
    error_count = 0
    for error in errors:
        error_count += 1
        log.write("%s\n" % error)
    log.write("\n\ttoplam: %s hata." % error_count)
    log.close()
    print "tamam.."

if __name__ == "__main__":
    if len(argv) != 3:
        _help()
        exit()
    yer = argv[1]
    hedef = argv[2]
    duzenle(yer, hedef)


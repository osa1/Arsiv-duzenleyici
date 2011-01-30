#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import gobject
import urllib2
import threading
from mutagen.easyid3 import EasyID3 as id3
from mutagen.flac import Open as flac
from mutagen.oggvorbis import Open as ogg

class Duzenleyici:
    def __init__(self, yer, hedef, method, gui=None, cover=False):
        self.gui = gui
        self.yer = yer
        self.hedef = hedef
        self.method = method
        self.errors = []
        self.songs = 0
        self.cover = cover
        self.supported_formats = ['mp3', 'flac', 'ogg']
        self.logfile = True

        # (for listener)
        # a list for folders created by organizer
        # with this, we can prevent trying to organize already organized folders
        self.created_folders = []

    def control(self):
        if not os.path.isdir(self.yer):
            self.gui.printg(u'Arsiv konumu hatali.\n')
            return False
        if not os.path.isdir(self.hedef):
            self.gui.printg(u'Hedef klasor olusturuluyor.. ')
            os.mkdir(self.hedef)
            self.gui.printg(u' OK\n')
        return True

    def main(self, dosyalar=None):
        for ana_dizin, dizinler, dosyalar in os.walk(self.yer):
            for dosya in dosyalar:
                self.organize(ana_dizin, dosya)
                yield True

        self.download_albumcover()
        self.handle_errors()
        yield False

    def organize(self, ana_dizin, dosya):
        Format = dosya.split(".")[-1]
        if Format in self.supported_formats:
            _dosya = os.path.join(ana_dizin, dosya)
            #if self.hedef in ana_dizin and self.hedef != self.yer:
                #continue
            self.gui.printg("%s " % _dosya)
            try:
                if Format == "mp3":
                    dosya = id3(_dosya)
                elif Format == "flac":
                    dosya = flac(_dosya)
                elif Format == "ogg":
                    dosya = ogg(_dosya)
                self.songs += 1
                artist = dosya["artist"][0].replace("/", "-")
                album = dosya["album"][0].replace("/", "-")
                title = dosya["title"][0].replace("/", "-")
                try:
                    os.makedirs(os.path.join(self.hedef, artist, album))
                    self.created_folders.append(os.path.join(
                        self.hedef, artist))
                except OSError:
                    pass
                #print "////////////////////////", self.created_folders
                self.method(_dosya, "%s.%s" %
                        (os.path.join(self.hedef, artist, album, title),
                            Format))
                self.update_counter()
                self.gui.printg("ok..\n")
            except:
                self.errors.append(_dosya)
                self.gui.printg("error..\n")
        else:
            self.errors.append(os.path.join(ana_dizin, dosya))

    def download_albumcover(self):
        if self.cover:
            ad = AlbumArtDownloader(self.gui)
            task = ad.scan(self.hedef)
            gobject.idle_add(task.next)

    def update_counter(self):
        self.gui.inc_counter()

    def handle_errors(self):
        self.gui.printg("others.. ")
        for dosya in self.errors:
            try:
                os.mkdir(os.path.join(self.hedef, "_OTHERS"))
            except:
                pass
            _hedef = os.path.join(self.hedef, "_OTHERS")
            yeni = dosya.split(os.path.sep)[-1]
            self.method(dosya, os.path.join(_hedef, yeni))
            self.update_counter()
            self.songs += 1
        self.gui.printg("ok..\n")

        if self.logfile:
            self.gui.printg("log file.. ")
            log = open(os.path.join(self.hedef, "log.txt"), "w")
            log.write("%s copied.\n\n" % self.songs)
            error_count = 0
            for error in self.errors:
                error_count += 1
                log.write("%s\n" % error)
            log.write("\n\ttotal: %s error." % error_count)
            log.close()
            self.gui.printg("ok..\n")
        self.gui.update_statusbar("Done.")

    def run(self):
        self.control()
        if isinstance(self.yer, list):
            backup = self.yer
            for s in backup:
                self.yer = s
                for x in self.main:
                    pass
        else:
            for x in self.main:
                pass
        self.handle_errors()


class AlbumArtDownloader:
    def __init__(self, gui):
        import mechanize
        self.gui = gui
        self.pattern = re.compile(r':(http://[a-zA-Z0-9\-\\/._]*)')
        self.br = mechanize.Browser()
        self.br.open('http://images.google.com')
        self.br.select_form(nr=0)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]  # lulz
        self.br.set_handle_equiv(False)
        self.br.set_handle_robots(False)
        self.sayac = 0
        assert self.br.title() == "Google Images"

    def scan(self, place):
        self.place = place
        artists = [folder for folder in os.listdir(self.place) if os.path.isdir(
            os.path.join(self.place, folder))]
        albums = []

        for artist in artists:
            p = os.path.join(self.place, artist)
            for album in os.listdir(p):
                t = os.path.join(p, album)
                if os.path.isdir(t):
                    files = os.listdir(t)
                    if "cover.jpg" in files or "cover.png" in files or "cover.gif" in files:
                        pass
                    else:
                        albums.append("%s:::%s" % (artist, album))

        for album in albums:
            self.download_albumart(album)
            self.gui.update_statusbar("Downloading %s album cover." %
                    album.split(":::")[1])
            yield True
        yield False

    def download_albumart(self, album):
        self.br.select_form(nr=0)
        self.br["q"] = "%s %s" % (album.split(":::")[0],
                album.split(":::")[1])
        response = self.br.submit()
        html = response.read()
        for url in self.pattern.findall(html):
            if "tinypic" in url:
                continue
            elif not ".jpg" in url and not ".gif" in url and not ".png" in url:
                continue
            break

        try:
            url  # check url
            print url
        except:
            return  # there is no image for this album

        threading.Thread(target=self.save_image, args=(url, album)).start()
        self.sayac += 1
        self.br.back()

    def save_image(self, url, album):
        artist, album = album.split(":::")
        try:
            image = urllib2.urlopen(url)
        except:  # urllib2.HTTPError, urllib2.URLError, ...
            return

        # f = url.split(".")[-1] format bulamk icin daha etkili bir yol?
        if ".jpg" in url:
            f = ".jpg"
        elif ".gif" in url:
            f = ".gif"
        elif ".png" in url:
            f = ".png"
        else:
            f = ""
        with open(os.path.join(self.place, artist, album, "cover%s" % f),
                "w") as cover:
            cover.write(image.read())
        self.sayac -= 1
        if self.sayac == 0:
            self.gui.update_statusbar("Done.")

class DummyGui:
    def printg(self, text):
        print text

    def update_statusbar(self, text):
        print text

    def inc_counter(self):
        pass


if __name__ == "__main__":
    from main import cp, yurut
    import sys
    if len(sys.argv) == 4:
        yer, hedef, method = sys.argv[1:]
        method = cp if method == "cp" else yurut

        gui = DummyGui()
        d = Duzenleyici(yer, hedef, method, gui, False)
        d.control()
        task = d.main()
        while True:
            try:
                task.next()
            except StopIteration:
                print "stopiteration"
                break
        ad = AlbumArtDownloader(gui)
        task = ad.scan(hedef)
        while True:
            try:
                task.next()
            except StopIteration:
                print "stopiteration"
                break

    else:
        print "lol"

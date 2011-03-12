#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import shutil
import urllib2
import threading
from sys import argv
from shutil import rmtree
from mutagen.flac import Open as flac
from mutagen.oggvorbis import Open as ogg
from mutagen.easyid3 import EasyID3 as id3


class Organizer:
    def __init__(self, archive, ui, cover=False):
        self.__errors = []
        self.__supported_formats = ['mp3', 'flac', 'ogg']
        self.archive = archive
        self.ui = ui 
        if cover:
            self.cover = AlbumArtDownloader(self.ui)
        else:
            self.cover = False 
        self.songs = 0

    def check_folder(self, folder):
        """Checks if there is a folder and creates if there isn't.
        returns false if target is a file."""
        if not os.path.exists(folder):
            os.mkdir(folder)
            self.ui.printg('Target folder created.')
            return True

        if not os.path.isdir(folder):
            self.ui.printg('Target is a file.')
            return False

        return True

    def __cmethod(self, source, dest, method):
        if (os.path.isdir(source)):
            return False
        try:
            method(source, dest)
        except shutil.Error:
            pass
        return True

    def __organize_folder(self, folder, method, target_folder=None):
        created_folders = set()
        if not target_folder:
            target_folder = folder

        for root, folders, files in os.walk(folder):
            if target_folder in root and target_folder != folder:
                # this folder is already organized
                continue

            for f in files:
                frmt = f.split('.')[-1]
                f = os.path.join(root, f)
                if not frmt in self.__supported_formats:
                    self.__errors.append(f)
                    continue
                self.ui.printg(f)
                # try ?
                if frmt == 'mp3':
                    f_attr = id3(f)
                elif frmt == 'flac':
                    f_attr = flac(f)
                elif frmt == 'ogg':
                    f_attr = ogg(f)
                self.songs += 1
                artist = f_attr['artist'][0].replace('/', '-')
                album = f_attr['album'][0].replace('/', '-')
                title = f_attr['title'][0].replace('/', '-')
                try:
                    os.makedirs(os.path.join(self.archive, artist, album))
                except OSError:  # there is already a folder
                    pass
                self.__cmethod(f, '%s.%s' % (
                    os.path.join(self.archive, artist, album, title), frmt), method)
                created_folders.update([os.path.join(self.archive, artist)])

        # buraya dikkat
        created_folders.update([self.__handle_errors(method, self.archive)])
        if self.cover:
            self.__download_albumcover(created_folders)
        self.clean(self.archive)
        return created_folders

    def __download_albumcover(self, created_folders):
        for artist in created_folders:
            if not os.path.isdir(artist):
                continue
            for album in os.listdir(os.path.join(self.archive, artist)):
                if not os.path.isdir(os.path.join(self.archive, artist)):
                    continue
                artist = os.path.split(artist)[-1]
                print "%s:::%s (arsiv: %s)" % (artist, album, self.archive)
                self.cover.download_albumart("%s:::%s" % (artist, album), self.archive)

    def __organize_file(self, f, method, target_folder=None):
        created_folders= set()
        if not target_folder:
            target_folder = os.path.dirname(f)

        frmt = f.split('.')[-1]
        if frmt not in self.__supported_formats:
            self.__errors.append(f)
            created_folders.update([self.__handle_errors(method, target_folder)])
            return created_folders

        if frmt == 'mp3':
            f_attr = id3(f)
        elif frmt == 'flac':
            f_attr = flac(f)
        elif frmt == 'ogg':
            f_attr = ogg(f)
        self.songs += 1
        artist = f_attr['artist'][0].replace('/', '-')
        album = f_attr['album'][0].replace('/', '-')
        title = f_attr['title'][0].replace('/', '-')
        try:
            os.makedirs(os.path.join(self.archive, artist, album))
        except OSError:
            pass
        self.__cmethod(f, '%s.%s' % (
            os.path.join(self.archive, artist, album, title), frmt), method)
        created_folders.update([os.path.join(self.archive, artist)])
        self.clean(self.archive)
        return created_folders

    def organize(self, f, method, target_folder=None):
        """Moves/copies(or does what method provides) the song(s) to target folder.
        Returns set of created folders."""
        if os.path.isdir(f):
            return self.__organize_folder(f, method, target_folder)
        return self.__organize_file(f, method, target_folder)

    def __handle_errors(self, method, target_folder):
        error_folder = os.path.join(target_folder, '_ERRORS')
        if not self.check_folder(error_folder):
            return
        for f in self.__errors:
            self.ui.printg("err folder: ")
            self.ui.printg(error_folder)
            method(f, error_folder)
        self.__errors = []
        return error_folder

    def clean(self, target):
        """Removes empty folders. Recursively."""
        l = os.listdir(target)
        for f in l:
            addr = os.path.join(target, f)
            if os.path.isdir(addr) and not self.count_files(addr):
                rmtree(os.path.join(target, f))

    def count_files(self, folder):
        """Recursively counts files in a folder. Does not count folders."""
        r = 0
        l = os.listdir(folder)
        if not l:
            return r
        for f in l:
            if os.path.isdir(os.path.join(folder, f)):
                r += self.count_files(os.path.join(folder, f))
            else:
                r += 1
        return r

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
        """Scans already organized folder tree and downloads album covers."""
        if not os.path.isdir(place):
            print "scan error"
            return
        self.place = place
        artists = [folder for folder in os.listdir(self.place) if os.path.isdir(
            os.path.join(self.place, folder)) and not '_ERRORS' in folder]
        albums = []

        print "---------------------------"
        print "artists: ",
        print artists 
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
            # for gtk
            #yield True
        #yield False

    def download_albumart(self, album, place=None):
        """Download album cover of artist:::album and save it."""
        if place:
            self.place = place
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

        threading.Thread(target=self.__save_image, args=(url, album)).start()
        self.sayac += 1
        self.br.back()

    def __save_image(self, url, album):
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
    """DumyGui to run script without a gui."""
    def printg(self, text):
        print text

    def update_statusbar(self, text):
        print text

    def inc_counter(self):
        pass

if __name__ == "__main__":
    # argparse kullanilabilir
    if len(argv) != 2:
        print "to use watcher: watcher.py folder-to-watch"
        print "to organize   : yeniduzenleyici.py folder-to-organize"
        exit(2)

    dg = DummyGui()
    aad = AlbumArtDownloader(dg)
    yer = argv[1]
    org = Organizer(yer, dg)

    org.organize(yer, shutil.move)
    aad.scan(yer)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gtk
import os
import re
import threading
import urllib2
from shutil import copy, move, rmtree
from sys import argv, exit, stderr
from mutagen.easyid3 import EasyID3 as id3
from mutagen.flac import Open as flac
from mutagen.oggvorbis import Open as ogg
import gobject

logfile = True


class Gui:
    def __init__(self):
        self.method = cp
        self.window = gtk.Window()
        self.window.connect("destroy", self.close)
        self.window.move(500, 10)
        self.window.set_title("\o/")
        self.window.set_default_size(400, 400)
        self.window.set_border_width(5)

        vbox = gtk.VBox(False, 8)
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC,
                                       gtk.POLICY_AUTOMATIC)
        self.textbuffer = gtk.TextBuffer()
        self.insert_mark = self.textbuffer.get_insert()

        hbox = gtk.HBox(False, 3)
        archivelabel = gtk.Label("Archive: ")
        self.entry = gtk.Entry()
        self.entry.set_text("")
        self.browsebutton = gtk.Button(u"Browse")
        self.browsebutton.connect("clicked", self.browse)
        self.entry.connect("changed", self.setwidgetactive)
        self.entry.connect('activate', self.countfiles)
        hbox.pack_start(archivelabel, False, False, 0)
        hbox.pack_start(self.entry, True, True, 0)
        hbox.pack_end(self.browsebutton, False, False, 0)

        checkbutton_hbox = gtk.HBox(False, 2)
        self.check_ayniKlasor = gtk.CheckButton(
            u"Organize in the same folder?")
        self.check_ayniKlasor.set_active(True)
        self.check_ayniKlasor.connect("toggled", self.toggled)
        self.check_logfile = gtk.CheckButton("Write a log file?")
        self.check_logfile.set_active(True)
        self.check_logfile.connect("toggled", self.toggled)  # asdasfdasdf
        checkbutton_hbox.pack_start(self.check_ayniKlasor, True, True, 0)
        checkbutton_hbox.pack_end(self.check_logfile, True, True, 0)

        hbox2 = gtk.HBox(False, 3)
        orderedlabel = gtk.Label("Ordered folder: ")
        self.new_folder = gtk.Entry()
        self.new_folder.set_text("")
        self.new_folder.set_sensitive(False)
        self.new_folder.connect("changed", self.setwidgetactive)
        self.browse_new_folder = gtk.Button(u"Browse")
        self.browse_new_folder.connect("clicked", self.browse)
        self.browse_new_folder.set_sensitive(False)
        hbox2.pack_start(orderedlabel, False, False, 0)
        hbox2.pack_start(self.new_folder, True, True, 0)
        hbox2.pack_end(self.browse_new_folder, False, False, 0)

        hbox3 = gtk.HBox(False, 6)
        methodlabel = gtk.Label('Method: ')
        liststore = gtk.ListStore(str)
        for item in ["Copy", "Move"]:
            liststore.append([item])
        cell = gtk.CellRendererText()
        combobox = gtk.ComboBox(liststore)
        combobox.pack_start(cell, True)
        combobox.add_attribute(cell, "text", 0)
        combobox.set_active(0)
        combobox.connect('changed', self.change_method)

        self.albumart = False
        self.check_albumart = gtk.CheckButton("Download the album cover")
        self.check_albumart.set_active(False)
        self.check_albumart.connect("toggled", self.albumartcontrol)

        self.bitenlabel = gtk.Label('0 /')
        self.sayaclabel = gtk.Label('0')

        hbox3.pack_start(methodlabel, False, False, 0)
        hbox3.pack_start(combobox, False, False, 0)
        hbox3.pack_start(self.check_albumart, False, False, 0)
        hbox3.pack_end(self.sayaclabel, False, False, 0)
        hbox3.pack_end(self.bitenlabel, False, False, 0)
        
        altHbox = gtk.HBox(False, 5)
        self.baslaButton = gtk.Button(u"Apply", gtk.STOCK_APPLY)
        self.baslaButton.connect("clicked", self.basla)
        closeButton = gtk.Button("Quit", gtk.STOCK_QUIT)
        closeButton.connect("clicked", self.close)
        aboutButton = gtk.Button("About", gtk.STOCK_ABOUT)
        aboutButton.connect("clicked", self.about)
        altHbox.pack_start(aboutButton, False, False, 0)
        altHbox.pack_end(closeButton, False, False, 0)
        altHbox.pack_end(self.baslaButton, False, False, 0)

        self.textview = gtk.TextView(self.textbuffer)
        self.textview.set_cursor_visible(False)
        self.textview.set_editable(False)

        self.filechooserdialog = gtk.FileChooserDialog("FileChooserDialog",
                                                       None,
                                                       gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                                       (gtk.STOCK_CANCEL,
                                                        gtk.RESPONSE_CANCEL,
                                                        gtk.STOCK_OK,
                                                        gtk.RESPONSE_OK))

        #self.filechooserdialog.connect('selection-changed',
        #        lambda w: self.entry.activate())
        #self.filechooserdialog.connect('close', self.countfiles)

        self.statusbar = gtk.Statusbar()

        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(checkbutton_hbox, False, False, 0)
        vbox.pack_start(hbox2, False, False, 0)
        vbox.pack_start(hbox3, False, False, 0)
        vbox.pack_start(self.scrolledwindow, True, True, 0)
        vbox.pack_end(self.statusbar, False, False, 0)
        vbox.pack_end(altHbox, False, False, 0)
        self.scrolledwindow.add(self.textview)

        self.window.add(vbox)
        self.window.show_all()

    def albumartcontrol(self, widget):
        if widget.get_active() == True:
            self.albumart = True
            try:
                import mechanize
            except ImportError:
                printg("No module named mechanize.\n")
                widget.set_active(False)
                self.albumart = False
        else:
            self.albumart = False

    def countfiles(self, widget):
        if len(self.entry.get_text()) > 2:
            task = self.countfilesgen(self.entry)
            gobject.idle_add(task.next)

    def countfilesgen(self, widget):
        if int(self.sayaclabel.get_text()) != 0:
            self.sayaclabel.set_text('0')
        for ana_dizin, dizinler, dosyalar in os.walk(widget.get_text()):
            for dosya in dosyalar:
                Format = dosya.split(".")[-1]
                if Format in ('mp3', 'flac', 'ogg'):
                    self.sayaclabel.set_label(
                            str(int(self.sayaclabel.get_label()) + 1))
            yield True
        yield False

    def browse(self, widget):
        response = self.filechooserdialog.run()
        if response == gtk.RESPONSE_OK:
            folder = self.filechooserdialog.get_filename()
            if widget == self.browsebutton:
                self.entry.set_text(folder)
                self.countfiles(self.entry)
            elif widget == self.browse_new_folder:
                self.new_folder.set_text(folder)
            self.filechooserdialog.hide()
        elif response == gtk.RESPONSE_CANCEL:
            self.filechooserdialog.hide()

    def toggled(self, widget):
        if widget == self.check_ayniKlasor:
            if self.new_folder.get_sensitive():
                self.new_folder.set_sensitive(False)
                self.browse_new_folder.set_sensitive(False)
            else:
                self.new_folder.set_sensitive(True)
                self.browse_new_folder.set_sensitive(True)
        elif widget == self.check_logfile:
            global logfile
            if self.check_logfile.get_active():
                logfile = True
            else:
                logfile = False
                
    def change_method(self, widget):
        # python'i seviyoruz :)
        self.method = cp if self.method == move else move

        if self.method is move:
            printg('Method changed from copy to move.\n')
        else:
            printg('Method changed from move to copy.\n')

    def setwidgetactive(self, widget):
        self.baslaButton.set_sensitive(True)
            

    def basla(self, widget):
        update_statusbar("Organizing..")
        widget.set_sensitive(False)
        yer = self.entry.get_text()
        if self.check_ayniKlasor.get_active():
            hedef = self.entry.get_text()
        else:
            hedef = self.new_folder.get_text()

        d = Duzenleyici(yer, hedef, self.method, self.albumart)
        d.control()
        task = d.main()
        gobject.idle_add(task.next)
                    
    def about(self, widget):
        aboutdialog = gtk.AboutDialog()
        aboutdialog.set_name(u"Osa1.net arşiv düzenleyici")
        aboutdialog.set_version("0.1")
        aboutdialog.set_comments(u"""Osa1.net arşiv düzenleyici\n
                Tavsiye / eleştiri / error raporu / tercüme için; omeragacan@gmail.com
                """)
        aboutdialog.set_website("http://www.osa1.net")
        aboutdialog.set_website_label("Osa1.net")
        aboutdialog.set_authors([u"Ömer Sinan Ağacan: omeragacan@gmail.com"])
        
        aboutdialog.run()
        aboutdialog.destroy()

    def close(self, widget):
        self.window.destroy()
        gtk.main_quit()


def update_statusbar(text):
    """Statusbar'a yazar"""
    gui.statusbar.push(0, text)


def printg(text):
    """Textbuffer'a yazar"""
    cursor = gui.textbuffer.get_end_iter()
    gui.textbuffer.place_cursor(cursor)
    #texttag = gtk.TextTag()
    #texttag.set_property('foreground', '003366')
    #gui.textbuffer.insert_with_tags(
    #        gui.textbuffer.get_end_iter(),
    #        text,
    #        texttag)
    gui.textbuffer.insert_at_cursor(text)
    gui.textview.scroll_to_mark(gui.insert_mark, 0.4)
    #print text


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


def kopyala(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        gui.bitenlabel.set_text(
            str(int(gui.bitenlabel.get_text().split(' /')[0]) + 1) +\
                    ' /')
        return res
    return wrapper


@kopyala
def cp(a, b):
    "Shutil.copy kullanarak kopyalama yapar. Once cakisma icin konrol eder."
    copy(a, kontrol(b))


@kopyala
def yurut(a, b):
    "Shutil.move kullanarak kopyalama yapar. Once cakisma icin kontrol eder."
    move(a, kontrol(b))


class Duzenleyici:
    def __init__(self, yer, hedef, method=cp, cover=False):
        self.yer = yer
        self.hedef = hedef
        self.method = method
        self.errors = []
        self.songs = 0
        self.cover = cover
        self.supported_formats = ['mp3', 'flac', 'ogg']

    def control(self):
        if not os.path.isdir(self.yer):
            printg(u'Arsiv konumu hatali.\n')
            return False
        if not os.path.isdir(self.hedef):
            printg(u'Hedef klasor olusturuluyor.. ')
            os.mkdir(self.hedef)
            printg(u' OK\n')
        return True

    def main(self):
        for ana_dizin, dizinler, dosyalar in os.walk(self.yer):
            for dosya in dosyalar:
                Format = dosya.split(".")[-1]
                if Format in self.supported_formats:
                    _dosya = os.path.join(ana_dizin, dosya)
                    if self.hedef in ana_dizin and self.hedef != self.yer:
                        continue
                    printg("%s " % _dosya)
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
                        except OSError:
                            pass
                        self.method(_dosya, "%s.%s" %
                                (os.path.join(self.hedef, artist, album, title),
                                    Format))
                        printg("ok..\n")
                    except:
                        self.errors.append(_dosya)
                        printg("error..\n")
                else:
                    self.errors.append(os.path.join(ana_dizin, dosya))
                yield True

        self.download_albumcover()
        self.handle_errors()
        self.clean()
        yield False

    def clean(self):
        """Removes empty folders in target."""
        recursive_cleaner(self.yer)


    def download_albumcover(self):
        if self.cover:
            ad = AlbumArtDownloader()
            task = ad.scan(self.hedef)
            gobject.idle_add(task.next)

    def handle_errors(self):
        global logfile
        printg("others.. ")
        for dosya in self.errors:
            try:
                os.mkdir(os.path.join(self.hedef, "_OTHERS"))
            except:
                pass
            _hedef = os.path.join(self.hedef, "_OTHERS")
            yeni = dosya.split(os.path.sep)[-1]
            self.method(dosya, os.path.join(_hedef, yeni))
            self.songs += 1
        printg("ok..\n")

        if logfile:
            printg("log file.. ")
            log = open(os.path.join(self.hedef, "log.txt"), "w")
            log.write("%s copied.\n\n" % self.songs)
            error_count = 0
            for error in self.errors:
                error_count += 1
                log.write("%s\n" % error)
            log.write("\n\ttotal: %s error." % error_count)
            log.close()
            printg("ok..\n")
        update_statusbar("Done.")

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


def count_files(folder):
    """Recursively counts files in a folder. Does not count folders."""
    r = 0
    l = os.listdir(folder)
    if not l:
        return r
    for f in l:
        if os.path.isdir(os.path.join(folder, f)):
            r += count_files(os.path.join(folder, f))
        else:
            r += 1
    return r


def recursive_cleaner(folder):
    """Recursively check folders and removes if it's empty"""
    l = os.listdir(folder)
    for f in l:
        addr = os.path.join(folder, f)
        if os.path.isdir(addr) and not count_files(addr):
            rmtree(os.path.join(folder, f))


class AlbumArtDownloader:
    def __init__(self):
        import mechanize
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
                if os.path.isdir(os.path.join(p, album)):
                    albums.append("%s:::%s" % (artist, album))

        for album in albums:
            self.download_albumart(album)
            update_statusbar("Downloading %s album cover." %
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
            update_statusbar("Done.")


if __name__ == '__main__':
    gui = Gui()
    gtk.main()
elif 'NAUTILUS_SCRIPT_SELECTED_FILE_PATHS' in os.environ:
    # buraya nautilus scripti kismi gelecek
    pass

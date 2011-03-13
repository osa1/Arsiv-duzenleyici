#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import gtk
import gobject
from shutil import copy2, move
from yeniduzenleyici import AlbumArtDownloader
from yeniduzenleyici import Organizer
from yeniduzenleyici import count_files

logfile = True


class Gui:
    def __init__(self):
        self.method = cp
        self.window = gtk.Window()
        self.window.connect("destroy", self.close)
        self.window.move(500, 10)
        self.window.set_title("Archive organizer 0.2")
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
        self.check_same_folder = gtk.CheckButton(
            u"Organize in the same folder?")
        self.check_same_folder.set_active(True)
        self.check_same_folder.connect("toggled", self.toggled)
        self.check_logfile = gtk.CheckButton("Write a log file?")
        self.check_logfile.set_active(True)
        self.check_logfile.connect("toggled", self.toggled)  # asdasfdasdf
        checkbutton_hbox.pack_start(self.check_same_folder, True, True, 0)
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

        self.finished = gtk.Label('0 /')
        self.counter = gtk.Label('0')

        hbox3.pack_start(methodlabel, False, False, 0)
        hbox3.pack_start(combobox, False, False, 0)
        hbox3.pack_start(self.check_albumart, False, False, 0)
        hbox3.pack_end(self.counter, False, False, 0)
        hbox3.pack_end(self.finished, False, False, 0)
        
        altHbox = gtk.HBox(False, 5)
        self.start_button = gtk.Button(u"Apply", gtk.STOCK_APPLY)
        self.start_button.connect("clicked", self.start)
        closeButton = gtk.Button("Quit", gtk.STOCK_QUIT)
        closeButton.connect("clicked", self.close)
        aboutButton = gtk.Button("About", gtk.STOCK_ABOUT)
        aboutButton.connect("clicked", self.about)
        altHbox.pack_start(aboutButton, False, False, 0)
        altHbox.pack_end(closeButton, False, False, 0)
        altHbox.pack_end(self.start_button, False, False, 0)

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
                self.printg(self, "No module named mechanize.\n")
                widget.set_active(False)
                self.albumart = False
        else:
            self.albumart = False

    def countfiles(self, widget):
        if len(self.entry.get_text()) > 2:
            task = self.countfilesgen(self.entry)
            gobject.idle_add(task.next)

    def countfilesgen(self, widget):
        if int(self.counter.get_text()) != 0:
            self.counter.set_text('0')
        for ana_dizin, dizinler, dosyalar in os.walk(widget.get_text()):
            for dosya in dosyalar:
                Format = dosya.split(".")[-1]
                if Format in ('mp3', 'flac', 'ogg'):
                    self.counter.set_label(
                            str(int(self.counter.get_label()) + 1))
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
        if widget == self.check_same_folder:
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
            self.printg('Method changed from copy to move.\n')
        else:
            self.printg('Method changed from move to copy.\n')

    def setwidgetactive(self, widget):
        self.start_button.set_sensitive(True)
            

    def start(self, widget):
        self.update_statusbar("Organizing..")
        widget.set_sensitive(False)
        source = self.entry.get_text()
        if self.check_same_folder.get_active():
            target = self.entry.get_text()
        else:
            target = self.new_folder.get_text()
        self.printg("blablabla")
        
        aad = AlbumArtDownloader(self)
        org = Organizer(source, self)
        
        task = org.organize(source, self.method, target)
        gobject.idle_add(task.next)
        self.update_statusbar('Done.')

                    
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
        
    def printg(self, text):
        """Prints gui's textbuffer."""
        cursor = self.textbuffer.get_end_iter()
        self.textbuffer.place_cursor(cursor)
        #texttag = gtk.TextTag()
        #texttag.set_property('foreground', '003366')
        #gui.textbuffer.insert_with_tags(
        #        gui.textbuffer.get_end_iter(),
        #        text,
        #        texttag)
        self.textbuffer.insert_at_cursor(text + '\n')
        self.textview.scroll_to_mark(gui.insert_mark, 0.4)
        #print text


    def update_statusbar(self, text):
        """Updates gui's statusbar."""
        self.statusbar.push(0, text)




def _help():
    print __doc__


def control(b):
    """
    Check for files with same name.
    Add '_' when overlap.
    """
    if os.path.isfile(b):
        _b = b.split(os.path.sep)
        b = os.sep.join(_b[:-1]) + os.path.sep + "_" + _b[-1]
    return b


def copy(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        gui.finished.set_text(
            str(int(gui.finished.get_text().split(' /')[0]) + 1) +\
                    ' /')
        return res
    return wrapper


@copy
def cp(a, b):
    "Shutil.copy kullanarak kopyalama yapar. Once cakisma icin konrol eder."
    copy2(a, control(b))


@copy
def yurut(a, b):
    "Shutil.move kullanarak kopyalama yapar. Once cakisma icin kontrol eder."
    move(a, control(b))



if __name__ == '__main__':
    gui = Gui()
    gtk.main()
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import gobject
import os
import duzenleyici

class Gui:
    def __init__(self, cp=None, move=None):
        self.cp = cp
        self.move = move
        self.logfile = True
        self.method = self.cp
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
        gtk.main()

    def albumartcontrol(self, widget):
        if widget.get_active() == True:
            self.albumart = True
            try:
                import mechanize
            except ImportError:
                self.printg("No module named mechanize.\n")
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
            if self.check_logfile.get_active():
                self.logfile = True
            else:
                self.logfile = False

    def change_method(self, widget):
        # python'i seviyoruz :)
        self.method = self.cp if self.method == self.move else self.move

        if self.method is self.move:
            self.printg('Method changed from copy to move.\n')
        else:
            self.printg('Method changed from move to copy.\n')

    def setwidgetactive(self, widget):
        self.baslaButton.set_sensitive(True)

    def inc_counter(self):
        self.bitenlabel.set_text(
                    str(int(
                        self.bitenlabel.get_text().split(' /')[0]) +1) + ' /')


    def basla(self, widget):
        self.update_statusbar("Organizing..")
        widget.set_sensitive(False)
        yer = self.entry.get_text()
        if self.check_ayniKlasor.get_active():
            hedef = self.entry.get_text()
        else:
            hedef = self.new_folder.get_text()

        d = duzenleyici.Duzenleyici(yer, hedef, self.method, self, self.albumart)
        if not self.logfile:
            d.logfile = False
        d.control()
        task = d.organize()
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

    def update_statusbar(self, text):
        self.statusbar.push(0, text)

    def printg(self, text):
        cursor = self.textbuffer.get_end_iter()
        self.textbuffer.place_cursor(cursor)
        #texttag = gtk.TextTag()
        #texttag.set_property('foreground', '003366')
        #self.textbuffer.insert_with_tags(
        #        self.textbuffer.get_end_iter(),
        #        text,
        #        texttag)
        self.textbuffer.insert_at_cursor(text)
        self.textview.scroll_to_mark(self.insert_mark, 0.4)
        #print text


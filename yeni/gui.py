#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gtk
import os
import re
import threading
import urllib2
from shutil import copy, move
from sys import argv, exit, stderr
from mutagen.easyid3 import EasyID3 as id3
from mutagen.flac import Open as flac
from mutagen.oggvorbis import Open as ogg
import gobject

logfile = True





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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from shutil import copy, move
import os
import gui2


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

if __name__ == "__main__":
    _gui = gui2.Gui(cp, yurut)

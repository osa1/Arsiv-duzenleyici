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

def delete_if_exists(func):
    # decorator for listener
    # when listener creates a file, a new signal emitted
    # because of the new folder, then listener copies tries to organize it again..
    def wrapper(a, b):
        if os.path.isfile(b):
            os.remove(b)
            return
        return func(a, b)
    return wrapper

@delete_if_exists
def cp(a, b):
    "Shutil.copy kullanarak kopyalama yapar. Once cakisma icin konrol eder."
    copy(a, kontrol(b))


@delete_if_exists
def yurut(a, b):
    "Shutil.move kullanarak kopyalama yapar. Once cakisma icin kontrol eder."
    print "moving"
    move(a, kontrol(b))

if __name__ == "__main__":
    _gui = gui2.Gui(cp, yurut)

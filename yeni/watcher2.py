"""
pyinotify'dan bir bok anlamayınca şöyle bir deneme yaptım
gayet güzel çalışıyor, performansı test etmek lazım,
5 saniyede bir bir sürü işlem yapacak, yüzlerce klasörlük bir
klasörde pek sağlıklı çalışmayabilir.
"""


#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import join
import time
from shutil import rmtree
import duzenleyici
from main import cp, yurut


target = '/home/osa1/Desktop/testler'
gui = duzenleyici.DummyGui()
d = duzenleyici.Duzenleyici(target, target, yurut, gui, False)
d.logfile = False
ad = duzenleyici.AlbumArtDownloader(gui)


before = [f for f in os.listdir(target)]

while True:
    time.sleep(5)
    after   = [f for f in os.listdir(target)]
    added   = [f for f in after if not f in before]
    removed = [f for f in before if not f in after]
    org = []


    if added:
        print "Added: ", ", ".join(added)
        for f in added:
            if os.path.isdir(join(target, f)):
                print "folder"
                d.yer = join(target, f)
                d.control()
                task = d.main()
                while True:
                    try:
                        org.append(task.next())
                    except StopIteration:
                        print "stopiteration"
                        break
                rmtree(join(target, f))
            else:
                d.yer = target
                org.append(d.organize(target, os.path.split(f)[-1]))

    if removed:
        print "removed: ", str(removed)
    
    [before.append(f) for f in org]
    [before.append(f) for f in after]
    [before.remove(f) for f in removed]

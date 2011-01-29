#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inotify
import os
import duzenleyici
import threading
from main import cp, yurut

"""dir(event)
['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'dir', 'mask', 'maskname', 'name', 'path', 'pathname', 'wd']
"""

wm = inotify.WatchManager()
mask = inotify.IN_CLOSE_NOWRITE|inotify.IN_CREATE
target = "/home/osa1/Desktop/testler"

d = duzenleyici.Duzenleyici(target, target, cp, duzenleyici.DummyGui(), False)

class EventHandler(inotify.ProcessEvent):

    folders = []

    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname
        folder = event.pathname
        if not folder in self.folders:
            self.folders.append(folder)
        print event

    def process_IN_CLOSE_NOWRITE(self, event):
        try:
            self.t.cancel()
        except:
            pass
        self.t = threading.Timer(2.0, self.start)
        self.t.start()
        print event

    def test(self):
        for path in self.folders:
            self.folders.remove(path)
            print path

    def start(self):
        for path in self.folders:
            self.folders.remove(path)
            d.yer = path
            if os.path.isdir(path):
                d.control()
                task = d.main()
                while True:
                    try:
                        task.next()
                    except StopIteration:
                        print "stopiteration"
                        break


handler = EventHandler()
notifier = inotify.Notifier(wm, handler)
wdd = wm.add_watch(target, mask, rec=True)

notifier.loop()

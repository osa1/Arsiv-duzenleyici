#!/usr/bin/env python

import os
from fsmonitor import FSMonitor

class Monitor:
    """Basic filesystem watcher."""
    def __init__(self, folder_to_watch=None):
        self.observers = []
        self.folder_to_watch = folder_to_watch

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self.observers:
            observer.update(*args, **kwargs)

    def start(self):
        m = FSMonitor()
        if type(self.folder_to_watch) == list:  # meh
            [m.add_dir_watch(f) for f in self.folder_to_watch]
        else:
            m.add_dir_watch(self.folder_to_watch)

        while True:
            for evt in m.read_events():
                #print "action_name: %s, evt.watch.path: %s, evt.name: %s" % (
                        #evt.action_name, evt.watch.path, evt.name)
                if evt.action_name == 'create':
                    self.notify_observers(created_files=
                            os.path.join(evt.watch.path, evt.name))
                elif evt.action_name == 'attrib':
                    self.notify_observers(attribd_files=
                            os.path.join(evt.watch.path, evt.name))


class Observer:
    """A simple observer class for Monitor."""
    def __init__(self, monitor, method):
        """Method will be called when necessary."""
        self.method = method 
        self.monitor = monitor
        self.monitor.add_observer(self)
        self.files_to_ignore = set()
        self.created_files = set()
        self.attribd_files = set()

    def update(self, created_files=None, attribd_files=None):
        if created_files:
            self.created_files.update([created_files])
        if attribd_files:
            self.attribd_files.update([attribd_files])

        # attribd signal emitted when copying a file is done
        for f in self.created_files & self.attribd_files:
            self.method(f)
            self.created_files.remove(f)
            self.attribd_files.remove(f)


class Organizer:
    def organize(self, *args, **kwargs):
        print "I'm teh organizer."
        print "organizing:"
        print args
        print kwargs


m = Monitor("/home/osa1/Desktop/fsw")
org = Organizer()
observer = Observer(m, org.organize)
m.add_observer(observer)
m.start()

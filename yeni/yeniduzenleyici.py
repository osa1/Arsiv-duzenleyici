#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from shutil import rmtree
from mutagen.easyid3 import EasyID3 as id3
from mutagen.oggvorbis import Open as ogg
from mutagen.flac import Open as flac

supported_formats = ['mp3', 'flac', 'ogg']
errors = []
songs = 0


def check_folder(folder):
    """Checks if there is a folder and creates if there isn't.
    returns false if target is a file."""
    if not os.path.exists(folder):
        os.mkdir(folder)
        print 'Target folder created.'
        return True

    if not os.path.isdir(folder):
        print 'Target is a file.'
        return False

    return True

def __cmethod(source, dest, method):
    if (os.path.isdir(source)):
        return False
    method(source, dest)
    return True


def __organize_folder(folder, method, target_folder=None):

    global songs, errors, supported_formats
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
            if not frmt in supported_formats:
                errors.append(f)
                continue
            print f
            # try ?
            if frmt == 'mp3':
                f_attr = id3(f)
            elif frmt == 'flac':
                f_attr = flac(f)
            elif frmt == 'ogg':
                f_attr = ogg(f)
            songs += 1
            artist = f_attr['artist'][0].replace('/', '-')
            album = f_attr['album'][0].replace('/', '-')
            title = f_attr['title'][0].replace('/', '-')
            try:
                os.makedirs(os.path.join(target_folder, artist, album))
            except OSError:  # there is already a folder
                pass
            __cmethod(f, '%s.%s' % (
                os.path.join(target_folder, artist, album, title), frmt), method)
            created_folders.update([os.path.join(target_folder, artist)])

    created_folders.update([__handle_errors(method, target_folder)])
    return created_folders

def __organize_file(f, method, target_folder=None):
    global supported_formats, errors, songs
    created_folders= set()
    if not target_folder:
        target_folder = os.path.dirname(f)

    frmt = f.split('.')[-1]
    if frmt not in supported_formats:
        errors.append(f)
        created_folders.update([__handle_errors(method, target_folder)])
        return created_folders

    if frmt == 'mp3':
        f_attr = id3(f)
    elif frmt == 'flac':
        f_attr = flac(f)
    elif frmt == 'ogg':
        f_attr = ogg(f)
    songs += 1
    artist = f_attr['artist'][0].replace('/', '-')
    album = f_attr['album'][0].replace('/', '-')
    title = f_attr['title'][0].replace('/', '-')
    try:
        os.makedirs(os.path.join(target_folder, artist, album))
    except OSError:
        pass
    __cmethod(f, '%s.%s' % (
        os.path.join(target_folder, artist, album, title), frmt), method)
    created_folders.update([os.path.join(target_folder, artist)])
    return created_folders

def organize(f, method, target_folder=None):
    """Moves/copies(or does what method provides) the song(s) to target folder.
    Returns set of created folders."""
    if os.path.isdir(f):
        return __organize_folder(f, method, target_folder)
    return __organize_file(f, method, target_folder)



def __handle_errors(method, target_folder):
    global errors
    error_folder = os.path.join(target_folder, '_ERRORS')
    if not check_folder(error_folder):
        return
    for f in errors:
        print "err folder: ",
        print error_folder
        method(f, error_folder)
    errors = []
    return error_folder


def clean(target):
    """Removes empty folders. Recursively."""
    l = os.listdir(target)
    for f in l:
        addr = os.path.join(target, f)
        if os.path.isdir(addr) and not count_files(addr):
            rmtree(os.path.join(target, f))


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


if __name__ == "__main__":
    #yer = "/home/osa1/Desktop/test/Ruins of The Perished.mp3"
    #yer = "/home/osa1/Desktop/test"
    yer = "/home/osa1/Desktop/test/testconcurrent.py"
    organize(yer, shutil.move)
    print errors

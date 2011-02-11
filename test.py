#!/usr/bin/env python

import mechanize
import urllib2
import os
import threading
import re
import sys

PATTERN = re.compile(r':(http://[a-zA-Z0-9\-\\/._]*)')


def browser_gen():
    br = mechanize.Browser()
    br.open('http://images.google.com')
    br.select_form(nr=0)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]  # lulz
    br.set_handle_equiv(False)
    br.set_handle_robots(False)
    return br


def indir(adres, album):
    print adres, 'indiriliyor'
    yer = '/home/osa1/Desktop/testler'
    grup, album = album.split(':::')
    try:
        image = urllib2.urlopen(adres)
    except:  # urllib2.HTTPError, urllib2.URLError, ...
        return



    f = adres.split('.')[-1]

    with open(os.path.join(yer, '%s.%s' % (album, f)), 'w') as dosya:
        dosya.write(image.read())
#    with open(os.path.join(yer, grup, album,
#        'cover.%s' % f), 'w') as dosya:
    print adres, 'bitti'


def album_indir(album, br, pattern):
    print album
    br.select_form(nr=0)
    br['q'] = '%s %s' % (album.split(':::')[0], album.split(':::')[1])
    response = br.submit()
    html = response.read()
    for url in pattern.findall(html):
        if 'tinypic' in url:
            continue
        break

    try:
        url
    except:
        return  # hicbir resmin bulunamama durumu

    threading.Thread(target=indir, args=(url, album)).start()
    #indir(url, album)
    br.back()


if __name__ == '__main__':
    try:
        yer = sys.argv[1]
    except IndexError:
        sys.exit()

    gruplar = [folder for folder in os.listdir(yer) if os.path.isdir(os.path.join(yer, folder))]
    albumler = []

    for grup in gruplar:
        yer2 = os.path.join(yer, grup)
        for album in os.listdir(yer2):
            if os.path.isdir(os.path.join(yer2, album)):
                albumler.append('%s:::%s' % (grup, album))

    for album in albumler:
        album_indir(album, browser_gen(), PATTERN)

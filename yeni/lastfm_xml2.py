import urllib2
import xml.etree.ElementTree as ET
from urllib import quote

artist = "inflames"
q_artist = quote(artist)
addr = "http://ws.audioscrobbler.com/2.0/?method=artist.getcorrection&artist=%s&api_key=b25b959554ed76058ac220b7b2e0a026" % q_artist
print addr


tree = ET.parse(urllib2.urlopen(addr))
# daha kolay bir yolu olmali
print tree.find("corrections").find("correction").find("artist").find("name").text


# lxml denenecek, xpath koyal gibi gozukuyor

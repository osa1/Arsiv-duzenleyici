import urllib2
from urllib import quote
from xml.dom import minidom

artist = "imflames"
q_artist = quote(artist)
addr = "http://ws.audioscrobbler.com/2.0/?method=artist.getcorrection&artist=%s&api_key=b25b959554ed76058ac220b7b2e0a026" % q_artist
print addr

try:
    last_xml = minidom.parse(urllib2.urlopen(addr))
except urllib2.HTTPError:
    print "httperror"
    exit()

#fuu = last_xml.firstChild.childNodes[1].childNodes[1].childNodes[1].childNodes[1].firstChild.data
#print fuu

print last_xml.toxml()
print "-----------------------------------------"
try:
    grammarNode = last_xml.firstChild
    print grammarNode.toxml()
    print "-----------------------------------------"
    refNode = grammarNode.childNodes[1]
    print refNode.toxml()
    print "-----------------------------------------"
    pNode = refNode.childNodes[1]
    print pNode.toxml()
    print "-----------------------------------------"
    araNode = pNode.childNodes[1]
    print araNode.toxml()
    print "-----------------------------------------"
    sonNode = araNode.childNodes[1]
    print sonNode.toxml()
    print "-----------------------------------------"
    print sonNode.firstChild.toxml()
    print "-----------------------------------------"
    print sonNode.firstChild.data
except IndexError:
    print "indexerror"

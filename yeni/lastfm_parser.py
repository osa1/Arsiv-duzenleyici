import urllib2
import xml.etree.ElementTree as ET
from urllib import quote


def get_artist_correction(artist):
    q_artist = quote(artist)
    artist_addr = "http://ws.audioscrobbler.com/2.0/?method=artist.getcorrection&artist=%s&api_key=b25b959554ed76058ac220b7b2e0a026" % q_artist
    print artist_addr
    try:
        tree = ET.parse(urllib2.urlopen(artist_addr))
    except urllib2.HTTPError:
        return artist
    c_artist = None
    try:
        c_artist = tree.find("corrections").find("correction").find("artist").find("name").text
    except:
        pass

    return c_artist if c_artist else artist

def get_track_correction(artist, track):
    """Artist isminin dogru oldugu varsayilir."""
    q_artist = quote(artist)
    q_track = quote(track)
    track_addr = "http://ws.audioscrobbler.com/2.0/?method=track.getcorrection&artist=%s&track=%s&api_key=b25b959554ed76058ac220b7b2e0a026" % (q_artist, q_track)
    print track_addr 
    try:
        tree = ET.parse(urllib2.urlopen(track_addr))
    except urllib2.HTTPError:
        print "httperror"
        return (artist, track)
    c_track = None
    try:
        c_track = tree.find("corrections").find("correction").find("track").find("name").text
    except:
        pass

    return (artist, c_track) if c_track else (artist, track)

if __name__ == "__main__":
    print get_track_correction("guns and roses", "mrbrownstone")
    print get_artist_correction("im flames")
    raw_input()
